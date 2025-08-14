#!/usr/bin/env python3
"""
Temporal pattern analysis for MBON data.

Functions for analyzing temporal patterns in detection data across
different time scales (daily, monthly, seasonal, annual).
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


def get_monthly_patterns(df: pd.DataFrame, detection_cols: List[str], 
                        by_station: bool = True) -> pd.DataFrame:
    """
    Analyze monthly patterns in detection data.
    
    Args:
        df: Detection dataframe with datetime columns
        detection_cols: List of detection column names
        by_station: Whether to group by station as well
        
    Returns:
        DataFrame with monthly patterns
    """
    if by_station:
        monthly = df.groupby(['year', 'month', 'station']).sum(numeric_only=True)
    else:
        monthly = df.groupby(['year', 'month']).sum(numeric_only=True)
    
    return monthly


def get_seasonal_patterns(df: pd.DataFrame, detection_cols: List[str],
                         by_station: bool = True) -> pd.DataFrame:
    """
    Analyze seasonal patterns in detection data.
    
    Args:
        df: Detection dataframe with season column
        detection_cols: List of detection column names  
        by_station: Whether to group by station as well
        
    Returns:
        DataFrame with seasonal patterns
    """
    if by_station:
        seasonal = df.groupby(['season', 'station'])[detection_cols].sum()
    else:
        seasonal = df.groupby('season')[detection_cols].sum()
    
    return seasonal


def get_yearly_patterns(df: pd.DataFrame, detection_cols: List[str],
                       by_station: bool = True) -> pd.DataFrame:
    """
    Analyze yearly patterns in detection data.
    
    Args:
        df: Detection dataframe with year column
        detection_cols: List of detection column names
        by_station: Whether to group by station as well
        
    Returns:
        DataFrame with yearly patterns
    """
    if by_station:
        yearly = df.groupby(['year', 'station'])[detection_cols].sum()
    else:
        yearly = df.groupby('year')[detection_cols].sum()
    
    return yearly


def get_daily_patterns(df: pd.DataFrame, detection_cols: List[str],
                      by_station: bool = True) -> pd.DataFrame:
    """
    Analyze daily patterns in detection data.
    
    Args:
        df: Detection dataframe with date column
        detection_cols: List of detection column names
        by_station: Whether to group by station as well
        
    Returns:
        DataFrame with daily patterns
    """
    df = df.copy()
    df['date_only'] = df['date'].dt.date
    
    if by_station:
        daily = df.groupby(['date_only', 'station'])[detection_cols].sum()
    else:
        daily = df.groupby('date_only')[detection_cols].sum()
    
    return daily


def find_temporal_peaks(df: pd.DataFrame, detection_cols: List[str],
                       time_grouping: str = 'month', top_n: int = 5) -> Dict[str, Any]:
    """
    Find temporal peaks in detection activity.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        time_grouping: Time scale to group by ('day', 'month', 'season', 'year')
        top_n: Number of top periods to return
        
    Returns:
        Dictionary with peak periods and their activity levels
    """
    # Group by specified time period
    if time_grouping == 'day':
        grouped = df.groupby(df['date'].dt.date)[detection_cols].sum().sum(axis=1)
    elif time_grouping == 'month':
        grouped = df.groupby([df['date'].dt.year, df['date'].dt.month])[detection_cols].sum().sum(axis=1)
    elif time_grouping == 'season':
        grouped = df.groupby('season')[detection_cols].sum().sum(axis=1)
    elif time_grouping == 'year':
        grouped = df.groupby('year')[detection_cols].sum().sum(axis=1)
    else:
        raise ValueError(f"Invalid time_grouping: {time_grouping}")
    
    # Find peaks
    peaks = grouped.nlargest(top_n)
    
    return {
        'time_grouping': time_grouping,
        'peaks': [
            {
                'period': str(period),
                'total_detections': int(activity),
                'rank': rank + 1
            }
            for rank, (period, activity) in enumerate(peaks.items())
        ],
        'average': float(grouped.mean()),
        'std': float(grouped.std())
    }


def analyze_temporal_trends(df: pd.DataFrame, detection_cols: List[str],
                          detection_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze temporal trends for specific detection or overall activity.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        detection_name: Specific detection to analyze (None for total activity)
        
    Returns:
        Dictionary with trend analysis results
    """
    if detection_name:
        if detection_name not in detection_cols:
            raise ValueError(f"Detection '{detection_name}' not found in detection_cols")
        data_col = detection_name
    else:
        # Create total activity column
        df = df.copy()
        df['total_activity'] = df[detection_cols].sum(axis=1)
        data_col = 'total_activity'
    
    # Monthly trend
    monthly_trend = df.groupby([df['date'].dt.year, df['date'].dt.month])[data_col].sum()
    
    # Calculate trend statistics
    x_values = np.arange(len(monthly_trend))
    y_values = monthly_trend.values
    
    # Simple linear regression for trend
    if len(x_values) > 1:
        slope, intercept = np.polyfit(x_values, y_values, 1)
        r_squared = np.corrcoef(x_values, y_values)[0, 1] ** 2
    else:
        slope = 0
        intercept = y_values[0] if len(y_values) > 0 else 0
        r_squared = 0
    
    return {
        'detection': detection_name or 'total_activity',
        'trend': {
            'slope': float(slope),
            'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
            'r_squared': float(r_squared),
            'significance': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.3 else 'weak'
        },
        'monthly_data': [
            {
                'period': f"{year}-{month:02d}",
                'value': float(value)
            }
            for (year, month), value in monthly_trend.items()
        ],
        'summary': {
            'total': float(monthly_trend.sum()),
            'mean': float(monthly_trend.mean()),
            'std': float(monthly_trend.std()),
            'min': float(monthly_trend.min()),
            'max': float(monthly_trend.max())
        }
    }


def compare_temporal_patterns(df: pd.DataFrame, detection_cols: List[str],
                            comparison_groups: List[str]) -> Dict[str, Any]:
    """
    Compare temporal patterns between different groups (e.g., stations, species).
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        comparison_groups: List of group names to compare
        
    Returns:
        Dictionary with comparison results
    """
    results = {}
    
    for group in comparison_groups:
        if group not in df.columns:
            continue
            
        group_patterns = {}
        for group_value in df[group].unique():
            subset = df[df[group] == group_value]
            
            # Monthly pattern
            monthly = subset.groupby('month')[detection_cols].sum().sum(axis=1)
            
            group_patterns[str(group_value)] = {
                'monthly_pattern': monthly.to_dict(),
                'total_detections': int(subset[detection_cols].sum().sum()),
                'peak_month': int(monthly.idxmax()) if not monthly.empty else None,
                'peak_value': float(monthly.max()) if not monthly.empty else 0
            }
        
        results[group] = group_patterns
    
    return results


# Example usage
if __name__ == "__main__":
    """Example usage of temporal analysis functions."""
    
    from mbon_analysis.core import load_processed_data, prepare_detection_data, get_detection_columns
    
    print("MBON Temporal Analysis Examples")
    print("=" * 50)
    
    # Load and prepare data
    detections, environmental, detection_meta, stations = load_processed_data()
    detections = prepare_detection_data(detections)
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    
    # Analyze monthly patterns
    print("\n1. Analyzing monthly patterns...")
    monthly = get_monthly_patterns(detections, detection_cols)
    print(f"   Monthly patterns shape: {monthly.shape}")
    
    # Find temporal peaks
    print("\n2. Finding temporal peaks...")
    peaks = find_temporal_peaks(detections, detection_cols, time_grouping='month')
    print(f"   Top month: {peaks['peaks'][0]['period']} ({peaks['peaks'][0]['total_detections']:,} detections)")
    
    # Analyze trends
    print("\n3. Analyzing temporal trends...")
    trends = analyze_temporal_trends(detections, detection_cols)
    print(f"   Overall trend: {trends['trend']['direction']} (R² = {trends['trend']['r_squared']:.3f})")
    
    # Compare patterns between stations
    print("\n4. Comparing patterns between stations...")
    comparison = compare_temporal_patterns(detections, detection_cols, ['station'])
    stations_analyzed = list(comparison.get('station', {}).keys())
    print(f"   Compared {len(stations_analyzed)} stations")
    
    print("\n✅ Temporal analysis examples completed!")