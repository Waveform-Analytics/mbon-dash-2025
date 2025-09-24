#!/usr/bin/env python3
"""
Quick Key Figure Regeneration

This script regenerates only the essential figures needed for the report
without running the full time-consuming analysis pipeline.

Usage:
    python regenerate_key_figures.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def regenerate_comparison_figure():
    """Regenerate the corrected acoustic vs manual detection comparison figure."""
    
    print("🎨 REGENERATING FIGURE 4: Acoustic vs Manual Detection Comparison")
    print("="*70)
    
    # Load data
    print("Loading aligned dataset...")
    df = pd.read_csv("data_01_aligned_2021.csv", low_memory=False)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Clean data types
    for col in df.columns:
        if col not in ['datetime', 'station']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Add temporal features
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df['period_of_day'] = df['datetime'].dt.hour // 2
    
    print("Creating heatmap comparison...")
    
    # Filter to specific station and species
    species = 'Spotted seatrout'
    station = '14M'
    station_df = df[df['station'] == station].copy()
    
    if species not in station_df.columns:
        print(f"⚠️ Species '{species}' not found in data")
        return False
    
    # Find top correlated acoustic indices
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
    from scipy.stats import pearsonr
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
    
    print(f"Selected top correlated acoustic indices for {species}:")
    for i, item in enumerate(correlations[:4], 1):
        print(f"   {i}. {item['index']} (r = {item['correlation']:.3f})")
    
    # Create heat map data function
    def create_heatmap_data(data_column, station_df, normalize=True):
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
        
        mask = counts > 0
        heatmap_data[mask] = heatmap_data[mask] / counts[mask]
        
        if normalize:
            data_min, data_max = heatmap_data.min(), heatmap_data.max()
            if data_max > data_min:
                heatmap_data = (heatmap_data - data_min) / (data_max - data_min)
        
        return heatmap_data
    
    # Create the comparison figure
    n_plots = len(acoustic_indices) + 1
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
    
    # Use corrected orientation: transpose and set extent
    im1 = axes_flat[0].imshow(species_heatmap.T, aspect='auto', cmap='viridis', origin='lower',
                             extent=[1, 365, 0, 11])
    axes_flat[0].set_title(f'{species}\\n(Manual Detections)', fontsize=12, fontweight='bold')
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
            
            # Use corrected orientation
            im = axes_flat[i].imshow(acoustic_heatmap.T, aspect='auto', cmap='viridis', origin='lower',
                                   extent=[1, 365, 0, 11])
            axes_flat[i].set_title(f'{acoustic_idx}\\n(Acoustic Index)', fontsize=12)
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
    print(f"✅ Saved corrected comparison figure: {fig_path}")
    
    plt.close()
    return True

def update_report_narrative():
    """Update the report with the corrected narrative."""
    
    print("\\n📝 UPDATING REPORT NARRATIVE")
    print("="*50)
    
    # Read the current Quarto file
    qmd_file = Path("Marine_Acoustic_Discovery_Report_v2.qmd")
    if not qmd_file.exists():
        print("⚠️ Quarto file not found")
        return False
    
    with open(qmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the section that needs updating
    pattern_section = """## The Hidden Patterns Revealed

When we plotted fish detection data this way, remarkably clear patterns emerged:
- **Silver perch**: Sharp seasonal peaks with consistent daily patterns
- **Oyster toadfish**: Tight spring spawning windows with dawn/dusk activity
- **Spotted seatrout**: Summer-focused activity with midday peaks

These patterns matched known fish biology."""
    
    new_section = """## The Hidden Patterns Revealed

### The Pattern Discovery

The breakthrough came when we started looking at our acoustic index heat maps alongside manual detection patterns. The visual similarity was striking - certain acoustic indices seemed to "light up" in the same temporal patterns as fish detections.

![Figure 4: Acoustic Index vs Manual Detection Comparison](output/phase6_temporal_correlation/figures/acoustic_vs_manual_detection_comparison_spotted_seatrout_station_14M.png){width=100%}
*Side-by-side heat maps showing manual detection patterns and acoustic indices. The visual similarity between these patterns was our first hint that there were discoverable temporal patterns in the data.*

### From Patterns to Probabilities

Seeing these patterns prompted us to reframe our approach. Instead of "Will fish be calling tomorrow?" we asked "Given that it's May 15th at 6 AM, how likely is it that fish are calling right now?"

This led us to systematically visualize our data as **2D probability surfaces** mapping fish activity likelihood across:
- **Day of year** (seasonal patterns) 
- **Time of day** (daily rhythms)

We created these surfaces by applying 2D Gaussian kernels to the raw detection patterns shown above.

### Species-Specific Activity Patterns

When we plotted fish detection data this way, remarkably clear patterns emerged:
- **Silver perch**: Sharp seasonal peaks with consistent daily patterns
- **Oyster toadfish**: Tight spring spawning windows with dawn/dusk activity  
- **Spotted seatrout**: Summer-focused activity with midday peaks

These patterns matched known fish biology."""
    
    # Replace the section
    if pattern_section in content:
        content = content.replace(pattern_section, new_section)
        
        # Write back
        with open(qmd_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated report narrative")
        return True
    else:
        print("⚠️ Could not find section to update")
        return False

def main():
    """Run the key figure regeneration."""
    
    print("🔄 REGENERATING KEY FIGURES")
    print("="*60)
    print("This will regenerate essential figures with corrected formatting.")
    
    success_count = 0
    
    # Step 1: Regenerate comparison figure
    if regenerate_comparison_figure():
        success_count += 1
    
    # Step 2: Update narrative
    if update_report_narrative():
        success_count += 1
    
    print(f"\\n✅ Completed {success_count}/2 updates")
    
    if success_count == 2:
        print("\\n🎉 SUCCESS! Next steps:")
        print("1. Regenerate HTML: quarto render Marine_Acoustic_Discovery_Report_v2.qmd")
        print("2. Update deployment: python prepare_netlify_deploy.py")
        return True
    else:
        print("\\n⚠️ Some updates failed. Check output above.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)