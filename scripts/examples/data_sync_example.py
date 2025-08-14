#!/usr/bin/env python3
"""
Examples showing different data loading strategies with the mbon_analysis package.

This demonstrates:
1. Basic loading (assumes data exists locally)
2. Sync checking (see what needs updating)
3. Auto-sync loading (ensures fresh data before loading)
4. Smart loading (flexible dataset selection)
"""

# No need for sys.path manipulation since package is installed in editable mode

from mbon_analysis.core import (
    # Basic loading
    load_processed_data,
    
    # Sync functions
    check_data_freshness,
    ensure_data_available,
    
    # Auto-loading  
    load_with_auto_sync,
    smart_load
)


def example_basic_loading():
    """Example 1: Basic loading (no sync checking)."""
    print("\n" + "=" * 50)
    print("Example 1: Basic Loading")
    print("=" * 50)
    print("This assumes data already exists locally.\n")
    
    try:
        detections, environmental, species, stations = load_processed_data()
        print(f"✅ Loaded {len(detections)} detections from local files")
    except FileNotFoundError as e:
        print(f"❌ Data not found locally: {e}")
        print("   Run sync first or use auto-sync loading")


def example_check_freshness():
    """Example 2: Check if data needs updating."""
    print("\n" + "=" * 50)
    print("Example 2: Check Data Freshness")
    print("=" * 50)
    print("Check what needs to be downloaded/updated.\n")
    
    # Check all data
    print("Checking all data types:")
    status = check_data_freshness("all")
    
    # Check specific type
    print("\nChecking just acoustic indices:")
    indices_status = check_data_freshness("indices")


def example_auto_sync_loading():
    """Example 3: Auto-sync loading."""
    print("\n" + "=" * 50)
    print("Example 3: Auto-Sync Loading")
    print("=" * 50)
    print("Automatically checks for updates and syncs before loading.\n")
    
    # This will sync if needed, then load
    detections, environmental, species, stations = load_with_auto_sync()
    
    print(f"\n✅ Data loaded and ready for analysis:")
    print(f"   - Detections: {detections.shape}")
    print(f"   - Environmental: {environmental.shape}")
    print(f"   - Species metadata: {len(species)} entries")
    print(f"   - Stations: {len(stations)} entries")


def example_smart_loading():
    """Example 4: Smart loading with specific datasets."""
    print("\n" + "=" * 50)
    print("Example 4: Smart Loading")
    print("=" * 50)
    print("Load only the datasets you need.\n")
    
    # Load specific datasets with auto-sync
    print("Loading detections and acoustic indices:")
    data = smart_load(["detections", "acoustic_indices"])
    
    if "detections" in data:
        print(f"   - Detections: {data['detections'].shape}")
    if "acoustic_indices" in data:
        print(f"   - Acoustic indices: {data['acoustic_indices'].shape}")
    
    # Load without auto-sync
    print("\nLoading stations without sync check:")
    data = smart_load(["stations"], auto_sync=False)
    print(f"   - Stations: {len(data['stations'])} entries")


def example_ensure_then_load():
    """Example 5: Ensure data available then load."""
    print("\n" + "=" * 50)
    print("Example 5: Ensure Available Then Load")
    print("=" * 50)
    print("Two-step process: ensure data exists, then load.\n")
    
    # Step 1: Ensure acoustic indices are available
    print("Step 1: Ensuring acoustic indices are available...")
    ensure_data_available("indices")
    
    # Step 2: Load the data
    print("\nStep 2: Loading acoustic indices...")
    from mbon_analysis.core import load_acoustic_indices
    indices = load_acoustic_indices()
    
    print(f"\n✅ Acoustic indices loaded: {indices.shape}")


def main():
    """Run all examples."""
    print("MBON Data Loading Examples")
    print("=" * 50)
    print("\nThis demonstrates different strategies for loading data:")
    print("- Basic: Just load from local files")
    print("- Check: See what needs updating")
    print("- Auto-sync: Ensure fresh data before loading")
    print("- Smart: Load specific datasets flexibly")
    
    # Run examples
    example_basic_loading()
    example_check_freshness()
    # example_auto_sync_loading()  # Commented out to avoid actual downloads
    example_smart_loading()
    # example_ensure_then_load()   # Commented out to avoid actual downloads
    
    print("\n" + "=" * 50)
    print("Examples Complete!")
    print("=" * 50)
    print("\nFor production use, we recommend:")
    print("1. load_with_auto_sync() - For analysis scripts that need fresh data")
    print("2. smart_load() - For flexible loading of specific datasets")
    print("3. load_processed_data() - For quick local loading without sync")


if __name__ == "__main__":
    main()