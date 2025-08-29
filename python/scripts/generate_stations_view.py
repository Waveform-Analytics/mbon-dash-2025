#!/usr/bin/env python3
"""Generate stations.json view file."""

from pathlib import Path
from mbon_analysis.views.stations import StationsViewGenerator


def main():
    """Generate stations view."""
    print("🏗️  Generating stations.json view")
    print("=" * 40)
    
    # Get data root directory
    current_dir = Path(__file__).parent.parent
    data_root = current_dir / "data"
    
    # Create view generator
    generator = StationsViewGenerator(data_root)
    
    # Generate and save the view
    try:
        result = generator.create_view("stations.json")
        
        print(f"✅ Successfully generated stations view:")
        print(f"   📁 File: {result['filename']}")
        print(f"   📍 Path: {result['path']}")
        print(f"   📊 Size: {result['size_kb']} KB")
        print(f"   📈 Records: {result['records']} stations")
        
        # Validate file size (should be < 50KB according to architecture)
        if result['size_kb'] < 50:
            print(f"✅ File size within target (< 50KB)")
        else:
            print(f"⚠️  File size exceeds target of 50KB")
            
    except Exception as e:
        print(f"❌ Failed to generate stations view: {e}")
        raise
    
    print("\n🎉 Stations view generation complete!")


if __name__ == "__main__":
    main()