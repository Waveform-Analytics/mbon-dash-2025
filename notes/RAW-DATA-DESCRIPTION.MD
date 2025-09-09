# Raw Data Description

Raw data files are located in the `data/raw` folder.

All data (acoustic indices, manual detections, environmental, and RMS SPL data) are from 3 stations in coastal South Carolina: **9M, 14M, and 37M**. 

Data are available for **two years: 2018 and 2021**.

## Directory Structure Overview

```
data/raw/
├── metadata/                    # Metadata and reference files
├── indices/                     # Acoustic indices (2021 only)
├── 2018/                       # 2018 data
│   ├── detections/             # Manual fish/vessel detections
│   ├── environmental/          # Temperature and depth data
│   └── rms_spl/               # RMS sound pressure level data
└── 2021/                       # 2021 data
    ├── detections/             # Manual fish/vessel detections
    ├── environmental/          # Temperature and depth data
    └── rms_spl/               # RMS sound pressure level data
```

## Manual Detection Data

**Source**: ESONS team at USCB  
**Format**: Excel files (.xlsx) with two sheets: Metadata and Data (we primarily use Data sheet)  
**Temporal Resolution**: 2-hour increments for entire year  
**Years Available**: 2018, 2021

### ⚠️ **Data Processing Notes:**
- **Date Column**: Contains complete datetime information (both date and time) - use this directly
- **Time Column**: Contains datetime objects from 1900 with only time portion relevant - do NOT use for datetime parsing
- **Station 37M Issue**: Date column is named `'Date '` (with trailing space) instead of `'Date'`
- **Recommended Processing**: Use only the Date column: `pd.to_datetime(df['Date' if 'Date' in df.columns else 'Date '], errors='coerce')`  

### Files:
**2018 Detections:**
- `data/raw/2018/detections/Master_Manual_9M_2h_2018.xlsx`
- `data/raw/2018/detections/Master_Manual_14M_2h_2018.xlsx`
- `data/raw/2018/detections/Master_Manual_37M_2h_2018.xlsx`

**2021 Detections:**
- `data/raw/2021/detections/Master_Manual_9M_2h_2021.xlsx`
- `data/raw/2021/detections/Master_Manual_14M_2h_2021.xlsx`
- `data/raw/2021/detections/Master_Manual_37M_2h_2021.xlsx`

### Detection Categories:
- **Fish Species**: Silver perch, Oyster toadfish (boat whistle & grunt), Black drum, Spotted seatrout, Red drum, Atlantic croaker, Weakfish
- **Marine Mammals**: Bottlenose dolphin (echolocation, burst pulses, whistles), Right whale, Manatee
- **Anthropogenic**: Vessels, Rain, Waves, Chain, Static
- **Other**: Unknown biological/anthropogenic, Alligator
- **Data Quality**: Intensity scale 0-3 for each species/category

## Environmental Data

**Temporal Resolution**: Temperature (20 min), Depth (1 hour)  
**Years Available**: 2018, 2021  
**Format**: Excel files (.xlsx)

### Temperature Files:
**Column Names**: "Date and time", "Water temp (°C)"
**Processing**: Works correctly with `pd.to_datetime(df['Date and time'], errors='coerce')`

**2018:**
- `data/raw/2018/environmental/Master_9M_Temp_2018.xlsx`
- `data/raw/2018/environmental/Master_14M_Temp_2018.xlsx`
- `data/raw/2018/environmental/Master_37M_Temp_2018.xlsx`

**2021:**
- `data/raw/2021/environmental/Master_9M_Temp_2021.xlsx`
- `data/raw/2021/environmental/Master_14M_Temp_2021.xlsx`
- `data/raw/2021/environmental/Master_37M_Temp_2021.xlsx`

### Depth Files:
**Column Names**: "Date and time", "Water depth (m)"  
**Processing**: Works correctly with `pd.to_datetime(df['Date and time'], errors='coerce')`

**2018:**
- `data/raw/2018/environmental/Master_9M_Depth_2018.xlsx`
- `data/raw/2018/environmental/Master_14M_Depth_2018.xlsx`
- `data/raw/2018/environmental/Master_37M_Depth_2018.xlsx`

**2021:**
- `data/raw/2021/environmental/Master_9M_Depth_2021.xlsx`
- `data/raw/2021/environmental/Master_14M_Depth_2021.xlsx`
- `data/raw/2021/environmental/Master_37M_Depth_2021.xlsx`

## RMS Sound Pressure Level Data

**Temporal Resolution**: 1-hour intervals  
**Years Available**: 2018, 2021  
**Format**: Excel files (.xlsx)  
**Note**: Date and Time are in separate columns and need to be combined

### ⚠️ **Data Processing Notes:**
- **Date Column**: Contains proper date information
- **Time Column**: Contains datetime objects from 1900 - extract only the time component using `.dt.time`
- **Recommended Processing**: 
  ```python
  time_components = df['Time'].dt.time
  combined_datetimes = []
  for date_val, time_val in zip(df['Date'], time_components):
      if pd.notna(date_val) and pd.notna(time_val):
          combined_dt = pd.to_datetime(date_val.date().strftime('%Y-%m-%d') + ' ' + time_val.strftime('%H:%M:%S'))
          combined_datetimes.append(combined_dt)
  ```

### Frequency Bands:
- **Broadband**: 1-40000 Hz
- **Low**: 50-1200 Hz  
- **High**: 7000-40000 Hz

### Files:
**2018:**
- `data/raw/2018/rms_spl/Master_rmsSPL_9M_1h_2018.xlsx`
- `data/raw/2018/rms_spl/Master_rmsSPL_14M_1h_2018.xlsx`
- `data/raw/2018/rms_spl/Master_rmsSPL_37M_1h_2018.xlsx`

**2021:**
- `data/raw/2021/rms_spl/Master_rmsSPL_9M_1h_2021.xlsx`
- `data/raw/2021/rms_spl/Master_rmsSPL_14M_1h_2021.xlsx`
- `data/raw/2021/rms_spl/Master_rmsSPL_37M_1h_2021.xlsx`

## Acoustic Indices

**Years Available**: 2021 only  
**Format**: CSV files  
**Stations**: All three (9M, 14M, 37M)  
**Versions**: Two bandwidth options available

### Index Categories:
60+ acoustic indices organized into categories:
- **Complexity Indices**: Amplitude variation, spatial/temporal activity, energy analysis
- **Diversity Indices**: Biodiversity measures, evenness, entropy metrics  
- **Spectral Indices**: Frequency analysis, energy distribution, balance measures
- **Temporal Indices**: Time-domain analysis, background noise, activity patterns
- **Amplitude Indices**: Sound level measurements, signal-to-noise ratios

### Files:
**FullBW (Full Bandwidth) Version:**
- `data/raw/indices/Acoustic_Indices_9M_2021_FullBW_v2_Final.csv`
- `data/raw/indices/Acoustic_Indices_14M_2021_FullBW_v2_Final.csv`
- `data/raw/indices/Acoustic_Indices_37M_2021_FullBW_v2_Final.csv`

**8kHz Version:**
- `data/raw/indices/Acoustic_Indices_9M_2021_8kHz_v2_Final.csv`
- `data/raw/indices/Acoustic_Indices_14M_2021_8kHz_v2_Final.csv`
- `data/raw/indices/Acoustic_Indices_37M_2021_8kHz_v2_Final.csv`

**Note**: Both bandwidth versions are available. Choice between FullBW vs 8kHz should be made based on analysis needs and computational requirements.

### ⚠️ **Data Processing Notes:**
- **Date Column**: Contains datetime in string format (e.g., '1/2/2021 0:00') 
- **Processing**: Works correctly with `pd.to_datetime(df['Date'], errors='coerce')`

## Metadata Files

### Reference Files:
- `data/raw/metadata/det_column_names.csv` - Column definitions for detection data
- `data/raw/metadata/Updated_Index_Categories_v2.csv` - Acoustic index descriptions and categories  
- `data/raw/metadata/1_Montie Lab_metadata_deployments_2017 to 2022.xlsx` - Deployment metadata

### Detection Categories (from det_column_names.csv):
- **Fish Species** (keep_species=1): Silver perch, Oyster toadfish boat whistle, Oyster toadfish grunt, Black drum, Spotted seatrout, Red drum, Atlantic croaker
- **Marine Mammals**: Bottlenose dolphin echolocation/burst pulses/whistles  
- **Anthropogenic**: Vessels (keep_species=1)
- **Environmental**: Rain, Waves, Chain, Static
- **Other Categories**: Weakfish, Right whale, Alligator, Manatee, Unknown biological/anthropogenic

## Data Coverage Summary

- **Spatial**: 3 stations (9M, 14M, 37M) in coastal South Carolina
- **Temporal**: 2018 and 2021 (acoustic indices only available for 2021)
- **Resolution**: 2-hour (detections), 20-min (temperature), 1-hour (depth, SPL)
- **Species Focus**: 6-7 primary fish species with vessel detection
- **Acoustic Analysis**: 60+ indices with two bandwidth options (2021 only)