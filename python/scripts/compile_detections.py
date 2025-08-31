#!/usr/bin/env python3
"""Entry point for compiling detections - calls the mbon_analysis package."""

import sys
from mbon_analysis.cli import main

if __name__ == "__main__":
    # Override sys.argv to call compile-detections command
    sys.argv = [sys.argv[0], "compile-detections"] + sys.argv[1:]
    sys.exit(main())
