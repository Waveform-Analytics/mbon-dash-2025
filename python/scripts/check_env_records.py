#!/usr/bin/env python3
"""Script to check actual record counts in environmental data files."""

import pandas as pd
from pathlib import Path

def check_environmental_files():
    base_path = Path('../data/raw')
    
    total_records = 0
    file_counts = {}
    
    print("=== Environmental Data Files ===")
    
    # Check both years and both data types
    for year in ['2018', '2021']:
        year_path = base_path / year / 'environmental'
        if year_path.exists():
            print(f"\n--- {year} Environmental Files ---")
            year_total = 0
            
            # Check all environmental files in this year
            for file_path in year_path.glob('Master_*M_*.xlsx'):
                try:
                    # Try reading the file
                    df = pd.read_excel(file_path)
                    record_count = len(df)
                    
                    print(f"{file_path.name}: {record_count:,} records")
                    
                    # Show structure to understand the data
                    if record_count > 0:
                        print(f"  Columns: {list(df.columns[:5])}...")
                        # Look for actual data (skip header rows)
                        non_null_rows = df.dropna(how='all')
                        print(f"  Non-empty rows: {len(non_null_rows):,}")
                        
                        # Show first few data rows
                        if len(non_null_rows) > 0:
                            print(f"  Sample data (first 3 rows):")
                            for i in range(min(3, len(non_null_rows))):
                                row_data = non_null_rows.iloc[i].tolist()[:3]  # First 3 columns
                                print(f"    {row_data}")
                    
                    file_counts[file_path.name] = record_count
                    year_total += record_count
                    total_records += record_count
                    
                except Exception as e:
                    print(f"Error reading {file_path.name}: {e}")
            
            print(f"Year {year} total: {year_total:,} records")
    
    print(f"\n=== ENVIRONMENTAL DATA SUMMARY ===")
    print(f"Total environmental records: {total_records:,}")
    
    # Calculate expected records
    stations = 3  # 9M, 14M, 37M
    years = 2     # 2018, 2021
    data_types = 2  # Temp and Depth
    hours_per_year = 8760  # 24 * 365
    
    expected_total = stations * years * data_types * hours_per_year
    print(f"Expected records (3 stations × 2 years × 2 data types × 8760 hours): {expected_total:,}")

if __name__ == "__main__":
    check_environmental_files()