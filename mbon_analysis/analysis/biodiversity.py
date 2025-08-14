#!/usr/bin/env python3
"""
Biodiversity and detection pattern analysis for MBON data.

Functions for analyzing detection patterns, co-occurrence matrices,
and biodiversity metrics from acoustic monitoring data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Any


def calculate_co_occurrence(df: pd.DataFrame, detection_cols: List[str]) -> pd.DataFrame:
    """
    Calculate co-occurrence matrix for detections.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        
    Returns:
        Co-occurrence matrix as DataFrame
    """
    detection_data = df[detection_cols]
    
    # Convert to binary presence/absence for co-occurrence
    detection_binary = (detection_data > 0).astype(int)
    co_occurrence = detection_binary.T.dot(detection_binary)
    
    return co_occurrence


def get_detection_rankings(df: pd.DataFrame, detection_cols: List[str], top_n: int = None) -> pd.Series:
    """
    Get detection rankings by total activity.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        top_n: Number of top detections to return (None for all)
        
    Returns:
        Series with detection totals, sorted descending
    """
    rankings = df[detection_cols].sum().sort_values(ascending=False)
    
    if top_n:
        rankings = rankings.head(top_n)
    
    return rankings


def analyze_bio_anthro_patterns(df: pd.DataFrame, biological: List[Dict], 
                               anthropogenic: List[Dict], detection_cols: List[str]) -> Dict[str, Any]:
    """
    Analyze biological vs anthropogenic detection patterns.
    
    Args:
        df: Detection dataframe
        biological: List of biological species metadata
        anthropogenic: List of anthropogenic sound metadata
        detection_cols: List of detection column names
        
    Returns:
        Dictionary with pattern analysis results
    """
    # Get column names for each type
    bio_cols = [item['short_name'] for item in biological if item['short_name'] in detection_cols]
    anthro_cols = [item['short_name'] for item in anthropogenic if item['short_name'] in detection_cols]
    
    # Calculate totals
    bio_activity = df[bio_cols].sum().sum() if bio_cols else 0
    anthro_activity = df[anthro_cols].sum().sum() if anthro_cols else 0
    
    # Temporal patterns
    bio_monthly = df.groupby('month')[bio_cols].sum().sum(axis=1) if bio_cols else pd.Series()
    anthro_monthly = df.groupby('month')[anthro_cols].sum().sum(axis=1) if anthro_cols else pd.Series()
    
    # Station patterns
    bio_by_station = df.groupby('station')[bio_cols].sum().sum(axis=1) if bio_cols else pd.Series()
    anthro_by_station = df.groupby('station')[anthro_cols].sum().sum(axis=1) if anthro_cols else pd.Series()
    
    return {
        'biological': {
            'total_detections': int(bio_activity),
            'species_count': len(bio_cols),
            'monthly_pattern': bio_monthly.to_dict(),
            'station_pattern': bio_by_station.to_dict(),
            'columns': bio_cols
        },
        'anthropogenic': {
            'total_detections': int(anthro_activity),
            'sound_count': len(anthro_cols),
            'monthly_pattern': anthro_monthly.to_dict(),
            'station_pattern': anthro_by_station.to_dict(),
            'columns': anthro_cols
        },
        'ratio': {
            'bio_to_anthro': bio_activity / anthro_activity if anthro_activity > 0 else float('inf'),
            'bio_percentage': (bio_activity / (bio_activity + anthro_activity)) * 100 if (bio_activity + anthro_activity) > 0 else 0
        }
    }


def get_diversity_metrics(df: pd.DataFrame, detection_cols: List[str], 
                         by_column: str = 'station') -> pd.DataFrame:
    """
    Calculate diversity metrics (richness, evenness) by grouping column.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        by_column: Column to group by (default: 'station')
        
    Returns:
        DataFrame with diversity metrics
    """
    # Group and sum detections
    grouped = df.groupby(by_column)[detection_cols].sum()
    
    metrics = []
    for group_value in grouped.index:
        detections = grouped.loc[group_value]
        
        # Species richness (number of detected species/sounds)
        richness = (detections > 0).sum()
        
        # Relative abundance
        total = detections.sum()
        if total > 0:
            proportions = detections / total
            # Shannon diversity
            shannon = -np.sum(proportions[proportions > 0] * np.log(proportions[proportions > 0]))
            # Evenness (Shannon / log(richness))
            evenness = shannon / np.log(richness) if richness > 1 else 0
        else:
            shannon = 0
            evenness = 0
        
        metrics.append({
            by_column: group_value,
            'richness': richness,
            'total_detections': total,
            'shannon_diversity': shannon,
            'evenness': evenness
        })
    
    return pd.DataFrame(metrics)


def find_detection_hotspots(df: pd.DataFrame, detection_cols: List[str], 
                          threshold_percentile: float = 90) -> Dict[str, Any]:
    """
    Find temporal and spatial hotspots of detection activity.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        threshold_percentile: Percentile threshold for defining hotspots
        
    Returns:
        Dictionary with hotspot information
    """
    # Calculate total activity per time period
    daily_activity = df.groupby(df['date'].dt.date)[detection_cols].sum().sum(axis=1)
    monthly_activity = df.groupby([df['date'].dt.year, df['date'].dt.month])[detection_cols].sum().sum(axis=1)
    station_activity = df.groupby('station')[detection_cols].sum().sum(axis=1)
    
    # Define thresholds
    daily_threshold = np.percentile(daily_activity, threshold_percentile)
    monthly_threshold = np.percentile(monthly_activity, threshold_percentile)
    station_threshold = np.percentile(station_activity, threshold_percentile)
    
    # Find hotspots
    daily_hotspots = daily_activity[daily_activity >= daily_threshold]
    monthly_hotspots = monthly_activity[monthly_activity >= monthly_threshold]
    station_hotspots = station_activity[station_activity >= station_threshold]
    
    return {
        'daily_hotspots': {
            'dates': daily_hotspots.index.tolist(),
            'activity': daily_hotspots.values.tolist(),
            'threshold': daily_threshold
        },
        'monthly_hotspots': {
            'periods': [f"{year}-{month:02d}" for year, month in monthly_hotspots.index],
            'activity': monthly_hotspots.values.tolist(),
            'threshold': monthly_threshold
        },
        'station_hotspots': {
            'stations': station_hotspots.index.tolist(),
            'activity': station_hotspots.values.tolist(),
            'threshold': station_threshold
        }
    }


# Example usage
if __name__ == "__main__":
    """Example usage of biodiversity analysis functions."""
    
    from mbon_analysis.core import load_processed_data, prepare_detection_data, get_detection_columns
    
    print("MBON Biodiversity Analysis Examples")
    print("=" * 50)
    
    # Load and prepare data
    detections, environmental, detection_meta, stations = load_processed_data()
    detections = prepare_detection_data(detections)
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    
    # Calculate co-occurrence
    print("\n1. Calculating co-occurrence matrix...")
    co_occurrence = calculate_co_occurrence(detections, detection_cols)
    print(f"   Co-occurrence matrix shape: {co_occurrence.shape}")
    
    # Get detection rankings
    print("\n2. Getting detection rankings...")
    rankings = get_detection_rankings(detections, detection_cols, top_n=10)
    print(f"   Top detection: {rankings.index[0]} ({rankings.iloc[0]:,} total)")
    
    # Analyze bio vs anthro patterns
    print("\n3. Analyzing bio vs anthropogenic patterns...")
    patterns = analyze_bio_anthro_patterns(detections, biological, anthropogenic, detection_cols)
    print(f"   Biological: {patterns['biological']['total_detections']:,} detections")
    print(f"   Anthropogenic: {patterns['anthropogenic']['total_detections']:,} detections")
    
    # Calculate diversity metrics
    print("\n4. Calculating diversity metrics...")
    diversity = get_diversity_metrics(detections, detection_cols, by_column='station')
    print(f"   Station diversity shape: {diversity.shape}")
    
    print("\n✅ Biodiversity analysis examples completed!")