#!/usr/bin/env python3

import pandas as pd
import numpy as np

# Load data
df = pd.read_parquet('../data/processed/aligned_dataset_2021.parquet')
indices_9M = pd.read_csv('../data/raw/indices/Acoustic_Indices_9M_2021_FullBW_v2_Final.csv')

print("=== DATETIME ALIGNMENT DEBUG ===")
print()

print("Aligned dataset:")
print(f"  Shape: {df.shape}")
print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"  Sample datetimes:")
for dt in df['datetime'].head(5):
    print(f"    {dt}")

print()
print("Acoustic indices (9M sample):")
print(f"  Shape: {indices_9M.shape}")
print(f"  Columns: {list(indices_9M.columns[:10])}")

# Find datetime column in indices
datetime_col = None
for col in ['datetime', 'DateTime', 'Date', 'time', 'Time']:
    if col in indices_9M.columns:
        datetime_col = col
        break

if datetime_col:
    indices_9M['datetime_parsed'] = pd.to_datetime(indices_9M[datetime_col])
    print(f"  Found datetime column: {datetime_col}")
    print(f"  Date range: {indices_9M['datetime_parsed'].min()} to {indices_9M['datetime_parsed'].max()}")
    print(f"  Sample datetimes:")
    for dt in indices_9M['datetime_parsed'].head(5):
        print(f"    {dt}")
    
    # Check overlap
    print()
    print("OVERLAP ANALYSIS:")
    
    # Create 2-hour floor for indices
    indices_9M['datetime_2h'] = indices_9M['datetime_parsed'].dt.floor('2h')
    
    # Find overlapping times
    aligned_times = set(df['datetime'])
    indices_times = set(indices_9M['datetime_2h'])
    
    print(f"  Aligned dataset unique times: {len(aligned_times)}")
    print(f"  Indices 2h-floored times: {len(indices_times)}")
    print(f"  Overlapping times: {len(aligned_times.intersection(indices_times))}")
    print(f"  Missing from indices: {len(aligned_times - indices_times)}")
    print(f"  Extra in indices: {len(indices_times - aligned_times)}")
    
    # Check a few missing times
    missing_times = list(aligned_times - indices_times)[:5]
    if missing_times:
        print(f"  Sample missing times: {missing_times}")
    
else:
    print("  No datetime column found!")

print()
print("ACOUSTIC INDEX MISSING DATA:")
acoustic_cols = ['ZCR', 'MEANt', 'ACI', 'NBPEAKS']
for col in acoustic_cols:
    if col in df.columns:
        missing_pct = df[col].isna().mean() * 100
        print(f"  {col}: {missing_pct:.1f}% missing")

print()
print("SPL DATA CHECK:")
spl_cols = [col for col in df.columns if 'spl_' in col.lower()]
for col in spl_cols[:3]:
    missing_pct = df[col].isna().mean() * 100
    print(f"  {col}: {missing_pct:.1f}% missing")