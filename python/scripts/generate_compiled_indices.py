#!/usr/bin/env python3
"""Generate compiled indices JSON file from all available acoustic indices CSV files.

This script reads all acoustic indices CSV files and compiles them into a single
large JSON file for intermediate processing. The file is stored locally and
contains all raw indices data organized by station and bandwidth.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List
import sys
import logging
from datetime import datetime

# Add the mbon_analysis package to the path
sys.path.append(str(Path(__file__).parent.parent))

from mbon_analysis.data.loaders import create_loader


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('compiled_indices_generation.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def compile_indices_data(data_root: Path, output_path: Path) -> Dict[str, Any]:
    """Compile all acoustic indices data into a single structure.
    
    Args:
        data_root: Path to the data directory
        output_path: Path where the compiled JSON should be saved
        
    Returns:
        Dictionary containing all compiled indices data
    """
    logger = logging.getLogger(__name__)
    
    # Create loader
    loader = create_loader(data_root)
    
    # Get available stations
    stations = loader.get_available_stations()
    logger.info(f"Found stations: {stations}")
    
    # Define bandwidths
    bandwidths = ["FullBW", "8kHz"]
    
    compiled_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "Compiled acoustic indices data from all available CSV files",
            "version": "1.0.0",
            "total_files_processed": 0,
            "total_records": 0
        },
        "stations": {},
        "summary": {
            "stations": {},
            "bandwidths": {},
            "total_files": 0,
            "total_records": 0
        }
    }
    
    total_files = 0
    total_records = 0
    
    # Process each station and bandwidth combination
    for station in stations:
        logger.info(f"Processing station: {station}")
        compiled_data["stations"][station] = {}
        compiled_data["summary"]["stations"][station] = {
            "total_records": 0,
            "bandwidths": {}
        }
        
        for bandwidth in bandwidths:
            try:
                logger.info(f"  Loading {bandwidth} data for {station}")
                
                # Load the indices data
                df = loader.load_acoustic_indices(station, bandwidth)
                
                # Convert DataFrame to records (list of dictionaries)
                records = df.to_dict('records')
                
                # Store the data
                compiled_data["stations"][station][bandwidth] = {
                    "data": records,
                    "columns": list(df.columns),
                    "shape": df.shape,
                    "file_info": {
                        "filename": f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv",
                        "records_count": len(records),
                        "columns_count": len(df.columns)
                    }
                }
                
                # Update summary statistics
                compiled_data["summary"]["stations"][station]["bandwidths"][bandwidth] = len(records)
                compiled_data["summary"]["stations"][station]["total_records"] += len(records)
                
                if bandwidth not in compiled_data["summary"]["bandwidths"]:
                    compiled_data["summary"]["bandwidths"][bandwidth] = 0
                compiled_data["summary"]["bandwidths"][bandwidth] += len(records)
                
                total_files += 1
                total_records += len(records)
                
                logger.info(f"    Loaded {len(records)} records from {bandwidth} data")
                
            except FileNotFoundError as e:
                logger.warning(f"    File not found for {station} {bandwidth}: {e}")
                compiled_data["stations"][station][bandwidth] = {
                    "error": "File not found",
                    "data": [],
                    "columns": [],
                    "shape": (0, 0),
                    "file_info": {
                        "filename": f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv",
                        "records_count": 0,
                        "columns_count": 0
                    }
                }
            except Exception as e:
                logger.error(f"    Error processing {station} {bandwidth}: {e}")
                compiled_data["stations"][station][bandwidth] = {
                    "error": str(e),
                    "data": [],
                    "columns": [],
                    "shape": (0, 0),
                    "file_info": {
                        "filename": f"Acoustic_Indices_{station}_2021_{bandwidth}_v2_Final.csv",
                        "records_count": 0,
                        "columns_count": 0
                    }
                }
    
    # Update final metadata
    compiled_data["metadata"]["total_files_processed"] = total_files
    compiled_data["metadata"]["total_records"] = total_records
    compiled_data["summary"]["total_files"] = total_files
    compiled_data["summary"]["total_records"] = total_records
    
    logger.info(f"Compilation complete: {total_files} files, {total_records} total records")
    
    return compiled_data


def save_compiled_data(data: Dict[str, Any], output_path: Path):
    """Save compiled data to JSON file.
    
    Args:
        data: Compiled data dictionary
        output_path: Path where to save the JSON file
    """
    logger = logging.getLogger(__name__)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save with pretty formatting for readability (though file will be large)
    logger.info(f"Saving compiled data to: {output_path}")
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    # Get file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"File saved successfully. Size: {file_size_mb:.2f} MB")


def main():
    """Main execution function."""
    logger = setup_logging()
    
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Option 1: Use current structure (python/data)
    current_data_root = script_dir.parent / "data"
    
    # Option 2: Use top-level data directory (recommended)
    top_level_data_root = project_root / "data"
    
    # Check which data directory exists and use it
    if top_level_data_root.exists():
        data_root = top_level_data_root
        logger.info("Using top-level data directory")
    elif current_data_root.exists():
        data_root = current_data_root
        logger.info("Using python/data directory")
    else:
        logger.error("No data directory found!")
        sys.exit(1)
    
    # Set output path in processed directory
    output_path = data_root / "processed" / "compiled_indices.json"
    
    logger.info(f"Data root: {data_root}")
    logger.info(f"Output path: {output_path}")
    
    try:
        # Compile the data
        compiled_data = compile_indices_data(data_root, output_path)
        
        # Save the compiled data
        save_compiled_data(compiled_data, output_path)
        
        logger.info("Compiled indices generation completed successfully!")
        
        # Print summary
        summary = compiled_data["summary"]
        print(f"\nSummary:")
        print(f"  Total files processed: {summary['total_files']}")
        print(f"  Total records: {summary['total_records']:,}")
        print(f"  Stations: {list(summary['stations'].keys())}")
        print(f"  Bandwidths: {list(summary['bandwidths'].keys())}")
        print(f"  Output file: {output_path}")
        
    except Exception as e:
        logger.error(f"Error during compilation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
