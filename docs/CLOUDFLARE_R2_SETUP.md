# Cloudflare R2 Setup Guide for MBON Dashboard

## Step 1: Create Cloudflare Account & R2 Bucket

1. **Sign up/Login** at https://dash.cloudflare.com
2. Navigate to **R2** in the sidebar
3. Click **Create bucket**
   - Name: `mbon-data` (or your preference)
   - Location: Automatic
   - Click **Create bucket**

## Step 2: Configure Public Access

1. In your R2 bucket, go to **Settings** tab
2. Under **Public Access**, click **Enable Public Development URL**
3. You'll get a URL like: `https://mbon-usc-2025.1234abcd.r2.dev`
4. This R2.dev URL is perfect for development and most production use cases

### Optional: Custom Domain Setup (Later)
If you eventually need a custom domain, you have options:

#### Option A: Subdomain Approach (Recommended)
Keep your main domain hosting intact and add only a subdomain to Cloudflare:

1. **In Cloudflare**: Go to **Websites** → **Add a site** → Enter just your subdomain: `data.yourdomain.com`
2. **In your current DNS provider** (Bluehost): Add a CNAME record:
   ```
   Type: CNAME
   Name: data
   Value: [cloudflare-target-from-step-1]
   ```
3. **In Cloudflare R2**: Go to bucket Settings → Public Access → Connect Domain → `data.yourdomain.com`

This keeps your main website and email exactly where they are!

#### Option B: Separate Domain
- Purchase a domain like `mbon-data.com` (~$10/year)
- Point entire domain to Cloudflare
- No impact on your existing domain setup

## Step 3: Upload Data Files

### Option A: Web Dashboard
1. Click **Objects** tab in your bucket
2. Click **Upload** 
3. Upload these files from `public/data/`:
   - `detections.json`
   - `environmental.json`
   - `acoustic.json`
   - `stations.json`
   - `species.json`
   - `metadata.json`

### Option B: Command Line (Wrangler)
```bash
# Install Cloudflare CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Upload files
wrangler r2 object put mbon-data/detections.json --file=public/data/detections.json
wrangler r2 object put mbon-data/environmental.json --file=public/data/environmental.json
wrangler r2 object put mbon-data/acoustic.json --file=public/data/acoustic.json
wrangler r2 object put mbon-data/stations.json --file=public/data/stations.json
wrangler r2 object put mbon-data/species.json --file=public/data/species.json
wrangler r2 object put mbon-data/metadata.json --file=public/data/metadata.json
```

## Step 4: Get Your Public URLs

Your files will be available at:
- `https://mbon-usc-2025.1234abcd.r2.dev/detections.json`
- `https://mbon-usc-2025.1234abcd.r2.dev/environmental.json`
- etc.

(Replace with your actual R2.dev URL from Step 2)

## Step 5: Configure CORS (Important!)

1. In R2 bucket settings, find **CORS Policy**
2. Add this configuration:

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

For production, replace `"*"` with your actual domain:
```json
"AllowedOrigins": ["https://yourdomain.com", "http://localhost:3000"]
```

## Step 6: Update Your Next.js App

Create `.env.local`:
```bash
NEXT_PUBLIC_DATA_URL=https://mbon-usc-2025.1234abcd.r2.dev
```
(Replace with your actual R2.dev URL)

## Step 7: Test Access

```bash
# Test that files are accessible (replace with your actual URL)
curl https://mbon-usc-2025.1234abcd.r2.dev/metadata.json

# Should return your JSON data
```

## Pricing

**R2 Free Tier includes:**
- 10 GB storage/month
- 10 million requests/month
- Unlimited bandwidth (egress)

Your ~50MB of data will easily fit in the free tier!

## Notes

- Files are cached at Cloudflare edge locations globally
- No bandwidth charges (unlike S3)
- Automatic compression for JSON files
- Can set cache headers for better performance