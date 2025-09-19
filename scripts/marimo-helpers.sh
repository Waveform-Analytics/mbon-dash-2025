#!/bin/bash

# Marimo Check Helper Functions
# Source this file in your shell: source marimo-helpers.sh

# Helper function to ensure we're in project root
_ensure_project_root() {
    if ! cd "$(git rev-parse --show-toplevel)" 2>/dev/null; then
        echo "❌ Must be run from within the git repository"
        return 1
    fi
}

# Function to check and fix a single marimo notebook
check_marimo() {
    local file="$1"
    if [ -z "$file" ]; then
        echo "Usage: check_marimo <notebook.py>"
        return 1
    fi
    
    _ensure_project_root || return 1
    
    echo "🔍 Checking marimo notebook: $file"
    (cd python && uv run marimo check --fix --verbose "../$file")
    
    if [ $? -eq 0 ]; then
        echo "✅ Check completed for $file"
    else
        echo "❌ Issues found in $file"
    fi
}

# Function to check all project marimo notebooks in python/scripts/notebooks/
check_all_marimo() {
    _ensure_project_root || return 1
    
    echo "🔍 Checking all project marimo notebooks..."
    
    if [ ! -d "python/scripts/notebooks" ]; then
        echo "❌ Directory python/scripts/notebooks not found"
        return 1
    fi
    
    # Find all .py files in the notebooks directory
    find python/scripts/notebooks -name "*.py" -type f | while read -r file; do
        echo "📝 Checking notebook: $file"
        (cd python && uv run marimo check --fix "../$file")
    done
    
    echo "✅ All project notebooks checked!"
}

# Function to check project marimo notebooks that were modified in the last N minutes
check_recent_marimo() {
    local minutes="${1:-30}"  # Default to 30 minutes
    
    _ensure_project_root || return 1
    
    echo "🔍 Checking project notebooks modified in the last $minutes minutes..."
    
    if [ ! -d "python/scripts/notebooks" ]; then
        echo "❌ Directory python/scripts/notebooks not found"
        return 1
    fi
    
    # Find recently modified .py files in notebooks directory only
    find python/scripts/notebooks -name "*.py" -type f -mmin -"$minutes" | while read -r file; do
        echo "📝 Checking recently modified: $file"
        (cd python && uv run marimo check --fix --verbose "../$file")
    done
}

# Function to set up file watching for automatic checking
watch_marimo() {
    local watch_dir="${1:-python/scripts/notebooks}"
    
    echo "👀 Watching for marimo notebook changes in: $watch_dir"
    echo "Press Ctrl+C to stop watching"
    
    if [ ! -d "$watch_dir" ]; then
        echo "❌ Directory $watch_dir not found"
        return 1
    fi
    
    # Use fswatch if available (install with: brew install fswatch)
    if command -v fswatch >/dev/null 2>&1; then
        fswatch -o "$watch_dir" -e '\.py$' | while read -r num; do
            echo "🔄 Changes detected, checking marimo notebooks..."
            check_all_marimo
        done
    else
        echo "⚠️  fswatch not found. Install with: brew install fswatch"
        echo "Falling back to basic file checking every 30 seconds..."
        
        while true; do
            sleep 30
            check_recent_marimo 1
        done
    fi
}

# Function to list all project marimo notebooks
list_marimo() {
    _ensure_project_root || return 1
    
    echo "📝 Project marimo notebooks:"
    
    if [ ! -d "python/scripts/notebooks" ]; then
        echo "❌ Directory python/scripts/notebooks not found"
        return 1
    fi
    
    find python/scripts/notebooks -name "*.py" -type f | sort | while read -r file; do
        echo "  • $file"
    done
}

# Function for AI workflow: create, check, and open notebook
ai_marimo() {
    local notebook_name="$1"
    if [ -z "$notebook_name" ]; then
        echo "Usage: ai_marimo <notebook_name.py>"
        return 1
    fi
    
    _ensure_project_root || return 1
    
    echo "🤖 AI Marimo Workflow for: $notebook_name"
    
    # If notebook exists, check it first
    if [ -f "$notebook_name" ]; then
        echo "📝 Checking existing notebook..."
        (cd python && uv run marimo check --fix --verbose "../$notebook_name")
    fi
    
    # Open in marimo editor
    echo "🚀 Opening marimo editor..."
    (cd python && uv run marimo edit "../$notebook_name")
}

echo "🎯 Marimo helper functions loaded!"
echo "Available commands:"
echo "  list_marimo              - List all project notebooks"
echo "  check_marimo <file>      - Check and fix a single notebook"
echo "  check_all_marimo         - Check all PROJECT notebooks (python/scripts/notebooks/)"
echo "  check_recent_marimo [N]  - Check project notebooks modified in last N minutes"
echo "  watch_marimo [dir]       - Watch directory for changes and auto-check (default: python/scripts/notebooks/)"
echo "  ai_marimo <file>         - AI workflow: check and open notebook"
