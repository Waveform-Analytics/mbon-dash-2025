#!/usr/bin/env python3
"""
Improved Temperature vs Fish Activity Visualization

This script creates better visualizations that properly handle the ordinal 
categorical nature of fish detection scores (0, 1, 2, 3).

Instead of misleading scatter plots with continuous trend lines, we'll use:
1. Stacked bar charts showing activity distribution by temperature bins
2. Heatmaps showing probability of each activity level vs temperature
3. Box plots showing temperature distributions for each activity level
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """Load and prepare temperature and fish detection data."""
    
    print("Loading temperature and fish detection data...")
    df = pd.read_csv("data_01_aligned_2021.csv", low_memory=False)
    
    # Clean temperature data
    df['Water temp (°C)'] = pd.to_numeric(df['Water temp (°C)'], errors='coerce')
    
    # Define activity labels
    activity_labels = {
        0: 'No calls',
        1: '1 call', 
        2: 'Multiple calls',
        3: 'Chorusing'
    }
    
    return df, activity_labels

def create_temperature_bins(temp_data, n_bins=8):
    """Create temperature bins for analysis."""
    temp_min, temp_max = temp_data.min(), temp_data.max()
    bins = np.linspace(temp_min, temp_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    return bins, bin_centers

def create_stacked_bar_chart(df, species, activity_labels):
    """Create stacked bar chart showing activity distribution by temperature."""
    
    # Clean data
    temp_data = df['Water temp (°C)'].dropna()
    species_data = pd.to_numeric(df[species], errors='coerce').fillna(0)
    
    # Create temperature bins
    bins, bin_centers = create_temperature_bins(temp_data, n_bins=8)
    temp_binned = pd.cut(temp_data, bins=bins, include_lowest=True)
    
    # Create combined dataset
    combined = pd.DataFrame({
        'temperature_bin': temp_binned,
        'activity': species_data,
        'temp_numeric': temp_data
    }).dropna()
    
    # Count activities in each temperature bin
    activity_counts = combined.groupby(['temperature_bin', 'activity']).size().unstack(fill_value=0)
    
    # Calculate proportions
    activity_props = activity_counts.div(activity_counts.sum(axis=1), axis=0)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Absolute counts (stacked bar)
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']  # Blue to red progression
    bottom = np.zeros(len(activity_counts))
    
    bin_labels = [f'{bins[i]:.1f}-{bins[i+1]:.1f}°C' for i in range(len(bins)-1)]
    
    for i, (activity_level, label) in enumerate(activity_labels.items()):
        if activity_level in activity_counts.columns:
            counts = activity_counts[activity_level].values
            ax1.bar(range(len(bin_labels)), counts, bottom=bottom, 
                   label=label, color=colors[i], alpha=0.8)
            bottom += counts
    
    ax1.set_xlabel('Temperature Range')
    ax1.set_ylabel('Number of Observations')
    ax1.set_title(f'{species}: Fish Activity Counts by Temperature')
    ax1.set_xticks(range(len(bin_labels)))
    ax1.set_xticklabels(bin_labels, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Proportions (stacked bar showing percentages)
    bottom = np.zeros(len(activity_props))
    
    for i, (activity_level, label) in enumerate(activity_labels.items()):
        if activity_level in activity_props.columns:
            props = activity_props[activity_level].values
            ax2.bar(range(len(bin_labels)), props, bottom=bottom,
                   label=label, color=colors[i], alpha=0.8)
            bottom += props
    
    ax2.set_xlabel('Temperature Range')
    ax2.set_ylabel('Proportion of Observations')
    ax2.set_title(f'{species}: Fish Activity Proportions by Temperature')
    ax2.set_xticks(range(len(bin_labels)))
    ax2.set_xticklabels(bin_labels, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)
    
    plt.tight_layout()
    return fig

def create_heatmap_analysis(df, species_list, activity_labels):
    """Create heatmap showing probability of each activity level vs temperature."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes_flat = axes.flatten()
    
    for idx, species in enumerate(species_list[:4]):
        ax = axes_flat[idx]
        
        if species not in df.columns:
            ax.set_visible(False)
            continue
            
        # Clean data
        temp_data = df['Water temp (°C)'].dropna()
        species_data = pd.to_numeric(df[species], errors='coerce').fillna(0)
        
        # Create temperature bins
        bins, bin_centers = create_temperature_bins(temp_data, n_bins=10)
        temp_binned = pd.cut(temp_data, bins=bins, include_lowest=True)
        
        # Create combined dataset
        combined = pd.DataFrame({
            'temperature_bin': temp_binned,
            'activity': species_data,
        }).dropna()
        
        # Calculate proportions for heatmap
        activity_props = combined.groupby(['temperature_bin', 'activity']).size().unstack(fill_value=0)
        activity_props = activity_props.div(activity_props.sum(axis=1), axis=0)
        
        # Create heatmap data
        heatmap_data = []
        temp_labels = []
        
        for temp_bin in activity_props.index:
            temp_labels.append(f'{temp_bin.left:.1f}-{temp_bin.right:.1f}°C')
            row = []
            for activity_level in range(4):
                if activity_level in activity_props.columns:
                    row.append(activity_props.loc[temp_bin, activity_level])
                else:
                    row.append(0)
            heatmap_data.append(row)
        
        heatmap_data = np.array(heatmap_data)
        
        # Plot heatmap
        im = ax.imshow(heatmap_data.T, cmap='YlOrRd', aspect='auto', origin='lower')
        
        # Set labels
        ax.set_xlabel('Temperature Range')
        ax.set_ylabel('Activity Level')
        ax.set_title(f'{species}')
        
        # Set ticks
        ax.set_xticks(range(len(temp_labels)))
        ax.set_xticklabels(temp_labels, rotation=45, ha='right')
        ax.set_yticks(range(4))
        ax.set_yticklabels([activity_labels[i] for i in range(4)])
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Proportion')
    
    # Hide unused subplots
    for idx in range(len(species_list), 4):
        axes_flat[idx].set_visible(False)
    
    plt.suptitle('Fish Activity Probability by Temperature', fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig

def create_temperature_distribution_plot(df, species_list, activity_labels):
    """Create box plots showing temperature distributions for each activity level."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes_flat = axes.flatten()
    
    for idx, species in enumerate(species_list[:4]):
        ax = axes_flat[idx]
        
        if species not in df.columns:
            ax.set_visible(False)
            continue
            
        # Clean data
        temp_data = df['Water temp (°C)']
        species_data = pd.to_numeric(df[species], errors='coerce').fillna(0)
        
        # Create combined dataset
        combined = pd.DataFrame({
            'temperature': temp_data,
            'activity': species_data
        }).dropna()
        
        # Prepare data for box plot
        box_data = []
        box_labels = []
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        for activity_level in sorted(combined['activity'].unique()):
            temps = combined[combined['activity'] == activity_level]['temperature']
            if len(temps) > 0:
                box_data.append(temps)
                box_labels.append(f"{activity_labels.get(activity_level, f'Level {activity_level}')}\\n(n={len(temps)})")
        
        # Create box plot
        box_plot = ax.boxplot(box_data, labels=box_labels, patch_artist=True)
        
        # Color the boxes
        for patch, color in zip(box_plot['boxes'], colors[:len(box_data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Water Temperature (°C)')
        ax.set_title(f'{species}')
        ax.grid(True, alpha=0.3)
        
        # Add statistical annotation
        if len(box_data) > 1:
            from scipy.stats import f_oneway
            try:
                f_stat, p_val = f_oneway(*box_data)
                significance = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
                ax.text(0.02, 0.98, f'ANOVA: {significance}', transform=ax.transAxes, 
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                       verticalalignment='top')
            except:
                pass
    
    # Hide unused subplots
    for idx in range(len(species_list), 4):
        axes_flat[idx].set_visible(False)
    
    plt.suptitle('Temperature Distributions by Fish Activity Level', fontsize=16, fontweight='bold')
    plt.tight_layout()
    return fig

def main():
    """Create improved temperature vs fish activity visualizations."""
    
    print("🎨 CREATING IMPROVED TEMPERATURE VS FISH ACTIVITY FIGURES")
    print("="*70)
    
    # Load data
    df, activity_labels = load_and_prepare_data()
    
    species_list = ['Spotted seatrout', 'Silver perch', 'Oyster toadfish boat whistle', 'Atlantic croaker']
    available_species = [s for s in species_list if s in df.columns]
    
    # Create output directory
    output_dir = Path("output/phase6_temporal_correlation/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating visualizations for {len(available_species)} species...")
    
    # 1. Create stacked bar chart for each species
    for species in available_species:
        print(f"  Creating stacked bar chart for {species}...")
        fig = create_stacked_bar_chart(df, species, activity_labels)
        
        filename = f"temperature_activity_stacked_{species.replace(' ', '_').lower()}.png"
        fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"    ✅ Saved: {filename}")
    
    # 2. Create heatmap analysis
    print("  Creating heatmap analysis...")
    fig = create_heatmap_analysis(df, available_species, activity_labels)
    fig.savefig(output_dir / "temperature_activity_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("    ✅ Saved: temperature_activity_heatmap.png")
    
    # 3. Create temperature distribution analysis
    print("  Creating temperature distribution analysis...")
    fig = create_temperature_distribution_plot(df, available_species, activity_labels)
    fig.savefig(output_dir / "temperature_distributions_by_activity.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print("    ✅ Saved: temperature_distributions_by_activity.png")
    
    print("\\n✅ All improved temperature figures created!")
    print("\\nKey improvements:")
    print("  - Proper handling of ordinal categorical data (0,1,2,3)")
    print("  - Stacked bars show activity distribution across temperature ranges") 
    print("  - Heatmaps show probability of each activity level")
    print("  - Box plots show temperature distributions for each activity level")
    print("  - Statistical tests included where appropriate")
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)