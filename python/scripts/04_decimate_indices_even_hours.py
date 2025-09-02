#!/usr/bin/env python3
"""
Decimate compiled_indices.json to keep only even hours (0, 2, 4, 6, etc.)
to align with the 2-hour resolution of detections data.

This creates a new file: compiled_indices_even_hours.json
"""

import json
import os
from datetime import datetime
from pathlib import Path

def parse_date_string(date_str: str) -> datetime:
    """Parse date string in format 'MM/DD/YYYY HH:MM'"""
    return datetime.strptime(date_str, "%m/%d/%Y %H:%M")

def is_even_hour(date_str: str) -> bool:
    """Check if the hour in the date string is even (0, 2, 4, 6, ...)"""
    dt = parse_date_string(date_str)
    return dt.hour % 2 == 0

def decimate_indices_to_even_hours(input_file: str, output_file: str):
    """
    Load compiled indices and keep only records with even hours.
    """
    print(f"Loading data from {input_file}...")
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Create new data structure
    decimated_data = {
        "metadata": {
            **data["metadata"],
            "description": "Compiled acoustic indices data decimated to even hours (0, 2, 4, 6, ...) to align with 2-hour detection data resolution",
            "processing_note": "Original data decimated from hourly to 2-hourly resolution by keeping only even hours",
            "decimated_at": datetime.now().isoformat(),
            "original_total_records": data["metadata"]["total_records"]
        },
        "stations": {}
    }
    
    total_original_records = 0
    total_decimated_records = 0
    
    # Process each station
    for station_id, station_data in data["stations"].items():
        print(f"Processing station {station_id}...")
        decimated_data["stations"][station_id] = {}
        
        # Process each year
        for year, year_data in station_data.items():
            decimated_data["stations"][station_id][year] = {}
            
            # Process each bandwidth
            for bandwidth, bandwidth_data in year_data.items():
                original_records = bandwidth_data["data"]
                original_count = len(original_records)
                
                # Filter to keep only even hours
                decimated_records = [
                    record for record in original_records 
                    if is_even_hour(record["Date"])
                ]
                decimated_count = len(decimated_records)
                
                # Store decimated data
                decimated_data["stations"][station_id][year][bandwidth] = {
                    "data": decimated_records
                }
                
                total_original_records += original_count
                total_decimated_records += decimated_count
                
                print(f"  {station_id} {year} {bandwidth}: {original_count} → {decimated_count} records ({decimated_count/original_count*100:.1f}%)")
    
    # Update metadata with actual counts
    decimated_data["metadata"]["total_records"] = total_decimated_records
    decimated_data["metadata"]["decimation_ratio"] = total_decimated_records / total_original_records
    
    print(f"\nOverall: {total_original_records} → {total_decimated_records} records ({total_decimated_records/total_original_records*100:.1f}%)")
    
    # Save decimated data
    print(f"Saving decimated data to {output_file}...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(decimated_data, f, indent=2)
    
    # Get file size
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Created {output_file} ({file_size_mb:.1f} MB)")
    
    return decimated_data

def main():
    """Main function to run the decimation process"""
    # Set up paths relative to script location
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    input_file = project_root / "data" / "processed" / "compiled_indices.json"
    output_file = project_root / "data" / "processed" / "compiled_indices_even_hours.json"
    
    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return
    
    print("=" * 60)
    print("MBON Acoustic Indices Decimation to Even Hours")
    print("=" * 60)
    
    decimate_indices_to_even_hours(str(input_file), str(output_file))
    
    print("\n" + "=" * 60)
    print("Decimation completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()