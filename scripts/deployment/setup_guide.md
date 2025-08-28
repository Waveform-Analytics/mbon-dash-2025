# CDN Deployment Setup Guide

This guide explains how to set up automated CDN deployment for MBON dashboard views.

## Local Development (No Setup Required)

By default, the system runs in local development mode:

```bash
# These are the default values for local development
CDN_PROVIDER=local_dev
CDN_BASE_URL=http://localhost:3000
```

In this mode:
- Files are served from the `public/views/` directory
- No CDN upload occurs
- Perfect for development and testing

## Production CDN Setup

### Option 1: Cloudflare R2 (Recommended)

Cloudflare R2 is cost-effective and performant for static assets.

1. **Create a Cloudflare R2 bucket:**
   - Go to https://dash.cloudflare.com/
   - Navigate to R2 Object Storage
   - Create a new bucket (e.g., `mbon-dashboard-data`)
   - Configure public access for the bucket

2. **Get R2 API credentials:**
   - Go to "Manage R2 API tokens"
   - Create a new API token with read/write permissions for your bucket
   - Note down: Account ID, Access Key ID, Secret Access Key

3. **Configure environment variables:**
   ```bash
   # In .env.local (for local testing) or production environment
   CDN_PROVIDER=cloudflare_r2
   CDN_BASE_URL=https://pub-YOUR-ACCOUNT-ID.r2.dev
   CDN_ACCOUNT_ID=your-cloudflare-account-id
   CDN_ACCESS_KEY_ID=your-r2-access-key-id
   CDN_SECRET_ACCESS_KEY=your-r2-secret-access-key
   CDN_BUCKET_NAME=your-bucket-name
   ```

4. **Install boto3 for R2 API access:**
   ```bash
   uv add boto3
   ```

### Option 2: AWS S3

1. **Create an S3 bucket:**
   - Configure for static website hosting
   - Set up appropriate CORS and bucket policies for public read access

2. **Configure AWS credentials:**
   ```bash
   # In .env.local or production environment
   CDN_PROVIDER=aws_s3
   CDN_BASE_URL=https://your-bucket.s3.amazonaws.com
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   CDN_BUCKET_NAME=your-bucket-name
   AWS_REGION=us-east-1
   ```

3. **Install boto3:**
   ```bash
   uv add boto3
   ```

## Deployment Commands

### Full Deployment Pipeline
```bash
# Generate views, upload to CDN, and validate
npm run deploy

# Or run the Python script directly:
uv run scripts/deployment/full_deploy.py
```

### Check What Would Be Deployed
```bash
# See what files would be uploaded without actually deploying
uv run scripts/deployment/full_deploy.py --check-only
```

### Dry Run
```bash
# Test the deployment process without uploading files
uv run scripts/deployment/full_deploy.py --dry-run
```

### Generate Views Only
```bash
# Just generate the view files locally
npm run generate-views
```

## Security Best Practices

### Environment Variables
- **Never commit CDN credentials to git**
- Use `.env.local` for local development
- Use secure environment variable management in production (e.g., Vercel environment variables)

### Access Permissions
- **Cloudflare R2**: Use API tokens with minimal required permissions (read/write to specific bucket only)
- **AWS S3**: Use IAM users with policies restricted to the specific bucket

### Example IAM Policy for S3:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/views/*"
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **"Missing credentials" error**
   - Check that all required environment variables are set
   - Verify credentials are correct and have proper permissions

2. **"boto3 not found" error**
   - Install boto3: `uv add boto3`

3. **Upload timeout**
   - Check network connectivity
   - Verify CDN endpoint URL is correct

4. **Permission denied**
   - Verify API credentials have write access to the bucket
   - Check bucket policies allow uploads

### Debug Mode
```bash
# Run deployment with verbose output
uv run scripts/deployment/full_deploy.py --dry-run
```

### Validation
The deployment script automatically validates uploads by:
- Checking file accessibility via HTTP requests
- Validating JSON structure
- Measuring response times
- Comparing file hashes

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Deploy to CDN
  env:
    CDN_PROVIDER: cloudflare_r2
    CDN_BASE_URL: ${{ secrets.CDN_BASE_URL }}
    CDN_ACCOUNT_ID: ${{ secrets.CDN_ACCOUNT_ID }}
    CDN_ACCESS_KEY_ID: ${{ secrets.CDN_ACCESS_KEY_ID }}
    CDN_SECRET_ACCESS_KEY: ${{ secrets.CDN_SECRET_ACCESS_KEY }}
    CDN_BUCKET_NAME: ${{ secrets.CDN_BUCKET_NAME }}
  run: npm run deploy
```

### Vercel Deployment
Set environment variables in the Vercel dashboard:
- CDN_PROVIDER
- CDN_BASE_URL
- CDN_ACCOUNT_ID
- CDN_ACCESS_KEY_ID
- CDN_SECRET_ACCESS_KEY
- CDN_BUCKET_NAME