#!/usr/bin/env python3
"""
Validate processed JSON files before deployment.
Run this after processing to ensure data integrity.
"""

import json
import sys
from pathlib import Path
import pandas as pd

def validate_json_file(filepath, expected_records=None):
    """Validate a single JSON file."""
    print(f"Validating {filepath.name}...")
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Check structure
        if isinstance(data, list):
            if len(data) == 0:
                print(f"  ❌ Empty data file")
                return False
            elif expected_records and len(data) < expected_records:
                print(f"  ⚠️  Warning: Only {len(data)} records (expected at least {expected_records})")
                return False
            else:
                print(f"  ✓ {len(data):,} records")
            
            # Check DataFrame structure
            if len(data) > 0:
                df = pd.DataFrame(data)
                print(f"  ✓ {len(df.columns)} columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        else:
            print(f"  ✓ Metadata/configuration file")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Validation error: {e}")
        return False

def main():
    output_dir = Path("data/cdn/processed")
    
    # Files with expected minimum record counts
    files_to_check = {
        "detections.json": 20000,        # Should have ~26k records
        "environmental.json": 200000,     # Should have ~237k records
        "species.json": 20,              # Should have ~27 species
        "stations.json": 3,              # Should have 3 stations
        "metadata.json": None,           # Metadata file
        "acoustic_indices.json": 30000   # Should have ~35k records if available
    }
    
    all_valid = True
    
    for filename, min_records in files_to_check.items():
        filepath = output_dir / filename
        if not filepath.exists():
            if filename == "acoustic_indices.json":
                print(f"ℹ️  Optional file missing: {filename}")
                continue
            else:
                print(f"❌ Missing required file: {filename}")
                all_valid = False
        else:
            if not validate_json_file(filepath, min_records):
                all_valid = False
    
    if all_valid:
        print(f"\n✅ All validations passed! Data is ready for deployment.")
        print(f"📁 Validated files in: {output_dir}")
        sys.exit(0)
    else:
        print(f"\n❌ Validation failed! Please fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()