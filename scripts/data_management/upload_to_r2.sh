#!/bin/bash
# Batch upload script for MBON processed data
# Make sure you have AWS CLI configured with R2 credentials

set -e  # Exit on any error

# Configuration
BUCKET_NAME="your-r2-bucket-name"
CDN_PATH="processed"
LOCAL_DIR="data/cdn/processed"

echo "🚀 Uploading processed data files to CDN..."

echo "📤 Uploading acoustic.json (2.0 B)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/acoustic.json" "s3://$BUCKET_NAME/$CDN_PATH/acoustic.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading acoustic_indices.json (83.4 MB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/acoustic_indices.json" "s3://$BUCKET_NAME/$CDN_PATH/acoustic_indices.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading deployment_metadata.json (46.6 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/deployment_metadata.json" "s3://$BUCKET_NAME/$CDN_PATH/deployment_metadata.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading detections.json (17.3 MB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/detections.json" "s3://$BUCKET_NAME/$CDN_PATH/detections.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading environmental.json (31.6 MB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/environmental.json" "s3://$BUCKET_NAME/$CDN_PATH/environmental.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading metadata.json (1.4 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/metadata.json" "s3://$BUCKET_NAME/$CDN_PATH/metadata.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading monthly_detections.json (273.0 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/monthly_detections.json" "s3://$BUCKET_NAME/$CDN_PATH/monthly_detections.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading pca_biplot.json (416.6 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/pca_biplot.json" "s3://$BUCKET_NAME/$CDN_PATH/pca_biplot.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading pca_biplot_8khz.json (416.6 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/pca_biplot_8khz.json" "s3://$BUCKET_NAME/$CDN_PATH/pca_biplot_8khz.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading pca_biplot_fullbw.json (416.6 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/pca_biplot_fullbw.json" "s3://$BUCKET_NAME/$CDN_PATH/pca_biplot_fullbw.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading species.json (4.2 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/species.json" "s3://$BUCKET_NAME/$CDN_PATH/species.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading stations.json (6.5 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/stations.json" "s3://$BUCKET_NAME/$CDN_PATH/stations.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "📤 Uploading step1a_raw_data_landscape.json (100.1 KB)..."
aws s3 cp "/Users/michelleweirathmueller/Documents/WORKSPACE/MBON-USC-2025/mbon-dash-2025/data/cdn/processed/step1a_raw_data_landscape.json" "s3://$BUCKET_NAME/$CDN_PATH/step1a_raw_data_landscape.json" --endpoint-url https://your-account-id.r2.cloudflarestorage.com

echo "✅ Upload complete!"
echo "Files should be available at:"
echo "  https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev/processed/"