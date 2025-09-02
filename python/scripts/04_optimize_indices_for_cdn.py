#!/usr/bin/env python3
"""
Optimize compiled indices data for faster CDN loading.

Creates pre-filtered files for each station/year/bandwidth combination
and removes unnecessary array fields to reduce file sizes.

Usage:
    uv run scripts/04_optimize_indices_for_cdn.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List


def clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove unnecessary array fields and large text data from a single record.
    Keep only the summary values that are actually used in visualizations.
    """
    # Fields to remove (large arrays that aren't used)
    fields_to_remove = [
        'ACI_by_band',  # Large array - we only use the ACI summary value
        # Add other array fields here if you find them and don't use them
    ]
    
    # Create a clean copy
    clean = record.copy()
    
    # Remove unwanted fields
    for field in fields_to_remove:
        if field in clean:
            del clean[field]
    
    return clean


def split_compiled_data(input_path: Path, output_dir: Path) -> None:
    """
    Split the large compiled_indices.json into smaller files per station/year/bandwidth.
    """
    print(f"Loading compiled data from: {input_path}")
    
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each station/year/bandwidth combination
    stations = data.get('stations', {})
    total_combinations = 0
    total_records_processed = 0
    
    for station, station_data in stations.items():
        for year, year_data in station_data.items():
            for bandwidth, bandwidth_data in year_data.items():
                total_combinations += 1
                
                # Extract the actual data array
                raw_data = bandwidth_data.get('data', []) if isinstance(bandwidth_data, dict) else bandwidth_data
                
                if not raw_data:
                    print(f"⚠️  No data found for {station}/{year}/{bandwidth}")
                    continue
                
                # Clean each record (remove array fields)
                cleaned_data = [clean_record(record) for record in raw_data]
                total_records_processed += len(cleaned_data)
                
                # Create optimized file structure
                optimized_data = {
                    'metadata': {
                        'station': station,
                        'year': int(year),
                        'bandwidth': bandwidth,
                        'generated_at': data.get('metadata', {}).get('generated_at'),
                        'total_records': len(cleaned_data),
                        'optimization_version': '1.0.0',
                        'description': f'Optimized acoustic indices data for {station}/{year}/{bandwidth}'
                    },
                    'data': cleaned_data
                }
                
                # Generate filename
                filename = f"indices_{station}_{year}_{bandwidth}.json"
                output_path = output_dir / filename
                
                # Write optimized file
                with open(output_path, 'w') as f:
                    json.dump(optimized_data, f, separators=(',', ':'))  # Compact JSON
                
                file_size_kb = output_path.stat().st_size / 1024
                print(f"✅ Created: {filename} ({file_size_kb:.1f}KB, {len(cleaned_data)} records)")
    
    print(f"\n📊 Optimization Summary:")
    print(f"   ✅ {total_combinations} optimized files created")
    print(f"   ✅ {total_records_processed:,} total records processed")
    print(f"   📁 Output directory: {output_dir}")
    
    # Calculate size savings
    original_size_mb = input_path.stat().st_size / (1024 * 1024)
    total_new_size_kb = sum(f.stat().st_size for f in output_dir.glob("indices_*.json")) / 1024
    savings_percent = (1 - (total_new_size_kb / 1024) / original_size_mb) * 100
    
    print(f"   📉 Size: {original_size_mb:.1f}MB → {total_new_size_kb:.1f}KB ({savings_percent:.1f}% reduction)")


def main():
    """Main execution function."""
    # Set up paths
    project_root = Path(__file__).parent.parent.parent
    input_file = project_root / "data" / "processed" / "compiled_indices.json"
    output_dir = project_root / "data" / "processed" / "optimized"
    
    # Verify input file exists
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        print("   Make sure you've run the data processing pipeline first.")
        sys.exit(1)
    
    print("🚀 Starting acoustic indices optimization...")
    print(f"   📥 Input: {input_file}")
    print(f"   📤 Output: {output_dir}")
    
    try:
        split_compiled_data(input_file, output_dir)
        print("\n✅ Optimization completed successfully!")
        print("\n🔄 Next steps:")
        print("   1. Upload optimized files to CDN: uv run scripts/03_upload_cdn.py")
        print("   2. Update your API route to use the new files")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()