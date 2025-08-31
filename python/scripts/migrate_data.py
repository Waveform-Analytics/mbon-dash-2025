#!/usr/bin/env python3
"""Entry point for data migration - calls the mbon_analysis package."""

import sys
from mbon_analysis.cli import main

if __name__ == "__main__":
    # Override sys.argv to call migrate-data command
    sys.argv = [sys.argv[0], "migrate-data"] + sys.argv[1:]
    sys.exit(main())
