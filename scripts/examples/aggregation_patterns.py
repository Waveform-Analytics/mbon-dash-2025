#!/usr/bin/env python3
"""
Common aggregation patterns for MBON data analysis.

This script is designed as a reference/example specifically for Python users. It
demonstrates various ways to aggregate detection data for different analysis needs -
from simple daily totals to complex multi-dimensional groupings. These patterns are
designed to work well with visualization libraries like Plotly, Matplotlib, and Seaborn.

Usage:
    uv run scripts/examples/aggregation_patterns.py
"""

import pandas as pd

# Import from mbon_analysis package
from mbon_analysis.core import (
    load_processed_data,
    prepare_detection_data,
    get_detection_columns
)


def temporal_aggregations(df, detection_cols):
    """
    Show different temporal aggregation patterns.
    """
    print("\n" + "="*60)
    print("TEMPORAL AGGREGATIONS")
    print("="*60)
    
    # ========================================================================
    # 1. DAILY AGGREGATIONS
    # ========================================================================
    print("\n1. Daily Activity Patterns")
    print("-" * 40)
    
    # Simple daily totals (all stations combined)
    daily_total = df.groupby(pd.Grouper(key='date', freq='D'))[detection_cols].sum()
    print(f"   Daily totals shape: {daily_total.shape}")
    print(f"   Date range: {daily_total.index[0]} to {daily_total.index[-1]}")
    
    # Daily by station (MultiIndex)
    daily_by_station = df.groupby([pd.Grouper(key='date', freq='D'), 'station'])[detection_cols].sum()
    print(f"   Daily by station shape: {daily_by_station.shape}")
    
    # For Plotly: Convert MultiIndex to columns
    daily_for_plotly = daily_by_station.reset_index()
    print(f"   Ready for Plotly shape: {daily_for_plotly.shape}")
    
    # ========================================================================
    # 2. WEEKLY AGGREGATIONS
    # ========================================================================
    print("\n2. Weekly Patterns")
    print("-" * 40)
    
    # Weekly totals with week starting on Monday
    weekly = df.groupby(pd.Grouper(key='date', freq='W-MON'))[detection_cols].sum()
    print(f"   Weekly totals shape: {weekly.shape}")
    
    # Weekly averages (useful for smoothing)
    weekly_avg = df.groupby(pd.Grouper(key='date', freq='W'))[detection_cols].mean()
    print(f"   Weekly averages shape: {weekly_avg.shape}")
    
    # ========================================================================
    # 3. MONTHLY AGGREGATIONS
    # ========================================================================
    print("\n3. Monthly Patterns")
    print("-" * 40)
    
    # Monthly totals
    monthly = df.groupby(pd.Grouper(key='date', freq='ME'))[detection_cols].sum()
    print(f"   Monthly totals shape: {monthly.shape}")
    
    # Month-Year with custom formatting
    df['month_year'] = df['date'].dt.to_period('M')
    monthly_custom = df.groupby('month_year')[detection_cols].sum()
    print(f"   Month-Year format shape: {monthly_custom.shape}")
    
    # Average by month of year (across all years)
    df['month_name'] = df['date'].dt.month_name()
    monthly_avg = df.groupby('month_name')[detection_cols].mean()
    print(f"   Average by month name: {monthly_avg.shape}")
    
    # ========================================================================
    # 4. SEASONAL AGGREGATIONS
    # ========================================================================
    print("\n4. Seasonal Patterns")
    print("-" * 40)
    
    # By season (already in prepared data)
    seasonal = df.groupby('season')[detection_cols].sum()
    print(f"   Seasonal totals shape: {seasonal.shape}")
    print(f"   Seasons: {seasonal.index.tolist()}")
    
    # Season by year
    seasonal_yearly = df.groupby(['year', 'season'])[detection_cols].sum()
    print(f"   Season by year shape: {seasonal_yearly.shape}")
    
    # ========================================================================
    # 5. HOURLY PATTERNS (Diel Analysis)
    # ========================================================================
    print("\n5. Hourly/Diel Patterns")
    print("-" * 40)
    
    # Extract hour for diel patterns
    df['hour'] = df['date'].dt.hour
    
    # Average activity by hour (across all days)
    hourly_avg = df.groupby('hour')[detection_cols].mean()
    print(f"   Hourly averages shape: {hourly_avg.shape}")
    
    # Hour by station
    hourly_station = df.groupby(['hour', 'station'])[detection_cols].mean()
    print(f"   Hourly by station shape: {hourly_station.shape}")
    
    # Day/Night comparison
    df['day_night'] = df['hour'].apply(lambda h: 'Day' if 6 <= h < 18 else 'Night')
    day_night = df.groupby('day_night')[detection_cols].sum()
    print(f"   Day/Night comparison shape: {day_night.shape}")
    
    return {
        'daily_total': daily_total,
        'daily_by_station': daily_by_station,
        'weekly': weekly,
        'monthly': monthly,
        'seasonal': seasonal,
        'hourly_avg': hourly_avg
    }


def spatial_aggregations(df, detection_cols):
    """
    Show different spatial/station aggregation patterns.
    """
    print("\n" + "="*60)
    print("SPATIAL AGGREGATIONS")
    print("="*60)
    
    # ========================================================================
    # 1. STATION COMPARISONS
    # ========================================================================
    print("\n1. Station Comparisons")
    print("-" * 40)
    
    # Total by station
    station_totals = df.groupby('station')[detection_cols].sum()
    print(f"   Station totals shape: {station_totals.shape}")
    
    # Average daily activity by station
    station_daily_avg = df.groupby('station')[detection_cols].mean()
    print(f"   Station daily averages shape: {station_daily_avg.shape}")
    
    # Station activity over time (pivot table)
    station_timeline = df.pivot_table(
        values=detection_cols[0],  # Use first detection type as example
        index=pd.Grouper(key='date', freq='ME'),
        columns='station',
        aggfunc='sum'
    )
    print(f"   Station timeline pivot shape: {station_timeline.shape}")
    
    # ========================================================================
    # 2. STATION-SPECIES MATRICES
    # ========================================================================
    print("\n2. Station-Species Matrices")
    print("-" * 40)
    
    # Station x Species total matrix
    station_species_matrix = df.groupby('station')[detection_cols].sum().T
    print(f"   Station-Species matrix shape: {station_species_matrix.shape}")
    print(f"   (rows=species, columns=stations)")
    
    # Normalized by station (percentage)
    station_species_pct = station_species_matrix.div(station_species_matrix.sum(axis=0), axis=1) * 100
    print(f"   Station-Species percentage shape: {station_species_pct.shape}")
    
    return {
        'station_totals': station_totals,
        'station_timeline': station_timeline,
        'station_species_matrix': station_species_matrix
    }


def species_focused_aggregations(df, detection_cols, biological, anthropogenic):
    """
    Show aggregations focused on species/detection types.
    """
    print("\n" + "="*60)
    print("SPECIES/DETECTION-FOCUSED AGGREGATIONS")
    print("="*60)
    
    # Get biological and anthropogenic columns
    bio_cols = [item['short_name'] for item in biological if item['short_name'] in detection_cols]
    anthro_cols = [item['short_name'] for item in anthropogenic if item['short_name'] in detection_cols]
    
    # ========================================================================
    # 1. TOP SPECIES ANALYSIS
    # ========================================================================
    print("\n1. Top Species Analysis")
    print("-" * 40)
    
    # Top 10 species overall
    species_totals = df[detection_cols].sum().sort_values(ascending=False)
    top_10_species = species_totals.head(10)
    print(f"   Top 10 species: {top_10_species.index.tolist()}")
    
    # Focus on top species over time
    top_species_monthly = df.groupby(pd.Grouper(key='date', freq='ME'))[top_10_species.index].sum()
    print(f"   Top species monthly shape: {top_species_monthly.shape}")
    
    # ========================================================================
    # 2. BIOLOGICAL VS ANTHROPOGENIC
    # ========================================================================
    print("\n2. Biological vs Anthropogenic")
    print("-" * 40)
    
    # Create summary columns
    df['bio_total'] = df[bio_cols].sum(axis=1) if bio_cols else 0
    df['anthro_total'] = df[anthro_cols].sum(axis=1) if anthro_cols else 0
    
    # Daily bio vs anthro
    bio_anthro_daily = df.groupby(pd.Grouper(key='date', freq='D'))[['bio_total', 'anthro_total']].sum()
    print(f"   Bio vs Anthro daily shape: {bio_anthro_daily.shape}")
    
    # Bio/Anthro ratio by station
    bio_anthro_station = df.groupby('station')[['bio_total', 'anthro_total']].sum()
    bio_anthro_station['bio_percentage'] = (bio_anthro_station['bio_total'] / 
                                           (bio_anthro_station['bio_total'] + bio_anthro_station['anthro_total']) * 100)
    print(f"   Bio/Anthro by station shape: {bio_anthro_station.shape}")
    
    # ========================================================================
    # 3. SPECIES CO-OCCURRENCE
    # ========================================================================
    print("\n3. Species Co-occurrence Patterns")
    print("-" * 40)
    
    # Binary presence/absence by day
    daily_presence = df.groupby(pd.Grouper(key='date', freq='D'))[detection_cols].sum()
    daily_presence_binary = (daily_presence > 0).astype(int)
    
    # Co-occurrence matrix
    co_occurrence = daily_presence_binary.T.dot(daily_presence_binary)
    print(f"   Co-occurrence matrix shape: {co_occurrence.shape}")
    
    return {
        'top_10_species': top_10_species,
        'bio_anthro_daily': bio_anthro_daily,
        'bio_anthro_station': bio_anthro_station,
        'co_occurrence': co_occurrence
    }


def advanced_aggregations(df, detection_cols):
    """
    Show more complex aggregation patterns.
    """
    print("\n" + "="*60)
    print("ADVANCED AGGREGATIONS")
    print("="*60)
    
    # ========================================================================
    # 1. ROLLING WINDOWS
    # ========================================================================
    print("\n1. Rolling Window Aggregations")
    print("-" * 40)
    
    # 7-day rolling average
    daily = df.groupby(pd.Grouper(key='date', freq='D'))[detection_cols[0]].sum()
    rolling_7d = daily.rolling(window=7, center=True).mean()
    print(f"   7-day rolling average shape: {rolling_7d.shape}")
    
    # 30-day rolling sum
    rolling_30d = daily.rolling(window=30).sum()
    print(f"   30-day rolling sum shape: {rolling_30d.shape}")
    
    # ========================================================================
    # 2. CUSTOM TIME BINS
    # ========================================================================
    print("\n2. Custom Time Binning")
    print("-" * 40)
    
    # Custom hour bins for diel analysis
    df['hour'] = df['date'].dt.hour
    df['time_period'] = pd.cut(df['hour'], 
                               bins=[0, 6, 12, 18, 24],
                               labels=['Night', 'Morning', 'Afternoon', 'Evening'],
                               include_lowest=True)
    
    time_period_activity = df.groupby('time_period', observed=False)[detection_cols].sum()
    print(f"   Time period activity shape: {time_period_activity.shape}")
    print(f"   Periods: {time_period_activity.index.tolist()}")
    
    # ========================================================================
    # 3. PERCENTILE AGGREGATIONS
    # ========================================================================
    print("\n3. Percentile-based Aggregations")
    print("-" * 40)
    
    # Daily percentiles
    daily_stats = df.groupby(pd.Grouper(key='date', freq='D'))[detection_cols[0]].agg([
        'sum', 'mean', 'std',
        ('25%', lambda x: x.quantile(0.25)),
        ('50%', lambda x: x.quantile(0.50)),
        ('75%', lambda x: x.quantile(0.75))
    ])
    print(f"   Daily statistics shape: {daily_stats.shape}")
    print(f"   Statistics calculated: {daily_stats.columns.tolist()}")
    
    # ========================================================================
    # 4. CONDITIONAL AGGREGATIONS
    # ========================================================================
    print("\n4. Conditional Aggregations")
    print("-" * 40)
    
    # High activity days only (top 25%)
    daily_totals = df.groupby(pd.Grouper(key='date', freq='D'))[detection_cols].sum().sum(axis=1)
    threshold = daily_totals.quantile(0.75)
    high_activity_dates = daily_totals[daily_totals > threshold].index
    
    high_activity_data = df[df['date'].dt.date.isin(high_activity_dates.date)]
    high_activity_patterns = high_activity_data.groupby('station')[detection_cols].sum()
    print(f"   High activity days: {len(high_activity_dates)} days")
    print(f"   High activity patterns shape: {high_activity_patterns.shape}")
    
    return {
        'rolling_7d': rolling_7d,
        'time_period_activity': time_period_activity,
        'daily_stats': daily_stats
    }


def main():
    """
    Main execution demonstrating all aggregation patterns.
    """
    print("MBON Data Aggregation Patterns")
    print("="*60)
    print("\nThis script demonstrates various aggregation patterns for")
    print("different analysis and visualization needs.\n")
    
    # Load and prepare data
    print("Loading data...")
    detections, environmental, detection_meta, stations = load_processed_data()
    detections = prepare_detection_data(detections)
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    
    print(f"✓ Loaded {len(detections):,} detection records")
    print(f"✓ Found {len(detection_cols)} detection types")
    
    # Run demonstrations
    temporal_aggs = temporal_aggregations(detections, detection_cols)
    spatial_aggs = spatial_aggregations(detections, detection_cols)
    species_aggs = species_focused_aggregations(detections, detection_cols, biological,
                                                anthropogenic)
    advanced_aggs = advanced_aggregations(detections, detection_cols)
    
    # ========================================================================
    # EXAMPLE: Creating a plot-ready DataFrame
    # ========================================================================
    print("\n" + "="*60)
    print("EXAMPLE: Creating Plot-Ready DataFrames")
    print("="*60)
    
    # For Plotly time series
    print("\n1. For Plotly Time Series:")
    daily_plotly = temporal_aggs['daily_by_station'].reset_index()
    print(f"   Shape: {daily_plotly.shape}")
    print(f"   Columns: {daily_plotly.columns[:5].tolist()}...")  # First 5 columns
    print("   Ready for: px.line(daily_plotly, x='date', y='bde', color='station')")
    
    # For Seaborn heatmap
    print("\n2. For Seaborn Heatmap:")
    station_matrix = spatial_aggs['station_species_matrix']
    print(f"   Shape: {station_matrix.shape}")
    print("   Ready for: sns.heatmap(station_matrix)")
    
    # For Matplotlib bar chart
    print("\n3. For Matplotlib Bar Chart:")
    top_species = species_aggs['top_10_species']
    print(f"   Shape: {top_species.shape}")
    print("   Ready for: plt.bar(top_species.index, top_species.values)")
    
    print("\n" + "="*60)
    print("✅ Aggregation examples complete!")
    print("="*60)
    print("\nThese DataFrames are now ready for visualization with:")
    print("  • Plotly (interactive plots)")
    print("  • Matplotlib/Seaborn (static plots)")
    print("  • Pandas .plot() (quick exploration)")
    print("  • Export to CSV/Excel for external tools")
    
    return {
        'temporal': temporal_aggs,
        'spatial': spatial_aggs,
        'species': species_aggs,
        'advanced': advanced_aggs
    }


if __name__ == "__main__":
    aggregations = main()
    print("\n💡 Tip: Run this script in an interactive environment (IPython/Jupyter)")
    print("   to explore the returned 'aggregations' dictionary!")