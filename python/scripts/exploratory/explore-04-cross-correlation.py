"""Exploratory Analysis Script 04: Cross-Correlation Analysis

This script performs cross-correlation analysis between manual species detections 
and acoustic indices to identify which indices are most predictive of species presence.

Key analyses:
- Cross-correlation at multiple time lags
- Correlation strength heatmaps across all species and indices
- Lead/lag relationship identification
- Index ranking by predictive power for each species
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal, stats
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
plt.rcParams['figure.figsize'] = (14, 10)

class CrossCorrelationAnalyzer:
    """Analyze cross-correlations between species detections and acoustic indices."""
    
    def __init__(self, data_root: Optional[Path] = None):
        self.loader = create_loader(data_root)
        self.detections = None
        self.acoustic_indices = None
        self.correlation_results = {}
        
    def load_data(self, station: str = '14M', year: int = 2021):
        """Load detection and acoustic index data for analysis."""
        logger.info(f"Loading data for station {station}, year {year}")
        
        # Load detection data
        try:
            self.detections = self.loader.load_detection_data(station, year)
            self.detections['datetime'] = pd.to_datetime(self.detections['Date'])
            self.detections = self.detections.sort_values('datetime')
            logger.info(f"Loaded {len(self.detections)} detection records")
        except Exception as e:
            logger.error(f"Failed to load detection data: {e}")
            return False
            
        # Load acoustic indices
        try:
            self.acoustic_indices = self.loader.load_acoustic_indices(station, 'FullBW')
            self.acoustic_indices['datetime'] = pd.to_datetime(self.acoustic_indices['Date'])
            self.acoustic_indices = self.acoustic_indices.sort_values('datetime')
            logger.info(f"Loaded {len(self.acoustic_indices)} acoustic index records")
        except Exception as e:
            logger.error(f"Failed to load acoustic indices: {e}")
            return False
            
        return True
    
    def align_timeseries(self, detection_series: pd.Series, index_series: pd.Series,
                        resolution: str = '2H') -> Tuple[np.ndarray, np.ndarray]:
        """Align detection and index time series to same temporal resolution."""
        
        # Create common time index
        start_time = max(detection_series.index.min(), index_series.index.min())
        end_time = min(detection_series.index.max(), index_series.index.max())
        
        # Resample to common resolution
        common_index = pd.date_range(start=start_time, end=end_time, freq=resolution)
        
        # Resample detection data (take max in each bin)
        det_resampled = detection_series.resample(resolution).max().fillna(0)
        det_aligned = det_resampled.reindex(common_index, fill_value=0)
        
        # Resample index data (take mean in each bin)
        idx_resampled = index_series.resample(resolution).mean()
        idx_aligned = idx_resampled.reindex(common_index, method='nearest')
        
        # Fill any remaining NaNs
        idx_aligned = idx_aligned.fillna(idx_aligned.mean())
        
        return det_aligned.values, idx_aligned.values
    
    def calculate_cross_correlation(self, detection_series: np.ndarray, 
                                   index_series: np.ndarray,
                                   max_lag: int = 24) -> Dict:
        """Calculate cross-correlation between detection and index series.
        
        Args:
            detection_series: Species detection intensity values
            index_series: Acoustic index values
            max_lag: Maximum lag to consider (in units of time resolution)
        
        Returns:
            Dictionary with correlation values, lags, and peak correlation info
        """
        
        # Normalize series (z-score)
        det_norm = (detection_series - np.mean(detection_series)) / (np.std(detection_series) + 1e-10)
        idx_norm = (index_series - np.mean(index_series)) / (np.std(index_series) + 1e-10)
        
        # Calculate cross-correlation
        correlation = signal.correlate(det_norm, idx_norm, mode='same', method='auto')
        lags = signal.correlation_lags(len(det_norm), len(idx_norm), mode='same')
        
        # Normalize correlation by length
        correlation = correlation / len(det_norm)
        
        # Find peak correlation within max_lag window
        lag_mask = np.abs(lags) <= max_lag
        correlation_windowed = correlation[lag_mask]
        lags_windowed = lags[lag_mask]
        
        if len(correlation_windowed) > 0:
            peak_idx = np.argmax(np.abs(correlation_windowed))
            peak_correlation = correlation_windowed[peak_idx]
            peak_lag = lags_windowed[peak_idx]
        else:
            peak_correlation = 0
            peak_lag = 0
        
        # Calculate Pearson correlation at zero lag for comparison
        if len(detection_series) == len(index_series):
            pearson_r, pearson_p = stats.pearsonr(detection_series, index_series)
        else:
            pearson_r, pearson_p = 0, 1
        
        return {
            'correlation': correlation[lag_mask],
            'lags': lags_windowed,
            'peak_correlation': peak_correlation,
            'peak_lag': peak_lag,
            'pearson_r': pearson_r,
            'pearson_p': pearson_p
        }
    
    def analyze_all_correlations(self, species_list: List[str] = None,
                                index_list: List[str] = None,
                                resolution: str = '2H',
                                max_lag: int = 24):
        """Calculate cross-correlations for all species-index pairs."""
        
        if self.detections is None or self.acoustic_indices is None:
            logger.error("Data not loaded")
            return
        
        # Get species list
        if species_list is None:
            # Get fish species from mapping
            species_mapping = self.loader.load_species_mapping()
            fish_species = species_mapping[
                (species_mapping['group'] == 'fish') & 
                (species_mapping['keep_species'] == 1)
            ]['long_name'].tolist()
            
            # Filter to species present in data
            species_list = [sp for sp in fish_species if sp in self.detections.columns]
            species_list = species_list[:10]  # Limit to top 10 for visualization
        
        # Get index list
        if index_list is None:
            # Select key indices from different categories
            index_categories = {
                'Temporal': ['MEANt', 'VARt', 'SKEWt', 'KURTt'],
                'Frequency': ['MEANf', 'VARf', 'SKEWf', 'KURTf'],
                'Complexity': ['ACI', 'NDSI', 'ADI', 'AEI'],
                'Diversity': ['H', 'Ht', 'Hf'],
                'Bioacoustic': ['BI', 'rBA'],
                'Energy': ['BioEnergy', 'AnthroEnergy']
            }
            
            index_list = []
            for category, indices in index_categories.items():
                for idx in indices:
                    if idx in self.acoustic_indices.columns:
                        index_list.append(idx)
        
        logger.info(f"Analyzing {len(species_list)} species x {len(index_list)} indices")
        
        # Prepare time-indexed data
        det_indexed = self.detections.set_index('datetime')
        idx_indexed = self.acoustic_indices.set_index('datetime')
        
        # Calculate correlations
        results = {}
        for species in species_list:
            logger.info(f"Processing species: {species}")
            species_results = {}
            
            # Convert species data to numeric
            species_data = pd.to_numeric(det_indexed[species], errors='coerce').fillna(0)
            
            for index in index_list:
                if index not in idx_indexed.columns:
                    continue
                    
                # Align time series
                det_aligned, idx_aligned = self.align_timeseries(
                    species_data, idx_indexed[index], resolution
                )
                
                # Calculate cross-correlation
                corr_result = self.calculate_cross_correlation(
                    det_aligned, idx_aligned, max_lag
                )
                
                species_results[index] = corr_result
            
            results[species] = species_results
        
        self.correlation_results = results
        return results
    
    def plot_correlation_heatmap(self, save_path: str = None):
        """Create heatmap showing peak correlations for all species-index pairs."""
        
        if not self.correlation_results:
            logger.error("No correlation results to plot")
            return
        
        # Extract peak correlations into matrix
        species_list = list(self.correlation_results.keys())
        index_list = list(next(iter(self.correlation_results.values())).keys())
        
        # Create correlation matrix
        corr_matrix = np.zeros((len(species_list), len(index_list)))
        lag_matrix = np.zeros((len(species_list), len(index_list)))
        
        for i, species in enumerate(species_list):
            for j, index in enumerate(index_list):
                if index in self.correlation_results[species]:
                    corr_matrix[i, j] = self.correlation_results[species][index]['peak_correlation']
                    lag_matrix[i, j] = self.correlation_results[species][index]['peak_lag']
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
        
        # Plot correlation strength
        sns.heatmap(corr_matrix, 
                   xticklabels=index_list,
                   yticklabels=species_list,
                   cmap='RdBu_r',
                   center=0,
                   vmin=-0.5,
                   vmax=0.5,
                   annot=True,
                   fmt='.2f',
                   ax=ax1,
                   cbar_kws={'label': 'Peak Correlation'})
        ax1.set_title('Peak Cross-Correlation: Species vs Acoustic Indices', fontsize=14)
        ax1.set_xlabel('Acoustic Index', fontsize=12)
        ax1.set_ylabel('Species', fontsize=12)
        
        # Plot optimal lag
        sns.heatmap(lag_matrix,
                   xticklabels=index_list,
                   yticklabels=species_list,
                   cmap='coolwarm',
                   center=0,
                   vmin=-12,
                   vmax=12,
                   annot=True,
                   fmt='.0f',
                   ax=ax2,
                   cbar_kws={'label': 'Optimal Lag (2-hour units)'})
        ax2.set_title('Optimal Time Lag (Positive = Index Leads)', fontsize=14)
        ax2.set_xlabel('Acoustic Index', fontsize=12)
        ax2.set_ylabel('Species', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved heatmap: {save_path}")
        
        return fig
    
    def plot_top_correlations_timeseries(self, n_top: int = 6, save_path: str = None):
        """Plot time series comparisons for top correlated species-index pairs."""
        
        if not self.correlation_results:
            logger.error("No correlation results to plot")
            return
        
        # Find top correlations
        top_pairs = []
        for species, indices in self.correlation_results.items():
            for index, result in indices.items():
                top_pairs.append({
                    'species': species,
                    'index': index,
                    'correlation': abs(result['peak_correlation']),
                    'lag': result['peak_lag'],
                    'sign': np.sign(result['peak_correlation'])
                })
        
        top_pairs = sorted(top_pairs, key=lambda x: x['correlation'], reverse=True)[:n_top]
        
        # Create figure
        fig, axes = plt.subplots(n_top, 1, figsize=(16, 3*n_top))
        if n_top == 1:
            axes = [axes]
        
        # Prepare time-indexed data
        det_indexed = self.detections.set_index('datetime')
        idx_indexed = self.acoustic_indices.set_index('datetime')
        
        for i, pair in enumerate(top_pairs):
            ax = axes[i]
            
            # Get aligned data
            species_data = pd.to_numeric(det_indexed[pair['species']], errors='coerce').fillna(0)
            det_aligned, idx_aligned = self.align_timeseries(
                species_data, idx_indexed[pair['index']], '2H'
            )
            
            # Create time axis
            time_axis = pd.date_range(
                start=det_indexed.index.min(),
                periods=len(det_aligned),
                freq='2H'
            )
            
            # Plot on dual axes
            ax2 = ax.twinx()
            
            # Plot detection data
            line1 = ax.plot(time_axis, det_aligned, 'b-', alpha=0.7, 
                          label=f"{pair['species'][:20]}...")
            ax.fill_between(time_axis, 0, det_aligned, alpha=0.3, color='blue')
            ax.set_ylabel('Detection Intensity', color='blue', fontsize=10)
            ax.tick_params(axis='y', labelcolor='blue')
            
            # Plot index data (potentially shifted by optimal lag)
            if pair['lag'] != 0:
                # Shift index by optimal lag
                idx_shifted = np.roll(idx_aligned, -pair['lag'])
                label = f"{pair['index']} (shifted {-pair['lag']*2}h)"
            else:
                idx_shifted = idx_aligned
                label = pair['index']
            
            line2 = ax2.plot(time_axis, idx_shifted, 'r-', alpha=0.7, label=label)
            ax2.set_ylabel(f'{pair["index"]} Value', color='red', fontsize=10)
            ax2.tick_params(axis='y', labelcolor='red')
            
            # Add correlation info to title
            corr_sign = '+' if pair['sign'] > 0 else '-'
            ax.set_title(f'Rank {i+1}: {pair["species"][:30]} vs {pair["index"]} | '
                        f'Correlation: {corr_sign}{pair["correlation"]:.3f} | '
                        f'Lag: {pair["lag"]*2}h',
                        fontsize=11)
            
            # Add legend
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc='upper right', fontsize=9)
            
            ax.grid(True, alpha=0.3)
            ax.set_xlim(time_axis[0], time_axis[-1])
        
        axes[-1].set_xlabel('Date', fontsize=12)
        
        plt.suptitle('Top Cross-Correlations: Species Detection vs Acoustic Indices', 
                    fontsize=14, y=1.01)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved time series comparison: {save_path}")
        
        return fig
    
    def plot_lag_analysis(self, species: str, index: str, save_path: str = None):
        """Plot detailed lag analysis for a specific species-index pair."""
        
        if species not in self.correlation_results or index not in self.correlation_results[species]:
            logger.error(f"No results for {species} - {index}")
            return
        
        result = self.correlation_results[species][index]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Panel 1: Cross-correlation function
        ax1 = axes[0, 0]
        ax1.plot(result['lags'] * 2, result['correlation'], 'b-', linewidth=2)
        ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax1.axvline(x=result['peak_lag'] * 2, color='r', linestyle='--', alpha=0.5,
                   label=f'Peak at {result["peak_lag"]*2}h')
        ax1.fill_between(result['lags'] * 2, 0, result['correlation'], alpha=0.3)
        ax1.set_xlabel('Lag (hours)', fontsize=11)
        ax1.set_ylabel('Cross-correlation', fontsize=11)
        ax1.set_title(f'Cross-correlation Function: {species} vs {index}', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Time series at optimal lag
        ax2 = axes[0, 1]
        
        # Get aligned data
        det_indexed = self.detections.set_index('datetime')
        idx_indexed = self.acoustic_indices.set_index('datetime')
        species_data = pd.to_numeric(det_indexed[species], errors='coerce').fillna(0)
        det_aligned, idx_aligned = self.align_timeseries(
            species_data, idx_indexed[index], '2H'
        )
        
        # Normalize for comparison
        det_norm = (det_aligned - np.mean(det_aligned)) / (np.std(det_aligned) + 1e-10)
        idx_norm = (idx_aligned - np.mean(idx_aligned)) / (np.std(idx_aligned) + 1e-10)
        
        # Apply optimal shift
        idx_shifted = np.roll(idx_norm, -result['peak_lag'])
        
        # Plot subset for clarity
        subset = min(168, len(det_norm))  # Show 2 weeks
        x_axis = np.arange(subset) * 2  # Convert to hours
        
        ax2.plot(x_axis, det_norm[:subset], 'b-', alpha=0.7, label='Detection (normalized)')
        ax2.plot(x_axis, idx_shifted[:subset], 'r-', alpha=0.7, 
                label=f'{index} (shifted {-result["peak_lag"]*2}h)')
        ax2.set_xlabel('Hours', fontsize=11)
        ax2.set_ylabel('Normalized Value', fontsize=11)
        ax2.set_title('Aligned Time Series (2-week sample)', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Panel 3: Scatter plot at optimal lag
        ax3 = axes[1, 0]
        idx_shifted_full = np.roll(idx_aligned, -result['peak_lag'])
        ax3.scatter(idx_shifted_full, det_aligned, alpha=0.5, s=20)
        
        # Add regression line
        z = np.polyfit(idx_shifted_full, det_aligned, 1)
        p = np.poly1d(z)
        x_line = np.linspace(idx_shifted_full.min(), idx_shifted_full.max(), 100)
        ax3.plot(x_line, p(x_line), "r--", alpha=0.8, 
                label=f'R={result["peak_correlation"]:.3f}')
        
        ax3.set_xlabel(f'{index} Value (shifted)', fontsize=11)
        ax3.set_ylabel('Detection Intensity', fontsize=11)
        ax3.set_title('Scatter Plot at Optimal Lag', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: Lag sensitivity
        ax4 = axes[1, 1]
        
        # Calculate correlation at different lags
        lag_range = range(-24, 25, 2)
        correlations = []
        
        for lag in lag_range:
            idx_test = np.roll(idx_aligned, -lag)
            corr, _ = stats.pearsonr(det_aligned, idx_test)
            correlations.append(corr)
        
        ax4.plot([l*2 for l in lag_range], correlations, 'g-', linewidth=2)
        ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax4.axvline(x=result['peak_lag']*2, color='r', linestyle='--', alpha=0.5)
        ax4.fill_between([l*2 for l in lag_range], 0, correlations, alpha=0.3, color='green')
        ax4.set_xlabel('Lag (hours)', fontsize=11)
        ax4.set_ylabel('Pearson Correlation', fontsize=11)
        ax4.set_title('Lag Sensitivity Analysis', fontsize=12)
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'Detailed Lag Analysis: {species} vs {index}', fontsize=14, y=1.02)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved lag analysis: {save_path}")
        
        return fig
    
    def rank_indices_by_species(self, save_path: str = None):
        """Create ranking of best indices for each species."""
        
        if not self.correlation_results:
            logger.error("No correlation results to rank")
            return
        
        rankings = {}
        for species, indices in self.correlation_results.items():
            # Sort indices by absolute correlation
            sorted_indices = sorted(
                indices.items(),
                key=lambda x: abs(x[1]['peak_correlation']),
                reverse=True
            )
            
            rankings[species] = [
                {
                    'index': idx,
                    'correlation': result['peak_correlation'],
                    'lag': result['peak_lag'],
                    'p_value': result['pearson_p']
                }
                for idx, result in sorted_indices[:5]  # Top 5
            ]
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Prepare data for heatmap
        species_list = list(rankings.keys())
        n_species = len(species_list)
        
        # Create text annotations
        cell_text = []
        colors = []
        
        for species in species_list:
            row_text = []
            row_colors = []
            for rank in range(5):
                if rank < len(rankings[species]):
                    item = rankings[species][rank]
                    text = f"{item['index']}\n{item['correlation']:.2f}"
                    row_text.append(text)
                    
                    # Color based on correlation strength
                    corr_abs = abs(item['correlation'])
                    if corr_abs > 0.4:
                        color = 'darkgreen'
                    elif corr_abs > 0.3:
                        color = 'green'
                    elif corr_abs > 0.2:
                        color = 'yellow'
                    else:
                        color = 'lightgray'
                    row_colors.append(color)
                else:
                    row_text.append('')
                    row_colors.append('white')
            
            cell_text.append(row_text)
            colors.append(row_colors)
        
        # Create table
        table = ax.table(cellText=cell_text,
                        cellColours=colors,
                        rowLabels=species_list,
                        colLabels=['Rank 1', 'Rank 2', 'Rank 3', 'Rank 4', 'Rank 5'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.15] * 5)
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 2)
        
        # Style the table headers
        for i in range(n_species + 1):
            for j in range(-1, 5):  # -1 for row labels, 0-4 for columns
                try:
                    cell = table[(i, j)]
                    if i == 0 or j == -1:  # Header row or row labels
                        cell.set_facecolor('#40466e')
                        cell.set_text_props(weight='bold', color='white')
                except KeyError:
                    continue
        
        ax.axis('off')
        ax.set_title('Top 5 Acoustic Indices by Species (Ranked by Correlation Strength)', 
                    fontsize=14, pad=20)
        
        # Add color legend
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, fc='darkgreen', label='|r| > 0.4'),
            plt.Rectangle((0, 0), 1, 1, fc='green', label='0.3 < |r| ≤ 0.4'),
            plt.Rectangle((0, 0), 1, 1, fc='yellow', label='0.2 < |r| ≤ 0.3'),
            plt.Rectangle((0, 0), 1, 1, fc='lightgray', label='|r| ≤ 0.2')
        ]
        ax.legend(handles=legend_elements, loc='upper right', title='Correlation Strength')
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved rankings: {save_path}")
        
        return fig, rankings

def main():
    """Run cross-correlation analysis."""
    
    print("=" * 60)
    print("Cross-Correlation Analysis: Species vs Acoustic Indices")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = CrossCorrelationAnalyzer(repo_root / "data")
    
    # Create output directory
    output_dir = Path.cwd() / "analysis_results" / "cross_correlation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data for station 14M, 2021 (best data coverage)
    print("\n1. Loading data for Station 14M, Year 2021...")
    if not analyzer.load_data(station='14M', year=2021):
        print("Failed to load data. Exiting.")
        return
    
    # Perform cross-correlation analysis
    print("\n2. Calculating cross-correlations...")
    print("   This analyzes all species-index pairs with various time lags")
    analyzer.analyze_all_correlations(
        species_list=None,  # Will auto-select top fish species
        index_list=None,     # Will auto-select key indices
        resolution='2H',     # Match detection data resolution
        max_lag=24          # Check up to 48 hours lag
    )
    
    # Generate correlation heatmap
    print("\n3. Creating correlation heatmap...")
    heatmap_path = output_dir / "correlation_heatmap.png"
    fig1 = analyzer.plot_correlation_heatmap(save_path=str(heatmap_path))
    plt.close(fig1)
    print(f"   Saved: {heatmap_path.name}")
    
    # Generate time series comparison for top correlations
    print("\n4. Creating time series comparisons for top correlations...")
    timeseries_path = output_dir / "top_correlations_timeseries.png"
    fig2 = analyzer.plot_top_correlations_timeseries(n_top=6, save_path=str(timeseries_path))
    plt.close(fig2)
    print(f"   Saved: {timeseries_path.name}")
    
    # Generate detailed lag analysis for best correlation
    print("\n5. Creating detailed lag analysis for strongest correlation...")
    
    # Find the strongest correlation
    best_pair = None
    best_corr = 0
    for species, indices in analyzer.correlation_results.items():
        for index, result in indices.items():
            if abs(result['peak_correlation']) > best_corr:
                best_corr = abs(result['peak_correlation'])
                best_pair = (species, index)
    
    if best_pair:
        lag_path = output_dir / f"lag_analysis_{best_pair[0].replace(' ', '_')}_{best_pair[1]}.png"
        fig3 = analyzer.plot_lag_analysis(best_pair[0], best_pair[1], save_path=str(lag_path))
        plt.close(fig3)
        print(f"   Saved: {lag_path.name}")
        print(f"   Best correlation: {best_pair[0]} vs {best_pair[1]} (r={best_corr:.3f})")
    
    # Generate index rankings by species
    print("\n6. Creating index rankings by species...")
    rankings_path = output_dir / "index_rankings_by_species.png"
    fig4, rankings = analyzer.rank_indices_by_species(save_path=str(rankings_path))
    plt.close(fig4)
    print(f"   Saved: {rankings_path.name}")
    
    # Save rankings as CSV for further analysis
    rankings_data = []
    for species, indices in rankings.items():
        for rank, item in enumerate(indices, 1):
            rankings_data.append({
                'species': species,
                'rank': rank,
                'index': item['index'],
                'correlation': item['correlation'],
                'lag_hours': item['lag'] * 2,
                'p_value': item['p_value']
            })
    
    rankings_df = pd.DataFrame(rankings_data)
    csv_path = output_dir / "correlation_rankings.csv"
    rankings_df.to_csv(csv_path, index=False)
    print(f"   Saved: {csv_path.name}")
    
    # Print key insights
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("=" * 60)
    
    # Find universally good indices
    all_indices = {}
    for species, indices in analyzer.correlation_results.items():
        for index, result in indices.items():
            if index not in all_indices:
                all_indices[index] = []
            all_indices[index].append(abs(result['peak_correlation']))
    
    # Calculate mean correlation per index
    mean_correlations = {idx: np.mean(corrs) for idx, corrs in all_indices.items()}
    best_indices = sorted(mean_correlations.items(), key=lambda x: x[1], reverse=True)[:3]
    
    print(f"\n1. Most universally predictive indices:")
    for idx, corr in best_indices:
        print(f"   - {idx}: mean |r| = {corr:.3f}")
    
    print(f"\n2. Species with strongest acoustic predictors:")
    species_max_corr = {}
    for species, indices in analyzer.correlation_results.items():
        max_corr = max([abs(r['peak_correlation']) for r in indices.values()])
        species_max_corr[species] = max_corr
    
    top_species = sorted(species_max_corr.items(), key=lambda x: x[1], reverse=True)[:3]
    for species, corr in top_species:
        print(f"   - {species}: max |r| = {corr:.3f}")
    
    print(f"\n3. Typical lag patterns:")
    all_lags = []
    for species, indices in analyzer.correlation_results.items():
        for index, result in indices.items():
            if abs(result['peak_correlation']) > 0.2:  # Only significant correlations
                all_lags.append(result['peak_lag'] * 2)  # Convert to hours
    
    if all_lags:
        print(f"   - Mean optimal lag: {np.mean(all_lags):.1f} hours")
        print(f"   - Most common lag: {stats.mode(all_lags).mode[0] if hasattr(stats.mode(all_lags), 'mode') else stats.mode(all_lags)[0][0]:.0f} hours")
    
    print("\n" + "=" * 60)
    print(f"Analysis complete! Visualizations saved to: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()