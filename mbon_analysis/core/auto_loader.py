#!/usr/bin/env python3
"""
Auto-loading utilities that ensure data is up-to-date before loading.

This module combines data_sync and data_loader functionality to provide
convenient functions that automatically check for updates and sync before loading.
"""

from typing import Tuple, Dict, List, Any, Optional
import pandas as pd
from pathlib import Path

from .data_sync import ensure_data_available, check_data_freshness
from .data_loader import load_processed_data, load_acoustic_indices


def load_with_auto_sync(include_acoustic_indices: bool = False,
                       check_updates: bool = True,
                       force_sync: bool = False,
                       verbose: bool = True) -> Tuple:
    """
    Load processed data with automatic CDN sync if needed.
    
    This function checks if raw data is up-to-date and syncs from CDN if needed,
    then loads the processed data. It's ideal for analysis scripts that should
    always work with the latest data.
    
    Args:
        include_acoustic_indices: Whether to include acoustic indices in return
        check_updates: Whether to check for updates (if False, just loads local)
        force_sync: Force sync even if data appears up-to-date
        verbose: Whether to print progress
        
    Returns:
        Same as load_processed_data() - tuple of dataframes and metadata
        
    Example:
        >>> # Auto-sync and load
        >>> detections, environmental, species, stations = load_with_auto_sync()
        
        >>> # Force fresh sync
        >>> *data, indices = load_with_auto_sync(
        ...     include_acoustic_indices=True,
        ...     force_sync=True
        ... )
    """
    if check_updates or force_sync:
        if verbose:
            print("🔄 Checking for data updates...")
        
        # Determine what data types we need
        data_types = ["detections", "environmental"]
        if include_acoustic_indices:
            data_types.append("indices")
        
        # Check and sync each type
        for data_type in data_types:
            if force_sync:
                if verbose:
                    print(f"  Force syncing {data_type}...")
                ensure_data_available(data_type, verbose=False)
            else:
                status = check_data_freshness(data_type, verbose=False)
                if status.get("needs_update") or status.get("missing"):
                    if verbose:
                        updates = len(status.get("needs_update", []))
                        missing = len(status.get("missing", []))
                        print(f"  📥 {data_type}: {updates} updates, {missing} missing files")
                    ensure_data_available(data_type, verbose=False)
                elif verbose:
                    print(f"  ✅ {data_type}: up-to-date")
    
    # Now load the processed data
    if verbose:
        print("\n📊 Loading processed data...")
    
    return load_processed_data(
        include_acoustic_indices=include_acoustic_indices,
        verbose=verbose
    )


def load_acoustic_indices_with_sync(check_updates: bool = True,
                                   force_sync: bool = False,
                                   verbose: bool = True) -> pd.DataFrame:
    """
    Load acoustic indices with automatic CDN sync if needed.
    
    Args:
        check_updates: Whether to check for updates
        force_sync: Force sync even if data appears up-to-date
        verbose: Whether to print progress
        
    Returns:
        DataFrame with acoustic indices
    """
    if check_updates or force_sync:
        if verbose:
            print("🔄 Checking for acoustic indices updates...")
        
        if force_sync:
            ensure_data_available("indices", verbose=verbose)
        else:
            status = check_data_freshness("indices", verbose=False)
            if status.get("needs_update") or status.get("missing"):
                if verbose:
                    print("  📥 Updates available, syncing...")
                ensure_data_available("indices", verbose=verbose)
            elif verbose:
                print("  ✅ Acoustic indices up-to-date")
    
    return load_acoustic_indices(verbose=verbose)


def smart_load(data_requested: List[str] = None,
              auto_sync: bool = True,
              verbose: bool = True) -> Dict[str, Any]:
    """
    Smart loader that returns requested datasets as a dictionary.
    
    This provides maximum flexibility for loading specific datasets.
    
    Args:
        data_requested: List of dataset names to load. Options:
            - "detections": Detection/annotation data
            - "environmental": Temperature and depth data
            - "species": Species metadata
            - "stations": Station metadata
            - "acoustic_indices": Acoustic indices data
            - "metadata": Processing metadata
            Default is ["detections", "environmental", "species", "stations"]
        auto_sync: Whether to check for updates and sync if needed
        verbose: Whether to print progress
        
    Returns:
        Dictionary with requested datasets
        
    Example:
        >>> # Load specific datasets
        >>> data = smart_load(["detections", "acoustic_indices"])
        >>> detections_df = data["detections"]
        >>> indices_df = data["acoustic_indices"]
        
        >>> # Load everything
        >>> all_data = smart_load(["detections", "environmental", 
        ...                       "species", "stations", 
        ...                       "acoustic_indices", "metadata"])
    """
    if data_requested is None:
        data_requested = ["detections", "environmental", "species", "stations"]
    
    # Check what we need to sync
    needs_indices = "acoustic_indices" in data_requested
    needs_core = any(d in data_requested for d in 
                     ["detections", "environmental", "species", "stations"])
    
    # Sync if requested
    if auto_sync:
        if needs_core:
            *core_data, = load_with_auto_sync(
                include_acoustic_indices=needs_indices,
                verbose=verbose
            )
        elif needs_indices:
            indices = load_acoustic_indices_with_sync(verbose=verbose)
    else:
        # Just load without syncing
        if needs_core:
            *core_data, = load_processed_data(
                include_acoustic_indices=needs_indices,
                verbose=verbose
            )
        elif needs_indices:
            from .data_loader import load_acoustic_indices
            indices = load_acoustic_indices(verbose=verbose)
    
    # Build result dictionary
    result = {}
    
    if needs_core:
        if needs_indices and len(core_data) == 5:
            # Unpack with indices
            detections, environmental, species, stations, indices = core_data
            if "acoustic_indices" in data_requested:
                result["acoustic_indices"] = indices
        else:
            # Unpack without indices
            detections, environmental, species, stations = core_data[:4]
        
        if "detections" in data_requested:
            result["detections"] = detections
        if "environmental" in data_requested:
            result["environmental"] = environmental
        if "species" in data_requested:
            result["species"] = species
        if "stations" in data_requested:
            result["stations"] = stations
    
    elif needs_indices and "acoustic_indices" in data_requested:
        result["acoustic_indices"] = indices
    
    # Load metadata if requested
    if "metadata" in data_requested:
        from .data_loader import load_metadata
        result["metadata"] = load_metadata(verbose=False)
    
    return result


# Example usage
if __name__ == "__main__":
    """Example usage of auto-loading functions."""
    
    print("MBON Auto-Loader Examples")
    print("=" * 50)
    
    # Example 1: Auto-sync and load
    print("\n1. Auto-sync and load core data:")
    detections, environmental, species, stations = load_with_auto_sync()
    print(f"   Loaded {len(detections)} detections")
    
    # Example 2: Smart load specific datasets
    print("\n2. Smart load specific datasets:")
    data = smart_load(["detections", "acoustic_indices"])
    print(f"   Detections shape: {data['detections'].shape}")
    if "acoustic_indices" in data:
        print(f"   Indices shape: {data['acoustic_indices'].shape}")