#!/usr/bin/env python3
"""
Thin wrapper to generate species timeline views.

This script generates optimized species timeline data for the dashboard frontend.
It processes detection data and aggregates it into monthly summaries for each
biological species, significantly reducing data size vs raw detection data.
"""

import sys
import json
from pathlib import Path

# Add project root to path to import mbon_analysis
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.views.species_views import generate_species_timeline


def main():
    """Generate species timeline view data."""
    print("🧬 Generating species timeline view...")
    
    # Generate the species timeline data
    data = generate_species_timeline(Path('data/cdn/processed'))
    
    # Ensure output directory exists
    output_path = Path('data/cdn/views/species_timeline.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Calculate and report file size
    file_size_bytes = len(json.dumps(data).encode('utf-8'))
    file_size_kb = file_size_bytes / 1024
    
    print(f"✅ Generated {output_path}")
    print(f"📊 File size: {file_size_kb:.1f} KB")
    print(f"🐟 Species included: {data['metadata']['total_species']}")
    print(f"📅 Aggregation level: {data['metadata']['aggregation_level']}")
    
    # Performance note
    if file_size_kb < 100:
        print("🚀 Excellent! File size is well under the 100KB target")
    elif file_size_kb < 200:
        print("✅ Good! File size is reasonable for dashboard loading")
    else:
        print(f"⚠️  Warning: File size ({file_size_kb:.1f} KB) may be too large for optimal performance")


if __name__ == "__main__":
    main()