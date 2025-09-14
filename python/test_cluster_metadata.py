#!/usr/bin/env python3
"""
Test script to verify cluster metadata generation
Run this after notebook 3 to check if files are created correctly
"""

import pandas as pd
from pathlib import Path

def test_files():
    data_dir = Path("../data/processed")
    views_dir = Path("../data/views")

    print("Testing cluster metadata generation...")
    print("=" * 50)

    # Check if full dataset exists
    full_path = data_dir / "02_acoustic_indices_aligned_2021_full.parquet"
    if full_path.exists():
        df_full = pd.read_parquet(full_path)
        print(f"✓ Full dataset found: {full_path}")
        print(f"  Shape: {df_full.shape}")

        # Count indices
        index_cols = [col for col in df_full.columns if col not in ['datetime', 'station', 'year']]
        print(f"  Total indices: {len(index_cols)}")
    else:
        print(f"✗ Full dataset NOT found: {full_path}")
        print("  Run notebook 3 first!")

    # Check if cluster metadata exists
    metadata_path = data_dir / "metadata" / "acoustic_indices_clusters.parquet"
    if metadata_path.exists():
        df_meta = pd.read_parquet(metadata_path)
        print(f"\n✓ Cluster metadata found: {metadata_path}")
        print(f"  Total indices: {len(df_meta)}")
        print(f"  Clusters: {df_meta['cluster_id'].nunique()}")
        print(f"  Selected indices: {df_meta['is_selected'].sum()}")

        # Show sample
        print("\n  Sample metadata:")
        sample = df_meta[df_meta['is_selected']].head(3)
        for _, row in sample.iterrows():
            print(f"    - {row['index_name']} (Cluster {row['cluster_id']})")
    else:
        print(f"\n✗ Cluster metadata NOT found: {metadata_path}")
        print("  Run notebook 3 first!")

    # Check if JSON views exist
    print("\n" + "=" * 50)
    print("Checking JSON views (run notebook 10 to generate)...")

    json_files = [
        "acoustic_indices_full.json",
        "acoustic_indices_clusters.json"
    ]

    for json_file in json_files:
        json_path = views_dir / json_file
        if json_path.exists():
            size_mb = json_path.stat().st_size / (1024 * 1024)
            print(f"✓ {json_file}: {size_mb:.2f} MB")
        else:
            print(f"✗ {json_file}: NOT FOUND")

    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. Run notebook 3 to generate cluster metadata")
    print("2. Run notebook 10 to create JSON views")
    print("3. Upload JSON files to CDN")
    print("4. Test the heatmap in the dashboard")

if __name__ == "__main__":
    test_files()