# Data File Column Reference

This document lists the actual column names found in each processed data file.
Updated automatically by analyzing all parquet files in data/processed/.

## Notebook 01 Files

### `01_depth_14M_2021.parquet`
- **Shape**: 20,731 rows × 3 columns
- **Size**: 0.5 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Date and time']`
- **Environmental** (1): `['Water depth (m)']`

**Missing Values:**
- `Water depth (m)`: 3 (0.0%)

### `01_depth_37M_2021.parquet`
- **Shape**: 20,736 rows × 3 columns
- **Size**: 0.5 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Date and time']`
- **Environmental** (1): `['Water depth (m)']`

**Missing Values:**
- `Water depth (m)`: 1 (0.0%)

### `01_depth_9M_2021.parquet`
- **Shape**: 20,733 rows × 3 columns
- **Size**: 0.5 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Date and time']`
- **Environmental** (1): `['Water depth (m)']`

**Missing Values:**
- `Water depth (m)`: 2 (0.0%)

### `01_detection_columns.parquet`
- **Shape**: 33 rows × 7 columns
- **Size**: 0.0 MB

**Column Categories:**
- **Acoustic Indices** (4): `['long_name', 'short_name', 'type', 'group']`
- **Detections** (1): `['keep_species']`
- **Other** (2): `['Unnamed: 5', 'Unnamed: 6']`

**Missing Values:**
- `Unnamed: 5`: 33 (100.0%)
- `Unnamed: 6`: 33 (100.0%)

### `01_detections_14M_2021.parquet`
- **Shape**: 4,380 rows × 16 columns
- **Size**: 1.0 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (2): `['File', 'datetime']`
- **Temporal** (1): `['Time']`
- **Acoustic Indices** (1): `['Date']`
- **Detections** (6): `['Black drum', 'Bottlenose dolphin echolocation', 'Bottlenose dolphin burst pulses', 'Vessel', 'Spotted seatrout', 'Bottlenose dolphin whistles']`
- **Other** (6): `['Deployment ID', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt', 'Red drum', 'Atlantic croaker', 'Silver perch']`

**Missing Values:**
- `Bottlenose dolphin echolocation`: 1 (0.0%)
- `Bottlenose dolphin burst pulses`: 1 (0.0%)
- `Bottlenose dolphin whistles`: 1 (0.0%)

### `01_detections_37M_2021.parquet`
- **Shape**: 4,380 rows × 16 columns
- **Size**: 1.2 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (2): `['File', 'datetime']`
- **Temporal** (1): `['Time']`
- **Detections** (6): `['Black drum', 'Bottlenose dolphin echolocation', 'Bottlenose dolphin burst pulses', 'Vessel', 'Spotted seatrout', 'Bottlenose dolphin whistles']`
- **Other** (7): `['Deployment ID', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt', 'Date ', 'Red drum', 'Atlantic croaker', 'Silver perch']`

**Missing Values:**
- `File`: 1 (0.0%)
- `Black drum`: 1 (0.0%)
- `Oyster toadfish boat whistle`: 1 (0.0%)
- `Bottlenose dolphin burst pulses`: 3 (0.1%)
- `Oyster toadfish grunt`: 1 (0.0%)
- `Vessel`: 1 (0.0%)
- `Red drum`: 1 (0.0%)
- `Spotted seatrout`: 1 (0.0%)
- `Bottlenose dolphin whistles`: 3 (0.1%)
- `Atlantic croaker`: 1 (0.0%)
- `Silver perch`: 1 (0.0%)

### `01_detections_9M_2021.parquet`
- **Shape**: 4,380 rows × 16 columns
- **Size**: 1.0 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (2): `['File', 'datetime']`
- **Temporal** (1): `['Time']`
- **Acoustic Indices** (1): `['Date']`
- **Detections** (6): `['Black drum', 'Bottlenose dolphin echolocation', 'Bottlenose dolphin burst pulses', 'Vessel', 'Spotted seatrout', 'Bottlenose dolphin whistles']`
- **Other** (6): `['Deployment ID', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt', 'Red drum', 'Atlantic croaker', 'Silver perch']`

### `01_indices_14M_2021.parquet`
- **Shape**: 8,735 rows × 65 columns
- **Size**: 29.5 MB

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Acoustic Indices** (43): `['Date', 'Filename', 'ZCR', 'VARt', 'SKEWt', 'KURTt', 'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf', 'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'NDSI', 'rBA', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI', 'LFC', 'MFC', 'HFC', 'TFSD', 'H_Renyi', 'H_gamma', 'RAOQ', 'AGI', 'nROI', 'aROI']`
- **Detections** (13): `['ACTtFraction', 'ACTtCount', 'ACTtMean', 'EVNtFraction', 'ACI', 'ACI_by_band', 'ACTspFract', 'ACTspCount', 'ACTspMean', 'EVNspFract', 'EVNspMean', 'EVNspCount', 'H_Havrda']`
- **Statistics** (4): `['MEANt', 'EVNtMean', 'EVNtCount', 'MEANf']`
- **Other** (4): `['FrequencyResolution', 'AnthroEnergy', 'H_pairedShannon', 'H_GiniSimpson']`

### `01_indices_37M_2021.parquet`
- **Shape**: 8,727 rows × 65 columns
- **Size**: 29.5 MB

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Acoustic Indices** (43): `['Date', 'Filename', 'ZCR', 'VARt', 'SKEWt', 'KURTt', 'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf', 'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'NDSI', 'rBA', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI', 'LFC', 'MFC', 'HFC', 'TFSD', 'H_Renyi', 'H_gamma', 'RAOQ', 'AGI', 'nROI', 'aROI']`
- **Detections** (13): `['ACTtFraction', 'ACTtCount', 'ACTtMean', 'EVNtFraction', 'ACI', 'ACI_by_band', 'ACTspFract', 'ACTspCount', 'ACTspMean', 'EVNspFract', 'EVNspMean', 'EVNspCount', 'H_Havrda']`
- **Statistics** (4): `['MEANt', 'EVNtMean', 'EVNtCount', 'MEANf']`
- **Other** (4): `['FrequencyResolution', 'AnthroEnergy', 'H_pairedShannon', 'H_GiniSimpson']`

### `01_indices_9M_2021.parquet`
- **Shape**: 8,616 rows × 65 columns
- **Size**: 29.1 MB

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Acoustic Indices** (43): `['Date', 'Filename', 'ZCR', 'VARt', 'SKEWt', 'KURTt', 'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf', 'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'NDSI', 'rBA', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI', 'LFC', 'MFC', 'HFC', 'TFSD', 'H_Renyi', 'H_gamma', 'RAOQ', 'AGI', 'nROI', 'aROI']`
- **Detections** (13): `['ACTtFraction', 'ACTtCount', 'ACTtMean', 'EVNtFraction', 'ACI', 'ACI_by_band', 'ACTspFract', 'ACTspCount', 'ACTspMean', 'EVNspFract', 'EVNspMean', 'EVNspCount', 'H_Havrda']`
- **Statistics** (4): `['MEANt', 'EVNtMean', 'EVNtCount', 'MEANf']`
- **Other** (4): `['FrequencyResolution', 'AnthroEnergy', 'H_pairedShannon', 'H_GiniSimpson']`

### `01_spl_14M_2021.parquet`
- **Shape**: 8,736 rows × 10 columns
- **Size**: 2.0 MB
- **Date Range**: 2021-01-02 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Time']`
- **Environmental** (4): `['Sample Rate (Hz)', 'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']`
- **Acoustic Indices** (1): `['Date']`
- **Detections** (1): `['Recorder type']`
- **Other** (2): `['Deployment ID', 'File number']`

**Missing Values:**
- `Deployment ID`: 1 (0.0%)
- `Recorder type`: 1 (0.0%)
- `Sample Rate (Hz)`: 1 (0.0%)
- `File number`: 1 (0.0%)
- `Broadband (1-40000 Hz)`: 1 (0.0%)
- `Low (50-1200 Hz)`: 1 (0.0%)
- `High (7000-40000 Hz)`: 1 (0.0%)

### `01_spl_37M_2021.parquet`
- **Shape**: 8,736 rows × 10 columns
- **Size**: 2.0 MB
- **Date Range**: 2021-01-02 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Time']`
- **Environmental** (4): `['Sample Rate (Hz)', 'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']`
- **Acoustic Indices** (1): `['Date']`
- **Detections** (1): `['Recorder type']`
- **Other** (2): `['Deployment ID', 'File number']`

**Missing Values:**
- `Deployment ID`: 2 (0.0%)
- `Recorder type`: 2 (0.0%)
- `Sample Rate (Hz)`: 2 (0.0%)
- `File number`: 2 (0.0%)
- `Broadband (1-40000 Hz)`: 2 (0.0%)
- `Low (50-1200 Hz)`: 2 (0.0%)
- `High (7000-40000 Hz)`: 2 (0.0%)

### `01_spl_9M_2021.parquet`
- **Shape**: 8,736 rows × 10 columns
- **Size**: 2.0 MB
- **Date Range**: 2021-01-02 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Time']`
- **Environmental** (4): `['Sample Rate (Hz)', 'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']`
- **Acoustic Indices** (1): `['Date']`
- **Detections** (1): `['Recorder type']`
- **Other** (2): `['Deployment ID', 'File number']`

**Missing Values:**
- `Deployment ID`: 1 (0.0%)
- `Recorder type`: 1 (0.0%)
- `Sample Rate (Hz)`: 1 (0.0%)
- `File number`: 1 (0.0%)
- `Broadband (1-40000 Hz)`: 1 (0.0%)
- `Low (50-1200 Hz)`: 1 (0.0%)
- `High (7000-40000 Hz)`: 1 (0.0%)

### `01_temperature_14M_2021.parquet`
- **Shape**: 21,906 rows × 3 columns
- **Size**: 0.5 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Date and time']`
- **Environmental** (1): `['Water temp (°C)']`

**Missing Values:**
- `Water temp (°C)`: 1 (0.0%)

### `01_temperature_37M_2021.parquet`
- **Shape**: 21,910 rows × 3 columns
- **Size**: 0.5 MB
- **Date Range**: 2020-12-31 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Date and time']`
- **Environmental** (1): `['Water temp (°C)']`

**Missing Values:**
- `Water temp (°C)`: 1 (0.0%)

### `01_temperature_9M_2021.parquet`
- **Shape**: 20,732 rows × 3 columns
- **Size**: 0.5 MB
- **Date Range**: 2021-01-01 to 2021-12-31

**Column Categories:**
- **Identifiers** (1): `['datetime']`
- **Temporal** (1): `['Date and time']`
- **Environmental** (1): `['Water temp (°C)']`

**Missing Values:**
- `Water temp (°C)`: 3 (0.0%)

## Notebook 02 Files

### `02_acoustic_indices_aligned_2021.parquet`
- **Shape**: 13,140 rows × 64 columns
- **Size**: 7.0 MB
- **Date Range**: 2021-01-01 to 2021-12-31
- **Stations**: ['14M', '37M', '9M']
- **Years**: [2021]

**Column Categories:**
- **Identifiers** (3): `['datetime', 'station', 'year']`
- **Acoustic Indices** (41): `['ZCR', 'VARt', 'SKEWt', 'KURTt', 'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf', 'ENRf', 'BGNf', 'SNRf', 'Hf', 'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'NDSI', 'rBA', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI', 'LFC', 'MFC', 'HFC', 'TFSD', 'H_Renyi', 'H_gamma', 'RAOQ', 'AGI', 'nROI', 'aROI']`
- **Detections** (12): `['ACTtFraction', 'ACTtCount', 'ACTtMean', 'EVNtFraction', 'ACI', 'ACTspFract', 'ACTspCount', 'ACTspMean', 'EVNspFract', 'EVNspMean', 'EVNspCount', 'H_Havrda']`
- **Statistics** (4): `['MEANt', 'EVNtMean', 'EVNtCount', 'MEANf']`
- **Other** (4): `['FrequencyResolution', 'AnthroEnergy', 'H_pairedShannon', 'H_GiniSimpson']`

**Missing Values:**
- `ZCR`: 40 (0.3%)
- `MEANt`: 40 (0.3%)
- `VARt`: 40 (0.3%)
- `SKEWt`: 40 (0.3%)
- `KURTt`: 40 (0.3%)
- `LEQt`: 40 (0.3%)
- `BGNt`: 40 (0.3%)
- `SNRt`: 40 (0.3%)
- `MED`: 40 (0.3%)
- `Ht`: 40 (0.3%)
- `ACTtFraction`: 40 (0.3%)
- `ACTtCount`: 40 (0.3%)
- `ACTtMean`: 40 (0.3%)
- `EVNtFraction`: 40 (0.3%)
- `EVNtMean`: 40 (0.3%)
- `EVNtCount`: 40 (0.3%)
- `MEANf`: 40 (0.3%)
- `VARf`: 40 (0.3%)
- `SKEWf`: 40 (0.3%)
- `KURTf`: 40 (0.3%)
- `NBPEAKS`: 40 (0.3%)
- `LEQf`: 40 (0.3%)
- `ENRf`: 40 (0.3%)
- `BGNf`: 40 (0.3%)
- `SNRf`: 40 (0.3%)
- `Hf`: 40 (0.3%)
- `EAS`: 40 (0.3%)
- `ECU`: 40 (0.3%)
- `ECV`: 40 (0.3%)
- `EPS`: 40 (0.3%)
- `EPS_KURT`: 40 (0.3%)
- `EPS_SKEW`: 40 (0.3%)
- `ACI`: 40 (0.3%)
- `FrequencyResolution`: 40 (0.3%)
- `NDSI`: 40 (0.3%)
- `rBA`: 40 (0.3%)
- `AnthroEnergy`: 40 (0.3%)
- `BioEnergy`: 40 (0.3%)
- `BI`: 40 (0.3%)
- `ROU`: 40 (0.3%)
- `ADI`: 40 (0.3%)
- `AEI`: 40 (0.3%)
- `LFC`: 40 (0.3%)
- `MFC`: 40 (0.3%)
- `HFC`: 40 (0.3%)
- `ACTspFract`: 40 (0.3%)
- `ACTspCount`: 40 (0.3%)
- `ACTspMean`: 40 (0.3%)
- `EVNspFract`: 40 (0.3%)
- `EVNspMean`: 40 (0.3%)
- `EVNspCount`: 40 (0.3%)
- `TFSD`: 40 (0.3%)
- `H_Havrda`: 40 (0.3%)
- `H_Renyi`: 40 (0.3%)
- `H_pairedShannon`: 40 (0.3%)
- `H_gamma`: 40 (0.3%)
- `H_GiniSimpson`: 40 (0.3%)
- `RAOQ`: 40 (0.3%)
- `AGI`: 40 (0.3%)
- `nROI`: 40 (0.3%)
- `aROI`: 40 (0.3%)

### `02_detections_aligned_2021.parquet`
- **Shape**: 13,140 rows × 14 columns
- **Size**: 2.1 MB
- **Date Range**: 2021-01-01 to 2021-12-31
- **Stations**: ['14M', '37M', '9M']
- **Years**: [2021]

**Column Categories:**
- **Identifiers** (3): `['datetime', 'station', 'year']`
- **Detections** (6): `['Black drum', 'Spotted seatrout', 'Bottlenose dolphin echolocation', 'Bottlenose dolphin burst pulses', 'Bottlenose dolphin whistles', 'Vessel']`
- **Other** (5): `['Silver perch', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt', 'Red drum', 'Atlantic croaker']`

**Missing Values:**
- `Silver perch`: 1 (0.0%)
- `Oyster toadfish boat whistle`: 1 (0.0%)
- `Oyster toadfish grunt`: 1 (0.0%)
- `Black drum`: 1 (0.0%)
- `Spotted seatrout`: 1 (0.0%)
- `Red drum`: 1 (0.0%)
- `Atlantic croaker`: 1 (0.0%)
- `Bottlenose dolphin echolocation`: 5 (0.0%)
- `Bottlenose dolphin burst pulses`: 4 (0.0%)
- `Bottlenose dolphin whistles`: 4 (0.0%)
- `Vessel`: 1 (0.0%)

### `02_environmental_aligned_2021.parquet`
- **Shape**: 13,140 rows × 26 columns
- **Size**: 3.2 MB
- **Date Range**: 2021-01-01 to 2021-12-31
- **Stations**: ['14M', '37M', '9M']
- **Years**: [2021]

**Column Categories:**
- **Identifiers** (3): `['datetime', 'station', 'year']`
- **Environmental** (23): `['Water temp (°C)', 'Water depth (m)', 'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'temp_lag_1', 'temp_lag_2', 'temp_lag_3', 'temp_change_2h', 'temp_change_4h', 'temp_mean_6h', 'temp_mean_12h', 'depth_lag_1', 'depth_lag_2', 'depth_change_2h', 'depth_change_4h', 'depth_mean_6h', 'depth_mean_12h', 'spl_broadband_lag_1', 'spl_broadband_lag_2', 'spl_broadband_mean_6h', 'spl_broadband_mean_12h', 'spl_broadband_mean_24h']`

**Missing Values:**
- `Broadband (1-40000 Hz)`: 36 (0.3%)
- `Low (50-1200 Hz)`: 36 (0.3%)
- `High (7000-40000 Hz)`: 36 (0.3%)
- `temp_lag_1`: 3 (0.0%)
- `temp_lag_2`: 6 (0.0%)
- `temp_lag_3`: 9 (0.1%)
- `temp_change_2h`: 3 (0.0%)
- `temp_change_4h`: 6 (0.0%)
- `depth_lag_1`: 3 (0.0%)
- `depth_lag_2`: 6 (0.0%)
- `depth_change_2h`: 3 (0.0%)
- `depth_change_4h`: 6 (0.0%)
- `spl_broadband_lag_1`: 39 (0.3%)
- `spl_broadband_lag_2`: 42 (0.3%)
- `spl_broadband_mean_6h`: 36 (0.3%)
- `spl_broadband_mean_12h`: 36 (0.3%)
- `spl_broadband_mean_24h`: 36 (0.3%)

### `02_temporal_features_2021.parquet`
- **Shape**: 13,140 rows × 14 columns
- **Size**: 2.2 MB
- **Date Range**: 2021-01-01 to 2021-12-31
- **Stations**: ['14M', '37M', '9M']
- **Years**: [2021]

**Column Categories:**
- **Identifiers** (3): `['datetime', 'station', 'year']`
- **Temporal** (10): `['hour', 'day_of_year', 'month', 'weekday', 'season', 'time_period', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos']`
- **Other** (1): `['week_of_year']`

## Notebook 03 Files

### `03_reduced_acoustic_indices.parquet`
- **Shape**: 13,140 rows × 21 columns
- **Size**: 2.7 MB
- **Date Range**: 2021-01-01 to 2021-12-31
- **Stations**: ['14M', '37M', '9M']
- **Years**: [2021]

**Column Categories:**
- **Identifiers** (3): `['datetime', 'station', 'year']`
- **Acoustic Indices** (12): `['EPS_KURT', 'ECU', 'NBPEAKS', 'TFSD', 'nROI', 'SNRt', 'ZCR', 'SKEWt', 'ADI', 'ENRf', 'VARf', 'VARt']`
- **Detections** (3): `['ACTspFract', 'ACTtFraction', 'EVNspMean']`
- **Statistics** (1): `['MEANt']`
- **Other** (2): `['FrequencyResolution', 'H_pairedShannon']`

**Missing Values:**
- `ACTspFract`: 40 (0.3%)
- `EPS_KURT`: 40 (0.3%)
- `ECU`: 40 (0.3%)
- `NBPEAKS`: 40 (0.3%)
- `TFSD`: 40 (0.3%)
- `nROI`: 40 (0.3%)
- `ACTtFraction`: 40 (0.3%)
- `SNRt`: 40 (0.3%)
- `MEANt`: 40 (0.3%)
- `FrequencyResolution`: 40 (0.3%)
- `EVNspMean`: 40 (0.3%)
- `ZCR`: 40 (0.3%)
- `SKEWt`: 40 (0.3%)
- `ADI`: 40 (0.3%)
- `H_pairedShannon`: 40 (0.3%)
- `ENRf`: 40 (0.3%)
- `VARf`: 40 (0.3%)
- `VARt`: 40 (0.3%)

## Notebook 04 Files

### `04_correlation_statistics.parquet`
- **Shape**: 119 rows × 4 columns
- **Size**: 0.0 MB

**Column Categories:**
- **Acoustic Indices** (1): `['index']`
- **Detections** (1): `['species']`
- **Statistics** (2): `['correlation', 'abs_correlation']`

### `04_index_fish_correlations.parquet`
- **Shape**: 18 rows × 7 columns
- **Size**: 0.0 MB

**Column Categories:**
- **Detections** (2): `['Black drum', 'Spotted seatrout']`
- **Other** (5): `['Silver perch', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt', 'Red drum', 'Atlantic croaker']`

**Missing Values:**
- `Silver perch`: 1 (5.6%)
- `Oyster toadfish boat whistle`: 1 (5.6%)
- `Oyster toadfish grunt`: 1 (5.6%)
- `Black drum`: 1 (5.6%)
- `Spotted seatrout`: 1 (5.6%)
- `Red drum`: 1 (5.6%)
- `Atlantic croaker`: 1 (5.6%)

## Other Files

### `acoustic_indices.parquet`
- **Shape**: 60 rows × 4 columns
- **Size**: 0.0 MB

**Column Categories:**
- **Acoustic Indices** (2): `['Prefix', 'Category']`
- **Other** (2): `['Subcategory', 'Description']`

### `deployments.parquet`
- **Shape**: 183 rows × 50 columns
- **Size**: 0.3 MB
- **Date Range**: 2025-01-01 to 2025-01-01
- **Stations**: ['14M', '37M', '9M', 'A', 'B', 'C', 'CC4', 'CR1', 'D', 'E', 'F', 'WB']
- **Years**: [2017, 2018, 2019, 2020, 2021, 2022]

**Column Categories:**
- **Identifiers** (2): `['Station', 'Year']`
- **Temporal** (1): `['Time zone']`
- **Environmental** (8): `['Depth (ft)', 'Depth (m)', 'Hydrophone Depth (m)', 'Temperature (°C)', 'Sample Rate (kHz)', 'HOBO Water Temp logger No.', 'Temperature data path', 'Depth data path']`
- **Acoustic Indices** (10): `['Source', 'Funder', 'Project', 'State', 'Estuary', 'Instrument', 'Duration', 'Interval', 'Analysis', 'Scientist']`
- **Detections** (5): `['Sponsor', 'Recorder No.', 'Location of backup', 'Packager', 'Issues/comments']`
- **Other** (24): `['Object ID', 'Sea Area', 'Public release date', 'Deployment number', 'Deployment ID', 'Start date', 'End date', 'Platform Type', 'GPS Lat', 'GPS Long', 'Salinity (ppt)', 'DO (mg/L)', 'pH ', 'Number of deployed files collected', 'Memory of wav files (GB)', 'Hydrophone Serial No.', 'Hydrophone Sensitivity (dBV µPa-1)', 'Gain (dB)', 'System Sensitivity (dBV µPa-1)', 'Sample bits', 'HOBO Water level logger No.', 'Duty Cycle', 'Location of wav files', 'How wav files are named']`

**Missing Values:**
- `Salinity (ppt)`: 9 (4.9%)
- `Temperature (°C)`: 11 (6.0%)
- `DO (mg/L)`: 73 (39.9%)
- `pH `: 87 (47.5%)
- `Number of deployed files collected`: 4 (2.2%)
- `Recorder No.`: 1 (0.5%)
- `Hydrophone Serial No.`: 10 (5.5%)
- `HOBO Water Temp logger No.`: 16 (8.7%)
- `Temperature data path`: 18 (9.8%)
- `HOBO Water level logger No.`: 18 (9.8%)
- `Depth data path`: 21 (11.5%)
- `Analysis`: 4 (2.2%)
- `Location of wav files`: 1 (0.5%)
- `Location of backup`: 1 (0.5%)
- `Issues/comments`: 153 (83.6%)

### `deployments_dictionary.parquet`
- **Shape**: 38 rows × 2 columns
- **Size**: 0.0 MB

**Column Categories:**
- **Other** (2): `['Column heading', 'Information']`
