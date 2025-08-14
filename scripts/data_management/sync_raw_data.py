#!/usr/bin/env python3
"""
Sync raw data files from CDN using manifest-based approach.

This script:
1. Downloads manifest from CDN to discover available files
2. Compares local files with CDN manifest (size, timestamp)
3. Downloads only files that are missing or outdated
4. Automatically discovers new indices files without code changes
"""

import os
import urllib.request
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

# CDN configuration
CDN_BASE_URL = "https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev/raw-data"
MANIFEST_URL = f"{CDN_BASE_URL}/data_manifest.json"

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file for integrity checking."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()[:8]  # First 8 chars for brevity
    except Exception:
        return ""

def get_local_file_info(file_path: Path) -> Dict[str, Any]:
    """Get local file information (size, modified time, checksum)."""
    if not file_path.exists():
        return {"exists": False}
    
    stat = file_path.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        "checksum": calculate_file_hash(file_path)
    }

def download_manifest() -> Optional[Dict[str, Any]]:
    """Download and parse the data manifest from CDN."""
    try:
        print(f"📋 Downloading manifest from {MANIFEST_URL}")
        with urllib.request.urlopen(MANIFEST_URL) as response:
            manifest = json.loads(response.read().decode())
        print(f"  ✓ Found {len(manifest['files'])} files in manifest")
        return manifest
    except Exception as e:
        print(f"  ✗ Failed to download manifest: {e}")
        return None

def needs_download(local_info: Dict[str, Any], cdn_info: Dict[str, Any]) -> Tuple[bool, str]:
    """Determine if file needs to be downloaded and why."""
    if not local_info["exists"]:
        return True, "missing"
    
    if local_info["size_bytes"] != cdn_info["size_bytes"]:
        return True, f"size mismatch (local: {local_info['size_bytes']}, cdn: {cdn_info['size_bytes']})"
    
    # Compare timestamps (if available)
    if "last_modified" in cdn_info and "last_modified" in local_info:
        if local_info["last_modified"] < cdn_info["last_modified"]:
            return True, "outdated"
    
    return False, "up-to-date"

def download_file(url: str, local_path: Path, expected_size: int) -> bool:
    """Download a file from URL to local path with progress indication."""
    try:
        print(f"⬇️  Downloading {url}")
        print(f"   → {local_path}")
        
        # Create parent directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        urllib.request.urlretrieve(url, local_path)
        
        # Verify size
        actual_size = local_path.stat().st_size
        size_mb = actual_size / (1024 * 1024)
        
        if actual_size != expected_size:
            print(f"   ⚠️  Size mismatch: expected {expected_size}, got {actual_size}")
            return False
        
        print(f"   ✓ Downloaded {size_mb:.1f} MB")
        return True
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

def find_indices_files(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all indices files from manifest."""
    indices_files = {}
    for file_path, info in manifest["files"].items():
        if file_path.startswith("indices/") and file_path.endswith(".csv"):
            indices_files[file_path] = info
    return indices_files

def sync_data(force_download: bool = False, indices_only: bool = False) -> None:
    """Main sync function."""
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / "data" / "cdn" / "raw-data"
    
    print("🔄 Syncing raw data with CDN...")
    print(f"CDN Base URL: {CDN_BASE_URL}")
    print(f"Local data directory: {data_dir}")
    print()
    
    # Download manifest
    manifest = download_manifest()
    if not manifest:
        print("❌ Cannot continue without manifest")
        return
    
    print(f"📅 Manifest last updated: {manifest.get('last_updated', 'unknown')}")
    print()
    
    # Filter files if indices_only
    files_to_check = manifest["files"]
    if indices_only:
        files_to_check = find_indices_files(manifest)
        print(f"🎯 Focusing on indices files only ({len(files_to_check)} files)")
        print()
    
    # Check each file
    download_queue = []
    up_to_date = 0
    
    for file_path, cdn_info in files_to_check.items():
        local_path = data_dir / file_path
        local_info = get_local_file_info(local_path)
        
        should_download, reason = needs_download(local_info, cdn_info)
        
        if force_download or should_download:
            download_queue.append((file_path, cdn_info, reason))
            status = "📥" if should_download else "🔄"
            print(f"{status} {file_path} - {reason}")
        else:
            up_to_date += 1
            print(f"✅ {file_path} - {reason}")
    
    print()
    print(f"📊 Summary: {up_to_date} up-to-date, {len(download_queue)} to download")
    
    if not download_queue:
        print("🎉 All files are up-to-date!")
        return
    
    # Download files
    print()
    print(f"⬇️  Downloading {len(download_queue)} files...")
    
    downloaded = 0
    failed = 0
    
    for file_path, cdn_info, reason in download_queue:
        url = f"{CDN_BASE_URL}/{file_path}"
        local_path = data_dir / file_path
        
        if download_file(url, local_path, cdn_info["size_bytes"]):
            downloaded += 1
        else:
            failed += 1
    
    print()
    print(f"✅ Sync complete: {downloaded} downloaded, {failed} failed")
    
    if failed > 0:
        print("❌ Some files failed to download. Check:")
        print("   1. CDN URL is accessible")
        print("   2. Internet connection") 
        print("   3. File permissions")
    else:
        print("🚀 Ready to process data: npm run process-data")

def main():
    """CLI interface for data sync."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync raw data files from CDN")
    parser.add_argument("--force", action="store_true", 
                       help="Force download all files (ignore local timestamps)")
    parser.add_argument("--indices-only", action="store_true",
                       help="Only sync indices files")
    parser.add_argument("--check-only", action="store_true",
                       help="Check status without downloading")
    
    args = parser.parse_args()
    
    if args.check_only:
        # Just show status without downloading
        manifest = download_manifest()
        if manifest:
            indices_files = find_indices_files(manifest)
            print(f"📋 Available indices files:")
            for file_path in indices_files:
                print(f"   • {file_path}")
    else:
        sync_data(force_download=args.force, indices_only=args.indices_only)

if __name__ == "__main__":
    main()