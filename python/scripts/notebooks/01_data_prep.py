import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Notebook 1: Data Loading and Initial Exploration

    **Purpose**: Load all data streams and perform initial quality assessment  
    **Key Outputs**: Raw data summaries, temporal coverage plots, missing data visualization

    This notebook processes data from three moored hydrophone stations (9M, 14M, 37M) deployed near May River in 2021. (Note that we do plan to also process 2018 data but are starting here.) We're combining multiple data streams to understand marine biodiversity patterns:

    - **Acoustic indices**: Computed soundscape metrics that capture ecosystem acoustic activity 
    - **Manual fish detections**: Human-annotated intensity level of fish species every 2 hours (where intensity level is a 0-3 integer scale with 0 being no calls, 1 being one, 2 being multiple, and 3 being a chorus where calls cannot be distinguished from each other.)
    - **Environmental data**: Temperature (20-min intervals) and depth (1-hour intervals) measurements. Depth data can be used as a proxy for tide.
    - **SPL data**: Sound pressure levels across frequency bands (broadband, low 50-1200Hz, high 7000-40000Hz)
    - **Vessel detections**: Ship noise events (included in manual detection files)

    Each data type was collected at different temporal resolutions, requiring careful alignment for integrated analysis.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    import warnings
    warnings.filterwarnings('ignore')

    # Set up plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Define constants
    STATIONS = ['9M', '14M', '37M']
    YEAR = 2021
    DATA_DIR = Path("../data/raw")
    OUTPUT_DIR = Path("../data/processed")

    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("✓ Libraries imported and constants defined")
    return DATA_DIR, OUTPUT_DIR, STATIONS, YEAR, np, pd, plt, sns


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 1. Load Acoustic Indices Data

    Acoustic indices are mathematical summaries of soundscape recordings that capture different aspects of ecosystem acoustic activity. The FullBW (full bandwidth) version includes indices computed across the entire frequency range of the hydrophones. These metrics help quantify biodiversity, ecosystem health, and acoustic complexity without requiring species-specific identification.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, STATIONS, YEAR, pd):
    # Load acoustic indices (FullBW version)
    indices_data = {}
    indices_info = {}

    for station_idx in STATIONS:
        file_path_idx = DATA_DIR / "indices" / f"Acoustic_Indices_{station_idx}_{YEAR}_FullBW_v2_Final.csv"
        print(file_path_idx)

        if file_path_idx.exists():
            df_idx = pd.read_csv(file_path_idx)
            indices_data[station_idx] = df_idx
            indices_info[station_idx] = {
                'rows': len(df_idx),
                'columns': len(df_idx.columns),
                'file_size_mb': file_path_idx.stat().st_size / (1024*1024)
            }
            print(f"✓ Loaded {station_idx}: {len(df_idx)} rows, {len(df_idx.columns)} columns")
        else:
            print(f"✗ File not found: {file_path_idx}")

    # Display summary
    print(f"\nAcoustic indices loaded for {len(indices_data)} stations")
    return (indices_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 2. Load Manual Detection Data

    Human annotators listened to 2-minute audio segments recorded every 2 hours. They recorded fish calling intensity on a 0-3 scale (0=absent, 1 = one , 2 = more than one, 3 = chorus). This dataset provides ground truth for fish community composition and temporal patterns. Each Excel file contains both detection data and metadata sheets.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, STATIONS, YEAR, pd):
    # Load manual detection data
    detection_data = {}
    detection_info = {}

    for station_det in STATIONS:
        file_path_det = DATA_DIR / str(YEAR) / "detections" / f"Master_Manual_{station_det}_2h_{YEAR}.xlsx"

        if file_path_det.exists():
            # Load the "Data" sheet (skip "Metadata" sheet as noted in description)
            df_det = pd.read_excel(file_path_det, sheet_name="Data")
            detection_data[station_det] = df_det
            detection_info[station_det] = {
                'rows': len(df_det),
                'columns': len(df_det.columns),
                'file_size_mb': file_path_det.stat().st_size / (1024*1024)
            }
            print(f"✓ Loaded {station_det}: {len(df_det)} rows, {len(df_det.columns)} columns")
        else:
            print(f"✗ File not found: {file_path_det}")

    print(f"\nManual detection data loaded for {len(detection_data)} stations")
    return (detection_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 2.1 Filter Detection Data Using Species Metadata

    The original detection files contain columns for many species as well as various other non-biological sounds, but analysis focuses on a subset selected by Alyssa Marian and Eric Montie from the Montie Lab. We use a metadata file that flags which species to retain (keep_species=1) based on annotation quality and ecological relevance.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, detection_data, pd):
    # Load species metadata to filter detection columns
    metadata_path = DATA_DIR / "metadata" / "det_column_names.csv"

    if metadata_path.exists():
        metadata_df = pd.read_csv(metadata_path)

        # Get columns where keep_species = 1 (plus essential info columns)
        keep_columns = metadata_df[metadata_df['keep_species'] == 1]['long_name'].tolist()

        # Always keep essential info columns (Date, Time, etc.)
        essential_columns = ['Date', 'Date ', 'Time', 'Deployment ID', 'File']

        # Combine and filter detection data
        detection_data_filtered = {}

        for station_filter in detection_data.keys():
            df_filter = detection_data[station_filter].copy()

            # Find which columns exist in this dataset
            available_keep_cols = [col for col in keep_columns if col in df_filter.columns]
            available_essential_cols = [col for col in essential_columns if col in df_filter.columns]

            # Combine columns to keep
            cols_to_keep = list(set(available_keep_cols + available_essential_cols))

            # Filter the dataframe
            df_filtered = df_filter[cols_to_keep]
            detection_data_filtered[station_filter] = df_filtered

            print(f"Station {station_filter}: Filtered from {len(df_filter.columns)} to {len(cols_to_keep)} columns")
            print(f"  Species columns kept: {available_keep_cols}")

        # Replace original detection_data with filtered version
        detection_data.clear()
        detection_data.update(detection_data_filtered)

        print(f"\n✓ Applied species filtering based on keep_species=1")
        print(f"✓ Kept species: {', '.join(keep_columns)}")
    else:
        print(f"⚠️ Metadata file not found: {metadata_path}")
        print("Proceeding without species filtering")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 3. Load Environmental Data

    Environmental conditions strongly influence marine ecosystems and acoustic activity. Temperature affects fish metabolism and behavior, while depth changes indicate tidal cycles and water column dynamics. These measurements provide context for interpreting biological patterns in the acoustic data.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, STATIONS, YEAR, pd):
    # Load temperature data (20-minute intervals)
    temp_data = {}
    temp_info = {}

    for station_temp in STATIONS:
        file_path_temp = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station_temp}_Temp_{YEAR}.xlsx"

        if file_path_temp.exists():
            df_temp = pd.read_excel(file_path_temp, sheet_name="Data")
            temp_data[station_temp] = df_temp
            temp_info[station_temp] = {
                'rows': len(df_temp),
                'columns': len(df_temp.columns),
                'file_size_mb': file_path_temp.stat().st_size / (1024*1024)
            }
            print(f"✓ Temperature {station_temp}: {len(df_temp)} rows, {len(df_temp.columns)} columns")
        else:
            print(f"✗ File not found: {file_path_temp}")

    print(f"\nTemperature data loaded for {len(temp_data)} stations")
    return (temp_data,)


@app.cell(hide_code=True)
def _(DATA_DIR, STATIONS, YEAR, pd):
    # Load depth data (1-hour intervals)
    depth_data = {}
    depth_info = {}

    for station_depth in STATIONS:
        file_path_depth = DATA_DIR / str(YEAR) / "environmental" / f"Master_{station_depth}_Depth_{YEAR}.xlsx"

        if file_path_depth.exists():
            df_depth = pd.read_excel(file_path_depth, sheet_name="Data")
            depth_data[station_depth] = df_depth
            depth_info[station_depth] = {
                'rows': len(df_depth),
                'columns': len(df_depth.columns), 
                'file_size_mb': file_path_depth.stat().st_size / (1024*1024)
            }
            print(f"✓ Depth {station_depth}: {len(df_depth)} rows, {len(df_depth.columns)} columns")
        else:
            print(f"✗ File not found: {file_path_depth}")

    print(f"\nDepth data loaded for {len(depth_data)} stations")
    return (depth_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 4. Load SPL Data

    Sound Pressure Level (SPL) measurements quantify sound levels across different frequency bands. Broadband SPL captures overall acoustic energy, while low-frequency SPL often reflects vessel noise and high-frequency SPL captures biological sounds like fish calls and snapping shrimp. These measurements help separate anthropogenic from biological acoustic activity.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, STATIONS, YEAR, pd):
    # Load RMS SPL data (1-hour intervals)
    spl_data = {}
    spl_info = {}

    for station_spl in STATIONS:
        file_path_spl = DATA_DIR / str(YEAR) / "rms_spl" / f"Master_rmsSPL_{station_spl}_1h_{YEAR}.xlsx"

        if file_path_spl.exists():
            df_spl = pd.read_excel(file_path_spl, sheet_name="Data")
            spl_data[station_spl] = df_spl
            spl_info[station_spl] = {
                'rows': len(df_spl),
                'columns': len(df_spl.columns),
                'file_size_mb': file_path_spl.stat().st_size / (1024*1024)
            }
            print(f"✓ SPL {station_spl}: {len(df_spl)} rows, {len(df_spl.columns)} columns")
        else:
            print(f"✗ File not found: {file_path_spl}")

    print(f"\nSPL data loaded for {len(spl_data)} stations")
    return (spl_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 5. Data Structure Inspection

    Before analysis, we examine the structure and content of each dataset to understand column names, data types, and potential formatting issues. This step identifies inconsistencies between stations and datasets that need to be addressed during processing.
    """
    )
    return


@app.cell(hide_code=True)
def _(detection_data, indices_data, mo):
    # Examine data structure for first station
    station_inspect = '9M'

    if station_inspect in indices_data:
        indices_cols = list(indices_data[station_inspect].columns)
        print("Acoustic Indices Columns (first 10):")
        print(indices_cols[:10])
        print(f"... and {len(indices_cols)-10} more columns")

        # Show first few rows
        indices_sample = indices_data[station_inspect].head(3)

    if station_inspect in detection_data:
        detection_cols = list(detection_data[station_inspect].columns)
        print(f"\nDetection Data Columns:")
        print(detection_cols)

        # Show first few rows 
        detection_sample = detection_data[station_inspect].head(3)

    mo.md(f"""
    ### Sample Data Structure for Station {station_inspect}

    **Acoustic Indices**: {len(indices_cols) if 'indices_cols' in locals() else 'N/A'} columns  
    **Detection Data**: {len(detection_cols) if 'detection_cols' in locals() else 'N/A'} columns
    """)
    return


@app.cell(hide_code=True)
def _(depth_data, spl_data, temp_data):
    # Examine environmental and SPL data structure
    station_env = '9M'

    if station_env in temp_data:
        temp_cols_inspect = list(temp_data[station_env].columns)
        print("Temperature Data Columns:")
        print(temp_cols_inspect)

    if station_env in depth_data:
        depth_cols_inspect = list(depth_data[station_env].columns)
        print("Depth Data Columns:")
        print(depth_cols_inspect)

    if station_env in spl_data:
        spl_cols_inspect = list(spl_data[station_env].columns)
        print("SPL Data Columns:")
        print(spl_cols_inspect)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 6. Data Quality Assessment

    Data quality checks identify missing values, temporal gaps, and potential collection issues that could affect downstream analysis. We quantify completeness across all data types and stations to understand where our analysis might be limited by data availability.
    """
    )
    return


@app.cell(hide_code=True)
def _(
    STATIONS,
    depth_data,
    detection_data,
    indices_data,
    pd,
    spl_data,
    temp_data,
):
    # Create comprehensive data summary
    data_summary = {}

    for station_summary in STATIONS:
        summary = {'station': station_summary}

        # Acoustic indices
        if station_summary in indices_data:
            df_summary_idx = indices_data[station_summary]
            summary['indices_rows'] = len(df_summary_idx)
            summary['indices_cols'] = len(df_summary_idx.columns)
            summary['indices_missing'] = df_summary_idx.isnull().sum().sum()
            summary['indices_missing_pct'] = (df_summary_idx.isnull().sum().sum() / (len(df_summary_idx) * len(df_summary_idx.columns))) * 100

        # Detection data
        if station_summary in detection_data:
            df_summary_det = detection_data[station_summary]
            summary['detection_rows'] = len(df_summary_det)
            summary['detection_cols'] = len(df_summary_det.columns)
            summary['detection_missing'] = df_summary_det.isnull().sum().sum()
            summary['detection_missing_pct'] = (df_summary_det.isnull().sum().sum() / (len(df_summary_det) * len(df_summary_det.columns))) * 100

        # Temperature data  
        if station_summary in temp_data:
            df_summary_temp = temp_data[station_summary]
            summary['temp_rows'] = len(df_summary_temp)
            summary['temp_missing'] = df_summary_temp.isnull().sum().sum()
            summary['temp_missing_pct'] = (df_summary_temp.isnull().sum().sum() / (len(df_summary_temp) * len(df_summary_temp.columns))) * 100

        # Depth data
        if station_summary in depth_data:
            df_summary_depth = depth_data[station_summary]
            summary['depth_rows'] = len(df_summary_depth)
            summary['depth_missing'] = df_summary_depth.isnull().sum().sum()
            summary['depth_missing_pct'] = (df_summary_depth.isnull().sum().sum() / (len(df_summary_depth) * len(df_summary_depth.columns))) * 100

        # SPL data
        if station_summary in spl_data:
            df_summary_spl = spl_data[station_summary]
            summary['spl_rows'] = len(df_summary_spl)
            summary['spl_missing'] = df_summary_spl.isnull().sum().sum()
            summary['spl_missing_pct'] = (df_summary_spl.isnull().sum().sum() / (len(df_summary_spl) * len(df_summary_spl.columns))) * 100

        data_summary[station_summary] = summary

    # Convert to DataFrame for display
    summary_df = pd.DataFrame(data_summary).T
    summary_df = summary_df.round(2)

    print("Data Quality Summary:")
    print(summary_df)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 7. Temporal Coverage Analysis

    Different data types were collected at different frequencies, creating a complex temporal mosaic. This analysis visualizes when each data type was collected across the deployment period to identify overlapping time periods suitable for integrated analysis. Gaps in coverage may indicate equipment issues or maintenance periods.
    """
    )
    return


@app.cell(hide_code=True)
def _(
    STATIONS,
    depth_data,
    detection_data,
    indices_data,
    pd,
    plt,
    spl_data,
    temp_data,
):
    # Analyze temporal coverage - convert datetime columns and assess coverage
    temporal_analysis = {}

    fig_temporal, axes_temporal = plt.subplots(len(STATIONS), 1, figsize=(12, 4*len(STATIONS)))
    if len(STATIONS) == 1:
        axes_temporal = [axes_temporal]

    for i, station_temporal in enumerate(STATIONS):
        coverage_data_list = []

        # Detection data (2-hour intervals) - Use only Date column (contains full datetime)
        if station_temporal in detection_data:
            df_temporal_det = detection_data[station_temporal]
            # Handle Station 37M which has 'Date ' with trailing space
            date_col_temporal = 'Date' if 'Date' in df_temporal_det.columns else 'Date '
            if date_col_temporal in df_temporal_det.columns:
                df_temporal_det['datetime'] = pd.to_datetime(df_temporal_det[date_col_temporal], errors='coerce')
                coverage_data_list.extend([('Detections (2h)', dt) for dt in df_temporal_det['datetime'].dropna()])

        # Temperature data (20-min intervals) 
        if station_temporal in temp_data:
            df_temporal_temp = temp_data[station_temporal]
            if 'Date and time' in df_temporal_temp.columns:
                df_temporal_temp['datetime'] = pd.to_datetime(df_temporal_temp['Date and time'], errors='coerce')
                coverage_data_list.extend([('Temperature (20m)', dt) for dt in df_temporal_temp['datetime'].dropna()])

        # Depth data (1-hour intervals)
        if station_temporal in depth_data:
            df_temporal_depth = depth_data[station_temporal]
            if 'Date and time' in df_temporal_depth.columns:
                df_temporal_depth['datetime'] = pd.to_datetime(df_temporal_depth['Date and time'], errors='coerce')
                coverage_data_list.extend([('Depth (1h)', dt) for dt in df_temporal_depth['datetime'].dropna()])

        # SPL data (1-hour intervals) - Properly combine Date and Time columns
        if station_temporal in spl_data:
            df_temporal_spl = spl_data[station_temporal]
            if 'Date' in df_temporal_spl.columns and 'Time' in df_temporal_spl.columns:
                # Extract time component from Time column (ignore 1900 date part)
                try:
                    # Time column contains datetime objects from 1900, extract time component
                    combined_datetimes_temporal = []
                    for date_val_temporal, time_val_temporal in zip(df_temporal_spl['Date'], df_temporal_spl['Time']):
                        if pd.notna(date_val_temporal) and pd.notna(time_val_temporal):
                            # Handle different time formats - could be datetime or time object
                            if hasattr(time_val_temporal, 'time'):
                                # It's a datetime object, extract time part
                                time_part = time_val_temporal.time()
                            else:
                                # It's already a time object
                                time_part = time_val_temporal
                            # Combine with actual date
                            combined_dt_temporal = pd.to_datetime(date_val_temporal.date().strftime('%Y-%m-%d') + ' ' + time_part.strftime('%H:%M:%S'))
                            combined_datetimes_temporal.append(combined_dt_temporal)
                        else:
                            combined_datetimes_temporal.append(pd.NaT)

                    datetime_series_temporal = pd.Series(combined_datetimes_temporal)
                    valid_dates_temporal = datetime_series_temporal.dropna()
                    coverage_data_list.extend([('SPL (1h)', dt) for dt in valid_dates_temporal])
                except Exception as e:
                    print(f"Warning: Could not parse SPL datetime for station {station_temporal}: {e}")

        # Acoustic indices - need to check what datetime column exists
        if station_temporal in indices_data:
            df_temporal_idx = indices_data[station_temporal]
            datetime_col_temporal = None
            # Check for common datetime column names
            for col in ['datetime', 'DateTime', 'Date', 'time', 'Time']:
                if col in df_temporal_idx.columns:
                    datetime_col_temporal = col
                    break

            if datetime_col_temporal:
                df_temporal_idx['datetime'] = pd.to_datetime(df_temporal_idx[datetime_col_temporal], errors='coerce')
                coverage_data_list.extend([('Indices', dt) for dt in df_temporal_idx['datetime'].dropna()])

        if coverage_data_list:
            # Create timeline plot
            coverage_df_temporal = pd.DataFrame(coverage_data_list, columns=['Data_Type', 'DateTime'])

            # Plot timeline
            ax_temporal = axes_temporal[i]
            for j, data_type in enumerate(coverage_df_temporal['Data_Type'].unique()):
                subset_temporal = coverage_df_temporal[coverage_df_temporal['Data_Type'] == data_type]
                ax_temporal.scatter(subset_temporal['DateTime'], [j] * len(subset_temporal), alpha=0.6, s=1)

            ax_temporal.set_yticks(range(len(coverage_df_temporal['Data_Type'].unique())))
            ax_temporal.set_yticklabels(coverage_df_temporal['Data_Type'].unique())
            ax_temporal.set_title(f'Station {station_temporal} - Temporal Coverage')
            ax_temporal.set_xlabel('Date')
            ax_temporal.grid(True, alpha=0.3)

            # Store analysis results
            temporal_analysis[station_temporal] = {
                'data_types': len(coverage_df_temporal['Data_Type'].unique()),
                'total_points': len(coverage_df_temporal),
                'date_range': (coverage_df_temporal['DateTime'].min(), coverage_df_temporal['DateTime'].max())
            }

    plt.tight_layout()
    plt.show()

    print("\nTemporal Coverage Summary:")
    for station_temp_summary, info_temporal in temporal_analysis.items():
        if info_temporal['date_range'][0] is not pd.NaT:
            print(f"{station_temp_summary}: {info_temporal['data_types']} data types, "
                  f"{info_temporal['total_points']} total points, "
                  f"Range: {info_temporal['date_range'][0].date()} to {info_temporal['date_range'][1].date()}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 8. Basic Statistical Summaries

    Statistical summaries provide baseline understanding of environmental conditions and detection patterns across stations. These metrics help identify differences between sites and establish typical ranges for each measurement type, forming the foundation for anomaly detection and comparative analysis.
    """
    )
    return


@app.cell(hide_code=True)
def _(STATIONS, depth_data, detection_data, np, spl_data, temp_data):
    # Generate basic statistics for numerical columns
    stats_summary = {}

    for station_stats in STATIONS:
        station_stats_dict = {}

        # Detection data - focus on species counts (0-3 scale)
        if station_stats in detection_data:
            df_stats_det = detection_data[station_stats]
            # Identify numeric columns that represent species detections
            numeric_cols_stats = df_stats_det.select_dtypes(include=[np.number]).columns
            if len(numeric_cols_stats) > 0:
                station_stats_dict['detection_stats'] = df_stats_det[numeric_cols_stats].describe()

        # Temperature data
        if station_stats in temp_data:
            df_stats_temp = temp_data[station_stats]
            temp_col_stats = 'Water temp (°C)'
            if temp_col_stats in df_stats_temp.columns:
                station_stats_dict['temperature_stats'] = df_stats_temp[temp_col_stats].describe()

        # Depth data  
        if station_stats in depth_data:
            df_stats_depth = depth_data[station_stats]
            depth_col_stats = 'Water depth (m)'
            if depth_col_stats in df_stats_depth.columns:
                station_stats_dict['depth_stats'] = df_stats_depth[depth_col_stats].describe()

        # SPL data
        if station_stats in spl_data:
            df_stats_spl = spl_data[station_stats]
            spl_cols_stats = ['Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']
            available_spl_cols_stats = [col for col in spl_cols_stats if col in df_stats_spl.columns]
            if available_spl_cols_stats:
                station_stats_dict['spl_stats'] = df_stats_spl[available_spl_cols_stats].describe()

        stats_summary[station_stats] = station_stats_dict

    # Display key statistics
    print("Basic Statistical Summary:")
    print("=" * 50)

    for station_display in STATIONS:
        print(f"\nStation {station_display}:")
        print("-" * 20)

        if station_display in stats_summary:
            if 'temperature_stats' in stats_summary[station_display]:
                temp_stats_display = stats_summary[station_display]['temperature_stats']
                print(f"Temperature: {temp_stats_display['mean']:.1f}°C ± {temp_stats_display['std']:.1f}°C")
                print(f"  Range: {temp_stats_display['min']:.1f}°C to {temp_stats_display['max']:.1f}°C")

            if 'depth_stats' in stats_summary[station_display]:
                depth_stats_display = stats_summary[station_display]['depth_stats']
                print(f"Depth: {depth_stats_display['mean']:.1f}m ± {depth_stats_display['std']:.1f}m") 
                print(f"  Range: {depth_stats_display['min']:.1f}m to {depth_stats_display['max']:.1f}m")

            if 'spl_stats' in stats_summary[station_display]:
                spl_stats_display = stats_summary[station_display]['spl_stats']
                print("SPL (mean ± std):")
                for col_display in spl_stats_display.columns:
                    print(f"  {col_display}: {spl_stats_display.loc['mean', col_display]:.1f} ± {spl_stats_display.loc['std', col_display]:.1f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 9. Distribution Histograms for Acoustic Indices

    Acoustic indices often show non-normal distributions with characteristic shapes that reflect ecosystem properties. Examining these distributions helps identify data quality issues (unusual spikes or gaps) and informs appropriate statistical methods for downstream analysis. Some indices may be heavily skewed or multimodal, requiring transformation or specialized handling.
    """
    )
    return


@app.cell(hide_code=True)
def _(indices_data, np, plt):
    # Create distribution histograms for a subset of acoustic indices
    station_hist = '9M'  # Use first station for example

    if station_hist in indices_data:
        df_hist = indices_data[station_hist]

        # Select numeric columns (acoustic indices)
        numeric_cols_hist = df_hist.select_dtypes(include=[np.number]).columns.tolist()

        # Sample 12 indices for visualization (too many to show all)
        if len(numeric_cols_hist) > 12:
            # Try to get diverse indices by sampling every nth column
            step_hist = len(numeric_cols_hist) // 12
            selected_indices_hist = numeric_cols_hist[::step_hist][:12]
        else:
            selected_indices_hist = numeric_cols_hist

        # Create subplots
        fig_hist, axes_hist = plt.subplots(3, 4, figsize=(16, 10))
        axes_flat_hist = axes_hist.flatten()

        for i_hist, col_hist in enumerate(selected_indices_hist):
            if i_hist < len(axes_flat_hist):
                ax_hist = axes_flat_hist[i_hist]
                data_hist = df_hist[col_hist].dropna()

                ax_hist.hist(data_hist, bins=30, edgecolor='black', alpha=0.7)
                ax_hist.set_title(col_hist[:20] + '...' if len(col_hist) > 20 else col_hist)
                ax_hist.set_xlabel('Value')
                ax_hist.set_ylabel('Frequency')
                ax_hist.grid(True, alpha=0.3)

        # Hide unused subplots
        for i_hist in range(len(selected_indices_hist), len(axes_flat_hist)):
            axes_flat_hist[i_hist].set_visible(False)

        plt.suptitle(f'Distribution of Selected Acoustic Indices - Station {station_hist}', fontsize=14)
        plt.tight_layout()
        plt.show()

        print(f"Displayed distributions for {len(selected_indices_hist)} of {len(numeric_cols_hist)} acoustic indices")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 10. Correlation Heatmap of Acoustic Indices

    Many acoustic indices capture overlapping aspects of soundscape complexity, leading to high correlations between certain metrics. Identifying these relationships helps reduce dimensionality in later analysis and avoid redundancy. Highly correlated indices (|r| > 0.85) may measure similar acoustic properties and can potentially be grouped or one representative selected.
    """
    )
    return


@app.cell(hide_code=True)
def _(indices_data, np, plt, sns):
    # Create correlation heatmap for acoustic indices
    station_corr = '9M'

    if station_corr in indices_data:
        df_corr = indices_data[station_corr]

        # Select numeric columns only
        numeric_cols_corr = df_corr.select_dtypes(include=[np.number]).columns

        # Calculate correlation matrix
        corr_matrix = df_corr[numeric_cols_corr].corr()

        # Create mask for upper triangle
        mask_corr = np.triu(np.ones_like(corr_matrix, dtype=bool))

        # Create figure
        fig_corr, ax_corr = plt.subplots(figsize=(20, 16))

        # Create heatmap
        sns.heatmap(corr_matrix, 
                   mask=mask_corr,
                   cmap='coolwarm',
                   center=0,
                   vmin=-1, vmax=1,
                   square=True,
                   linewidths=0.5,
                   cbar_kws={"shrink": 0.8},
                   ax=ax_corr)

        ax_corr.set_title(f'Correlation Matrix of Acoustic Indices - Station {station_corr}', fontsize=14)
        plt.tight_layout()
        plt.show()

        # Find highly correlated pairs
        high_corr_pairs = []
        for i_corr in range(len(corr_matrix.columns)):
            for j_corr in range(i_corr+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i_corr, j_corr]) > 0.85:
                    high_corr_pairs.append((corr_matrix.columns[i_corr], 
                                           corr_matrix.columns[j_corr], 
                                           corr_matrix.iloc[i_corr, j_corr]))

        print(f"Correlation matrix shape: {corr_matrix.shape}")
        print(f"Found {len(high_corr_pairs)} highly correlated pairs (|r| > 0.85)")
        if len(high_corr_pairs) > 0:
            print("Top 5 highest correlations:")
            sorted_pairs = sorted(high_corr_pairs, key=lambda x: abs(x[2]), reverse=True)[:5]
            for pair in sorted_pairs:
                print(f"  {pair[0][:30]} <-> {pair[1][:30]}: {pair[2]:.3f}")
            print("\n→ High correlations suggest redundancy between these acoustic indices.")
            print("  Consider selecting representative indices from each highly correlated group.")
        else:
            print("\n→ No highly correlated pairs found - indices capture distinct acoustic properties.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 11. Time Series Plots of Environmental and SPL Data

    Time series visualization reveals temporal patterns in environmental conditions and acoustic levels. Temperature typically shows diel cycles and seasonal trends. Depth changes reflect tidal patterns. SPL variations may indicate daily activity patterns, weather effects, or anthropogenic noise events. These patterns provide important context for interpreting biological activity.
    """
    )
    return


@app.cell(hide_code=True)
def _(STATIONS, depth_data, pd, plt, spl_data, temp_data):
    # Create time series plots for temperature, depth, and SPL
    fig_ts, axes_ts = plt.subplots(3, 3, figsize=(18, 10))

    for col_idx_ts, station_ts in enumerate(STATIONS):
        # Temperature time series
        if station_ts in temp_data:
            df_temp_ts = temp_data[station_ts]
            if 'Date and time' in df_temp_ts.columns and 'Water temp (°C)' in df_temp_ts.columns:
                datetime_temp_ts = pd.to_datetime(df_temp_ts['Date and time'], errors='coerce')
                valid_idx_temp = datetime_temp_ts.notna()

                ax_temp_ts = axes_ts[0, col_idx_ts]
                ax_temp_ts.plot(datetime_temp_ts[valid_idx_temp], 
                              df_temp_ts.loc[valid_idx_temp, 'Water temp (°C)'], 
                              linewidth=0.5, alpha=0.7)
                ax_temp_ts.set_title(f'Temperature - Station {station_ts}')
                ax_temp_ts.set_ylabel('Temperature (°C)')
                ax_temp_ts.grid(True, alpha=0.3)
                ax_temp_ts.tick_params(axis='x', rotation=45)

        # Depth time series
        if station_ts in depth_data:
            df_depth_ts = depth_data[station_ts]
            if 'Date and time' in df_depth_ts.columns and 'Water depth (m)' in df_depth_ts.columns:
                datetime_depth_ts = pd.to_datetime(df_depth_ts['Date and time'], errors='coerce')
                valid_idx_depth = datetime_depth_ts.notna()

                ax_depth_ts = axes_ts[1, col_idx_ts]
                ax_depth_ts.plot(datetime_depth_ts[valid_idx_depth], 
                               df_depth_ts.loc[valid_idx_depth, 'Water depth (m)'], 
                               linewidth=0.5, alpha=0.7, color='green')
                ax_depth_ts.set_title(f'Depth - Station {station_ts}')
                ax_depth_ts.set_ylabel('Depth (m)')
                ax_depth_ts.grid(True, alpha=0.3)
                ax_depth_ts.tick_params(axis='x', rotation=45)

        # SPL time series (Broadband)
        if station_ts in spl_data:
            df_spl_ts = spl_data[station_ts]
            if 'Date' in df_spl_ts.columns and 'Broadband (1-40000 Hz)' in df_spl_ts.columns:
                # Create datetime from Date column (simpler approach)
                datetime_spl_ts = pd.to_datetime(df_spl_ts['Date'], errors='coerce')
                valid_idx_spl = datetime_spl_ts.notna()

                ax_spl_ts = axes_ts[2, col_idx_ts]
                ax_spl_ts.plot(datetime_spl_ts[valid_idx_spl], 
                             df_spl_ts.loc[valid_idx_spl, 'Broadband (1-40000 Hz)'], 
                             linewidth=0.5, alpha=0.7, color='red')
                ax_spl_ts.set_title(f'SPL Broadband - Station {station_ts}')
                ax_spl_ts.set_ylabel('SPL (dB)')
                ax_spl_ts.set_xlabel('Date')
                ax_spl_ts.grid(True, alpha=0.3)
                ax_spl_ts.tick_params(axis='x', rotation=45)

    plt.suptitle('Environmental and SPL Time Series by Station', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.show()

    print("Time series plots for temperature, depth, and SPL displayed")
    print("\n→ Look for:")
    print("  • Temperature: Diel cycles (daily warming/cooling) and seasonal trends")
    print("  • Depth: Tidal patterns (regular ~12.5 hour cycles) and longer-term changes")
    print("  • SPL: Daily activity patterns, weather events, and anthropogenic noise")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 12. Outlier Detection with Box Plots

    We use box plots to identify unusual values that may represent measurement errors, extreme environmental events, or interesting biological phenomena. Outliers in environmental data might indicate sensor malfunctions, while outliers in SPL data could represent ship passages or storm events. Species detection outliers might indicate unusual biological activity worth investigating further.
    """
    )
    return


@app.cell(hide_code=True)
def _(STATIONS, depth_data, detection_data, plt, spl_data, temp_data):
    # Create box plots for outlier detection
    fig_box, axes_box = plt.subplots(2, 3, figsize=(15, 8))

    # Collect data for box plots
    temp_data_box = []
    depth_data_box = []
    spl_broadband_box = []
    labels_box = []

    for station_box in STATIONS:
        labels_box.append(station_box)

        # Temperature
        if station_box in temp_data:
            df_temp_box = temp_data[station_box]
            if 'Water temp (°C)' in df_temp_box.columns:
                temp_data_box.append(df_temp_box['Water temp (°C)'].dropna())
            else:
                temp_data_box.append([])
        else:
            temp_data_box.append([])

        # Depth
        if station_box in depth_data:
            df_depth_box = depth_data[station_box]
            if 'Water depth (m)' in df_depth_box.columns:
                depth_data_box.append(df_depth_box['Water depth (m)'].dropna())
            else:
                depth_data_box.append([])
        else:
            depth_data_box.append([])

        # SPL Broadband
        if station_box in spl_data:
            df_spl_box = spl_data[station_box]
            if 'Broadband (1-40000 Hz)' in df_spl_box.columns:
                spl_broadband_box.append(df_spl_box['Broadband (1-40000 Hz)'].dropna())
            else:
                spl_broadband_box.append([])
        else:
            spl_broadband_box.append([])

    # Temperature box plots
    ax_temp_box = axes_box[0, 0]
    if any(len(d) > 0 for d in temp_data_box):
        bp_temp = ax_temp_box.boxplot([d for d in temp_data_box if len(d) > 0], 
                                      labels=[l for l, d in zip(labels_box, temp_data_box) if len(d) > 0])
        ax_temp_box.set_title('Temperature Distribution by Station')
        ax_temp_box.set_ylabel('Temperature (°C)')
        ax_temp_box.grid(True, alpha=0.3)

    # Depth box plots
    ax_depth_box = axes_box[0, 1]
    if any(len(d) > 0 for d in depth_data_box):
        bp_depth = ax_depth_box.boxplot([d for d in depth_data_box if len(d) > 0],
                                        labels=[l for l, d in zip(labels_box, depth_data_box) if len(d) > 0])
        ax_depth_box.set_title('Depth Distribution by Station')
        ax_depth_box.set_ylabel('Depth (m)')
        ax_depth_box.grid(True, alpha=0.3)

    # SPL Broadband box plots
    ax_spl_box = axes_box[0, 2]
    if any(len(d) > 0 for d in spl_broadband_box):
        bp_spl = ax_spl_box.boxplot([d for d in spl_broadband_box if len(d) > 0],
                                    labels=[l for l, d in zip(labels_box, spl_broadband_box) if len(d) > 0])
        ax_spl_box.set_title('SPL Broadband Distribution by Station')
        ax_spl_box.set_ylabel('SPL (dB)')
        ax_spl_box.grid(True, alpha=0.3)

    # SPL Low frequency box plots
    spl_low_box = []
    for station_box in STATIONS:
        if station_box in spl_data:
            df_spl_box = spl_data[station_box]
            if 'Low (50-1200 Hz)' in df_spl_box.columns:
                spl_low_box.append(df_spl_box['Low (50-1200 Hz)'].dropna())
            else:
                spl_low_box.append([])
        else:
            spl_low_box.append([])

    ax_spl_low_box = axes_box[1, 0]
    if any(len(d) > 0 for d in spl_low_box):
        bp_spl_low = ax_spl_low_box.boxplot([d for d in spl_low_box if len(d) > 0],
                                            labels=[l for l, d in zip(labels_box, spl_low_box) if len(d) > 0])
        ax_spl_low_box.set_title('SPL Low Freq Distribution by Station')
        ax_spl_low_box.set_ylabel('SPL (dB)')
        ax_spl_low_box.grid(True, alpha=0.3)

    # SPL High frequency box plots
    spl_high_box = []
    for station_box in STATIONS:
        if station_box in spl_data:
            df_spl_box = spl_data[station_box]
            if 'High (7000-40000 Hz)' in df_spl_box.columns:
                spl_high_box.append(df_spl_box['High (7000-40000 Hz)'].dropna())
            else:
                spl_high_box.append([])
        else:
            spl_high_box.append([])

    ax_spl_high_box = axes_box[1, 1]
    if any(len(d) > 0 for d in spl_high_box):
        bp_spl_high = ax_spl_high_box.boxplot([d for d in spl_high_box if len(d) > 0],
                                              labels=[l for l, d in zip(labels_box, spl_high_box) if len(d) > 0])
        ax_spl_high_box.set_title('SPL High Freq Distribution by Station')
        ax_spl_high_box.set_ylabel('SPL (dB)')
        ax_spl_high_box.grid(True, alpha=0.3)

    # Detection data - count non-zero detections
    detection_counts_box = []
    for station_box in STATIONS:
        if station_box in detection_data:
            df_det_box = detection_data[station_box]
            # Count non-zero values for each row (any species detected)
            numeric_cols_det_box = df_det_box.select_dtypes(include=['number']).columns
            if len(numeric_cols_det_box) > 0:
                row_sums_box = (df_det_box[numeric_cols_det_box] > 0).sum(axis=1)
                detection_counts_box.append(row_sums_box)
            else:
                detection_counts_box.append([])
        else:
            detection_counts_box.append([])

    ax_det_box = axes_box[1, 2]
    if any(len(d) > 0 for d in detection_counts_box):
        bp_det = ax_det_box.boxplot([d for d in detection_counts_box if len(d) > 0],
                                    labels=[l for l, d in zip(labels_box, detection_counts_box) if len(d) > 0])
        ax_det_box.set_title('Species Detection Count Distribution')
        ax_det_box.set_ylabel('Number of Species Detected')
        ax_det_box.grid(True, alpha=0.3)

    plt.suptitle('Outlier Detection Box Plots', fontsize=14)
    plt.tight_layout()
    plt.show()

    print("Box plots for outlier detection displayed")
    print("\n→ Outliers may indicate:")
    print("  • Environmental: Sensor malfunctions or extreme weather events")
    print("  • SPL: Ship passages, storm events, or equipment noise")
    print("  • Detections: Unusual biological activity or annotation inconsistencies")
    print("  Review outliers to determine if they represent real phenomena or data quality issues.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 13. Load and Process Metadata Files

    We have two important metadata files that provide context for our analyses:

    1. **Deployment Metadata**: Excel file containing detailed information about each hydrophone deployment including GPS coordinates, depths, environmental conditions, and instrument specifications
    2. **Acoustic Index Categories**: CSV file defining the 60 acoustic indices, their categories (Complexity, Temporal, Diversity, Spectral, Amplitude), and detailed descriptions

    These metadata files are essential for understanding the data collection context and interpreting the acoustic indices.
    """
    )
    return


@app.cell(hide_code=True)
def _(DATA_DIR, pd):
    # Load deployment metadata from Excel file
    metadata_excel_path = DATA_DIR / "metadata" / "1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
    metadata_data = {}

    if metadata_excel_path.exists():
        print("Loading deployment metadata...")

        # Read all sheets to understand structure
        xlsx_meta = pd.ExcelFile(metadata_excel_path)
        print(f"Found {len(xlsx_meta.sheet_names)} sheets: {xlsx_meta.sheet_names}")

        # Load the main "Data" sheet with deployment information
        df_deployments = pd.read_excel(metadata_excel_path, sheet_name="Data")
        metadata_data['deployments'] = df_deployments
        print(f"✓ Loaded deployments: {len(df_deployments)} records, {len(df_deployments.columns)} columns")

        # Load the "Key" sheet with column descriptions
        df_key = pd.read_excel(metadata_excel_path, sheet_name="Key")
        metadata_data['deployments_key'] = df_key
        print(f"✓ Loaded data dictionary: {len(df_key)} column descriptions")

        # Note: Skipping "Sheet1" as it appears to be a pivot table summary

        # Display key deployment info for 2021 (our focus year)
        df_2021 = df_deployments[df_deployments['Year'] == 2021]
        print(f"\n2021 Deployments: {len(df_2021)} records")
        if len(df_2021) > 0:
            print(f"Stations: {df_2021['Station'].unique()}")
            print(f"Date range: {df_2021['Start date'].min()} to {df_2021['End date'].max()}")
    else:
        print(f"✗ Deployment metadata not found: {metadata_excel_path}")

    # Load acoustic index categories from CSV
    index_csv_path = DATA_DIR / "metadata" / "Updated_Index_Categories_v2.csv"

    if index_csv_path.exists():
        print("\nLoading acoustic index categories...")
        df_index_categories = pd.read_csv(index_csv_path)
        metadata_data['index_categories'] = df_index_categories
        print(f"✓ Loaded index categories: {len(df_index_categories)} indices")

        # Show category distribution
        category_counts = df_index_categories['Category'].value_counts()
        print("\nIndex categories:")
        for cat, count in category_counts.items():
            print(f"  - {cat}: {count} indices")
    else:
        print(f"✗ Index categories not found: {index_csv_path}")

    return (metadata_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 14. Save Processed Data

    Clean, standardized datasets are saved in efficient Parquet format with consistent datetime columns and naming conventions. This preprocessing step ensures all subsequent notebooks can reliably load and combine data across different types and stations. The standardized timestamps enable temporal alignment in the next processing stage.
    """
    )
    return


@app.cell
def _(
    OUTPUT_DIR,
    STATIONS,
    YEAR,
    depth_data,
    detection_data,
    indices_data,
    metadata_data,
    pd,
    spl_data,
    temp_data,
):
    # Save cleaned datasets as parquet files with standardized column names and timestamps
    saved_files = []

    # Create metadata subdirectory
    metadata_dir = OUTPUT_DIR / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    for station_save in STATIONS:
        # Save acoustic indices
        if station_save in indices_data:
            df_save_idx = indices_data[station_save].copy()
            output_file_idx = OUTPUT_DIR / f"01_indices_{station_save}_{YEAR}.parquet"
            df_save_idx.to_parquet(output_file_idx, index=False)
            saved_files.append(str(output_file_idx))
            print(f"✓ Saved indices: {output_file_idx}")

        # Save detection data
        if station_save in detection_data:
            df_save_det = detection_data[station_save].copy()

            # Convert Time column to string to avoid Parquet conversion issues
            if 'Time' in df_save_det.columns:
                df_save_det['Time'] = df_save_det['Time'].astype(str)

            # Convert all object-type columns to string to avoid Arrow conversion issues
            object_cols = df_save_det.select_dtypes(include=['object']).columns
            for col_obj in object_cols:
                if col_obj not in ['Date', 'Date ']:  # Skip date columns
                    df_save_det[col_obj] = df_save_det[col_obj].astype(str)

            # Use only Date column (contains full datetime), handle Station 37M trailing space
            date_col_save = 'Date' if 'Date' in df_save_det.columns else 'Date '
            if date_col_save in df_save_det.columns:
                df_save_det['datetime'] = pd.to_datetime(df_save_det[date_col_save], errors='coerce')

            output_file_det = OUTPUT_DIR / f"01_detections_{station_save}_{YEAR}.parquet"
            df_save_det.to_parquet(output_file_det, index=False)
            saved_files.append(str(output_file_det))
            print(f"✓ Saved detections: {output_file_det}")

        # Save temperature data
        if station_save in temp_data:
            df_save_temp = temp_data[station_save].copy()
            if 'Date and time' in df_save_temp.columns:
                df_save_temp['datetime'] = pd.to_datetime(df_save_temp['Date and time'], errors='coerce')
            output_file_temp = OUTPUT_DIR / f"01_temperature_{station_save}_{YEAR}.parquet"
            df_save_temp.to_parquet(output_file_temp, index=False)
            saved_files.append(str(output_file_temp))
            print(f"✓ Saved temperature: {output_file_temp}")

        # Save depth data
        if station_save in depth_data:
            df_save_depth = depth_data[station_save].copy()
            if 'Date and time' in df_save_depth.columns:
                df_save_depth['datetime'] = pd.to_datetime(df_save_depth['Date and time'], errors='coerce')
            output_file_depth = OUTPUT_DIR / f"01_depth_{station_save}_{YEAR}.parquet"
            df_save_depth.to_parquet(output_file_depth, index=False)
            saved_files.append(str(output_file_depth))
            print(f"✓ Saved depth: {output_file_depth}")

        # Save SPL data
        if station_save in spl_data:
            df_save_spl = spl_data[station_save].copy()

            # Properly combine Date and Time columns BEFORE converting to string
            if 'Date' in df_save_spl.columns and 'Time' in df_save_spl.columns:
                try:
                    # Time column contains datetime objects from 1900, extract time component  
                    combined_datetimes_save = []
                    for date_val_save, time_val_save in zip(df_save_spl['Date'], df_save_spl['Time']):
                        if pd.notna(date_val_save) and pd.notna(time_val_save):
                            # Handle different time formats - could be datetime or time object
                            if hasattr(time_val_save, 'time'):
                                # It's a datetime object, extract time part
                                time_part_save = time_val_save.time()
                            else:
                                # It's already a time object
                                time_part_save = time_val_save

                            # Combine with actual date
                            combined_dt_save = pd.to_datetime(
                                date_val_save.date().strftime('%Y-%m-%d') + ' ' + 
                                time_part_save.strftime('%H:%M:%S')
                            )
                            combined_datetimes_save.append(combined_dt_save)
                        else:
                            combined_datetimes_save.append(pd.NaT)

                    df_save_spl['datetime'] = pd.Series(combined_datetimes_save)
                    print(f"✓ SPL {station_save}: Created {(~df_save_spl['datetime'].isna()).sum()} valid datetimes from {len(df_save_spl)} rows")

                except Exception as e:
                    print(f"Warning: Could not create datetime for SPL {station_save}: {e}")
                    # Fallback: just use Date column
                    df_save_spl['datetime'] = pd.to_datetime(df_save_spl['Date'], errors='coerce')

            # Convert Time column to string AFTER datetime creation to avoid Parquet conversion issues
            if 'Time' in df_save_spl.columns:
                df_save_spl['Time'] = df_save_spl['Time'].astype(str)

            output_file_spl = OUTPUT_DIR / f"01_spl_{station_save}_{YEAR}.parquet"
            df_save_spl.to_parquet(output_file_spl, index=False)
            saved_files.append(str(output_file_spl))
            print(f"✓ Saved SPL: {output_file_spl}")

    # Save metadata files
    if metadata_data:
        print("\nSaving metadata files...")

        # Save deployment data
        if 'deployments' in metadata_data:
            df_deployments_save = metadata_data['deployments'].copy()

            # Handle columns that should be numeric but contain mixed types
            # These columns contain things like 'No data', '.', or other strings mixed with numbers
            numeric_cols_to_fix = [
                'Number of deployed files collected',
                'Recorder No.',
                'Hydrophone Serial No.',
                'HOBO Water Temp logger No.',
                'HOBO Water level logger No.'
            ]

            for col_problem in numeric_cols_to_fix:
                if col_problem in df_deployments_save.columns:
                    # Convert to string first to handle mixed types, then to numeric
                    df_deployments_save[col_problem] = df_deployments_save[col_problem].astype(str)
                    # Replace common non-numeric values with NaN
                    df_deployments_save[col_problem] = df_deployments_save[col_problem].replace(
                        ['No data', '.', '', 'nan', 'None', 'NA'], pd.NA
                    )
                    # Convert to numeric, coercing errors to NaN
                    df_deployments_save[col_problem] = pd.to_numeric(df_deployments_save[col_problem], errors='coerce')

            # Convert date columns to datetime if they're stored as strings
            date_cols = ['Start date', 'End date', 'Public release date']
            for col_date in date_cols:
                if col_date in df_deployments_save.columns:
                    df_deployments_save[col_date] = pd.to_datetime(df_deployments_save[col_date], errors='coerce')

            # For remaining object columns that might have issues, convert to string
            # This ensures they can be saved to parquet without type conflicts
            for col_deps in df_deployments_save.columns:
                if df_deployments_save[col_deps].dtype == 'object':
                    # Skip datetime columns we already converted
                    if col_deps not in date_cols:
                        df_deployments_save[col_deps] = df_deployments_save[col_deps].astype(str)
                        # Replace 'nan' strings with actual NaN for cleaner data
                        df_deployments_save[col_deps] = df_deployments_save[col_deps].replace('nan', pd.NA)

            output_file_deployments = metadata_dir / "deployments.parquet"
            df_deployments_save.to_parquet(output_file_deployments, index=False)
            saved_files.append(str(output_file_deployments))
            print(f"✓ Saved deployments: {output_file_deployments}")

        # Save deployment data dictionary
        if 'deployments_key' in metadata_data:
            output_file_deploy_key = metadata_dir / "deployments_dictionary.parquet"
            metadata_data['deployments_key'].to_parquet(output_file_deploy_key, index=False)
            saved_files.append(str(output_file_deploy_key))
            print(f"✓ Saved deployment dictionary: {output_file_deploy_key}")

        # Save acoustic index categories
        if 'index_categories' in metadata_data:
            output_file_indices_cat = metadata_dir / "acoustic_indices.parquet"
            metadata_data['index_categories'].to_parquet(output_file_indices_cat, index=False)
            saved_files.append(str(output_file_indices_cat))
            print(f"✓ Saved acoustic index categories: {output_file_indices_cat}")

    print(f"\nTotal files saved: {len(saved_files)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Summary

    **Notebook 1 Complete!**

    ✅ **Data Successfully Loaded:**
    - Acoustic indices (2021, FullBW version, 3 stations)
    - Manual fish detection data (2021, 3 stations, 2-hour resolution) 
    - Environmental data (temperature 20-min, depth 1-hour, 3 stations)
    - SPL data (broadband/low/high frequency bands, 1-hour, 3 stations)
    - Vessel detection data (included in manual detections)
    - Deployment metadata (183 deployments 2017-2022, instrument specs, GPS locations)
    - Acoustic index categories (60 indices with descriptions)

    ✅ **Quality Assessment Completed:**
    - Temporal coverage analysis across all data types
    - Missing data quantification
    - Basic statistical summaries
    - Data structure inspection

    ✅ **Output Generated:**  
    - Clean datasets saved as parquet files with standardized timestamps
    - Metadata saved in `processed/metadata/` folder as parquet files
    - Ready for Notebook 2 (temporal alignment and aggregation)

    **Next Steps:** Proceed to Notebook 2 for temporal alignment to 2-hour resolution.
    """
    )
    return


if __name__ == "__main__":
    app.run()
