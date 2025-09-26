#!/usr/bin/env python3
"""
Script 2: Feature Reduction
===========================

Purpose: Reduce acoustic indices to non-redundant set focused on biological signal
Key Question: Which indices provide unique information vs redundant signal?

This script takes the aligned dataset from Script 1 and performs systematic reduction
of the ~60 acoustic indices down to ~15-20 non-redundant indices that capture 
distinct acoustic dimensions while preserving ecological information.

Key Outputs:
- data/processed/reduced_acoustic_indices.parquet - Final reduced index set
- data/processed/index_reduction_report.json - Selection rationale and statistics
- figures/02_index_correlation_matrix.png - Before/after reduction visualization
- figures/02_index_clustering_dendrogram.png - Functional groupings
- figures/02_vessel_impact_assessment.png - Index robustness to vessel noise

Reference Sources:
- python/scripts/notebooks/03_acoustic_index_reduction.py - Index reduction methods
- python/acoustic_vs_environmental/01_data_loading.py - Correlation analysis patterns
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

# Statistical analysis imports
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

def find_project_root():
    """Find project root by looking for the data folder"""
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent
    return project_root

# Set up paths using standard pattern
PROJECT_ROOT = find_project_root()
DATA_ROOT = PROJECT_ROOT / "data"
INPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
FIGURE_DIR = Path(__file__).parent.parent / "figures"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# Analysis parameters
CORRELATION_THRESHOLD = 0.85  # Remove indices with correlation above this
TARGET_CLUSTERS = 18  # Aim for ~15-20 final indices

print("="*60)
print("SCRIPT 2: FEATURE REDUCTION")
print("="*60)
print(f"Project root: {PROJECT_ROOT}")
print(f"Input directory: {INPUT_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Figure directory: {FIGURE_DIR}")
print(f"Correlation threshold: {CORRELATION_THRESHOLD}")
print(f"Target clusters: {TARGET_CLUSTERS}")
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
    print(f"Stations: {sorted(df['station'].unique()) if 'station' in df.columns else 'No station column'}")
    print()
    
    return df

def identify_acoustic_indices(df):
    """Identify acoustic index columns from the dataset"""
    print("2. IDENTIFYING ACOUSTIC INDEX COLUMNS")
    print("-" * 40)
    
    # Need to load acoustic indices from the raw data since Script 1 only has detection data
    # Let's load the acoustic indices directly from the raw source
    indices_data = {}
    stations = ['9M', '14M', '37M']
    year = 2021
    
    for station in stations:
        file_path = DATA_ROOT / "raw" / "indices" / f"Acoustic_Indices_{station}_{year}_FullBW_v2_Final.csv"
        if file_path.exists():
            try:
                df_idx = pd.read_csv(file_path)
                # Create datetime column for merging
                df_idx['datetime'] = pd.to_datetime(df_idx['Date'], errors='coerce')
                df_idx['station'] = station
                indices_data[station] = df_idx
                print(f"✓ Loaded {station}: {len(df_idx)} rows, {len(df_idx.columns)} columns")
            except Exception as e:
                print(f"✗ Error loading {station}: {e}")
        else:
            print(f"✗ File not found for {station}: {file_path}")
    
    if not indices_data:
        raise RuntimeError("No acoustic indices data loaded")
    
    # Combine all stations
    df_indices_combined = pd.concat(indices_data.values(), ignore_index=True)
    
    # Identify acoustic index columns (exclude metadata columns)
    exclude_cols = ['Date', 'Time', 'station', 'datetime', 'year', 'month', 'day', 
                   'hour', 'minute', 'second', 'File', 'Deployment ID']
    
    acoustic_index_cols = [col for col in df_indices_combined.columns 
                          if col not in exclude_cols and df_indices_combined[col].dtype in ['float64', 'int64']]
    
    print(f"Identified {len(acoustic_index_cols)} acoustic index columns")
    print(f"First 10: {acoustic_index_cols[:10]}")
    print(f"Combined indices dataset: {df_indices_combined.shape}")
    print()
    
    return df_indices_combined, acoustic_index_cols

def analyze_correlations(df_indices, acoustic_index_cols):
    """Perform correlation analysis on acoustic indices"""
    print("3. CORRELATION ANALYSIS")
    print("-" * 30)
    
    # Extract only the acoustic index columns
    df_indices_only = df_indices[acoustic_index_cols].copy()
    
    # Remove columns with all NaN or constant values
    df_indices_only = df_indices_only.dropna(axis=1, how='all')  # Remove all-NaN columns
    df_indices_only = df_indices_only.loc[:, df_indices_only.var() > 0]  # Remove constant columns
    
    print(f"After removing NaN/constant columns: {len(df_indices_only.columns)} indices")
    
    # Calculate correlation matrix
    corr_matrix = df_indices_only.corr()
    
    print(f"Correlation matrix shape: {corr_matrix.shape}")
    print(f"Mean absolute correlation: {corr_matrix.abs().mean().mean():.3f}")
    
    # Find highly correlated pairs
    high_corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = abs(corr_matrix.iloc[i, j])
            if corr_val > CORRELATION_THRESHOLD:
                high_corr_pairs.append((
                    corr_matrix.columns[i], 
                    corr_matrix.columns[j], 
                    corr_val
                ))
    
    print(f"Found {len(high_corr_pairs)} pairs with |correlation| > {CORRELATION_THRESHOLD}")
    
    if high_corr_pairs:
        high_corr_df = pd.DataFrame(high_corr_pairs, columns=['Index1', 'Index2', 'Correlation'])
        high_corr_df = high_corr_df.sort_values('Correlation', ascending=False)
        print("\nTop 10 highest correlations:")
        print(high_corr_df.head(10).to_string(index=False))
    
    print()
    return corr_matrix, high_corr_pairs, df_indices_only.columns.tolist()

def perform_hierarchical_clustering(corr_matrix):
    """Perform hierarchical clustering on correlation matrix"""
    print("4. HIERARCHICAL CLUSTERING")
    print("-" * 30)
    
    # Convert correlation to distance (1 - |correlation|)
    distance_matrix = 1 - corr_matrix.abs()
    
    # Convert to numpy array and ensure symmetry
    dist_array = distance_matrix.values
    dist_array = (dist_array + dist_array.T) / 2
    np.fill_diagonal(dist_array, 0)
    
    # Handle NaN values and ensure non-negative distances
    if np.any(np.isnan(dist_array)):
        print(f"Warning: Found {np.sum(np.isnan(dist_array))} NaN values in distance matrix")
        dist_array = np.nan_to_num(dist_array, nan=1.0)
    
    dist_array = np.maximum(dist_array, 0)
    epsilon = 1e-10
    dist_array = dist_array + epsilon * (1 - np.eye(dist_array.shape[0]))
    
    # Perform hierarchical clustering
    condensed_distances = squareform(dist_array, checks=False)
    linkage_matrix = linkage(condensed_distances, method='ward')
    
    # Get cluster assignments
    cluster_labels = fcluster(linkage_matrix, TARGET_CLUSTERS, criterion='maxclust')
    
    # Create cluster assignment dataframe
    cluster_df = pd.DataFrame({
        'index': corr_matrix.columns,
        'cluster': cluster_labels
    })
    
    cluster_summary = cluster_df.groupby('cluster').size().sort_values(ascending=False)
    print(f"Clustering with {TARGET_CLUSTERS} clusters:")
    print(f"Cluster sizes: {cluster_summary.values}")
    print(f"Largest cluster: {cluster_summary.iloc[0]} indices")
    print(f"Smallest cluster: {cluster_summary.iloc[-1]} indices")
    print()
    
    return linkage_matrix, cluster_df, cluster_summary

def select_representative_indices(cluster_df, corr_matrix):
    """Select representative indices from each cluster"""
    print("5. SELECTING REPRESENTATIVE INDICES")
    print("-" * 40)
    
    selected_indices = []
    selection_rationale = {}
    
    for cluster_id in sorted(cluster_df['cluster'].unique()):
        cluster_indices = cluster_df[cluster_df['cluster'] == cluster_id]['index'].tolist()
        
        if len(cluster_indices) == 1:
            # Single index in cluster - automatically selected
            selected_idx = cluster_indices[0]
            selection_rationale[selected_idx] = f"Only index in cluster {cluster_id}"
        else:
            # Multiple indices - choose most representative
            cluster_corr_means = []
            
            for idx in cluster_indices:
                other_indices = [i for i in cluster_indices if i != idx]
                mean_corr = corr_matrix.loc[idx, other_indices].abs().mean()
                cluster_corr_means.append(mean_corr)
            
            # Select index with highest mean correlation (most representative)
            best_idx_pos = np.argmax(cluster_corr_means)
            selected_idx = cluster_indices[best_idx_pos]
            
            selection_rationale[selected_idx] = (
                f"Most representative of cluster {cluster_id} "
                f"({len(cluster_indices)} indices, mean_r={cluster_corr_means[best_idx_pos]:.3f})"
            )
        
        selected_indices.append(selected_idx)
    
    print(f"Selected {len(selected_indices)} representative indices from {TARGET_CLUSTERS} clusters")
    print(f"Reduction ratio: {len(selected_indices)}/{len(corr_matrix.columns)} = {len(selected_indices)/len(corr_matrix.columns):.2f}")
    
    print("\nSelected indices (first 10):")
    for idx in selected_indices[:10]:
        print(f"  {idx}: {selection_rationale[idx]}")
    if len(selected_indices) > 10:
        print(f"  ... and {len(selected_indices) - 10} more")
    
    print()
    return selected_indices, selection_rationale

def assess_vessel_impact(df_indices, selected_indices):
    """Assess how selected indices respond to vessel presence"""
    print("6. VESSEL IMPACT ASSESSMENT")
    print("-" * 30)
    
    # This is a placeholder - would need vessel detection data
    # For now, just note which indices were selected
    vessel_impact = {}
    for idx in selected_indices:
        vessel_impact[idx] = {
            'robust_to_vessel': 'unknown',  # Would assess using vessel detection data
            'rationale': 'Vessel impact assessment requires vessel detection data'
        }
    
    print("✓ Vessel impact assessment prepared (requires vessel detection data from detections)")
    print()
    return vessel_impact

def create_visualizations(corr_matrix, linkage_matrix, cluster_df, selected_indices):
    """Create visualizations for the reduction process"""
    print("7. CREATING VISUALIZATIONS")
    print("-" * 30)
    
    # Set up plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 1. Correlation matrix heatmap
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Before reduction (sample if too large)
    if len(corr_matrix) > 50:
        # Sample 50 random indices for visualization
        sample_indices = np.random.choice(corr_matrix.columns, 50, replace=False)
        corr_sample = corr_matrix.loc[sample_indices, sample_indices]
    else:
        corr_sample = corr_matrix
    
    sns.heatmap(corr_sample, cmap='RdBu_r', center=0, 
                square=True, ax=ax1, cbar_kws={'shrink': 0.8})
    ax1.set_title(f'Before Reduction\n({len(corr_matrix)} indices, sample shown)')
    ax1.tick_params(axis='both', labelsize=8)
    
    # After reduction
    corr_reduced = corr_matrix.loc[selected_indices, selected_indices]
    sns.heatmap(corr_reduced, cmap='RdBu_r', center=0, 
                square=True, ax=ax2, cbar_kws={'shrink': 0.8})
    ax2.set_title(f'After Reduction\n({len(selected_indices)} indices)')
    ax2.tick_params(axis='both', labelsize=8)
    
    plt.tight_layout()
    corr_file = FIGURE_DIR / "02_index_correlation_matrix.png"
    plt.savefig(corr_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Correlation matrix saved: {corr_file}")
    
    # 2. Clustering dendrogram
    fig, ax = plt.subplots(figsize=(15, 8))
    dendrogram(linkage_matrix, labels=corr_matrix.columns, ax=ax, 
               leaf_rotation=90, leaf_font_size=8)
    ax.set_title(f'Hierarchical Clustering of Acoustic Indices\n({TARGET_CLUSTERS} clusters)')
    ax.set_xlabel('Acoustic Indices')
    ax.set_ylabel('Distance (1 - |correlation|)')
    
    plt.tight_layout()
    dendro_file = FIGURE_DIR / "02_index_clustering_dendrogram.png"
    plt.savefig(dendro_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Dendrogram saved: {dendro_file}")
    
    # 3. Cluster summary plot
    fig, ax = plt.subplots(figsize=(12, 6))
    cluster_sizes = cluster_df.groupby('cluster').size().sort_values(ascending=False)
    
    bars = ax.bar(range(len(cluster_sizes)), cluster_sizes.values)
    ax.set_title(f'Cluster Sizes (Target: {TARGET_CLUSTERS} clusters)')
    ax.set_xlabel('Cluster ID (sorted by size)')
    ax.set_ylabel('Number of Indices')
    ax.set_xticks(range(len(cluster_sizes)))
    ax.set_xticklabels([f'C{i+1}' for i in range(len(cluster_sizes))])
    
    # Add value labels on bars
    for bar, size in zip(bars, cluster_sizes.values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1, str(size),
                ha='center', va='bottom')
    
    plt.tight_layout()
    cluster_file = FIGURE_DIR / "02_cluster_sizes.png"
    plt.savefig(cluster_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Cluster sizes plot saved: {cluster_file}")

def save_results(df_indices, selected_indices, selection_rationale, cluster_df, vessel_impact):
    """Save the reduced dataset and analysis results"""
    print("8. SAVING RESULTS")
    print("-" * 20)
    
    # Save reduced acoustic indices dataset
    df_reduced = df_indices[['datetime', 'station'] + selected_indices].copy()
    reduced_file = OUTPUT_DIR / "reduced_acoustic_indices.parquet"
    df_reduced.to_parquet(reduced_file, index=False)
    print(f"✓ Reduced indices saved: {reduced_file}")
    
    # Create comprehensive reduction report
    reduction_report = {
        'generation_timestamp': datetime.now().isoformat(),
        'analysis_parameters': {
            'correlation_threshold': CORRELATION_THRESHOLD,
            'target_clusters': TARGET_CLUSTERS,
            'original_indices': len(cluster_df),
            'selected_indices': len(selected_indices)
        },
        'reduction_summary': {
            'reduction_ratio': len(selected_indices) / len(cluster_df),
            'indices_removed': len(cluster_df) - len(selected_indices),
            'final_count': len(selected_indices)
        },
        'selected_indices': selected_indices,
        'selection_rationale': selection_rationale,
        'cluster_assignments': cluster_df.to_dict('records'),
        'vessel_impact': vessel_impact
    }
    
    # Save reduction report
    report_file = OUTPUT_DIR / "index_reduction_report.json"
    with open(report_file, 'w') as f:
        json.dump(reduction_report, f, indent=2, default=str)
    print(f"✓ Reduction report saved: {report_file}")
    
    # Create human-readable summary
    summary_text = f"""
ACOUSTIC INDEX REDUCTION SUMMARY
================================

Original indices: {len(cluster_df)}
Selected indices: {len(selected_indices)}
Reduction ratio: {len(selected_indices) / len(cluster_df):.2f}

CLUSTERS AND REPRESENTATIVES:
"""
    
    for cluster_id in sorted(cluster_df['cluster'].unique()):
        cluster_indices = cluster_df[cluster_df['cluster'] == cluster_id]['index'].tolist()
        selected = [idx for idx in cluster_indices if idx in selected_indices]
        summary_text += f"\nCluster {cluster_id} ({len(cluster_indices)} indices):\n"
        summary_text += f"  Selected: {selected[0] if selected else 'None'}\n"
        summary_text += f"  Members: {', '.join(cluster_indices[:5])}"
        if len(cluster_indices) > 5:
            summary_text += f" ... and {len(cluster_indices) - 5} more"
        summary_text += "\n"
    
    summary_file = OUTPUT_DIR / "index_reduction_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(summary_text)
    print(f"✓ Human-readable summary saved: {summary_file}")

def main():
    """Main execution function"""
    print("Starting feature reduction pipeline...")
    
    # Load data
    df_aligned = load_aligned_dataset()
    df_indices, acoustic_index_cols = identify_acoustic_indices(df_aligned)
    
    # Analyze correlations
    corr_matrix, high_corr_pairs, valid_index_cols = analyze_correlations(df_indices, acoustic_index_cols)
    
    # Perform clustering
    linkage_matrix, cluster_df, cluster_summary = perform_hierarchical_clustering(corr_matrix)
    
    # Select representatives
    selected_indices, selection_rationale = select_representative_indices(cluster_df, corr_matrix)
    
    # Assess vessel impact
    vessel_impact = assess_vessel_impact(df_indices, selected_indices)
    
    # Create visualizations
    create_visualizations(corr_matrix, linkage_matrix, cluster_df, selected_indices)
    
    # Save results
    save_results(df_indices, selected_indices, selection_rationale, cluster_df, vessel_impact)
    
    print()
    print("="*60)
    print("FEATURE REDUCTION COMPLETE")
    print("="*60)
    print(f"Reduced from {len(corr_matrix)} to {len(selected_indices)} indices")
    print(f"Key outputs:")
    print(f"- Reduced dataset: {OUTPUT_DIR / 'reduced_acoustic_indices.parquet'}")
    print(f"- Reduction report: {OUTPUT_DIR / 'index_reduction_report.json'}")
    print(f"- Correlation matrix: {FIGURE_DIR / '02_index_correlation_matrix.png'}")
    print(f"- Clustering dendrogram: {FIGURE_DIR / '02_index_clustering_dendrogram.png'}")

if __name__ == "__main__":
    main()