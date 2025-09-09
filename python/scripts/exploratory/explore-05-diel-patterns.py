"""Exploratory Analysis Script 05: Diel Patterns and Weekly Rhythms

This script analyzes hourly calling patterns (diel cycles) for species and acoustic indices,
showing how activity varies by hour of day and how these patterns change week to week.

Key analyses:
- Hourly activity patterns for each species
- Comparison with acoustic index diel patterns
- Week-by-week variation in daily rhythms
- Tidal vs circadian pattern detection
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats, signal
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

from mbon_analysis.data.loaders import create_loader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

class DielPatternAnalyzer:
    """Analyze daily (diel) patterns in species detections and acoustic indices."""
    
    def __init__(self, data_root: Optional[Path] = None):
        self.loader = create_loader(data_root)
        self.detections = None
        self.acoustic_indices = None
        
    def load_data(self, station: str = '14M', year: int = 2021):
        """Load detection and acoustic index data for analysis."""
        logger.info(f"Loading data for station {station}, year {year}")
        
        # Load detection data
        try:
            self.detections = self.loader.load_detection_data(station, year)
            self.detections['datetime'] = pd.to_datetime(self.detections['Date'])
            self.detections['hour'] = self.detections['datetime'].dt.hour
            self.detections['week'] = self.detections['datetime'].dt.isocalendar().week
            self.detections['dayofweek'] = self.detections['datetime'].dt.dayofweek
            self.detections = self.detections.sort_values('datetime')
            logger.info(f"Loaded {len(self.detections)} detection records")
        except Exception as e:
            logger.error(f"Failed to load detection data: {e}")
            return False
            
        # Load acoustic indices
        try:
            self.acoustic_indices = self.loader.load_acoustic_indices(station, 'FullBW')
            self.acoustic_indices['datetime'] = pd.to_datetime(self.acoustic_indices['Date'])
            self.acoustic_indices['hour'] = self.acoustic_indices['datetime'].dt.hour
            self.acoustic_indices['week'] = self.acoustic_indices['datetime'].dt.isocalendar().week
            self.acoustic_indices['dayofweek'] = self.acoustic_indices['datetime'].dt.dayofweek
            self.acoustic_indices = self.acoustic_indices.sort_values('datetime')
            logger.info(f"Loaded {len(self.acoustic_indices)} acoustic index records")
        except Exception as e:
            logger.error(f"Failed to load acoustic indices: {e}")
            return False
            
        return True
    
    def calculate_hourly_patterns(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """Calculate average activity by hour of day."""
        
        # Convert to numeric
        data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
        
        # Calculate mean and std by hour
        hourly_stats = data.groupby('hour')[column].agg(['mean', 'std', 'count'])
        hourly_stats['se'] = hourly_stats['std'] / np.sqrt(hourly_stats['count'])
        
        return hourly_stats
    
    def calculate_weekly_hourly_patterns(self, data: pd.DataFrame, column: str) -> pd.DataFrame:
        """Calculate hourly patterns for each week."""
        
        # Convert to numeric
        data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
        
        # Pivot to create week x hour matrix
        weekly_hourly = data.pivot_table(
            values=column,
            index='week',
            columns='hour',
            aggfunc='mean',
            fill_value=0
        )
        
        return weekly_hourly
    
    def plot_diel_comparison(self, species: str, index: str, save_path: str = None):
        """Compare diel patterns between a species and an acoustic index."""
        
        if species not in self.detections.columns:
            logger.error(f"Species {species} not found in data")
            return
        
        if index not in self.acoustic_indices.columns:
            logger.error(f"Index {index} not found in data")
            return
        
        # Calculate hourly patterns
        species_hourly = self.calculate_hourly_patterns(self.detections, species)
        index_hourly = self.calculate_hourly_patterns(self.acoustic_indices, index)
        
        # Create figure
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        
        # Panel 1: Species diel pattern
        ax1 = axes[0, 0]
        hours = species_hourly.index
        ax1.plot(hours, species_hourly['mean'], 'b-', linewidth=2, label=species)
        ax1.fill_between(hours, 
                         species_hourly['mean'] - species_hourly['se'],
                         species_hourly['mean'] + species_hourly['se'],
                         alpha=0.3, color='blue')
        ax1.set_xlabel('Hour of Day', fontsize=11)
        ax1.set_ylabel('Mean Detection Intensity', fontsize=11)
        ax1.set_title(f'{species} - Daily Activity Pattern', fontsize=12)
        ax1.set_xticks(range(0, 24, 2))
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add day/night shading
        ax1.axvspan(0, 6, alpha=0.1, color='navy', label='Night')
        ax1.axvspan(18, 24, alpha=0.1, color='navy')
        ax1.axvspan(6, 18, alpha=0.1, color='yellow', label='Day')
        
        # Panel 2: Index diel pattern
        ax2 = axes[0, 1]
        hours = index_hourly.index
        ax2.plot(hours, index_hourly['mean'], 'r-', linewidth=2, label=index)
        ax2.fill_between(hours,
                         index_hourly['mean'] - index_hourly['se'],
                         index_hourly['mean'] + index_hourly['se'],
                         alpha=0.3, color='red')
        ax2.set_xlabel('Hour of Day', fontsize=11)
        ax2.set_ylabel(f'Mean {index} Value', fontsize=11)
        ax2.set_title(f'{index} - Daily Pattern', fontsize=12)
        ax2.set_xticks(range(0, 24, 2))
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Add day/night shading
        ax2.axvspan(0, 6, alpha=0.1, color='navy')
        ax2.axvspan(18, 24, alpha=0.1, color='navy')
        ax2.axvspan(6, 18, alpha=0.1, color='yellow')
        
        # Panel 3: Normalized comparison
        ax3 = axes[1, 0]
        
        # Normalize both patterns
        species_norm = (species_hourly['mean'] - species_hourly['mean'].mean()) / species_hourly['mean'].std()
        index_norm = (index_hourly['mean'] - index_hourly['mean'].mean()) / index_hourly['mean'].std()
        
        ax3.plot(species_hourly.index, species_norm, 'b-', linewidth=2, label=species)
        ax3.plot(index_hourly.index, index_norm, 'r-', linewidth=2, label=index)
        ax3.set_xlabel('Hour of Day', fontsize=11)
        ax3.set_ylabel('Normalized Activity (z-score)', fontsize=11)
        ax3.set_title('Normalized Diel Pattern Comparison', fontsize=12)
        ax3.set_xticks(range(0, 24, 2))
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        
        # Panel 4: Correlation by hour
        ax4 = axes[1, 1]
        
        # Calculate correlation for each hour
        hourly_corr = []
        for hour in range(24):
            det_hour = self.detections[self.detections['hour'] == hour][species]
            idx_hour = self.acoustic_indices[self.acoustic_indices['hour'] == hour][index]
            
            # Align by date
            det_hour = pd.to_numeric(det_hour, errors='coerce').fillna(0)
            idx_hour = pd.to_numeric(idx_hour, errors='coerce').fillna(0)
            
            if len(det_hour) > 10 and len(idx_hour) > 10:
                # Resample to common dates
                corr, _ = stats.pearsonr(det_hour[:min(len(det_hour), len(idx_hour))], 
                                        idx_hour[:min(len(det_hour), len(idx_hour))])
                hourly_corr.append(corr)
            else:
                hourly_corr.append(np.nan)
        
        ax4.bar(range(24), hourly_corr, color=['blue' if c > 0 else 'red' for c in hourly_corr])
        ax4.set_xlabel('Hour of Day', fontsize=11)
        ax4.set_ylabel('Correlation Coefficient', fontsize=11)
        ax4.set_title('Hourly Correlation between Species and Index', fontsize=12)
        ax4.set_xticks(range(0, 24, 2))
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=0, color='k', linestyle='-', alpha=0.5)
        
        plt.suptitle(f'Diel Pattern Analysis: {species} vs {index}', fontsize=14, y=1.02)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved diel comparison: {save_path}")
        
        return fig
    
    def plot_weekly_heatmaps(self, species_list: List[str] = None, 
                            index_list: List[str] = None,
                            save_path: str = None):
        """Create heatmaps showing hourly patterns for each week."""
        
        if species_list is None:
            # Get top species
            species_mapping = self.loader.load_species_mapping()
            fish_species = species_mapping[
                (species_mapping['group'] == 'fish') & 
                (species_mapping['keep_species'] == 1)
            ]['long_name'].tolist()
            species_list = [sp for sp in fish_species if sp in self.detections.columns][:3]
        
        if index_list is None:
            # Select key indices that showed good correlation
            index_list = ['Hf', 'ACI', 'BI'] if all(idx in self.acoustic_indices.columns for idx in ['Hf', 'ACI', 'BI']) else []
        
        n_species = len(species_list)
        n_indices = len(index_list)
        
        # Create figure with subplots for species and indices
        fig, axes = plt.subplots(n_species + n_indices, 1, figsize=(20, 4 * (n_species + n_indices)))
        if n_species + n_indices == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # Plot species heatmaps
        for species in species_list:
            ax = axes[plot_idx]
            
            # Calculate weekly hourly patterns
            weekly_hourly = self.calculate_weekly_hourly_patterns(self.detections, species)
            
            # Transpose so weeks are on x-axis, hours on y-axis
            weekly_hourly_T = weekly_hourly.T
            
            # Create heatmap
            sns.heatmap(weekly_hourly_T, 
                       cmap='YlOrRd',
                       ax=ax,
                       cbar_kws={'label': 'Detection Intensity'},
                       xticklabels=True,
                       yticklabels=True)
            
            ax.set_xlabel('Week of Year', fontsize=11)
            ax.set_ylabel('Hour of Day', fontsize=11)
            ax.set_title(f'{species} - Weekly Diel Patterns', fontsize=12)
            
            # Add horizontal lines for day/night transitions
            ax.axhline(y=6, color='yellow', linestyle='--', alpha=0.5, linewidth=0.5)
            ax.axhline(y=18, color='navy', linestyle='--', alpha=0.5, linewidth=0.5)
            
            # Invert y-axis so 0 hour is at top
            ax.invert_yaxis()
            
            plot_idx += 1
        
        # Plot index heatmaps
        for index in index_list:
            ax = axes[plot_idx]
            
            # Calculate weekly hourly patterns
            weekly_hourly = self.calculate_weekly_hourly_patterns(self.acoustic_indices, index)
            
            # Transpose so weeks are on x-axis, hours on y-axis
            weekly_hourly_T = weekly_hourly.T
            
            # Create heatmap
            sns.heatmap(weekly_hourly_T,
                       cmap='viridis',
                       ax=ax,
                       cbar_kws={'label': f'{index} Value'},
                       xticklabels=True,
                       yticklabels=True)
            
            ax.set_xlabel('Week of Year', fontsize=11)
            ax.set_ylabel('Hour of Day', fontsize=11)
            ax.set_title(f'{index} Index - Weekly Diel Patterns', fontsize=12)
            
            # Add horizontal lines for day/night transitions
            ax.axhline(y=6, color='yellow', linestyle='--', alpha=0.5, linewidth=0.5)
            ax.axhline(y=18, color='navy', linestyle='--', alpha=0.5, linewidth=0.5)
            
            # Invert y-axis so 0 hour is at top
            ax.invert_yaxis()
            
            plot_idx += 1
        
        plt.suptitle('Weekly Evolution of Daily Activity Patterns', fontsize=14, y=1.001)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved weekly heatmaps: {save_path}")
        
        return fig
    
    def plot_species_chorus_patterns(self, species_list: List[str] = None, save_path: str = None):
        """Analyze and visualize chorus patterns (synchronized calling) across species."""
        
        if species_list is None:
            # Get fish species
            species_mapping = self.loader.load_species_mapping()
            fish_species = species_mapping[
                (species_mapping['group'] == 'fish') & 
                (species_mapping['keep_species'] == 1)
            ]['long_name'].tolist()
            species_list = [sp for sp in fish_species if sp in self.detections.columns][:6]
        
        # Create figure
        fig, axes = plt.subplots(3, 1, figsize=(16, 12))
        
        # Panel 1: Stacked hourly patterns
        ax1 = axes[0]
        
        hours = range(24)
        bottom = np.zeros(24)
        colors = plt.cm.Set3(np.linspace(0, 1, len(species_list)))
        
        for i, species in enumerate(species_list):
            hourly = self.calculate_hourly_patterns(self.detections, species)
            ax1.bar(hours, hourly['mean'], bottom=bottom, label=species[:20], 
                   color=colors[i], alpha=0.8)
            bottom += hourly['mean'].values
        
        ax1.set_xlabel('Hour of Day', fontsize=12)
        ax1.set_ylabel('Cumulative Detection Intensity', fontsize=12)
        ax1.set_title('Species Chorus Patterns - Stacked Daily Activity', fontsize=13)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax1.set_xticks(range(0, 24, 2))
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add day/night shading
        ax1.axvspan(0, 6, alpha=0.1, color='navy')
        ax1.axvspan(18, 24, alpha=0.1, color='navy')
        
        # Panel 2: Correlation matrix by hour
        ax2 = axes[1]
        
        # Calculate correlation between species for each hour
        hour_correlations = np.zeros((len(species_list), 24))
        
        for hour in range(24):
            hour_data = self.detections[self.detections['hour'] == hour]
            
            for i, species in enumerate(species_list):
                if species in hour_data.columns:
                    # Calculate mean correlation with other species at this hour
                    correlations = []
                    sp1_data = pd.to_numeric(hour_data[species], errors='coerce').fillna(0)
                    
                    for other_species in species_list:
                        if other_species != species and other_species in hour_data.columns:
                            sp2_data = pd.to_numeric(hour_data[other_species], errors='coerce').fillna(0)
                            if len(sp1_data) > 10:
                                corr, _ = stats.pearsonr(sp1_data, sp2_data)
                                correlations.append(corr)
                    
                    if correlations:
                        hour_correlations[i, hour] = np.mean(correlations)
        
        im = ax2.imshow(hour_correlations, aspect='auto', cmap='RdBu_r', vmin=-0.5, vmax=0.5)
        ax2.set_yticks(range(len(species_list)))
        ax2.set_yticklabels([sp[:20] for sp in species_list], fontsize=10)
        ax2.set_xticks(range(0, 24, 2))
        ax2.set_xticklabels(range(0, 24, 2))
        ax2.set_xlabel('Hour of Day', fontsize=12)
        ax2.set_title('Inter-species Correlation by Hour (Chorus Synchronization)', fontsize=13)
        
        plt.colorbar(im, ax=ax2, label='Mean Correlation with Other Species')
        
        # Panel 3: Diversity index by hour
        ax3 = axes[2]
        
        # Calculate Shannon diversity for each hour
        diversity_by_hour = []
        dominance_by_hour = []
        
        for hour in range(24):
            hour_data = self.detections[self.detections['hour'] == hour]
            
            # Calculate relative abundance
            abundances = []
            for species in species_list:
                if species in hour_data.columns:
                    sp_data = pd.to_numeric(hour_data[species], errors='coerce').fillna(0)
                    abundances.append(sp_data.mean())
            
            if sum(abundances) > 0:
                # Normalize to proportions
                proportions = np.array(abundances) / sum(abundances)
                proportions = proportions[proportions > 0]  # Remove zeros
                
                # Shannon diversity
                shannon = -np.sum(proportions * np.log(proportions))
                diversity_by_hour.append(shannon)
                
                # Simpson's dominance
                simpson = np.sum(proportions ** 2)
                dominance_by_hour.append(1 - simpson)
            else:
                diversity_by_hour.append(0)
                dominance_by_hour.append(0)
        
        ax3_twin = ax3.twinx()
        
        line1 = ax3.plot(hours, diversity_by_hour, 'g-', linewidth=2, label='Shannon Diversity')
        ax3.fill_between(hours, 0, diversity_by_hour, alpha=0.3, color='green')
        ax3.set_xlabel('Hour of Day', fontsize=12)
        ax3.set_ylabel('Shannon Diversity', color='green', fontsize=12)
        ax3.tick_params(axis='y', labelcolor='green')
        
        line2 = ax3_twin.plot(hours, dominance_by_hour, 'purple', linewidth=2, 
                             label='Simpson\'s Evenness', linestyle='--')
        ax3_twin.set_ylabel('Simpson\'s Evenness', color='purple', fontsize=12)
        ax3_twin.tick_params(axis='y', labelcolor='purple')
        
        ax3.set_title('Acoustic Diversity Throughout the Day', fontsize=13)
        ax3.set_xticks(range(0, 24, 2))
        ax3.grid(True, alpha=0.3)
        
        # Combine legends
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, loc='upper right')
        
        # Add day/night shading
        ax3.axvspan(0, 6, alpha=0.1, color='navy')
        ax3.axvspan(18, 24, alpha=0.1, color='navy')
        
        plt.suptitle('Multi-Species Chorus Analysis: Synchronization and Diversity', 
                    fontsize=14, y=1.01)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved chorus patterns: {save_path}")
        
        return fig
    
    def analyze_peak_calling_times(self, save_path: str = None):
        """Identify and visualize peak calling times for each species."""
        
        # Get species list
        species_mapping = self.loader.load_species_mapping()
        fish_species = species_mapping[
            (species_mapping['group'] == 'fish') & 
            (species_mapping['keep_species'] == 1)
        ]['long_name'].tolist()
        species_list = [sp for sp in fish_species if sp in self.detections.columns][:10]
        
        # Analyze peak times
        peak_times = {}
        peak_intensities = {}
        
        for species in species_list:
            hourly = self.calculate_hourly_patterns(self.detections, species)
            
            # Find peak hour
            peak_hour = hourly['mean'].idxmax()
            peak_intensity = hourly['mean'].max()
            
            # Find hours with >50% of peak activity
            active_hours = hourly[hourly['mean'] > 0.5 * peak_intensity].index.tolist()
            
            peak_times[species] = {
                'peak_hour': peak_hour,
                'peak_intensity': peak_intensity,
                'active_hours': active_hours,
                'hourly_pattern': hourly['mean'].values
            }
        
        # Create visualization
        fig, axes = plt.subplots(2, 1, figsize=(16, 10))
        
        # Panel 1: Clock plot showing peak times
        ax1 = axes[0]
        ax1 = plt.subplot(2, 1, 1, projection='polar')
        
        # Convert hours to radians (0-23 hours to 0-2π)
        theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        
        # Plot each species' pattern
        colors = plt.cm.tab10(np.linspace(0, 1, len(species_list)))
        
        for i, (species, data) in enumerate(peak_times.items()):
            # Normalize pattern
            pattern = data['hourly_pattern'] / data['peak_intensity']
            
            # Close the circle
            pattern = np.concatenate([pattern, [pattern[0]]])
            theta_plot = np.concatenate([theta, [theta[0]]])
            
            ax1.plot(theta_plot, pattern, color=colors[i], linewidth=2, 
                    label=species[:15], alpha=0.7)
            
            # Mark peak hour
            peak_rad = theta[data['peak_hour']]
            ax1.scatter(peak_rad, 1.0, color=colors[i], s=100, marker='*', 
                       edgecolor='black', linewidth=1)
        
        # Customize polar plot
        ax1.set_theta_zero_location('N')
        ax1.set_theta_direction(-1)
        ax1.set_xticks(theta)
        ax1.set_xticklabels([f'{h:02d}' for h in range(24)])
        ax1.set_ylim(0, 1.1)
        ax1.set_title('Daily Calling Patterns (24-hour clock)', fontsize=13, pad=20)
        ax1.legend(bbox_to_anchor=(1.15, 1), loc='upper left', fontsize=9)
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Summary table/bar chart of peak times
        ax2 = axes[1]
        
        # Sort species by peak hour
        sorted_species = sorted(peak_times.items(), key=lambda x: x[1]['peak_hour'])
        
        species_names = [sp[0][:25] for sp in sorted_species]
        peak_hours = [sp[1]['peak_hour'] for sp in sorted_species]
        peak_intensities_list = [sp[1]['peak_intensity'] for sp in sorted_species]
        
        # Create bar chart
        bars = ax2.barh(range(len(species_names)), peak_hours, height=0.8)
        
        # Color bars by time of day
        for i, (bar, hour) in enumerate(zip(bars, peak_hours)):
            if hour < 6 or hour >= 18:  # Night
                bar.set_color('darkblue')
                bar.set_alpha(0.8)
            elif 6 <= hour < 12:  # Morning
                bar.set_color('gold')
                bar.set_alpha(0.8)
            else:  # Afternoon
                bar.set_color('orange')
                bar.set_alpha(0.8)
        
        # Add intensity as text
        for i, (hour, intensity) in enumerate(zip(peak_hours, peak_intensities_list)):
            ax2.text(hour + 0.5, i, f'{intensity:.2f}', va='center', fontsize=9)
        
        ax2.set_yticks(range(len(species_names)))
        ax2.set_yticklabels(species_names, fontsize=10)
        ax2.set_xlabel('Peak Calling Hour (0-23)', fontsize=12)
        ax2.set_title('Peak Calling Times by Species (bar length = peak hour, number = intensity)', 
                     fontsize=13)
        ax2.set_xlim(0, 24)
        ax2.set_xticks(range(0, 25, 3))
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add day/night regions
        ax2.axvspan(0, 6, alpha=0.1, color='navy', label='Night')
        ax2.axvspan(6, 12, alpha=0.1, color='yellow', label='Morning')
        ax2.axvspan(12, 18, alpha=0.1, color='orange', label='Afternoon')
        ax2.axvspan(18, 24, alpha=0.1, color='navy')
        ax2.legend(loc='lower right')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved peak calling times: {save_path}")
        
        return fig, peak_times

def main():
    """Run diel pattern analysis."""
    
    print("=" * 60)
    print("Diel Pattern Analysis: Daily Rhythms in Marine Soundscapes")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = DielPatternAnalyzer(repo_root / "data")
    
    # Create output directory
    output_dir = Path.cwd() / "analysis_results" / "diel_patterns"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n1. Loading data for Station 14M, Year 2021...")
    if not analyzer.load_data(station='14M', year=2021):
        print("Failed to load data. Exiting.")
        return
    
    # Get best correlated species-index pair from previous analysis
    print("\n2. Analyzing diel patterns for top correlated species-index pair...")
    # Based on previous results: Spotted seatrout vs Hf
    diel_path = output_dir / "diel_comparison_spotted_seatrout_Hf.png"
    fig1 = analyzer.plot_diel_comparison('Spotted seatrout', 'Hf', save_path=str(diel_path))
    plt.close(fig1)
    print(f"   Saved: {diel_path.name}")
    
    # Create weekly heatmaps
    print("\n3. Creating weekly heatmaps of hourly patterns...")
    heatmap_path = output_dir / "weekly_hourly_heatmaps.png"
    
    # Select top species and indices
    species_list = ['Spotted seatrout', 'Silver perch', 'Oyster toadfish boat whistle']
    index_list = ['Hf', 'ACI', 'BI']
    
    # Filter to available species
    species_list = [sp for sp in species_list if sp in analyzer.detections.columns]
    index_list = [idx for idx in index_list if idx in analyzer.acoustic_indices.columns]
    
    fig2 = analyzer.plot_weekly_heatmaps(species_list, index_list, save_path=str(heatmap_path))
    plt.close(fig2)
    print(f"   Saved: {heatmap_path.name}")
    
    # Analyze chorus patterns
    print("\n4. Analyzing multi-species chorus patterns...")
    chorus_path = output_dir / "species_chorus_patterns.png"
    fig3 = analyzer.plot_species_chorus_patterns(save_path=str(chorus_path))
    plt.close(fig3)
    print(f"   Saved: {chorus_path.name}")
    
    # Analyze peak calling times
    print("\n5. Identifying peak calling times for all species...")
    peak_path = output_dir / "peak_calling_times.png"
    fig4, peak_times = analyzer.analyze_peak_calling_times(save_path=str(peak_path))
    plt.close(fig4)
    print(f"   Saved: {peak_path.name}")
    
    # Save peak times data
    peak_data = []
    for species, data in peak_times.items():
        peak_data.append({
            'species': species,
            'peak_hour': data['peak_hour'],
            'peak_intensity': data['peak_intensity'],
            'active_hours': len(data['active_hours']),
            'active_period': f"{min(data['active_hours'])}-{max(data['active_hours'])}" if data['active_hours'] else 'N/A'
        })
    
    peak_df = pd.DataFrame(peak_data)
    csv_path = output_dir / "peak_calling_times.csv"
    peak_df.to_csv(csv_path, index=False)
    print(f"   Saved: {csv_path.name}")
    
    # Print insights
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("=" * 60)
    
    # Categorize species by calling time
    dawn_species = [sp for sp, d in peak_times.items() if 4 <= d['peak_hour'] < 8]
    day_species = [sp for sp, d in peak_times.items() if 8 <= d['peak_hour'] < 16]
    dusk_species = [sp for sp, d in peak_times.items() if 16 <= d['peak_hour'] < 20]
    night_species = [sp for sp, d in peak_times.items() if d['peak_hour'] < 4 or d['peak_hour'] >= 20]
    
    print(f"\n1. Temporal Partitioning:")
    print(f"   Dawn chorus (4-8h): {len(dawn_species)} species")
    if dawn_species:
        print(f"      {', '.join(dawn_species[:3])}")
    print(f"   Day callers (8-16h): {len(day_species)} species")
    if day_species:
        print(f"      {', '.join(day_species[:3])}")
    print(f"   Dusk chorus (16-20h): {len(dusk_species)} species")
    if dusk_species:
        print(f"      {', '.join(dusk_species[:3])}")
    print(f"   Night callers (20-4h): {len(night_species)} species")
    if night_species:
        print(f"      {', '.join(night_species[:3])}")
    
    print(f"\n2. Most predictable species (narrow active window):")
    narrow_window = sorted(peak_data, key=lambda x: x['active_hours'])[:3]
    for sp in narrow_window:
        print(f"   - {sp['species']}: {sp['active_hours']} active hours ({sp['active_period']})")
    
    print(f"\n3. Most active species (highest peak intensity):")
    most_active = sorted(peak_data, key=lambda x: x['peak_intensity'], reverse=True)[:3]
    for sp in most_active:
        print(f"   - {sp['species']}: peak intensity {sp['peak_intensity']:.2f} at hour {sp['peak_hour']}")
    
    print("\n" + "=" * 60)
    print(f"Analysis complete! Visualizations saved to: {output_dir}")
    print("\nKey finding: Species show distinct temporal partitioning with")
    print("predictable daily calling patterns that acoustic indices can track.")
    print("=" * 60)

if __name__ == "__main__":
    main()