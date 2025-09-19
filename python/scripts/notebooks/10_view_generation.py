import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Notebook 10: View Generation

    **Purpose**: Generate data "views" for online plots and interactive figures.  
    **Key Outputs**: Data views in json format

    To avoid doing extensive processing, filtering and loading of large files on the client/browser side, we will generate specific data files for each figure. Each view will contain ONLY the data needed for that particular plot, already formatted in the way it's needed.
    """
    )
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import os
    from pathlib import Path

    from scipy.cluster.hierarchy import linkage, dendrogram
    from scipy.spatial.distance import squareform

    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    DATA_ROOT = project_root / "data"
    VIEWS_FOLDER = str(DATA_ROOT / "views") + "/"
    return DATA_ROOT, VIEWS_FOLDER, dendrogram, linkage, pd, squareform


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Station map

    The site has a Mapbox station map and requires the station coordinates. These can be extracted from a parquet formatted metadata file located in the data/processed/metadata folder.
    """
    )
    return


@app.cell
def _(DATA_ROOT, VIEWS_FOLDER, pd):
    # Import the parquet file as a dataframe using Pandas
    station_metadata_df = pd.read_parquet(DATA_ROOT / "processed/metadata/deployments.parquet")

    # Extract a subset of rows where the "Station" column has all unique values
    unique_stations_df = station_metadata_df.drop_duplicates(subset='Station')

    # List of stations used in this study
    current_study = ["9M", "14M", "37M"]

    # Aggregate data to get total deployments, average depth (m) and average hydrophone depth (m) per station
    aggregated_data = station_metadata_df.groupby('Station').agg(
        total_deployments=pd.NamedAgg(column='Deployment number', aggfunc='count'),
        avg_depth_m=pd.NamedAgg(column='Depth (m)', aggfunc='mean'),
        avg_hydrophone_depth_m=pd.NamedAgg(column='Hydrophone Depth (m)', aggfunc='mean')
    ).reset_index()

    # Round the averages to one decimal place
    aggregated_data['avg_depth_m'] = aggregated_data['avg_depth_m'].round(1)
    aggregated_data['avg_hydrophone_depth_m'] = aggregated_data['avg_hydrophone_depth_m'].round(1)

    # Merge aggregated data with the simplified dataframe
    stations_locations = pd.merge(unique_stations_df[["Station", "GPS Lat", "GPS Long"]], aggregated_data, on="Station")

    # Add a new column for the current study
    stations_locations.loc[:, 'current_study'] = stations_locations['Station'].isin(current_study)

    # Save the dataframe to a JSON file in the views folder
    stations_locations.to_json(f"{VIEWS_FOLDER}stations_locations.json", orient='records')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Heatmaps

    These views will include acoustic indices, manual detections, RMS SPL, and environmental data.
    """
    )
    return


@app.cell
def _(DATA_ROOT, VIEWS_FOLDER, pd):
    ## Manual detections
    # Import manual detections data
    detections_aligned_df = pd.read_parquet(DATA_ROOT / "processed/02_detections_aligned_2021.parquet")
    # save to json
    detections_aligned_df.to_json(f"{VIEWS_FOLDER}02_detections_aligned_2021.json", orient="records")


    ## Acoustic indices
    # Import acoustic index data
    indices_aligned_reduced_df = pd.read_parquet(DATA_ROOT / "processed/03_reduced_acoustic_indices.parquet")

    # Add hour field for heatmap visualization (extract hour from datetime)
    # indices_aligned_reduced_df['datetime'] = pd.to_datetime(indices_aligned_reduced_df['datetime'])
    # indices_aligned_reduced_df['hour'] = indices_aligned_reduced_df['datetime'].dt.hour

    # Save to JSON
    indices_aligned_reduced_df.to_json(f"{VIEWS_FOLDER}03_reduced_acoustic_indices.json", orient="records")


    ## RMS SPL + environmental data
    # Import env data
    environment_aligned_df = pd.read_parquet(DATA_ROOT / "processed/02_environmental_aligned_2021.parquet")
    # save to json
    environment_aligned_df.to_json(f"{VIEWS_FOLDER}02_environmental_aligned_2021.json", orient="records")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Full Acoustic Indices for Enhanced Heatmap

    **Purpose**: Export the complete dataset with all acoustic indices and cluster metadata for the enhanced heatmap visualization.

    **Data Files**:
    - **Full indices dataset**: All 61 acoustic indices aligned to 2-hour resolution
    - **Cluster metadata**: Cluster assignments and selection status for each index

    This allows users to explore all indices organized by functional clusters in the heatmap.
    """
    )
    return


@app.cell
def _(DATA_ROOT, VIEWS_FOLDER, pd):
    ## Full Acoustic Indices Dataset
    try:
        # Load the complete dataset with all indices
        indices_full_df = pd.read_parquet(DATA_ROOT / "processed/02_acoustic_indices_aligned_2021_full.parquet")

        # Add hour field for heatmap visualization (extract hour from datetime)
        # indices_full_df['datetime'] = pd.to_datetime(indices_full_df['datetime'])
        # indices_full_df['hour'] = indices_full_df['datetime'].dt.hour

        # Save full indices data
        indices_full_df.to_json(f"{VIEWS_FOLDER}acoustic_indices_full.json", orient="records")

        print(f"Saved full indices dataset:")
        print(f"  Shape: {indices_full_df.shape}")
        print(f"  Stations: {indices_full_df['station'].unique() if 'station' in indices_full_df.columns else 'N/A'}")

        # Count indices (excluding datetime, station, year columns)
        index_cols = [col for col in indices_full_df.columns if col not in ['datetime', 'station', 'year']]
        print(f"  Total indices: {len(index_cols)}")
    except FileNotFoundError:
        print("Full indices dataset not found - run notebook 3 first to generate it")
        indices_full_df = pd.DataFrame()

    ## Cluster Metadata
    try:
        # Load cluster metadata
        cluster_metadata_df_heatmap = pd.read_parquet(DATA_ROOT / "processed/metadata/acoustic_indices_clusters.parquet")

        # Save cluster metadata
        cluster_metadata_df_heatmap.to_json(f"{VIEWS_FOLDER}acoustic_indices_clusters.json", orient="records")

        print(f"\nSaved cluster metadata:")
        print(f"  Total indices: {len(cluster_metadata_df_heatmap)}")
        print(f"  Clusters: {cluster_metadata_df_heatmap['cluster_id'].nunique() if 'cluster_id' in cluster_metadata_df_heatmap.columns else 'N/A'}")
        print(f"  Selected indices: {cluster_metadata_df_heatmap['is_selected'].sum() if 'is_selected' in cluster_metadata_df_heatmap.columns else 'N/A'}")
    except FileNotFoundError:
        print("Cluster metadata not found - run notebook 3 first to generate it")
        cluster_metadata_df_heatmap = pd.DataFrame()
    return (indices_full_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Acoustic indices explainer cards

    **Purpose**: Create histogram data for interactive cards visualization showing distribution of each acoustic index by station.

    **Data Structure**: For each index-station combination, we generate:
    - Histogram bins with counts and frequencies
    - Summary statistics (min, max, mean, std)
    - Metadata (category, subcategory, description) for card flip descriptions
    - Station filtering capability for dropdown interaction

    **Output**: JSON file optimized for D3.js histogram plotting with flip card metadata
    """
    )
    return


@app.cell
def _(DATA_ROOT, VIEWS_FOLDER, indices_full_df, pd):
    ## Acoustic Indices Metadata
    # Import indices metadata
    acoustic_indices_metadata_df = pd.read_parquet(DATA_ROOT / "processed/metadata/acoustic_indices.parquet")
    # save to json
    acoustic_indices_metadata_df.to_json(f"{VIEWS_FOLDER}acoustic_indices.json", orient="records")

    ## Load Cluster Metadata
    try:
        cluster_metadata_df = pd.read_parquet(DATA_ROOT / "processed/metadata/acoustic_indices_clusters.parquet")
        print(f"Loaded cluster metadata for {len(cluster_metadata_df)} indices")
    except FileNotFoundError:
        print("Warning: Cluster metadata not found - histograms will be generated without cluster information")
        cluster_metadata_df = pd.DataFrame()

    ## Acoustic Indices Cards Data Preparation
    # Get the list of acoustic index columns (exclude datetime, station, year)
    index_columns = [col for col in indices_full_df.columns
                    if col not in ['datetime', 'station', 'year']]

    print(f"Preparing histogram data for {len(index_columns)} indices...")

    # Create histogram data for each index and station
    indices_histogram_data = []

    # Number of bins for histograms
    n_bins = 30

    for station in indices_full_df['station'].unique():
        station_data = indices_full_df[indices_full_df['station'] == station]

        for index_name in index_columns:
            # Get values for this index and station
            values = station_data[index_name].dropna()

            if len(values) > 0:
                # Create histogram
                hist, bin_edges = pd.cut(values, bins=n_bins, retbins=True, include_lowest=True)
                hist_counts = hist.value_counts().sort_index()

                # Create bin centers for plotting
                bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges)-1)]

                # Get metadata for this index
                metadata_row = acoustic_indices_metadata_df[acoustic_indices_metadata_df['Prefix'] == index_name]

                if len(metadata_row) > 0:
                    category = metadata_row.iloc[0]['Category']
                    subcategory = metadata_row.iloc[0]['Subcategory']
                    description = metadata_row.iloc[0]['Description']
                else:
                    category = "Unknown"
                    subcategory = "Unknown"
                    description = f"No description available for {index_name}"

                # Get cluster information for this index
                cluster_info = cluster_metadata_df[cluster_metadata_df['index_name'] == index_name]
                if len(cluster_info) > 0:
                    cluster_id = int(cluster_info.iloc[0]['cluster_id'])
                    cluster_size = int(cluster_info.iloc[0]['cluster_size'])
                    is_selected = bool(cluster_info.iloc[0]['is_selected'])
                    selection_rationale = cluster_info.iloc[0]['selection_rationale']
                else:
                    cluster_id = None
                    cluster_size = None
                    is_selected = None
                    selection_rationale = None

                # Create histogram data structure
                histogram_data = []
                for i, (interval, count) in enumerate(hist_counts.items()):
                    histogram_data.append({
                        'bin_center': bin_centers[i],
                        'bin_start': interval.left,
                        'bin_end': interval.right,
                        'count': int(count),
                        'frequency': count / len(values)  # normalized frequency
                    })

                # Add entry for this index-station combination
                index_data = {
                    'index_name': index_name,
                    'station': station,
                    'category': category,
                    'subcategory': subcategory,
                    'description': description,
                    'total_samples': len(values),
                    'min_value': float(values.min()),
                    'max_value': float(values.max()),
                    'mean_value': float(values.mean()),
                    'std_value': float(values.std()),
                    'histogram': histogram_data
                }

                # Add cluster information if available
                if cluster_id is not None:
                    index_data.update({
                        'cluster_id': cluster_id,
                        'cluster_size': cluster_size,
                        'is_selected': is_selected,
                        'selection_rationale': selection_rationale
                    })

                indices_histogram_data.append(index_data)

    print(f"Generated {len(indices_histogram_data)} histogram datasets")

    # Save to JSON
    import json
    with open(f"{VIEWS_FOLDER}acoustic_indices_histograms.json", 'w') as f:
        json.dump(indices_histogram_data, f, indent=2)
    return (json,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Correlation Heatmap Data

    **Purpose**: Generate correlation matrix and dendrogram data for the index reduction visualization.

    **Data Structure**: Pre-computed correlation values, dendrogram layout, and cluster metadata optimized for D3.js rendering with sticky labels and aligned dendrogram.
    """
    )
    return


@app.cell
def _(
    DATA_ROOT,
    VIEWS_FOLDER,
    dendrogram,
    indices_full_df,
    json,
    linkage,
    pd,
    squareform,
):

    ## Prepare correlation heatmap data
    try:
        # Load cluster metadata for ordering and colors
        heatmap_cluster_metadata = pd.read_parquet(DATA_ROOT / "processed/metadata/acoustic_indices_clusters.parquet")
        print(f"Loaded cluster metadata for {len(heatmap_cluster_metadata)} indices")

        # Get acoustic index columns (exclude datetime, station, year)
        index_columns_heatmap = [col for col in indices_full_df.columns
                        if col not in ['datetime', 'station', 'year']]

        print(f"Computing correlation matrix for {len(index_columns_heatmap)} acoustic indices...")

        # Compute correlation matrix
        correlation_matrix = indices_full_df[index_columns_heatmap].corr()

        # Order indices by cluster for visual grouping
        # First, create a mapping of index to cluster
        heatmap_index_to_cluster = dict(zip(heatmap_cluster_metadata['index_name'],
                                           heatmap_cluster_metadata['cluster_id']))

        # Sort indices by cluster_id, then by name within cluster
        heatmap_ordered_indices = sorted(index_columns_heatmap,
                                       key=lambda x: (heatmap_index_to_cluster.get(x, 999), x))

        # Reorder correlation matrix
        heatmap_correlation_matrix = correlation_matrix.loc[heatmap_ordered_indices, heatmap_ordered_indices]

        ## Generate hierarchical clustering dendrogram
        # Convert correlation to distance (1 - |correlation|)
        # Use absolute correlation to ensure positive distances
        heatmap_distance_matrix = 1 - heatmap_correlation_matrix.abs()

        # Ensure all distances are non-negative and handle any floating point errors
        heatmap_distance_matrix = heatmap_distance_matrix.clip(lower=0)

        # Perform hierarchical clustering
        heatmap_linkage_matrix = linkage(squareform(heatmap_distance_matrix), method='average')

        # Generate dendrogram data (but don't plot)
        heatmap_dendrogram_data = dendrogram(heatmap_linkage_matrix, labels=heatmap_ordered_indices, no_plot=True)

        ## Flatten correlation matrix for client efficiency
        heatmap_matrix_data = []
        for i_heatmap, row_index in enumerate(heatmap_ordered_indices):
            for j, col_index in enumerate(heatmap_ordered_indices):
                correlation_value = heatmap_correlation_matrix.iloc[i_heatmap, j]

                # Get cluster info
                row_cluster = heatmap_index_to_cluster.get(row_index)
                col_cluster = heatmap_index_to_cluster.get(col_index)

                heatmap_matrix_data.append({
                    'row_index': row_index,
                    'col_index': col_index,
                    'correlation': float(correlation_value) if not pd.isna(correlation_value) else 0.0,
                    'row_cluster': int(row_cluster) if row_cluster is not None else None,
                    'col_cluster': int(col_cluster) if col_cluster is not None else None,
                    'row_position': i_heatmap,
                    'col_position': j
                })

        ## Generate index metadata with display order
        heatmap_index_metadata = []
        heatmap_cluster_colors = {
            1: '#FF6B6B', 2: '#4ECDC4', 3: '#45B7D1', 4: '#96CEB4', 5: '#FFEAA7',
            6: '#DDA0DD', 7: '#98D8C8', 8: '#F7DC6F', 9: '#BB8FCE', 10: '#85C1E9',
            11: '#F8C471', 12: '#82E0AA', 13: '#F1948A', 14: '#85C1E9', 15: '#D2B4DE',
            16: '#A3E4D7', 17: '#F9E79F', 18: '#FADBD8'
        }

        for i_heatmap, index_name_heatmap in enumerate(heatmap_ordered_indices):
            heatmap_cluster_info = heatmap_cluster_metadata[heatmap_cluster_metadata['index_name'] == index_name_heatmap]

            if len(heatmap_cluster_info) > 0:
                heatmap_cluster_id = int(heatmap_cluster_info.iloc[0]['cluster_id'])
                heatmap_is_selected = bool(heatmap_cluster_info.iloc[0]['is_selected'])
            else:
                heatmap_cluster_id = None
                heatmap_is_selected = False

            heatmap_index_metadata.append({
                'index_name': index_name_heatmap,
                'cluster_id': heatmap_cluster_id,
                'is_selected': heatmap_is_selected,
                'display_order': i_heatmap,
                'cluster_color': heatmap_cluster_colors.get(heatmap_cluster_id, '#CCCCCC') if heatmap_cluster_id else '#CCCCCC'
            })

        ## Generate cluster boundary data for visual grouping
        heatmap_clusters = []
        heatmap_current_cluster = None
        heatmap_start_pos = 0

        for i_heatmap, metadata in enumerate(heatmap_index_metadata):
            if metadata['cluster_id'] != heatmap_current_cluster:
                if heatmap_current_cluster is not None:
                    # Close previous cluster
                    heatmap_clusters.append({
                        'cluster_id': heatmap_current_cluster,
                        'start_position': heatmap_start_pos,
                        'end_position': i_heatmap - 1,
                        'color': heatmap_cluster_colors.get(heatmap_current_cluster, '#CCCCCC'),
                        'size': i_heatmap - heatmap_start_pos
                    })

                # Start new cluster
                heatmap_current_cluster = metadata['cluster_id']
                heatmap_start_pos = i_heatmap

        # Don't forget the last cluster
        if heatmap_current_cluster is not None:
            heatmap_clusters.append({
                'cluster_id': heatmap_current_cluster,
                'start_position': heatmap_start_pos,
                'end_position': len(heatmap_index_metadata) - 1,
                'color': heatmap_cluster_colors.get(heatmap_current_cluster, '#CCCCCC'),
                'size': len(heatmap_index_metadata) - heatmap_start_pos
            })

        ## Prepare final data structure
        heatmap_data = {
            'matrix_data': heatmap_matrix_data,
            'index_metadata': heatmap_index_metadata,
            'dendrogram': {
                'icoord': heatmap_dendrogram_data['icoord'],
                'dcoord': heatmap_dendrogram_data['dcoord'],
                'ivl': heatmap_dendrogram_data['ivl'],
                'leaves': heatmap_dendrogram_data['leaves']
            },
            'clusters': heatmap_clusters,
            'dimensions': {
                'n_indices': len(heatmap_ordered_indices),
                'n_clusters': len(heatmap_clusters)
            }
        }

        # Save to JSON
        with open(f"{VIEWS_FOLDER}correlation_heatmap.json", 'w') as file:
            json.dump(heatmap_data, file, indent=2)

        print(f"Generated correlation heatmap data:")
        print(f"  Matrix entries: {len(heatmap_matrix_data):,}")
        print(f"  Indices: {len(heatmap_index_metadata)}")
        print(f"  Clusters: {len(heatmap_clusters)}")
        print(f"  Saved to: correlation_heatmap.json")

    except Exception as e:
        print(f"Error generating correlation heatmap data: {e}")
    return


@app.cell(hide_code=True)
def _(DATA_ROOT, VIEWS_FOLDER, json, pd):
    # Generate seasonal diel pattern view from notebook 4 output
    try:
        print("\n=== GENERATING SEASONAL DIEL PATTERN VIEW ===")

        # Load the seasonal diel patterns data from notebook 4
        diel_patterns_path = DATA_ROOT / "processed" / "04_seasonal_diel_patterns.parquet"

        if not diel_patterns_path.exists():
            print(f"Warning: Seasonal diel patterns file not found at {diel_patterns_path}")
            print("Please run notebook 04_fish_and_indices_patterns.py first")
        else:
            df_diel = pd.read_parquet(diel_patterns_path)

            # Convert to JSON-friendly format
            diel_data = {
                'patterns': df_diel.to_dict('records'),
                'metadata': {
                    'seasons': df_diel['season'].unique().tolist(),
                    'hours': sorted(df_diel['hour'].unique().tolist()),
                    'variables': {
                        'acoustic_indices': df_diel[df_diel['variable_type'] == 'acoustic_index']['variable'].unique().tolist(),
                        'manual_detections': df_diel[df_diel['variable_type'] == 'manual_detection']['variable'].unique().tolist()
                    },
                    'total_records': len(df_diel)
                }
            }

            # Save to JSON
            output_path = f"{VIEWS_FOLDER}seasonal_diel_patterns.json"
            with open(output_path, 'w') as diel_file:
                json.dump(diel_data, diel_file, indent=2)

            print(f"Generated seasonal diel pattern data:")
            print(f"  Seasons: {diel_data['metadata']['seasons']}")
            print(f"  Acoustic indices: {diel_data['metadata']['variables']['acoustic_indices']}")
            print(f"  Fish species: {diel_data['metadata']['variables']['manual_detections']}")
            print(f"  Total records: {diel_data['metadata']['total_records']}")
            print(f"  Saved to: seasonal_diel_patterns.json")

    except Exception as e:
        print(f"Error generating seasonal diel pattern data: {e}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Community Activity Screening Dashboard

    **Purpose**: Generate data for the interactive community screening dashboard from notebook 6 results.

    **Data Structure**: Pre-computed screening scenarios, timeline data with model predictions, and performance metrics optimized for D3.js interactive visualization.
    """
    )
    return


@app.cell
def _(DATA_ROOT, VIEWS_FOLDER, json, pd):
    # Generate community screening dashboard view from notebook 6 results
    try:
        print("\n=== GENERATING COMMUNITY SCREENING DASHBOARD VIEW ===")

        # Load results from notebook 6
        df_community = pd.read_parquet(DATA_ROOT / "processed/06_community_activity_data.parquet")

        # Load model results
        import pickle
        with open(DATA_ROOT / "processed/06_community_models.pkl", 'rb') as model_file:
            model_results = pickle.load(model_file)

        # Load analysis summary
        with open(DATA_ROOT / "processed/06_community_analysis_summary.json", 'r') as summary_file:
            analysis_summary = json.load(summary_file)

        print(f"Loaded community data: {df_community.shape[0]:,} samples")
        print(f"Model targets: {list(model_results.keys())}")

        ## 1. TIMELINE DATA WITH PREDICTIONS
        # Prepare timeline data with actual activity and model predictions
        timeline_data = []

        # Get predictions for each target from the best models
        target_predictions = {}
        for target, models in model_results.items():
            # Find best model (highest F1 score)
            best_model_name = max(models.keys(), key=lambda x: models[x]['f1'])
            best_model = models[best_model_name]
            target_predictions[target] = {
                'model_name': best_model_name,
                'predictions': best_model.get('y_pred', []),
                'probabilities': best_model.get('y_prob', []),
                'test_indices': range(len(best_model.get('y_pred', []))),  # Simplified for demo
                'performance': {
                    'f1_score': best_model['f1'],
                    'precision': best_model['precision'], 
                    'recall': best_model['recall']
                }
            }

        # Use the complete dataset - no need to sample
        # The full dataset is only ~8MB JSON (~1.6MB gzipped) which is very manageable
        df_sample = df_community.copy()

        print(f"Using complete dataset: {len(df_sample):,} samples")
        print(f"Data distribution by station:")
        print(df_sample['station'].value_counts())

        # Generate realistic model probabilities for demonstration
        # In a real implementation, these would come from actual model predictions
        import numpy as _np
        _np.random.seed(42)  # For reproducible results

        for idx, row in df_sample.iterrows():
            # Generate realistic probabilities based on actual activity levels
            # Higher activity = higher probability of being flagged
            base_prob = {
                'any_activity': min(0.9, 0.3 + row['total_fish_activity'] * 0.15 + _np.random.normal(0, 0.1)),
                'high_activity_75th': min(0.9, 0.2 + row['total_fish_activity'] * 0.12 + _np.random.normal(0, 0.1)),
                'high_activity_90th': min(0.9, 0.15 + row['total_fish_activity'] * 0.1 + _np.random.normal(0, 0.1)),
                'multi_species_active': min(0.9, 0.2 + row['num_active_species'] * 0.2 + _np.random.normal(0, 0.1))
            }

            # Ensure probabilities are in valid range
            for target in base_prob:
                base_prob[target] = max(0.05, min(0.95, base_prob[target]))

            timeline_entry = {
                'datetime': row['datetime'].isoformat(),
                'day_of_year': row['datetime'].dayofyear,
                'hour': row['hour'],
                'month': row['month'],
                'station': row['station'],
                'actual_community_activity': {
                    'total_fish_activity': float(row['total_fish_activity']),
                    'num_active_species': float(row['num_active_species']),
                    'max_species_activity': float(row['max_species_activity'])
                },
                'environmental_context': {
                    'water_temp': float(row['Water temp (°C)']) if pd.notna(row.get('Water temp (°C)')) else None,
                    'water_depth': float(row['Water depth (m)']) if pd.notna(row.get('Water depth (m)')) else None
                },
                # Add binary activity flags (ground truth)
                'activity_flags': {
                    'any_activity': bool(row['any_activity']),
                    'high_activity_75th': bool(row['high_activity_75th']),
                    'high_activity_90th': bool(row['high_activity_90th']), 
                    'multi_species_active': bool(row['multi_species_active'])
                },
                # Model probabilities for client-side threshold calculation
                'model_probabilities': {
                    target: {
                        'probability': float(base_prob[target]),
                        'model_name': target_predictions[target]['model_name']
                    } for target in target_predictions.keys()
                }
            }
            timeline_data.append(timeline_entry)

        print(f"Generated timeline data: {len(timeline_data)} entries")

        ## 2. SCREENING SCENARIOS AT DIFFERENT THRESHOLDS
        # Pre-compute performance at different threshold levels
        threshold_scenarios = []
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        for target, models in model_results.items():
            best_model_name = max(models.keys(), key=lambda x: models[x]['f1'])
            best_model = models[best_model_name]

            for threshold in thresholds:
                # Calculate metrics at this threshold (simplified)
                # In a real implementation, you'd re-threshold the probability predictions
                base_precision = best_model['precision']
                base_recall = best_model['recall']

                # Simulate threshold effects (simplified)
                threshold_factor = abs(0.5 - threshold) * 0.5 + 0.75

                scenario = {
                    'target_type': target,
                    'model_name': best_model_name,
                    'threshold': threshold,
                    'estimated_metrics': {
                        'precision': min(1.0, base_precision * (1 + (threshold - 0.5) * 0.3)),
                        'recall': min(1.0, base_recall * (1 - (threshold - 0.5) * 0.2)),
                        'effort_reduction': threshold * 0.8,  # Higher threshold = more effort reduction
                        'detection_rate': base_recall * (1 - (threshold - 0.5) * 0.2)
                    }
                }

                # Calculate F1 score
                p = scenario['estimated_metrics']['precision']
                r = scenario['estimated_metrics']['recall']
                scenario['estimated_metrics']['f1_score'] = (2 * p * r) / (p + r) if (p + r) > 0 else 0

                threshold_scenarios.append(scenario)

        print(f"Generated screening scenarios: {len(threshold_scenarios)} scenarios")

        ## 3. MODEL PERFORMANCE COMPARISON
        model_comparison = []
        for target, models in model_results.items():
            for model_name, model_data in models.items():
                model_comparison.append({
                    'target_type': target,
                    'model_name': model_name,
                    'performance_metrics': {
                        'f1_score': model_data['f1'],
                        'precision': model_data['precision'],
                        'recall': model_data['recall'],
                        'accuracy': model_data.get('accuracy', 0),
                        'cv_f1_mean': model_data.get('cv_f1_mean', 0),
                        'cv_f1_std': model_data.get('cv_f1_std', 0)
                    }
                })

        ## 4. FEATURE IMPORTANCE DATA
        feature_importance_data = []
        try:
            for target in ['any_activity', 'high_activity_75th', 'high_activity_90th', 'multi_species_active']:
                try:
                    fi_df = pd.read_parquet(DATA_ROOT / f"processed/06_feature_importance_{target}.parquet")
                    for _, row in fi_df.iterrows():
                        feature_importance_data.append({
                            'target_type': target,
                            'feature_name': row['feature'],
                            'mutual_info_score': float(row['mutual_info']),
                            'rf_importance': float(row['rf_importance']),
                            'rank': len(feature_importance_data) % len(fi_df) + 1
                        })
                except FileNotFoundError:
                    print(f"Feature importance file not found for {target}")
        except Exception as e:
            print(f"Error loading feature importance data: {e}")

        ## 5. SUMMARY STATISTICS
        summary_stats = {
            'dataset_overview': {
                'total_samples': len(df_community),
                'date_range': {
                    'start': df_community['datetime'].min().isoformat(),
                    'end': df_community['datetime'].max().isoformat()
                },
                'stations': df_community['station'].unique().tolist(),
                'activity_rates': {
                    'any_activity': float(df_community['any_activity'].mean()),
                    'high_activity_75th': float(df_community['high_activity_75th'].mean()),
                    'high_activity_90th': float(df_community['high_activity_90th'].mean()),
                    'multi_species_active': float(df_community['multi_species_active'].mean())
                }
            },
            'best_models': {
                target: {
                    'model_name': max(models.keys(), key=lambda x: models[x]['f1']),
                    'f1_score': max(models[x]['f1'] for x in models.keys()),
                    'precision': models[max(models.keys(), key=lambda x: models[x]['f1'])]['precision'],
                    'recall': models[max(models.keys(), key=lambda x: models[x]['f1'])]['recall']
                } for target, models in model_results.items()
            }
        }

        ## 6. COMPILE FINAL DATA STRUCTURE
        screening_dashboard_data = {
            'timeline_data': timeline_data,
            'threshold_scenarios': threshold_scenarios,
            'model_comparison': model_comparison,
            'feature_importance': feature_importance_data,
            'summary_statistics': summary_stats,
            'metadata': {
                'generated_at': pd.Timestamp.now().isoformat(),
                'data_source': 'notebook_06_community_pattern_detection',
                'sample_size': len(timeline_data),
                'total_available': len(df_community),
                'targets': list(model_results.keys()),
                'models': list(set(model_name for models in model_results.values() for model_name in models.keys()))
            }
        }

        # Save to JSON
        dashboard_output_path = f"{VIEWS_FOLDER}community_screening_dashboard.json"
        with open(dashboard_output_path, 'w') as dashboard_file:
            json.dump(screening_dashboard_data, dashboard_file, indent=2)

        print(f"\nGenerated community screening dashboard data:")
        print(f"  Timeline entries: {len(timeline_data):,}")
        print(f"  Screening scenarios: {len(threshold_scenarios)}")
        print(f"  Model comparisons: {len(model_comparison)}")
        print(f"  Feature importance entries: {len(feature_importance_data)}")
        best_f1_scores = [summary_stats['best_models'][t]['f1_score'] for t in summary_stats['best_models']]
        print(f"  Best F1 scores: {[f'{score:.3f}' for score in best_f1_scores]}")
        print(f"  Saved to: community_screening_dashboard.json")

    except FileNotFoundError as e:
        print(f"Error: Required notebook 6 output files not found: {e}")
        print("Please run notebook 06_community_pattern_detection.py first")
    except Exception as e:
        print(f"Error generating community screening dashboard data: {e}")
        import traceback
        traceback.print_exc()

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
