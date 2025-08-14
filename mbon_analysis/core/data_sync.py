#!/usr/bin/env python3
"""
CDN data synchronization utilities for MBON datasets.

This module provides functions to check for updates and sync raw data files
from the CDN using a manifest-based approach. It works alongside data_loader
to ensure you have the latest data before analysis.
"""

import json
import hashlib
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

# CDN configuration
CDN_BASE_URL = "https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev/raw-data"
MANIFEST_URL = f"{CDN_BASE_URL}/data_manifest.json"


def get_raw_data_directory(custom_path: Optional[Path] = None) -> Path:
    """
    Get the path to the raw data directory.
    
    Args:
        custom_path: Optional custom path to data directory
        
    Returns:
        Path to the raw data directory
    """
    if custom_path:
        return Path(custom_path)
    
    # Get project root (3 levels up from this file)
    package_dir = Path(__file__).resolve().parent.parent.parent
    return package_dir / "data" / "cdn" / "raw-data"


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file for integrity checking."""
    if not file_path.exists():
        return ""
    
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()[:8]  # First 8 chars for brevity
    except Exception:
        return ""


def download_manifest(verbose: bool = True) -> Optional[Dict[str, Any]]:
    """
    Download and parse the data manifest from CDN.
    
    Args:
        verbose: Whether to print progress
        
    Returns:
        Manifest dictionary or None if download fails
    """
    try:
        if verbose:
            print(f"📋 Downloading manifest from CDN...")
        
        with urllib.request.urlopen(MANIFEST_URL) as response:
            manifest = json.loads(response.read().decode())
        
        if verbose:
            print(f"  ✓ Found {len(manifest.get('files', {}))} files in manifest")
            print(f"  ✓ Last updated: {manifest.get('last_updated', 'unknown')}")
        
        return manifest
    except Exception as e:
        if verbose:
            print(f"  ✗ Failed to download manifest: {e}")
        return None


def check_file_status(local_path: Path, cdn_info: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check if a local file needs to be updated from CDN.
    
    Args:
        local_path: Path to local file
        cdn_info: CDN file metadata from manifest
        
    Returns:
        Tuple of (needs_update, reason)
    """
    if not local_path.exists():
        return True, "missing"
    
    # Check file size
    local_size = local_path.stat().st_size
    cdn_size = cdn_info.get("size_bytes", 0)
    
    if local_size != cdn_size:
        return True, f"size mismatch (local: {local_size}, cdn: {cdn_size})"
    
    # Check hash if available
    if "checksum" in cdn_info:
        local_hash = calculate_file_hash(local_path)
        if local_hash != cdn_info["checksum"]:
            return True, "checksum mismatch"
    
    return False, "up-to-date"


def download_file(url: str, local_path: Path, expected_size: int = 0, 
                 verbose: bool = True) -> bool:
    """
    Download a file from URL to local path.
    
    Args:
        url: URL to download from
        local_path: Local path to save to
        expected_size: Expected file size for verification
        verbose: Whether to print progress
        
    Returns:
        True if download successful
    """
    try:
        if verbose:
            print(f"  ⬇️  Downloading {local_path.name}...")
        
        # Create parent directory if needed
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download file
        urllib.request.urlretrieve(url, local_path)
        
        # Verify size if provided
        if expected_size > 0:
            actual_size = local_path.stat().st_size
            if actual_size != expected_size:
                if verbose:
                    print(f"     ⚠️  Size mismatch: expected {expected_size}, got {actual_size}")
                return False
        
        size_mb = local_path.stat().st_size / (1024 * 1024)
        if verbose:
            print(f"     ✓ Downloaded {size_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"     ✗ Failed: {e}")
        return False


def check_data_freshness(data_type: str = "all", verbose: bool = True) -> Dict[str, Any]:
    """
    Check which data files need updating from CDN.
    
    Args:
        data_type: Type of data to check ("all", "indices", "detections", "environmental")
        verbose: Whether to print status
        
    Returns:
        Dictionary with status information
    """
    raw_data_dir = get_raw_data_directory()
    
    # Download manifest
    manifest = download_manifest(verbose=verbose)
    if not manifest:
        return {"status": "error", "message": "Could not download manifest"}
    
    # Filter files by type if requested
    files_to_check = manifest.get("files", {})
    
    if data_type == "indices":
        files_to_check = {k: v for k, v in files_to_check.items() 
                         if k.startswith("indices/")}
    elif data_type == "detections":
        files_to_check = {k: v for k, v in files_to_check.items() 
                         if "Manual" in k}
    elif data_type == "environmental":
        files_to_check = {k: v for k, v in files_to_check.items() 
                         if "Temp" in k or "Depth" in k}
    
    # Check each file
    results = {
        "up_to_date": [],
        "needs_update": [],
        "missing": []
    }
    
    for file_path, cdn_info in files_to_check.items():
        local_path = raw_data_dir / file_path
        needs_update, reason = check_file_status(local_path, cdn_info)
        
        file_info = {
            "path": file_path,
            "reason": reason,
            "size_mb": cdn_info.get("size_bytes", 0) / (1024 * 1024)
        }
        
        if reason == "missing":
            results["missing"].append(file_info)
        elif needs_update:
            results["needs_update"].append(file_info)
        else:
            results["up_to_date"].append(file_info)
    
    if verbose:
        print(f"\n📊 Data freshness summary:")
        print(f"  ✓ Up-to-date: {len(results['up_to_date'])} files")
        print(f"  ⚠️  Needs update: {len(results['needs_update'])} files")
        print(f"  ❌ Missing: {len(results['missing'])} files")
    
    return results


def sync_raw_data(data_type: str = "all", force: bool = False, 
                  verbose: bool = True) -> bool:
    """
    Sync raw data files from CDN.
    
    Args:
        data_type: Type of data to sync ("all", "indices", "detections", "environmental")
        force: Force download even if files are up-to-date
        verbose: Whether to print progress
        
    Returns:
        True if sync successful
    """
    raw_data_dir = get_raw_data_directory()
    
    if verbose:
        print(f"🔄 Syncing {data_type} data from CDN...")
    
    # Check what needs updating
    if not force:
        status = check_data_freshness(data_type, verbose=False)
        files_to_download = status["needs_update"] + status["missing"]
        
        if not files_to_download:
            if verbose:
                print("✅ All files are up-to-date!")
            return True
    else:
        # Force download all files
        manifest = download_manifest(verbose=False)
        if not manifest:
            return False
        
        files_to_download = [
            {"path": path, "size_mb": info.get("size_bytes", 0) / (1024 * 1024)}
            for path, info in manifest.get("files", {}).items()
        ]
    
    # Download files
    if verbose:
        total_size = sum(f["size_mb"] for f in files_to_download)
        print(f"⬇️  Downloading {len(files_to_download)} files ({total_size:.1f} MB total)")
    
    success_count = 0
    failed_count = 0
    
    manifest = download_manifest(verbose=False)  # Get manifest for file info
    
    for file_info in files_to_download:
        file_path = file_info["path"]
        cdn_info = manifest["files"].get(file_path, {})
        
        url = f"{CDN_BASE_URL}/{file_path}"
        local_path = raw_data_dir / file_path
        
        if download_file(url, local_path, cdn_info.get("size_bytes", 0), verbose):
            success_count += 1
        else:
            failed_count += 1
    
    if verbose:
        print(f"\n✅ Sync complete: {success_count} downloaded, {failed_count} failed")
    
    return failed_count == 0


def ensure_data_available(data_type: str = "all", verbose: bool = True) -> bool:
    """
    Ensure required data is available locally, downloading if needed.
    
    This is a convenience function that checks and syncs in one step.
    
    Args:
        data_type: Type of data to ensure ("all", "indices", "detections", "environmental")
        verbose: Whether to print progress
        
    Returns:
        True if all required data is available
    """
    # Check current status
    status = check_data_freshness(data_type, verbose)
    
    # Sync if needed
    if status["needs_update"] or status["missing"]:
        return sync_raw_data(data_type, verbose=verbose)
    
    return True


def sync_and_process(process_func=None, verbose: bool = True) -> bool:
    """
    Sync raw data from CDN and then run processing.
    
    Args:
        process_func: Optional function to run after syncing (e.g., process_excel_to_json)
        verbose: Whether to print progress
        
    Returns:
        True if both sync and processing successful
    """
    # First sync raw data
    if not sync_raw_data(verbose=verbose):
        return False
    
    # Then run processing if function provided
    if process_func:
        if verbose:
            print("\n🔄 Running data processing...")
        
        try:
            process_func()
            if verbose:
                print("✅ Processing complete!")
            return True
        except Exception as e:
            if verbose:
                print(f"❌ Processing failed: {e}")
            return False
    
    return True


# Example usage
if __name__ == "__main__":
    """Example usage of CDN sync functions."""
    
    print("MBON Data Sync Examples")
    print("=" * 50)
    
    # Check data freshness
    print("\n1. Checking data freshness:")
    status = check_data_freshness("indices")
    
    # Ensure indices are available
    print("\n2. Ensuring acoustic indices are available:")
    ensure_data_available("indices")
    
    # Sync all data
    print("\n3. Syncing all data:")
    sync_raw_data("all")