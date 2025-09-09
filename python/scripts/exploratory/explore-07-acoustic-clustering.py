"""Exploratory Analysis Script 07: Acoustic Clustering for Ecosystem Monitoring

This script uses clustering and dimensionality reduction on acoustic indices to identify
distinct acoustic "states" or "regimes" that could serve as ecosystem monitoring markers.

Key analyses:
- PCA + clustering to identify acoustic regimes
- Temporal clustering patterns (hourly, daily, weekly, seasonal)
- Anomaly detection for unusual acoustic events
- Validation against biological activity patterns
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy import stats
try:
    import umap.umap_ as umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
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

class AcousticClusteringAnalyzer:
    """Analyze acoustic clustering patterns for ecosystem monitoring."""
    
    def __init__(self, data_root: Optional[Path] = None):
        self.loader = create_loader(data_root)
        self.acoustic_indices = None
        self.detections = None
        self.clustering_results = {}
        self.pca_results = {}
        
    def load_data(self, station: str = '14M', year: int = 2021):
        """Load acoustic indices and detection data."""
        logger.info(f"Loading data for station {station}, year {year}")
        
        # Load acoustic indices (full resolution for clustering)
        try:
            self.acoustic_indices = self.loader.load_acoustic_indices(station, 'FullBW')
            self.acoustic_indices['datetime'] = pd.to_datetime(self.acoustic_indices['Date'])
            self.acoustic_indices['hour'] = self.acoustic_indices['datetime'].dt.hour
            self.acoustic_indices['day'] = self.acoustic_indices['datetime'].dt.dayofyear
            self.acoustic_indices['week'] = self.acoustic_indices['datetime'].dt.isocalendar().week
            self.acoustic_indices['month'] = self.acoustic_indices['datetime'].dt.month
            self.acoustic_indices = self.acoustic_indices.sort_values('datetime')
            logger.info(f"Loaded {len(self.acoustic_indices)} acoustic index records")
        except Exception as e:
            logger.error(f"Failed to load acoustic indices: {e}")
            return False
            
        # Load detection data for validation
        try:
            self.detections = self.loader.load_detection_data(station, year)
            self.detections['datetime'] = pd.to_datetime(self.detections['Date'])
            self.detections['hour'] = self.detections['datetime'].dt.hour
            self.detections['day'] = self.detections['datetime'].dt.dayofyear
            self.detections['week'] = self.detections['datetime'].dt.isocalendar().week
            self.detections['month'] = self.detections['datetime'].dt.month
            logger.info(f"Loaded {len(self.detections)} detection records for validation")
        except Exception as e:
            logger.warning(f"Could not load detection data: {e}")
            
        return True
    
    def prepare_clustering_features(self, temporal_resolution: str = 'hourly') -> pd.DataFrame:
        """Prepare features for clustering at different temporal resolutions."""
        
        if temporal_resolution == 'hourly':
            # Use raw hourly data
            features_df = self.acoustic_indices.copy()
            time_col = 'datetime'
        
        elif temporal_resolution == 'daily':
            # First identify numeric columns
            potential_cols = [col for col in self.acoustic_indices.columns 
                            if col not in ['datetime', 'Date', 'hour', 'day', 'week', 'month']]
            numeric_cols = []
            for col in potential_cols:
                try:
                    # Convert to numeric and check if mostly numeric
                    numeric_series = pd.to_numeric(self.acoustic_indices[col], errors='coerce')
                    if numeric_series.notna().sum() / len(numeric_series) > 0.8:
                        numeric_cols.append(col)
                        # Replace the column with numeric version
                        self.acoustic_indices[col] = numeric_series
                except:
                    continue
            
            # Aggregate to daily means using only numeric columns
            agg_dict = {col: 'mean' for col in numeric_cols}
            agg_dict.update({
                'datetime': 'first',
                'month': 'first', 
                'week': 'first'
            })
            
            features_df = self.acoustic_indices.groupby('day').agg(agg_dict).reset_index()
            time_col = 'datetime'
        
        elif temporal_resolution == 'weekly':
            # Use already cleaned numeric columns from daily processing
            if hasattr(self, '_numeric_cols'):
                numeric_cols = self._numeric_cols
            else:
                # Identify numeric columns
                potential_cols = [col for col in self.acoustic_indices.columns 
                               if col not in ['datetime', 'Date', 'hour', 'day', 'week', 'month']]
                numeric_cols = []
                for col in potential_cols:
                    try:
                        numeric_series = pd.to_numeric(self.acoustic_indices[col], errors='coerce')
                        if numeric_series.notna().sum() / len(numeric_series) > 0.8:
                            numeric_cols.append(col)
                            self.acoustic_indices[col] = numeric_series
                    except:
                        continue
                self._numeric_cols = numeric_cols
            
            agg_dict = {col: 'mean' for col in numeric_cols}
            agg_dict.update({'datetime': 'first', 'month': 'first'})
            
            features_df = self.acoustic_indices.groupby('week').agg(agg_dict).reset_index()
            time_col = 'datetime'
        
        elif temporal_resolution == 'monthly':
            # Use already cleaned numeric columns
            if hasattr(self, '_numeric_cols'):
                numeric_cols = self._numeric_cols  
            else:
                # Identify numeric columns
                potential_cols = [col for col in self.acoustic_indices.columns 
                               if col not in ['datetime', 'Date', 'hour', 'day', 'week', 'month']]
                numeric_cols = []
                for col in potential_cols:
                    try:
                        numeric_series = pd.to_numeric(self.acoustic_indices[col], errors='coerce')
                        if numeric_series.notna().sum() / len(numeric_series) > 0.8:
                            numeric_cols.append(col)
                            self.acoustic_indices[col] = numeric_series
                    except:
                        continue
                self._numeric_cols = numeric_cols
            
            agg_dict = {col: 'mean' for col in numeric_cols}
            agg_dict.update({'datetime': 'first'})
            
            features_df = self.acoustic_indices.groupby('month').agg(agg_dict).reset_index()
            time_col = 'datetime'
        
        else:
            raise ValueError(f"Unknown temporal resolution: {temporal_resolution}")
        
        # Select numeric acoustic index columns
        acoustic_cols = [col for col in features_df.columns 
                        if col not in ['datetime', 'Date', 'hour', 'day', 'week', 'month']]
        
        # More robust numeric column detection
        numeric_cols = []
        for col in acoustic_cols:
            try:
                # Try to convert to numeric and check if mostly numbers
                numeric_series = pd.to_numeric(features_df[col], errors='coerce')
                if numeric_series.notna().sum() / len(numeric_series) > 0.8:  # At least 80% numeric
                    numeric_cols.append(col)
            except:
                continue
        
        acoustic_cols = numeric_cols
        
        # Clean the data
        features_clean = features_df[acoustic_cols + [time_col]].copy()
        
        # Remove columns with too many NaNs or constant values
        valid_cols = []
        for col in acoustic_cols:
            if features_clean[col].isna().sum() / len(features_clean) < 0.5:  # Less than 50% NaN
                if features_clean[col].std() > 1e-10:  # Not constant
                    valid_cols.append(col)
        
        features_clean = features_clean[valid_cols + [time_col]]
        
        # Fill remaining NaNs with median
        for col in valid_cols:
            features_clean[col] = features_clean[col].fillna(features_clean[col].median())
        
        logger.info(f"Prepared {len(features_clean)} samples with {len(valid_cols)} features for {temporal_resolution} clustering")
        
        return features_clean
    
    def perform_pca_analysis(self, features_df: pd.DataFrame, n_components: int = 10) -> Dict:
        """Perform PCA analysis on acoustic features."""
        
        # Prepare feature matrix
        time_col = 'datetime'
        feature_cols = [col for col in features_df.columns if col != time_col]
        X = features_df[feature_cols].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform PCA
        pca = PCA(n_components=n_components)
        X_pca = pca.fit_transform(X_scaled)
        
        # Calculate explained variance
        explained_variance = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        
        # Create component loadings dataframe
        loadings_df = pd.DataFrame(
            pca.components_.T,
            index=feature_cols,
            columns=[f'PC{i+1}' for i in range(n_components)]
        )
        
        results = {
            'pca': pca,
            'scaler': scaler,
            'X_scaled': X_scaled,
            'X_pca': X_pca,
            'explained_variance': explained_variance,
            'cumulative_variance': cumulative_variance,
            'loadings': loadings_df,
            'feature_names': feature_cols,
            'timestamps': features_df[time_col].values
        }
        
        logger.info(f"PCA explained variance: {cumulative_variance[2]:.1%} (first 3 components)")
        
        return results
    
    def find_optimal_clusters(self, X_pca: np.ndarray, max_k: int = 12) -> Dict:
        """Find optimal number of clusters using multiple metrics."""
        
        k_range = range(2, max_k + 1)
        silhouette_scores = []
        calinski_scores = []
        inertias = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_pca)
            
            silhouette_scores.append(silhouette_score(X_pca, labels))
            calinski_scores.append(calinski_harabasz_score(X_pca, labels))
            inertias.append(kmeans.inertia_)
        
        # Find optimal k
        optimal_k_silhouette = k_range[np.argmax(silhouette_scores)]
        optimal_k_calinski = k_range[np.argmax(calinski_scores)]
        
        # Elbow method (simplified)
        inertia_diff = np.diff(inertias)
        elbow_k = k_range[np.argmax(inertia_diff[:-1] - inertia_diff[1:]) + 1]
        
        return {
            'k_range': list(k_range),
            'silhouette_scores': silhouette_scores,
            'calinski_scores': calinski_scores,
            'inertias': inertias,
            'optimal_k_silhouette': optimal_k_silhouette,
            'optimal_k_calinski': optimal_k_calinski,
            'optimal_k_elbow': elbow_k
        }
    
    def perform_clustering(self, X_pca: np.ndarray, n_clusters: int = None) -> Dict:
        """Perform multiple clustering algorithms."""
        
        if n_clusters is None:
            # Auto-determine optimal clusters
            cluster_metrics = self.find_optimal_clusters(X_pca)
            n_clusters = cluster_metrics['optimal_k_silhouette']
            logger.info(f"Auto-selected {n_clusters} clusters based on silhouette score")
        
        results = {}
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(X_pca)
        results['kmeans'] = {
            'labels': kmeans_labels,
            'centers': kmeans.cluster_centers_,
            'silhouette': silhouette_score(X_pca, kmeans_labels)
        }
        
        # Hierarchical clustering
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
        hierarchical_labels = hierarchical.fit_predict(X_pca)
        results['hierarchical'] = {
            'labels': hierarchical_labels,
            'silhouette': silhouette_score(X_pca, hierarchical_labels)
        }
        
        # DBSCAN (density-based)
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = dbscan.fit_predict(X_pca)
        n_dbscan_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
        
        if n_dbscan_clusters > 1:
            results['dbscan'] = {
                'labels': dbscan_labels,
                'n_clusters': n_dbscan_clusters,
                'silhouette': silhouette_score(X_pca, dbscan_labels) if n_dbscan_clusters > 1 else -1
            }
        
        logger.info(f"Clustering results: K-means={results['kmeans']['silhouette']:.3f}, "
                   f"Hierarchical={results['hierarchical']['silhouette']:.3f}")
        
        return results
    
    def analyze_cluster_characteristics(self, features_df: pd.DataFrame, 
                                     pca_results: Dict, 
                                     clustering_results: Dict) -> Dict:
        """Analyze what each cluster represents."""
        
        # Use best clustering method
        best_method = max(clustering_results.keys(), 
                         key=lambda x: clustering_results[x].get('silhouette', -1))
        labels = clustering_results[best_method]['labels']
        
        logger.info(f"Using {best_method} clustering for analysis")
        
        # Add cluster labels to features
        time_col = 'datetime'
        feature_cols = [col for col in features_df.columns if col != time_col]
        
        analysis_df = features_df.copy()
        analysis_df['cluster'] = labels
        analysis_df['timestamp'] = pd.to_datetime(analysis_df[time_col])
        
        cluster_stats = {}
        n_clusters = len(np.unique(labels[labels >= 0]))  # Exclude noise (-1) if present
        
        for cluster_id in range(n_clusters):
            cluster_mask = labels == cluster_id
            cluster_data = analysis_df[cluster_mask]
            
            # Time characteristics
            cluster_hours = cluster_data['timestamp'].dt.hour.values
            cluster_months = cluster_data['timestamp'].dt.month.values
            
            # Acoustic characteristics (using original features)
            cluster_features = cluster_data[feature_cols].mean()
            
            # PCA space characteristics
            cluster_pca = pca_results['X_pca'][cluster_mask]
            
            # Handle stats.mode() differences across scipy versions
            def safe_mode(data):
                if len(data) == 0:
                    return None
                try:
                    mode_result = stats.mode(data)
                    if hasattr(mode_result, 'mode'):
                        return mode_result.mode[0] if len(mode_result.mode) > 0 else None
                    else:
                        return mode_result[0][0] if len(mode_result[0]) > 0 else None
                except:
                    # Fallback to most common value
                    unique, counts = np.unique(data, return_counts=True)
                    return unique[np.argmax(counts)]
            
            cluster_stats[cluster_id] = {
                'size': cluster_mask.sum(),
                'proportion': cluster_mask.mean(),
                'peak_hour': safe_mode(cluster_hours),
                'peak_month': safe_mode(cluster_months),
                'hour_distribution': np.bincount(cluster_hours, minlength=24),
                'month_distribution': np.bincount(cluster_months, minlength=13)[1:],  # Remove 0 index
                'feature_means': cluster_features,
                'pca_centroid': cluster_pca.mean(axis=0),
                'timestamps': cluster_data['timestamp'].tolist()
            }
        
        return {
            'method': best_method,
            'labels': labels,
            'cluster_stats': cluster_stats,
            'analysis_df': analysis_df
        }
    
    def validate_clusters_with_biology(self, cluster_analysis: Dict) -> Dict:
        """Validate acoustic clusters against biological activity."""
        
        if self.detections is None:
            logger.warning("No detection data available for biological validation")
            return {}
        
        # Get fish species for validation
        species_mapping = self.loader.load_species_mapping()
        fish_species = species_mapping[
            (species_mapping['group'] == 'fish') & 
            (species_mapping['keep_species'] == 1)
        ]['long_name'].tolist()
        
        available_species = [sp for sp in fish_species if sp in self.detections.columns][:5]
        
        validation_results = {}
        labels = cluster_analysis['labels']
        n_clusters = len(cluster_analysis['cluster_stats'])
        
        for species in available_species:
            # Convert species data to numeric
            species_data = pd.to_numeric(self.detections[species], errors='coerce').fillna(0)
            
            # Calculate mean activity per cluster
            cluster_activity = {}
            for cluster_id in range(n_clusters):
                cluster_mask = labels == cluster_id
                if cluster_mask.sum() > 0:
                    # Match timestamps between acoustic indices and detections
                    # This is a simplified matching - assumes same temporal resolution
                    activity_mean = species_data[cluster_mask[:len(species_data)]].mean()
                    cluster_activity[cluster_id] = activity_mean
            
            validation_results[species] = cluster_activity
        
        return validation_results
    
    def plot_clustering_overview(self, pca_results: Dict, clustering_results: Dict,
                                cluster_analysis: Dict, save_path: str = None):
        """Create comprehensive clustering visualization."""
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        
        # Panel 1: Explained variance
        ax1 = axes[0, 0]
        n_components = len(pca_results['explained_variance'])
        ax1.bar(range(1, n_components + 1), pca_results['explained_variance'], alpha=0.7)
        ax1.plot(range(1, n_components + 1), pca_results['cumulative_variance'], 'ro-')
        ax1.set_xlabel('Principal Component')
        ax1.set_ylabel('Explained Variance Ratio')
        ax1.set_title('PCA Explained Variance')
        ax1.legend(['Individual', 'Cumulative'])
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: PCA scatter (first 2 components)
        ax2 = axes[0, 1]
        labels = cluster_analysis['labels']
        X_pca = pca_results['X_pca']
        
        # Color by cluster
        unique_labels = np.unique(labels[labels >= 0])
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
        
        for i, label in enumerate(unique_labels):
            mask = labels == label
            ax2.scatter(X_pca[mask, 0], X_pca[mask, 1], c=[colors[i]], 
                       label=f'Cluster {label}', alpha=0.6, s=20)
        
        ax2.set_xlabel(f'PC1 ({pca_results["explained_variance"][0]:.1%})')
        ax2.set_ylabel(f'PC2 ({pca_results["explained_variance"][1]:.1%})')
        ax2.set_title('Clusters in PCA Space')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Panel 3: Cluster sizes
        ax3 = axes[0, 2]
        cluster_sizes = [stats['size'] for stats in cluster_analysis['cluster_stats'].values()]
        cluster_ids = list(cluster_analysis['cluster_stats'].keys())
        
        bars = ax3.bar(cluster_ids, cluster_sizes, color=colors[:len(cluster_ids)])
        ax3.set_xlabel('Cluster ID')
        ax3.set_ylabel('Number of Observations')
        ax3.set_title('Cluster Sizes')
        ax3.grid(True, alpha=0.3)
        
        # Add percentages on bars
        total = sum(cluster_sizes)
        for i, (bar, size) in enumerate(zip(bars, cluster_sizes)):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + total*0.01,
                    f'{size/total:.1%}', ha='center', va='bottom', fontsize=9)
        
        # Panel 4: Temporal distribution (hourly)
        ax4 = axes[1, 0]
        hours = range(24)
        
        for i, (cluster_id, stats) in enumerate(cluster_analysis['cluster_stats'].items()):
            hour_dist = stats['hour_distribution'] / stats['size']  # Normalize
            ax4.plot(hours, hour_dist, 'o-', color=colors[i], 
                    label=f'Cluster {cluster_id}', alpha=0.7)
        
        ax4.set_xlabel('Hour of Day')
        ax4.set_ylabel('Relative Frequency')
        ax4.set_title('Cluster Temporal Patterns (Hourly)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xticks(range(0, 24, 4))
        
        # Panel 5: Seasonal distribution
        ax5 = axes[1, 1]
        months = range(1, 13)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for i, (cluster_id, stats) in enumerate(cluster_analysis['cluster_stats'].items()):
            month_dist = stats['month_distribution'] / stats['size']  # Normalize
            ax5.plot(months, month_dist, 'o-', color=colors[i], 
                    label=f'Cluster {cluster_id}', alpha=0.7)
        
        ax5.set_xlabel('Month')
        ax5.set_ylabel('Relative Frequency')
        ax5.set_title('Cluster Seasonal Patterns')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_xticks(months)
        ax5.set_xticklabels(month_names, rotation=45)
        
        # Panel 6: Top feature loadings for PC1
        ax6 = axes[1, 2]
        pc1_loadings = pca_results['loadings']['PC1'].abs().sort_values(ascending=True)
        top_features = pc1_loadings.tail(10)
        
        ax6.barh(range(len(top_features)), top_features.values)
        ax6.set_yticks(range(len(top_features)))
        ax6.set_yticklabels(top_features.index, fontsize=9)
        ax6.set_xlabel('|Loading|')
        ax6.set_title('Top PC1 Feature Loadings')
        ax6.grid(True, alpha=0.3)
        
        plt.suptitle(f'Acoustic Clustering Analysis - {cluster_analysis["method"].title()} Method', 
                    fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved clustering overview: {save_path}")
        
        return fig
    
    def plot_biological_validation(self, cluster_analysis: Dict, validation_results: Dict,
                                 save_path: str = None):
        """Plot biological validation of acoustic clusters."""
        
        if not validation_results:
            logger.warning("No biological validation data to plot")
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        species_list = list(validation_results.keys())
        n_clusters = len(cluster_analysis['cluster_stats'])
        
        # Panel 1: Activity heatmap
        ax1 = axes[0, 0]
        
        activity_matrix = np.zeros((len(species_list), n_clusters))
        for i, species in enumerate(species_list):
            for j in range(n_clusters):
                activity_matrix[i, j] = validation_results[species].get(j, 0)
        
        im1 = ax1.imshow(activity_matrix, cmap='YlOrRd', aspect='auto')
        ax1.set_xticks(range(n_clusters))
        ax1.set_xticklabels([f'Cluster {i}' for i in range(n_clusters)])
        ax1.set_yticks(range(len(species_list)))
        ax1.set_yticklabels([sp[:20] for sp in species_list], fontsize=10)
        ax1.set_title('Mean Species Activity by Cluster')
        plt.colorbar(im1, ax=ax1, label='Detection Intensity')
        
        # Panel 2: Cluster interpretation
        ax2 = axes[0, 1]
        
        # Create cluster interpretation text
        interpretations = []
        for cluster_id, stats in cluster_analysis['cluster_stats'].items():
            peak_hour = stats['peak_hour']
            peak_month = stats['peak_month']
            size_pct = stats['proportion'] * 100
            
            # Interpret time of day
            if 5 <= peak_hour <= 8:
                time_desc = "Dawn"
            elif 9 <= peak_hour <= 16:
                time_desc = "Day"
            elif 17 <= peak_hour <= 20:
                time_desc = "Dusk"
            else:
                time_desc = "Night"
            
            # Interpret season
            if peak_month in [12, 1, 2]:
                season_desc = "Winter"
            elif peak_month in [3, 4, 5]:
                season_desc = "Spring"
            elif peak_month in [6, 7, 8]:
                season_desc = "Summer"
            else:
                season_desc = "Fall"
            
            interpretations.append(f"Cluster {cluster_id} ({size_pct:.1f}%):\n"
                                 f"  {time_desc} sounds, {season_desc} peak\n"
                                 f"  Peak: {peak_hour:02d}:00, Month {peak_month}")
        
        # Display interpretations
        ax2.text(0.05, 0.95, '\n\n'.join(interpretations), 
                transform=ax2.transAxes, fontsize=11, 
                verticalalignment='top', fontfamily='monospace')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('Cluster Interpretations')
        
        # Panel 3: Activity by cluster (bar chart)
        ax3 = axes[1, 0]
        
        cluster_total_activity = []
        for cluster_id in range(n_clusters):
            total_activity = sum(validation_results[sp].get(cluster_id, 0) for sp in species_list)
            cluster_total_activity.append(total_activity)
        
        bars = ax3.bar(range(n_clusters), cluster_total_activity, 
                      color=plt.cm.tab10(np.linspace(0, 1, n_clusters)))
        ax3.set_xlabel('Cluster ID')
        ax3.set_ylabel('Total Species Activity')
        ax3.set_title('Biological Activity by Acoustic Cluster')
        ax3.set_xticks(range(n_clusters))
        ax3.set_xticklabels([f'C{i}' for i in range(n_clusters)])
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: Species-specific patterns
        ax4 = axes[1, 1]
        
        # Show top 3 species
        top_species = species_list[:3]
        x_pos = np.arange(n_clusters)
        width = 0.25
        
        for i, species in enumerate(top_species):
            activities = [validation_results[species].get(j, 0) for j in range(n_clusters)]
            ax4.bar(x_pos + i * width, activities, width, 
                   label=species[:15], alpha=0.8)
        
        ax4.set_xlabel('Cluster ID')
        ax4.set_ylabel('Detection Intensity')
        ax4.set_title('Top Species Activity by Cluster')
        ax4.set_xticks(x_pos + width)
        ax4.set_xticklabels([f'C{i}' for i in range(n_clusters)])
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Biological Validation of Acoustic Clusters', fontsize=16, y=0.98)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"Saved biological validation: {save_path}")
        
        return fig

def main():
    """Run acoustic clustering analysis."""
    
    print("=" * 60)
    print("Acoustic Clustering Analysis: Ecosystem State Detection")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = AcousticClusteringAnalyzer(repo_root / "data")
    
    # Create output directory
    output_dir = Path.cwd() / "analysis_results" / "acoustic_clustering"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\n1. Loading data for Station 14M, Year 2021...")
    if not analyzer.load_data(station='14M', year=2021):
        print("Failed to load data. Exiting.")
        return
    
    # Test different temporal resolutions
    temporal_resolutions = ['daily', 'weekly']  # Start with these for cleaner results
    
    for resolution in temporal_resolutions:
        print(f"\n2. Analyzing {resolution} acoustic clustering patterns...")
        
        # Prepare features
        features_df = analyzer.prepare_clustering_features(resolution)
        
        if len(features_df) < 10:
            print(f"   Insufficient data for {resolution} analysis")
            continue
        
        # Perform PCA
        print(f"   Performing PCA analysis...")
        pca_results = analyzer.perform_pca_analysis(features_df, n_components=8)
        
        # Perform clustering
        print(f"   Performing clustering analysis...")
        clustering_results = analyzer.perform_clustering(pca_results['X_pca'][:, :5])  # Use first 5 PCs
        
        # Analyze cluster characteristics
        print(f"   Analyzing cluster characteristics...")
        cluster_analysis = analyzer.analyze_cluster_characteristics(
            features_df, pca_results, clustering_results)
        
        # Validate with biological data
        print(f"   Validating with biological activity...")
        validation_results = analyzer.validate_clusters_with_biology(cluster_analysis)
        
        # Store results
        analyzer.clustering_results[resolution] = {
            'pca': pca_results,
            'clustering': clustering_results,
            'analysis': cluster_analysis,
            'validation': validation_results
        }
        
        # Create visualizations
        print(f"   Creating visualizations...")
        
        overview_path = output_dir / f"clustering_overview_{resolution}.png"
        fig1 = analyzer.plot_clustering_overview(
            pca_results, clustering_results, cluster_analysis, save_path=str(overview_path))
        plt.close(fig1)
        
        if validation_results:
            validation_path = output_dir / f"biological_validation_{resolution}.png"
            fig2 = analyzer.plot_biological_validation(
                cluster_analysis, validation_results, save_path=str(validation_path))
            if fig2:
                plt.close(fig2)
        
        print(f"   Saved: clustering_overview_{resolution}.png")
        
        # Print insights for this resolution
        n_clusters = len(cluster_analysis['cluster_stats'])
        best_silhouette = max([result.get('silhouette', -1) 
                              for result in clustering_results.values()])
        
        print(f"   Results: {n_clusters} clusters, silhouette score: {best_silhouette:.3f}")
    
    # Summary insights
    print("\n" + "=" * 60)
    print("KEY INSIGHTS:")
    print("=" * 60)
    
    for resolution in temporal_resolutions:
        if resolution in analyzer.clustering_results:
            results = analyzer.clustering_results[resolution]
            cluster_stats = results['analysis']['cluster_stats']
            
            print(f"\n{resolution.title()} Clustering:")
            print(f"  Found {len(cluster_stats)} distinct acoustic regimes")
            
            # Describe each cluster
            for cluster_id, stats in cluster_stats.items():
                peak_hour = stats.get('peak_hour', 'N/A')
                peak_month = stats.get('peak_month', 'N/A')
                size_pct = stats.get('proportion', 0) * 100
                
                print(f"    Cluster {cluster_id}: {size_pct:.1f}% of time, "
                      f"peaks at hour {peak_hour}, month {peak_month}")
    
    print("\n" + "=" * 60)
    print("Potential Applications:")
    print("- Real-time ecosystem state monitoring")
    print("- Automated detection of unusual acoustic events")
    print("- Seasonal baseline establishment and drift detection")  
    print("- Integration with environmental sensor networks")
    print("=" * 60)

if __name__ == "__main__":
    main()