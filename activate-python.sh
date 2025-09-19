#!/bin/bash
# Helper script to activate the Python environment for this project

echo "Activating Python environment..."
cd "$(dirname "$0")/python" || exit 1

# Check if we're already in the environment
if [[ "$VIRTUAL_ENV" == *"mbon-dash-2025/python/.venv"* ]]; then
    echo "Python environment already activated!"
    cd ..
    return 0 2>/dev/null || exit 0
fi

# Activate the virtual environment
source .venv/bin/activate

# Return to project root
cd ..

echo "Python environment activated!"
echo "To run marimo: marimo edit python/scripts/notebooks/[notebook].py"
echo "To deactivate: deactivate"