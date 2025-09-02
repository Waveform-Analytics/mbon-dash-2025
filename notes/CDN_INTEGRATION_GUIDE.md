# CDN Integration Guide for MBON Dashboard

This guide covers the complete setup and implementation of Cloudflare R2 CDN integration for the MBON Marine Biodiversity Dashboard.

## Overview

The dashboard uses a **CDN-first architecture** where:
- **Python backend** processes raw data and generates optimized view files
- **Cloudflare R2** stores and serves these view files globally
- **Next.js frontend** loads data from CDN with local API fallback
- **Custom domain** `waveformdata.work` provides professional access

> **Note on Environment Variables**: This project uses a single `.env.local` file at the root level that's shared between Python scripts and Next.js. While Next.js typically expects `.env.local` in the `dashboard/` folder, the shared approach works if you configure both environments to read from the root.

## Architecture

```
Raw Data (Excel/CSV) → Python Processing → Optimized Views → Cloudflare R2 → Dashboard
     (50+ files)         (Heavy compute)      (JSON files)      (Global CDN)    (Fast UI)
```

### Benefits
- **Global Performance**: Sub-second loading from anywhere in the world
- **Scalability**: Automatic scaling for traffic spikes
- **Cost Effective**: Pay only for storage and bandwidth used
- **Professional**: Custom domain for data access
- **Reliability**: 99.9% uptime with automatic failover

## Prerequisites

### 1. Cloudflare Account Setup
- [Sign up for Cloudflare](https://dash.cloudflare.com/sign-up)
- Verify your email and set up your account
- Navigate to R2 Object Storage in your dashboard

### 2. R2 Bucket Creation
1. Go to **R2 Object Storage** in Cloudflare dashboard
2. Click **Create bucket**
3. Name it `mbon-usc-2025`
4. Leave location as "Automatic" for global distribution
5. Click **Create bucket**

### 3. Custom Domain Configuration
1. In R2 dashboard, select your bucket
2. Go to **Settings** tab
3. Under **Public Access**, click **Connect Domain**
4. Enter `waveformdata.work` (must be a domain in your Cloudflare account)
5. R2 will automatically configure the domain for public access

### 4. Generate R2 API Credentials
1. In R2 dashboard, click **Manage R2 API tokens**
2. Click **Create API token**
3. Configure permissions:
   - **Permissions**: Object Read & Write
   - **Specify bucket**: `mbon-usc-2025`
   - **TTL**: Permanent (or set expiration as needed)
4. Click **Create API Token**
5. **IMPORTANT**: Save the Access Key ID and Secret Access Key immediately (shown only once)

---

## 🔍 CHECKPOINT 1: Verify Cloudflare Setup

Before proceeding, verify your Cloudflare setup is complete:

### Test 1: Check Custom Domain
```bash
# This should return HTTP headers (200 or 404 is fine at this stage)
curl -I https://waveformdata.work/

# Expected output includes headers like:
# HTTP/2 404  (or 200 if you have content)
# server: cloudflare
# cf-ray: [some-id]
```

### Test 2: Verify Domain Points to R2
```bash
# Check DNS resolution
nslookup waveformdata.work

# Should show Cloudflare IPs
```

### Test 3: R2 Bucket Exists
- Go to Cloudflare Dashboard → R2
- Confirm bucket `mbon-usc-2025` is listed
- Confirm custom domain shows as "Connected"

✅ **If all tests pass**: Continue to Environment Configuration
❌ **If any test fails**: Review Prerequisites section and fix issues

---

## Required Credentials

You'll need these values from your Cloudflare dashboard:

### Account Information
- **Account ID**: Found in Account Home → Account ID
- **Email**: Your Cloudflare account email

### API Access
- **Access Key ID**: R2 Object Storage → Manage R2 API tokens
- **Secret Access Key**: Generated when creating the access key
- **Endpoint URL**: `https://{ACCOUNT_ID}.r2.cloudflarestorage.com`

### Custom Domain
- **Public URL**: `https://waveformdata.work`
- **Bucket**: `mbon-usc-2025`

## Environment Configuration

### 1. Create Environment File

Create `.env.local` at the **project root**:

```bash
# Cloudflare R2 Configuration
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key_id_here
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_access_key_here
CLOUDFLARE_R2_BUCKET_NAME=mbon-usc-2025
CLOUDFLARE_R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com

# Dashboard Configuration
NEXT_PUBLIC_CDN_BASE_URL=https://waveformdata.work
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here

# Optional: Development overrides
NODE_ENV=development
```

### 2. Configure Next.js to Read from Root

Since Next.js expects `.env.local` in the `dashboard/` folder, you need to tell it to read from the root. Update `dashboard/next.config.js`:

```javascript
const path = require('path');
const dotenv = require('dotenv');

// Load root-level .env.local file
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

/** @type {import('next').NextConfig} */
const nextConfig = {
  // your existing config
}

module.exports = nextConfig;
```

Also install dotenv in your dashboard:
```bash
cd dashboard/
npm install dotenv
```

### 3. File Structure

```
mbon-dash-2025/
├── .env.local          ← Single environment file here
├── .gitignore          ← Must include .env.local
├── dashboard/
├── python/
└── data/
```

**Benefits of Single File**:
- One place to manage all credentials
- No duplication of environment variables
- Both Python and Next.js read from same source
- Easier deployment configuration

---

## 🔍 CHECKPOINT 2: Verify Environment Setup

After creating `.env.local`, test that credentials are set correctly:

### Test 1: Check File Exists and Has Content
```bash
# Verify file exists at root
ls -la .env.local

# Check it has the required variables (without showing secrets)
grep "CLOUDFLARE_R2" .env.local | cut -d= -f1

# Should output:
# CLOUDFLARE_R2_ACCOUNT_ID
# CLOUDFLARE_R2_ACCESS_KEY_ID
# CLOUDFLARE_R2_SECRET_ACCESS_KEY
# CLOUDFLARE_R2_BUCKET_NAME
# CLOUDFLARE_R2_ENDPOINT
```

### Test 2: Verify Python Can Read Environment
```bash
cd python/
uv run -c "
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('../.env.local')
print(f'Environment file exists: {env_path.exists()}')

load_dotenv(env_path)
required = ['CLOUDFLARE_R2_ACCOUNT_ID', 'CLOUDFLARE_R2_ACCESS_KEY_ID', 
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY', 'CLOUDFLARE_R2_BUCKET_NAME', 
            'CLOUDFLARE_R2_ENDPOINT']
            
for var in required:
    value = os.getenv(var)
    if value:
        print(f'✅ {var}: Set ({len(value)} chars)')
    else:
        print(f'❌ {var}: Not set')
"
```

### Test 3: Test R2 Connection with Credentials
```bash
cd python/
uv run -c "
import boto3
import os
from dotenv import load_dotenv

load_dotenv('../.env.local')

try:
    s3 = boto3.client('s3',
        endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
        aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
        region_name='auto'
    )
    
    # Try to list buckets
    response = s3.list_buckets()
    print('✅ Successfully connected to R2!')
    print(f'Found {len(response[\"Buckets\"])} bucket(s)')
    
    # Try to access our specific bucket
    bucket = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
    response = s3.head_bucket(Bucket=bucket)
    print(f'✅ Bucket {bucket} is accessible!')
    
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

✅ **If all tests pass**: Continue to Implementation Steps
❌ **If any test fails**: Check your .env.local file and credentials

---

## Implementation Steps

### Step 1: Install Dependencies

The project already includes `boto3` in `python/pyproject.toml`:

```toml
dependencies = [
    "boto3>=1.28.0",
    "python-dotenv>=1.0.0",
    # ... other dependencies
]
```

Install with:
```bash
cd python/
uv sync
```

---

## 🔍 CHECKPOINT 3: Verify Python Dependencies

```bash
cd python/

# Check boto3 is installed
uv run -c "import boto3; print(f'✅ boto3 version: {boto3.__version__}')"

# Check python-dotenv is installed  
uv run -c "import dotenv; print('✅ python-dotenv installed')"

# Quick S3 client test
uv run -c "
import boto3
s3 = boto3.client('s3', endpoint_url='https://test.r2.cloudflarestorage.com')
print('✅ Can create S3 client for R2')
"
```

✅ **If all tests pass**: Continue to Step 2
❌ **If any test fails**: Run `uv sync` again

---

### Step 2: Create CDN Upload Script

Create `python/scripts/upload_to_cdn.py`:

```python
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
```

---

## 🔍 CHECKPOINT 4: Test Upload Script (Dry Run)

Before uploading real data, test the script can connect:

### Test 1: Script Runs Without Errors
```bash
cd python/
# Create a test file to upload
echo '{"test": "data"}' > ../data/views/test.json

# Run upload script
uv run scripts/upload_to_cdn.py

# Check output for success message
```

### Test 2: Verify File Was Uploaded
```bash
# Check via curl
curl https://waveformdata.work/views/test.json

# Should return: {"test": "data"}
```

### Test 3: Clean Up Test File
```bash
# Remove local test file
rm data/views/test.json

# Optionally delete from R2 via dashboard or script
```

✅ **If all tests pass**: Continue to Step 3
❌ **If upload fails**: Check error messages and verify credentials

---

### Step 3: Update Frontend Data Loading

Modify `dashboard/src/lib/data/useViewData.ts` to support CDN loading:

```typescript
/**
 * Hook for loading view data from CDN or local API
 */

import { useState, useEffect } from 'react';

interface UseViewDataResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useViewData<T>(viewName: string): UseViewDataResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        console.log(`useViewData: Loading ${viewName}`);
        setLoading(true);
        setError(null);
        
        // Try CDN first, fallback to local API
        const cdnUrl = process.env.NEXT_PUBLIC_CDN_BASE_URL;
        const apiUrl = `/api/views/${viewName}`;
        
        let response: Response;
        let dataSource: 'cdn' | 'local' = 'local';
        
        if (cdnUrl) {
          // Try CDN first
          try {
            const cdnResponse = await fetch(`${cdnUrl}/views/${viewName}`);
            if (cdnResponse.ok) {
              response = cdnResponse;
              dataSource = 'cdn';
              console.log(`useViewData: Loading from CDN: ${cdnUrl}/views/${viewName}`);
            } else {
              throw new Error(`CDN returned ${cdnResponse.status}`);
            }
          } catch (cdnError) {
            console.warn(`CDN failed, falling back to local API:`, cdnError);
            response = await fetch(apiUrl);
            dataSource = 'local';
          }
        } else {
          // Use local API only
          response = await fetch(apiUrl);
          dataSource = 'local';
        }
        
        if (!response.ok) {
          throw new Error(`Failed to load ${viewName}: ${response.statusText}`);
        }
        
        const jsonData = await response.json();
        console.log(`useViewData: Successfully loaded ${viewName} from ${dataSource}:`, {
          dataType: typeof jsonData,
          hasData: !!jsonData,
          keys: jsonData ? Object.keys(jsonData) : 'no data'
        });
        setData(jsonData);
      } catch (err) {
        console.error(`useViewData: Error loading ${viewName}:`, err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [viewName]);

  return { data, loading, error };
}
```

---

## 🔍 CHECKPOINT 5: Test Frontend CDN Integration

### Test 1: Verify Next.js Config Works
```bash
cd dashboard/

# Test that Next.js can read root .env.local
npm run dev

# Check browser console for:
# - No errors about missing environment variables
# - Look for "Loading from CDN" messages in console
```

### Test 2: Test CDN Loading in Browser
```javascript
// In browser console at http://localhost:3000
// Check if CDN URL is set
console.log('CDN URL:', process.env.NEXT_PUBLIC_CDN_BASE_URL);
// Should output: https://waveformdata.work

// Test fetch from CDN
fetch('https://waveformdata.work/views/stations.json')
  .then(r => r.json())
  .then(data => console.log('CDN data:', data))
  .catch(err => console.error('CDN error:', err));
```

### Test 3: Verify Fallback Works
```bash
# Temporarily rename CDN URL to test fallback
# In .env.local, comment out NEXT_PUBLIC_CDN_BASE_URL
# Restart Next.js and verify it falls back to local API
```

✅ **If all tests pass**: Continue to Step 4
❌ **If CDN loading fails**: Check browser console and network tab

---

### Step 4: Update Package.json Scripts

Add CDN operations to your root `package.json`:

```json
{
  "scripts": {
    "// CDN Operations": "========================================",
    "cdn:upload": "cd python && uv run scripts/upload_to_cdn.py",
    "cdn:upload-views": "npm run data:views && npm run cdn:upload",
    "cdn:test": "curl -I https://waveformdata.work/views/stations.json",
    "cdn:verify": "cd python && uv run scripts/test_cdn_connection.py",
    
    "// Data Processing": "========================================",
    "data:process": "npm run data:test && npm run data:views",
    "data:deploy": "npm run data:process && npm run cdn:upload",
    
    "// Development": "========================================",
    "dev": "concurrently -n \"DASHBOARD,INFO\" -c \"cyan,green\" \"npm run dev:dashboard\" \"echo '\\n🌊 MBON Dashboard started at http://localhost:3000\\n'\"",
    "dev:dashboard": "cd dashboard && npm run dev"
  }
}
```

### Step 5: Create CDN Test Script

Create `python/scripts/test_cdn_connection.py`:

```python
#!/usr/bin/env python3
"""Test Cloudflare R2 connection and list bucket contents."""

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv

def test_cdn_connection():
    """Test connection to Cloudflare R2 and list bucket contents."""
    
    # Load environment variables from root directory
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / '.env.local'
    
    if not env_file.exists():
        print("❌ Environment file not found. Please create .env.local at project root.")
        return False
    
    load_dotenv(env_file)
    
    # Test connection
    try:
        r2 = boto3.client(
            's3',
            endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
            aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
        
        bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
        
        # Test bucket access
        response = r2.list_objects_v2(Bucket=bucket_name, MaxKeys=10)
        
        print("✅ Successfully connected to Cloudflare R2!")
        print(f"📦 Bucket: {bucket_name}")
        print(f"🔗 Endpoint: {os.getenv('CLOUDFLARE_R2_ENDPOINT')}")
        print(f"🌐 Public URL: {os.getenv('NEXT_PUBLIC_CDN_BASE_URL', 'Not set')}")
        
        # List recent objects
        if 'Contents' in response:
            print(f"\n📁 Recent objects in bucket:")
            for obj in response['Contents']:
                print(f"   • {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("\n📁 Bucket is empty")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to R2: {e}")
        return False

if __name__ == "__main__":
    test_cdn_connection()
```

---

## 🔍 CHECKPOINT 6: Verify Complete Integration

### Final Integration Test
```bash
# 1. Generate test view data
cd python/
uv run scripts/generate_views.py  # If you have this script

# 2. Upload to CDN
uv run scripts/upload_to_cdn.py

# 3. Test from dashboard
cd ../dashboard/
npm run dev

# Visit http://localhost:3000 and verify:
# - Data loads without errors
# - Network tab shows requests to waveformdata.work
# - No CORS errors
```

✅ **If all tests pass**: Setup is complete!
❌ **If any test fails**: Review the specific checkpoint that failed

---

## Setup Workflow

### 1. Initial Setup

```bash
# 1. Create environment file at root level
nano .env.local  # Add your Cloudflare credentials

# 2. Test R2 connection
npm run cdn:verify

# 3. Process data and generate views
npm run data:process

# 4. Upload views to R2
npm run cdn:upload

# 5. Test public CDN access
npm run cdn:test
```

### 2. Daily Development

```bash
# Start development (uses local data)
npm run dev

# When you want to update CDN
npm run data:deploy
```

### 3. Production Deployment

```bash
# Process data and deploy to CDN
npm run data:deploy

# Deploy dashboard
cd dashboard/
npm run build
vercel deploy --prod
```

## Troubleshooting

### Common Issues

#### 1. Environment Variables Not Found
```
❌ Environment file not found: /path/to/.env.local
```
**Solution**: 
- Ensure `.env.local` exists at project root
- Make sure `dashboard/next.config.js` is configured to read from root (see Step 2 in Environment Configuration)

#### 2. R2 Connection Failed
```
❌ Failed to connect to R2: An error occurred (InvalidAccessKeyId)
```
**Solution**: Check your access key ID and secret access key in `.env.local`.

#### 3. Bucket Not Found
```
❌ An error occurred (NoSuchBucket) when calling the ListObjectsV2 operation
```
**Solution**: Verify bucket name and ensure it exists in your Cloudflare R2 dashboard.

#### 4. Permission Denied
```
❌ An error occurred (AccessDenied) when calling the PutObject operation
```
**Solution**: Check that your API token has "Object Write" permissions for the bucket.

### Debug Commands

```bash
# Test R2 connection
cd python/
uv run scripts/test_cdn_connection.py

# Check environment variables are loaded
cd python/
uv run -c "import os; from dotenv import load_dotenv; load_dotenv('../.env.local'); print('R2_ENDPOINT:', os.getenv('CLOUDFLARE_R2_ENDPOINT'))"

# List bucket contents using boto3
cd python/
uv run -c "
import boto3
import os
from dotenv import load_dotenv
load_dotenv('../.env.local')
s3 = boto3.client('s3',
    endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'),
    aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
)
response = s3.list_objects_v2(Bucket='mbon-usc-2025', MaxKeys=5)
if 'Contents' in response:
    for obj in response['Contents']:
        print(f\"{obj['Key']} - {obj['Size']} bytes\")
else:
    print('Bucket is empty')
"

# Test public CDN access
curl -I https://waveformdata.work/views/stations.json

# Check if file exists in R2
curl https://waveformdata.work/views/stations.json | head -20
```

## Security Considerations

### 1. Environment File
- **Never commit** `.env.local` to version control
- **Already ignored** by `.gitignore`
- **Use different credentials** for development vs production

### 2. API Permissions
- **Minimal permissions**: Only grant necessary R2 access
- **Read-only tokens**: For dashboard access
- **Write tokens**: Only for upload scripts

### 3. Public Access
- **Views are public**: Anyone can access your data
- **Consider authentication**: For sensitive data in the future
- **Rate limiting**: Cloudflare provides DDoS protection

## Performance Optimization

### 1. Caching Strategy
- **Browser cache**: 1 hour for view files (configured in upload script)
- **CDN cache**: Cloudflare automatically caches at edge locations
- **Cache Purge**: Use Cloudflare dashboard or API to purge cached files after updates

### 2. File Optimization
- **Automatic compression**: Cloudflare provides Brotli/Gzip compression
- **JSON minification**: Remove whitespace in production views
- **Progressive loading**: Load critical data first, details on demand

### 3. R2-Specific Optimizations
- **Direct URL access**: Use custom domain for fastest access
- **Batch uploads**: Upload multiple files in parallel when possible
- **Smart routing**: R2 automatically routes to nearest datacenter

### 4. Monitoring
- **R2 Analytics**: Monitor usage in Cloudflare dashboard → R2 → Analytics
- **Request metrics**: Track requests, bandwidth, and cache hit rates
- **Cost tracking**: Monitor storage and bandwidth costs

## Future Enhancements

### 1. Automated Uploads
- **Git hooks**: Upload on commit
- **CI/CD integration**: Upload on merge to main
- **Scheduled uploads**: Daily/weekly updates

### 2. Advanced Features
- **Version control**: Keep multiple versions of views
- **Rollback capability**: Revert to previous versions
- **A/B testing**: Serve different views to different users

### 3. Analytics
- **Usage tracking**: Monitor which views are accessed most
- **Performance metrics**: Track loading times by region
- **Cost optimization**: Monitor bandwidth usage

## Cost Estimates

### Cloudflare R2 Pricing (as of 2024)
- **Storage**: $0.015 per GB-month (first 10 GB free)
- **Class A operations** (writes): $4.50 per million requests
- **Class B operations** (reads): $0.36 per million requests
- **Data transfer**: Free (no egress fees!)

### Expected Costs for MBON Dashboard
- **Storage**: ~1 GB of view files = Free (under 10 GB)
- **Uploads**: ~100 files per month = Negligible
- **Reads**: ~10,000 requests per month = Negligible
- **Bandwidth**: Unlimited free egress
- **Estimated monthly cost**: < $1

## Support Resources

### Documentation
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)
- [R2 with boto3 Guide](https://developers.cloudflare.com/r2/examples/boto3/)
- [R2 Public Buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)

### Community
- [Cloudflare Community Forums](https://community.cloudflare.com/c/developers/r2/")
- [Cloudflare Discord](https://discord.cloudflare.com)

---

## Quick Reference

### 🎯 Quick Start for Your Current Status

Since you've completed Cloudflare setup (up to line 99), here's your next steps:

```bash
# 1. Run CHECKPOINT 1 to verify Cloudflare setup
curl -I https://waveformdata.work/

# 2. Create .env.local at project root with your credentials
nano .env.local

# 3. Run CHECKPOINT 2 to verify environment setup
cd python/
uv run -c "import os; from dotenv import load_dotenv; load_dotenv('../.env.local'); print('✅ Connected!' if os.getenv('CLOUDFLARE_R2_ENDPOINT') else '❌ No env vars')"

# 4. Configure Next.js (Step 2 in Environment Configuration)
cd dashboard/
npm install dotenv
# Then update next.config.js as shown

# 5. Continue with remaining checkpoints...
```

### Essential Commands
```bash
# Test R2 connection
npm run cdn:verify

# Upload views to R2
npm run cdn:upload

# Process data and deploy to CDN
npm run data:deploy

# Test public CDN access
npm run cdn:test

# Check what's in your bucket
cd python && uv run -c "import boto3, os; from dotenv import load_dotenv; load_dotenv('../.env.local'); s3 = boto3.client('s3', endpoint_url=os.getenv('CLOUDFLARE_R2_ENDPOINT'), aws_access_key_id=os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')); [print(obj['Key']) for obj in s3.list_objects_v2(Bucket='mbon-usc-2025').get('Contents', [])]"
```

### Environment Variables
```bash
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key_id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_access_key
CLOUDFLARE_R2_BUCKET_NAME=mbon-usc-2025
CLOUDFLARE_R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
NEXT_PUBLIC_CDN_BASE_URL=https://waveformdata.work
```

### File Structure
```
mbon-dash-2025/
├── .env.local                    # Shared CDN credentials (root level)
├── .gitignore                    # Must include .env.local
├── python/scripts/
│   ├── upload_to_cdn.py         # Upload script
│   └── test_cdn_connection.py   # Connection test
├── dashboard/
│   ├── next.config.js           # Configure to read root .env.local
│   └── src/lib/data/
│       └── useViewData.ts       # CDN-enabled data loader
└── data/views/                  # Generated view files to upload
```

### Key Differences from AWS S3
- **No ACLs**: Public access configured via custom domain, not ACLs
- **No bucket regions**: R2 uses automatic global distribution
- **Free egress**: No bandwidth charges for downloads
- **S3-compatible API**: Use boto3 with custom endpoint
- **Instant propagation**: No wait time for DNS or CDN propagation

This guide provides everything you need to implement Cloudflare R2 CDN integration. Start with bucket creation and environment setup, test the connection, then implement the upload pipeline.
