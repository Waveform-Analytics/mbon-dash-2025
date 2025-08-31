#!/usr/bin/env python3
"""Entry point for testing dashboard data access - calls the mbon_analysis package."""

import sys
from mbon_analysis.cli import main

if __name__ == "__main__":
    # Override sys.argv to call test-dashboard command
    sys.argv = [sys.argv[0], "test-dashboard"] + sys.argv[1:]
    sys.exit(main())
