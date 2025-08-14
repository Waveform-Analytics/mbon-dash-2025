#!/usr/bin/env python3
"""
Download raw data files from CDN for local development.

This script downloads the raw Excel/CSV files needed for data processing
from the CDN to your local data/ directory.
"""

import os
import urllib.request
import json
from pathlib import Path

# CDN base URL (nested structure - mirrors local organization)
CDN_BASE_URL = "https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev/raw-data"

# Raw data file manifest (nested paths)
RAW_DATA_FILES = [
    # Acoustic indices
    "indices/Acoustic_Indices_9m_FullBW_v1.csv",
    
    # Detection data (2018)
    "2018/Master_Manual_9M_2h_2018.xlsx",
    "2018/Master_Manual_14M_2h_2018.xlsx", 
    "2018/Master_Manual_37M_2h_2018.xlsx",
    
    # Detection data (2021)
    "2021/Master_Manual_9M_2h_2021.xlsx",
    "2021/Master_Manual_14M_2h_2021.xlsx",
    "2021/Master_Manual_37M_2h_2021.xlsx",
    
    # Environmental data (2018)
    "2018/Master_9M_Temp_2018.xlsx",
    "2018/Master_9M_Depth_2018.xlsx",
    "2018/Master_14M_Temp_2018.xlsx", 
    "2018/Master_14M_Depth_2018.xlsx",
    "2018/Master_37M_Temp_2018.xlsx",
    "2018/Master_37M_Depth_2018.xlsx",
    
    # Environmental data (2021)
    "2021/Master_9M_Temp_2021.xlsx",
    "2021/Master_9M_Depth_2021.xlsx",
    "2021/Master_14M_Temp_2021.xlsx",
    "2021/Master_14M_Depth_2021.xlsx", 
    "2021/Master_37M_Temp_2021.xlsx",
    "2021/Master_37M_Depth_2021.xlsx",
    
    # Acoustic indices data (2018)
    "2018/Master_rmsSPL_9M_1h_2018.xlsx",
    "2018/Master_rmsSPL_14M_1h_2018.xlsx",
    "2018/Master_rmsSPL_37M_1h_2018.xlsx",
    
    # Acoustic indices data (2021) 
    "2021/Master_rmsSPL_9M_1h_2021.xlsx",
    "2021/Master_rmsSPL_14M_1h_2021.xlsx",
    "2021/Master_rmsSPL_37M_1h_2021.xlsx",
    
    # Metadata
    "1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
]

def download_file(url: str, local_path: Path) -> bool:
    """Download a file from URL to local path."""
    try:
        print(f"Downloading {url} -> {local_path}")
        
        # Create parent directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        urllib.request.urlretrieve(url, local_path)
        
        # Check file size
        size_mb = local_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ Downloaded {size_mb:.1f} MB")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def main():
    """Download all raw data files."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "raw-data"
    
    print("🔄 Downloading raw data files from CDN...")
    print(f"CDN Base URL: {CDN_BASE_URL}")
    print(f"Local data directory: {data_dir}")
    print()
    
    downloaded = 0
    failed = 0
    
    for file_path in RAW_DATA_FILES:
        url = f"{CDN_BASE_URL}/{file_path}"
        local_path = data_dir / file_path
        
        if download_file(url, local_path):
            downloaded += 1
        else:
            failed += 1
    
    print()
    print(f"✅ Download complete: {downloaded} files downloaded, {failed} failed")
    
    if failed > 0:
        print("❌ Some files failed to download. Check:")
        print("   1. CDN URL is correct")
        print("   2. Files exist on CDN") 
        print("   3. Internet connection")
        print("   4. File names match exactly (case-sensitive)")
    else:
        print("🚀 Ready to run: npm run build-data")

if __name__ == "__main__":
    main()