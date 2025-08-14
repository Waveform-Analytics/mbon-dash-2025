#!/usr/bin/env python3
"""
Data loading utilities for MBON processed datasets.

This module provides functions to load processed JSON files from the dashboard
data pipeline, making them easily accessible for analysis scripts.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Tuple, Dict, List, Any, Union


def get_data_directory(custom_path: Union[str, Path, None] = None) -> Path:
    """
    Get the path to the processed data directory.
    
    Args:
        custom_path: Optional custom path to data directory. 
                    If None, uses default relative to package location.
    
    Returns:
        Path to the processed data directory
        
    Raises:
        FileNotFoundError: If data directory doesn't exist
    """
    if custom_path:
        data_dir = Path(custom_path)
    else:
        # Get project root (3 levels up from this file: mbon_analysis/core/data_loader.py)
        package_dir = Path(__file__).resolve().parent.parent.parent
        data_dir = package_dir / "data" / "cdn" / "processed"
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    return data_dir


def load_processed_data(data_dir: Union[str, Path, None] = None, 
                       include_acoustic_indices: bool = False,
                       verbose: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict], List[Dict]]:
    """
    Load all core processed datasets from JSON files.
    
    This function loads the main datasets needed for most analysis workflows:
    - Detection/annotation data
    - Environmental data (temperature, depth)
    - Species metadata with type classifications
    - Station metadata
    
    Args:
        data_dir: Optional custom path to data directory
        include_acoustic_indices: Whether to also load acoustic indices data
        verbose: Whether to print loading progress
        
    Returns:
        Tuple of (detections_df, environmental_df, species_metadata, stations_metadata)
        If include_acoustic_indices=True, returns additional acoustic_indices_df as 5th element
        
    Raises:
        FileNotFoundError: If required data files are missing
    """
    data_path = get_data_directory(data_dir)
    
    if verbose:
        print(f"Loading data from: {data_path}")
    
    # Load detection data
    detections_file = data_path / "detections.json"
    if not detections_file.exists():
        raise FileNotFoundError(f"Detections file not found: {detections_file}")
    
    with open(detections_file, 'r') as f:
        detections = pd.DataFrame(json.load(f))
    
    if verbose:
        print(f"  ✓ Loaded {len(detections):,} detection records")
    
    # Load environmental data
    environmental_file = data_path / "environmental.json"
    if not environmental_file.exists():
        raise FileNotFoundError(f"Environmental file not found: {environmental_file}")
        
    with open(environmental_file, 'r') as f:
        environmental = pd.DataFrame(json.load(f))
    
    if verbose:
        print(f"  ✓ Loaded {len(environmental):,} environmental records")
    
    # Load species metadata
    species_file = data_path / "species.json"
    if not species_file.exists():
        raise FileNotFoundError(f"Species file not found: {species_file}")
        
    with open(species_file, 'r') as f:
        species_metadata = json.load(f)
    
    if verbose:
        print(f"  ✓ Loaded {len(species_metadata)} species definitions")
    
    # Load station metadata
    stations_file = data_path / "stations.json"
    if not stations_file.exists():
        raise FileNotFoundError(f"Stations file not found: {stations_file}")
        
    with open(stations_file, 'r') as f:
        stations_metadata = json.load(f)
    
    if verbose:
        print(f"  ✓ Loaded {len(stations_metadata)} station definitions")
    
    # Optionally load acoustic indices
    if include_acoustic_indices:
        acoustic_indices_file = data_path / "acoustic_indices.json"
        if acoustic_indices_file.exists():
            with open(acoustic_indices_file, 'r') as f:
                acoustic_indices = pd.DataFrame(json.load(f))
            if verbose:
                print(f"  ✓ Loaded {len(acoustic_indices):,} acoustic indices records")
            return detections, environmental, species_metadata, stations_metadata, acoustic_indices
        else:
            if verbose:
                print("  ⚠️ Acoustic indices file not found, skipping")
            return detections, environmental, species_metadata, stations_metadata, pd.DataFrame()
    
    return detections, environmental, species_metadata, stations_metadata


def load_acoustic_indices(data_dir: Union[str, Path, None] = None, 
                         verbose: bool = True) -> pd.DataFrame:
    """
    Load acoustic indices data specifically.
    
    Args:
        data_dir: Optional custom path to data directory
        verbose: Whether to print loading progress
        
    Returns:
        DataFrame with acoustic indices data
        
    Raises:
        FileNotFoundError: If acoustic indices file not found
    """
    data_path = get_data_directory(data_dir)
    
    acoustic_indices_file = data_path / "acoustic_indices.json"
    if not acoustic_indices_file.exists():
        raise FileNotFoundError(f"Acoustic indices file not found: {acoustic_indices_file}")
    
    with open(acoustic_indices_file, 'r') as f:
        acoustic_indices = pd.DataFrame(json.load(f))
    
    if verbose:
        print(f"✓ Loaded {len(acoustic_indices):,} acoustic indices records")
        
        # Show what we loaded
        if 'station' in acoustic_indices.columns:
            stations = acoustic_indices['station'].unique()
            print(f"  Stations: {', '.join(sorted(stations))}")
        
        if 'year' in acoustic_indices.columns:
            years = acoustic_indices['year'].unique()
            print(f"  Years: {', '.join(map(str, sorted(years)))}")
            
        if 'bandwidth' in acoustic_indices.columns:
            bandwidths = acoustic_indices['bandwidth'].unique()
            print(f"  Bandwidths: {', '.join(sorted(bandwidths))}")
    
    return acoustic_indices


def load_metadata(data_dir: Union[str, Path, None] = None,
                  verbose: bool = True) -> Dict[str, Any]:
    """
    Load processing metadata and data summary.
    
    Args:
        data_dir: Optional custom path to data directory
        verbose: Whether to print loading progress
        
    Returns:
        Dictionary with metadata including data summary and column mappings
    """
    data_path = get_data_directory(data_dir)
    
    metadata_file = data_path / "metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    if verbose:
        print(f"✓ Loaded processing metadata")
        if 'data_summary' in metadata:
            summary = metadata['data_summary']
            print(f"  Generated: {metadata.get('generated_at', 'unknown')}")
            print(f"  Total detections: {summary.get('total_detections', 0):,}")
            print(f"  Total environmental: {summary.get('total_environmental_records', 0):,}")
            if 'total_acoustic_indices_records' in summary:
                print(f"  Total acoustic indices: {summary.get('total_acoustic_indices_records', 0):,}")
    
    return metadata


# Convenience aliases for backward compatibility
load_data = load_processed_data  # For scripts that use the original function name


# Example usage for documentation
if __name__ == "__main__":
    """
    Example usage of the data loading functions.
    """
    print("MBON Data Loader Example")
    print("=" * 40)
    
    # Load all core data
    detections, environmental, species_meta, stations = load_processed_data()
    
    # Load with acoustic indices
    print("\nLoading with acoustic indices:")
    *core_data, acoustic_indices = load_processed_data(include_acoustic_indices=True)
    
    # Load acoustic indices separately
    print("\nLoading acoustic indices separately:")
    indices = load_acoustic_indices()
    
    # Load metadata
    print("\nLoading metadata:")
    metadata = load_metadata()