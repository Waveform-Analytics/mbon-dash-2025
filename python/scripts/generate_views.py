#!/usr/bin/env python3
"""Entry point for generating views - calls the mbon_analysis package."""

import sys
from mbon_analysis.cli import generate_views_cli

if __name__ == "__main__":
    sys.exit(generate_views_cli())
