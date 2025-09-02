#!/usr/bin/env python3
"""Configure CORS settings for Cloudflare R2 bucket."""

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
import json

def configure_r2_cors():
    """Configure CORS settings for R2 bucket to allow dashboard access."""
    
    # Load environment variables from root directory
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / '.env.local'
    
    if not env_file.exists():
        print(f"❌ Environment file not found: {env_file}")
        return False
    
    load_dotenv(env_file)
    
    # R2 configuration
    try:
        r2 = boto3.client(
            's3',
            endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
        print("✅ Connected to Cloudflare R2")
    except Exception as e:
        print(f"❌ Failed to connect to R2: {e}")
        return False
    
    bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
    
    # CORS configuration
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedOrigins': [
                    'http://localhost:3000',
                    'http://localhost:3001', 
                    'http://localhost:3002',
                    'http://localhost:3003',
                    'http://localhost:3004',
                    'https://mbon-dash-2025.vercel.app',
                    'https://mbon-dash-2025-*.vercel.app'
                ],
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    
    try:
        # Set CORS configuration
        r2.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        print(f"✅ CORS configured successfully for bucket: {bucket_name}")
        
        # Verify CORS configuration
        cors_response = r2.get_bucket_cors(Bucket=bucket_name)
        print("\n📋 Current CORS configuration:")
        for rule in cors_response['CORSConfiguration']['CORSRules']:
            print(f"   • Allowed Origins: {', '.join(rule['AllowedOrigins'])}")
            print(f"   • Allowed Methods: {', '.join(rule['AllowedMethods'])}")
            print(f"   • Max Age: {rule['MaxAgeSeconds']} seconds")
        
        print(f"\n🌐 You can now access files from localhost!")
        print(f"💡 Test: curl -H 'Origin: http://localhost:3004' https://waveformdata.work/views/stations.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to configure CORS: {e}")
        print("\n💡 Alternative: You can configure CORS manually in Cloudflare dashboard:")
        print("   1. Go to R2 → Your Bucket → Settings")
        print("   2. Add CORS policy:")
        print(json.dumps(cors_configuration, indent=2))
        return False

if __name__ == "__main__":
    configure_r2_cors()