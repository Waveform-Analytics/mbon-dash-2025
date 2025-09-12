# Data File Naming Convention

All processed data files are stored in `data/processed/` and follow the naming convention:
`NN_description.parquet` where NN is the notebook number that creates the file.

## Files Created by Each Notebook

### Notebook 01: Data Loading and Initial Exploration
Raw data files (per station/year):

**`01_indices_[STATION]_[YEAR].parquet`** - Raw acoustic indices (65 columns, ~8,700 rows per station)
- Key columns: `'Date'`, `'Filename'`, `'ZCR'`, `'MEANt'`, `'VARt'`, `'H'`, `'ACI'`, etc.
- Contains ~60 acoustic index measurements per hour-long recording

**`01_detections_[STATION]_[YEAR].parquet`** - Raw fish detection data (16 columns, 4,380 rows per station)
- Key columns: `'Date'`, `'Time'`, `'File'`, `'Deployment ID'`, `'Silver perch'`, `'Oyster toadfish boat whistle'`, `'Oyster toadfish grunt'`, `'Black drum'`, `'Spotted seatrout'`, `'Red drum'`, `'Atlantic croaker'`
- Fish calling intensity scores on 0-3 scale

**`01_temperature_[STATION]_[YEAR].parquet`** - Raw temperature data (3 columns, ~21,900 rows per station)
- Key columns: `'Date and time'`, `'Water temp (°C)'`, `'datetime'`
- 20-minute resolution temperature measurements

**`01_depth_[STATION]_[YEAR].parquet`** - Raw depth/pressure data (3 columns, ~20,730 rows per station)  
- Key columns: `'Date and time'`, `'Water depth (m)'`, `'datetime'`
- Hourly depth measurements for tidal analysis

**`01_spl_[STATION]_[YEAR].parquet`** - Raw SPL data (10 columns, 8,736 rows per station)
- Key columns: `'Deployment ID'`, `'Date'`, `'Broadband (1-40000 Hz)'`, `'Low (50-1200 Hz)'`, `'High (7000-40000 Hz)'`
- Sound pressure levels in multiple frequency bands

**Metadata files:**
- `metadata/01_detection_columns.parquet` - Detection column metadata (33 rows, 7 columns)
  - Columns: `'long_name'`, `'short_name'`, `'type'`, `'group'`, `'keep_species'`
- `metadata/deployments.parquet` - Deployment information (183 rows, 50 columns)
- `metadata/deployments_dictionary.parquet` - Deployment data dictionary (38 rows, 2 columns)
- `metadata/acoustic_indices.parquet` - Acoustic index categories (60 rows, 4 columns)

### Notebook 02: Temporal Alignment and Aggregation
Aligned 2-hour resolution data (all files: 13,140 rows = 3 stations × 365 days × 12 two-hour periods):

**`02_acoustic_indices_aligned_2021.parquet`** - All acoustic indices aligned to 2-hour intervals (64 columns)
- Key columns: `'datetime'`, `'station'`, `'year'`, `'ZCR'`, `'MEANt'`, `'VARt'`, `'H'`, `'ACI'`, etc.
- Contains ~60 acoustic indices aggregated to 2-hour means

**`02_detections_aligned_2021.parquet`** - Fish detections at 2-hour intervals (14 columns)
- Key columns: `'datetime'`, `'station'`, `'year'`, `'Silver perch'`, `'Oyster toadfish boat whistle'`, `'Oyster toadfish grunt'`, `'Black drum'`, `'Spotted seatrout'`, `'Red drum'`, `'Atlantic croaker'`
- Fish calling intensities aligned to 2-hour intervals

**`02_environmental_aligned_2021.parquet`** - Environmental data aggregated to 2-hour (26 columns)
- Key columns: `'datetime'`, `'station'`, `'year'`, `'Water temp (°C)'`, `'Water depth (m)'`, `'Broadband (1-40000 Hz)'`, `'Low (50-1200 Hz)'`, `'High (7000-40000 Hz)'`
- Includes lag variables: temperature/depth lag, change, and rolling means
- SPL data in multiple frequency bands with temporal features

**`02_temporal_features_2021.parquet`** - Temporal variables (14 columns)
- Key columns: `'datetime'`, `'station'`, `'year'`, `'hour'`, `'day_of_year'`, `'month'`, `'season'`, `'weekday'`, `'diel_period'`
- Temporal features for seasonality and diel pattern analysis

### Notebook 03: Acoustic Index Reduction
**`03_reduced_acoustic_indices.parquet`** - Selected ~18 indices (21 columns, 13,140 rows)
- Key columns: `'datetime'`, `'station'`, `'year'`, `'ACTspFract'`, `'EPS_KURT'`, `'VARspec'`, `'ADI'`, `'AEI'`, etc.
- Reduced set of non-redundant acoustic indices after correlation analysis

**`03_selected_indices.txt`** - List of selected indices with rationale
**`03_reduction_summary.json`** - Statistical summary of reduction process

### Notebook 04: Fish Detection Pattern Analysis
**`04_index_fish_correlations.parquet`** - Correlation matrix between indices and fish species (18 rows, 7 columns)
- Key columns: Fish species names (`'Silver perch'`, `'Oyster toadfish boat whistle'`, etc.)
- Correlation values between each reduced acoustic index and each fish species

**`04_correlation_statistics.parquet`** - Detailed correlation statistics (119 rows, 4 columns)
- Key columns: `'index'`, `'species'`, `'correlation'`, `'abs_correlation'`
- Flattened correlation data for analysis and modeling

### Notebook 05: Vessel Detection Model (planned)
- `05_vessel_detection_model.pkl` - Trained vessel detection model
- `05_vessel_predictions.parquet` - Vessel presence predictions

### Notebook 06: Acoustic Indices as Predictors (planned)
- `06_fish_prediction_models.pkl` - Trained fish calling models
- `06_model_performance.parquet` - Model performance metrics
- `06_predictions.parquet` - Fish calling predictions

### Notebook 07: Validation (planned)
- `07_validation_results.parquet` - Comprehensive validation metrics
- `07_temporal_transfer.parquet` - Temporal transfer test results

### Notebook 08: Summary (planned)
- `08_final_recommendations.json` - Final recommendations and conclusions
- `08_method_comparison.parquet` - Comparison of different approaches

## Key Files for Analysis Pipeline

The main analysis pipeline uses these core files:
1. `02_acoustic_indices_aligned_2021.parquet` - Full aligned acoustic indices
2. `02_detections_aligned_2021.parquet` - Aligned manual detections
3. `02_environmental_aligned_2021.parquet` - Aligned environmental data
4. `03_reduced_acoustic_indices.parquet` - Reduced index set for modeling
5. `04_index_fish_correlations.parquet` - Index-fish relationships

## Notes
- All timestamps are in UTC
- All files include 'datetime', 'station', and 'year' columns for merging
- Missing data is represented as NaN
- Station codes: '14M', '37M', '9M' (May River stations)

## Using Detection Column Metadata

The actual column names for fish species in detection data are full descriptive names, not short codes:

**Primary Fish Species (use these for analysis):**
- `'Silver perch'`
- `'Oyster toadfish boat whistle'`
- `'Oyster toadfish grunt'`  
- `'Black drum'`
- `'Spotted seatrout'`
- `'Red drum'`
- `'Atlantic croaker'`

To properly identify fish species columns using metadata:

```python
# Load detection column metadata
metadata_file = data_dir / "metadata" / "01_detection_columns.parquet"
df_det_metadata = pd.read_parquet(metadata_file)

# Get primary fish species columns (group='fish' and keep_species=1)
# Use 'long_name' for actual column names in processed data
fish_cols = df_det_metadata[
    (df_det_metadata['group'] == 'fish') & 
    (df_det_metadata['keep_species'] == 1)
]['long_name'].tolist()

# Get all fish columns (including interruptions)
all_fish_cols = df_det_metadata[
    df_det_metadata['group'] == 'fish'
]['long_name'].tolist()

# Get dolphin columns
dolphin_cols = df_det_metadata[
    df_det_metadata['group'] == 'dolphin'
]['long_name'].tolist()
```

**Note**: Use `'long_name'` not `'short_name'` for actual column names in processed data files.