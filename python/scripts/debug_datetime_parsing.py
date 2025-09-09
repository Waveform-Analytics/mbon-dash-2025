#!/usr/bin/env python3
"""
Debug script to investigate datetime parsing issues in the acoustic data.
This script will load the raw data and examine the datetime columns to identify
why temporal coverage plots are showing sparse data.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Define constants
STATIONS = ['9M', '14M', '37M']
YEAR = 2021
DATA_DIR = Path("../data/raw")

print("=== DEBUGGING DATETIME PARSING ===")
print(f"Data directory: {DATA_DIR.resolve()}")
print(f"Stations: {STATIONS}")
print(f"Year: {YEAR}")

# Load all data types for debugging
detection_data = {}
temp_data = {}
depth_data = {}
spl_data = {}
indices_data = {}

print("\n=== LOADING DATA FOR DEBUGGING ===")

# Load detection data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "detections" / f"Master_Manual_{station}_2h_{YEAR}.xlsx"
    if file_path.exists():
        try:
            df = pd.read_excel(file_path, sheet_name="Data")
            detection_data[station] = df
            print(f"✓ Detection {station}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading detection {station}: {e}")
    else:
        print(f"✗ Detection file not found: {file_path}")

# Load temperature data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Temp_{YEAR}.xlsx"
    if file_path.exists():
        try:
            df = pd.read_excel(file_path, sheet_name="Data")
            temp_data[station] = df
            print(f"✓ Temperature {station}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading temperature {station}: {e}")
    else:
        print(f"✗ Temperature file not found: {file_path}")

# Load depth data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Depth_{YEAR}.xlsx"
    if file_path.exists():
        try:
            df = pd.read_excel(file_path, sheet_name="Data")
            depth_data[station] = df
            print(f"✓ Depth {station}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading depth {station}: {e}")
    else:
        print(f"✗ Depth file not found: {file_path}")

# Load SPL data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "rms_spl" / f"Master_rmsSPL_{station}_1h_{YEAR}.xlsx"
    if file_path.exists():
        try:
            df = pd.read_excel(file_path, sheet_name="Data")
            spl_data[station] = df
            print(f"✓ SPL {station}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading SPL {station}: {e}")
    else:
        print(f"✗ SPL file not found: {file_path}")

# Load indices data
for station in STATIONS:
    file_path = DATA_DIR / "indices" / f"Acoustic_Indices_{station}_{YEAR}_FullBW_v2_Final.csv"
    if file_path.exists():
        try:
            df = pd.read_csv(file_path)
            indices_data[station] = df
            print(f"✓ Indices {station}: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"✗ Error loading indices {station}: {e}")
    else:
        print(f"✗ Indices file not found: {file_path}")

print("\n" + "="*60)
print("DETAILED DATETIME ANALYSIS")
print("="*60)

for station in STATIONS:
    print(f"\n{'='*20} Station {station} {'='*20}")
    
    # === DETECTION DATA ===
    if station in detection_data:
        print(f"\n--- DETECTION DATA ({station}) ---")
        df_det = detection_data[station]
        print(f"Shape: {df_det.shape}")
        print(f"Columns: {list(df_det.columns)}")
        
        # Check for date/time columns
        date_cols = [col for col in df_det.columns if 'date' in col.lower()]
        time_cols = [col for col in df_det.columns if 'time' in col.lower()]
        print(f"Date-like columns: {date_cols}")
        print(f"Time-like columns: {time_cols}")
        
        # Try different column combinations
        if 'Date' in df_det.columns and 'Time' in df_det.columns:
            print("Found 'Date' and 'Time' columns")
            print("Date sample (first 5):")
            print(df_det['Date'].head().tolist())
            print("Time sample (first 5):")
            print(df_det['Time'].head().tolist())
            
            # Check for null values
            print(f"Date nulls: {df_det['Date'].isnull().sum()}/{len(df_det)}")
            print(f"Time nulls: {df_det['Time'].isnull().sum()}/{len(df_det)}")
            
            # Try parsing
            combined = df_det['Date'].astype(str) + ' ' + df_det['Time'].astype(str)
            print("Combined sample (first 3):")
            print(combined.head(3).tolist())
            
            parsed = pd.to_datetime(combined, errors='coerce')
            valid_dates = parsed.notna().sum()
            print(f"Successfully parsed: {valid_dates}/{len(parsed)} ({100*valid_dates/len(parsed):.1f}%)")
            
            if valid_dates > 0:
                print(f"Date range: {parsed.min()} to {parsed.max()}")
            else:
                print("❌ No valid dates parsed! Checking data types...")
                print(f"Date column dtype: {df_det['Date'].dtype}")
                print(f"Time column dtype: {df_det['Time'].dtype}")
    else:
        print(f"❌ No detection data for station {station}")
    
    # === SPL DATA ===
    if station in spl_data:
        print(f"\n--- SPL DATA ({station}) ---")
        df_spl = spl_data[station]
        print(f"Shape: {df_spl.shape}")
        print(f"Columns: {list(df_spl.columns)}")
        
        if 'Date' in df_spl.columns and 'Time' in df_spl.columns:
            print("Date sample:", df_spl['Date'].head(3).tolist())
            print("Time sample:", df_spl['Time'].head(3).tolist())
            print(f"Date nulls: {df_spl['Date'].isnull().sum()}")
            print(f"Time nulls: {df_spl['Time'].isnull().sum()}")
            
            combined = df_spl['Date'].astype(str) + ' ' + df_spl['Time'].astype(str)
            parsed = pd.to_datetime(combined, errors='coerce')
            valid_dates = parsed.notna().sum()
            print(f"Successfully parsed: {valid_dates}/{len(parsed)} ({100*valid_dates/len(parsed):.1f}%)")
            
            if valid_dates > 0:
                print(f"Date range: {parsed.min()} to {parsed.max()}")
    else:
        print(f"❌ No SPL data for station {station}")
    
    # === TEMPERATURE DATA ===
    if station in temp_data:
        print(f"\n--- TEMPERATURE DATA ({station}) ---")
        df_temp = temp_data[station]
        print(f"Shape: {df_temp.shape}")
        print(f"Columns: {list(df_temp.columns)}")
        
        if 'Date and time' in df_temp.columns:
            print("Date and time sample:", df_temp['Date and time'].head(3).tolist())
            parsed = pd.to_datetime(df_temp['Date and time'], errors='coerce')
            valid_dates = parsed.notna().sum()
            print(f"Successfully parsed: {valid_dates}/{len(parsed)} ({100*valid_dates/len(parsed):.1f}%)")
            if valid_dates > 0:
                print(f"Date range: {parsed.min()} to {parsed.max()}")
    else:
        print(f"❌ No temperature data for station {station}")
    
    # === DEPTH DATA ===
    if station in depth_data:
        print(f"\n--- DEPTH DATA ({station}) ---")
        df_depth = depth_data[station]
        print(f"Shape: {df_depth.shape}")
        print(f"Columns: {list(df_depth.columns)}")
        
        if 'Date and time' in df_depth.columns:
            print("Date and time sample:", df_depth['Date and time'].head(3).tolist())
            parsed = pd.to_datetime(df_depth['Date and time'], errors='coerce')
            valid_dates = parsed.notna().sum()
            print(f"Successfully parsed: {valid_dates}/{len(parsed)} ({100*valid_dates/len(parsed):.1f}%)")
            if valid_dates > 0:
                print(f"Date range: {parsed.min()} to {parsed.max()}")
    else:
        print(f"❌ No depth data for station {station}")
    
    # === INDICES DATA ===
    if station in indices_data:
        print(f"\n--- INDICES DATA ({station}) ---")
        df_idx = indices_data[station]
        print(f"Shape: {df_idx.shape}")
        print(f"Columns (first 10): {list(df_idx.columns)[:10]}")
        
        # Check for datetime columns
        datetime_cols = [col for col in df_idx.columns if any(x in col.lower() for x in ['date', 'time'])]
        print(f"Datetime-like columns: {datetime_cols}")
        
        # Try common datetime column names
        for col_name in ['datetime', 'DateTime', 'Date', 'time', 'Time']:
            if col_name in df_idx.columns:
                print(f"Found '{col_name}' column")
                print(f"Sample values: {df_idx[col_name].head(3).tolist()}")
                parsed = pd.to_datetime(df_idx[col_name], errors='coerce')
                valid_dates = parsed.notna().sum()
                print(f"Successfully parsed: {valid_dates}/{len(parsed)} ({100*valid_dates/len(parsed):.1f}%)")
                if valid_dates > 0:
                    print(f"Date range: {parsed.min()} to {parsed.max()}")
                break
        else:
            print("❌ No standard datetime column found")
    else:
        print(f"❌ No indices data for station {station}")

print(f"\n{'='*60}")
print("SUMMARY")
print("="*60)

print(f"Detection data loaded: {list(detection_data.keys())}")
print(f"Temperature data loaded: {list(temp_data.keys())}")
print(f"Depth data loaded: {list(depth_data.keys())}")
print(f"SPL data loaded: {list(spl_data.keys())}")
print(f"Indices data loaded: {list(indices_data.keys())}")