# CDN Setup Guide

How to set up Cloudflare R2 for storing and serving data files.

## Why Cloudflare R2?

- **Cost-effective**: No egress fees (unlike AWS S3)
- **Fast global delivery**: Built on Cloudflare's edge network
- **S3-compatible**: Works with existing S3 tools
- **Simple setup**: Public URLs available immediately

## Step 1: Create R2 Bucket

1. **Sign up/Login** at [dash.cloudflare.com](https://dash.cloudflare.com)
2. Navigate to **R2** in the sidebar
3. Click **Create bucket**
   - Name: `mbon-data` (or your preference)
   - Location: Automatic
   - Click **Create bucket**

## Step 2: Enable Public Access

1. In your R2 bucket, go to **Settings** tab
2. Under **Public Access**, click **Enable Public Development URL**
3. You'll get a URL like: `https://pub-[id].r2.dev`
4. Save this URL - you'll use it in your `.env.local` file

## Step 3: Upload Data Files

### Directory Structure on CDN

Mirror your local `data/cdn/` structure:

```
/processed/              # Dashboard JSON files
  detections.json
  environmental.json
  deployment_metadata.json
  stations.json
  species.json
  metadata.json

/raw-data/              # Raw Excel files (114MB+)
  /2018/
    Master_Manual_[STATION]_2h_2018.xlsx
    Master_[STATION]_Temp_2018.xlsx
    Master_[STATION]_Depth_2018.xlsx
  /2021/
    [Same structure for 2021]
  /indices/raw/
    Acoustic_Indices_9m_FullBW_v1.csv
  1_Montie Lab_metadata_deployments_2017 to 2022.xlsx
```

### Upload Methods

#### Option 1: Web Dashboard (Simple)
1. Go to your R2 bucket
2. Click **Upload**
3. Create folders: `processed/` and `raw-data/`
4. Upload files maintaining structure

#### Option 2: Command Line (Advanced)
Using rclone or AWS CLI configured for R2:

```bash
# Configure rclone for R2
rclone config

# Upload processed data
rclone copy data/cdn/ r2:mbon-data/processed/

# Upload raw data
rclone copy data/raw-data/ r2:mbon-data/raw-data/
```

## Step 4: Configure Dashboard

Update your `.env.local` file:

```bash
NEXT_PUBLIC_DATA_URL=https://pub-[your-id].r2.dev
```

The dashboard will now load data from:
- `https://pub-[your-id].r2.dev/processed/detections.json`
- `https://pub-[your-id].r2.dev/processed/stations.json`
- etc.

## Step 5: Test Data Loading

```bash
# Test that files are accessible
curl https://pub-[your-id].r2.dev/processed/metadata.json

# Should return JSON data
```

## Optional: Custom Domain

If you need a custom domain later:

### Subdomain Approach (Recommended)
1. Add subdomain to Cloudflare: `data.yourdomain.com`
2. In your DNS provider, add CNAME:
   - Name: `data`
   - Value: `[cloudflare-target]`
3. Configure R2 custom domain in Settings

### Full Domain Migration
Only if you want to move entire domain to Cloudflare:
1. Transfer nameservers to Cloudflare
2. Configure custom domain in R2 Settings
3. Add CNAME record in Cloudflare DNS

## Data Update Workflow

When you need to update data:

1. **Process locally**:
   ```bash
   npm run build-data
   ```

2. **Upload to CDN**:
   - Upload files from `data/cdn/` to `r2:mbon-data/processed/`
   - Files are immediately available

3. **No deployment needed**:
   - Dashboard automatically uses latest data from CDN
   - Users get updates on next page load

## Monitoring Usage

In Cloudflare dashboard:
- View request analytics
- Monitor bandwidth usage
- Check file access patterns
- Set up alerts if needed

## Troubleshooting

### CORS Issues
If you get CORS errors:
1. Go to R2 bucket settings
2. Add CORS rule allowing your domain
3. Or use wildcard `*` for development

### 404 Errors
- Check file paths match exactly (case-sensitive)
- Verify files uploaded to correct folders
- Ensure public access is enabled

### Slow Loading
- Check if files are compressed (R2 auto-gzips)
- Consider splitting large files
- Use browser caching headers

## Cost Estimation

R2 Pricing (as of 2024):
- **Storage**: $0.015/GB/month
- **Operations**: $0.36/million requests
- **Egress**: FREE (main advantage)

For MBON project (~200MB data):
- Storage: ~$0.003/month
- Requests: Negligible for research use
- **Total**: Essentially free for this scale