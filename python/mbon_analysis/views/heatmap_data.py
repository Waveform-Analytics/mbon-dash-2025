"""Heatmap data view generator for temporal visualization of detections."""

import json
from datetime import datetime
from typing import Dict, Any, List
from .base import BaseViewGenerator
from ..data.loaders import create_loader
from ..utils.species_filter import SpeciesFilter


class HeatmapDataGenerator(BaseViewGenerator):
    """Generate heatmap_data.json for temporal visualization of detections."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate view data for heatmap visualization.
        
        Returns:
            Dictionary with heatmap data organized by detection type and temporal structure
        """
        loader = create_loader(self.data_root)
        
        try:
            # Load compiled detections data
            detections_data = loader.load_compiled_detections()
            print(f"Loaded compiled detections data")
        except Exception as e:
            print(f"Error loading compiled detections: {e}")
            return {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "description": "Error loading compiled detections data",
                    "error": str(e)
                },
                "data": []
            }
        
        # Extract detection types from metadata
        # Apply species filtering if enabled
        species_filter = SpeciesFilter()
        keep_species = species_filter.get_keep_species() if species_filter.is_enabled() else set()
        
        detection_types = []
        for col in detections_data['metadata']['column_mappings']:
            if col['type'] in ['bio', 'anthro']:
                # If filtering is enabled, only include species in the keep list
                if species_filter.is_enabled():
                    if col['short_name'] in keep_species:
                        detection_types.append({
                            'long_name': col['long_name'],
                            'short_name': col['short_name'],
                            'type': col['type']
                        })
                else:
                    # No filtering - include all bio and anthro types
                    detection_types.append({
                        'long_name': col['long_name'],
                        'short_name': col['short_name'],
                        'type': col['type']
                    })
        
        print(f"Found {len(detection_types)} detection types")
        
        # Track statistics
        total_records_processed = 0
        total_records_included = 0
        
        all_data = []
        value_ranges = {}
        date_range = [None, None]
        hours = set()
        
        # Process all stations and years
        for station_id, station_data in detections_data['stations'].items():
            for year_key, year_data in station_data.items():
                if 'data' not in year_data:
                    continue
                    
                for record in year_data['data']:
                    total_records_processed += 1
                    # Check for required fields - handle both "Date" and "Date " (with space)
                    date_field = None
                    if 'Date' in record:
                        date_field = 'Date'
                    elif 'Date ' in record:  # Handle space in field name
                        date_field = 'Date '
                    
                    if date_field is None or 'Time' not in record:
                        continue
                    
                    # Parse date and time
                    try:
                        date_str = record[date_field].split(' ')[0]
                        time_str = record['Time']
                        
                        # Handle different time formats
                        if ' ' in time_str:
                            time_part = time_str.split(' ')[1]
                        else:
                            time_part = time_str
                        
                        try:
                            hour = int(time_part.split(':')[0])
                            hours.add(hour)
                        except (ValueError, IndexError):
                            hour = 0  # Default to midnight if parsing fails
                        
                        # Calculate day of year
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        day_of_year = date_obj.timetuple().tm_yday
                        timestamp = date_obj.replace(hour=hour).isoformat() + 'Z'
                    except (ValueError, KeyError, AttributeError):
                        # Skip records with invalid date/time data
                        continue
                    
                    # Update date range
                    if date_range[0] is None or date_str < date_range[0]:
                        date_range[0] = date_str
                    if date_range[1] is None or date_str > date_range[1]:
                        date_range[1] = date_str
                    
                    # Process detection types and only include non-zero values
                    has_non_zero_values = False
                    detection_values = {}
                    
                    for detection_type in detection_types:
                        long_name = detection_type['long_name']
                        raw_value = record.get(long_name, 0.0)
                        
                        # Handle different value types
                        try:
                            if isinstance(raw_value, str):
                                # Skip string values (like "boat" in "Fish interruption cause")
                                continue
                            value = float(raw_value)
                        except (ValueError, TypeError):
                            # Skip non-numeric values
                            continue
                        
                        # Only include non-zero values to reduce file size
                        if value > 0:
                            has_non_zero_values = True
                            detection_values[long_name] = value
                            
                            # Track value ranges per detection type
                            if long_name not in value_ranges:
                                value_ranges[long_name] = [value, value]
                            else:
                                value_ranges[long_name][0] = min(value_ranges[long_name][0], value)
                                value_ranges[long_name][1] = max(value_ranges[long_name][1], value)
                    
                    # Only create data points if there are non-zero values
                    if has_non_zero_values:
                        # Create one data point per non-zero detection type
                        for long_name, value in detection_values.items():
                            detection_type = next(dt for dt in detection_types if dt['long_name'] == long_name)
                            
                            data_point = {
                                'date': date_str,
                                'hour': hour,
                                'value': value,
                                'station': station_id,
                                'year': int(year_key),
                                'detection_type': long_name,
                                'detection_type_short': detection_type['short_name'],
                                'dayOfYear': day_of_year,
                                'timestamp': timestamp
                            }
                            
                            all_data.append(data_point)
                            total_records_included += 1
        
        # Sort hours and determine interval
        sorted_hours = sorted(list(hours))
        hour_interval = 2  # Default to 2-hour intervals
        
        # Try to determine actual interval from data
        if len(sorted_hours) > 1:
            intervals = [sorted_hours[i+1] - sorted_hours[i] for i in range(len(sorted_hours)-1)]
            if intervals:
                hour_interval = min(intervals)
        
        # Create regular hour sequence
        regular_hours = list(range(0, 24, hour_interval))
        
        # Get unique stations and years
        stations = sorted(list(set(point['station'] for point in all_data)))
        years = sorted(list(set(point['year'] for point in all_data)))
        
        print(f"Processing results:")
        print(f"  Total records processed: {total_records_processed:,}")
        print(f"  Records with non-zero values: {total_records_included:,}")
        print(f"  Reduction: {((total_records_processed - total_records_included) / total_records_processed * 100):.1f}%")
        print(f"  Stations found: {stations}")
        print(f"  Years found: {years}")
        
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'description': 'Optimized heatmap data for temporal visualization of detections (non-zero values only)',
                'dateRange': date_range,
                'hourInterval': hour_interval,
                'hours': regular_hours,
                'detection_types': detection_types,
                'stations': stations,
                'years': years,
                'value_ranges': value_ranges,
                'total_records': len(all_data),
                'optimization_stats': {
                    'total_processed': total_records_processed,
                    'total_included': total_records_included,
                    'reduction_percentage': round((total_records_processed - total_records_included) / total_records_processed * 100, 1)
                },
                'data_structure': {
                    'date': 'Date string (YYYY-MM-DD)',
                    'hour': 'Hour of day (0-23)',
                    'value': 'Detection count/value (non-zero only)',
                    'station': 'Station identifier',
                    'year': 'Year',
                    'detection_type': 'Full detection type name',
                    'detection_type_short': 'Short detection type code',
                    'dayOfYear': 'Day of year (1-366)',
                    'timestamp': 'ISO timestamp'
                }
            },
            'data': all_data
        }
