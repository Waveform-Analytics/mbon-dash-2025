#!/usr/bin/env python3
"""
Fixed temporal coverage analysis that correctly handles the different datetime formats:

1. Detection data: Use only 'Date' column (contains both date and time)
2. SPL data: Combine 'Date' and 'Time' columns, but extract only time portion from Time column
3. Temperature/Depth: Use 'Date and time' column (already works)
4. Indices: Use 'Date' column (already works)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Define constants
STATIONS = ['9M', '14M', '37M']
YEAR = 2021
DATA_DIR = Path("../data/raw")

# Load all data types
detection_data = {}
temp_data = {}
depth_data = {}
spl_data = {}
indices_data = {}

print("Loading data...")

# Load detection data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "detections" / f"Master_Manual_{station}_2h_{YEAR}.xlsx"
    if file_path.exists():
        df = pd.read_excel(file_path, sheet_name="Data")
        detection_data[station] = df
        print(f"✓ Detection {station}: {len(df)} rows")

# Load SPL data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "rms_spl" / f"Master_rmsSPL_{station}_1h_{YEAR}.xlsx"
    if file_path.exists():
        df = pd.read_excel(file_path, sheet_name="Data")
        spl_data[station] = df
        print(f"✓ SPL {station}: {len(df)} rows")

# Load temperature data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Temp_{YEAR}.xlsx"
    if file_path.exists():
        df = pd.read_excel(file_path, sheet_name="Data")
        temp_data[station] = df
        print(f"✓ Temperature {station}: {len(df)} rows")

# Load depth data
for station in STATIONS:
    file_path = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station}_Depth_{YEAR}.xlsx"
    if file_path.exists():
        df = pd.read_excel(file_path, sheet_name="Data")
        depth_data[station] = df
        print(f"✓ Depth {station}: {len(df)} rows")

# Load indices data
for station in STATIONS:
    file_path = DATA_DIR / "indices" / f"Acoustic_Indices_{station}_{YEAR}_FullBW_v2_Final.csv"
    if file_path.exists():
        df = pd.read_csv(file_path)
        indices_data[station] = df
        print(f"✓ Indices {station}: {len(df)} rows")

print("\n" + "="*60)
print("FIXED TEMPORAL COVERAGE ANALYSIS")
print("="*60)

# Create temporal coverage analysis with correct datetime handling
temporal_analysis = {}

fig_temporal, axes_temporal = plt.subplots(len(STATIONS), 1, figsize=(15, 5*len(STATIONS)))
if len(STATIONS) == 1:
    axes_temporal = [axes_temporal]

for i, station in enumerate(STATIONS):
    coverage_data_list = []
    
    print(f"\n--- Processing Station {station} ---")
    
    # 1. DETECTION DATA - Use only 'Date' column (has both date and time)
    if station in detection_data:
        df_det = detection_data[station]
        
        # Handle Station 37M which has 'Date ' with trailing space
        date_col = 'Date' if 'Date' in df_det.columns else 'Date '
        
        if date_col in df_det.columns:
            # The Date column already contains full datetime
            datetime_series = pd.to_datetime(df_det[date_col], errors='coerce')
            valid_dates = datetime_series.dropna()
            coverage_data_list.extend([('Detections (2h)', dt) for dt in valid_dates])
            print(f"  Detection dates: {len(valid_dates)}/{len(df_det)} parsed successfully")
            if len(valid_dates) > 0:
                print(f"  Date range: {valid_dates.min()} to {valid_dates.max()}")
    
    # 2. SPL DATA - Combine Date and Time, but handle Time column correctly
    if station in spl_data:
        df_spl = spl_data[station]
        
        if 'Date' in df_spl.columns and 'Time' in df_spl.columns:
            # Extract just the time component from the Time column (ignore the 1900 date part)
            time_components = df_spl['Time'].dt.time  # Extract time only
            
            # Combine date with time
            combined_datetimes = []
            for idx, (date_val, time_val) in enumerate(zip(df_spl['Date'], time_components)):
                try:
                    # Combine date with time component
                    if pd.notna(date_val) and pd.notna(time_val):
                        combined_dt = pd.to_datetime(date_val.date().strftime('%Y-%m-%d') + ' ' + time_val.strftime('%H:%M:%S'))
                        combined_datetimes.append(combined_dt)
                    else:
                        combined_datetimes.append(pd.NaT)
                except Exception:
                    combined_datetimes.append(pd.NaT)
            
            # Convert to Series and filter valid dates
            datetime_series = pd.Series(combined_datetimes)
            valid_dates = datetime_series.dropna()
            coverage_data_list.extend([('SPL (1h)', dt) for dt in valid_dates])
            print(f"  SPL dates: {len(valid_dates)}/{len(df_spl)} parsed successfully")
            if len(valid_dates) > 0:
                print(f"  Date range: {valid_dates.min()} to {valid_dates.max()}")
    
    # 3. TEMPERATURE DATA - Use 'Date and time' column (already works fine)
    if station in temp_data:
        df_temp = temp_data[station]
        if 'Date and time' in df_temp.columns:
            datetime_series = pd.to_datetime(df_temp['Date and time'], errors='coerce')
            valid_dates = datetime_series.dropna()
            coverage_data_list.extend([('Temperature (20m)', dt) for dt in valid_dates])
            print(f"  Temperature dates: {len(valid_dates)}/{len(df_temp)} parsed successfully")
    
    # 4. DEPTH DATA - Use 'Date and time' column (already works fine)  
    if station in depth_data:
        df_depth = depth_data[station]
        if 'Date and time' in df_depth.columns:
            datetime_series = pd.to_datetime(df_depth['Date and time'], errors='coerce')
            valid_dates = datetime_series.dropna()
            coverage_data_list.extend([('Depth (1h)', dt) for dt in valid_dates])
            print(f"  Depth dates: {len(valid_dates)}/{len(df_depth)} parsed successfully")
    
    # 5. INDICES DATA - Use 'Date' column (already works fine)
    if station in indices_data:
        df_idx = indices_data[station]
        if 'Date' in df_idx.columns:
            datetime_series = pd.to_datetime(df_idx['Date'], errors='coerce')
            valid_dates = datetime_series.dropna()
            coverage_data_list.extend([('Indices', dt) for dt in valid_dates])
            print(f"  Indices dates: {len(valid_dates)}/{len(df_idx)} parsed successfully")
    
    # Create timeline plot
    if coverage_data_list:
        coverage_df = pd.DataFrame(coverage_data_list, columns=['Data_Type', 'DateTime'])
        
        # Plot timeline
        ax = axes_temporal[i]
        colors = ['blue', 'green', 'red', 'orange', 'purple']
        
        for j, data_type in enumerate(coverage_df['Data_Type'].unique()):
            subset = coverage_df[coverage_df['Data_Type'] == data_type]
            ax.scatter(subset['DateTime'], [j] * len(subset), alpha=0.6, s=2, 
                      color=colors[j % len(colors)], label=data_type)
        
        ax.set_yticks(range(len(coverage_df['Data_Type'].unique())))
        ax.set_yticklabels(coverage_df['Data_Type'].unique())
        ax.set_title(f'Station {station} - Temporal Coverage (Fixed)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Store analysis results
        temporal_analysis[station] = {
            'data_types': len(coverage_df['Data_Type'].unique()),
            'total_points': len(coverage_df),
            'date_range': (coverage_df['DateTime'].min(), coverage_df['DateTime'].max())
        }
        
        print(f"  Total data points plotted: {len(coverage_df)}")

plt.tight_layout()
plt.show()

print(f"\n{'='*60}")
print("TEMPORAL COVERAGE SUMMARY")
print("="*60)

for station, info in temporal_analysis.items():
    if info['date_range'][0] is not pd.NaT:
        print(f"\n{station}:")
        print(f"  Data types: {info['data_types']}")
        print(f"  Total points: {info['total_points']:,}")
        print(f"  Date range: {info['date_range'][0].strftime('%Y-%m-%d %H:%M')} to {info['date_range'][1].strftime('%Y-%m-%d %H:%M')}")
    else:
        print(f"\n{station}: No valid temporal data found")

print(f"\n{'='*60}")
print("RECOMMENDATIONS FOR MARIMO NOTEBOOK")
print("="*60)

print("""
Based on this analysis, update your marimo notebook temporal coverage cell to:

1. For Detection data: Use only the 'Date' column (handle 'Date ' for station 37M)
2. For SPL data: Extract time from Time column and combine with Date
3. Keep Temperature/Depth/Indices parsing as-is (they work correctly)

Key code changes needed:
- Detection: df_temporal_det['datetime'] = pd.to_datetime(df_temporal_det[date_col], errors='coerce')
- SPL: Combine date with time component properly
- Handle Station 37M's 'Date ' column name
""")