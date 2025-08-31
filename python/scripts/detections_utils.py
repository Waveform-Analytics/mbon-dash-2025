#!/usr/bin/env python3
"""Entry point for detections utilities - calls the mbon_analysis package."""

import sys
from mbon_analysis.cli import main

if __name__ == "__main__":
    # Override sys.argv to call detections-utils command
    sys.argv = [sys.argv[0], "detections-utils"] + sys.argv[1:]
    sys.exit(main())
