#!/usr/bin/env python3
"""
Script to paginate large JSON datasets for optimized frontend loading.

This script identifies large JSON files and splits them into smaller paginated chunks
that can be loaded on-demand by the frontend, significantly improving performance.
"""

import sys
from pathlib import Path
import logging
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.core.pagination import paginate_large_datasets

def main():
    parser = argparse.ArgumentParser(description='Paginate large JSON datasets for frontend optimization')
    parser.add_argument('--data-dir', 
                       default='data/cdn/processed', 
                       help='Directory containing processed JSON files (default: data/cdn/processed)')
    parser.add_argument('--page-size-acoustic', 
                       type=int, 
                       default=1000, 
                       help='Page size for acoustic indices (default: 1000)')
    parser.add_argument('--page-size-env', 
                       type=int, 
                       default=2000, 
                       help='Page size for environmental data (default: 2000)')
    parser.add_argument('--page-size-detections', 
                       type=int, 
                       default=5000, 
                       help='Page size for detection data (default: 5000)')
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
    
    logger.info(f"Starting pagination process for directory: {data_dir}")
    
    # Custom pagination configurations based on arguments
    pagination_configs = {
        'acoustic_indices': {
            'page_size': args.page_size_acoustic,
            'date_column': 'datetime',
            'sample_size': 100
        },
        'environmental': {
            'page_size': args.page_size_env,
            'date_column': 'datetime', 
            'sample_size': 200
        },
        'detections': {
            'page_size': args.page_size_detections,
            'date_column': 'datetime',
            'sample_size': 500
        }
    }
    
    # Override minimum file size if force is specified
    if args.force:
        logger.info("Force mode enabled - will paginate all specified files regardless of size")
    
    try:
        # Run pagination
        results = paginate_large_datasets(
            processed_data_dir=data_dir,
            pagination_configs=pagination_configs
        )
        
        # Print results summary
        print("\n" + "="*60)
        print("PAGINATION RESULTS SUMMARY")
        print("="*60)
        
        for dataset_name, result in results['datasets'].items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            size_info = f"({result['original_size_mb']:.1f}MB)"
            
            print(f"\n{dataset_name} {size_info}: {status}")
            
            if result['success']:
                pagination = result['pagination']
                print(f"  • Created {pagination['total_pages']} pages")
                print(f"  • {pagination['total_records']:,} total records")
                print(f"  • Page size: {pagination['page_size']} records")
                if pagination.get('sorted_by'):
                    print(f"  • Sorted by: {pagination['sorted_by']}")
            else:
                print(f"  • Error: {result['error']}")
        
        print(f"\nOverall Summary:")
        print(f"  • Datasets processed: {results['summary']['total_datasets']}")
        print(f"  • Successful: {results['summary']['successful_paginations']}")
        print(f"  • Failed: {results['summary']['failed_paginations']}")
        
        paginated_dir = data_dir / 'paginated'
        print(f"\nPaginated files saved to: {paginated_dir}")
        print(f"Master index: {paginated_dir / 'pagination_master_index.json'}")
        
        if results['summary']['failed_paginations'] > 0:
            logger.warning("Some datasets failed to paginate. Check logs above for details.")
            sys.exit(1)
        else:
            logger.info("✅ All datasets paginated successfully!")
            
    except Exception as e:
        logger.error(f"Fatal error during pagination: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()