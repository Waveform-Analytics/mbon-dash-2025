#!/usr/bin/env python3
"""Script to check actual record counts in raw manual detection files."""

import pandas as pd
from pathlib import Path

def check_detection_files():
    base_path = Path('../data/raw')
    
    total_records = 0
    file_counts = {}
    
    # Check 2018 files
    for year in ['2018', '2021']:
        year_path = base_path / year / 'detections'
        if year_path.exists():
            print(f"\n=== {year} Detection Files ===")
            year_total = 0
            
            for file_path in year_path.glob('Master_Manual_*.xlsx'):
                try:
                    df = pd.read_excel(file_path)
                    record_count = len(df)
                    print(f"{file_path.name}: {record_count:,} records")
                    
                    file_counts[file_path.name] = record_count
                    year_total += record_count
                    total_records += record_count
                    
                    # Show first few columns to understand structure
                    if record_count > 0:
                        print(f"  Columns: {list(df.columns[:5])}...")
                        print(f"  Sample dates: {df.iloc[0:2, 0].tolist() if len(df) > 0 else 'No data'}")
                    
                except Exception as e:
                    print(f"Error reading {file_path.name}: {e}")
            
            print(f"Year {year} total: {year_total:,} records")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total detection records across all files: {total_records:,}")
    
    # Also check environmental files for comparison
    print(f"\n=== Environmental Files (for comparison) ===")
    env_total = 0
    for year in ['2018', '2021']:
        year_path = base_path / year / 'environmental'
        if year_path.exists():
            for file_path in year_path.glob('Master_*_Temp_*.xlsx'):
                try:
                    df = pd.read_excel(file_path)
                    record_count = len(df)
                    print(f"{file_path.name}: {record_count:,} records")
                    env_total += record_count
                except Exception as e:
                    print(f"Error reading {file_path.name}: {e}")
    
    print(f"Total environmental records: {env_total:,}")

if __name__ == "__main__":
    check_detection_files()