#!/usr/bin/env python3
"""
Generate data manifest from local files for CDN upload.

This script scans your local data directory and creates a manifest.json
file that lists all files with their metadata (size, timestamp, checksum).
Upload this manifest to your CDN so the sync script can discover files.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()[:8]  # First 8 chars for brevity

def generate_manifest(data_dir: Path) -> Dict[str, Any]:
    """Generate manifest from files in data directory."""
    manifest = {
        "version": "1.0",
        "last_updated": datetime.now().isoformat() + "Z",
        "description": "MBON raw data file manifest for CDN synchronization",
        "files": {}
    }
    
    # Find all files recursively
    for file_path in data_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            # Get relative path from data_dir
            rel_path = file_path.relative_to(data_dir)
            rel_path_str = str(rel_path).replace('\\', '/')  # Use forward slashes
            
            # Get file stats
            stat = file_path.stat()
            
            # Add to manifest
            manifest["files"][rel_path_str] = {
                "size_bytes": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                "checksum": calculate_file_hash(file_path),
                "description": generate_description(rel_path_str)
            }
    
    return manifest

def generate_description(file_path: str) -> str:
    """Generate human-readable description for file."""
    path_parts = file_path.split('/')
    filename = path_parts[-1]
    
    # Acoustic indices
    if "indices" in path_parts and filename.endswith('.csv'):
        if "9m" in filename.lower() or "9M" in filename:
            return "Station 9M acoustic indices"
        elif "14m" in filename.lower() or "14M" in filename:
            return "Station 14M acoustic indices"
        elif "37m" in filename.lower() or "37M" in filename:
            return "Station 37M acoustic indices"
        else:
            return "Acoustic indices data"
    
    # Manual detection files
    if "Manual" in filename:
        station = "Unknown"
        year = "Unknown"
        if "9M" in filename:
            station = "9M"
        elif "14M" in filename:
            station = "14M"
        elif "37M" in filename:
            station = "37M"
        
        if "2018" in filename:
            year = "2018"
        elif "2021" in filename:
            year = "2021"
        
        return f"Station {station} manual detections, {year}"
    
    # Environmental data
    if "Temp" in filename:
        station = "Unknown"
        year = "Unknown"
        if "9M" in filename:
            station = "9M"
        elif "14M" in filename:
            station = "14M"
        elif "37M" in filename:
            station = "37M"
        
        if "2018" in filename:
            year = "2018"
        elif "2021" in filename:
            year = "2021"
        
        return f"Station {station} temperature data, {year}"
    
    if "Depth" in filename:
        station = "Unknown"
        year = "Unknown"
        if "9M" in filename:
            station = "9M"
        elif "14M" in filename:
            station = "14M"
        elif "37M" in filename:
            station = "37M"
        
        if "2018" in filename:
            year = "2018"
        elif "2021" in filename:
            year = "2021"
        
        return f"Station {station} depth data, {year}"
    
    # RMS SPL data
    if "rmsSPL" in filename:
        station = "Unknown"
        year = "Unknown"
        if "9M" in filename:
            station = "9M"
        elif "14M" in filename:
            station = "14M"
        elif "37M" in filename:
            station = "37M"
        
        if "2018" in filename:
            year = "2018"
        elif "2021" in filename:
            year = "2021"
        
        return f"Station {station} RMS SPL data, {year}"
    
    # Metadata
    if "metadata" in filename.lower() or "deployment" in filename.lower():
        return "Deployment metadata 2017-2022"
    
    if "column_names" in filename:
        return "Detection column name mappings"
    
    if "Index_Categories" in filename:
        return "Acoustic index categories"
    
    # Default
    return f"Data file: {filename}"

def main():
    """Generate manifest from local data directory."""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "cdn" / "raw-data"
    output_file = project_root / "scripts" / "data_management" / "data_manifest.json"
    
    print("📋 Generating data manifest...")
    print(f"Scanning directory: {data_dir}")
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    # Generate manifest
    manifest = generate_manifest(data_dir)
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Manifest generated: {output_file}")
    print(f"📊 Found {len(manifest['files'])} files")
    
    # Show indices files
    indices_files = [f for f in manifest['files'].keys() if f.startswith('indices/')]
    if indices_files:
        print(f"\n🎯 Indices files found:")
        for f in indices_files:
            size_mb = manifest['files'][f]['size_bytes'] / (1024 * 1024)
            print(f"   • {f} ({size_mb:.1f} MB)")
    
    print(f"\n📤 Next steps:")
    print(f"   1. Upload {output_file.name} to your CDN root")
    print(f"   2. Upload all files from {data_dir} to CDN")
    print(f"   3. Run: uv run scripts/data_management/sync_raw_data.py --check-only")

if __name__ == "__main__":
    main()