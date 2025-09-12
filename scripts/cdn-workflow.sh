#!/bin/bash

# MBON Dashboard CDN Workflow Helper
# Provides easy commands for CDN management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}🌊 MBON Dashboard CDN Workflow${NC}"
    echo "========================================"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Commands
cmd_help() {
    print_header
    echo ""
    echo "Available commands:"
    echo ""
    echo "  upload    - Upload view files to CDN"
    echo "  test      - Test CDN connectivity"
    echo "  deploy    - Generate views and upload to CDN"
    echo "  dev       - Start dashboard development server"
    echo "  status    - Check CDN and local setup status"
    echo "  help      - Show this help message"
    echo ""
}

cmd_upload() {
    print_header
    echo "Uploading view files to CDN..."
    npm run cdn:upload
    print_success "Upload complete!"
}

cmd_test() {
    print_header
    echo "Testing CDN connectivity..."
    npm run cdn:test
    print_success "CDN test complete!"
}

cmd_deploy() {
    print_header
    echo "Generating views and deploying to CDN..."
    npm run data:deploy
    print_success "Deployment complete!"
}

cmd_dev() {
    print_header
    echo "Starting dashboard development server..."
    npm run dev
}

cmd_status() {
    print_header
    echo "Checking CDN and local setup status..."
    
    echo ""
    echo "📡 Testing CDN connectivity..."
    if npm run cdn:test > /dev/null 2>&1; then
        print_success "CDN is accessible"
    else
        print_error "CDN is not accessible"
    fi
    
    echo ""
    echo "📁 Checking local view files..."
    if [ -d "data/views" ] && [ -n "$(ls -A data/views 2>/dev/null)" ]; then
        VIEW_COUNT=$(ls data/views/*.json 2>/dev/null | wc -l)
        print_success "Found $VIEW_COUNT view files locally"
    else
        print_warning "No view files found locally"
    fi
    
    echo ""
    echo "🔧 Environment check..."
    if [ -f "dashboard/.env.local" ]; then
        print_success "Environment file exists"
    else
        print_error "Environment file missing"
    fi
}

# Main command handler
case "${1:-help}" in
    upload)     cmd_upload ;;
    test)       cmd_test ;;
    deploy)     cmd_deploy ;;
    dev)        cmd_dev ;;
    status)     cmd_status ;;
    help)       cmd_help ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac