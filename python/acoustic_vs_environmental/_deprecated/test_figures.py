#!/usr/bin/env python3
"""
Quick test script to generate key figures for the report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_data():
    """Load the aligned dataset."""
    data_path = Path("data_01_aligned_2021.csv")
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Convert all non-datetime/station columns to numeric
    for col in df.columns:
        if col not in ['datetime', 'station']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"✓ Loaded dataset: {df.shape}")
    return df

def create_figure_3_temperature_activity(df):
    """Figure 3: Temperature vs Fish Activity"""
    print("🎨 Creating Figure 3: Temperature vs Fish Activity")
    
    species_to_plot = ['Spotted seatrout', 'Silver perch', 'Oyster toadfish boat whistle']
    available_species = [s for s in species_to_plot if s in df.columns]
    
    if 'Water temp (°C)' not in df.columns:
        print("⚠️ Water temperature data not available")
        return
    
    fig, axes = plt.subplots(1, len(available_species), figsize=(5*len(available_species), 5))
    if len(available_species) == 1:
        axes = [axes]
    
    colors = plt.cm.Set1(np.linspace(0, 1, len(available_species)))
    
    for i, species in enumerate(available_species):
        ax = axes[i] if len(available_species) > 1 else axes[0]
        
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
    
    plt.suptitle('Temperature vs Fish Detection Activity', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save figure
    output_dir = Path("output/phase6_temporal_correlation/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig_path = output_dir / "temperature_vs_fish_activity.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Figure 3: {fig_path}")
    plt.close()

def create_figure_4_heatmap_comparison(df, species='Spotted seatrout', station='14M'):
    """Figure 4: Acoustic Index vs Manual Detection Comparison"""
    print(f"🎨 Creating Figure 4: Acoustic Index vs Manual Detection ({species}, Station {station})")
    
    # Filter to specific station
    station_df = df[df['station'] == station].copy()
    
    if species not in station_df.columns:
        print(f"⚠️ Species '{species}' not found")
        return
    
    # Add temporal features
    station_df['day_of_year'] = station_df['datetime'].dt.dayofyear
    station_df['period_of_day'] = station_df['datetime'].dt.hour // 2
    
    # Get top correlated acoustic indices
    exclude_cols = [
        'datetime', 'station', 'day_of_year', 'period_of_day',
        'Water temp (°C)', 'Water depth (m)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 
        'Broadband (1-40000 Hz)', 'Spotted seatrout', 'Atlantic croaker', 'Vessel',
        'Oyster toadfish boat whistle', 'Red drum', 'Silver perch', 'Black drum',
        'total_fish_activity', 'any_activity', 'high_activity', 'num_active_species'
    ]
    
    potential_acoustic = [col for col in station_df.columns if col not in exclude_cols]
    potential_acoustic = [col for col in potential_acoustic if station_df[col].dtype in ['float64', 'int64']]
    
    # Calculate correlations
    correlations = []
    species_data = pd.to_numeric(station_df[species], errors='coerce').fillna(0)
    
    for acoustic in potential_acoustic:
        acoustic_data = pd.to_numeric(station_df[acoustic], errors='coerce')
        acoustic_data = acoustic_data.fillna(acoustic_data.mean())
        
        if acoustic_data.std() > 0:
            corr, p_val = pearsonr(acoustic_data, species_data)
            correlations.append({'index': acoustic, 'correlation': abs(corr), 'p_value': p_val})
    
    # Take top 3 correlated indices
    correlations = sorted(correlations, key=lambda x: x['correlation'], reverse=True)
    top_acoustic_indices = [item['index'] for item in correlations[:3]]
    
    print(f"   Selected acoustic indices: {[c['index'][:20] for c in correlations[:3]]}")
    
    def create_heatmap_data(data_column, station_df):
        """Create 2D heatmap data"""
        heatmap_data = np.zeros((365, 12))
        counts = np.zeros((365, 12))
        
        for _, row in station_df.iterrows():
            day = int(row['day_of_year']) - 1
            period = int(row['period_of_day'])
            
            if 0 <= day < 365 and 0 <= period < 12:
                value = pd.to_numeric(row[data_column], errors='coerce')
                if not np.isnan(value):
                    heatmap_data[day, period] += value
                    counts[day, period] += 1
        
        # Average and normalize
        mask = counts > 0
        heatmap_data[mask] = heatmap_data[mask] / counts[mask]
        
        # Normalize to 0-1 range
        data_min, data_max = heatmap_data.min(), heatmap_data.max()
        if data_max > data_min:
            heatmap_data = (heatmap_data - data_min) / (data_max - data_min)
        
        return heatmap_data
    
    # Create the comparison figure
    n_plots = len(top_acoustic_indices) + 1
    fig, axes = plt.subplots(1, n_plots, figsize=(5*n_plots, 4))
    if n_plots == 1:
        axes = [axes]
    
    # Plot species detection heatmap first
    species_heatmap = create_heatmap_data(species, station_df)
    
    im1 = axes[0].imshow(species_heatmap, aspect='auto', cmap='viridis', origin='lower')
    axes[0].set_title(f'{species}\n(Manual Detections)', fontweight='bold')
    axes[0].set_xlabel('Time of Day (2-hour periods)')
    axes[0].set_ylabel('Day of Year')
    axes[0].set_xticks(range(0, 12, 2))
    axes[0].set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 4)])
    axes[0].set_yticks([0, 91, 182, 273, 364])
    axes[0].set_yticklabels(['Jan', 'Apr', 'Jul', 'Oct', 'Dec'])
    plt.colorbar(im1, ax=axes[0], label='Normalized Activity')
    
    # Plot acoustic index heatmaps
    for i, acoustic_idx in enumerate(top_acoustic_indices, 1):
        if i < len(axes):
            acoustic_heatmap = create_heatmap_data(acoustic_idx, station_df)
            
            im = axes[i].imshow(acoustic_heatmap, aspect='auto', cmap='viridis', origin='lower')
            short_name = acoustic_idx[:15] + "..." if len(acoustic_idx) > 18 else acoustic_idx
            axes[i].set_title(f'{short_name}\n(Acoustic Index)')
            axes[i].set_xlabel('Time of Day (2-hour periods)')
            axes[i].set_ylabel('Day of Year')
            axes[i].set_xticks(range(0, 12, 2))
            axes[i].set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 4)])
            axes[i].set_yticks([0, 91, 182, 273, 364])
            axes[i].set_yticklabels(['Jan', 'Apr', 'Jul', 'Oct', 'Dec'])
            plt.colorbar(im, ax=axes[i], label='Normalized Value')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path("output/phase6_temporal_correlation/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig_path = output_dir / f"acoustic_vs_manual_detection_comparison_{species.replace(' ', '_').lower()}_station_{station}.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Figure 4: {fig_path}")
    plt.close()

def main():
    """Generate key figures for the report"""
    print("🎨 GENERATING FIGURES FOR REPORT")
    print("=" * 50)
    
    # Load data
    df = load_data()
    
    # Generate figures
    create_figure_3_temperature_activity(df)
    create_figure_4_heatmap_comparison(df, species='Spotted seatrout', station='14M')
    
    # Try another station/species combo if available
    if df[df['station'] == '9M']['Silver perch'].sum() > 50:
        create_figure_4_heatmap_comparison(df, species='Silver perch', station='9M')
    
    print("\n🎉 Figure generation complete!")

if __name__ == "__main__":
    main()