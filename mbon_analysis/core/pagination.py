"""
Data pagination utilities for optimizing frontend performance.

This module provides utilities for splitting large JSON datasets into smaller,
paginated files that can be loaded on-demand by the frontend.
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging
import math
from datetime import datetime

logger = logging.getLogger(__name__)

class DataPaginator:
    """
    Handles pagination of large datasets for optimal frontend loading.
    
    Supports different pagination strategies:
    - Simple pagination: Split data into equal-sized pages
    - Temporal pagination: Split by date ranges 
    - Indexed pagination: Create index files for efficient navigation
    """
    
    def __init__(self, output_dir: Union[str, Path]):
        """
        Initialize paginator with output directory.
        
        Args:
            output_dir: Directory where paginated files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def paginate_json_file(self, 
                          input_file: Union[str, Path],
                          base_name: str,
                          page_size: int = 1000,
                          date_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Split a large JSON file into paginated chunks.
        
        Args:
            input_file: Path to the input JSON file
            base_name: Base name for output files (e.g., 'acoustic_indices')
            page_size: Number of records per page
            date_column: If specified, sort by this date column before pagination
            
        Returns:
            Dictionary with pagination metadata
        """
        logger.info(f"Starting pagination of {input_file} with page size {page_size}")
        
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Load the full dataset
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError(f"Expected list data structure, got {type(data)}")
        
        total_records = len(data)
        total_pages = math.ceil(total_records / page_size)
        
        logger.info(f"Splitting {total_records} records into {total_pages} pages")
        
        # Sort by date if specified
        if date_column:
            logger.info(f"Sorting by date column: {date_column}")
            try:
                # Convert to DataFrame for easier date sorting
                df = pd.DataFrame(data)
                df[date_column] = pd.to_datetime(df[date_column])
                df = df.sort_values(date_column)
                data = df.to_dict('records')
            except Exception as e:
                logger.warning(f"Failed to sort by {date_column}: {e}. Using original order.")
        
        # Create paginated files
        page_files = []
        for page_num in range(total_pages):
            start_idx = page_num * page_size
            end_idx = min((page_num + 1) * page_size, total_records)
            
            page_data = data[start_idx:end_idx]
            page_filename = f"{base_name}_page_{page_num + 1:03d}.json"
            page_path = self.output_dir / page_filename
            
            with open(page_path, 'w') as f:
                json.dump(page_data, f, separators=(',', ':'), default=str)  # Compact JSON with string fallback
            
            page_info = {
                'page': page_num + 1,
                'filename': page_filename,
                'records': len(page_data),
                'start_index': start_idx,
                'end_index': end_idx - 1
            }
            
            # Add date range if we sorted by date
            if date_column and page_data:
                try:
                    page_df = pd.DataFrame(page_data)
                    page_df[date_column] = pd.to_datetime(page_df[date_column])
                    page_info['date_range'] = {
                        'start': page_df[date_column].min().isoformat(),
                        'end': page_df[date_column].max().isoformat()
                    }
                except:
                    pass
            
            page_files.append(page_info)
            logger.debug(f"Created {page_filename} with {len(page_data)} records")
        
        # Create pagination index
        pagination_metadata = {
            'dataset': base_name,
            'total_records': total_records,
            'total_pages': total_pages,
            'page_size': page_size,
            'sorted_by': date_column,
            'generated_at': datetime.now().isoformat(),
            'pages': page_files
        }
        
        index_filename = f"{base_name}_pagination_index.json"
        index_path = self.output_dir / index_filename
        
        with open(index_path, 'w') as f:
            json.dump(pagination_metadata, f, indent=2)
        
        logger.info(f"Pagination complete. Index saved to {index_filename}")
        return pagination_metadata
    
    def create_lightweight_summary(self, 
                                 pagination_metadata: Dict[str, Any],
                                 sample_size: int = 100) -> Dict[str, Any]:
        """
        Create a lightweight summary file with a sample of records for initial loading.
        
        Args:
            pagination_metadata: Metadata from paginate_json_file()
            sample_size: Number of records to include in summary
            
        Returns:
            Summary metadata
        """
        base_name = pagination_metadata['dataset']
        total_records = pagination_metadata['total_records']
        
        # Load a sample from first few pages
        sample_data = []
        records_collected = 0
        
        for page_info in pagination_metadata['pages']:
            if records_collected >= sample_size:
                break
                
            page_path = self.output_dir / page_info['filename']
            with open(page_path, 'r') as f:
                page_data = json.load(f)
            
            # Take records from this page
            remaining_needed = sample_size - records_collected
            sample_from_page = page_data[:remaining_needed]
            sample_data.extend(sample_from_page)
            records_collected += len(sample_from_page)
        
        # Create summary file
        summary = {
            'dataset': base_name,
            'sample_records': sample_data,
            'summary_info': {
                'total_records': total_records,
                'total_pages': pagination_metadata['total_pages'],
                'sample_size': len(sample_data),
                'pagination_available': True
            },
            'pagination_index': f"{base_name}_pagination_index.json",
            'generated_at': datetime.now().isoformat()
        }
        
        summary_filename = f"{base_name}_summary.json"
        summary_path = self.output_dir / summary_filename
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, separators=(',', ':'), default=str)
        
        logger.info(f"Created summary file {summary_filename} with {len(sample_data)} sample records")
        return summary

def paginate_large_datasets(processed_data_dir: Union[str, Path], 
                          pagination_configs: Optional[Dict[str, Dict]] = None):
    """
    Paginate all large datasets based on configuration.
    
    Args:
        processed_data_dir: Directory containing processed JSON files
        pagination_configs: Dictionary mapping dataset names to pagination config
    """
    processed_dir = Path(processed_data_dir)
    
    # Default pagination configurations
    default_configs = {
        'acoustic_indices': {
            'page_size': 1000,
            'date_column': 'datetime'
        },
        'environmental': {
            'page_size': 2000,
            'date_column': 'datetime'
        },
        'detections': {
            'page_size': 5000,
            'date_column': 'datetime'
        }
    }
    
    configs = pagination_configs or default_configs
    
    # Create paginated directory
    paginated_dir = processed_dir / 'paginated'
    paginator = DataPaginator(paginated_dir)
    
    results = {}
    
    for dataset_name, config in configs.items():
        input_file = processed_dir / f"{dataset_name}.json"
        
        if not input_file.exists():
            logger.warning(f"Dataset file not found: {input_file}")
            continue
        
        # Check file size to determine if pagination is needed
        file_size_mb = input_file.stat().st_size / (1024 * 1024)
        if file_size_mb < 5:  # Skip pagination for files smaller than 5MB
            logger.info(f"Skipping pagination for {dataset_name} ({file_size_mb:.1f}MB - too small)")
            continue
            
        logger.info(f"Paginating {dataset_name} ({file_size_mb:.1f}MB)")
        
        try:
            # Paginate the dataset
            pagination_metadata = paginator.paginate_json_file(
                input_file=input_file,
                base_name=dataset_name,
                page_size=config['page_size'],
                date_column=config.get('date_column')
            )
            
            # Create lightweight summary
            summary_metadata = paginator.create_lightweight_summary(
                pagination_metadata=pagination_metadata,
                sample_size=config.get('sample_size', 100)
            )
            
            results[dataset_name] = {
                'success': True,
                'pagination': pagination_metadata,
                'summary': summary_metadata,
                'original_size_mb': file_size_mb
            }
            
        except Exception as e:
            logger.error(f"Failed to paginate {dataset_name}: {e}")
            results[dataset_name] = {
                'success': False,
                'error': str(e),
                'original_size_mb': file_size_mb
            }
    
    # Create master pagination index
    master_index = {
        'datasets': results,
        'generated_at': datetime.now().isoformat(),
        'pagination_directory': 'paginated/',
        'summary': {
            'total_datasets': len(results),
            'successful_paginations': len([r for r in results.values() if r['success']]),
            'failed_paginations': len([r for r in results.values() if not r['success']])
        }
    }
    
    master_index_path = paginated_dir / 'pagination_master_index.json'
    with open(master_index_path, 'w') as f:
        json.dump(master_index, f, indent=2)
    
    logger.info(f"Pagination complete. Master index saved to {master_index_path}")
    return master_index

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pagination.py <processed_data_directory>")
        sys.exit(1)
    
    processed_data_dir = sys.argv[1]
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run pagination
    results = paginate_large_datasets(processed_data_dir)
    
    print(f"\nPagination Summary:")
    print(f"- Total datasets processed: {results['summary']['total_datasets']}")
    print(f"- Successful paginations: {results['summary']['successful_paginations']}")
    print(f"- Failed paginations: {results['summary']['failed_paginations']}")