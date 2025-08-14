#!/usr/bin/env python3
"""
Exploratory data analysis for the Data Explorer dashboard page.

This script is designed for interactive exploration - add breakpoints,
modify visualizations, and experiment with different aggregations to
find the most interesting patterns.

Usage:
    uv run scripts/exploratory/step01_explore_data_for_dashboard.py
"""

import pandas as pd
import numpy as np
import json
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Package is installed in editable mode, no path manipulation needed

# Import from mbon_analysis package
from mbon_analysis.core import load_processed_data

# Set up visualization defaults - use non-interactive backend
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)

# ============================================================================
# DATA LOADING
# ============================================================================
# Data loading is now handled by mbon_analysis.core.load_processed_data


# ============================================================================
# DATA PREPARATION
# ============================================================================

def prepare_detection_data(df):
    """Prepare detection data for analysis."""
    
    # Convert date columns to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Clean mixed data type columns - convert to numeric where possible
    mixed_columns = ['fic', 'bde', 'bdbp', 'none']
    for col in mixed_columns:
        if col in df.columns:
            # Convert to numeric, replacing non-numeric values with NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"  ✓ Cleaned {col}: converted to numeric")
    
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


def get_detection_columns(df, detection_meta):
    """Identify which columns are detection/annotation columns based on updated metadata."""
    
    # Get short names from detection metadata and filter for bio/anthro types only
    detection_cols = []
    biological = []
    anthropogenic = []
    
    for item in detection_meta:
        short_name = item['short_name']
        detection_type = item.get('type', item.get('category', 'unknown'))  # Prefer new 'type' field over old 'category'
        
        # Only include bio and anthro types as detections
        if detection_type in ['bio', 'anthro'] and short_name in df.columns:
            # Only include if column is numeric
            if pd.api.types.is_numeric_dtype(df[short_name]):
                detection_cols.append(short_name)
                
                if detection_type == 'bio':
                    biological.append(item)
                elif detection_type == 'anthro':
                    anthropogenic.append(item)
            else:
                print(f"  ! Skipping {short_name}: not numeric (type: {df[short_name].dtype})")
        elif detection_type in ['info', 'none']:
            # Skip info and none columns - these are metadata or empty
            continue
        elif short_name in df.columns:
            print(f"  ! Skipping {short_name}: type '{detection_type}' not bio/anthro")
    
    print(f"\nFound {len(detection_cols)} detection/annotation columns:")
    print(f"  - {len(biological)} biological species")
    print(f"  - {len(anthropogenic)} anthropogenic sounds (vessels, etc.)")
    
    return detection_cols, biological, anthropogenic


# ============================================================================
# EXPLORATORY ANALYSIS
# ============================================================================

def explore_temporal_patterns(df, detection_cols):
    """Explore different temporal aggregations to find interesting patterns."""
    
    print("\n" + "="*60)
    print("TEMPORAL PATTERN EXPLORATION")
    print("="*60)
    
    # Set a breakpoint here to explore the data structure
    # breakpoint()
    
    # 1. Overall temporal coverage
    print(f"\nTemporal coverage:")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Years: {sorted(df['year'].unique())}")
    print(f"  Stations: {sorted(df['station'].unique())}")
    
    # 2. Monthly patterns
    monthly = df.groupby(['year', 'month', 'station']).sum(numeric_only=True)
    
    # Plot monthly patterns for top annotations/detections (both bio and anthro)
    top_detections = df[detection_cols].sum().nlargest(5).index
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Monthly Detection Patterns - Top Annotations")
    
    for idx, detection in enumerate(top_detections[:6]):
        ax = axes[idx // 3, idx % 3]
        
        for station in df['station'].unique():
            station_data = df[df['station'] == station].groupby('month')[detection].sum()
            ax.plot(station_data.index, station_data.values, marker='o', label=station)
        
        ax.set_title(detection)
        ax.set_xlabel('Month')
        ax.set_ylabel('Detections')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create figures directory if it doesn't exist
    script_dir = Path(__file__).resolve().parent
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    # Save with informative filename
    filename = figures_dir / "step01_monthly_detection_patterns_top_annotations.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved plot: {filename.name}")
    
    # 3. Seasonal patterns
    seasonal = df.groupby(['season', 'station'])[detection_cols].sum()
    print(f"\nSeasonal summary shape: {seasonal.shape}")
    
    # 4. Year-over-year comparison
    yearly = df.groupby(['year', 'station'])[detection_cols].sum()
    print(f"\nYearly summary shape: {yearly.shape}")
    
    return monthly, seasonal, yearly


def explore_station_patterns(df, detection_cols):
    """Explore differences between stations."""
    
    print("\n" + "="*60)
    print("STATION COMPARISON EXPLORATION")
    print("="*60)
    
    # Station activity levels
    station_activity = df.groupby('station')[detection_cols].sum()
    
    # Plot station comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, station in enumerate(station_activity.index):
        ax = axes[idx]
        
        # Get top 10 annotations for this station (bio + anthro)
        top_10 = station_activity.loc[station].nlargest(10)
        
        ax.barh(range(len(top_10)), top_10.values)
        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels(top_10.index)
        ax.set_xlabel('Total Detections')
        ax.set_title(f'Station {station} - Top 10 Annotations')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create figures directory if it doesn't exist
    script_dir = Path(__file__).resolve().parent
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    # Save with informative filename
    filename = figures_dir / "step01_station_comparison_top10_annotations.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved plot: {filename.name}")
    
    return station_activity


def explore_detection_patterns(df, detection_cols, biological, anthropogenic):
    """Explore detection co-occurrence and patterns for both biological species and anthropogenic sounds."""
    
    print("\n" + "="*60)
    print("DETECTION PATTERN EXPLORATION")
    print("="*60)
    
    # Detection co-occurrence matrix (includes both biological and anthropogenic)
    detection_data = df[detection_cols]
    
    # Convert to binary presence/absence for co-occurrence
    detection_binary = (detection_data > 0).astype(int)
    co_occurrence = detection_binary.T.dot(detection_binary)
    
    # Plot co-occurrence heatmap for top detections
    top_detections = detection_data.sum().nlargest(15).index
    co_occur_subset = co_occurrence.loc[top_detections, top_detections]
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(co_occur_subset, annot=True, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Co-occurrence Count'})
    plt.title('Detection Co-occurrence Matrix (Top 15)')
    plt.tight_layout()
    
    # Create figures directory if it doesn't exist
    script_dir = Path(__file__).resolve().parent
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    # Save with informative filename
    filename = figures_dir / "step01_detection_cooccurrence_matrix_top15.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved plot: {filename.name}")
    
    # Biological vs anthropogenic patterns
    bio_cols = [item['short_name'] for item in biological if item['short_name'] in detection_cols]
    anthro_cols = [item['short_name'] for item in anthropogenic if item['short_name'] in detection_cols]
    
    bio_activity = df[bio_cols].sum().sum()
    anthro_activity = df[anthro_cols].sum().sum()
    
    print(f"\nActivity breakdown:")
    print(f"  Biological species: {bio_activity:,.0f} detections")
    print(f"  Anthropogenic sounds: {anthro_activity:,.0f} detections")
    
    return co_occurrence


def explore_environmental_relationships(df, environmental):
    """Explore relationships between detections and environmental conditions."""
    
    print("\n" + "="*60)
    print("ENVIRONMENTAL RELATIONSHIP EXPLORATION")
    print("="*60)
    
    # This would require merging detection and environmental data
    # Add breakpoint to explore merge strategies
    # breakpoint()
    
    print("Environmental data shape:", environmental.shape)
    print("Measurement types:", environmental['measurement_type'].unique() if 'measurement_type' in environmental.columns else "N/A")
    
    # Placeholder for environmental analysis
    # You can expand this section based on what patterns you find interesting
    
    return None


# ============================================================================
# DATA AGGREGATION FOR DASHBOARD
# ============================================================================

def create_dashboard_views(df, detection_cols):
    """Create pre-aggregated views optimized for dashboard display."""
    
    print("\n" + "="*60)
    print("CREATING DASHBOARD VIEWS")
    print("="*60)
    
    views = {}
    
    # 1. Daily aggregation (for timeline)
    daily = df.set_index('date').groupby([pd.Grouper(freq='D'), 'station']).sum(numeric_only=True)
    views['daily_by_station'] = daily.reset_index().to_dict('records')
    print(f"  ✓ Daily aggregation: {len(daily)} records")
    
    # 2. Monthly aggregation (for broader patterns)
    monthly = df.set_index('date').groupby([pd.Grouper(freq='ME'), 'station']).sum(numeric_only=True)
    views['monthly_by_station'] = monthly.reset_index().to_dict('records')
    print(f"  ✓ Monthly aggregation: {len(monthly)} records")
    
    # 3. Detection rankings (both biological and anthropogenic)
    detection_totals = df[detection_cols].sum().sort_values(ascending=False)
    views['detection_rankings'] = [
        {'detection': det, 'total': int(total)} 
        for det, total in detection_totals.items()
    ]
    print(f"  ✓ Detection rankings: {len(detection_totals)} detections")
    
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
    print(f"  ✓ Station summaries: {len(station_summaries)} stations")
    
    return views


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main exploration workflow."""
    
    # Load data using mbon_analysis package
    detections, environmental, detection_meta, stations = load_processed_data()
    
    # Prepare detection data
    detections = prepare_detection_data(detections)
    
    # Get detection columns (bio and anthro only)
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    
    # Add a breakpoint here to explore the prepared data
    print("\n🔍 Data loaded and prepared. Add breakpoint here to explore.")
    # breakpoint()
    
    # Explore temporal patterns
    monthly, seasonal, yearly = explore_temporal_patterns(detections, detection_cols)
    
    # Explore station patterns
    station_activity = explore_station_patterns(detections, detection_cols)
    
    # Explore detection patterns (both biological and anthropogenic)
    co_occurrence = explore_detection_patterns(detections, detection_cols, biological, anthropogenic)
    
    # Explore environmental relationships
    explore_environmental_relationships(detections, environmental)
    
    # Create dashboard views
    dashboard_views = create_dashboard_views(detections, detection_cols)
    
    # Save dashboard views
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    output_path = project_root / "data" / "intermediate_results" / "explorer_views.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(dashboard_views, f, indent=2, default=str)
    
    print(f"\n✅ Dashboard views saved to: {output_path}")
    
    # Final breakpoint for examining results
    print("\n🔍 Analysis complete. Add breakpoint here to examine results.")
    # breakpoint()
    
    return detections, environmental, dashboard_views


if __name__ == "__main__":
    detections, environmental, dashboard_views = main()
    
    print("\n" + "="*60)
    print("EXPLORATION COMPLETE")
    print("="*60)
    print("\nVariables available for further exploration:")
    print("  - detections: Full detection/annotation dataframe")
    print("  - environmental: Environmental data")
    print("  - dashboard_views: Pre-aggregated views for dashboard")
    print("\nAdd breakpoints or modify visualizations as needed!")