#!/bin/bash

# Complete Rebuild Pipeline
# Exports all notebooks to HTML, builds dashboard, and optionally deploys

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔄 Complete Rebuild Pipeline${NC}"
    echo "=============================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    echo "Usage: ./scripts/full-rebuild.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --deploy    Also deploy data views to CDN after rebuild"
    echo "  --help      Show this help message"
    echo ""
    echo "This script performs a complete rebuild:"
    echo "  1. Export all marimo notebooks to HTML"
    echo "  2. Build dashboard with updated HTML files"
    echo "  3. Optionally deploy data views to CDN"
}

# Parse command line arguments
DEPLOY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --deploy)
            DEPLOY=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Change to project root
cd "$(git rev-parse --show-toplevel)"

print_header

# Step 1: Export notebooks
print_info "Step 1: Exporting all marimo notebooks to HTML..."
if ! ./scripts/export-notebooks.sh; then
    print_error "Failed to export notebooks"
    exit 1
fi

echo ""

# Step 2: Build dashboard
print_info "Step 2: Building dashboard with updated notebooks..."
if ! ./scripts/build-dashboard.sh; then
    print_error "Failed to build dashboard"
    exit 1
fi

echo ""

# Step 3: Deploy (optional)
if [ "$DEPLOY" = true ]; then
    print_info "Step 3: Deploying data views to CDN..."
    cd dashboard
    if npm run data:deploy; then
        print_success "Data views deployed to CDN"
    else
        print_error "Failed to deploy data views"
        exit 1
    fi
    cd ..
    echo ""
fi

# Summary
print_success "🎉 Complete rebuild finished!"
echo ""
print_info "What was updated:"
print_info "  ✓ All marimo notebooks exported to HTML"
print_info "  ✓ Dashboard rebuilt with latest notebook content"
if [ "$DEPLOY" = true ]; then
    print_info "  ✓ Data views deployed to CDN"
fi

echo ""
print_info "Next steps:"
print_info "  - Review changes with: git status"
print_info "  - Start dashboard: cd dashboard && npm run dev"
if [ "$DEPLOY" = false ]; then
    print_info "  - Deploy data views: ./scripts/full-rebuild.sh --deploy"
fi