#!/bin/bash

# Export Marimo Notebooks to HTML
# Usage: ./scripts/export-notebooks.sh [notebook_name]
# If no notebook_name provided, exports all notebooks

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}📓 Exporting Marimo Notebooks to HTML${NC}"
    echo "==========================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Notebook directory
NOTEBOOKS_DIR="python/scripts/notebooks"
HTML_DIR="$NOTEBOOKS_DIR/__marimo__"

# Ensure HTML directory exists
mkdir -p "$HTML_DIR"

export_notebook() {
    local notebook_file="$1"
    local filename=$(basename "$notebook_file" .py)
    local html_output="$HTML_DIR/${filename}.html"
    
    echo "Exporting $notebook_file..."
    
    if uv run --project python marimo export html "$notebook_file" -o "$html_output" --force; then
        print_success "Exported: ${filename}.html"
        return 0
    else
        echo "❌ Failed to export: $notebook_file"
        return 1
    fi
}

print_header

# Check if specific notebook was requested
if [ $# -eq 1 ]; then
    NOTEBOOK_NAME="$1"
    NOTEBOOK_FILE="$NOTEBOOKS_DIR/${NOTEBOOK_NAME}.py"
    
    if [ ! -f "$NOTEBOOK_FILE" ]; then
        NOTEBOOK_FILE="$NOTEBOOKS_DIR/$NOTEBOOK_NAME"
        if [ ! -f "$NOTEBOOK_FILE" ]; then
            echo "❌ Notebook not found: $NOTEBOOK_NAME"
            echo "Available notebooks:"
            ls "$NOTEBOOKS_DIR"/*.py | xargs -n1 basename | sed 's/.py$//'
            exit 1
        fi
    fi
    
    export_notebook "$NOTEBOOK_FILE"
else
    # Export all notebooks
    print_info "Exporting all notebooks in $NOTEBOOKS_DIR..."
    
    exported_count=0
    failed_count=0
    
    for notebook_file in "$NOTEBOOKS_DIR"/*.py; do
        if [ -f "$notebook_file" ]; then
            if export_notebook "$notebook_file"; then
                exported_count=$((exported_count + 1))
            else
                failed_count=$((failed_count + 1))
            fi
        fi
    done
    
    echo ""
    print_success "Export complete: $exported_count successful, $failed_count failed"
    
    if [ $exported_count -gt 0 ]; then
        print_info "HTML files saved to: $HTML_DIR/"
        print_info "Next step: Run './scripts/build-dashboard.sh' to update the web dashboard"
    fi
fi