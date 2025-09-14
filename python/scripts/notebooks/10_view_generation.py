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

    VIEWS_FOLDER = "../data/views/"
    return VIEWS_FOLDER, pd


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
def _(VIEWS_FOLDER, pd):
    # Import the parquet file as a dataframe using Pandas
    station_metadata_df = pd.read_parquet("../data/processed/metadata/deployments.parquet")

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
def _(VIEWS_FOLDER, pd):
    ## Manual detections
    # Import manual detections data
    detections_aligned_df = pd.read_parquet("../data/processed/02_detections_aligned_2021.parquet")
    # save to json
    detections_aligned_df.to_json(f"{VIEWS_FOLDER}02_detections_aligned_2021.json", orient="records")


    ## Acoustic indices
    # Import acoustic index data
    indices_aligned_reduced_df = pd.read_parquet("../data/processed/03_reduced_acoustic_indices.parquet")
    # Save to JSON
    indices_aligned_reduced_df.to_json(f"{VIEWS_FOLDER}03_reduced_acoustic_indices.json", orient="records")


    ## RMS SPL + environmental data
    # Import env data
    environment_aligned_df = pd.read_parquet("../data/processed/02_environmental_aligned_2021.parquet")
    # save to json
    environment_aligned_df.to_json(f"{VIEWS_FOLDER}02_environmental_aligned_2021.json", orient="records")
    return


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
def _(VIEWS_FOLDER, pd):
    ## Acoustic Indices Metadata
    # Import indices metadata
    acoustic_indices_metadata_df = pd.read_parquet("../data/processed/metadata/acoustic_indices.parquet")
    # save to json
    acoustic_indices_metadata_df.to_json(f"{VIEWS_FOLDER}acoustic_indices.json", orient="records")

    ## Acoustic Indices Cards Data Preparation
    # Get the list of acoustic index columns (exclude datetime, station, year)
    index_columns = [col for col in indices_aligned_reduced_df.columns
                    if col not in ['datetime', 'station', 'year']]

    print(f"Preparing histogram data for {len(index_columns)} indices...")

    # Create histogram data for each index and station
    indices_histogram_data = []

    # Number of bins for histograms
    n_bins = 30

    for station in indices_aligned_reduced_df['station'].unique():
        station_data = indices_aligned_reduced_df[indices_aligned_reduced_df['station'] == station]

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
                indices_histogram_data.append({
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
                })

    print(f"Generated {len(indices_histogram_data)} histogram datasets")

    # Save to JSON
    import json
    with open(f"{VIEWS_FOLDER}acoustic_indices_histograms.json", 'w') as f:
        json.dump(indices_histogram_data, f, indent=2)

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
