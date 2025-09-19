#!/bin/bash
# Helper script to activate the Python environment for this project

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Change to project root first
if ! cd "$(git rev-parse --show-toplevel)" 2>/dev/null; then
    print_error "This script must be run from within the git repository"
    exit 1
fi

PROJECT_ROOT="$(pwd)"
print_info "Using project root: $PROJECT_ROOT"

# Verify we're in the correct project
if [ ! -f "python/pyproject.toml" ]; then
    print_error "Python project not found - are you in the correct directory?"
    print_error "Expected to find: python/pyproject.toml"
    exit 1
fi

print_info "Activating Python environment..."

# Check if we're already in the environment  
if [[ "$VIRTUAL_ENV" == *"mbon-dash-2025/python/.venv"* ]]; then
    print_success "Python environment already activated!"
    return 0 2>/dev/null || exit 0
fi

# Change to python directory and verify .venv exists
cd python
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found at: $PROJECT_ROOT/python/.venv"
    print_info "Run 'uv sync' from the python directory to create it"
    exit 1
fi

# Activate the virtual environment
if ! source .venv/bin/activate; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Return to project root
cd "$PROJECT_ROOT"

print_success "Python environment activated!"
print_info "Current directory: $(pwd)"
print_info "To run marimo: marimo edit python/scripts/notebooks/[notebook].py"
print_info "To deactivate: deactivate"
