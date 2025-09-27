#!/usr/bin/env python3
"""
Script 3: Community Metrics
===========================

Purpose: Define and compute community-level biological targets
Key Question: What biological patterns do we want to predict?

This script takes the aligned dataset from Script 1 and creates community-level
biological metrics that serve as targets for our acoustic vs environmental analysis.
Focus is on species richness, diversity, and activity levels rather than individual species.

Key Outputs:
- data/processed/community_metrics.parquet - All target variables
- data/processed/community_patterns_summary.json - Temporal pattern statistics  
- figures/03_community_temporal_patterns.png - Seasonal/diel patterns
- figures/03_community_metrics_distributions.png - Target variable distributions
- figures/03_vessel_impact_on_biology.png - Community metrics with/without vessels

Reference Sources:
- python/scripts/notebooks/04_fish_and_indices_patterns.py - Community pattern analysis
- python/scripts/notebooks/06_community_pattern_detection.py - Target variable definitions
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def find_project_root():
    """Find main project root (mbon-dash-2025) by looking for data/raw folder structure"""
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data" / "raw").exists() and project_root != project_root.parent:
        project_root = project_root.parent
    return project_root

# Set up paths using standard pattern
PROJECT_ROOT = find_project_root()
DATA_ROOT = PROJECT_ROOT / "data"
INPUT_DIR = DATA_ROOT / "processed"  # Main project processed folder
OUTPUT_DIR = DATA_ROOT / "processed"  # Main project processed folder
FIGURE_DIR = DATA_ROOT / "processed" / "fresh_start_figures"  # Figures subfolder

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("SCRIPT 3: COMMUNITY METRICS")
print("="*60)
print(f"Project root: {PROJECT_ROOT}")
print(f"Input directory: {INPUT_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Figure directory: {FIGURE_DIR}")
print()

def load_aligned_dataset():
    """Load the aligned dataset from Script 1"""
    print("1. LOADING ALIGNED DATASET")
    print("-" * 30)
    
    input_file = INPUT_DIR / "aligned_dataset_2021.parquet"
    
    if not input_file.exists():
        raise FileNotFoundError(f"Aligned dataset not found: {input_file}\nPlease run Script 1 first.")
    
    df = pd.read_parquet(input_file)
    print(f"✓ Loaded aligned dataset: {df.shape}")
    print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"Stations: {sorted(df['station'].value_counts().index.tolist())}")
    print()
    
    return df

def identify_species_columns(df):
    """Identify fish, dolphin, and other biological detection columns"""
    print("2. IDENTIFYING SPECIES AND BIOLOGICAL COLUMNS")
    print("-" * 45)
    
    # Filter out administrative/metadata columns
    exclude_cols = ['datetime', 'station', 'Date', 'Date ', 'Time', 'Deployment ID', 'File']
    potential_species = [col for col in df.columns if col not in exclude_cols]
    
    # Categorize species based on your metadata knowledge
    fish_species = []
    dolphin_species = []
    vessel_anthro = []
    unknown_bio = []
    
    for col in potential_species:
        col_lower = col.lower()
        if any(fish in col_lower for fish in ['perch', 'drum', 'seatrout', 'toadfish', 'croaker', 'weakfish']):
            fish_species.append(col)
        elif 'dolphin' in col_lower:
            dolphin_species.append(col)
        elif any(anthro in col_lower for anthro in ['vessel', 'anthropogenic']):
            vessel_anthro.append(col)
        elif 'biological' in col_lower:
            unknown_bio.append(col)
    
    print(f"Fish species ({len(fish_species)}):")
    for species in fish_species:
        print(f"  - {species}")
    
    print(f"\nDolphin species ({len(dolphin_species)}):")
    for species in dolphin_species:
        print(f"  - {species}")
    
    print(f"\nVessel/Anthropogenic ({len(vessel_anthro)}):")
    for species in vessel_anthro:
        print(f"  - {species}")
        
    print(f"\nUnknown biological ({len(unknown_bio)}):")
    for species in unknown_bio:
        print(f"  - {species}")
    
    print()
    return fish_species, dolphin_species, vessel_anthro, unknown_bio

def create_community_metrics(df, fish_species, dolphin_species, unknown_bio):
    """Create community-level biological metrics"""
    print("3. CREATING COMMUNITY METRICS")
    print("-" * 35)
    
    df_metrics = df[['datetime', 'station']].copy()
    
    # 1. Total Fish Calling Intensity (sum across all fish species)
    if fish_species:
        df_metrics['total_fish_intensity'] = df[fish_species].sum(axis=1)
        print(f"✓ Total fish intensity: sum of {len(fish_species)} fish species")
    else:
        df_metrics['total_fish_intensity'] = 0
        print("⚠️ No fish species found")
    
    # 2. Fish Species Richness (number of species calling in each time period)
    if fish_species:
        df_metrics['fish_species_richness'] = (df[fish_species] > 0).sum(axis=1)
        print(f"✓ Fish species richness: count of active species from {len(fish_species)} total")
    else:
        df_metrics['fish_species_richness'] = 0
    
    # 3. Total Dolphin Activity (sum of all dolphin detection types)
    if dolphin_species:
        df_metrics['total_dolphin_activity'] = df[dolphin_species].sum(axis=1)
        print(f"✓ Total dolphin activity: sum of {len(dolphin_species)} dolphin detection types")
    else:
        df_metrics['total_dolphin_activity'] = 0
        print("⚠️ No dolphin species found")
    
    # 4. Total Biological Activity (fish + dolphins + unknown biological)
    bio_columns = fish_species + dolphin_species + unknown_bio
    if bio_columns:
        df_metrics['total_biological_activity'] = df[bio_columns].sum(axis=1)
        print(f"✓ Total biological activity: sum of {len(bio_columns)} biological detection types")
    else:
        df_metrics['total_biological_activity'] = 0
    
    # 5. Activity Level Percentiles (binary indicators for different activity thresholds)
    if fish_species:
        fish_intensity = df_metrics['total_fish_intensity']
        
        # Any fish activity (> 0)
        df_metrics['any_fish_activity'] = (fish_intensity > 0).astype(int)
        
        # High activity thresholds based on percentiles
        percentile_75 = fish_intensity.quantile(0.75)
        percentile_90 = fish_intensity.quantile(0.90)
        
        df_metrics['fish_activity_75th'] = (fish_intensity >= percentile_75).astype(int)
        df_metrics['fish_activity_90th'] = (fish_intensity >= percentile_90).astype(int)
        
        print(f"✓ Activity thresholds: 75th percentile = {percentile_75:.2f}, 90th percentile = {percentile_90:.2f}")
    else:
        df_metrics['any_fish_activity'] = 0
        df_metrics['fish_activity_75th'] = 0  
        df_metrics['fish_activity_90th'] = 0
    
    # 6. Temporal features for modeling
    df_metrics['hour_of_day'] = df_metrics['datetime'].dt.hour
    df_metrics['day_of_year'] = df_metrics['datetime'].dt.dayofyear
    df_metrics['month'] = df_metrics['datetime'].dt.month
    df_metrics['season'] = df_metrics['month'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring', 
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    print(f"✓ Added temporal features: hour, day_of_year, month, season")
    print(f"Final community metrics dataset: {df_metrics.shape}")
    print()
    
    return df_metrics

def analyze_vessel_impact(df, df_metrics, vessel_anthro):
    """Analyze how vessel presence affects biological community metrics"""
    print("4. ANALYZING VESSEL IMPACT ON BIOLOGY")
    print("-" * 40)
    
    if not vessel_anthro:
        print("⚠️ No vessel detection columns found - skipping vessel impact analysis")
        return {}
    
    # Get vessel presence indicator - prioritize 'Vessel' column
    vessel_col = None
    if 'Vessel' in vessel_anthro:
        vessel_col = 'Vessel'
    elif vessel_anthro:
        vessel_col = vessel_anthro[0]  # Fallback to first available
    
    if vessel_col is None:
        print("⚠️ No suitable vessel column found")
        return {}
    
    vessel_present = df[vessel_col] > 0
    
    vessel_impact = {}
    
    # Compare community metrics with and without vessels
    metrics_to_compare = ['total_fish_intensity', 'fish_species_richness', 'total_dolphin_activity', 'total_biological_activity']
    
    for metric in metrics_to_compare:
        if metric in df_metrics.columns:
            with_vessels = df_metrics[vessel_present][metric]
            without_vessels = df_metrics[~vessel_present][metric]
            
            vessel_impact[metric] = {
                'with_vessels_mean': float(with_vessels.mean()),
                'without_vessels_mean': float(without_vessels.mean()),
                'with_vessels_count': int(vessel_present.sum()),
                'without_vessels_count': int((~vessel_present).sum()),
                'difference': float(with_vessels.mean() - without_vessels.mean()),
                'percent_change': float((with_vessels.mean() - without_vessels.mean()) / without_vessels.mean() * 100) if without_vessels.mean() > 0 else 0
            }
    
    print(f"Vessel presence analysis ({vessel_col}):")
    print(f"  Periods with vessels: {vessel_present.sum()}")
    print(f"  Periods without vessels: {(~vessel_present).sum()}")
    
    for metric, stats in vessel_impact.items():
        print(f"  {metric}:")
        print(f"    With vessels: {stats['with_vessels_mean']:.3f}")
        print(f"    Without vessels: {stats['without_vessels_mean']:.3f}")
        print(f"    Difference: {stats['difference']:.3f} ({stats['percent_change']:+.1f}%)")
    
    print()
    return vessel_impact

def create_temporal_visualizations(df_metrics):
    """Create visualizations of temporal patterns in community metrics"""
    print("5. CREATING TEMPORAL PATTERN VISUALIZATIONS")
    print("-" * 45)
    
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create comprehensive temporal analysis figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Community Temporal Patterns - 2021', fontsize=16, fontweight='bold')
    
    # 1. Seasonal patterns (by month)
    ax1 = axes[0, 0]
    monthly_fish = df_metrics.groupby('month')['total_fish_intensity'].mean()
    monthly_fish.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Seasonal Fish Activity Pattern')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Mean Fish Intensity')
    ax1.tick_params(axis='x', rotation=0)
    
    # 2. Diel patterns (by hour)
    ax2 = axes[0, 1]
    hourly_fish = df_metrics.groupby('hour_of_day')['total_fish_intensity'].mean()
    hourly_fish.plot(ax=ax2, marker='o', color='orange')
    ax2.set_title('Diel Fish Activity Pattern')
    ax2.set_xlabel('Hour of Day')
    ax2.set_ylabel('Mean Fish Intensity')
    ax2.set_xlim(0, 23)
    
    # 3. Species richness by season
    ax3 = axes[0, 2]
    seasonal_richness = df_metrics.groupby('season')['fish_species_richness'].mean()
    seasonal_richness.plot(kind='bar', ax=ax3, color='lightgreen')
    ax3.set_title('Seasonal Species Richness')
    ax3.set_xlabel('Season')
    ax3.set_ylabel('Mean Species Count')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Activity levels distribution
    ax4 = axes[1, 0]
    activity_levels = df_metrics[['any_fish_activity', 'fish_activity_75th', 'fish_activity_90th']].sum()
    activity_levels.plot(kind='bar', ax=ax4, color=['lightcoral', 'gold', 'red'])
    ax4.set_title('Activity Level Frequencies')
    ax4.set_xlabel('Activity Threshold')
    ax4.set_ylabel('Number of Time Periods')
    ax4.tick_params(axis='x', rotation=45)
    
    # 5. Station comparison
    ax5 = axes[1, 1]
    station_fish = df_metrics.groupby('station')['total_fish_intensity'].mean()
    station_fish.plot(kind='bar', ax=ax5, color='lightblue')
    ax5.set_title('Fish Activity by Station')
    ax5.set_xlabel('Station')
    ax5.set_ylabel('Mean Fish Intensity')
    ax5.tick_params(axis='x', rotation=0)
    
    # 6. Dolphins vs Fish activity
    ax6 = axes[1, 2]
    ax6.scatter(df_metrics['total_fish_intensity'], df_metrics['total_dolphin_activity'], 
                alpha=0.5, s=1)
    ax6.set_title('Fish vs Dolphin Activity')
    ax6.set_xlabel('Total Fish Intensity')
    ax6.set_ylabel('Total Dolphin Activity')
    
    plt.tight_layout()
    temporal_file = FIGURE_DIR / "03_community_temporal_patterns.png"
    plt.savefig(temporal_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Temporal patterns saved: {temporal_file}")

def create_distribution_visualizations(df_metrics):
    """Create visualizations of community metrics distributions"""
    print("6. CREATING DISTRIBUTION VISUALIZATIONS")
    print("-" * 40)
    
    # Community metrics distributions
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Community Metrics Distributions - 2021', fontsize=16, fontweight='bold')
    
    # 1. Total fish intensity distribution
    ax1 = axes[0, 0]
    df_metrics['total_fish_intensity'].hist(bins=50, ax=ax1, color='skyblue', alpha=0.7)
    ax1.set_title('Total Fish Intensity Distribution')
    ax1.set_xlabel('Fish Intensity')
    ax1.set_ylabel('Frequency')
    ax1.axvline(df_metrics['total_fish_intensity'].mean(), color='red', linestyle='--', label=f'Mean: {df_metrics["total_fish_intensity"].mean():.2f}')
    ax1.legend()
    
    # 2. Species richness distribution  
    ax2 = axes[0, 1]
    df_metrics['fish_species_richness'].hist(bins=range(int(df_metrics['fish_species_richness'].max())+2), 
                                           ax=ax2, color='lightgreen', alpha=0.7)
    ax2.set_title('Species Richness Distribution')
    ax2.set_xlabel('Number of Species')
    ax2.set_ylabel('Frequency')
    
    # 3. Total biological activity distribution
    ax3 = axes[1, 0]
    df_metrics['total_biological_activity'].hist(bins=50, ax=ax3, color='orange', alpha=0.7)
    ax3.set_title('Total Biological Activity Distribution')
    ax3.set_xlabel('Biological Activity')
    ax3.set_ylabel('Frequency')
    
    # 4. Activity summary statistics
    ax4 = axes[1, 1]
    summary_stats = pd.DataFrame({
        'Total Fish': df_metrics['total_fish_intensity'].describe(),
        'Species Richness': df_metrics['fish_species_richness'].describe(),
        'Total Biological': df_metrics['total_biological_activity'].describe()
    })
    
    # Create text summary
    summary_text = f"""
COMMUNITY METRICS SUMMARY

Total Fish Intensity:
  Mean: {df_metrics['total_fish_intensity'].mean():.3f}
  Std:  {df_metrics['total_fish_intensity'].std():.3f}
  Max:  {df_metrics['total_fish_intensity'].max():.3f}

Species Richness:
  Mean: {df_metrics['fish_species_richness'].mean():.3f}  
  Max:  {int(df_metrics['fish_species_richness'].max())} species

Activity Frequencies:
  Any Activity: {df_metrics['any_fish_activity'].sum():,} periods ({df_metrics['any_fish_activity'].mean()*100:.1f}%)
  75th Percentile: {df_metrics['fish_activity_75th'].sum():,} periods ({df_metrics['fish_activity_75th'].mean()*100:.1f}%)
  90th Percentile: {df_metrics['fish_activity_90th'].sum():,} periods ({df_metrics['fish_activity_90th'].mean()*100:.1f}%)
"""
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1) 
    ax4.axis('off')
    
    plt.tight_layout()
    dist_file = FIGURE_DIR / "03_community_metrics_distributions.png"
    plt.savefig(dist_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Distributions saved: {dist_file}")

def create_vessel_impact_visualization(df_metrics, vessel_impact):
    """Create visualization of vessel impact on biological community"""
    print("7. CREATING VESSEL IMPACT VISUALIZATION")
    print("-" * 40)
    
    if not vessel_impact:
        print("⚠️ No vessel impact data - skipping visualization")
        return
        
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Vessel Impact on Biological Community - 2021', fontsize=16, fontweight='bold')
    
    # Extract comparison data
    metrics = list(vessel_impact.keys())
    with_vessels = [vessel_impact[m]['with_vessels_mean'] for m in metrics]
    without_vessels = [vessel_impact[m]['without_vessels_mean'] for m in metrics]
    
    # 1. Bar comparison
    ax1 = axes[0, 0]
    x = np.arange(len(metrics))
    width = 0.35
    
    ax1.bar(x - width/2, with_vessels, width, label='With Vessels', color='red', alpha=0.7)
    ax1.bar(x + width/2, without_vessels, width, label='Without Vessels', color='blue', alpha=0.7)
    
    ax1.set_title('Community Metrics: With vs Without Vessels')
    ax1.set_ylabel('Mean Activity Level')
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.replace('_', ' ').title() for m in metrics], rotation=45)
    ax1.legend()
    
    # 2. Percent change
    ax2 = axes[0, 1]
    percent_changes = [vessel_impact[m]['percent_change'] for m in metrics]
    colors = ['red' if x < 0 else 'green' for x in percent_changes]
    
    bars = ax2.bar(range(len(metrics)), percent_changes, color=colors, alpha=0.7)
    ax2.set_title('Percent Change with Vessel Presence')
    ax2.set_ylabel('Percent Change (%)')
    ax2.set_xticks(range(len(metrics)))
    ax2.set_xticklabels([m.replace('_', ' ').title() for m in metrics], rotation=45)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Add value labels on bars
    for bar, pct in zip(bars, percent_changes):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + (1 if height >= 0 else -3), 
                f'{pct:+.1f}%', ha='center', va='bottom' if height >= 0 else 'top')
    
    # 3. Sample counts
    ax3 = axes[1, 0]
    vessel_counts = [vessel_impact[metrics[0]]['with_vessels_count'], vessel_impact[metrics[0]]['without_vessels_count']]
    ax3.pie(vessel_counts, labels=['With Vessels', 'Without Vessels'], autopct='%1.1f%%', 
            colors=['red', 'blue'])
    ax3.set_title('Time Period Distribution')
    
    # 4. Summary statistics table
    ax4 = axes[1, 1]
    summary_text = "VESSEL IMPACT SUMMARY\n" + "="*25 + "\n\n"
    
    for metric in metrics:
        stats = vessel_impact[metric]
        summary_text += f"{metric.replace('_', ' ').title()}:\n"
        summary_text += f"  With vessels: {stats['with_vessels_mean']:.3f} (n={stats['with_vessels_count']})\n"
        summary_text += f"  Without: {stats['without_vessels_mean']:.3f} (n={stats['without_vessels_count']})\n"
        summary_text += f"  Change: {stats['percent_change']:+.1f}%\n\n"
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=9,
             verticalalignment='top', fontfamily='monospace')
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)
    ax4.axis('off')
    
    plt.tight_layout()
    vessel_file = FIGURE_DIR / "03_vessel_impact_on_biology.png"
    plt.savefig(vessel_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Vessel impact visualization saved: {vessel_file}")

def save_results(df_metrics, vessel_impact, fish_species, dolphin_species):
    """Save community metrics and analysis results"""
    print("8. SAVING RESULTS")
    print("-" * 20)
    
    # Save community metrics dataset
    output_file = OUTPUT_DIR / "community_metrics.parquet"
    df_metrics.to_parquet(output_file, index=False)
    print(f"✓ Community metrics saved: {output_file}")
    
    # Create comprehensive summary
    summary_stats = {
        'generation_timestamp': datetime.now().isoformat(),
        'dataset_summary': {
            'total_records': len(df_metrics),
            'stations': sorted(df_metrics['station'].unique().tolist()),
            'date_range': (df_metrics['datetime'].min().isoformat(), df_metrics['datetime'].max().isoformat()),
            'temporal_coverage': {
                'months': sorted(df_metrics['month'].unique().tolist()),
                'hours': sorted(df_metrics['hour_of_day'].unique().tolist())
            }
        },
        'species_categories': {
            'fish_species': fish_species,
            'dolphin_species': dolphin_species,
            'fish_count': len(fish_species),
            'dolphin_count': len(dolphin_species)
        },
        'community_metrics': {
            'total_fish_intensity': {
                'mean': float(df_metrics['total_fish_intensity'].mean()),
                'std': float(df_metrics['total_fish_intensity'].std()), 
                'max': float(df_metrics['total_fish_intensity'].max()),
                'min': float(df_metrics['total_fish_intensity'].min())
            },
            'fish_species_richness': {
                'mean': float(df_metrics['fish_species_richness'].mean()),
                'max': int(df_metrics['fish_species_richness'].max()),
                'min': int(df_metrics['fish_species_richness'].min())
            },
            'activity_frequencies': {
                'any_activity_periods': int(df_metrics['any_fish_activity'].sum()),
                'any_activity_percent': float(df_metrics['any_fish_activity'].mean() * 100),
                'high_activity_75th_periods': int(df_metrics['fish_activity_75th'].sum()),
                'high_activity_90th_periods': int(df_metrics['fish_activity_90th'].sum())
            }
        },
        'vessel_impact': vessel_impact,
        'target_variables': [
            'total_fish_intensity', 'fish_species_richness', 'total_dolphin_activity',
            'total_biological_activity', 'any_fish_activity', 'fish_activity_75th', 'fish_activity_90th'
        ]
    }
    
    # Save summary report
    summary_file = OUTPUT_DIR / "community_patterns_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary_stats, f, indent=2, default=str)
    print(f"✓ Patterns summary saved: {summary_file}")
    
    # Display key results
    print(f"\nCOMMUNITY METRICS SUMMARY:")
    print(f"Target variables created: {len(summary_stats['target_variables'])}")
    print(f"Fish species analyzed: {len(fish_species)}")
    print(f"Mean fish intensity: {summary_stats['community_metrics']['total_fish_intensity']['mean']:.3f}")
    print(f"Max species richness: {summary_stats['community_metrics']['fish_species_richness']['max']} species")
    print(f"Active periods: {summary_stats['community_metrics']['activity_frequencies']['any_activity_percent']:.1f}%")

def main():
    """Main execution function"""
    print("Starting community metrics pipeline...")
    
    # Load data
    df = load_aligned_dataset()
    
    # Identify species categories
    fish_species, dolphin_species, vessel_anthro, unknown_bio = identify_species_columns(df)
    
    # Create community metrics
    df_metrics = create_community_metrics(df, fish_species, dolphin_species, unknown_bio)
    
    # Analyze vessel impact
    vessel_impact = analyze_vessel_impact(df, df_metrics, vessel_anthro)
    
    # Create visualizations
    create_temporal_visualizations(df_metrics)
    create_distribution_visualizations(df_metrics)
    create_vessel_impact_visualization(df_metrics, vessel_impact)
    
    # Save results
    save_results(df_metrics, vessel_impact, fish_species, dolphin_species)
    
    print()
    print("="*60)
    print("COMMUNITY METRICS COMPLETE")
    print("="*60)
    print(f"Key outputs:")
    print(f"- Community metrics: {OUTPUT_DIR / 'community_metrics.parquet'}")
    print(f"- Patterns summary: {OUTPUT_DIR / 'community_patterns_summary.json'}")
    print(f"- Temporal patterns: {FIGURE_DIR / '03_community_temporal_patterns.png'}")
    print(f"- Distributions: {FIGURE_DIR / '03_community_metrics_distributions.png'}")
    print(f"- Vessel impact: {FIGURE_DIR / '03_vessel_impact_on_biology.png'}")

if __name__ == "__main__":
    main()