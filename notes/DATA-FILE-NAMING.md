# Data File Naming Convention

All processed data files are stored in `data/processed/` and follow the naming convention:
`NN_description.parquet` where NN is the notebook number that creates the file.

## Files Created by Each Notebook

### Notebook 01: Data Loading and Initial Exploration
Raw data files (per station/year):
- `01_indices_[STATION]_[YEAR].parquet` - Raw acoustic indices
- `01_detections_[STATION]_[YEAR].parquet` - Raw fish detection data  
- `01_temperature_[STATION]_[YEAR].parquet` - Raw temperature data
- `01_depth_[STATION]_[YEAR].parquet` - Raw depth/pressure data
- `01_spl_[STATION]_[YEAR].parquet` - Raw SPL data

Metadata files:
- `metadata/01_detection_columns.parquet` - Detection column metadata (group, keep_species, etc.)
- `metadata/deployments.parquet` - Deployment information
- `metadata/deployments_dictionary.parquet` - Deployment data dictionary  
- `metadata/acoustic_indices.parquet` - Acoustic index categories and descriptions

### Notebook 02: Temporal Alignment and Aggregation
Aligned 2-hour resolution data:
- `02_acoustic_indices_aligned_2021.parquet` - All acoustic indices aligned to 2-hour intervals
- `02_detections_aligned_2021.parquet` - Fish detections at 2-hour intervals
- `02_environmental_aligned_2021.parquet` - Temperature and depth data aggregated to 2-hour
- `02_temporal_features_2021.parquet` - Temporal variables (hour, day, season, etc.)

### Notebook 03: Acoustic Index Reduction
- `03_reduced_acoustic_indices.parquet` - Selected ~18 indices with datetime/station/year
- `03_selected_indices.txt` - List of selected indices with rationale
- `03_reduction_summary.json` - Statistical summary of reduction process

### Notebook 04: Fish Detection Pattern Analysis
- `04_index_fish_correlations.parquet` - Correlation matrix between indices and fish species
- `04_correlation_statistics.parquet` - Detailed correlation statistics

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

To properly identify fish species columns in detection data:

```python
# Load detection column metadata
metadata_file = data_dir / "metadata" / "01_detection_columns.parquet"
df_det_metadata = pd.read_parquet(metadata_file)

# Get primary fish species columns (group='fish' and keep_species=1)
fish_cols = df_det_metadata[
    (df_det_metadata['group'] == 'fish') & 
    (df_det_metadata['keep_species'] == 1)
]['short_name'].tolist()

# Get all fish columns (including interruptions)
all_fish_cols = df_det_metadata[
    df_det_metadata['group'] == 'fish'
]['short_name'].tolist()

# Get dolphin columns
dolphin_cols = df_det_metadata[
    df_det_metadata['group'] == 'dolphin'
]['short_name'].tolist()
```

This approach is more robust than hardcoding column names or using exclusion lists.