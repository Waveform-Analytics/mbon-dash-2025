#!/usr/bin/env python3
"""
Spatial pattern analysis for MBON data.

Functions for analyzing spatial patterns in detection data across
monitoring stations and comparing acoustic environments.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional


def get_station_activity(df: pd.DataFrame, detection_cols: List[str]) -> pd.DataFrame:
    """
    Calculate total activity levels by station.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        
    Returns:
        DataFrame with station activity totals
    """
    station_activity = df.groupby('station')[detection_cols].sum()
    return station_activity


def compare_stations(df: pd.DataFrame, detection_cols: List[str],
                    stations: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compare detection patterns between stations.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        stations: List of stations to compare (None for all)
        
    Returns:
        Dictionary with station comparison results
    """
    if stations:
        df = df[df['station'].isin(stations)]
    
    station_patterns = {}
    
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        
        # Basic statistics
        total_detections = station_data[detection_cols].sum().sum()
        active_days = station_data['date'].nunique()
        date_range = {
            'start': station_data['date'].min().isoformat(),
            'end': station_data['date'].max().isoformat()
        }
        
        # Top detections for this station
        top_detections = station_data[detection_cols].sum().nlargest(10)
        
        # Monthly pattern
        monthly_pattern = station_data.groupby('month')[detection_cols].sum().sum(axis=1)
        
        # Seasonal pattern
        seasonal_pattern = station_data.groupby('season')[detection_cols].sum().sum(axis=1)
        
        station_patterns[station] = {
            'total_detections': int(total_detections),
            'active_days': int(active_days),
            'date_range': date_range,
            'detections_per_day': total_detections / active_days if active_days > 0 else 0,
            'top_detections': [
                {'detection': det, 'count': int(count)}
                for det, count in top_detections.items()
            ],
            'monthly_pattern': monthly_pattern.to_dict(),
            'seasonal_pattern': seasonal_pattern.to_dict(),
            'peak_month': int(monthly_pattern.idxmax()) if not monthly_pattern.empty else None,
            'peak_season': str(seasonal_pattern.idxmax()) if not seasonal_pattern.empty else None
        }
    
    return station_patterns


def calculate_station_similarity(df: pd.DataFrame, detection_cols: List[str],
                                metric: str = 'correlation') -> pd.DataFrame:
    """
    Calculate similarity between stations based on detection patterns.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        metric: Similarity metric ('correlation', 'cosine', 'jaccard')
        
    Returns:
        DataFrame with pairwise station similarities
    """
    # Get station activity patterns
    station_activity = df.groupby('station')[detection_cols].sum()
    
    if metric == 'correlation':
        similarity_matrix = station_activity.T.corr()
    elif metric == 'cosine':
        # Cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = pd.DataFrame(
            cosine_similarity(station_activity),
            index=station_activity.index,
            columns=station_activity.index
        )
    elif metric == 'jaccard':
        # Jaccard similarity (binary presence/absence)
        binary_activity = (station_activity > 0).astype(int)
        from sklearn.metrics.pairwise import jaccard_score
        n_stations = len(binary_activity)
        similarity_matrix = pd.DataFrame(
            index=binary_activity.index,
            columns=binary_activity.index
        )
        for i, station1 in enumerate(binary_activity.index):
            for j, station2 in enumerate(binary_activity.index):
                if i == j:
                    similarity_matrix.loc[station1, station2] = 1.0
                else:
                    sim = jaccard_score(binary_activity.loc[station1], 
                                      binary_activity.loc[station2])
                    similarity_matrix.loc[station1, station2] = sim
    else:
        raise ValueError(f"Unknown metric: {metric}")
    
    return similarity_matrix


def identify_station_specialization(df: pd.DataFrame, detection_cols: List[str],
                                  threshold_ratio: float = 2.0) -> Dict[str, Any]:
    """
    Identify detections that are specialized to particular stations.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        threshold_ratio: Ratio threshold for considering a detection specialized
        
    Returns:
        Dictionary with specialization results
    """
    station_activity = df.groupby('station')[detection_cols].sum()
    
    specializations = {}
    
    for detection in detection_cols:
        detection_by_station = station_activity[detection]
        max_station = detection_by_station.idxmax()
        max_value = detection_by_station.max()
        
        # Calculate how much higher the max station is compared to others
        other_values = detection_by_station.drop(max_station)
        mean_others = other_values.mean() if len(other_values) > 0 else 0
        
        if mean_others > 0:
            specialization_ratio = max_value / mean_others
        else:
            specialization_ratio = float('inf') if max_value > 0 else 1.0
        
        if specialization_ratio >= threshold_ratio:
            specializations[detection] = {
                'specialized_station': max_station,
                'max_count': int(max_value),
                'specialization_ratio': float(specialization_ratio),
                'other_stations': {
                    station: int(count) 
                    for station, count in other_values.items()
                }
            }
    
    return specializations


def analyze_spatial_gradients(df: pd.DataFrame, detection_cols: List[str],
                            station_metadata: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Analyze spatial gradients in detection patterns.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        station_metadata: Optional metadata with station coordinates/properties
        
    Returns:
        Dictionary with spatial gradient analysis
    """
    results = {
        'station_rankings': {},
        'gradient_patterns': {}
    }
    
    # Rank stations by total activity
    station_totals = df.groupby('station')[detection_cols].sum().sum(axis=1).sort_values(ascending=False)
    results['station_rankings']['total_activity'] = [
        {'station': station, 'total': int(total), 'rank': rank + 1}
        for rank, (station, total) in enumerate(station_totals.items())
    ]
    
    # Rank stations by detection diversity (species richness)
    station_diversity = df.groupby('station')[detection_cols].apply(lambda x: (x.sum() > 0).sum())
    station_diversity = station_diversity.sort_values(ascending=False)
    results['station_rankings']['diversity'] = [
        {'station': station, 'species_count': int(count), 'rank': rank + 1}
        for rank, (station, count) in enumerate(station_diversity.items())
    ]
    
    # If station metadata available, look for environmental gradients
    if station_metadata is not None:
        # This would require station coordinates or environmental variables
        # Placeholder for future implementation
        results['environmental_gradients'] = {
            'note': 'Environmental gradient analysis requires station metadata with coordinates'
        }
    
    return results


def get_station_profiles(df: pd.DataFrame, detection_cols: List[str],
                        biological: List[Dict], anthropogenic: List[Dict]) -> Dict[str, Any]:
    """
    Create detailed profiles for each station.
    
    Args:
        df: Detection dataframe
        detection_cols: List of detection column names
        biological: List of biological species metadata
        anthropogenic: List of anthropogenic sound metadata
        
    Returns:
        Dictionary with detailed station profiles
    """
    bio_cols = [item['short_name'] for item in biological if item['short_name'] in detection_cols]
    anthro_cols = [item['short_name'] for item in anthropogenic if item['short_name'] in detection_cols]
    
    profiles = {}
    
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        
        # Basic metrics
        total_detections = station_data[detection_cols].sum().sum()
        bio_detections = station_data[bio_cols].sum().sum() if bio_cols else 0
        anthro_detections = station_data[anthro_cols].sum().sum() if anthro_cols else 0
        
        # Activity patterns
        hourly_pattern = station_data.groupby(station_data['date'].dt.hour)[detection_cols].sum().sum(axis=1)
        daily_pattern = station_data.groupby(station_data['date'].dt.day_name())[detection_cols].sum().sum(axis=1)
        
        profiles[station] = {
            'summary': {
                'total_detections': int(total_detections),
                'biological_detections': int(bio_detections),
                'anthropogenic_detections': int(anthro_detections),
                'bio_percentage': (bio_detections / total_detections * 100) if total_detections > 0 else 0,
                'active_species': int((station_data[bio_cols].sum() > 0).sum()) if bio_cols else 0,
                'monitoring_days': int(station_data['date'].nunique())
            },
            'temporal_patterns': {
                'hourly': hourly_pattern.to_dict(),
                'daily': daily_pattern.to_dict(),
                'peak_hour': int(hourly_pattern.idxmax()) if not hourly_pattern.empty else None,
                'peak_day': str(daily_pattern.idxmax()) if not daily_pattern.empty else None
            },
            'top_biological': [
                {'species': item['short_name'], 'count': int(station_data[item['short_name']].sum())}
                for item in biological 
                if item['short_name'] in bio_cols and station_data[item['short_name']].sum() > 0
            ][:10],  # Top 10
            'top_anthropogenic': [
                {'sound': item['short_name'], 'count': int(station_data[item['short_name']].sum())}
                for item in anthropogenic 
                if item['short_name'] in anthro_cols and station_data[item['short_name']].sum() > 0
            ][:10]  # Top 10
        }
    
    return profiles


# Example usage
if __name__ == "__main__":
    """Example usage of spatial analysis functions."""
    
    from mbon_analysis.core import load_processed_data, prepare_detection_data, get_detection_columns
    
    print("MBON Spatial Analysis Examples")
    print("=" * 50)
    
    # Load and prepare data
    detections, environmental, detection_meta, stations = load_processed_data()
    detections = prepare_detection_data(detections)
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    
    # Get station activity
    print("\n1. Analyzing station activity...")
    activity = get_station_activity(detections, detection_cols)
    print(f"   Station activity shape: {activity.shape}")
    
    # Compare stations
    print("\n2. Comparing stations...")
    comparison = compare_stations(detections, detection_cols)
    print(f"   Analyzed {len(comparison)} stations")
    
    # Calculate similarity
    print("\n3. Calculating station similarity...")
    similarity = calculate_station_similarity(detections, detection_cols, metric='correlation')
    print(f"   Similarity matrix shape: {similarity.shape}")
    
    # Find specializations
    print("\n4. Finding station specializations...")
    specializations = identify_station_specialization(detections, detection_cols)
    print(f"   Found {len(specializations)} specialized detections")
    
    print("\n✅ Spatial analysis examples completed!")