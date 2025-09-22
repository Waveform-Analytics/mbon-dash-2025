#!/usr/bin/env python3
"""
Phase 1: Data Loading and Initial Exploration

Load clean data from notebook 1 outputs and create 2-hour aligned dataset
matching the detection intervals. This creates the foundation for all
subsequent analysis phases.

Key outputs:
- Combined dataset aligned to 2-hour detection intervals  
- Basic exploratory statistics
- Data quality assessment
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
import numpy as np
from utils.data_utils import CleanDataLoader


def aggregate_to_2hour(df: pd.DataFrame, datetime_col: str = 'datetime', 
                      station_col: str = 'station') -> pd.DataFrame:
    """
    Aggregate data to 2-hour intervals to match detection data.
    
    Args:
        df: DataFrame with datetime and station columns
        datetime_col: Name of datetime column
        station_col: Name of station column
    
    Returns:
        DataFrame aggregated to 2-hour intervals
    """
    df_agg = df.copy()
    
    # Create 2-hour time bins (floor to even hours: 0, 2, 4, 6, etc.)
    df_agg[datetime_col] = pd.to_datetime(df_agg[datetime_col])
    df_agg['datetime_2h'] = df_agg[datetime_col].dt.floor('2h')
    
    # Group by station and 2-hour bins, aggregate numeric columns
    numeric_cols = df_agg.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in [station_col]]
    
    if not numeric_cols:
        print(f"⚠️  No numeric columns found for aggregation")
        return df_agg
    
    aggregated = (df_agg.groupby([station_col, 'datetime_2h'])[numeric_cols]
                  .mean()
                  .reset_index())
    
    # Rename datetime column back
    aggregated = aggregated.rename(columns={'datetime_2h': datetime_col})
    
    print(f"✓ Aggregated to 2-hour intervals: {df.shape} → {aggregated.shape}")
    return aggregated


def create_biological_targets(detections_df: pd.DataFrame, 
                            species_cols: list) -> pd.DataFrame:
    """
    Create biological target variables from detection data.
    
    Args:
        detections_df: Raw detections DataFrame
        species_cols: List of species column names
        
    Returns:
        DataFrame with target variables
    """
    targets_df = detections_df.copy()
    
    # Create community-level targets
    targets_df['total_fish_activity'] = targets_df[species_cols].sum(axis=1)
    targets_df['any_activity'] = (targets_df['total_fish_activity'] > 0).astype(int)
    targets_df['num_active_species'] = (targets_df[species_cols] > 0).sum(axis=1)
    
    # High activity threshold (75th percentile)
    activity_75th = targets_df['total_fish_activity'].quantile(0.75)
    targets_df['high_activity'] = (targets_df['total_fish_activity'] > activity_75th).astype(int)
    
    print(f"✓ Created biological targets:")
    print(f"   Any activity: {targets_df['any_activity'].mean():.1%} of time periods")
    print(f"   High activity (>75th): {targets_df['high_activity'].mean():.1%} of time periods")
    print(f"   Mean species per period: {targets_df['num_active_species'].mean():.1f}")
    
    return targets_df


def main():
    """Load and prepare all data for acoustic vs environmental analysis."""
    
    print("🔄 PHASE 1: DATA LOADING & PREPARATION")
    print("="*60)
    
    # Initialize data loader
    loader = CleanDataLoader()
    
    # Load all raw data
    print("\n📥 Loading raw data...")
    indices_df = loader.load_acoustic_indices()
    detections_df = loader.load_detections()
    env_df = loader.load_environmental()
    
    # Get feature column names
    acoustic_cols = loader.get_acoustic_index_names(indices_df)
    species_cols = loader.get_species_names(detections_df)
    
    print(f"\n📊 Raw data summary:")
    print(f"   Acoustic indices: {len(acoustic_cols)} features, {indices_df.shape[0]} observations")
    print(f"   Species detections: {len(species_cols)} species, {detections_df.shape[0]} observations")
    print(f"   Environmental: {env_df.shape[1]} columns, {env_df.shape[0]} observations")
    
    # Aggregate acoustic indices to 2-hour intervals
    print(f"\n⏰ Aggregating to 2-hour intervals...")
    indices_2h = aggregate_to_2hour(indices_df)
    env_2h = aggregate_to_2hour(env_df)
    
    # Create biological targets and align to 2-hour grid
    detections_df['datetime'] = pd.to_datetime(detections_df['datetime']).dt.floor('2h')
    targets_df = create_biological_targets(detections_df, species_cols)
    
    # Merge all data
    print(f"\n🔗 Merging datasets...")
    
    # Start with detection data as the base (it defines the 2-hour grid)
    merged_df = targets_df.copy()
    
    # Merge acoustic indices (use inner join to keep only overlapping times)
    print(f"   Detection data: {merged_df.shape}")
    merged_df = merged_df.merge(
        indices_2h,
        on=['datetime', 'station'],
        how='inner',
        suffixes=('', '_acoustic')
    )
    print(f"   After acoustic merge: {merged_df.shape}")
    
    # Merge environmental data
    merged_df = merged_df.merge(
        env_2h,
        on=['datetime', 'station'],
        how='left',
        suffixes=('', '_env')
    )
    print(f"   After environmental merge: {merged_df.shape}")
    
    # Clean up the merged dataset - only drop rows with missing values in key columns
    key_columns = ['datetime', 'station', 'any_activity', 'total_fish_activity'] + acoustic_cols[:5]
    available_key_columns = [col for col in key_columns if col in merged_df.columns]
    merged_df = merged_df.dropna(subset=available_key_columns)
    print(f"   After dropna (key columns only): {merged_df.shape}")
    
    print(f"✓ Final merged dataset: {merged_df.shape}")
    print(f"   Time range: {merged_df['datetime'].min()} to {merged_df['datetime'].max()}")
    print(f"   Stations: {sorted(merged_df['station'].unique())}")
    
    # Data quality check
    print(f"\n🔍 Data quality assessment:")
    missing_data = merged_df.isnull().sum()
    if missing_data.sum() > 0:
        print(f"   Missing values detected:")
        for col, count in missing_data[missing_data > 0].items():
            print(f"     {col}: {count} ({count/len(merged_df)*100:.1f}%)")
    else:
        print(f"   ✅ No missing values in final dataset")
    
    # Clean up problematic columns and data types before saving
    # Remove non-numeric columns that cause parquet issues
    problematic_cols = ['Date', 'Date ', 'Time', 'Deployment ID', 'Recorder type', 
                       'Sample Rate (Hz)', 'File number', 'Date and time_x', 'Date and time_y']
    cols_to_drop = [col for col in problematic_cols if col in merged_df.columns]
    if cols_to_drop:
        merged_df = merged_df.drop(columns=cols_to_drop)
        print(f"   Removed {len(cols_to_drop)} problematic columns")
    
    # Convert species columns to numeric (some have mixed types)
    for col in species_cols:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')
    
    # Save as CSV for now (parquet has arrow conversion issues with mixed types)
    output_path = Path("data_01_aligned_2021.csv")
    merged_df.to_csv(output_path, index=False)
    print(f"💾 Saved aligned dataset: {output_path}")
    
    # Feature summary for next phases
    available_acoustic_cols = [col for col in acoustic_cols if col in merged_df.columns]
    available_env_cols = [col for col in merged_df.columns 
                         if any(x in col.lower() for x in ['temp', 'depth', 'spl', 'broadband', 'low', 'high'])]
    
    print(f"\n📋 Features available for analysis:")
    print(f"   Acoustic indices: {len(available_acoustic_cols)}")
    print(f"   Environmental: {len(available_env_cols)}")
    print(f"   Target variables: any_activity, high_activity, total_fish_activity, num_active_species")
    
    # Basic target distribution
    print(f"\n🎯 Target variable distributions:")
    for target in ['any_activity', 'high_activity']:
        dist = merged_df[target].value_counts(normalize=True)
        print(f"   {target}: {dict(dist)}")
    
    return merged_df, available_acoustic_cols, available_env_cols


if __name__ == "__main__":
    merged_df, acoustic_cols, env_cols = main()
    print(f"\n🎉 Phase 1 complete! Ready for baseline comparison.")