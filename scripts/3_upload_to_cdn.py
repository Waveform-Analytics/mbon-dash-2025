#!/usr/bin/env python3
"""
Upload views to Cloudflare R2 CDN.

Uploads optimized view files to CDN for dashboard consumption.
This is Step 3 of the 3-step data pipeline.
"""

import json
import os
import hashlib
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Setup simple logging
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configuration
VIEWS_DIR = Path("data/cdn/views")
CDN_BASE_URL = "https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev"


def format_bytes(bytes_size: int) -> str:
    """Format bytes in human readable form."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash for file integrity."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()[:8]


def check_upload_tools():
    """Check if upload tools are available."""
    tools = []
    
    # Check for AWS CLI (for R2)
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            tools.append('aws-cli')
    except FileNotFoundError:
        pass
    
    # Check for rclone
    try:
        result = subprocess.run(['rclone', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            tools.append('rclone')
    except FileNotFoundError:
        pass
        
    return tools


def upload_with_aws_cli():
    """Upload files using AWS CLI (for Cloudflare R2)."""
    try:
        logger.info("📤 Uploading with AWS CLI...")
        
        # Upload views directory to R2
        cmd = [
            'aws', 's3', 'sync', 
            str(VIEWS_DIR),
            f's3://your-r2-bucket/views/',
            '--endpoint-url', 'https://your-account-id.r2.cloudflarestorage.com',
            '--delete'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ AWS CLI upload successful!")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"❌ AWS CLI upload failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error with AWS CLI upload: {e}")
        return False


def generate_upload_summary():
    """Generate upload summary and instructions."""
    if not VIEWS_DIR.exists():
        logger.error(f"❌ Views directory not found: {VIEWS_DIR}")
        logger.error("   Run '2_generate_all_views.py' first")
        return None
        
    files_to_upload = []
    total_size = 0
    
    for file_path in VIEWS_DIR.glob("*.json"):
        stat = file_path.stat()
        files_to_upload.append({
            "filename": file_path.name,
            "size_bytes": stat.st_size,
            "size_human": format_bytes(stat.st_size),
            "checksum": calculate_file_hash(file_path),
            "local_path": str(file_path),
            "cdn_url": f"{CDN_BASE_URL}/views/{file_path.name}"
        })
        total_size += stat.st_size
        
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_files": len(files_to_upload),
        "total_size_bytes": total_size,
        "total_size_human": format_bytes(total_size),
        "files": files_to_upload,
        "upload_instructions": {
            "manual_upload": f"Upload all files from {VIEWS_DIR} to your CDN",
            "aws_cli_example": f"aws s3 sync {VIEWS_DIR} s3://your-bucket/views/ --endpoint-url https://your-account.r2.cloudflarestorage.com",
            "verification": f"Check files are accessible at {CDN_BASE_URL}/views/"
        }
    }
    
    return summary


def main():
    """Upload view files to CDN."""
    try:
        logger.info("📤 Starting CDN upload...")
        
        # Generate upload summary
        summary = generate_upload_summary()
        if not summary:
            return 1
            
        logger.info(f"📊 Found {summary['total_files']} files ({summary['total_size_human']})")
        
        # Check for upload tools
        tools = check_upload_tools()
        
        if 'aws-cli' in tools:
            # Try automated upload with AWS CLI
            success = upload_with_aws_cli()
            if success:
                logger.info("✅ Upload complete!")
                return 0
        
        # Fallback to manual instructions
        logger.info("📋 Manual upload required:")
        logger.info(f"   Source: {VIEWS_DIR}")
        logger.info(f"   Destination: Your CDN /views/ directory")
        logger.info("")
        logger.info("Files to upload:")
        
        for file_info in summary['files']:
            logger.info(f"  ✓ {file_info['filename']} ({file_info['size_human']})")
            
        logger.info("")
        logger.info("Upload verification:")
        for file_info in summary['files']:
            logger.info(f"  🌐 {file_info['cdn_url']}")
            
        # Save upload summary for reference
        summary_path = VIEWS_DIR / "upload_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"📄 Upload summary saved: {summary_path}")
        logger.info("")
        logger.info("💡 Setup automated upload:")
        logger.info("   1. Install AWS CLI: pip install awscli")
        logger.info("   2. Configure R2 credentials: aws configure")
        logger.info("   3. Update bucket name in this script")
        logger.info("   4. Re-run this script for automatic upload")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error in CDN upload: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())