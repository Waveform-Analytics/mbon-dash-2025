#!/usr/bin/env python3
"""
Example showing how to use the mbon_analysis data loading functions.

This demonstrates the various ways to load data from the processed JSON files
using the mbon_analysis package.
"""

# No need for sys.path manipulation since package is installed in editable mode

from mbon_analysis.core import (
    load_processed_data,
    load_acoustic_indices, 
    load_metadata
)

def main():
    """Demonstrate data loading functions."""
    
    print("MBON Data Loading Examples")
    print("=" * 50)
    
    # Example 1: Load core datasets
    print("\n1. Loading core datasets:")
    detections, environmental, species_meta, stations = load_processed_data()
    
    print(f"   Detection data shape: {detections.shape}")
    print(f"   Environmental data shape: {environmental.shape}")
    print(f"   Species metadata: {len(species_meta)} entries")
    print(f"   Station metadata: {len(stations)} entries")
    
    # Example 2: Load with acoustic indices
    print("\n2. Loading with acoustic indices:")
    *core_data, acoustic_indices = load_processed_data(include_acoustic_indices=True)
    print(f"   Acoustic indices shape: {acoustic_indices.shape}")
    
    # Example 3: Load acoustic indices separately
    print("\n3. Loading acoustic indices separately:")
    indices = load_acoustic_indices()
    print(f"   Acoustic indices shape: {indices.shape}")
    
    # Example 4: Load metadata
    print("\n4. Loading processing metadata:")
    metadata = load_metadata()
    
    if 'data_summary' in metadata:
        summary = metadata['data_summary']
        print(f"   Processing date: {metadata.get('generated_at', 'unknown')}")
        print(f"   Total detections: {summary.get('total_detections', 0):,}")
        print(f"   Total environmental: {summary.get('total_environmental_records', 0):,}")
        print(f"   Total acoustic indices: {summary.get('total_acoustic_indices_records', 0):,}")
    
    # Example 5: Working with the data
    print("\n5. Quick data exploration:")
    print(f"   Detection date range: {detections['date'].min()} to {detections['date'].max()}")
    print(f"   Stations available: {sorted(detections['station'].unique())}")
    print(f"   Years available: {sorted(detections['year'].unique())}")
    
    if not acoustic_indices.empty:
        print(f"   Acoustic indices stations: {sorted(acoustic_indices['station'].unique())}")
        print(f"   Acoustic indices years: {sorted(acoustic_indices['year'].unique())}")
        print(f"   Bandwidths: {sorted(acoustic_indices['bandwidth'].unique())}")
    
    print("\n✅ All examples completed successfully!")

if __name__ == "__main__":
    main()