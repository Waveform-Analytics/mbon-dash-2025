#!/bin/bash

# Build Dashboard with Updated Notebook HTML
# Processes marimo HTML files and creates Next.js pages

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🏗️  Building Dashboard with Notebook Updates${NC}"
    echo "=============================================="
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

# Change to project root
cd "$(git rev-parse --show-toplevel)"

print_header

# Check if HTML files exist
HTML_DIR="python/scripts/notebooks/__marimo__"
if [ ! -d "$HTML_DIR" ] || [ -z "$(ls -A "$HTML_DIR"/*.html 2>/dev/null)" ]; then
    print_error "No HTML files found in $HTML_DIR"
    print_info "Run './scripts/export-notebooks.sh' first to generate HTML files"
    exit 1
fi

print_info "Found HTML files in $HTML_DIR"

# Run the dashboard build script
BUILD_SCRIPT="dashboard/scripts/build-notebooks.js"
if [ ! -f "$BUILD_SCRIPT" ]; then
    print_error "Build script not found: $BUILD_SCRIPT"
    exit 1
fi

print_info "Running dashboard build script..."

cd dashboard
if node scripts/build-notebooks.js; then
    print_success "Dashboard build completed successfully"
    
    echo ""
    print_info "Updated files:"
    print_info "  - Next.js pages: app/analysis/notebooks/"
    print_info "  - Public HTML: public/analysis/notebooks/html/"
    print_info "  - Metadata: public/analysis/notebooks/notebooks.json"
    
    echo ""
    print_info "🚀 Dashboard is ready! Start with 'npm run dev' in the dashboard/ folder"
else
    print_error "Dashboard build failed"
    exit 1
fi