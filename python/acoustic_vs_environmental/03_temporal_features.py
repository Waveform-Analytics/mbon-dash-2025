#!/usr/bin/env python3
"""
PHASE 3: TEMPORAL FEATURE ENGINEERING
=====================================
Goal: Create time-aware features from selected acoustic indices and environmental variables
      to capture temporal patterns, trends, and contextual information for improved prediction.

Features to engineer:
1. Rolling window statistics (mean, std, min, max) over multiple time horizons
2. Lag features (values from previous time periods) 
3. Temporal trends (local slopes, changes)
4. Seasonal/cyclical patterns (hour-of-day, day-of-week effects)
5. Recent activity context (biological activity in recent windows)

This phase focuses on the top-performing features from Phase 2 to avoid feature explosion.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def create_rolling_features(df, feature_cols, windows=[4, 12, 24]):
    """
    Create rolling window statistics for specified features.
    
    Args:
        df: DataFrame with datetime index and features
        feature_cols: List of column names to create rolling features for
        windows: List of window sizes (in 2-hour periods)
    
    Returns:
        DataFrame with added rolling features
    """
    print(f"🔄 Creating rolling features for {len(feature_cols)} features...")
    
    result = df.copy()
    
    for window in windows:
        print(f"  📊 Window: {window} periods ({window*2} hours)")
        
        for col in feature_cols:
            if col not in df.columns:
                continue
                
            # Rolling statistics
            rolling = df.groupby('station')[col].rolling(window, min_periods=1)
            
            result[f'{col}_roll_{window}h_mean'] = rolling.mean().values
            result[f'{col}_roll_{window}h_std'] = rolling.std().fillna(0).values
            result[f'{col}_roll_{window}h_min'] = rolling.min().values
            result[f'{col}_roll_{window}h_max'] = rolling.max().values
            
    print(f"✅ Added {len(windows) * 4 * len(feature_cols)} rolling features")
    return result

def create_lag_features(df, feature_cols, lags=[1, 2, 4, 8]):
    """
    Create lag features (values from previous time periods).
    
    Args:
        df: DataFrame with datetime index and features
        feature_cols: List of column names to create lag features for
        lags: List of lag periods (in 2-hour periods)
    
    Returns:
        DataFrame with added lag features
    """
    print(f"🔄 Creating lag features for {len(feature_cols)} features...")
    
    result = df.copy()
    
    for lag in lags:
        print(f"  ⏰ Lag: {lag} periods ({lag*2} hours)")
        
        for col in feature_cols:
            if col not in df.columns:
                continue
                
            # Lag features by station
            result[f'{col}_lag_{lag}h'] = df.groupby('station')[col].shift(lag)
            
    print(f"✅ Added {len(lags) * len(feature_cols)} lag features")
    return result

def create_trend_features(df, feature_cols, windows=[4, 12]):
    """
    Create trend features (local slopes and changes).
    
    Args:
        df: DataFrame with datetime index and features
        feature_cols: List of column names to create trend features for  
        windows: List of window sizes for trend calculation
    
    Returns:
        DataFrame with added trend features
    """
    print(f"🔄 Creating trend features for {len(feature_cols)} features...")
    
    result = df.copy()
    
    for window in windows:
        print(f"  📈 Trend window: {window} periods ({window*2} hours)")
        
        for col in feature_cols:
            if col not in df.columns:
                continue
                
            # Calculate linear trend (slope) over rolling window
            def calculate_slope(series):
                if len(series) < 2:
                    return 0
                x = np.arange(len(series))
                y = series.values
                if np.var(x) == 0:
                    return 0
                slope = np.cov(x, y)[0,1] / np.var(x)
                return slope
            
            trend = df.groupby('station')[col].rolling(window, min_periods=2).apply(calculate_slope)
            result[f'{col}_trend_{window}h'] = trend.values
            
            # Change from window periods ago
            result[f'{col}_change_{window}h'] = df.groupby('station')[col].diff(window)
            
    print(f"✅ Added {len(windows) * 2 * len(feature_cols)} trend features")
    return result

def create_temporal_context_features(df):
    """
    Create temporal context features (hour, day patterns).
    
    Args:
        df: DataFrame with datetime index
    
    Returns:
        DataFrame with added temporal context features
    """
    print("🔄 Creating temporal context features...")
    
    result = df.copy()
    
    # Hour of day (cyclical encoding)
    hour = df['datetime'].dt.hour
    result['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    result['hour_cos'] = np.cos(2 * np.pi * hour / 24)
    
    # Day of week (cyclical encoding) 
    day_of_week = df['datetime'].dt.dayofweek
    result['dow_sin'] = np.sin(2 * np.pi * day_of_week / 7)
    result['dow_cos'] = np.cos(2 * np.pi * day_of_week / 7)
    
    # Month (cyclical encoding)
    month = df['datetime'].dt.month
    result['month_sin'] = np.sin(2 * np.pi * month / 12)
    result['month_cos'] = np.cos(2 * np.pi * month / 12)
    
    print("✅ Added 6 temporal context features")
    return result

def create_biological_context_features(df, windows=[4, 12, 24]):
    """
    Create biological context features (recent activity patterns).
    
    Args:
        df: DataFrame with biological activity targets
        windows: List of window sizes for activity context
    
    Returns:
        DataFrame with added biological context features
    """
    print("🔄 Creating biological context features...")
    
    result = df.copy()
    
    # Rolling activity statistics
    for window in windows:
        print(f"  🐟 Activity window: {window} periods ({window*2} hours)")
        
        rolling = df.groupby('station')['any_activity'].rolling(window, min_periods=1)
        result[f'recent_activity_rate_{window}h'] = rolling.mean().values
        
        # Activity change indicators
        result[f'activity_increasing_{window}h'] = (
            result[f'recent_activity_rate_{window}h'] > 
            df.groupby('station')['any_activity'].rolling(window*2, min_periods=1).mean().values
        ).astype(int)
    
    print(f"✅ Added {len(windows) * 2} biological context features")
    return result

def load_selected_features():
    """Load the selected acoustic indices from Phase 2."""
    selected_path = Path("selected_acoustic_indices.csv")
    if not selected_path.exists():
        raise FileNotFoundError("Selected acoustic indices file not found. Run Phase 2 first.")
    
    selected_df = pd.read_csv(selected_path)
    acoustic_features = selected_df['acoustic_index'].tolist()
    
    # Environmental features (from Phase 2 analysis)
    environmental_features = [
        'Low (50-1200 Hz)', 'Water temp (°C)', 'Broadband (1-40000 Hz)', 
        'High (7000-40000 Hz)', 'Mid (1200-7000 Hz)'
    ]
    
    return acoustic_features, environmental_features

def main():
    print("🔄 PHASE 3: TEMPORAL FEATURE ENGINEERING")
    print("=" * 70)
    print("Goal: Create time-aware features to capture temporal patterns")
    print("Focus: Top-performing features from Phase 2 analysis")
    
    # Load aligned dataset
    data_path = Path("data_01_aligned_2021.csv") 
    if not data_path.exists():
        raise FileNotFoundError("Aligned dataset not found. Run Phase 1 first.")
    
    print("✅ Loading aligned dataset...")
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    print(f"   Dataset shape: {df.shape}")
    print(f"   Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"   Stations: {sorted(df['station'].unique())}")
    
    # Load selected features
    print("\n📋 Loading selected features from Phase 2...")
    acoustic_features, environmental_features = load_selected_features()
    
    print(f"   Selected acoustic indices: {len(acoustic_features)}")
    print(f"   Environmental features: {len(environmental_features)}")
    
    # Verify features exist in dataset
    missing_acoustic = [f for f in acoustic_features if f not in df.columns]
    missing_environmental = [f for f in environmental_features if f not in df.columns]
    
    if missing_acoustic:
        print(f"⚠️  Missing acoustic features: {missing_acoustic}")
        acoustic_features = [f for f in acoustic_features if f in df.columns]
    
    if missing_environmental:
        print(f"⚠️  Missing environmental features: {missing_environmental}")
        environmental_features = [f for f in environmental_features if f in df.columns]
    
    print(f"   Final acoustic features: {len(acoustic_features)}")
    print(f"   Final environmental features: {len(environmental_features)}")
    
    # Sort by datetime and station for proper time series operations
    df = df.sort_values(['station', 'datetime']).reset_index(drop=True)
    
    # Track original feature count
    original_features = df.shape[1]
    
    print("\n🛠️  TEMPORAL FEATURE ENGINEERING PIPELINE")
    print("=" * 50)
    
    # 1. Rolling window features for top acoustic indices
    print("\n1. 🎵 Acoustic Rolling Features")
    df = create_rolling_features(df, acoustic_features, windows=[4, 12, 24])
    
    # 2. Rolling window features for environmental variables (fewer windows to control size)
    print("\n2. 🌡️ Environmental Rolling Features") 
    df = create_rolling_features(df, environmental_features, windows=[4, 12])
    
    # 3. Lag features for key indices
    print("\n3. ⏰ Lag Features")
    key_features = acoustic_features[:5] + environmental_features[:3]  # Limit to top features
    df = create_lag_features(df, key_features, lags=[1, 2, 4, 8])
    
    # 4. Trend features
    print("\n4. 📈 Trend Features")
    df = create_trend_features(df, key_features, windows=[4, 12])
    
    # 5. Temporal context
    print("\n5. ⏰ Temporal Context Features")
    df = create_temporal_context_features(df)
    
    # 6. Biological context features
    print("\n6. 🐟 Biological Context Features")
    df = create_biological_context_features(df, windows=[4, 12, 24])
    
    # Summary
    new_features = df.shape[1] - original_features
    print(f"\n📊 TEMPORAL ENGINEERING SUMMARY")
    print("=" * 40)
    print(f"   Original features: {original_features}")
    print(f"   Added features: {new_features}")
    print(f"   Total features: {df.shape[1]}")
    print(f"   Dataset shape: {df.shape}")
    
    # Check for any issues
    print("\n🔍 QUALITY CHECK")
    print("=" * 20)
    null_counts = df.isnull().sum()
    features_with_nulls = null_counts[null_counts > 0]
    
    if len(features_with_nulls) > 0:
        print(f"⚠️  Features with nulls: {len(features_with_nulls)}")
        print("   Top 10 features with most nulls:")
        for feat, count in features_with_nulls.head(10).items():
            print(f"     {feat}: {count} nulls ({count/len(df):.1%})")
    else:
        print("✅ No null values found")
    
    # Identify feature categories for analysis
    feature_categories = {
        'original': [col for col in df.columns if not any(x in col for x in ['_roll_', '_lag_', '_trend_', '_change_', 'hour_', 'dow_', 'month_', 'recent_activity', 'activity_increasing'])],
        'rolling': [col for col in df.columns if '_roll_' in col],
        'lag': [col for col in df.columns if '_lag_' in col], 
        'trend': [col for col in df.columns if any(x in col for x in ['_trend_', '_change_'])],
        'temporal': [col for col in df.columns if any(x in col for x in ['hour_', 'dow_', 'month_'])],
        'biological': [col for col in df.columns if any(x in col for x in ['recent_activity', 'activity_increasing'])]
    }
    
    print(f"\n📋 FEATURE BREAKDOWN BY TYPE")
    print("=" * 35)
    for category, features in feature_categories.items():
        print(f"   {category.capitalize()}: {len(features)}")
    
    # Save enhanced dataset
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "temporal_features_dataset.csv"
    print(f"\n💾 Saving enhanced dataset to: {output_path}")
    df.to_csv(output_path, index=False)
    
    # Save feature metadata
    feature_metadata = {
        'creation_timestamp': datetime.now().isoformat(),
        'original_features': original_features,
        'added_features': new_features,
        'total_features': df.shape[1],
        'dataset_shape': df.shape,
        'feature_categories': {k: len(v) for k, v in feature_categories.items()},
        'selected_acoustic_features': acoustic_features,
        'selected_environmental_features': environmental_features,
        'feature_engineering_config': {
            'rolling_windows': [4, 12, 24],
            'lag_periods': [1, 2, 4, 8],
            'trend_windows': [4, 12],
            'biological_context_windows': [4, 12, 24]
        }
    }
    
    metadata_path = output_dir / "phase3_temporal_features_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(feature_metadata, f, indent=2, default=str)
    
    print(f"💾 Saved feature metadata to: {metadata_path}")
    print(f"📊 Dataset size: {output_path.stat().st_size / (1024*1024):.1f} MB")
    
    print("\n🎉 PHASE 3 COMPLETE!")
    print("=" * 25)
    print("✅ Created comprehensive temporal features")
    print("✅ Enhanced dataset with time-aware patterns")
    print("✅ Preserved data quality and relationships")
    print("✅ Ready for Phase 4: Advanced modeling")
    
    return df

if __name__ == "__main__":
    main()