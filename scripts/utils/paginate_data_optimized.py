#!/usr/bin/env python3
"""
Optimized pagination script that stays under Cloudflare R2's 100-file dashboard limit.

This version uses larger page sizes and smarter file management to create
fewer files while maintaining good performance.
"""

import sys
from pathlib import Path
import logging
import argparse
import math

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.core.pagination import paginate_large_datasets

def calculate_optimal_page_sizes(data_dir: Path, max_files: int = 90):
    """
    Calculate optimal page sizes to stay under file limit while maintaining performance.
    
    Args:
        data_dir: Directory with processed JSON files
        max_files: Maximum number of files to create (leaving buffer under 100)
    
    Returns:
        Dictionary with optimized pagination configs
    """
    logger = logging.getLogger(__name__)
    
    # Check actual file sizes to calculate optimal pagination
    file_info = {}
    large_files = ['acoustic_indices', 'environmental', 'detections']
    
    for dataset in large_files:
        json_file = data_dir / f"{dataset}.json"
        if json_file.exists():
            size_mb = json_file.stat().st_size / (1024 * 1024)
            file_info[dataset] = size_mb
        else:
            logger.warning(f"File not found: {json_file}")
    
    if not file_info:
        logger.error("No large files found to paginate")
        return {}
    
    logger.info("File sizes found:")
    for dataset, size in file_info.items():
        logger.info(f"  {dataset}: {size:.1f}MB")
    
    # Allocate files proportionally based on size, but ensure good performance
    total_size = sum(file_info.values())
    allocated_files = {}
    total_allocated = 0
    
    for dataset, size in file_info.items():
        # Allocate files proportionally, but with minimum and maximum limits
        proportion = size / total_size
        base_allocation = int(proportion * max_files)
        
        # Set reasonable bounds
        if dataset == 'acoustic_indices':
            # Acoustic indices is huge but needs good UX - cap at 30 files
            allocated = min(base_allocation, 30)
        elif dataset == 'environmental': 
            # Environmental is large but less interactive - cap at 25 files
            allocated = min(base_allocation, 25)
        else:
            # Detections and others - cap at 15 files
            allocated = min(base_allocation, 15)
        
        # Ensure minimum of 3 files for reasonable UX
        allocated = max(allocated, 3)
        allocated_files[dataset] = allocated
        total_allocated += allocated
    
    # If we're over the limit, scale down proportionally
    if total_allocated > max_files:
        scale_factor = max_files / total_allocated
        for dataset in allocated_files:
            allocated_files[dataset] = max(3, int(allocated_files[dataset] * scale_factor))
        total_allocated = sum(allocated_files.values())
    
    logger.info(f"File allocation (total: {total_allocated}):")
    
    # Calculate page sizes based on file allocations
    optimized_configs = {}
    
    for dataset, allocated in allocated_files.items():
        if dataset not in file_info:
            continue
            
        # Estimate records (rough approximation)
        size_mb = file_info[dataset]
        if dataset == 'acoustic_indices':
            # Acoustic indices: ~4.5KB per record
            estimated_records = int(size_mb * 1024 / 4.5)
        elif dataset == 'environmental':
            # Environmental: ~0.2KB per record  
            estimated_records = int(size_mb * 1024 / 0.2)
        elif dataset == 'detections':
            # Detections: ~0.55KB per record
            estimated_records = int(size_mb * 1024 / 0.55)
        else:
            # Default estimate
            estimated_records = int(size_mb * 1024 / 1.0)
        
        # Calculate page size to get desired number of files
        page_size = max(100, int(estimated_records / allocated))  # Minimum 100 records
        
        optimized_configs[dataset] = {
            'page_size': page_size,
            'date_column': 'datetime',
            'sample_size': min(200, page_size // 10)  # 10% sample, max 200
        }
        
        logger.info(f"  {dataset}: {allocated} files, ~{page_size} records/page ({size_mb:.1f}MB)")
    
    return optimized_configs

def main():
    parser = argparse.ArgumentParser(description='Optimized pagination for Cloudflare R2 limits')
    parser.add_argument('--data-dir', 
                       default='data/cdn/processed', 
                       help='Directory containing processed JSON files')
    parser.add_argument('--max-files',
                       type=int,
                       default=90,
                       help='Maximum number of files to create (default: 90, under R2 limit)')
    parser.add_argument('--force', 
                       action='store_true', 
                       help='Force pagination even for smaller files')
    parser.add_argument('--verbose', '-v', 
                       action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Resolve data directory path
    data_dir = Path(args.data_dir)
    if not data_dir.is_absolute():
        data_dir = Path.cwd() / data_dir
    
    if not data_dir.exists():
        logger.error(f"Data directory does not exist: {data_dir}")
        sys.exit(1)
    
    logger.info(f"Starting OPTIMIZED pagination for Cloudflare R2 dashboard limit")
    logger.info(f"Target: max {args.max_files} files (under 100 limit)")
    logger.info(f"Directory: {data_dir}")
    
    # Calculate optimal configurations
    try:
        optimized_configs = calculate_optimal_page_sizes(data_dir, args.max_files)
        
        if not optimized_configs:
            logger.error("Could not generate optimized configurations")
            sys.exit(1)
        
        # Clean up existing paginated directory
        paginated_dir = data_dir / 'paginated'
        if paginated_dir.exists():
            import shutil
            logger.info("Cleaning up existing paginated files...")
            shutil.rmtree(paginated_dir)
        
        # Run optimized pagination
        results = paginate_large_datasets(
            processed_data_dir=data_dir,
            pagination_configs=optimized_configs
        )
        
        # Count actual files created
        if paginated_dir.exists():
            actual_files = len(list(paginated_dir.glob('*.json')))
        else:
            actual_files = 0
        
        # Print results summary
        print("\n" + "="*70)
        print("OPTIMIZED PAGINATION RESULTS")
        print("="*70)
        
        print(f"\n📁 Files Created: {actual_files} (limit: 100)")
        
        if actual_files > 100:
            print("⚠️  WARNING: Still over 100 files! May need manual upload.")
        elif actual_files > 90:
            print("⚠️  CAUTION: Close to limit. Consider reducing further.")
        else:
            print("✅ SUCCESS: Under Cloudflare R2 dashboard limit!")
        
        for dataset_name, result in results['datasets'].items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            size_info = f"({result['original_size_mb']:.1f}MB)"
            
            print(f"\n{dataset_name} {size_info}: {status}")
            
            if result['success']:
                pagination = result['pagination']
                files_per_dataset = pagination['total_pages'] + 2  # pages + summary + index
                print(f"  • {pagination['total_pages']} pages + summary/index = {files_per_dataset} files")
                print(f"  • {pagination['total_records']:,} records, {pagination['page_size']} per page")
            else:
                print(f"  • Error: {result['error']}")
        
        print(f"\n📂 Location: {paginated_dir}")
        print(f"🚀 Ready for Cloudflare R2 dashboard upload!")
        
        if results['summary']['failed_paginations'] > 0:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error during optimized pagination: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()