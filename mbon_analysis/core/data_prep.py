#!/usr/bin/env python3
"""
Data preparation utilities for MBON analysis.

Functions for cleaning, preparing, and structuring detection, environmental,
and species metadata for analysis.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any


def prepare_detection_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare detection data for analysis by cleaning and adding derived columns.
    
    Args:
        df: Raw detection dataframe
        
    Returns:
        Cleaned dataframe with derived time columns
    """
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Convert date columns to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Clean mixed data type columns - convert to numeric where possible
    mixed_columns = ['fic', 'bde', 'bdbp', 'none']
    for col in mixed_columns:
        if col in df.columns:
            # Convert to numeric, replacing non-numeric values with NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add derived time columns for different aggregations
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    df['season'] = df['date'].dt.month.map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_year'] = df['date'].dt.dayofyear
    
    return df


def get_detection_columns(df: pd.DataFrame, detection_meta: List[Dict]) -> Tuple[List[str], List[Dict], List[Dict]]:
    """
    Identify detection/annotation columns based on metadata and classify by type.
    
    Args:
        df: Detection dataframe
        detection_meta: Species/sound metadata list
        
    Returns:
        Tuple of (detection_cols, biological_items, anthropogenic_items)
    """
    # Get short names from detection metadata and filter for bio/anthro types only
    detection_cols = []
    biological = []
    anthropogenic = []
    
    for item in detection_meta:
        short_name = item['short_name']
        detection_type = item.get('type', item.get('category', 'unknown'))  # Prefer new 'type' field
        
        # Only include bio and anthro types as detections
        if detection_type in ['bio', 'anthro'] and short_name in df.columns:
            # Only include if column is numeric
            if pd.api.types.is_numeric_dtype(df[short_name]):
                detection_cols.append(short_name)
                
                if detection_type == 'bio':
                    biological.append(item)
                elif detection_type == 'anthro':
                    anthropogenic.append(item)
        elif detection_type in ['info', 'none']:
            # Skip info and none columns - these are metadata or empty
            continue
    
    return detection_cols, biological, anthropogenic


def classify_detections(detection_meta: List[Dict]) -> Dict[str, List[str]]:
    """
    Classify detection columns by type from metadata.
    
    Args:
        detection_meta: Species/sound metadata list
        
    Returns:
        Dictionary with 'biological', 'anthropogenic', 'info', 'none' lists
    """
    classification = {
        'biological': [],
        'anthropogenic': [], 
        'info': [],
        'none': []
    }
    
    for item in detection_meta:
        short_name = item['short_name']
        detection_type = item.get('type', item.get('category', 'unknown'))
        
        if detection_type == 'bio':
            classification['biological'].append(short_name)
        elif detection_type == 'anthro':
            classification['anthropogenic'].append(short_name)
        elif detection_type == 'info':
            classification['info'].append(short_name)
        elif detection_type == 'none':
            classification['none'].append(short_name)
    
    return classification


def create_dashboard_aggregations(df: pd.DataFrame, detection_cols: List[str]) -> Dict[str, Any]:
    """
    Create pre-aggregated views optimized for dashboard display. This makes it easier for
    the web dashboard to quickly filter and display data.
    
    Args:
        df: Detection dataframe with datetime index
        detection_cols: List of detection column names
        
    Returns:
        Dictionary of aggregated views for dashboard
    """
    views = {}
    
    # 1. Daily aggregation (for timeline)
    daily = df.set_index('date').groupby([pd.Grouper(freq='D'), 'station']).sum(numeric_only=True)
    views['daily_by_station'] = daily.reset_index().to_dict('records')
    
    # 2. Monthly aggregation (for broader patterns)  
    monthly = df.set_index('date').groupby([pd.Grouper(freq='ME'), 'station']).sum(numeric_only=True)
    views['monthly_by_station'] = monthly.reset_index().to_dict('records')
    
    # 3. Detection rankings (both biological and anthropogenic)
    detection_totals = df[detection_cols].sum().sort_values(ascending=False)
    views['detection_rankings'] = [
        {'detection': det, 'total': int(total)} 
        for det, total in detection_totals.items()
    ]
    
    # 4. Station summaries
    station_summaries = []
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        station_summaries.append({
            'station': station,
            'total_detections': int(station_data[detection_cols].sum().sum()),
            'active_days': int(station_data['date'].nunique()),
            'date_range': {
                'start': station_data['date'].min().isoformat(),
                'end': station_data['date'].max().isoformat()
            }
        })
    views['station_summaries'] = station_summaries
    
    return views


# Example usage
if __name__ == "__main__":
    """Example usage of data preparation functions."""
    
    from mbon_analysis.core import load_processed_data
    
    print("MBON Data Preparation Examples")
    print("=" * 50)
    
    # Load data
    detections, environmental, detection_meta, stations = load_processed_data()
    
    # Prepare detection data
    print("\n1. Preparing detection data...")
    detections_clean = prepare_detection_data(detections)
    print(f"   Added derived columns: {['year', 'month', 'season', 'week', 'day_of_year']}")
    
    # Get detection columns
    print("\n2. Classifying detection columns...")
    detection_cols, biological, anthropogenic = get_detection_columns(detections_clean, detection_meta)
    print(f"   Found {len(detection_cols)} detection columns:")
    print(f"   - {len(biological)} biological species")
    print(f"   - {len(anthropogenic)} anthropogenic sounds")
    
    # Create dashboard aggregations
    print("\n3. Creating dashboard aggregations...")
    dashboard_views = create_dashboard_aggregations(detections_clean, detection_cols)
    print(f"   Created {len(dashboard_views)} aggregated views")
    
    print("\n✅ Data preparation examples completed!")