#!/usr/bin/env python3
"""
Create temporal lag and moving average features for acoustic indices 
to enable fair comparison with environmental temporal features.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def create_acoustic_temporal_features(df, indices_to_lag=None, lag_hours=[1, 2, 3], window_hours=[6, 12, 24]):
    """
    Create lag and moving average features for acoustic indices.
    
    Args:
        df: DataFrame with acoustic indices (must have datetime index)
        indices_to_lag: List of index names to create features for. If None, uses key indices
        lag_hours: List of lag periods in hours
        window_hours: List of moving average window sizes in hours
    
    Returns:
        DataFrame with original + temporal features
    """
    
    # Key acoustic indices to create temporal features for
    if indices_to_lag is None:
        indices_to_lag = [
            'ACI', 'ADI', 'AEI', 'BI', 'ENRf', 'NDSI', 
            'AnthroEnergy', 'BioEnergy', 'H_Renyi', 'RAOQ'
        ]
    
    # Filter to indices that actually exist in the data
    indices_to_lag = [idx for idx in indices_to_lag if idx in df.columns]
    
    print(f"Creating temporal features for {len(indices_to_lag)} acoustic indices:")
    print(f"  Indices: {indices_to_lag}")
    print(f"  Lag hours: {lag_hours}")
    print(f"  Moving average windows: {window_hours}")
    
    result_df = df.copy()
    
    # Sort by station and datetime to ensure proper temporal order
    result_df = result_df.sort_values(['station', 'datetime'])
    
    temporal_features = []
    
    for station in result_df['station'].unique():
        print(f"\nProcessing station {station}...")
        station_mask = result_df['station'] == station
        station_df = result_df[station_mask].set_index('datetime').sort_index()
        
        for index_name in indices_to_lag:
            if index_name in station_df.columns:
                # Create lag features
                for lag_h in lag_hours:
                    lag_col = f'{index_name}_lag_{lag_h}'
                    station_df[lag_col] = station_df[index_name].shift(lag_h)
                    temporal_features.append(lag_col)
                
                # Create moving averages
                for window_h in window_hours:
                    window_col = f'{index_name}_mean_{window_h}h'
                    station_df[window_col] = station_df[index_name].rolling(
                        window=window_h, min_periods=max(1, window_h//2)
                    ).mean()
                    temporal_features.append(window_col)
                
                # Create change features (similar to environmental)
                change_2h_col = f'{index_name}_change_2h'
                change_4h_col = f'{index_name}_change_4h'
                station_df[change_2h_col] = station_df[index_name] - station_df[index_name].shift(2)
                station_df[change_4h_col] = station_df[index_name] - station_df[index_name].shift(4)
                temporal_features.extend([change_2h_col, change_4h_col])
        
        # Update the main dataframe with station results
        station_df = station_df.reset_index()
        result_df.loc[station_mask, station_df.columns] = station_df.values
    
    # Remove duplicates from temporal_features list
    temporal_features = list(set(temporal_features))
    
    print(f"\n✅ Created {len(temporal_features)} acoustic temporal features:")
    print(f"   Sample features: {temporal_features[:10]}")
    
    return result_df, temporal_features

def main():
    data_dir = Path('../data')
    
    print("🔍 CREATING ACOUSTIC TEMPORAL FEATURES")
    print("="*50)
    
    # Load acoustic indices
    print("Loading acoustic indices...")
    indices_df = pd.read_parquet(data_dir / 'processed' / '02_acoustic_indices_aligned_2021.parquet')
    print(f"Original shape: {indices_df.shape}")
    
    # Create temporal features
    indices_enhanced, temporal_features = create_acoustic_temporal_features(indices_df)
    
    print(f"\n📊 RESULTS:")
    print(f"Enhanced shape: {indices_enhanced.shape}")
    print(f"Added {len(temporal_features)} temporal features")
    print(f"Original features: {indices_df.shape[1]}")
    print(f"New features: {indices_enhanced.shape[1] - indices_df.shape[1]}")
    
    # Save enhanced dataset
    output_path = data_dir / 'processed' / '02_acoustic_indices_with_temporal_features.parquet'
    indices_enhanced.to_parquet(output_path)
    print(f"\n💾 Saved enhanced acoustic indices to: {output_path}")
    
    # Create feature list for easy reference
    feature_info = {
        'original_features': [col for col in indices_df.columns if col not in ['datetime', 'station', 'year']],
        'temporal_features': temporal_features,
        'total_features': indices_enhanced.shape[1]
    }
    
    import json
    feature_info_path = data_dir / 'processed' / 'acoustic_temporal_features_info.json'
    with open(feature_info_path, 'w') as f:
        json.dump(feature_info, f, indent=2)
    print(f"💾 Saved feature info to: {feature_info_path}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Original acoustic features: {len(feature_info['original_features'])}")
    print(f"  New temporal features: {len(temporal_features)}")
    print(f"  Total features: {feature_info['total_features']}")
    print(f"\nReady for fair comparison with environmental temporal features!")

if __name__ == "__main__":
    main()