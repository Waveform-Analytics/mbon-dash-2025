#!/usr/bin/env python3
"""
CDN Upload Script for MBON Dashboard
Uploads view files from data/views/ to Cloudflare R2 CDN
"""

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
import mimetypes
import logging
from typing import List, Tuple

def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cdn_upload.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_environment() -> bool:
    """Load and validate environment variables."""
    # Look for .env.local in the expected location
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / 'dashboard' / '.env.local'
    
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        print("Please ensure .env.local exists in the dashboard/ folder")
        return False
    
    load_dotenv(env_file)
    
    # Validate required environment variables
    required_vars = [
        'CLOUDFLARE_R2_ACCOUNT_ID',
        'CLOUDFLARE_R2_ACCESS_KEY_ID', 
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
        'CLOUDFLARE_R2_BUCKET_NAME',
        'CLOUDFLARE_R2_ENDPOINT'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables loaded successfully")
    return True

def create_r2_client():
    """Create and test R2 client connection."""
    try:
        r2_client = boto3.client(
            's3',
            endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'  # R2 uses 'auto' region
        )
        
        # Test connection
        bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
        r2_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Connected to R2 bucket: {bucket_name}")
        
        return r2_client
        
    except Exception as e:
        print(f"❌ Failed to connect to R2: {e}")
        return None

def get_view_files() -> List[Path]:
    """Get list of JSON view files to upload."""
    root_dir = Path(__file__).parent.parent.parent
    views_dir = root_dir / 'data' / 'views'
    
    if not views_dir.exists():
        print(f"❌ Views directory not found: {views_dir}")
        return []
    
    json_files = list(views_dir.glob('*.json'))
    print(f"📁 Found {len(json_files)} view files in {views_dir}")
    
    return json_files

def upload_file_to_r2(r2_client, file_path: Path, bucket_name: str) -> bool:
    """Upload a single file to R2."""
    try:
        # Determine content type
        content_type = mimetypes.guess_type(str(file_path))[0] or 'application/json'
        
        # Upload to views/ subfolder in bucket
        s3_key = f'views/{file_path.name}'
        
        with open(file_path, 'rb') as f:
            r2_client.upload_fileobj(
                f,
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=3600',  # 1 hour cache
                }
            )
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to upload {file_path.name}: {e}")
        return False

def main():
    """Main upload function."""
    print("🌊 MBON Dashboard - CDN Upload Script")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging()
    
    # Load environment
    if not load_environment():
        return False
    
    # Create R2 client
    r2_client = create_r2_client()
    if not r2_client:
        return False
    
    # Get view files
    view_files = get_view_files()
    if not view_files:
        print("⚠️ No view files found to upload")
        return True
    
    # Upload files
    bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
    cdn_url = os.getenv('CLOUDFLARE_R2_PUBLIC_URL', 'https://waveformdata.work')
    
    uploaded_count = 0
    failed_count = 0
    
    print(f"🚀 Uploading {len(view_files)} files to CDN...")
    
    for file_path in view_files:
        if upload_file_to_r2(r2_client, file_path, bucket_name):
            print(f"   ✅ {file_path.name}")
            uploaded_count += 1
        else:
            failed_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Upload Summary:")
    print(f"   ✅ Successfully uploaded: {uploaded_count} files")
    print(f"   ❌ Failed: {failed_count} files")
    
    if uploaded_count > 0:
        print(f"\n🌐 View your data at: {cdn_url}/views/")
        print(f"📱 Example: {cdn_url}/views/stations_locations.json")
    
    success = failed_count == 0
    if success:
        print("\n🎉 All files uploaded successfully!")
    else:
        print(f"\n⚠️ {failed_count} files failed to upload")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)