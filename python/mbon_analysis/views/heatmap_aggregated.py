"""Aggregated heatmap data view generator for temporal visualization of detections."""

import json
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict
from .base import BaseViewGenerator
from ..data.loaders import create_loader


class AggregatedHeatmapDataGenerator(BaseViewGenerator):
    """Generate aggregated heatmap_data.json for temporal visualization of detections."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate aggregated view data for heatmap visualization.
        
        Returns:
            Dictionary with aggregated heatmap data organized by day/hour for efficient visualization
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
        detection_types = []
        for col in detections_data['metadata']['column_mappings']:
            if col['type'] in ['bio', 'anthro']:
                detection_types.append({
                    'long_name': col['long_name'],
                    'short_name': col['short_name'],
                    'type': col['type']
                })
        
        print(f"Found {len(detection_types)} detection types")
        
        # Track statistics
        total_records_processed = 0
        aggregation_stats = {}
        
        # Initialize aggregation structure
        # Key: (station, year, detection_type, date, hour)
        # Value: {'sum': 0, 'count': 0, 'max': 0}
        aggregated_data = defaultdict(lambda: {'sum': 0, 'count': 0, 'max': 0})
        
        date_range = [None, None]
        hours = set()
        stations = set()
        years = set()
        
        # Process all stations and years
        for station_id, station_data in detections_data['stations'].items():
            stations.add(station_id)
            
            for year_key, year_data in station_data.items():
                if 'data' not in year_data:
                    continue
                
                years.add(int(year_key))
                
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
                        
                    except (ValueError, KeyError, AttributeError):
                        # Skip records with invalid date/time data
                        continue
                    
                    # Update date range
                    if date_range[0] is None or date_str < date_range[0]:
                        date_range[0] = date_str
                    if date_range[1] is None or date_str > date_range[1]:
                        date_range[1] = date_str
                    
                    # Process detection types
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
                        
                        # Only aggregate non-zero values
                        if value > 0:
                            key = (station_id, int(year_key), long_name, date_str, hour)
                            aggregated_data[key]['sum'] += value
                            aggregated_data[key]['count'] += 1
                            aggregated_data[key]['max'] = max(aggregated_data[key]['max'], value)
        
        # Convert aggregated data to final format
        all_data = []
        value_ranges = {}
        detection_type_stats = defaultdict(lambda: {'total_sum': 0, 'total_count': 0, 'max_value': 0})
        
        for (station, year, detection_type_name, date, hour), stats in aggregated_data.items():
            # Calculate day of year
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                day_of_year = date_obj.timetuple().tm_yday
                timestamp = date_obj.replace(hour=hour).isoformat() + 'Z'
            except ValueError:
                continue
            
            # Use average value for the aggregation
            avg_value = stats['sum'] / stats['count'] if stats['count'] > 0 else 0
            
            # Find detection type info
            detection_type_info = next((dt for dt in detection_types if dt['long_name'] == detection_type_name), None)
            if not detection_type_info:
                continue
            
            data_point = {
                'date': date,
                'hour': hour,
                'value': round(avg_value, 2),  # Round to 2 decimal places
                'station': station,
                'year': year,
                'detection_type': detection_type_name,
                'detection_type_short': detection_type_info['short_name'],
                'dayOfYear': day_of_year,
                'timestamp': timestamp,
                'count': stats['count'],  # Number of records aggregated
                'max_value': round(stats['max'], 2)
            }
            
            all_data.append(data_point)
            
            # Track value ranges
            if detection_type_name not in value_ranges:
                value_ranges[detection_type_name] = [avg_value, avg_value]
            else:
                value_ranges[detection_type_name][0] = min(value_ranges[detection_type_name][0], avg_value)
                value_ranges[detection_type_name][1] = max(value_ranges[detection_type_name][1], avg_value)
            
            # Track statistics
            detection_type_stats[detection_type_name]['total_sum'] += stats['sum']
            detection_type_stats[detection_type_name]['total_count'] += stats['count']
            detection_type_stats[detection_type_name]['max_value'] = max(
                detection_type_stats[detection_type_name]['max_value'], stats['max']
            )
        
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
        
        # Sort stations and years
        stations = sorted(list(stations))
        years = sorted(list(years))
        
        # Filter detection types to only include those with data
        active_detection_types = []
        for dt in detection_types:
            if dt['long_name'] in detection_type_stats:
                active_detection_types.append(dt)
        
        print(f"Aggregation results:")
        print(f"  Total records processed: {total_records_processed:,}")
        print(f"  Aggregated data points: {len(all_data):,}")
        print(f"  Reduction: {((total_records_processed - len(all_data)) / total_records_processed * 100):.1f}%")
        print(f"  Active detection types: {len(active_detection_types)} out of {len(detection_types)}")
        
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'description': 'Aggregated heatmap data for temporal visualization of detections (averaged by day/hour)',
                'dateRange': date_range,
                'hourInterval': hour_interval,
                'hours': regular_hours,
                'detection_types': active_detection_types,
                'stations': stations,
                'years': years,
                'value_ranges': value_ranges,
                'total_records': len(all_data),
                'aggregation_stats': {
                    'total_processed': total_records_processed,
                    'aggregated_points': len(all_data),
                    'reduction_percentage': round((total_records_processed - len(all_data)) / total_records_processed * 100, 1),
                    'detection_type_stats': dict(detection_type_stats)
                },
                'data_structure': {
                    'date': 'Date string (YYYY-MM-DD)',
                    'hour': 'Hour of day (0-23)',
                    'value': 'Average detection count/value for the hour',
                    'station': 'Station identifier',
                    'year': 'Year',
                    'detection_type': 'Full detection type name',
                    'detection_type_short': 'Short detection type code',
                    'dayOfYear': 'Day of year (1-366)',
                    'timestamp': 'ISO timestamp',
                    'count': 'Number of records aggregated',
                    'max_value': 'Maximum value in the aggregation'
                }
            },
            'data': all_data
        }
