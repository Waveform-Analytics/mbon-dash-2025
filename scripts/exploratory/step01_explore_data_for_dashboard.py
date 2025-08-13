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
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set up visualization defaults - use non-interactive backend
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load all available datasets from processed JSON files."""
    
    # Get the project root directory (2 levels up from this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    data_dir = project_root / "data" / "cdn" / "processed"
    
    print(f"Loading data from: {data_dir}")
    
    # Check if directory exists
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    print("Loading data...")
    
    # Load detection data
    with open(data_dir / "detections.json", 'r') as f:
        detections = pd.DataFrame(json.load(f))
    print(f"  ✓ Loaded {len(detections):,} detection records")
    
    # Load environmental data
    with open(data_dir / "environmental.json", 'r') as f:
        environmental = pd.DataFrame(json.load(f))
    print(f"  ✓ Loaded {len(environmental):,} environmental records")
    
    # Load species metadata
    with open(data_dir / "species.json", 'r') as f:
        species_meta = json.load(f)
    print(f"  ✓ Loaded {len(species_meta)} species definitions")
    
    # Load station metadata
    with open(data_dir / "stations.json", 'r') as f:
        stations = json.load(f)
    print(f"  ✓ Loaded {len(stations)} station definitions")
    
    return detections, environmental, species_meta, stations


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


def get_species_columns(df, species_meta):
    """Identify which columns are species/detection columns."""
    
    # Get short names from species metadata
    species_cols = [s['short_name'] for s in species_meta]
    
    # Find which columns exist in the dataframe AND are numeric
    available_species = []
    for col in species_cols:
        if col in df.columns:
            # Only include if column is numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                available_species.append(col)
            else:
                print(f"  ! Skipping {col}: not numeric (type: {df[col].dtype})")
    
    print(f"\nFound {len(available_species)} numeric species/detection columns:")
    
    # Separate biological vs non-biological
    biological = []
    non_biological = []
    
    for sp in species_meta:
        if sp['short_name'] in available_species:
            if sp['category'] in ['anthropogenic_environmental', 'other']:
                non_biological.append(sp)
            else:
                biological.append(sp)
    
    print(f"  - {len(biological)} biological species")
    print(f"  - {len(non_biological)} non-biological sounds (vessels, etc.)")
    
    return available_species, biological, non_biological


# ============================================================================
# EXPLORATORY ANALYSIS
# ============================================================================

def explore_temporal_patterns(df, species_cols):
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
    
    # Plot monthly patterns for top species
    top_species = df[species_cols].sum().nlargest(5).index
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Monthly Detection Patterns - Top Species")
    
    for idx, species in enumerate(top_species[:6]):
        ax = axes[idx // 3, idx % 3]
        
        for station in df['station'].unique():
            station_data = df[df['station'] == station].groupby('month')[species].sum()
            ax.plot(station_data.index, station_data.values, marker='o', label=station)
        
        ax.set_title(species)
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
    filename = figures_dir / "step01_monthly_detection_patterns_top_species.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved plot: {filename.name}")
    
    # 3. Seasonal patterns
    seasonal = df.groupby(['season', 'station'])[species_cols].sum()
    print(f"\nSeasonal summary shape: {seasonal.shape}")
    
    # 4. Year-over-year comparison
    yearly = df.groupby(['year', 'station'])[species_cols].sum()
    print(f"\nYearly summary shape: {yearly.shape}")
    
    return monthly, seasonal, yearly


def explore_station_patterns(df, species_cols):
    """Explore differences between stations."""
    
    print("\n" + "="*60)
    print("STATION COMPARISON EXPLORATION")
    print("="*60)
    
    # Station activity levels
    station_activity = df.groupby('station')[species_cols].sum()
    
    # Plot station comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for idx, station in enumerate(station_activity.index):
        ax = axes[idx]
        
        # Get top 10 species for this station
        top_10 = station_activity.loc[station].nlargest(10)
        
        ax.barh(range(len(top_10)), top_10.values)
        ax.set_yticks(range(len(top_10)))
        ax.set_yticklabels(top_10.index)
        ax.set_xlabel('Total Detections')
        ax.set_title(f'Station {station} - Top 10 Species')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create figures directory if it doesn't exist
    script_dir = Path(__file__).resolve().parent
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    # Save with informative filename
    filename = figures_dir / "step01_station_comparison_top10_species.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved plot: {filename.name}")
    
    return station_activity


def explore_species_patterns(df, species_cols, biological, non_biological):
    """Explore species co-occurrence and patterns."""
    
    print("\n" + "="*60)
    print("SPECIES PATTERN EXPLORATION")
    print("="*60)
    
    # Species co-occurrence matrix
    species_data = df[species_cols]
    
    # Convert to binary presence/absence for co-occurrence
    species_binary = (species_data > 0).astype(int)
    co_occurrence = species_binary.T.dot(species_binary)
    
    # Plot co-occurrence heatmap for top species
    top_species = species_data.sum().nlargest(15).index
    co_occur_subset = co_occurrence.loc[top_species, top_species]
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(co_occur_subset, annot=True, fmt='d', cmap='YlOrRd', 
                cbar_kws={'label': 'Co-occurrence Count'})
    plt.title('Species Co-occurrence Matrix (Top 15)')
    plt.tight_layout()
    
    # Create figures directory if it doesn't exist
    script_dir = Path(__file__).resolve().parent
    figures_dir = script_dir / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    # Save with informative filename
    filename = figures_dir / "step01_species_cooccurrence_matrix_top15.png"
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved plot: {filename.name}")
    
    # Biological vs non-biological patterns
    bio_cols = [s['short_name'] for s in biological if s['short_name'] in species_cols]
    non_bio_cols = [s['short_name'] for s in non_biological if s['short_name'] in species_cols]
    
    bio_activity = df[bio_cols].sum().sum()
    non_bio_activity = df[non_bio_cols].sum().sum()
    
    print(f"\nActivity breakdown:")
    print(f"  Biological sounds: {bio_activity:,.0f} detections")
    print(f"  Non-biological sounds: {non_bio_activity:,.0f} detections")
    
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

def create_dashboard_views(df, species_cols):
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
    monthly = df.set_index('date').groupby([pd.Grouper(freq='M'), 'station']).sum(numeric_only=True)
    views['monthly_by_station'] = monthly.reset_index().to_dict('records')
    print(f"  ✓ Monthly aggregation: {len(monthly)} records")
    
    # 3. Species rankings
    species_totals = df[species_cols].sum().sort_values(ascending=False)
    views['species_rankings'] = [
        {'species': sp, 'total': int(total)} 
        for sp, total in species_totals.items()
    ]
    print(f"  ✓ Species rankings: {len(species_totals)} species")
    
    # 4. Station summaries
    station_summaries = []
    for station in df['station'].unique():
        station_data = df[df['station'] == station]
        station_summaries.append({
            'station': station,
            'total_detections': int(station_data[species_cols].sum().sum()),
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
    
    # Load data
    detections, environmental, species_meta, stations = load_data()
    
    # Prepare detection data
    detections = prepare_detection_data(detections)
    
    # Get species columns
    species_cols, biological, non_biological = get_species_columns(detections, species_meta)
    
    # Add a breakpoint here to explore the prepared data
    print("\n🔍 Data loaded and prepared. Add breakpoint here to explore.")
    # breakpoint()
    
    # Explore temporal patterns
    monthly, seasonal, yearly = explore_temporal_patterns(detections, species_cols)
    
    # Explore station patterns
    station_activity = explore_station_patterns(detections, species_cols)
    
    # Explore species patterns
    co_occurrence = explore_species_patterns(detections, species_cols, biological, non_biological)
    
    # Explore environmental relationships
    explore_environmental_relationships(detections, environmental)
    
    # Create dashboard views
    dashboard_views = create_dashboard_views(detections, species_cols)
    
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
    print("  - detections: Full detection dataframe")
    print("  - environmental: Environmental data")
    print("  - dashboard_views: Pre-aggregated views for dashboard")
    print("\nAdd breakpoints or modify visualizations as needed!")