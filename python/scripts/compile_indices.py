#!/usr/bin/env python3
"""Entry point for compiling indices - calls the mbon_analysis package."""

import sys
from mbon_analysis.cli import main

if __name__ == "__main__":
    # Override sys.argv to call compile-indices command
    sys.argv = [sys.argv[0], "compile-indices"] + sys.argv[1:]
    sys.exit(main())
