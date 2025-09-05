#!/usr/bin/env python3
"""Check for duplicate timestamps in detection data"""

import json
from pathlib import Path

det_file = Path(__file__).parent.parent.parent / "data" / "processed" / "compiled_detections.json"
with open(det_file, 'r') as f:
    det = json.load(f)

for station in ['9M', '14M']:
    times = {}
    for r in det['stations'][station]['2021']['data']:
        # Extract timestamp without microseconds
        time = r['Date'].split('.')[0] if '.' in r['Date'] else r['Date']
        if time not in times:
            times[time] = 0
        times[time] += 1
    
    # Check for issues
    dups = {k:v for k,v in times.items() if v > 1}
    print(f'{station}: {len(times)} unique times from {len(det["stations"][station]["2021"]["data"])} records')
    print(f'  Duplicates: {len(dups)} timestamps appear multiple times')
    
    # Check coverage
    times_list = sorted(times.keys())
    print(f'  Date range: {times_list[0]} to {times_list[-1]}')
    
    # Check if it's every 2 hours
    jan_times = [t for t in times_list if t.startswith('2021-01')]
    if len(jan_times) > 10:
        print(f'  First 5 January timestamps: {jan_times[:5]}')