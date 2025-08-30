#!/usr/bin/env python3
"""Generate acoustic_indices_distributions.json for dashboard."""

from pathlib import Path
from mbon_analysis.views.acoustic_indices_distributions import AcousticIndicesDistributionsGenerator

def main():
    """Generate the view."""
    # Path to data directory
    data_root = Path(__file__).parent.parent / "data"
    
    print("🎵 Generating acoustic indices distributions view...")
    print(f"   Data root: {data_root}")
    
    # Generate view
    generator = AcousticIndicesDistributionsGenerator(data_root)
    result = generator.create_view("acoustic_indices_distributions.json")
    
    print(f"✅ Generated {result['filename']}")
    print(f"   Size: {result['size_kb']} KB")
    print(f"   Path: {result['path']}")
    print(f"   Records: {result['records']}")

if __name__ == "__main__":
    main()