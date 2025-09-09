#!/usr/bin/env python3
"""
Installation script for mbon_analysis package.

This script helps ensure the package is properly installed for development,
especially for IDE environments like PyCharm.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Install the mbon_analysis package in editable mode."""
    
    project_root = Path(__file__).parent
    print(f"Installing mbon_analysis package from: {project_root}")
    
    # Change to project directory
    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(project_root)
        
        # Install in editable mode
        print("Installing package in editable mode...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], check=True, capture_output=True, text=True)
        
        print("✓ Package installed successfully!")
        print(f"Output: {result.stdout}")
        
        # Test import
        try:
            print("\nTesting import...")
            import mbon_analysis
            from mbon_analysis.data.loaders import create_loader
            print("✓ Import successful!")
            print(f"mbon_analysis package location: {mbon_analysis.__file__}")
            
        except ImportError as e:
            print(f"✗ Import failed: {e}")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return 1
    finally:
        os.chdir(original_cwd)
    
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    print("\nTo use in PyCharm:")
    print("1. Make sure PyCharm is using the same Python interpreter")
    print("2. Check File > Settings > Project > Python Interpreter")
    print(f"3. The interpreter should be: {sys.executable}")
    print("4. Restart PyCharm if needed")
    print("\nTo test the setup, try running:")
    print("python scripts/exploratory/explore-01.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())