#!/usr/bin/env python3
"""
Generate acoustic indices histogram data for cards visualization
Run this to create the histogram data file needed for the frontend
"""

import pandas as pd
import json
import numpy as np

def generate_histogram_data():
    VIEWS_FOLDER = "../data/views/"

    # Load the data
    print("Loading data...")
    indices_aligned_reduced_df = pd.read_parquet("../data/processed/03_reduced_acoustic_indices.parquet")
    acoustic_indices_metadata_df = pd.read_parquet("../data/processed/metadata/acoustic_indices.parquet")

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
    output_file = f"{VIEWS_FOLDER}acoustic_indices_histograms.json"
    with open(output_file, 'w') as f:
        json.dump(indices_histogram_data, f, indent=2)

    print(f"Saved to: {output_file}")

    # Show sample of first entry
    if indices_histogram_data:
        sample = indices_histogram_data[0]
        print(f"\nSample entry structure:")
        print(f"Index: {sample['index_name']}")
        print(f"Station: {sample['station']}")
        print(f"Category: {sample['category']}")
        print(f"Total samples: {sample['total_samples']}")
        print(f"Histogram bins: {len(sample['histogram'])}")
        print(f"First bin: {sample['histogram'][0]}")

if __name__ == "__main__":
    generate_histogram_data()