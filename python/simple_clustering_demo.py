#!/usr/bin/env python3
"""Simple demonstration of acoustic clustering for ecosystem monitoring."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

from mbon_analysis.data.loaders import create_loader

def main():
    """Demonstrate acoustic clustering analysis."""
    
    print("Simple Acoustic Clustering Demo")
    print("=" * 40)
    
    # Load data
    loader = create_loader(repo_root / "data")
    acoustic_indices = loader.load_acoustic_indices('14M', 'FullBW')
    
    print(f"Loaded {len(acoustic_indices)} acoustic index records")
    
    # Add temporal features
    acoustic_indices['datetime'] = pd.to_datetime(acoustic_indices['Date'])
    acoustic_indices['hour'] = acoustic_indices['datetime'].dt.hour
    acoustic_indices['day'] = acoustic_indices['datetime'].dt.dayofyear
    acoustic_indices['month'] = acoustic_indices['datetime'].dt.month
    
    # Select numeric columns only
    potential_cols = [col for col in acoustic_indices.columns 
                     if col not in ['datetime', 'Date', 'hour', 'day', 'month']]
    
    numeric_cols = []
    for col in potential_cols:
        try:
            # Convert to numeric and check if mostly numbers
            numeric_series = pd.to_numeric(acoustic_indices[col], errors='coerce')
            if numeric_series.notna().sum() / len(numeric_series) > 0.8:  # At least 80% numeric
                numeric_cols.append(col)
                acoustic_indices[col] = numeric_series
        except:
            continue
    
    print(f"Found {len(numeric_cols)} valid acoustic indices")
    
    # Aggregate to daily means for cleaner clustering
    daily_features = acoustic_indices.groupby('day').agg({
        **{col: 'mean' for col in numeric_cols},
        'datetime': 'first',
        'month': 'first',
        'hour': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else x.iloc[0]  # Most common hour
    }).reset_index()
    
    print(f"Aggregated to {len(daily_features)} daily samples")
    
    # Prepare feature matrix
    X = daily_features[numeric_cols].fillna(daily_features[numeric_cols].median()).values
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform PCA
    pca = PCA(n_components=10)
    X_pca = pca.fit_transform(X_scaled)
    
    print(f"PCA: {pca.explained_variance_ratio_[:3].sum():.1%} variance in first 3 components")
    
    # Find optimal clusters
    silhouette_scores = []
    k_range = range(2, 8)
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_pca[:, :5])  # Use first 5 PCs
        score = silhouette_score(X_pca[:, :5], labels)
        silhouette_scores.append(score)
    
    optimal_k = k_range[np.argmax(silhouette_scores)]
    print(f"Optimal clusters: {optimal_k} (silhouette score: {max(silhouette_scores):.3f})")
    
    # Perform final clustering
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_pca[:, :5])
    
    # Add cluster labels to dataframe
    daily_features['cluster'] = labels
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Panel 1: PCA explained variance
    ax1 = axes[0, 0]
    ax1.bar(range(1, 11), pca.explained_variance_ratio_[:10])
    ax1.set_xlabel('Principal Component')
    ax1.set_ylabel('Explained Variance Ratio')
    ax1.set_title('PCA Explained Variance')
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Clusters in PCA space
    ax2 = axes[0, 1]
    colors = plt.cm.tab10(np.linspace(0, 1, optimal_k))
    for i in range(optimal_k):
        mask = labels == i
        ax2.scatter(X_pca[mask, 0], X_pca[mask, 1], c=[colors[i]], 
                   label=f'Cluster {i}', alpha=0.7, s=30)
    
    ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
    ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    ax2.set_title('Daily Acoustic Regimes')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Panel 3: Temporal patterns
    ax3 = axes[1, 0]
    for i in range(optimal_k):
        cluster_data = daily_features[daily_features['cluster'] == i]
        month_counts = cluster_data['month'].value_counts().sort_index()
        # Normalize to proportions
        month_props = month_counts / len(cluster_data)
        ax3.plot(month_props.index, month_props.values, 'o-', 
                color=colors[i], label=f'Cluster {i}', alpha=0.7)
    
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Proportion of Days')
    ax3.set_title('Seasonal Patterns by Cluster')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(range(1, 13))
    ax3.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
    
    # Panel 4: Cluster characteristics
    ax4 = axes[1, 1]
    cluster_sizes = daily_features['cluster'].value_counts().sort_index()
    bars = ax4.bar(range(optimal_k), cluster_sizes.values, color=colors[:optimal_k])
    ax4.set_xlabel('Cluster ID')
    ax4.set_ylabel('Number of Days')
    ax4.set_title('Cluster Sizes')
    ax4.grid(True, alpha=0.3)
    
    # Add percentages
    total_days = len(daily_features)
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height/total_days:.1%}', ha='center', va='bottom')
    
    plt.suptitle('Acoustic Clustering Analysis: Daily Ecosystem Regimes', fontsize=14)
    plt.tight_layout()
    
    # Save
    output_dir = Path.cwd() / "analysis_results" / "acoustic_clustering"
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / "simple_clustering_demo.png"
    fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    
    print(f"\\nSaved visualization: {save_path}")
    
    # Print cluster interpretations
    print("\\nCluster Interpretations:")
    print("-" * 25)
    for i in range(optimal_k):
        cluster_data = daily_features[daily_features['cluster'] == i]
        size = len(cluster_data)
        peak_month = cluster_data['month'].mode().iloc[0]
        peak_hour = cluster_data['hour'].mode().iloc[0]
        
        # Season interpretation
        season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',
                     3: 'Spring', 4: 'Spring', 5: 'Spring',
                     6: 'Summer', 7: 'Summer', 8: 'Summer',
                     9: 'Fall', 10: 'Fall', 11: 'Fall'}
        
        # Time interpretation  
        time_map = {**{h: 'Night' for h in range(0, 6)},
                   **{h: 'Morning' for h in range(6, 12)},
                   **{h: 'Afternoon' for h in range(12, 18)},
                   **{h: 'Evening' for h in range(18, 24)}}
        
        season = season_map.get(peak_month, 'Unknown')
        time_of_day = time_map.get(peak_hour, 'Unknown')
        
        print(f"Cluster {i}: {size} days ({size/total_days:.1%})")
        print(f"  Peak season: {season} (month {peak_month})")
        print(f"  Typical time: {time_of_day} (hour {peak_hour})")
        print()
    
    print("=" * 40)
    print("Potential Applications:")
    print("- Automated ecosystem state detection")
    print("- Seasonal baseline establishment")  
    print("- Anomaly detection for unusual acoustic events")
    print("- Long-term monitoring trend analysis")

if __name__ == "__main__":
    main()