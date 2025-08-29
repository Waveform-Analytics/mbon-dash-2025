#!/usr/bin/env python3
"""
Generate chart view data files.

This script creates optimized data files for chart components,
reducing file sizes and improving dashboard performance.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.views.chart_views import generate_raw_data_landscape, generate_index_distributions


def main():
    """Generate all chart view files."""
    
    processed_data_dir = Path('data/cdn/processed')
    views_dir = Path('data/cdn/views')
    
    # Ensure output directory exists
    views_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate Raw Data Landscape view
    print("🔄 Generating raw data landscape view...")
    landscape_data = generate_raw_data_landscape(processed_data_dir)
    
    landscape_path = views_dir / 'raw_data_landscape.json'
    with open(landscape_path, 'w') as f:
        json.dump(landscape_data, f, indent=2)
    
    size_kb = len(json.dumps(landscape_data)) / 1024
    indices_count = len(landscape_data['raw_data_landscape']['indices_overview'])
    datasets_count = len(landscape_data['raw_data_landscape']['datasets_info'])
    
    print(f"✅ Generated {landscape_path}")
    print(f"   📊 {indices_count} indices, {datasets_count} datasets")
    print(f"   📏 {size_kb:.1f} KB")
    
    # Generate Index Distributions view
    print("🔄 Generating index distributions view...")
    distributions_data = generate_index_distributions(processed_data_dir)
    
    distributions_path = views_dir / 'index_distributions.json'
    with open(distributions_path, 'w') as f:
        json.dump(distributions_data, f, indent=2)
    
    distributions_size_kb = len(json.dumps(distributions_data)) / 1024
    bandwidths = distributions_data['available_bandwidths']
    total_analyses = sum(
        len(analyses) for analyses in distributions_data['index_distributions_by_bandwidth'].values()
    )
    
    print(f"✅ Generated {distributions_path}")
    print(f"   📊 {total_analyses} analyses across {len(bandwidths)} bandwidths")
    print(f"   📏 {distributions_size_kb:.1f} KB")
    
    # Summary
    print(f"\n🎉 Chart views generation complete!")
    print(f"   📁 Views saved to: {views_dir}")
    print(f"\n💡 Next steps:")
    print(f"   1. Test views: npm run dev")
    print(f"   2. Deploy to CDN: npm run deploy")


if __name__ == "__main__":
    main()