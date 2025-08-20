#!/usr/bin/env python3
"""
Acoustic indices data loading utilities for raw CSV files.

This module provides functions to load raw acoustic indices CSV files 
and prepare them for visualization components like temporal heatmaps 
and box plots.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime


def get_indices_data_directory(custom_path: Union[str, Path, None] = None) -> Path:
    """
    Get the path to the raw acoustic indices data directory.
    
    Args:
        custom_path: Optional custom path to indices directory
    
    Returns:
        Path to the indices data directory
    """
    if custom_path:
        indices_dir = Path(custom_path)
    else:
        # Get project root and navigate to indices directory
        package_dir = Path(__file__).resolve().parent.parent.parent
        indices_dir = package_dir / "data" / "cdn" / "raw-data" / "indices"
    
    if not indices_dir.exists():
        raise FileNotFoundError(f"Indices directory not found: {indices_dir}")
    
    return indices_dir


def load_acoustic_indices_csv(station: str = '9M', 
                              bandwidth: str = 'FullBW',
                              year: int = 2021,
                              indices_dir: Optional[Path] = None) -> pd.DataFrame:
    """
    Load a single acoustic indices CSV file.
    
    Args:
        station: Station name ('9M', '14M', '37M')
        bandwidth: Bandwidth type ('FullBW' or '8kHz')
        year: Year of data (currently only 2021 available)
        indices_dir: Optional custom path to indices directory
    
    Returns:
        DataFrame with acoustic indices data
    """
    if indices_dir is None:
        indices_dir = get_indices_data_directory()
    
    # Construct filename
    filename = f"Acoustic_Indices_{station}_{year}_{bandwidth}_v2_Final.csv"
    filepath = indices_dir / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Indices file not found: {filepath}")
    
    # Load CSV
    df = pd.read_csv(filepath)
    
    # Parse datetime if Date column exists
    if 'Date' in df.columns:
        df['datetime'] = pd.to_datetime(df['Date'])
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        df['time_of_day'] = df['datetime'].dt.strftime('%H:%M')
    
    return df


def load_all_acoustic_indices(stations: List[str] = ['9M', '14M', '37M'],
                              bandwidths: List[str] = ['FullBW', '8kHz'],
                              year: int = 2021) -> Dict[str, pd.DataFrame]:
    """
    Load all available acoustic indices CSV files.
    
    Args:
        stations: List of station names
        bandwidths: List of bandwidth types
        year: Year of data
    
    Returns:
        Dictionary mapping dataset keys to DataFrames
        Keys are formatted as "{station}_{bandwidth}"
    """
    datasets = {}
    
    for station in stations:
        for bandwidth in bandwidths:
            key = f"{station}_{bandwidth}"
            try:
                df = load_acoustic_indices_csv(station, bandwidth, year)
                datasets[key] = df
                print(f"Loaded {key}: {len(df)} records")
            except FileNotFoundError as e:
                print(f"Warning: Could not load {key} - {e}")
    
    return datasets


def prepare_temporal_heatmap_data(df: pd.DataFrame, 
                                  index_name: str,
                                  aggregate_func: str = 'mean') -> pd.DataFrame:
    """
    Prepare data for temporal heatmap visualization (date x time-of-day).
    
    Args:
        df: DataFrame with acoustic indices data
        index_name: Name of the index column to visualize
        aggregate_func: Aggregation function ('mean', 'median', 'max', 'min')
    
    Returns:
        DataFrame with date, hour, and aggregated value
    """
    if index_name not in df.columns:
        raise ValueError(f"Index '{index_name}' not found in DataFrame columns")
    
    # Ensure datetime columns exist
    if 'datetime' not in df.columns and 'Date' in df.columns:
        df['datetime'] = pd.to_datetime(df['Date'])
    
    if 'date' not in df.columns:
        df['date'] = df['datetime'].dt.date
    
    if 'hour' not in df.columns:
        df['hour'] = df['datetime'].dt.hour
    
    # Aggregate by date and hour
    agg_funcs = {
        'mean': np.mean,
        'median': np.median,
        'max': np.max,
        'min': np.min
    }
    
    if aggregate_func not in agg_funcs:
        raise ValueError(f"Invalid aggregate_func. Choose from: {list(agg_funcs.keys())}")
    
    result = df.groupby(['date', 'hour'])[index_name].agg(agg_funcs[aggregate_func]).reset_index()
    result.columns = ['date', 'hour', 'value']
    
    # Add string representations for visualization
    result['date_str'] = result['date'].astype(str)
    result['hour_str'] = result['hour'].apply(lambda h: f"{h:02d}:00")
    
    return result


def prepare_box_plot_data(datasets: Dict[str, pd.DataFrame],
                         index_name: str) -> pd.DataFrame:
    """
    Prepare data for box plot visualization comparing stations and bandwidths.
    
    Args:
        datasets: Dictionary of DataFrames from load_all_acoustic_indices
        index_name: Name of the index column to visualize
    
    Returns:
        DataFrame with station, bandwidth, and values for box plot
    """
    box_plot_data = []
    
    for key, df in datasets.items():
        if index_name not in df.columns:
            print(f"Warning: Index '{index_name}' not found in {key}")
            continue
        
        # Parse station and bandwidth from key
        parts = key.split('_')
        station = parts[0]
        bandwidth = '_'.join(parts[1:]) if len(parts) > 1 else 'Unknown'
        
        # Get values
        values = df[index_name].dropna()
        
        # Add records for box plot
        for value in values:
            box_plot_data.append({
                'station': station,
                'bandwidth': bandwidth,
                'value': value,
                'group': f"{station}_{bandwidth}"
            })
    
    return pd.DataFrame(box_plot_data)


def get_available_indices(df: pd.DataFrame) -> List[str]:
    """
    Get list of available acoustic indices from a DataFrame.
    
    Args:
        df: DataFrame with acoustic indices data
    
    Returns:
        List of acoustic index column names
    """
    # Exclude metadata columns
    exclude_cols = ['Date', 'datetime', 'date', 'hour', 'time_of_day', 
                   'year', 'month', 'day', 'hour_str', 'date_str']
    
    # Get numeric columns that are not in exclude list
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    indices = [col for col in numeric_cols if col not in exclude_cols]
    
    return sorted(indices)


def export_for_dashboard(datasets: Dict[str, pd.DataFrame],
                         output_dir: Union[str, Path, None] = None) -> Dict[str, str]:
    """
    Export acoustic indices data in formats suitable for dashboard components.
    
    Args:
        datasets: Dictionary of DataFrames from load_all_acoustic_indices
        output_dir: Directory to save JSON files (default: data/cdn/processed)
    
    Returns:
        Dictionary mapping output type to file path
    """
    if output_dir is None:
        package_dir = Path(__file__).resolve().parent.parent.parent
        output_dir = package_dir / "data" / "cdn" / "processed"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = {}
    
    # Combine all datasets for export
    combined_data = []
    
    for key, df in datasets.items():
        parts = key.split('_')
        station = parts[0]
        bandwidth = '_'.join(parts[1:]) if len(parts) > 1 else 'Unknown'
        
        # Add metadata columns
        df_export = df.copy()
        df_export['station'] = station
        df_export['bandwidth'] = bandwidth
        
        combined_data.append(df_export)
    
    # Concatenate all data
    if combined_data:
        all_data = pd.concat(combined_data, ignore_index=True)
        
        # Export to JSON
        output_file = output_dir / "acoustic_indices_raw.json"
        
        # Convert to records format for dashboard
        records = all_data.to_dict(orient='records')
        
        # Save with metadata
        export_data = {
            'indices_data': records,
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_records': len(records),
                'stations': list(all_data['station'].unique()),
                'bandwidths': list(all_data['bandwidth'].unique()),
                'available_indices': get_available_indices(all_data)
            }
        }
        
        import json
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        output_files['acoustic_indices_raw'] = str(output_file)
        print(f"Exported {len(records)} records to {output_file}")
    
    return output_files


# Example usage functions
def create_temporal_heatmap_json(station: str = '9M',
                                 bandwidth: str = 'FullBW',
                                 index_name: str = 'ACI') -> Dict:
    """
    Create JSON data for temporal heatmap visualization.
    
    Args:
        station: Station name
        bandwidth: Bandwidth type
        index_name: Acoustic index to visualize
    
    Returns:
        Dictionary ready for JSON export
    """
    # Load data
    df = load_acoustic_indices_csv(station, bandwidth)
    
    # Prepare heatmap data
    heatmap_data = prepare_temporal_heatmap_data(df, index_name)
    
    # Format for export
    return {
        'heatmap_data': heatmap_data.to_dict(orient='records'),
        'metadata': {
            'station': station,
            'bandwidth': bandwidth,
            'index': index_name,
            'date_range': {
                'start': str(heatmap_data['date'].min()),
                'end': str(heatmap_data['date'].max())
            },
            'hours': sorted(heatmap_data['hour'].unique().tolist())
        }
    }


def create_box_plot_json(index_name: str = 'ACI') -> Dict:
    """
    Create JSON data for box plot visualization.
    
    Args:
        index_name: Acoustic index to visualize
    
    Returns:
        Dictionary ready for JSON export
    """
    # Load all datasets
    datasets = load_all_acoustic_indices()
    
    # Prepare box plot data
    box_data = prepare_box_plot_data(datasets, index_name)
    
    # Calculate summary statistics for each group
    summary_stats = box_data.groupby(['station', 'bandwidth'])['value'].describe()
    
    # Format for export
    return {
        'box_plot_data': box_data.to_dict(orient='records'),
        'summary_stats': summary_stats.to_dict(),
        'metadata': {
            'index': index_name,
            'total_values': len(box_data),
            'stations': sorted(box_data['station'].unique().tolist()),
            'bandwidths': sorted(box_data['bandwidth'].unique().tolist())
        }
    }