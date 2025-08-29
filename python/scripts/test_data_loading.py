#!/usr/bin/env python3
"""Test script to validate data loading functionality."""

from mbon_analysis.data.loaders import create_loader


def main():
    """Test basic data loading functionality."""
    print("🧪 Testing MBON Data Loading")
    print("=" * 40)
    
    # Create loader
    loader = create_loader()
    
    # Test 1: Load deployment metadata
    try:
        metadata = loader.load_deployment_metadata()
        print(f"✅ Deployment metadata: {metadata.shape[0]} rows, {metadata.shape[1]} columns")
        print(f"   Columns: {list(metadata.columns[:5])}..." if len(metadata.columns) > 5 else f"   Columns: {list(metadata.columns)}")
    except Exception as e:
        print(f"❌ Deployment metadata failed: {e}")
    
    # Test 2: Load species mapping
    try:
        species = loader.load_species_mapping()
        print(f"✅ Species mapping: {species.shape[0]} rows, {species.shape[1]} columns")
        print(f"   Columns: {list(species.columns)}")
    except Exception as e:
        print(f"❌ Species mapping failed: {e}")
    
    # Test 3: Load indices reference
    try:
        indices_ref = loader.load_indices_reference()
        print(f"✅ Indices reference: {indices_ref.shape[0]} rows, {indices_ref.shape[1]} columns")
        print(f"   Columns: {list(indices_ref.columns)}")
    except Exception as e:
        print(f"❌ Indices reference failed: {e}")
    
    # Test 4: Check available stations and years
    try:
        stations = loader.get_available_stations()
        years = loader.get_available_years()
        print(f"✅ Available stations: {stations}")
        print(f"✅ Available years: {years}")
    except Exception as e:
        print(f"❌ Station/year discovery failed: {e}")
    
    # Test 5: Load sample detection data
    if stations and years:
        try:
            sample_station = stations[0]
            sample_year = years[0]
            detections = loader.load_detection_data(sample_station, sample_year)
            print(f"✅ Detection data ({sample_station}, {sample_year}): {detections.shape[0]} rows, {detections.shape[1]} columns")
        except Exception as e:
            print(f"❌ Detection data failed: {e}")
    
    # Test 6: Load sample acoustic indices
    if stations:
        try:
            sample_station = stations[0]
            indices = loader.load_acoustic_indices(sample_station)
            print(f"✅ Acoustic indices ({sample_station}): {indices.shape[0]} rows, {indices.shape[1]} columns")
        except Exception as e:
            print(f"❌ Acoustic indices failed: {e}")
    
    print("\n🎉 Data loading test complete!")


if __name__ == "__main__":
    main()