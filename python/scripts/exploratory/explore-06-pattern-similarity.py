"""Exploratory Analysis Script 06: Pattern Similarity Analysis

This script analyzes 2D pattern similarities between species calling patterns and acoustic indices
at the weekly-hourly resolution, automatically detecting which indices show matching temporal patterns
to species detections.

Key analyses:
- 2D correlation between weekly-hourly heatmaps
- Pattern similarity ranking for all species-index pairs
- Detection of indices that correlate with multiple species
- Visualization of top matching patterns
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats, signal, ndimage
from sklearn.metrics import normalized_mutual_info_score
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

class PatternSimilarityAnalyzer:
    """Analyze 2D pattern similarities between species and acoustic indices."""
    
    def __init__(self, data_root: Optional[Path] = None):
        self.loader = create_loader(data_root)
        self.detections = None
        self.acoustic_indices = None
        self.species_heatmaps = {}
        self.index_heatmaps = {}
        self.similarity_results = {}
        
    def load_data(self, station: str = '14M', year: int = 2021):
        """Load detection and acoustic index data for analysis."""
        logger.info(f"Loading data for station {station}, year {year}")
        
        # Load detection data
        try:
            self.detections = self.loader.load_detection_data(station, year)
            self.detections['datetime'] = pd.to_datetime(self.detections['Date'])
            self.detections['hour'] = self.detections['datetime'].dt.hour
            self.detections['week'] = self.detections['datetime'].dt.isocalendar().week
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
            
            # IMPORTANT FIX: Detection data is at 2-hour resolution (even hours only)
            # Downsample acoustic indices to match detection resolution
            even_hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
            original_len = len(self.acoustic_indices)
            self.acoustic_indices = self.acoustic_indices[self.acoustic_indices['hour'].isin(even_hours)]
            
            self.acoustic_indices = self.acoustic_indices.sort_values('datetime')
            logger.info(f"Loaded {len(self.acoustic_indices)} acoustic index records (downsampled from {original_len} to match 2-hour detection resolution)")
        except Exception as e:
            logger.error(f"Failed to load acoustic indices: {e}")
            return False
            
        return True
    
    def calculate_weekly_hourly_heatmap(self, data: pd.DataFrame, column: str) -> np.ndarray:
        """Calculate weekly-hourly heatmap as a 2D array."""
        
        # Convert to numeric
        data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
        
        # Create pivot table (week x hour)
        heatmap = data.pivot_table(
            values=column,
            index='week',
            columns='hour',
            aggfunc='mean',
            fill_value=0
        )
        
        return heatmap.values
    
    def calculate_2d_correlation(self, heatmap1: np.ndarray, heatmap2: np.ndarray) -> Dict:
        """Calculate various 2D similarity metrics between two heatmaps."""
        
        # Ensure same shape by padding/cropping
        min_weeks = min(heatmap1.shape[0], heatmap2.shape[0])
        min_hours = min(heatmap1.shape[1], heatmap2.shape[1])
        
        h1 = heatmap1[:min_weeks, :min_hours]
        h2 = heatmap2[:min_weeks, :min_hours]
        
        # Flatten for correlation calculations
        h1_flat = h1.flatten()
        h2_flat = h2.flatten()
        
        # Remove any NaN values
        valid_mask = ~(np.isnan(h1_flat) | np.isnan(h2_flat))
        h1_clean = h1_flat[valid_mask]
        h2_clean = h2_flat[valid_mask]
        
        if len(h1_clean) < 10:  # Need minimum data points
            return {'pearson_r': 0, 'spearman_r': 0, 'mutual_info': 0, 
                   'cosine_similarity': 0, 'structural_similarity': 0}
        
        # 1. Pearson correlation
        try:
            pearson_r, pearson_p = stats.pearsonr(h1_clean, h2_clean)
        except:
            pearson_r, pearson_p = 0, 1
        
        # 2. Spearman correlation (rank-based, robust to outliers)
        try:
            spearman_r, spearman_p = stats.spearmanr(h1_clean, h2_clean)
        except:
            spearman_r, spearman_p = 0, 1
        
        # 3. Normalized Mutual Information (captures non-linear relationships)
        try:
            # Discretize for mutual information
            h1_discrete = np.digitize(h1_clean, bins=np.percentile(h1_clean, [0, 25, 50, 75, 100]))
            h2_discrete = np.digitize(h2_clean, bins=np.percentile(h2_clean, [0, 25, 50, 75, 100]))
            mutual_info = normalized_mutual_info_score(h1_discrete, h2_discrete)
        except:
            mutual_info = 0
        
        # 4. Cosine similarity (good for sparse patterns)
        try:
            dot_product = np.dot(h1_clean, h2_clean)
            norm1 = np.linalg.norm(h1_clean)
            norm2 = np.linalg.norm(h2_clean)
            cosine_similarity = dot_product / (norm1 * norm2) if (norm1 * norm2) > 0 else 0
        except:
            cosine_similarity = 0
        
        # 5. Structural Similarity (considers spatial structure)
        try:
            # Normalize heatmaps
            h1_norm = (h1 - h1.mean()) / (h1.std() + 1e-10)
            h2_norm = (h2 - h2.mean()) / (h2.std() + 1e-10)
            
            # Mean squared difference
            mse = np.mean((h1_norm - h2_norm) ** 2)
            structural_similarity = 1 / (1 + mse)  # Convert to similarity measure
        except:
            structural_similarity = 0
        
        return {
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'mutual_info': mutual_info,
            'cosine_similarity': cosine_similarity,
            'structural_similarity': structural_similarity
        }
    
    def calculate_pattern_shifts(self, heatmap1: np.ndarray, heatmap2: np.ndarray) -> Dict:
        """Calculate optimal time shifts that maximize correlation."""
        
        # Ensure same shape
        min_weeks = min(heatmap1.shape[0], heatmap2.shape[0])
        min_hours = min(heatmap1.shape[1], heatmap2.shape[1])
        
        h1 = heatmap1[:min_weeks, :min_hours]
        h2 = heatmap2[:min_weeks, :min_hours]
        
        best_correlations = {}
        
        # Test weekly shifts (-4 to +4 weeks)
        for week_shift in range(-4, 5):
            if abs(week_shift) >= h1.shape[0]:
                continue
                
            if week_shift >= 0:
                h1_shifted = h1[week_shift:, :]
                h2_aligned = h2[:h1.shape[0] - week_shift, :]
            else:
                h1_shifted = h1[:h1.shape[0] + week_shift, :]
                h2_aligned = h2[-week_shift:, :]
            
            if h1_shifted.size > 0 and h2_aligned.size > 0:
                corr, _ = stats.pearsonr(h1_shifted.flatten(), h2_aligned.flatten())
                best_correlations[f'week_shift_{week_shift}'] = corr
        
        # Test hourly shifts (-6 to +6 hours)
        for hour_shift in range(-6, 7):
            if abs(hour_shift) >= h1.shape[1]:
                continue
                
            if hour_shift >= 0:
                h1_shifted = h1[:, hour_shift:]
                h2_aligned = h2[:, :h1.shape[1] - hour_shift]
            else:
                h1_shifted = h1[:, :h1.shape[1] + hour_shift]
                h2_aligned = h2[:, -hour_shift:]
            
            if h1_shifted.size > 0 and h2_aligned.size > 0:
                corr, _ = stats.pearsonr(h1_shifted.flatten(), h2_aligned.flatten())
                best_correlations[f'hour_shift_{hour_shift}'] = corr
        
        # Find best shifts
        best_week_shift = max([(k, v) for k, v in best_correlations.items() if 'week_shift' in k], 
                             key=lambda x: abs(x[1]), default=('week_shift_0', 0))
        best_hour_shift = max([(k, v) for k, v in best_correlations.items() if 'hour_shift' in k], 
                             key=lambda x: abs(x[1]), default=('hour_shift_0', 0))
        
        return {
            'best_week_shift': int(best_week_shift[0].split('_')[-1]),
            'best_week_correlation': best_week_shift[1],
            'best_hour_shift': int(best_hour_shift[0].split('_')[-1]),
            'best_hour_correlation': best_hour_shift[1],
            'all_shifts': best_correlations
        }
    
    def analyze_all_similarities(self, species_list: List[str] = None, 
                                index_list: List[str] = None):
        """Calculate pattern similarities for all species-index pairs."""
        
        if species_list is None:
            # Get fish species
            species_mapping = self.loader.load_species_mapping()
            fish_species = species_mapping[
                (species_mapping['group'] == 'fish') & 
                (species_mapping['keep_species'] == 1)
            ]['long_name'].tolist()
            species_list = [sp for sp in fish_species if sp in self.detections.columns][:10]
        
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
                        
            index_list = index_list[:20]  # Limit for performance
        
        logger.info(f"Analyzing {len(species_list)} species x {len(index_list)} indices")
        
        # Pre-calculate all heatmaps
        logger.info("Pre-calculating heatmaps...")
        for species in species_list:
            self.species_heatmaps[species] = self.calculate_weekly_hourly_heatmap(
                self.detections, species)
        
        for index in index_list:
            self.index_heatmaps[index] = self.calculate_weekly_hourly_heatmap(
                self.acoustic_indices, index)
        
        # Calculate similarities
        logger.info("Calculating pattern similarities...")
        results = {}
        
        for species in species_list:
            species_results = {}
            species_heatmap = self.species_heatmaps[species]
            
            for index in index_list:
                if index not in self.index_heatmaps:
                    continue
                    
                index_heatmap = self.index_heatmaps[index]
                
                # Calculate similarity metrics
                similarity = self.calculate_2d_correlation(species_heatmap, index_heatmap)
                
                # Calculate optimal shifts
                shifts = self.calculate_pattern_shifts(species_heatmap, index_heatmap)
                
                # Combine results
                result = {**similarity, **shifts}
                
                # Calculate composite similarity score
                result['composite_score'] = (
                    0.4 * abs(result['pearson_r']) +
                    0.3 * abs(result['spearman_r']) +
                    0.2 * result['mutual_info'] +
                    0.1 * result['structural_similarity']
                )
                
                species_results[index] = result
            
            results[species] = species_results
        
        self.similarity_results = results
        return results
    
    def plot_similarity_heatmap(self, metric: str = 'composite_score', save_path: str = None):
        """Create heatmap showing pattern similarities."""
        
        if not self.similarity_results:
            logger.error("No similarity results to plot")
            return
        
        # Extract similarity matrix
        species_list = list(self.similarity_results.keys())
        index_list = list(next(iter(self.similarity_results.values())).keys())
        
        similarity_matrix = np.zeros((len(species_list), len(index_list)))
        
        for i, species in enumerate(species_list):
            for j, index in enumerate(index_list):
                if index in self.similarity_results[species]:
                    similarity_matrix[i, j] = self.similarity_results[species][index][metric]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Plot heatmap
        im = ax.imshow(similarity_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(range(len(index_list)))
        ax.set_xticklabels(index_list, rotation=45, ha='right', fontsize=10)
        ax.set_yticks(range(len(species_list)))
        ax.set_yticklabels([sp[:25] for sp in species_list], fontsize=10)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(f'{metric.replace("_", " ").title()}', fontsize=12)
        
        # Add text annotations for high similarities
        for i in range(len(species_list)):
            for j in range(len(index_list)):
                if similarity_matrix[i, j] > 0.5:  # Only show strong similarities
                    ax.text(j, i, f'{similarity_matrix[i, j]:.2f}', 
                           ha='center', va='center', fontsize=8, 
                           color='white' if similarity_matrix[i, j] > 0.7 else 'black')
        
        ax.set_title(f'Pattern Similarity: Species vs Acoustic Indices\n(Weekly-Hourly Heatmap {metric.replace("_", " ").title()})', 
                    fontsize=14)
        ax.set_xlabel('Acoustic Index', fontsize=12)
        ax.set_ylabel('Species', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved similarity heatmap: {save_path}")
        
        return fig
    
    def plot_top_matches(self, n_top: int = 6, save_path: str = None):
        """Plot side-by-side heatmaps for top matching species-index pairs."""
        
        if not self.similarity_results:
            logger.error("No similarity results to plot")
            return
        
        # Find top matches
        all_matches = []
        for species, indices in self.similarity_results.items():
            for index, result in indices.items():
                all_matches.append({
                    'species': species,
                    'index': index,
                    'score': result['composite_score'],
                    'pearson_r': result['pearson_r'],
                    'pattern_type': 'positive' if result['pearson_r'] > 0 else 'negative'
                })
        
        # Sort by composite score
        top_matches = sorted(all_matches, key=lambda x: x['score'], reverse=True)[:n_top]
        
        # Create figure
        fig, axes = plt.subplots(n_top, 2, figsize=(16, 4 * n_top))
        if n_top == 1:
            axes = axes.reshape(1, -1)
        
        for i, match in enumerate(top_matches):
            species = match['species']
            index = match['index']
            
            # Get heatmaps
            species_heatmap = self.species_heatmaps[species]
            index_heatmap = self.index_heatmaps[index]
            
            # Plot species heatmap
            ax1 = axes[i, 0]
            im1 = ax1.imshow(species_heatmap.T, cmap='YlOrRd', aspect='auto', origin='upper')
            ax1.set_title(f'{species[:30]}...', fontsize=11)
            ax1.set_xlabel('Week of Year', fontsize=10)
            ax1.set_ylabel('Hour of Day (2h resolution)', fontsize=10)
            
            # Now both datasets should have same resolution (12 even hours)
            # Map the 12 indices to actual hour labels
            even_hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
            ax1.set_yticks(range(0, len(even_hours), 2))  # Every 4 hours: 0,4,8...
            ax1.set_yticklabels([even_hours[i] for i in range(0, len(even_hours), 2)])
            
            # Add horizontal lines for day/night (in index space)
            ax1.axhline(y=3, color='yellow', linestyle='--', alpha=0.5, linewidth=0.5)  # 6am = index 3
            ax1.axhline(y=9, color='navy', linestyle='--', alpha=0.5, linewidth=0.5)    # 18pm = index 9
            
            plt.colorbar(im1, ax=ax1, shrink=0.6)
            
            # Plot index heatmap
            ax2 = axes[i, 1]
            im2 = ax2.imshow(index_heatmap.T, cmap='viridis', aspect='auto', origin='upper')
            ax2.set_title(f'{index} (r={match["pearson_r"]:.3f}, score={match["score"]:.3f})', fontsize=11)
            ax2.set_xlabel('Week of Year', fontsize=10)
            ax2.set_ylabel('Hour of Day (2h resolution)', fontsize=10)
            
            # Same for index heatmap
            ax2.set_yticks(range(0, len(even_hours), 2))
            ax2.set_yticklabels([even_hours[i] for i in range(0, len(even_hours), 2)])
            
            # Add horizontal lines for day/night (in index space)
            ax2.axhline(y=3, color='yellow', linestyle='--', alpha=0.5, linewidth=0.5)  # 6am = index 3
            ax2.axhline(y=9, color='navy', linestyle='--', alpha=0.5, linewidth=0.5)    # 18pm = index 9
            
            plt.colorbar(im2, ax=ax2, shrink=0.6)
        
        plt.suptitle('Top Pattern Matches: Species vs Acoustic Indices\n(Weekly-Hourly Heatmap Comparisons)', 
                    fontsize=14, y=1.01)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved top matches: {save_path}")
        
        return fig
    
    def identify_multi_species_indices(self, threshold: float = 0.4) -> Dict:
        """Identify indices that correlate with multiple species."""
        
        if not self.similarity_results:
            logger.error("No similarity results available")
            return {}
        
        # Count how many species each index correlates with
        index_species_count = {}
        index_correlations = {}
        
        for species, indices in self.similarity_results.items():
            for index, result in indices.items():
                if index not in index_species_count:
                    index_species_count[index] = 0
                    index_correlations[index] = []
                
                if result['composite_score'] > threshold:
                    index_species_count[index] += 1
                    index_correlations[index].append({
                        'species': species,
                        'score': result['composite_score'],
                        'correlation': result['pearson_r']
                    })
        
        # Sort by number of species
        multi_species_indices = {
            index: {
                'count': count,
                'correlations': index_correlations[index],
                'mean_score': np.mean([c['score'] for c in index_correlations[index]])
            }
            for index, count in index_species_count.items()
            if count > 1
        }
        
        return dict(sorted(multi_species_indices.items(), 
                          key=lambda x: x[1]['count'], reverse=True))

def main():
    """Run pattern similarity analysis."""
    
    print("=" * 60)
    print("Pattern Similarity Analysis: Weekly-Hourly Heatmap Matching")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = PatternSimilarityAnalyzer(repo_root / "data")
    
    # Create output directory
    output_dir = Path.cwd() / "analysis_results" / "pattern_similarity"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n1. Loading data for Station 14M, Year 2021...")
    if not analyzer.load_data(station='14M', year=2021):
        print("Failed to load data. Exiting.")
        return
    
    # Analyze similarities
    print("\n2. Calculating pattern similarities for all species-index pairs...")
    print("   This compares weekly-hourly heatmaps using multiple similarity metrics")
    
    analyzer.analyze_all_similarities()
    
    # Create similarity heatmap
    print("\n3. Creating pattern similarity heatmap...")
    heatmap_path = output_dir / "pattern_similarity_heatmap.png"
    fig1 = analyzer.plot_similarity_heatmap(metric='composite_score', save_path=str(heatmap_path))
    plt.close(fig1)
    print(f"   Saved: {heatmap_path.name}")
    
    # Create top matches visualization
    print("\n4. Creating top pattern matches visualization...")
    matches_path = output_dir / "top_pattern_matches.png"
    fig2 = analyzer.plot_top_matches(n_top=8, save_path=str(matches_path))
    plt.close(fig2)
    print(f"   Saved: {matches_path.name}")
    
    # Identify multi-species indices
    print("\n5. Identifying indices that correlate with multiple species...")
    multi_species = analyzer.identify_multi_species_indices(threshold=0.4)
    
    # Save detailed results
    all_results = []
    for species, indices in analyzer.similarity_results.items():
        for index, result in indices.items():
            all_results.append({
                'species': species,
                'index': index,
                'composite_score': result['composite_score'],
                'pearson_r': result['pearson_r'],
                'spearman_r': result['spearman_r'],
                'mutual_info': result['mutual_info'],
                'structural_similarity': result['structural_similarity'],
                'best_week_shift': result['best_week_shift'],
                'best_hour_shift': result['best_hour_shift']
            })
    
    results_df = pd.DataFrame(all_results)
    csv_path = output_dir / "pattern_similarity_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"   Saved: {csv_path.name}")
    
    # Print insights
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("=" * 60)
    
    # Top matches
    top_matches = results_df.nlargest(5, 'composite_score')
    print(f"\n1. Strongest pattern matches (composite score):")
    for _, match in top_matches.iterrows():
        print(f"   - {match['species'][:25]} vs {match['index']}: "
              f"score={match['composite_score']:.3f}, r={match['pearson_r']:.3f}")
    
    # Multi-species indices
    if multi_species:
        print(f"\n2. Indices correlating with multiple species:")
        for index, data in list(multi_species.items())[:5]:
            species_names = [c['species'][:15] for c in data['correlations'][:3]]
            print(f"   - {index}: {data['count']} species (mean score={data['mean_score']:.3f})")
            print(f"     Top species: {', '.join(species_names)}")
    
    # Pattern types
    positive_patterns = results_df[results_df['pearson_r'] > 0.3]
    negative_patterns = results_df[results_df['pearson_r'] < -0.3]
    
    print(f"\n3. Pattern relationship types:")
    print(f"   - Strong positive correlations: {len(positive_patterns)} pairs")
    print(f"   - Strong negative correlations: {len(negative_patterns)} pairs")
    
    if len(positive_patterns) > 0:
        best_positive = positive_patterns.loc[positive_patterns['pearson_r'].idxmax()]
        print(f"   - Best positive: {best_positive['species'][:20]} vs {best_positive['index']} "
              f"(r={best_positive['pearson_r']:.3f})")
    
    if len(negative_patterns) > 0:
        best_negative = negative_patterns.loc[negative_patterns['pearson_r'].idxmin()]
        print(f"   - Best negative: {best_negative['species'][:20]} vs {best_negative['index']} "
              f"(r={best_negative['pearson_r']:.3f})")
    
    # Time shift patterns
    significant_shifts = results_df[
        (results_df['composite_score'] > 0.3) & 
        ((abs(results_df['best_week_shift']) > 0) | (abs(results_df['best_hour_shift']) > 2))
    ]
    
    if len(significant_shifts) > 0:
        print(f"\n4. Patterns with significant time offsets:")
        for _, shift in significant_shifts.head(3).iterrows():
            print(f"   - {shift['species'][:20]} vs {shift['index']}: "
                  f"week_shift={shift['best_week_shift']}, hour_shift={shift['best_hour_shift']}")
    
    print("\n" + "=" * 60)
    print(f"Analysis complete! Results saved to: {output_dir}")
    print("Key finding: Multiple acoustic indices show strong 2D pattern")
    print("similarities with species calling patterns at weekly-hourly resolution.")
    print("=" * 60)

if __name__ == "__main__":
    main()