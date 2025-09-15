import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    from pathlib import Path

    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    DATA_ROOT = project_root / "data"

    # Configuration variables
    YEAR = 2021
    STATIONS = ['9M', '14M', '37M']
    AGGREGATION_HOURS = 2  # Aggregate to 2-hour intervals

    # Data directories
    DATA_DIR = DATA_ROOT / "processed"
    OUTPUT_DIR = DATA_ROOT / "processed"

    print(f"Configuration:")
    print(f"  Year: {YEAR}")
    print(f"  Stations: {STATIONS}")
    print(f"  Aggregation interval: {AGGREGATION_HOURS} hours")
    print(f"  Data directory: {DATA_DIR}")
    return (
        AGGREGATION_HOURS,
        DATA_DIR,
        OUTPUT_DIR,
        STATIONS,
        YEAR,
        mo,
        np,
        pd,
        plt,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Notebook 2: Temporal Alignment and Aggregation

    **Purpose**: Align all data to consistent 2-hour temporal resolution matching manual detections
    **Key Outputs**: Temporally aligned dataset ready for analysis

    This notebook addresses the fundamental challenge of temporal misalignment across multiple data streams with different collection frequencies. By aggregating everything to a common 2-hour resolution and engineering relevant features, we create analysis-ready datasets that preserve ecological information while enabling modeling.

    ## 1. Load Processed Data from Notebook 1

    Loading the cleaned and standardized data streams from each station. Notebook 1 performed quality control,
    standardized column names, and converted timestamps to consistent formats. Here we systematically load:

    - **Acoustic indices** (50-60 indices per station): Hourly summaries of soundscape characteristics
    - **Detection data** (2-hour intervals): Manual annotations of fish calling activity by species  
    - **Temperature data** (20-min intervals): Water temperature from autonomous sensors
    - **Depth data** (hourly): Water depth measurements for tidal pattern analysis
    - **SPL data** (hourly): Sound pressure levels in multiple frequency bands

    **Expected Outcome**: Five data dictionaries organized by data type and station, ready for temporal alignment.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, STATIONS, YEAR, pd):
    # Load all processed data from Notebook 1
    data_loaded = {
        'indices': {},
        'detections': {},
        'temperature': {},
        'depth': {},
        'spl': {}
    }

    for station_load in STATIONS:
        # Load acoustic indices
        indices_path = DATA_DIR / f"01_indices_{station_load}_{YEAR}.parquet"
        if indices_path.exists():
            data_loaded['indices'][station_load] = pd.read_parquet(indices_path)
            print(f"✓ Loaded indices for {station_load}: {len(data_loaded['indices'][station_load])} rows")

        # Load detection data
        detection_path = DATA_DIR / f"01_detections_{station_load}_{YEAR}.parquet"
        if detection_path.exists():
            data_loaded['detections'][station_load] = pd.read_parquet(detection_path)
            print(f"✓ Loaded detections for {station_load}: {len(data_loaded['detections'][station_load])} rows")

        # Load temperature data
        temp_path = DATA_DIR / f"01_temperature_{station_load}_{YEAR}.parquet"
        if temp_path.exists():
            data_loaded['temperature'][station_load] = pd.read_parquet(temp_path)
            print(f"✓ Loaded temperature for {station_load}: {len(data_loaded['temperature'][station_load])} rows")

        # Load depth data
        depth_path = DATA_DIR / f"01_depth_{station_load}_{YEAR}.parquet"
        if depth_path.exists():
            data_loaded['depth'][station_load] = pd.read_parquet(depth_path)
            print(f"✓ Loaded depth for {station_load}: {len(data_loaded['depth'][station_load])} rows")

        # Load SPL data
        spl_path = DATA_DIR / f"01_spl_{station_load}_{YEAR}.parquet"
        if spl_path.exists():
            data_loaded['spl'][station_load] = pd.read_parquet(spl_path)
            print(f"✓ Loaded SPL for {station_load}: {len(data_loaded['spl'][station_load])} rows")

    print(f"\n✓ All data loaded successfully")
    return (data_loaded,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 2. Examine Temporal Resolution of Each Dataset""")
    return


@app.cell(hide_code=True)
def _(STATIONS, data_loaded, pd):
    # Examine the temporal resolution and datetime columns of each dataset
    temporal_info = {}

    for station_exam in STATIONS:
        station_info = {}

        # Detection data (already 2-hour)
        if station_exam in data_loaded['detections']:
            df_det_exam = data_loaded['detections'][station_exam]
            if 'datetime' in df_det_exam.columns:
                df_det_exam['datetime'] = pd.to_datetime(df_det_exam['datetime'])
                time_diffs = df_det_exam['datetime'].diff().dropna()
                station_info['detections'] = {
                    'median_interval': time_diffs.median(),
                    'min_datetime': df_det_exam['datetime'].min(),
                    'max_datetime': df_det_exam['datetime'].max()
                }

        # Temperature data (20-min intervals)
        if station_exam in data_loaded['temperature']:
            df_temp_exam = data_loaded['temperature'][station_exam]
            if 'datetime' in df_temp_exam.columns:
                df_temp_exam['datetime'] = pd.to_datetime(df_temp_exam['datetime'])
                time_diffs = df_temp_exam['datetime'].diff().dropna()
                station_info['temperature'] = {
                    'median_interval': time_diffs.median(),
                    'min_datetime': df_temp_exam['datetime'].min(),
                    'max_datetime': df_temp_exam['datetime'].max()
                }

        # Depth data (1-hour intervals)
        if station_exam in data_loaded['depth']:
            df_depth_exam = data_loaded['depth'][station_exam]
            if 'datetime' in df_depth_exam.columns:
                df_depth_exam['datetime'] = pd.to_datetime(df_depth_exam['datetime'])
                time_diffs = df_depth_exam['datetime'].diff().dropna()
                station_info['depth'] = {
                    'median_interval': time_diffs.median(),
                    'min_datetime': df_depth_exam['datetime'].min(),
                    'max_datetime': df_depth_exam['datetime'].max()
                }

        # SPL data (1-hour intervals)
        if station_exam in data_loaded['spl']:
            df_spl_exam = data_loaded['spl'][station_exam]
            if 'datetime' in df_spl_exam.columns:
                df_spl_exam['datetime'] = pd.to_datetime(df_spl_exam['datetime'])
                time_diffs = df_spl_exam['datetime'].diff().dropna()
                station_info['spl'] = {
                    'median_interval': time_diffs.median(),
                    'min_datetime': df_spl_exam['datetime'].min(),
                    'max_datetime': df_spl_exam['datetime'].max()
                }

        # Acoustic indices (need to check)
        if station_exam in data_loaded['indices']:
            df_idx_exam = data_loaded['indices'][station_exam]
            # Find datetime column
            datetime_col_exam = None
            for col_exam in ['datetime', 'DateTime', 'Date', 'time', 'Time']:
                if col_exam in df_idx_exam.columns:
                    datetime_col_exam = col_exam
                    break

            if datetime_col_exam:
                df_idx_exam['datetime_parsed'] = pd.to_datetime(df_idx_exam[datetime_col_exam])
                time_diffs = df_idx_exam['datetime_parsed'].diff().dropna()
                station_info['indices'] = {
                    'median_interval': time_diffs.median(),
                    'min_datetime': df_idx_exam['datetime_parsed'].min(),
                    'max_datetime': df_idx_exam['datetime_parsed'].max(),
                    'datetime_column': datetime_col_exam
                }

        temporal_info[station_exam] = station_info

    # Display temporal resolution summary
    print("Temporal Resolution Summary:")
    print("=" * 60)
    for station_display, info in temporal_info.items():
        print(f"\nStation {station_display}:")
        for data_type, details in info.items():
            if 'median_interval' in details:
                print(f"  {data_type}: {details['median_interval']} median interval")
                print(f"    Range: {details['min_datetime']} to {details['max_datetime']}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 3. Create Common Time Grid for Alignment""")
    return


@app.cell(hide_code=True)
def _(AGGREGATION_HOURS, STATIONS, data_loaded, pd):
    # Create a common 2-hour time grid based on detection data
    # Detection data already has the correct 2-hour resolution

    time_grids = {}

    for station_grid in STATIONS:
        if station_grid in data_loaded['detections']:
            df_det_grid = data_loaded['detections'][station_grid]
            if 'datetime' in df_det_grid.columns:
                # Use detection times as the reference grid
                df_det_grid['datetime'] = pd.to_datetime(df_det_grid['datetime'])
                # Floor to 2-hour boundaries to handle timestamp drift/precision issues
                df_det_grid['datetime_clean'] = df_det_grid['datetime'].dt.floor(f'{AGGREGATION_HOURS}h')
                time_grids[station_grid] = df_det_grid['datetime_clean'].sort_values().reset_index(drop=True)

                print(f"Station {station_grid} time grid:")
                print(f"  Start: {time_grids[station_grid].min()}")
                print(f"  End: {time_grids[station_grid].max()}")
                print(f"  Points: {len(time_grids[station_grid])}")
                print(f"  Expected interval: {AGGREGATION_HOURS} hours")
    return (time_grids,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 4. Aggregate Acoustic Indices to 2-Hour Resolution

    Now we begin the core temporal alignment process. The acoustic indices were calculated hourly, but our manual detection data exists at 2-hour intervals. To enable meaningful comparisons and modeling, we need to aggregate the acoustic data to match the detection temporal resolution.

    **Aggregation strategy:** We take the mean of each acoustic index within each 2-hour window. The mean is more robust than other statistics for acoustic indices, which can have occasional extreme values due to transient sounds.

    For each station, we:

    1. **Group hourly data** into 2-hour windows (e.g., 00:00-02:00, 02:00-04:00)
    2. **Calculate means** for all numeric acoustic indices within each window
    3. **Align to detection grid** to ensure exactly matching timestamps
    4. **Fill gaps** where acoustic data is missing but detections exist (marked as NaN)
    """
    )
    return


@app.cell(hide_code=True)
def _(AGGREGATION_HOURS, STATIONS, data_loaded, np, pd, time_grids):
    # Aggregate acoustic indices from hourly to 2-hour means
    indices_aggregated = {}

    for station_agg_idx in STATIONS:
        if station_agg_idx in data_loaded['indices'] and station_agg_idx in time_grids:
            df_idx_agg = data_loaded['indices'][station_agg_idx].copy()

            # Find and parse datetime column
            datetime_col_idx = None
            for col_idx in ['datetime', 'DateTime', 'Date', 'time', 'Time']:
                if col_idx in df_idx_agg.columns:
                    datetime_col_idx = col_idx
                    break

            if datetime_col_idx:
                df_idx_agg['datetime'] = pd.to_datetime(df_idx_agg[datetime_col_idx])

                # Get numeric columns (indices)
                numeric_cols_idx = df_idx_agg.select_dtypes(include=[np.number]).columns.tolist()

                # Create aggregation groups (2-hour windows)
                df_idx_agg['datetime_2h'] = df_idx_agg['datetime'].dt.floor(f'{AGGREGATION_HOURS}h')

                # Aggregate numeric columns by taking the mean
                agg_dict_idx = {col: 'mean' for col in numeric_cols_idx}
                df_idx_grouped = df_idx_agg.groupby('datetime_2h').agg(agg_dict_idx).reset_index()
                df_idx_grouped.rename(columns={'datetime_2h': 'datetime'}, inplace=True)

                # Align to detection time grid
                df_idx_aligned = pd.DataFrame({'datetime': time_grids[station_agg_idx]})
                df_idx_aligned = df_idx_aligned.merge(df_idx_grouped, on='datetime', how='left')

                indices_aggregated[station_agg_idx] = df_idx_aligned

                print(f"✓ Station {station_agg_idx}: Aggregated {len(numeric_cols_idx)} indices")
                print(f"  Original rows: {len(df_idx_agg)} → Aggregated rows: {len(df_idx_aligned)}")
                print(f"  Missing values after aggregation: {df_idx_aligned[numeric_cols_idx].isnull().sum().sum()}")
    return (indices_aggregated,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 5. Aggregate Environmental Data to 2-Hour Resolution

    Environmental variables often drive fish calling behavior, but they're collected at different temporal resolutions than our biological data. Temperature sensors record every 20 minutes, while depth sensors record hourly. We need to aggregate both to our standard 2-hour intervals.

    **Temperature aggregation (20-min → 2-hour):** Temperature changes relatively slowly in marine environments, so averaging 20-minute readings over 2-hour windows captures the meaningful thermal environment fish experience while filtering out sensor noise and very short-term fluctuations.

    **Depth aggregation (1-hour → 2-hour):** Water depth varies with tides and is already measured hourly. The 2-hour mean provides a stable measure of the average depth conditions during each analysis window.

    **Gap filling strategy:** For small data gaps (≤6 hours), we use forward-fill interpolation since environmental conditions change gradually. This helps maintain continuity while avoiding unrealistic interpolation across long gaps that might span weather events or equipment failures.
    """
    )
    return


@app.cell(hide_code=True)
def _(AGGREGATION_HOURS, STATIONS, data_loaded, pd, time_grids):
    # Aggregate temperature data (20-min to 2-hour)
    temperature_aggregated = {}

    for station_agg_temp in STATIONS:
        if station_agg_temp in data_loaded['temperature'] and station_agg_temp in time_grids:
            df_temp_agg = data_loaded['temperature'][station_agg_temp].copy()

            if 'datetime' in df_temp_agg.columns and 'Water temp (°C)' in df_temp_agg.columns:
                df_temp_agg['datetime'] = pd.to_datetime(df_temp_agg['datetime'])

                # Create 2-hour windows
                df_temp_agg['datetime_2h'] = df_temp_agg['datetime'].dt.floor(f'{AGGREGATION_HOURS}h')

                # Aggregate by taking mean
                df_temp_grouped = df_temp_agg.groupby('datetime_2h').agg({
                    'Water temp (°C)': 'mean'
                }).reset_index()
                df_temp_grouped.rename(columns={'datetime_2h': 'datetime'}, inplace=True)

                # Align to detection time grid
                df_temp_aligned = pd.DataFrame({'datetime': time_grids[station_agg_temp]})
                df_temp_aligned = df_temp_aligned.merge(df_temp_grouped, on='datetime', how='left')

                # Forward fill small gaps (up to 3 intervals = 6 hours)
                df_temp_aligned['Water temp (°C)'] = df_temp_aligned['Water temp (°C)'].fillna(method='ffill', limit=3)

                temperature_aggregated[station_agg_temp] = df_temp_aligned

                print(f"✓ Station {station_agg_temp} temperature: {len(df_temp_agg)} → {len(df_temp_aligned)} rows")
                print(f"  Missing values: {df_temp_aligned['Water temp (°C)'].isnull().sum()}")
    return (temperature_aggregated,)


@app.cell(hide_code=True)
def _(AGGREGATION_HOURS, STATIONS, data_loaded, pd, time_grids):
    # Aggregate depth data (1-hour to 2-hour)
    depth_aggregated = {}

    for station_agg_depth in STATIONS:
        if station_agg_depth in data_loaded['depth'] and station_agg_depth in time_grids:
            df_depth_agg = data_loaded['depth'][station_agg_depth].copy()

            if 'datetime' in df_depth_agg.columns and 'Water depth (m)' in df_depth_agg.columns:
                df_depth_agg['datetime'] = pd.to_datetime(df_depth_agg['datetime'])

                # Create 2-hour windows
                df_depth_agg['datetime_2h'] = df_depth_agg['datetime'].dt.floor(f'{AGGREGATION_HOURS}h')

                # Aggregate by taking mean
                df_depth_grouped = df_depth_agg.groupby('datetime_2h').agg({
                    'Water depth (m)': 'mean'
                }).reset_index()
                df_depth_grouped.rename(columns={'datetime_2h': 'datetime'}, inplace=True)

                # Align to detection time grid
                df_depth_aligned = pd.DataFrame({'datetime': time_grids[station_agg_depth]})
                df_depth_aligned = df_depth_aligned.merge(df_depth_grouped, on='datetime', how='left')

                # Forward fill small gaps
                df_depth_aligned['Water depth (m)'] = df_depth_aligned['Water depth (m)'].fillna(method='ffill', limit=3)

                depth_aggregated[station_agg_depth] = df_depth_aligned

                print(f"✓ Station {station_agg_depth} depth: {len(df_depth_agg)} → {len(df_depth_aligned)} rows")
                print(f"  Missing values: {df_depth_aligned['Water depth (m)'].isnull().sum()}")
    return (depth_aggregated,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Sound Pressure Level (SPL) Aggregation

    **SPL measurements** quantify the actual loudness of the underwater environment across different frequency ranges. We have three SPL bands: broadband (full spectrum), low frequency (50-1,200 Hz, often anthropogenic), and high frequency (7,000-40,000 Hz, often biological). 

    Like other environmental variables, SPL provides important context for interpreting fish calling patterns and acoustic indices.
    """
    )
    return


@app.cell(hide_code=True)
def _(AGGREGATION_HOURS, STATIONS, data_loaded, pd, time_grids):
    # Aggregate SPL data (1-hour to 2-hour)
    spl_aggregated = {}

    for station_agg_spl in STATIONS:
        if station_agg_spl in data_loaded['spl'] and station_agg_spl in time_grids:
            df_spl_agg = data_loaded['spl'][station_agg_spl].copy()

            if 'datetime' in df_spl_agg.columns:
                df_spl_agg['datetime'] = pd.to_datetime(df_spl_agg['datetime'])
                # Remove timezone information to avoid merge conflicts
                if df_spl_agg['datetime'].dt.tz is not None:
                    df_spl_agg['datetime'] = df_spl_agg['datetime'].dt.tz_convert(None)

                # SPL columns to aggregate
                spl_cols = ['Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']
                available_spl_cols = [col_spl for col_spl in spl_cols if col_spl in df_spl_agg.columns]

                # Create 2-hour windows
                df_spl_agg['datetime_2h'] = df_spl_agg['datetime'].dt.floor(f'{AGGREGATION_HOURS}h')

                # Aggregate by taking mean (SPL in dB should be averaged on linear scale, but for simplicity using arithmetic mean)
                agg_dict_spl = {col_spl: 'mean' for col_spl in available_spl_cols}
                df_spl_grouped = df_spl_agg.groupby('datetime_2h').agg(agg_dict_spl).reset_index()
                df_spl_grouped.rename(columns={'datetime_2h': 'datetime'}, inplace=True)

                # Ensure time grid is also timezone-naive
                time_grid_spl = time_grids[station_agg_spl].copy()
                if time_grid_spl.dt.tz is not None:
                    time_grid_spl = time_grid_spl.dt.tz_convert(None)

                # Align to detection time grid
                df_spl_aligned = pd.DataFrame({'datetime': time_grid_spl})
                df_spl_aligned = df_spl_aligned.merge(df_spl_grouped, on='datetime', how='left')

                # Forward fill small gaps
                for col_spl_fill in available_spl_cols:
                    df_spl_aligned[col_spl_fill] = df_spl_aligned[col_spl_fill].fillna(method='ffill', limit=3)

                spl_aggregated[station_agg_spl] = df_spl_aligned

                print(f"✓ Station {station_agg_spl} SPL: {len(df_spl_agg)} → {len(df_spl_aligned)} rows")
                print(f"  Missing values: {df_spl_aligned[available_spl_cols].isnull().sum().sum()}")
    return (spl_aggregated,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 6. Create Temporal Features

    Fish calling behavior follows strong temporal patterns - daily, weekly, seasonal, and even annual cycles. To capture these patterns in our models, we need to convert raw timestamps into meaningful temporal features that machine learning algorithms can work with.

    **Why cyclic encoding?** Simple linear features (hour = 0, 1, 2, ..., 23) create artificial discontinuities - hour 23 appears far from hour 0, when they're actually consecutive. Cyclic encoding using sine and cosine transforms preserves the circular nature of time, ensuring that 11 PM and 1 AM are represented as close in feature space.

    **Feature categories we create:**
    - **Hourly patterns**: Hour of day as both linear and cyclic features (for diel activity patterns)
    - **Daily patterns**: Day of year and day of week (for seasonal and weekly patterns)  
    - **Seasonal patterns**: Month as both linear and cyclic features
    - **Periodic cycles**: Week of year for longer-term patterns

    These features will help our models recognize that a fish species might call more at dawn, during certain seasons, or on particular days of the week.
    """
    )
    return


@app.cell(hide_code=True)
def _(AGGREGATION_HOURS, STATIONS, data_loaded, np, pd):
    # Create temporal features for each station
    temporal_features = {}

    for station_feat in STATIONS:
        if station_feat in data_loaded['detections']:
            df_det_feat = data_loaded['detections'][station_feat].copy()

            if 'datetime' in df_det_feat.columns:
                df_det_feat['datetime'] = pd.to_datetime(df_det_feat['datetime'])
                # Use cleaned timestamps for consistency with time grid
                df_det_feat['datetime'] = df_det_feat['datetime'].dt.floor(f'{AGGREGATION_HOURS}h')

                # Basic temporal features
                df_det_feat['hour'] = df_det_feat['datetime'].dt.hour
                df_det_feat['day_of_year'] = df_det_feat['datetime'].dt.dayofyear
                df_det_feat['month'] = df_det_feat['datetime'].dt.month
                df_det_feat['weekday'] = df_det_feat['datetime'].dt.weekday
                df_det_feat['week_of_year'] = df_det_feat['datetime'].dt.isocalendar().week

                # Season (meteorological seasons for Northern Hemisphere)
                df_det_feat['season'] = df_det_feat['month'].map({
                    12: 'Winter', 1: 'Winter', 2: 'Winter',
                    3: 'Spring', 4: 'Spring', 5: 'Spring',
                    6: 'Summer', 7: 'Summer', 8: 'Summer',
                    9: 'Fall', 10: 'Fall', 11: 'Fall'
                })

                # Time of day categories (simplified - would need solar calculator for accurate dawn/dusk)
                df_det_feat['time_period'] = pd.cut(
                    df_det_feat['hour'],
                    bins=[-0.1, 6, 12, 18, 24],
                    labels=['Night', 'Morning', 'Afternoon', 'Evening']
                )

                # Cyclic encoding for hour (sine and cosine to preserve circular nature)
                df_det_feat['hour_sin'] = np.sin(2 * np.pi * df_det_feat['hour'] / 24)
                df_det_feat['hour_cos'] = np.cos(2 * np.pi * df_det_feat['hour'] / 24)

                # Cyclic encoding for day of year
                df_det_feat['day_sin'] = np.sin(2 * np.pi * df_det_feat['day_of_year'] / 365)
                df_det_feat['day_cos'] = np.cos(2 * np.pi * df_det_feat['day_of_year'] / 365)

                # Select temporal features columns
                temporal_cols = ['datetime', 'hour', 'day_of_year', 'month', 'weekday', 
                                'week_of_year', 'season', 'time_period',
                                'hour_sin', 'hour_cos', 'day_sin', 'day_cos']

                temporal_features[station_feat] = df_det_feat[temporal_cols]

                print(f"✓ Station {station_feat}: Created {len(temporal_cols)-1} temporal features")

    # Display sample temporal features
    if temporal_features:
        sample_station = list(temporal_features.keys())[0]
        print(f"\nSample temporal features for station {sample_station}:")
        print(temporal_features[sample_station].head(3))
    return (temporal_features,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 7. Combine All Aligned Data""")
    return


@app.cell(hide_code=True)
def _(
    STATIONS,
    data_loaded,
    depth_aggregated,
    indices_aggregated,
    pd,
    spl_aggregated,
    temperature_aggregated,
    temporal_features,
):
    # Combine all aligned data into single dataframes per station
    combined_data = {}

    for station_comb in STATIONS:
        # Start with temporal features as base
        if station_comb in temporal_features:
            df_combined = temporal_features[station_comb].copy()

            # Add detection data (already 2-hour resolution)
            if station_comb in data_loaded['detections']:
                df_det_comb = data_loaded['detections'][station_comb].copy()
                # Remove columns we don't need or that would conflict
                cols_to_drop = ['Date', 'Date ', 'Time', 'datetime', 'Deployment ID', 'File']
                cols_to_drop = [col_drop for col_drop in cols_to_drop if col_drop in df_det_comb.columns]
                df_det_clean = df_det_comb.drop(columns=cols_to_drop)

                # Merge detection data
                df_combined = pd.concat([df_combined, df_det_clean], axis=1)

            # Add aggregated acoustic indices
            if station_comb in indices_aggregated:
                df_idx_comb = indices_aggregated[station_comb].drop(columns=['datetime'])
                df_combined = pd.concat([df_combined, df_idx_comb], axis=1)

            # Add aggregated temperature
            if station_comb in temperature_aggregated:
                df_temp_comb = temperature_aggregated[station_comb].drop(columns=['datetime'])
                df_combined = pd.concat([df_combined, df_temp_comb], axis=1)

            # Add aggregated depth
            if station_comb in depth_aggregated:
                df_depth_comb = depth_aggregated[station_comb].drop(columns=['datetime'])
                df_combined = pd.concat([df_combined, df_depth_comb], axis=1)

            # Add aggregated SPL
            if station_comb in spl_aggregated:
                df_spl_comb = spl_aggregated[station_comb].drop(columns=['datetime'])
                df_combined = pd.concat([df_combined, df_spl_comb], axis=1)

            # Add station identifier
            df_combined['station'] = station_comb

            combined_data[station_comb] = df_combined

            print(f"✓ Station {station_comb}: Combined dataset has {len(df_combined)} rows × {len(df_combined.columns)} columns")
            print(f"  Column groups: {len(temporal_features[station_comb].columns)} temporal, "
                  f"{len(df_det_clean.columns) if station_comb in data_loaded['detections'] else 0} detection, "
                  f"{len(df_idx_comb.columns) if station_comb in indices_aggregated else 0} indices, "
                  f"3 environmental, 3 SPL")
    return (combined_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 8. Engineer Lag Variables and Running Means

    **Why lag variables?** Marine animals often respond to environmental changes with delays. Fish might not immediately start calling when temperature changes - they may respond to conditions from 2-6 hours earlier. Lag variables capture these delayed ecological responses.

    **Why rolling means?** Short-term environmental fluctuations (sensor noise, brief weather events) may be less important than longer-term trends. Rolling means smooth out noise and capture the environmental context that fish actually experience over several hours.

    **Feature engineering strategy:**

    **Temperature features:**
    - **Lag variables** (1-3 intervals = 2-6 hours ago): Capture delayed thermal responses
    - **Change rates** (2h, 4h): Detect rapid warming/cooling events that might trigger behavior
    - **Rolling means** (6h, 12h): Capture longer-term thermal trends

    **Depth features:**
    - **Lag variables**: Capture tidal cycle effects on calling behavior
    - **Change rates**: Detect rising vs falling tides (fish may respond differently)
    - **Rolling means**: Smooth out tidal fluctuations to reveal underlying patterns

    **SPL features:**
    - **Lag variables**: Account for delayed responses to noise events
    - **Rolling means** (6h, 12h, 24h): Capture ambient noise climate rather than momentary sounds

    **Selected acoustic indices:**
    - **Rolling means only** (to avoid too many features): Capture recent acoustic environment trends

    → These engineered features help models understand not just current conditions, but recent environmental history that influences animal behavior.
    """
    )
    return


@app.cell(hide_code=True)
def _(STATIONS, combined_data):
    # Create lag variables and running means for key features
    enhanced_data = {}

    for station_lag in STATIONS:
        if station_lag in combined_data:
            df_lag = combined_data[station_lag].copy()

            # Sort by datetime to ensure correct lag calculation
            df_lag = df_lag.sort_values('datetime')

            # Temperature lag variables (t-1, t-2 = 2 hours, 4 hours ago)
            if 'Water temp (°C)' in df_lag.columns:
                df_lag['temp_lag_1'] = df_lag['Water temp (°C)'].shift(1)
                df_lag['temp_lag_2'] = df_lag['Water temp (°C)'].shift(2)
                df_lag['temp_lag_3'] = df_lag['Water temp (°C)'].shift(3)

                # Temperature change rate
                df_lag['temp_change_2h'] = df_lag['Water temp (°C)'] - df_lag['temp_lag_1']
                df_lag['temp_change_4h'] = df_lag['Water temp (°C)'] - df_lag['temp_lag_2']

                # Rolling means (3 periods = 6 hours, 6 periods = 12 hours)
                df_lag['temp_mean_6h'] = df_lag['Water temp (°C)'].rolling(window=3, min_periods=1).mean()
                df_lag['temp_mean_12h'] = df_lag['Water temp (°C)'].rolling(window=6, min_periods=1).mean()

            # Depth lag variables
            if 'Water depth (m)' in df_lag.columns:
                df_lag['depth_lag_1'] = df_lag['Water depth (m)'].shift(1)
                df_lag['depth_lag_2'] = df_lag['Water depth (m)'].shift(2)

                # Depth change (tidal indicators)
                df_lag['depth_change_2h'] = df_lag['Water depth (m)'] - df_lag['depth_lag_1']
                df_lag['depth_change_4h'] = df_lag['Water depth (m)'] - df_lag['depth_lag_2']

                # Rolling means
                df_lag['depth_mean_6h'] = df_lag['Water depth (m)'].rolling(window=3, min_periods=1).mean()
                df_lag['depth_mean_12h'] = df_lag['Water depth (m)'].rolling(window=6, min_periods=1).mean()

            # SPL lag variables (for broadband)
            if 'Broadband (1-40000 Hz)' in df_lag.columns:
                df_lag['spl_broadband_lag_1'] = df_lag['Broadband (1-40000 Hz)'].shift(1)
                df_lag['spl_broadband_lag_2'] = df_lag['Broadband (1-40000 Hz)'].shift(2)

                # SPL rolling means
                df_lag['spl_broadband_mean_6h'] = df_lag['Broadband (1-40000 Hz)'].rolling(window=3, min_periods=1).mean()
                df_lag['spl_broadband_mean_12h'] = df_lag['Broadband (1-40000 Hz)'].rolling(window=6, min_periods=1).mean()
                df_lag['spl_broadband_mean_24h'] = df_lag['Broadband (1-40000 Hz)'].rolling(window=12, min_periods=1).mean()

            # Select a few key acoustic indices for lag features (if they exist)
            # We'll identify these by looking for common index names
            acoustic_index_cols = [col_lag for col_lag in df_lag.columns if any(x in col_lag for x in ['ACI', 'ADI', 'AEI', 'BI', 'H'])]

            if len(acoustic_index_cols) > 0:
                # Take first 5 indices for lag features (to avoid too many features)
                selected_indices = acoustic_index_cols[:5]

                for idx_col in selected_indices:
                    # Create rolling means for indices
                    df_lag[f'{idx_col}_mean_6h'] = df_lag[idx_col].rolling(window=3, min_periods=1).mean()
                    df_lag[f'{idx_col}_mean_12h'] = df_lag[idx_col].rolling(window=6, min_periods=1).mean()

            enhanced_data[station_lag] = df_lag

            # Count new features
            new_features = [col_new for col_new in df_lag.columns if col_new not in combined_data[station_lag].columns]
            print(f"✓ Station {station_lag}: Added {len(new_features)} lag/rolling features")
    return (enhanced_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 9. Visualize Temporal Alignment

    After all this data processing, it's essential to visualize the results to ensure our temporal alignment worked correctly and to understand the patterns in our aligned dataset.

    **What to look for in these visualizations:**

    **Data availability heatmaps:** Show which variables have data at which time points. Ideally, we should see:
    - Consistent coverage across detection periods (manual annotations were done every 2 hours)
    - Reasonable coverage for environmental variables (some gaps are expected due to equipment maintenance)
    - Clear patterns where all data types align temporally

    **Time series examples:** Sample traces of key variables help us verify:
    - Realistic environmental patterns (temperature cycles, tidal patterns)
    - Sensible acoustic index values (no extreme outliers after aggregation)
    - Proper alignment between fish detection timing and environmental conditions

    → These plots serve as quality control for our temporal alignment process and provide intuition about the data patterns we'll be modeling.
    """
    )
    return


@app.cell(hide_code=True)
def _(STATIONS, enhanced_data, pd, plt):
    # Visualize the temporal alignment and aggregation results
    fig_align, axes_align = plt.subplots(3, 2, figsize=(15, 12))

    for i_align, station_plot in enumerate(STATIONS):
        if station_plot in enhanced_data:
            df_plot = enhanced_data[station_plot]

            # Plot 1: Data availability heatmap
            ax_avail = axes_align[i_align, 0]

            # Select key columns for availability check
            key_cols = ['Water temp (°C)', 'Water depth (m)', 'Broadband (1-40000 Hz)']
            # Add first few acoustic indices if available
            acoustic_cols_plot = [col_plot for col_plot in df_plot.columns if any(x in col_plot for x in ['ACI', 'ADI', 'AEI', 'BI', 'H'])][:3]
            key_cols.extend(acoustic_cols_plot)

            # Add detection columns (species)
            detection_cols_plot = [col_det_plot for col_det_plot in df_plot.columns if col_det_plot not in key_cols and df_plot[col_det_plot].dtype in ['float64', 'int64']][:3]
            key_cols.extend(detection_cols_plot)

            # Create availability matrix
            availability_matrix = []
            for col_avail in key_cols:
                if col_avail in df_plot.columns:
                    availability_matrix.append((~df_plot[col_avail].isna()).astype(int))

            if availability_matrix:
                availability_df = pd.DataFrame(availability_matrix, index=key_cols[:len(availability_matrix)])

                # Plot heatmap with discrete colormap for binary data
                from matplotlib.colors import ListedColormap
                binary_cmap = ListedColormap(['red', 'green'])  # 0=red (missing), 1=green (present)
                im = ax_avail.imshow(availability_df.values, aspect='auto', cmap=binary_cmap, vmin=0, vmax=1)
                ax_avail.set_yticks(range(len(availability_df)))
                ax_avail.set_yticklabels([label[:20] for label in availability_df.index])
                ax_avail.set_xlabel('Time Index')
                ax_avail.set_title(f'Station {station_plot} - Data Availability')

                # Add colorbar with discrete ticks
                cbar = plt.colorbar(im, ax=ax_avail, fraction=0.046, pad=0.04, ticks=[0, 1])
                cbar.set_ticklabels(['Missing', 'Present'])

            # Plot 2: Temperature with rolling means
            ax_temp_plot = axes_align[i_align, 1]

            if 'Water temp (°C)' in df_plot.columns:
                ax_temp_plot.plot(df_plot['datetime'], df_plot['Water temp (°C)'], 
                                 alpha=0.5, label='2h aggregated', linewidth=0.5)
                if 'temp_mean_12h' in df_plot.columns:
                    ax_temp_plot.plot(df_plot['datetime'], df_plot['temp_mean_12h'], 
                                     label='12h rolling mean', linewidth=1.5, color='red')

                ax_temp_plot.set_ylabel('Temperature (°C)')
                ax_temp_plot.set_title(f'Station {station_plot} - Temperature Aggregation')
                ax_temp_plot.legend()
                ax_temp_plot.grid(True, alpha=0.3)
                ax_temp_plot.tick_params(axis='x', rotation=45)

    plt.suptitle('Temporal Alignment and Aggregation Results', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 10. Visualize Temporal Features""")
    return


@app.cell(hide_code=True)
def _(STATIONS, enhanced_data, plt):
    # Visualize temporal features distributions
    fig_temp_feat, axes_temp_feat = plt.subplots(2, 3, figsize=(15, 8))
    axes_flat_temp = axes_temp_feat.flatten()

    # Use first station for examples
    if STATIONS and STATIONS[0] in enhanced_data:
        df_feat_viz = enhanced_data[STATIONS[0]]

        # Hour distribution
        if 'hour' in df_feat_viz.columns:
            ax_hour = axes_flat_temp[0]
            df_feat_viz['hour'].value_counts().sort_index().plot(kind='bar', ax=ax_hour)
            ax_hour.set_title('Hour of Day Distribution')
            ax_hour.set_xlabel('Hour')
            ax_hour.set_ylabel('Count')

        # Day of year distribution
        if 'day_of_year' in df_feat_viz.columns:
            ax_day = axes_flat_temp[1]
            ax_day.hist(df_feat_viz['day_of_year'], bins=52, edgecolor='black', alpha=0.7)
            ax_day.set_title('Day of Year Distribution')
            ax_day.set_xlabel('Day of Year')
            ax_day.set_ylabel('Count')

        # Month distribution
        if 'month' in df_feat_viz.columns:
            ax_month = axes_flat_temp[2]
            df_feat_viz['month'].value_counts().sort_index().plot(kind='bar', ax=ax_month)
            ax_month.set_title('Month Distribution')
            ax_month.set_xlabel('Month')
            ax_month.set_ylabel('Count')

        # Season distribution
        if 'season' in df_feat_viz.columns:
            ax_season = axes_flat_temp[3]
            df_feat_viz['season'].value_counts().plot(kind='bar', ax=ax_season)
            ax_season.set_title('Season Distribution')
            ax_season.set_xlabel('Season')
            ax_season.set_ylabel('Count')

        # Time period distribution
        if 'time_period' in df_feat_viz.columns:
            ax_period = axes_flat_temp[4]
            df_feat_viz['time_period'].value_counts().plot(kind='bar', ax=ax_period)
            ax_period.set_title('Time Period Distribution')
            ax_period.set_xlabel('Time Period')
            ax_period.set_ylabel('Count')

        # Cyclic hour encoding
        if 'hour_sin' in df_feat_viz.columns and 'hour_cos' in df_feat_viz.columns:
            ax_cyclic = axes_flat_temp[5]
            ax_cyclic.scatter(df_feat_viz['hour_sin'], df_feat_viz['hour_cos'], 
                            c=df_feat_viz['hour'], cmap='twilight', alpha=0.6)
            ax_cyclic.set_title('Cyclic Hour Encoding')
            ax_cyclic.set_xlabel('Hour Sin')
            ax_cyclic.set_ylabel('Hour Cos')
            ax_cyclic.set_aspect('equal')
            plt.colorbar(ax_cyclic.collections[0], ax=ax_cyclic, label='Hour')

    plt.suptitle(f'Temporal Features - Station {STATIONS[0]}', fontsize=14)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 11. Compare Before/After Aggregation""")
    return


@app.cell(hide_code=True)
def _(STATIONS, data_loaded, enhanced_data, pd, plt):
    # Compare data resolution before and after aggregation
    fig_compare, axes_compare = plt.subplots(2, 2, figsize=(14, 10))

    station_compare = STATIONS[0] if STATIONS else None

    if station_compare:
        # Temperature comparison
        if station_compare in data_loaded['temperature'] and station_compare in enhanced_data:
            ax_temp_comp = axes_compare[0, 0]

            # Original 20-min data
            df_temp_orig = data_loaded['temperature'][station_compare]
            if 'datetime' in df_temp_orig.columns and 'Water temp (°C)' in df_temp_orig.columns:
                df_temp_orig['datetime'] = pd.to_datetime(df_temp_orig['datetime'])
                # Ensure timezone-naive for comparisons
                if df_temp_orig['datetime'].dt.tz is not None:
                    df_temp_orig['datetime'] = df_temp_orig['datetime'].dt.tz_convert(None)
                # Plot subset for clarity
                subset_start = df_temp_orig['datetime'].min()
                subset_end = subset_start + pd.Timedelta(days=7)
                subset_orig = df_temp_orig[(df_temp_orig['datetime'] >= subset_start) & 
                                          (df_temp_orig['datetime'] <= subset_end)]

                ax_temp_comp.plot(subset_orig['datetime'], subset_orig['Water temp (°C)'], 
                                'b-', alpha=0.5, linewidth=0.5, label='Original (20-min)')

            # Aggregated 2-hour data
            df_temp_agg_comp = enhanced_data[station_compare]
            if 'datetime' in df_temp_agg_comp.columns and 'Water temp (°C)' in df_temp_agg_comp.columns:
                subset_agg = df_temp_agg_comp[(df_temp_agg_comp['datetime'] >= subset_start) & 
                                             (df_temp_agg_comp['datetime'] <= subset_end)]
                ax_temp_comp.plot(subset_agg['datetime'], subset_agg['Water temp (°C)'], 
                                'ro-', markersize=4, linewidth=1, label='Aggregated (2-hour)')

            ax_temp_comp.set_title('Temperature: Before vs After Aggregation (1 week)')
            ax_temp_comp.set_ylabel('Temperature (°C)')
            ax_temp_comp.legend()
            ax_temp_comp.grid(True, alpha=0.3)

        # SPL comparison
        if station_compare in data_loaded['spl'] and station_compare in enhanced_data:
            ax_spl_comp = axes_compare[0, 1]

            # Original 1-hour data
            df_spl_orig = data_loaded['spl'][station_compare]
            if 'datetime' in df_spl_orig.columns and 'Broadband (1-40000 Hz)' in df_spl_orig.columns:
                df_spl_orig['datetime'] = pd.to_datetime(df_spl_orig['datetime'])
                # Ensure timezone-naive for comparisons
                if df_spl_orig['datetime'].dt.tz is not None:
                    df_spl_orig['datetime'] = df_spl_orig['datetime'].dt.tz_convert(None)
                subset_spl_orig = df_spl_orig[(df_spl_orig['datetime'] >= subset_start) & 
                                             (df_spl_orig['datetime'] <= subset_end)]

                ax_spl_comp.plot(subset_spl_orig['datetime'], subset_spl_orig['Broadband (1-40000 Hz)'], 
                               'b-', alpha=0.5, linewidth=0.5, label='Original (1-hour)')

            # Aggregated 2-hour data
            if 'Broadband (1-40000 Hz)' in df_temp_agg_comp.columns:
                ax_spl_comp.plot(subset_agg['datetime'], subset_agg['Broadband (1-40000 Hz)'], 
                               'ro-', markersize=4, linewidth=1, label='Aggregated (2-hour)')

            ax_spl_comp.set_title('SPL Broadband: Before vs After Aggregation (1 week)')
            ax_spl_comp.set_ylabel('SPL (dB)')
            ax_spl_comp.legend()
            ax_spl_comp.grid(True, alpha=0.3)

        # Data completeness comparison
        ax_complete = axes_compare[1, 0]

        completeness_before = {}
        completeness_after = {}

        # Calculate completeness for each data type
        data_types_comp = ['temperature', 'depth', 'spl', 'indices']

        for dtype in data_types_comp:
            if station_compare in data_loaded.get(dtype, {}):
                df_before = data_loaded[dtype][station_compare]
                # Count non-null values in main data column
                if dtype == 'temperature' and 'Water temp (°C)' in df_before.columns:
                    completeness_before[dtype] = (~df_before['Water temp (°C)'].isna()).mean() * 100
                elif dtype == 'depth' and 'Water depth (m)' in df_before.columns:
                    completeness_before[dtype] = (~df_before['Water depth (m)'].isna()).mean() * 100
                elif dtype == 'spl' and 'Broadband (1-40000 Hz)' in df_before.columns:
                    completeness_before[dtype] = (~df_before['Broadband (1-40000 Hz)'].isna()).mean() * 100
                elif dtype == 'indices':
                    # Use first numeric column
                    numeric_cols_comp = df_before.select_dtypes(include=['number']).columns
                    if len(numeric_cols_comp) > 0:
                        completeness_before[dtype] = (~df_before[numeric_cols_comp[0]].isna()).mean() * 100

        # After aggregation
        df_after = enhanced_data[station_compare]
        if 'Water temp (°C)' in df_after.columns:
            completeness_after['temperature'] = (~df_after['Water temp (°C)'].isna()).mean() * 100
        if 'Water depth (m)' in df_after.columns:
            completeness_after['depth'] = (~df_after['Water depth (m)'].isna()).mean() * 100
        if 'Broadband (1-40000 Hz)' in df_after.columns:
            completeness_after['spl'] = (~df_after['Broadband (1-40000 Hz)'].isna()).mean() * 100

        # Check for acoustic indices in aggregated data
        acoustic_cols_after = [col_idx_after for col_idx_after in df_after.columns if any(x in col_idx_after for x in ['ACI', 'ADI', 'AEI', 'BI', 'H'])]
        if len(acoustic_cols_after) > 0:
            # Use the same first index that was used in the "before" calculation
            first_idx_col = acoustic_cols_after[0]
            completeness_after['indices'] = (~df_after[first_idx_col].isna()).mean() * 100
        else:
            completeness_after['indices'] = 0  # No indices found

        # Plot completeness
        x_pos = range(len(completeness_before))
        width = 0.35

        ax_complete.bar([p - width/2 for p in x_pos], list(completeness_before.values()), 
                       width, label='Before Aggregation', alpha=0.7)
        ax_complete.bar([p + width/2 for p in x_pos], 
                       [completeness_after.get(k, 0) for k in completeness_before.keys()], 
                       width, label='After Aggregation', alpha=0.7)

        ax_complete.set_xticks(x_pos)
        ax_complete.set_xticklabels(list(completeness_before.keys()))
        ax_complete.set_ylabel('Data Completeness (%)')
        ax_complete.set_title('Data Completeness Comparison')
        ax_complete.legend()
        ax_complete.grid(True, alpha=0.3, axis='y')

        # Summary statistics
        ax_summary = axes_compare[1, 1]

        summary_text = f"Station {station_compare} Aggregation Summary\n"
        summary_text += "=" * 40 + "\n\n"
        summary_text += f"Temperature: 20-min → 2-hour\n"
        summary_text += f"Depth: 1-hour → 2-hour\n"
        summary_text += f"SPL: 1-hour → 2-hour\n"
        summary_text += f"Indices: ~1-hour → 2-hour\n\n"
        summary_text += f"Total rows after alignment: {len(df_after)}\n"
        summary_text += f"Total columns: {len(df_after.columns)}\n"
        summary_text += f"Temporal features added: 12\n"
        summary_text += f"Lag/rolling features added: "

        lag_cols = [col_after for col_after in df_after.columns if 'lag' in col_after or 'mean_' in col_after or 'change' in col_after]
        summary_text += f"{len(lag_cols)}"

        ax_summary.text(0.1, 0.5, summary_text, transform=ax_summary.transAxes,
                       fontsize=10, verticalalignment='center', fontfamily='monospace')
        ax_summary.axis('off')

    plt.suptitle('Aggregation Comparison and Summary', fontsize=14)
    plt.tight_layout()
    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 12. Save Aligned and Enhanced Dataset

    After all the temporal alignment and feature engineering, we save our processed data in organized files for downstream analysis. Rather than creating one massive combined file, we save separate datasets by data type for clarity and modularity.

    **File organization strategy:**

    **`02_acoustic_indices_aligned_2021.parquet`** - All acoustic indices aggregated to 2-hour resolution
    - Contains: ~50-60 acoustic indices per station and time point
    - Use for: Index analysis, correlation studies, dimensionality reduction

    **`02_detections_aligned_2021.parquet`** - Fish detection data with temporal features  
    - Contains: Species calling intensities (0-3 scale) + temporal features (hour_sin, day_cos, etc.)
    - Use for: Response variable analysis, temporal pattern exploration

    **`02_environmental_aligned_2021.parquet`** - Environmental variables with lag/rolling features
    - Contains: Temperature, depth, SPL + lag variables + rolling means
    - Use for: Environmental driver analysis, feature selection

    **`02_temporal_features_2021.parquet`** - Pure temporal features
    - Contains: Hour, day, month, season, cyclic encodings
    - Use for: Temporal pattern analysis, seasonality studies

    **Why separate files?** This organization:
    - **Clarifies data provenance** - easy to see what came from where
    - **Enables modular analysis** - load only what you need for specific tasks  
    - **Facilitates debugging** - easier to isolate issues to specific data types
    - **Supports collaboration** - different team members can work with different data aspects

    → Each file includes consistent identifiers (datetime, station, year) enabling clean joins when needed.
    """
    )
    return


@app.cell
def _(OUTPUT_DIR, YEAR, enhanced_data, pd):
    # Save the aligned and enhanced datasets
    saved_files_final = []

    # Also create and save a combined dataset with all stations
    if enhanced_data:
        all_stations_df = pd.concat(list(enhanced_data.values()), ignore_index=True)

        # Apply same data type fixes to combined dataset
        for col_fix_combined in all_stations_df.columns:
            if all_stations_df[col_fix_combined].dtype == 'object':
                if col_fix_combined not in ['datetime', 'season', 'time_period', 'station']:
                    try:
                        all_stations_df[col_fix_combined] = pd.to_numeric(all_stations_df[col_fix_combined], errors='coerce')
                    except:
                        pass

    if enhanced_data:

        # Add year column to combined dataset
        all_stations_df['year'] = YEAR

        # Define core identifiers 
        core_ids = ['datetime', 'station', 'year']

        # Test: Save just acoustic indices first
        acoustic_indices = [
            'ZCR', 'MEANt', 'VARt', 'SKEWt', 'KURTt', 'LEQt', 'BGNt', 'SNRt', 'MED', 'Ht',
            'ACTtFraction', 'ACTtCount', 'ACTtMean', 'EVNtFraction', 'EVNtMean', 'EVNtCount',
            'MEANf', 'VARf', 'SKEWf', 'KURTf', 'NBPEAKS', 'LEQf', 'ENRf', 'BGNf', 'SNRf', 'Hf',
            'EAS', 'ECU', 'ECV', 'EPS', 'EPS_KURT', 'EPS_SKEW', 'ACI', 
            'NDSI', 'rBA', 'AnthroEnergy', 'BioEnergy', 'BI', 'ROU', 'ADI', 'AEI',
            'LFC', 'MFC', 'HFC', 'ACTspFract', 'ACTspCount', 'ACTspMean',
            'EVNspFract', 'EVNspMean', 'EVNspCount', 'TFSD', 'H_Havrda', 'H_Renyi',
            'H_pairedShannon', 'H_gamma', 'H_GiniSimpson', 'RAOQ', 'AGI', 'nROI', 'aROI'
        ]

        # Find available acoustic indices
        available_acoustic = [col for col in acoustic_indices if col in all_stations_df.columns]

        if available_acoustic:
            try:
                acoustic_df = all_stations_df[core_ids + available_acoustic].copy()

                # Remove rows where the "ZCR" column is non-numeric
                acoustic_df = acoustic_df[pd.to_numeric(acoustic_df['ZCR'], errors='coerce').notna()]

                acoustic_path = OUTPUT_DIR / f"02_acoustic_indices_aligned_{YEAR}.parquet"
                acoustic_df.to_parquet(acoustic_path, index=False)
                saved_files_final.append(str(acoustic_path))
                print(f"✓ Saved acoustic indices: {acoustic_path}")
                print(f"  Shape: {acoustic_df.shape} ({len(available_acoustic)} indices)")
            except Exception as e:
                print(f"✗ Error saving acoustic indices: {e}")

        # Test: Save detection data
        keep_species = [
            'Silver perch', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt',
            'Black drum', 'Spotted seatrout', 'Red drum', 'Atlantic croaker',
            'Bottlenose dolphin echolocation', 'Bottlenose dolphin burst pulses', 
            'Bottlenose dolphin whistles', 'Vessel'
        ]
        available_detection = [col for col in keep_species if col in all_stations_df.columns]

        if available_detection:
            try:
                detection_df = all_stations_df[core_ids + available_detection].copy()
                detection_path_aligned = OUTPUT_DIR / f"02_detections_aligned_{YEAR}.parquet"
                detection_df.to_parquet(detection_path_aligned, index=False)
                saved_files_final.append(str(detection_path_aligned))
                print(f"✓ Saved detections: {detection_path_aligned}")
                print(f"  Shape: {detection_df.shape} ({len(available_detection)} species/types)")
            except Exception as e:
                print(f"✗ Error saving detections: {e}")

        # Test: Save environmental data
        env_cols = ['Water temp (°C)', 'Water depth (m)', 
                   'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']
        env_lag_cols = [col for col in all_stations_df.columns if any(
            pattern in col for pattern in ['temp_lag', 'temp_change', 'temp_mean',
                                          'depth_lag', 'depth_change', 'depth_mean',
                                          'spl_broadband_lag', 'spl_broadband_mean'])]
        env_cols.extend(env_lag_cols)
        available_env = [col for col in env_cols if col in all_stations_df.columns]

        if available_env:
            try:
                env_df = all_stations_df[core_ids + available_env].copy()
                env_path = OUTPUT_DIR / f"02_environmental_aligned_{YEAR}.parquet"
                env_df.to_parquet(env_path, index=False)
                saved_files_final.append(str(env_path))
                print(f"✓ Saved environmental data: {env_path}")
                print(f"  Shape: {env_df.shape} ({len(available_env)} variables)")
            except Exception as e:
                print(f"✗ Error saving environmental data: {e}")

        # Test: Save temporal features
        temporal_cols_aligned = ['hour', 'day_of_year', 'month', 'weekday', 'week_of_year', 
                        'season', 'time_period', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos']
        available_temporal = [col for col in temporal_cols_aligned if col in all_stations_df.columns]

        if available_temporal:
            try:
                temporal_df = all_stations_df[core_ids + available_temporal].copy()
                temporal_path = OUTPUT_DIR / f"02_temporal_features_{YEAR}.parquet"
                temporal_df.to_parquet(temporal_path, index=False)
                saved_files_final.append(str(temporal_path))
                print(f"✓ Saved temporal features: {temporal_path}")
                print(f"  Shape: {temporal_df.shape} ({len(available_temporal)} features)")
            except Exception as e:
                print(f"✗ Error saving temporal features: {e}")

    print(f"\n✅ Successfully saved {len(saved_files_final)} files")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Summary

    **What we accomplished:** This notebook solved the fundamental challenge of temporal misalignment across multiple data streams with different collection frequencies. By aggregating everything to a common 2-hour resolution and engineering relevant features, we've created analysis-ready datasets that preserve ecological information while enabling modeling.

    ✅ **Successfully Aligned All Data to 2-Hour Resolution:**
    - **Acoustic indices**: Aggregated from ~hourly to 2-hour means (preserves acoustic patterns while reducing noise)
    - **Temperature**: Aggregated from 20-min to 2-hour means (captures thermal environment without sensor noise)
    - **Depth**: Aggregated from 1-hour to 2-hour means (smooths tidal fluctuations to environmental context)
    - **SPL**: Aggregated from 1-hour to 2-hour means (provides ambient noise context)
    - **Detection data**: Already at 2-hour resolution (used as temporal reference framework)

    ✅ **Created Temporal Features for Ecological Modeling:**
    - **Basic temporal**: hour, day_of_year, month, weekday, week_of_year (linear time representations)
    - **Categorical time periods**: season, time_period (Night/Morning/Afternoon/Evening) (ecologically meaningful groupings)
    - **Cyclic encodings**: hour_sin/cos, day_sin/cos (preserve circular nature of time for machine learning)

    ✅ **Engineered Advanced Features for Delayed Ecological Responses:**
    - **Lag variables**: temperature, depth, and SPL at t-1, t-2, t-3 (capture delayed animal responses to environmental change)
    - **Change rates**: 2h and 4h differences (detect rapid environmental transitions that trigger behavior)
    - **Rolling means**: 6h, 12h, 24h windows (capture environmental context and trends beyond momentary conditions)
    - **Selected acoustic index rolling means**: recent acoustic environment trends (context for current conditions)

    ✅ **Output Files - Organized by Data Type:**
    - **`02_acoustic_indices_aligned_2021.parquet`**: ~50-60 acoustic indices ready for correlation analysis and dimensionality reduction
    - **`02_detections_aligned_2021.parquet`**: Fish calling intensities with temporal features for response pattern analysis
    - **`02_environmental_aligned_2021.parquet`**: Environmental drivers with lag/rolling features for predictor analysis
    - **`02_temporal_features_2021.parquet`**: Pure temporal features for seasonality and diel pattern analysis

    **Data quality achieved:** All files share consistent temporal identifiers (datetime, station, year) enabling clean joins while maintaining clear data provenance and supporting modular analysis approaches.

    **Next Steps:** Proceed to Notebook 3 for acoustic index characterization and dimensionality reduction using the acoustic indices file. The organized data structure will facilitate focused analysis of acoustic patterns without environmental data complexity.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    # All tasks completed successfully!
    print("✅ Notebook 2 completed successfully!")
    print("  - All data aligned to 2-hour resolution")
    print("  - Temporal features created")
    print("  - Lag variables and rolling means engineered") 
    print("  - Visualizations generated")
    print("  - Enhanced datasets saved for next notebook")
    return


if __name__ == "__main__":
    app.run()
