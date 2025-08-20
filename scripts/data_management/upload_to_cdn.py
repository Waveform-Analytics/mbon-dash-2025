#!/usr/bin/env python3
"""
Upload processed JSON files to Cloudflare R2 CDN.

This script handles uploading processed dashboard data to the CDN for production use.
For now, it provides instructions for manual upload. Future versions could integrate
with R2 API or AWS CLI for automated uploads.
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# CDN configuration
CDN_BASE_URL = "https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev"

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file for integrity checking."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()[:8]

def get_file_info(file_path: Path) -> Dict[str, Any]:
    """Get file metadata for upload verification."""
    if not file_path.exists():
        return {"exists": False}
    
    stat = file_path.stat()
    return {
        "exists": True,
        "filename": file_path.name,
        "size_bytes": stat.st_size,
        "size_human": format_bytes(stat.st_size),
        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "checksum": calculate_file_hash(file_path)
    }

def format_bytes(bytes_size: int) -> str:
    """Format bytes in human readable form."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

def find_processed_files() -> List[Path]:
    """Find all processed JSON files that should be uploaded to CDN."""
    processed_dir = Path(__file__).parent.parent.parent / "data" / "cdn" / "processed"
    
    if not processed_dir.exists():
        print(f"❌ Processed data directory not found: {processed_dir}")
        return []
    
    json_files = list(processed_dir.glob("*.json"))
    return sorted(json_files)

def generate_upload_manifest(files: List[Path]) -> Dict[str, Any]:
    """Generate manifest for upload verification."""
    manifest = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "description": "MBON processed data files for CDN upload",
        "cdn_destination": f"{CDN_BASE_URL}/processed/",
        "files": {}
    }
    
    for file_path in files:
        file_info = get_file_info(file_path)
        if file_info["exists"]:
            manifest["files"][file_path.name] = file_info
    
    return manifest

def create_upload_script(files: List[Path]) -> str:
    """Generate shell script for batch upload using AWS CLI or similar."""
    script_lines = [
        "#!/bin/bash",
        "# Batch upload script for MBON processed data",
        "# Make sure you have AWS CLI configured with R2 credentials",
        "",
        "set -e  # Exit on any error",
        "",
        "# Configuration",
        "BUCKET_NAME=\"your-r2-bucket-name\"",
        "CDN_PATH=\"processed\"",
        "LOCAL_DIR=\"data/cdn/processed\"",
        "",
        "echo \"🚀 Uploading processed data files to CDN...\"",
        ""
    ]
    
    for file_path in files:
        file_info = get_file_info(file_path)
        if file_info["exists"]:
            relative_path = file_path.name
            script_lines.extend([
                f"echo \"📤 Uploading {relative_path} ({file_info['size_human']})...\"",
                f"aws s3 cp \"{file_path}\" \"s3://$BUCKET_NAME/$CDN_PATH/{relative_path}\" --endpoint-url https://your-account-id.r2.cloudflarestorage.com",
                ""
            ])
    
    script_lines.extend([
        "echo \"✅ Upload complete!\"",
        "echo \"Files should be available at:\"",
        f"echo \"  {CDN_BASE_URL}/processed/\"",
    ])
    
    return "\n".join(script_lines)

def main():
    """Generate upload instructions and scripts for CDN deployment."""
    print("📦 MBON Dashboard CDN Upload Utility")
    print("=" * 50)
    
    # Find processed files
    print("\n📊 Finding processed JSON files...")
    files = find_processed_files()
    
    if not files:
        print("❌ No processed files found. Run data processing scripts first:")
        print("   npm run process-data")
        print("   uv run scripts/analysis/generate_step1a_raw_data_landscape.py")
        return
    
    print(f"✅ Found {len(files)} processed files:")
    
    total_size = 0
    for file_path in files:
        file_info = get_file_info(file_path)
        if file_info["exists"]:
            print(f"   • {file_info['filename']:<40} {file_info['size_human']:>10}")
            total_size += file_info["size_bytes"]
    
    print(f"\n📊 Total size to upload: {format_bytes(total_size)}")
    
    # Generate manifest
    print("\n📋 Generating upload manifest...")
    manifest = generate_upload_manifest(files)
    
    # Save manifest
    manifest_path = Path(__file__).parent / "upload_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Upload manifest saved: {manifest_path}")
    
    # Generate upload script
    print("\n🔧 Generating upload script...")
    upload_script = create_upload_script(files)
    
    script_path = Path(__file__).parent / "upload_to_r2.sh"
    with open(script_path, 'w') as f:
        f.write(upload_script)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Upload script generated: {script_path}")
    
    # Instructions
    print("\n" + "=" * 60)
    print("📋 UPLOAD INSTRUCTIONS")
    print("=" * 60)
    
    print("\n🔧 Option 1: Manual Upload via Cloudflare Dashboard")
    print("   1. Go to Cloudflare R2 dashboard")
    print("   2. Navigate to your bucket")
    print("   3. Create 'processed' folder if it doesn't exist")
    print("   4. Upload these files to the 'processed' folder:")
    
    for file_path in files:
        print(f"      • {file_path}")
    
    print(f"\n🤖 Option 2: Automated Upload via AWS CLI")
    print("   1. Install AWS CLI: https://aws.amazon.com/cli/")
    print("   2. Configure R2 credentials:")
    print("      aws configure set aws_access_key_id YOUR_R2_KEY_ID")
    print("      aws configure set aws_secret_access_key YOUR_R2_SECRET_KEY")
    print(f"   3. Edit the upload script: {script_path}")
    print("      - Update BUCKET_NAME")
    print("      - Update endpoint URL with your account ID")
    print("   4. Run the upload script:")
    print(f"      bash {script_path}")
    
    print("\n🔍 Option 3: Verification")
    print("   After upload, verify files are accessible:")
    for file_path in files:
        print(f"   • {CDN_BASE_URL}/processed/{file_path.name}")
    
    print(f"\n📊 Upload Summary:")
    print(f"   • Files to upload: {len(files)}")
    print(f"   • Total size: {format_bytes(total_size)}")
    print(f"   • Manifest: {manifest_path}")
    print(f"   • Upload script: {script_path}")

if __name__ == "__main__":
    main()