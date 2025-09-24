#!/usr/bin/env python3
"""
PHASE 6: TEMPORAL CORRELATION ANALYSIS
=====================================
Goal: Capture the temporal synchrony between acoustic indices and species detection
      that is visible in heatmaps but missed by traditional ML approaches.

This addresses the key question:
- Why do some acoustic indices visually match species patterns but don't 
  show up as strong predictors in ML models?

Analyses to perform:
1. Time-series correlation analysis (preserving temporal order)
2. Circadian pattern correlation 
3. Seasonal pattern correlation
4. Event-based synchrony analysis
5. Lag correlation analysis (species detection following acoustic patterns)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from scipy.signal import correlate
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def load_aligned_data():
    """Load the aligned dataset for temporal analysis."""
    data_path = Path("data_01_aligned_2021.csv")
    if not data_path.exists():
        raise FileNotFoundError("Aligned dataset not found. Run Phase 1 first.")
    
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Convert all non-datetime/station columns to numeric, handling mixed types
    for col in df.columns:
        if col not in ['datetime', 'station']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Sort by station and datetime for proper time series analysis
    df = df.sort_values(['station', 'datetime']).reset_index(drop=True)
    
    print(f"✓ Loaded aligned dataset: {df.shape}")
    return df

def identify_key_features(df):
    """Identify acoustic indices and species for correlation analysis."""
    
    # Species columns
    species_cols = [
        'Spotted seatrout', 'Atlantic croaker', 'Oyster toadfish boat whistle',
        'Bottlenose dolphin echolocation', 'Red drum', 'Silver perch',
        'Oyster toadfish grunt', 'Vessel'
    ]
    available_species = [col for col in species_cols if col in df.columns]
    
    # Acoustic indices (exclude metadata and environmental features)
    acoustic_cols = [col for col in df.columns if col not in [
        'datetime', 'station', 'Water temp (°C)', 'Water depth (m)',
        'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'Broadband (1-40000 Hz)',
        'total_fish_activity', 'any_activity', 'high_activity', 'num_active_species'
    ] + available_species]
    
    # Filter to numeric columns only
    acoustic_cols = [col for col in acoustic_cols if df[col].dtype in ['float64', 'int64']]
    
    print(f"📊 Features identified:")
    print(f"   Species: {len(available_species)}")
    print(f"   Acoustic indices: {len(acoustic_cols)}")
    
    return available_species, acoustic_cols

def temporal_correlation_analysis(df, species_list, acoustic_list, station='9M'):
    """
    Perform temporal correlation analysis preserving time series structure.
    """
    print(f"\n🔍 TEMPORAL CORRELATION ANALYSIS - Station {station}")
    print("=" * 60)
    
    # Filter to single station to preserve temporal structure
    station_df = df[df['station'] == station].copy()
    station_df = station_df.sort_values('datetime').reset_index(drop=True)
    
    print(f"Station {station} data: {station_df.shape}")
    print(f"Date range: {station_df['datetime'].min()} to {station_df['datetime'].max()}")
    
    correlation_results = []
    
    for species in species_list:
        if species not in station_df.columns:
            continue
            
        species_data = pd.to_numeric(station_df[species], errors='coerce').fillna(0)
        
        # Skip species with very low activity
        if species_data.sum() < 20:
            continue
            
        print(f"\n🐟 Analyzing: {species}")
        print(f"   Total detections: {species_data.sum()}")
        print(f"   Detection rate: {(species_data > 0).mean():.2%}")
        
        species_correlations = []
        
        for acoustic in acoustic_list:
            if acoustic not in station_df.columns:
                continue
                
            acoustic_data = pd.to_numeric(station_df[acoustic], errors='coerce')
            acoustic_data = acoustic_data.fillna(acoustic_data.mean())
            
            # Skip if acoustic data is constant
            if acoustic_data.std() == 0:
                continue
            
            # Pearson correlation (linear relationship)
            r_pearson, p_pearson = pearsonr(acoustic_data, species_data)
            
            # Spearman correlation (monotonic relationship)
            r_spearman, p_spearman = spearmanr(acoustic_data, species_data)
            
            correlation_result = {
                'species': species,
                'acoustic_index': acoustic,
                'pearson_r': r_pearson,
                'pearson_p': p_pearson,
                'spearman_r': r_spearman,
                'spearman_p': p_spearman,
                'station': station
            }
            
            correlation_results.append(correlation_result)
            species_correlations.append(correlation_result)
        
        # Show top correlations for this species
        if species_correlations:
            species_df = pd.DataFrame(species_correlations)
            top_pearson = species_df.nlargest(5, 'pearson_r')
            
            print(f"   Top 5 Pearson correlations:")
            for _, row in top_pearson.iterrows():
                significance = "***" if row['pearson_p'] < 0.001 else "**" if row['pearson_p'] < 0.01 else "*" if row['pearson_p'] < 0.05 else ""
                print(f"     {row['acoustic_index'][:25]:25} | r={row['pearson_r']:+.3f} {significance}")
    
    return pd.DataFrame(correlation_results)

def circadian_pattern_correlation(df, species_list, acoustic_list, station='9M'):
    """
    Analyze correlation of circadian (hourly) patterns.
    """
    print(f"\n🌅 CIRCADIAN PATTERN CORRELATION - Station {station}")
    print("=" * 50)
    
    station_df = df[df['station'] == station].copy()
    station_df['hour'] = station_df['datetime'].dt.hour
    
    # Create hourly averages
    hourly_patterns = station_df.groupby('hour').agg({
        **{species: 'mean' for species in species_list if species in station_df.columns},
        **{acoustic: 'mean' for acoustic in acoustic_list if acoustic in station_df.columns}
    })
    
    circadian_correlations = []
    
    for species in species_list:
        if species not in hourly_patterns.columns:
            continue
            
        species_hourly = hourly_patterns[species]
        
        if species_hourly.sum() == 0:  # Skip if no activity
            continue
            
        print(f"\n🐟 {species} circadian correlations:")
        
        species_results = []
        for acoustic in acoustic_list:
            if acoustic not in hourly_patterns.columns:
                continue
                
            acoustic_hourly = hourly_patterns[acoustic]
            
            if acoustic_hourly.std() == 0:  # Skip constant values
                continue
                
            # Correlation of hourly patterns
            r, p = pearsonr(acoustic_hourly, species_hourly)
            
            result = {
                'species': species,
                'acoustic_index': acoustic,
                'circadian_r': r,
                'circadian_p': p,
                'station': station
            }
            
            circadian_correlations.append(result)
            species_results.append(result)
        
        # Show top circadian correlations
        if species_results:
            species_df = pd.DataFrame(species_results)
            top_correlations = species_df.nlargest(3, 'circadian_r')
            
            for _, row in top_correlations.iterrows():
                significance = "***" if row['circadian_p'] < 0.001 else "**" if row['circadian_p'] < 0.01 else "*" if row['circadian_p'] < 0.05 else ""
                print(f"   {row['acoustic_index'][:30]:30} | r={row['circadian_r']:+.3f} {significance}")
    
    return pd.DataFrame(circadian_correlations)

def lag_correlation_analysis(df, species_list, acoustic_list, station='9M', max_lag=6):
    """
    Analyze if species detection follows acoustic patterns with a time delay.
    """
    print(f"\n⏰ LAG CORRELATION ANALYSIS - Station {station}")
    print("=" * 50)
    print(f"Testing lags up to {max_lag} periods ({max_lag*2} hours)")
    
    station_df = df[df['station'] == station].copy()
    station_df = station_df.sort_values('datetime').reset_index(drop=True)
    
    lag_results = []
    
    for species in species_list:
        if species not in station_df.columns:
            continue
            
        species_data = pd.to_numeric(station_df[species], errors='coerce').fillna(0)
        
        if species_data.sum() < 20:  # Skip low-activity species
            continue
            
        print(f"\n🐟 {species} lag correlations:")
        
        best_lags = []
        
        for acoustic in acoustic_list[:10]:  # Limit to top acoustic indices
            if acoustic not in station_df.columns:
                continue
                
            acoustic_data = pd.to_numeric(station_df[acoustic], errors='coerce')
            acoustic_data = acoustic_data.fillna(acoustic_data.mean())
            
            if acoustic_data.std() == 0:
                continue
            
            # Test different lags
            lag_correlations = []
            for lag in range(0, max_lag + 1):
                if lag == 0:
                    r, p = pearsonr(acoustic_data, species_data)
                else:
                    # Acoustic leads species by 'lag' periods
                    if len(acoustic_data) > lag:
                        acoustic_lagged = acoustic_data[:-lag]
                        species_lagged = species_data[lag:]
                        r, p = pearsonr(acoustic_lagged, species_lagged)
                    else:
                        r, p = 0, 1
                
                lag_correlations.append({
                    'lag': lag,
                    'correlation': r,
                    'p_value': p
                })
            
            # Find best lag
            best_lag_result = max(lag_correlations, key=lambda x: abs(x['correlation']))
            
            result = {
                'species': species,
                'acoustic_index': acoustic,
                'best_lag': best_lag_result['lag'],
                'best_lag_r': best_lag_result['correlation'],
                'best_lag_p': best_lag_result['p_value'],
                'station': station
            }
            
            lag_results.append(result)
            best_lags.append(result)
        
        # Show top lag correlations
        if best_lags:
            best_lags_df = pd.DataFrame(best_lags)
            # Sort by absolute correlation value
            best_lags_df['abs_correlation'] = best_lags_df['best_lag_r'].abs()
            top_lags_df = best_lags_df.nlargest(3, 'abs_correlation')
            
            for _, row in top_lags_df.iterrows():
                lag_hours = row['best_lag'] * 2
                significance = "***" if row['best_lag_p'] < 0.001 else "**" if row['best_lag_p'] < 0.01 else "*" if row['best_lag_p'] < 0.05 else ""
                print(f"   {row['acoustic_index'][:25]:25} | lag={row['best_lag']:2d} ({lag_hours:2d}h) | r={row['best_lag_r']:+.3f} {significance}")
    
    return pd.DataFrame(lag_results)

def comprehensive_correlation_summary(temporal_corr, circadian_corr, lag_corr):
    """
    Create a comprehensive summary of correlation analyses.
    """
    print(f"\n🎯 COMPREHENSIVE CORRELATION SUMMARY")
    print("=" * 60)
    
    # Merge all correlation results
    summary_data = []
    
    # Process temporal correlations
    for _, row in temporal_corr.iterrows():
        summary_data.append({
            'species': row['species'],
            'acoustic_index': row['acoustic_index'],
            'temporal_pearson_r': row['pearson_r'],
            'temporal_pearson_p': row['pearson_p'],
            'temporal_spearman_r': row['spearman_r'],
            'temporal_spearman_p': row['spearman_p']
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Add circadian correlations
    if not circadian_corr.empty:
        circadian_pivot = circadian_corr.pivot(index=['species', 'acoustic_index'], 
                                             columns=[], 
                                             values=['circadian_r', 'circadian_p']).reset_index()
        circadian_pivot.columns = ['species', 'acoustic_index', 'circadian_r', 'circadian_p']
        
        summary_df = summary_df.merge(circadian_pivot, 
                                    on=['species', 'acoustic_index'], 
                                    how='left')
    
    # Add lag correlations
    if not lag_corr.empty:
        lag_pivot = lag_corr[['species', 'acoustic_index', 'best_lag', 'best_lag_r', 'best_lag_p']]
        summary_df = summary_df.merge(lag_pivot, 
                                    on=['species', 'acoustic_index'], 
                                    how='left')
    
    # Calculate composite correlation strength
    summary_df['max_correlation'] = summary_df[['temporal_pearson_r', 'temporal_spearman_r', 'circadian_r', 'best_lag_r']].abs().max(axis=1)
    
    print(f"\n🏆 TOP ACOUSTIC-SPECIES CORRELATIONS (All Methods Combined):")
    print("-" * 80)
    print(f"{'Species':<25} {'Acoustic Index':<25} {'Best Method':<12} {'Max |r|':<8} {'Significance'}")
    print("-" * 80)
    
    # Show top correlations across all species
    top_correlations = summary_df.nlargest(20, 'max_correlation')
    
    for _, row in top_correlations.iterrows():
        # Find which method gave the maximum correlation
        correlations = {
            'Temporal': abs(row.get('temporal_pearson_r', 0)),
            'Spearman': abs(row.get('temporal_spearman_r', 0)),
            'Circadian': abs(row.get('circadian_r', 0)),
            'Lag': abs(row.get('best_lag_r', 0))
        }
        
        best_method = max(correlations, key=correlations.get)
        max_r = correlations[best_method]
        
        # Get significance for best method
        if best_method == 'Temporal':
            p_val = row.get('temporal_pearson_p', 1)
        elif best_method == 'Spearman':
            p_val = row.get('temporal_spearman_p', 1)
        elif best_method == 'Circadian':
            p_val = row.get('circadian_p', 1)
        else:  # Lag
            p_val = row.get('best_lag_p', 1)
        
        significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
        
        species_short = row['species'][:23] + ".." if len(row['species']) > 25 else row['species']
        acoustic_short = row['acoustic_index'][:23] + ".." if len(row['acoustic_index']) > 25 else row['acoustic_index']
        
        print(f"{species_short:<25} {acoustic_short:<25} {best_method:<12} {max_r:<8.3f} {significance}")
    
    return summary_df

def create_heatmap_comparison_figure(df, species='Spotted seatrout', acoustic_indices=None, station='9M'):
    """
    FIGURE 4: Create side-by-side heat maps comparing acoustic indices with manual detections.
    This visualization led to the breakthrough - showing acoustic indices 'light up' in 
    the same temporal patterns as fish detections.
    """
    print(f"\n🎨 CREATING FIGURE 4: Acoustic Index vs Manual Detection Comparison")
    print("=" * 70)
    
    # Filter to specific station and species
    station_df = df[df['station'] == station].copy()
    
    if species not in station_df.columns:
        print(f"⚠️ Species '{species}' not found in data")
        return
    
    # Add temporal features if not already present
    if 'day_of_year' not in station_df.columns:
        station_df['day_of_year'] = station_df['datetime'].dt.dayofyear
    if 'period_of_day' not in station_df.columns:
        station_df['period_of_day'] = station_df['datetime'].dt.hour // 2
    
    # If no acoustic indices specified, use top correlated ones from earlier analysis
    if acoustic_indices is None:
        # Get acoustic columns
        exclude_cols = [
            'datetime', 'station', 'day_of_year', 'period_of_day',
            'Water temp (°C)', 'Water depth (m)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 
            'Broadband (1-40000 Hz)', 'Spotted seatrout', 'Atlantic croaker', 'Vessel',
            'Oyster toadfish boat whistle', 'Red drum', 'Silver perch', 'Black drum',
            'total_fish_activity', 'any_activity', 'high_activity', 'num_active_species'
        ]
        
        potential_acoustic = [col for col in station_df.columns if col not in exclude_cols]
        potential_acoustic = [col for col in potential_acoustic if station_df[col].dtype in ['float64', 'int64']]
        
        # Calculate correlations to find best acoustic indices
        correlations = []
        species_data = pd.to_numeric(station_df[species], errors='coerce').fillna(0)
        
        for acoustic in potential_acoustic:
            acoustic_data = pd.to_numeric(station_df[acoustic], errors='coerce')
            acoustic_data = acoustic_data.fillna(acoustic_data.mean())
            
            if acoustic_data.std() > 0:
                corr, p_val = pearsonr(acoustic_data, species_data)
                correlations.append({'index': acoustic, 'correlation': abs(corr), 'p_value': p_val})
        
        # Take top 4 correlated indices
        correlations = sorted(correlations, key=lambda x: x['correlation'], reverse=True)
        acoustic_indices = [item['index'] for item in correlations[:4]]
        
        print(f"   Selected top correlated acoustic indices for {species}:")
        for i, item in enumerate(correlations[:4], 1):
            print(f"   {i}. {item['index']} (r = {item['correlation']:.3f})")
    
    # Create heat map data
    def create_heatmap_data(data_column, station_df, normalize=True):
        # Create 2D grid: day_of_year (rows) vs period_of_day (columns)
        heatmap_data = np.zeros((365, 12))  # 365 days, 12 periods per day
        counts = np.zeros((365, 12))  # For averaging
        
        for _, row in station_df.iterrows():
            day = int(row['day_of_year']) - 1  # 0-indexed
            period = int(row['period_of_day'])  # Already 0-11
            
            if 0 <= day < 365 and 0 <= period < 12:
                value = pd.to_numeric(row[data_column], errors='coerce')
                if not np.isnan(value):
                    heatmap_data[day, period] += value
                    counts[day, period] += 1
        
        # Average where we have multiple observations
        mask = counts > 0
        heatmap_data[mask] = heatmap_data[mask] / counts[mask]
        
        if normalize:
            # Normalize to 0-1 range for better comparison
            data_min, data_max = heatmap_data.min(), heatmap_data.max()
            if data_max > data_min:
                heatmap_data = (heatmap_data - data_min) / (data_max - data_min)
        
        return heatmap_data
    
    # Create the comparison figure
    n_plots = len(acoustic_indices) + 1  # +1 for species detection
    n_cols = min(3, n_plots)
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
    if n_plots == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = axes.reshape(1, -1)
    
    axes_flat = axes.flatten()
    
    # Plot species detection heatmap first
    species_heatmap = create_heatmap_data(species, station_df, normalize=True)
    
    # Transpose to match probability surface orientation (day on x-axis, period on y-axis)
    im1 = axes_flat[0].imshow(species_heatmap.T, aspect='auto', cmap='viridis', origin='lower',
                             extent=[1, 365, 0, 11])
    axes_flat[0].set_title(f'{species}\n(Manual Detections)', fontsize=12, fontweight='bold')
    axes_flat[0].set_xlabel('Day of Year')
    axes_flat[0].set_ylabel('2-Hour Period (0=midnight-2am)')
    axes_flat[0].set_xticks([1, 91, 182, 273, 365])
    axes_flat[0].set_xticklabels(['Jan 1', 'Apr 1', 'Jul 1', 'Oct 1', 'Dec 31'])
    axes_flat[0].set_yticks(range(0, 12, 2))
    axes_flat[0].set_yticklabels([f'{h:02d}:00' for h in range(0, 24, 4)])
    plt.colorbar(im1, ax=axes_flat[0], label='Normalized Activity')
    
    # Plot acoustic index heatmaps
    for i, acoustic_idx in enumerate(acoustic_indices, 1):
        if i < len(axes_flat):
            acoustic_heatmap = create_heatmap_data(acoustic_idx, station_df, normalize=True)
            
            # Transpose to match probability surface orientation (day on x-axis, period on y-axis)
            im = axes_flat[i].imshow(acoustic_heatmap.T, aspect='auto', cmap='viridis', origin='lower',
                                   extent=[1, 365, 0, 11])
            axes_flat[i].set_title(f'{acoustic_idx}\n(Acoustic Index)', fontsize=12)
            axes_flat[i].set_xlabel('Day of Year')
            axes_flat[i].set_ylabel('2-Hour Period (0=midnight-2am)')
            axes_flat[i].set_xticks([1, 91, 182, 273, 365])
            axes_flat[i].set_xticklabels(['Jan 1', 'Apr 1', 'Jul 1', 'Oct 1', 'Dec 31'])
            axes_flat[i].set_yticks(range(0, 12, 2))
            axes_flat[i].set_yticklabels([f'{h:02d}:00' for h in range(0, 24, 4)])
            plt.colorbar(im, ax=axes_flat[i], label='Normalized Value')
    
    # Hide unused subplots
    for j in range(len(acoustic_indices) + 1, len(axes_flat)):
        axes_flat[j].set_visible(False)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path("output/phase6_temporal_correlation/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig_path = output_dir / f"acoustic_vs_manual_detection_comparison_{species.replace(' ', '_').lower()}_station_{station}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Figure 4: {fig_path}")
    
    # Also create a summary correlation plot
    fig2, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    correlations_for_plot = []
    for acoustic_idx in acoustic_indices:
        acoustic_data = pd.to_numeric(station_df[acoustic_idx], errors='coerce').fillna(station_df[acoustic_idx].mean())
        species_data = pd.to_numeric(station_df[species], errors='coerce').fillna(0)
        
        if acoustic_data.std() > 0:
            corr, p_val = pearsonr(acoustic_data, species_data)
            correlations_for_plot.append({
                'index': acoustic_idx.replace('_', ' '),
                'correlation': corr,
                'p_value': p_val
            })
    
    if correlations_for_plot:
        corr_df = pd.DataFrame(correlations_for_plot)
        
        # Create bar plot
        bars = ax.bar(range(len(corr_df)), corr_df['correlation'], 
                     color=['green' if r > 0 else 'red' for r in corr_df['correlation']])
        
        ax.set_xlabel('Acoustic Index')
        ax.set_ylabel('Pearson Correlation with Manual Detections')
        ax.set_title(f'Acoustic Index Correlations with {species} Detections\nStation {station}')
        ax.set_xticks(range(len(corr_df)))
        ax.set_xticklabels([idx[:20] + '...' if len(idx) > 23 else idx 
                           for idx in corr_df['index']], rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        # Add significance stars
        for i, (bar, p_val) in enumerate(zip(bars, corr_df['p_value'])):
            height = bar.get_height()
            significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            if significance:
                ax.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height > 0 else -0.03), 
                       significance, ha='center', va='bottom' if height > 0 else 'top')
    
    plt.tight_layout()
    fig2_path = output_dir / f"acoustic_correlations_{species.replace(' ', '_').lower()}_station_{station}.png"
    plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved correlation plot: {fig2_path}")
    
    plt.show()
    
    return species_heatmap, [create_heatmap_data(idx, station_df, normalize=True) for idx in acoustic_indices]

def create_temperature_activity_figure(df):
    """
    FIGURE 3: Create scatter plot showing temperature vs fish activity relationship.
    """
    print(f"\n🎨 CREATING FIGURE 3: Temperature vs Fish Activity Relationship")
    print("=" * 60)
    
    # Species to analyze
    species_to_plot = ['Spotted seatrout', 'Silver perch', 'Oyster toadfish boat whistle', 'Atlantic croaker']
    available_species = [s for s in species_to_plot if s in df.columns]
    
    if 'Water temp (°C)' not in df.columns:
        print("⚠️ Water temperature data not available")
        return
    
    # Create the plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes_flat = axes.flatten()
    
    colors = plt.cm.Set1(np.linspace(0, 1, len(available_species)))
    
    for i, species in enumerate(available_species[:4]):
        ax = axes_flat[i]
        
        # Get data
        temp_data = pd.to_numeric(df['Water temp (°C)'], errors='coerce')
        species_data = pd.to_numeric(df[species], errors='coerce').fillna(0)
        
        # Remove NaN temperature values
        valid_mask = ~np.isnan(temp_data)
        temp_clean = temp_data[valid_mask]
        species_clean = species_data[valid_mask]
        
        # Create scatter plot
        ax.scatter(temp_clean, species_clean, alpha=0.6, c=colors[i], s=30)
        
        # Add trend line
        if len(temp_clean) > 10:
            z = np.polyfit(temp_clean, species_clean, 1)
            p = np.poly1d(z)
            temp_range = np.linspace(temp_clean.min(), temp_clean.max(), 100)
            ax.plot(temp_range, p(temp_range), color='red', linestyle='--', linewidth=2)
            
            # Calculate correlation
            corr, p_val = pearsonr(temp_clean, species_clean)
            significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
            
            ax.text(0.05, 0.95, f'r = {corr:.3f}{significance}', transform=ax.transAxes, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                   verticalalignment='top')
        
        ax.set_xlabel('Water Temperature (°C)')
        ax.set_ylabel(f'{species} Detections')
        ax.set_title(species)
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplot if we have fewer than 4 species
    for j in range(len(available_species), 4):
        axes_flat[j].set_visible(False)
    
    plt.suptitle('Temperature vs Fish Detection Activity', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save figure
    output_dir = Path("output/phase6_temporal_correlation/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig_path = output_dir / "temperature_vs_fish_activity.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Figure 3: {fig_path}")
    
    plt.show()
    
    return fig_path

def main():
    print("🔄 PHASE 6: TEMPORAL CORRELATION ANALYSIS")
    print("=" * 70)
    print("Goal: Capture temporal synchrony that visual inspection reveals")
    print("      but traditional ML analysis misses")
    
    # Load data
    df = load_aligned_data()
    species_list, acoustic_list = identify_key_features(df)
    
    # Run analyses for each station
    all_temporal_corr = []
    all_circadian_corr = []
    all_lag_corr = []
    
    stations = df['station'].unique()
    
    for station in stations:
        print(f"\n{'='*20} STATION {station} {'='*20}")
        
        # Temporal correlation analysis
        temporal_corr = temporal_correlation_analysis(df, species_list, acoustic_list, station)
        temporal_corr['station'] = station
        all_temporal_corr.append(temporal_corr)
        
        # Circadian pattern correlation
        circadian_corr = circadian_pattern_correlation(df, species_list, acoustic_list, station)
        circadian_corr['station'] = station
        all_circadian_corr.append(circadian_corr)
        
        # Lag correlation analysis
        lag_corr = lag_correlation_analysis(df, species_list, acoustic_list, station)
        lag_corr['station'] = station
        all_lag_corr.append(lag_corr)
    
    # Combine results
    combined_temporal = pd.concat(all_temporal_corr, ignore_index=True)
    combined_circadian = pd.concat(all_circadian_corr, ignore_index=True)
    combined_lag = pd.concat(all_lag_corr, ignore_index=True)
    
    # Comprehensive summary
    summary_df = comprehensive_correlation_summary(combined_temporal, combined_circadian, combined_lag)
    
    # Generate key figures for the report
    print(f"\n📊 GENERATING FIGURES FOR REPORT")
    print("=" * 40)
    
    # Figure 3: Temperature vs Fish Activity
    create_temperature_activity_figure(df)
    
    # Figure 4: Acoustic Index vs Manual Detection Comparison
    # Try different species and stations to find good examples
    for species in ['Spotted seatrout', 'Silver perch']:
        if species in df.columns:
            for station in df['station'].unique():
                species_count = df[df['station'] == station][species].sum()
                if species_count > 50:  # Only create plots for species with sufficient data
                    print(f"   Creating comparison for {species} at station {station} ({species_count} detections)")
                    create_heatmap_comparison_figure(df, species=species, station=station)
                    break  # Only create one plot per species
    
    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    combined_temporal.to_csv(output_dir / "phase6_temporal_correlations.csv", index=False)
    combined_circadian.to_csv(output_dir / "phase6_circadian_correlations.csv", index=False)
    combined_lag.to_csv(output_dir / "phase6_lag_correlations.csv", index=False)
    summary_df.to_csv(output_dir / "phase6_correlation_summary.csv", index=False)
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"   📊 Temporal correlations: phase6_temporal_correlations.csv")
    print(f"   🌅 Circadian correlations: phase6_circadian_correlations.csv") 
    print(f"   ⏰ Lag correlations: phase6_lag_correlations.csv")
    print(f"   🎯 Summary: phase6_correlation_summary.csv")
    
    print("\n🎉 PHASE 6 COMPLETE!")
    print("=" * 30)
    print("✅ Temporal correlation analysis completed")
    print("✅ Visual patterns quantified")
    print("✅ Hidden relationships revealed")
    
    # Specific insights for ADI and Spotted Seatrout
    adi_spotted = summary_df[
        (summary_df['species'] == 'Spotted seatrout') & 
        (summary_df['acoustic_index'].str.contains('ADI', case=False, na=False))
    ]
    
    if not adi_spotted.empty:
        print(f"\n🎯 ADI vs SPOTTED SEATROUT ANALYSIS:")
        for _, row in adi_spotted.iterrows():
            print(f"   Temporal r: {row.get('temporal_pearson_r', 'N/A'):.3f}")
            print(f"   Circadian r: {row.get('circadian_r', 'N/A'):.3f}")
            print(f"   Best lag: {row.get('best_lag', 'N/A')} periods")
            print(f"   Max correlation: {row.get('max_correlation', 'N/A'):.3f}")
    
    return combined_temporal, combined_circadian, combined_lag, summary_df

if __name__ == "__main__":
    main()