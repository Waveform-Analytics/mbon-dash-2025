#!/usr/bin/env python3
"""
Editor Integration Script for Marimo Check
This script can be called from editors like VS Code to automatically check and fix marimo notebooks.

Usage:
    python editor-marimo-check.py <notebook.py>
    
Configure in VS Code by adding to tasks.json:
{
    "label": "Check Marimo Notebook",
    "type": "shell",
    "command": "python",
    "args": ["${workspaceFolder}/editor-marimo-check.py", "${file}"],
    "group": "build",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "panel": "new"
    }
}
"""

import sys
import subprocess
import os
from pathlib import Path

def is_marimo_notebook(file_path):
    """Check if a Python file is a marimo notebook."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return '@app.cell' in content or 'marimo as mo' in content
    except Exception:
        return False

def run_marimo_check(file_path, auto_fix=True):
    """Run marimo check on a file."""
    print(f"🔍 Checking marimo notebook: {file_path}")
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Build command
    cmd = ["uv", "run", "marimo", "check"]
    if auto_fix:
        cmd.append("--fix")
    cmd.extend(["--verbose", str(file_path)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print("📝 Output:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Marimo check completed successfully!")
        else:
            print(f"❌ Marimo check failed with exit code {result.returncode}")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running marimo check: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python editor-marimo-check.py <notebook.py>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Verify file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    # Check if it's a marimo notebook
    if not is_marimo_notebook(file_path):
        print(f"⚠️  File doesn't appear to be a marimo notebook: {file_path}")
        print("Looking for '@app.cell' or 'marimo as mo' in file content...")
        sys.exit(1)
    
    # Run the check
    success = run_marimo_check(file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()