#!/usr/bin/env python3
"""Quick script to diagnose why alignment stops at July"""

import json
from pathlib import Path

# Load indices data
indices_file = Path(__file__).parent.parent.parent / "data" / "processed" / "compiled_indices_even_hours.json"
with open(indices_file, 'r') as f:
    indices = json.load(f)

# Check date ranges
for station in ['9M', '14M']:
    dates = [r['Date'] for r in indices['stations'][station]['2021']['FullBW']['data']]
    print(f'{station} indices: {dates[0]} to {dates[-1]} ({len(dates)} records)')
    # Check for July gap
    july_dates = [d for d in dates if d.startswith('7/')]
    aug_dates = [d for d in dates if d.startswith('8/')]
    print(f'  July dates: {len(july_dates)}, August dates: {len(aug_dates)}')
    if july_dates:
        print(f'  Last July: {july_dates[-1]}')
    if aug_dates:
        print(f'  First Aug: {aug_dates[0]}')

print()

# Load detections
det_file = Path(__file__).parent.parent.parent / "data" / "processed" / "compiled_detections.json"
with open(det_file, 'r') as f:
    detections = json.load(f)

for station in ['9M', '14M']:
    data = detections['stations'][station]['2021']['data']
    dates = [r['Date'] for r in data]
    print(f'{station} detections: {dates[0]} to {dates[-1]} ({len(dates)} records)')
    # Check for July gap
    july_dates = [d for d in dates if '2021-07' in d]
    aug_dates = [d for d in dates if '2021-08' in d]
    print(f'  July dates: {len(july_dates)}, August dates: {len(aug_dates)}')
    if july_dates:
        print(f'  Last July: {july_dates[-1]}')
    if aug_dates:
        print(f'  First Aug: {aug_dates[0]}')