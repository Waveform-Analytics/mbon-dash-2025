#!/usr/bin/env python3
"""Thin wrapper to generate station views.

This script generates optimized station overview data for the dashboard frontend.
It reads from processed JSON files and creates a lightweight view file.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.views.station_views import generate_station_overview


def main():
    """Generate station overview JSON file."""
    try:
        # Generate the station overview data
        print("🔄 Generating station overview from processed data...")
        data = generate_station_overview(Path('data/cdn/processed'))
        
        # Create output directory if it doesn't exist
        output_path = Path('data/cdn/views/station_overview.json')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the optimized JSON file
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Report success with file size
        file_size = len(json.dumps(data))
        file_size_kb = file_size / 1024
        
        print(f"✅ Generated {output_path}")
        print(f"📊 File size: {file_size} bytes ({file_size_kb:.1f} KB)")
        print(f"🏢 Stations: {data['metadata']['total_stations']}")
        print(f"📅 Generated: {data['metadata']['generated_at']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating station views: {e}")
        return 1


if __name__ == "__main__":
    exit(main())