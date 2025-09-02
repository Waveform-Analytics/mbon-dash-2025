#!/usr/bin/env python3
"""Upload view files to Cloudflare R2 CDN."""

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
import mimetypes
import logging

def setup_logging():
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

def upload_views_to_cdn():
    """Upload all view files to Cloudflare R2."""
    
    logger = setup_logging()
    
    # Load environment variables from root directory
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / '.env.local'
    
    if not env_file.exists():
        logger.error(f"Environment file not found: {env_file}")
        logger.error("Please create .env.local at the project root")
        return False
    
    # Load environment variables
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
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    # R2 configuration
    try:
        r2 = boto3.client(
            's3',
            endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'  # R2 uses 'auto' region
        )
        logger.info("Successfully connected to Cloudflare R2")
    except Exception as e:
        logger.error(f"Failed to connect to R2: {e}")
        return False
    
    bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
    views_dir = root_dir / 'data' / 'views'
    
    if not views_dir.exists():
        logger.error(f"Views directory not found: {views_dir}")
        return False
    
    logger.info(f"Uploading views from: {views_dir}")
    logger.info(f"Target bucket: {bucket_name}")
    
    uploaded_count = 0
    errors = []
    
    # Get list of JSON files
    json_files = list(views_dir.glob('*.json'))
    logger.info(f"Found {len(json_files)} view files to upload")
    
    for json_file in json_files:
        try:
            # Determine content type
            content_type = mimetypes.guess_type(str(json_file))[0] or 'application/json'
            
            # Upload file to views/ subfolder in bucket
            with open(json_file, 'rb') as f:
                r2.upload_fileobj(
                    f,
                    bucket_name,
                    f'views/{json_file.name}',
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': 'public, max-age=3600'  # 1 hour cache
                        # Note: R2 doesn't use ACLs - public access is configured via custom domain
                    }
                )
            
            logger.info(f"✅ Uploaded: {json_file.name}")
            uploaded_count += 1
            
        except Exception as e:
            error_msg = f"❌ Failed to upload {json_file.name}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    # Print summary
    logger.info(f"\n📊 Upload Summary:")
    logger.info(f"   ✅ Successfully uploaded: {uploaded_count} files")
    logger.info(f"   ❌ Errors: {len(errors)}")
    
    if errors:
        logger.error("\n❌ Errors encountered:")
        for error in errors:
            logger.error(f"   {error}")
        return False
    
    logger.info(f"\n🎉 All {uploaded_count} view files uploaded successfully!")
    logger.info(f"🌐 Access your data at: https://waveformdata.work/views/")
    
    return True

if __name__ == "__main__":
    success = upload_views_to_cdn()
    exit(0 if success else 1)