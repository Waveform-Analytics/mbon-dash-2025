#!/usr/bin/env python3
"""
Thin wrapper to generate acoustic summary views.

This script generates optimized acoustic analysis views from processed data,
focusing on PCA analysis and index categorization for research use.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.views.acoustic_views import generate_acoustic_summary


def main():
    """Generate acoustic summary view file."""
    print("🎵 Generating acoustic summary view...")
    
    # Generate acoustic summary data
    try:
        data = generate_acoustic_summary(Path('data/cdn/processed'))
    except Exception as e:
        print(f"❌ Error generating acoustic summary: {e}")
        sys.exit(1)
    
    # Prepare output
    output_path = Path('data/cdn/views/acoustic_summary.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the data
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving acoustic summary: {e}")
        sys.exit(1)
    
    # Report results
    file_size_kb = len(json.dumps(data)) / 1024
    stations = data['metadata']['stations_included']
    total_indices = data['metadata']['total_indices']
    records_processed = data['metadata']['total_records_processed']
    pca_components = len(data['pca_analysis']['components'])
    categories = len(data['index_categories'])
    
    print(f"✅ Generated {output_path}")
    print(f"📊 Size: {file_size_kb:.1f} KB")
    print(f"🏠 Stations: {', '.join(stations) if stations else 'None'}")
    print(f"📈 Indices: {total_indices}")
    print(f"📝 Records: {records_processed:,}")
    print(f"🧬 PCA components: {pca_components}")
    print(f"📂 Categories: {categories}")
    
    # Performance comparison
    original_path = Path('data/cdn/processed/acoustic_indices.json')
    if original_path.exists():
        original_size_mb = original_path.stat().st_size / (1024 * 1024)
        improvement = original_size_mb * 1024 / file_size_kb
        print(f"🚀 Performance: {improvement:.0f}x smaller than original ({original_size_mb:.0f}MB → {file_size_kb:.1f}KB)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())