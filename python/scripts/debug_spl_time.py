#!/usr/bin/env python3
"""
Debug SPL Time column to understand its actual format
"""

import pandas as pd
from pathlib import Path

# Define constants
STATIONS = ['9M', '14M', '37M']
YEAR = 2021
DATA_DIR = Path("../data/raw")

print("=== SPL TIME COLUMN DEBUGGING ===")

for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "rms_spl" / f"Master_rmsSPL_{station}_1h_{YEAR}.xlsx"
    
    if file_path.exists():
        print(f"\n--- Station {station} ---")
        df = pd.read_excel(file_path, sheet_name="Data")
        
        print(f"Columns: {list(df.columns)}")
        print(f"Shape: {df.shape}")
        
        if 'Date' in df.columns:
            print(f"\nDate column:")
            print(f"  Type: {df['Date'].dtype}")
            print(f"  Sample: {df['Date'].head(3).tolist()}")
            print(f"  Is datetime? {pd.api.types.is_datetime64_any_dtype(df['Date'])}")
        
        if 'Time' in df.columns:
            print(f"\nTime column:")
            print(f"  Type: {df['Time'].dtype}")
            print(f"  Sample: {df['Time'].head(3).tolist()}")
            print(f"  Is datetime? {pd.api.types.is_datetime64_any_dtype(df['Time'])}")
            print(f"  Is string? {df['Time'].dtype == 'object'}")
            print(f"  Is numeric? {pd.api.types.is_numeric_dtype(df['Time'])}")
            
            # Try different approaches
            print(f"\n  Attempting different parsing approaches:")
            
            # Check if it's actually a string that looks like time
            sample_time = df['Time'].iloc[0]
            print(f"    First value type: {type(sample_time)}")
            print(f"    First value: {repr(sample_time)}")
            
            # If it's a datetime object, try extracting time
            if pd.api.types.is_datetime64_any_dtype(df['Time']):
                try:
                    time_only = df['Time'].dt.time.head(3)
                    print(f"    .dt.time works: {time_only.tolist()}")
                except Exception as e:
                    print(f"    .dt.time failed: {e}")
            
            # If it's a string, try parsing it
            elif df['Time'].dtype == 'object':
                print(f"    String values: {df['Time'].head(5).tolist()}")
                # Try to parse as time
                try:
                    parsed_times = pd.to_datetime(df['Time'].head(3), format='%H:%M:%S').dt.time
                    print(f"    Parsed as time: {parsed_times.tolist()}")
                except Exception as e:
                    print(f"    Time parsing failed: {e}")
            
            # Try combining with Date in different ways
            print(f"\n  Attempting Date + Time combination:")
            try:
                # Method 1: Simple string concatenation
                combined_str = df['Date'].astype(str) + ' ' + df['Time'].astype(str)
                print(f"    String combination sample: {combined_str.head(2).tolist()}")
                parsed_combined = pd.to_datetime(combined_str.head(3), errors='coerce')
                print(f"    Parsed result: {parsed_combined.tolist()}")
                valid_count = parsed_combined.notna().sum()
                print(f"    Valid parses: {valid_count}/3")
            except Exception as e:
                print(f"    Combination failed: {e}")

    else:
        print(f"File not found: {file_path}")

print(f"\n{'='*50}")
print("SUMMARY")
print("="*50)
print("Check the output above to see the actual format of Date and Time columns")
print("We need to adapt our parsing approach based on what we find")