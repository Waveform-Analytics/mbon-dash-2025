#!/usr/bin/env python3
"""Quick script to check all stations in deployment metadata."""

import pandas as pd
from pathlib import Path

# Read deployment metadata
metadata_path = Path('../data/raw/metadata/1_Montie Lab_metadata_deployments_2017 to 2022.xlsx')
df = pd.read_excel(metadata_path)

# Get unique stations
unique_stations = df['Station'].dropna().unique()
print(f"Total unique stations: {len(unique_stations)}")
print("\nAll stations:")
for station in sorted(unique_stations):
    print(f"  - {station}")

# Check which columns have location data
print("\nColumns in metadata:")
print(df.columns.tolist())

# Show sample of location data
print("\nSample station data:")
sample_df = df[['Station', 'GPS Lat', 'GPS Long', 'Platform Type', 'Depth (m)']].dropna(subset=['Station']).drop_duplicates(subset=['Station'])
print(sample_df.head(10))