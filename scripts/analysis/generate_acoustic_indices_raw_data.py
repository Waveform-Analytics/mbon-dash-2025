#!/usr/bin/env python3
"""
Generate raw acoustic indices data for dashboard visualizations.

This script uses the mbon_analysis package to load acoustic indices CSV files
and export them in a format suitable for the temporal heatmap and box plot
visualizations.
"""

import json
from pathlib import Path
from datetime import datetime

# Import from our package
from mbon_analysis.core import (
    load_all_acoustic_indices,
    export_for_dashboard
)


def main():
    """Generate and export acoustic indices raw data."""
    
    print("🎵 Generating Acoustic Indices Raw Data for Dashboard")
    print("=" * 60)
    
    # Load all acoustic indices datasets
    print("\n📊 Loading acoustic indices CSV files...")
    datasets = load_all_acoustic_indices()
    
    if not datasets:
        print("❌ No datasets loaded. Check that CSV files exist.")
        return
    
    print(f"\n✅ Loaded {len(datasets)} datasets:")
    for key, df in datasets.items():
        print(f"   • {key}: {len(df)} records, {len(df.columns)} columns")
    
    # Export for dashboard
    print("\n💾 Exporting data for dashboard components...")
    output_files = export_for_dashboard(datasets)
    
    # Also save a more detailed version with all the raw data
    print("\n📝 Creating detailed export with all raw values...")
    
    # Get output directory
    package_dir = Path(__file__).resolve().parent.parent.parent
    output_dir = package_dir / "data" / "cdn" / "processed"
    
    # Combine all data with proper metadata
    all_records = []
    for key, df in datasets.items():
        parts = key.split('_')
        station = parts[0]
        bandwidth = '_'.join(parts[1:]) if len(parts) > 1 else 'Unknown'
        
        # Convert each row to a record with metadata
        for _, row in df.iterrows():
            record = row.to_dict()
            record['station'] = station
            record['bandwidth'] = bandwidth
            record['dataset_key'] = key
            all_records.append(record)
    
    # Save detailed version
    detailed_output = {
        'acoustic_indices': all_records,
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_records': len(all_records),
            'datasets': list(datasets.keys()),
            'stations': sorted(list(set(r['station'] for r in all_records))),
            'bandwidths': sorted(list(set(r['bandwidth'] for r in all_records))),
            'description': 'Raw acoustic indices data for temporal heatmap and box plot visualizations'
        }
    }
    
    detailed_file = output_dir / "acoustic_indices_detailed.json"
    with open(detailed_file, 'w') as f:
        json.dump(detailed_output, f, indent=2, default=str)
    
    print(f"   • Saved detailed data to: {detailed_file}")
    print(f"   • Total records: {len(all_records)}")
    
    print("\n✅ Data generation complete!")
    print("\n🚀 Next steps:")
    print("   1. Upload files to CDN")
    print("   2. Update React components to use new data structure")
    print("   3. Test visualizations with raw data")


if __name__ == "__main__":
    main()