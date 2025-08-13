#!/usr/bin/env python3
"""
Check if processed data files exist and are fresh.
Used to determine if data processing needs to run.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

OUTPUT_DIR = Path("public/data")
METADATA_FILE = OUTPUT_DIR / "metadata.json"

# How old data can be before considered stale (in hours)
FRESHNESS_THRESHOLD_HOURS = 24

def check_data_exists():
    """Check if all required data files exist."""
    required_files = [
        "detections.json",
        "environmental.json", 
        "acoustic.json",
        "stations.json",
        "species.json",
        "metadata.json"
    ]
    
    for filename in required_files:
        if not (OUTPUT_DIR / filename).exists():
            print(f"❌ Missing file: {filename}")
            return False
    
    return True

def check_data_freshness():
    """Check if data was processed recently."""
    if not METADATA_FILE.exists():
        return False
        
    try:
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        
        generated_at = metadata.get('generated_at')
        if not generated_at:
            return False
            
        # Parse the timestamp
        generated_time = datetime.fromisoformat(generated_at)
        age = datetime.now() - generated_time
        
        if age > timedelta(hours=FRESHNESS_THRESHOLD_HOURS):
            print(f"⚠️  Data is {age.days} days old (threshold: {FRESHNESS_THRESHOLD_HOURS} hours)")
            return False
            
        print(f"✅ Data is fresh ({age.total_seconds() / 3600:.1f} hours old)")
        return True
        
    except Exception as e:
        print(f"❌ Error checking data freshness: {e}")
        return False

def main():
    """Main check function."""
    if not check_data_exists():
        print("📊 Data processing needed: Missing files")
        sys.exit(1)
    
    if not check_data_freshness():
        print("📊 Data processing recommended: Data is stale")
        sys.exit(1)
    
    print("✅ Data is fresh and complete - no processing needed")
    sys.exit(0)

if __name__ == "__main__":
    main()