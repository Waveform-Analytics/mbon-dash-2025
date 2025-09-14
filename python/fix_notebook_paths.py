#!/usr/bin/env python3
"""
Script to fix path resolution in all marimo notebooks.
This standardizes path handling to work regardless of where notebooks are launched from.
"""

import re
from pathlib import Path

def fix_notebook_paths(notebook_path):
    """Fix paths in a single notebook file."""
    print(f"Fixing paths in {notebook_path}")

    with open(notebook_path, 'r') as f:
        content = f.read()

    # Skip if already has DATA_ROOT setup
    if 'DATA_ROOT' in content:
        print(f"  Already has DATA_ROOT setup - skipping")
        return

    # Find the imports cell (usually has pandas and numpy)
    imports_pattern = r'(@app\.cell\ndef _\(\):.*?import pandas as pd.*?return.*?\n)'
    imports_match = re.search(imports_pattern, content, re.DOTALL)

    if not imports_match:
        # Try alternative pattern
        imports_pattern = r'(@app\.cell\ndef _\(\):.*?import pandas as pd.*?return[^)]*\))'
        imports_match = re.search(imports_pattern, content, re.DOTALL)

    if imports_match:
        original_cell = imports_match.group(1)

        # Create new imports cell with DATA_ROOT
        new_cell = '''@app.cell
def _():
    import pandas as pd
    import numpy as np
    import os
    from pathlib import Path

    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    DATA_ROOT = project_root / "data"

    return pd, DATA_ROOT'''

        content = content.replace(original_cell, new_cell)

        # Update function signatures to include DATA_ROOT
        content = re.sub(r'def _\((.*pd[^)]*)\):', r'def _(\1, DATA_ROOT):', content)

        # Fix relative paths to use DATA_ROOT
        path_patterns = [
            (r'"\.\.\/data\/([^"]*)"', r'DATA_ROOT / "\1"'),
            (r'"\.\.\/\.\.\/data\/([^"]*)"', r'DATA_ROOT / "\1"'),
            (r'"\.\.\/\.\.\/\.\.\/data\/([^"]*)"', r'DATA_ROOT / "\1"'),
        ]

        for pattern, replacement in path_patterns:
            content = re.sub(pattern, replacement, content)

        # Write back to file
        with open(notebook_path, 'w') as f:
            f.write(content)
        print(f"  Fixed paths in {notebook_path}")
    else:
        print(f"  Could not find imports cell pattern - skipping")

def main():
    notebook_dir = Path("scripts/notebooks")

    for notebook_file in notebook_dir.glob("*.py"):
        if notebook_file.name != "10_view_generation.py":  # Already fixed
            fix_notebook_paths(notebook_file)

    print("Path fixing complete!")

if __name__ == "__main__":
    main()