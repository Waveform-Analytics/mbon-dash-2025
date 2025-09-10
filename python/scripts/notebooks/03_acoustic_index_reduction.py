import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Notebook 3: Acoustic Index Characterization and Reduction

        **Purpose**: Understand index behavior and reduce to manageable set while preserving ecological information

        **Key Outputs**: Reduced index set (~15-20 indices) with ecological justification

        ## Overview

        This notebook takes the temporally aligned dataset from Notebook 2 and performs comprehensive analysis of the ~50-60 acoustic indices to:

        1. **Index Analysis**: Correlation matrices, PCA, and multicollinearity assessment
        2. **Reduction Strategy**: Apply correlation thresholds and hierarchical clustering to identify functional groups
        3. **Index-Environment Relationships**: Analyze how indices respond to environmental variables and vessel presence
        4. **Quality Assessment**: Validate the reduction approach and document ecological justification

        The goal is to reduce from ~50-60 indices down to ~15-20 indices that capture the majority of acoustic variance while maintaining ecological interpretability and robustness to vessel noise.
        """
    )
    return (mo,)


@app.cell(hide_code=True)
def _():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    import warnings
    warnings.filterwarnings('ignore')

    # Statistical analysis
    from scipy import stats
    from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
    from scipy.spatial.distance import squareform
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    # Set plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Data directory
    data_dir = Path("../data/processed")

    print("Libraries loaded successfully")
    print(f"Data directory: {data_dir}")
    return (
        PCA,
        Path,
        StandardScaler,
        data_dir,
        dendrogram,
        fcluster,
        linkage,
        np,
        pd,
        plt,
        sns,
        squareform,
        stats,
        variance_inflation_factor,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Data Loading

    Loading the temporally aligned dataset from Notebook 2, which contains:

    - Acoustic indices aggregated to 2-hour resolution 
    - Environmental variables (temperature, depth/pressure)
    - SPL data aligned to 2-hour intervals
    - Vessel detection data
    - Temporal variables (hour, day of year, season, etc.)
    """
    )
    return


@app.cell
def _(data_dir, pd):
    # Load the acoustic indices dataset from Notebook 2
    acoustic_indices_file = data_dir / "02_acoustic_indices_aligned_2021.parquet"

    if acoustic_indices_file.exists():
        df_acoustic_indices = pd.read_parquet(acoustic_indices_file)
        print(f"Loaded acoustic indices dataset: {df_acoustic_indices.shape}")
        print(f"Columns: {len(df_acoustic_indices.columns)}")
        print(f"Date range: {df_acoustic_indices['datetime'].min()} to {df_acoustic_indices['datetime'].max()}")
        print(f"Stations: {sorted(df_acoustic_indices['station'].unique())}")
        print(f"Year: {sorted(df_acoustic_indices['year'].unique())}")
    else:
        print(f"Warning: Acoustic indices file not found at {acoustic_indices_file}")
        print("Please run Notebook 2 first to generate the aligned datasets")
        # Create a placeholder for development
        df_acoustic_indices = pd.DataFrame()

    return (df_acoustic_indices,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Acoustic Index Identification

    Identifying the acoustic index columns from the dataset. These should be the numerical columns
    that represent the ~50-60 acoustic indices calculated from the soundscape data.
    """
    )
    return


@app.cell
def _(df_acoustic_indices, pd):
    if not df_acoustic_indices.empty:
        # Identify acoustic index columns - exclude core identifiers
        core_identifiers = ['datetime', 'station', 'year']
        
        # Get all acoustic index columns (everything except identifiers)
        acoustic_index_cols = [col for col in df_acoustic_indices.columns if col not in core_identifiers]

        print(f"Identified {len(acoustic_index_cols)} acoustic index columns:")
        print(acoustic_index_cols[:10], "..." if len(acoustic_index_cols) > 10 else "")

        # Extract acoustic indices dataframe
        df_indices = df_acoustic_indices[acoustic_index_cols].copy()

        # Basic statistics
        print(f"\nAcoustic indices shape: {df_indices.shape}")
        print(f"Missing values per column: {df_indices.isnull().sum().sum()}")

    else:
        acoustic_index_cols = []
        df_indices = pd.DataFrame()
        print("Cannot identify acoustic indices - no data loaded")

    return acoustic_index_cols, df_indices


@app.cell
def _(acoustic_index_cols):
    acoustic_index_cols
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Index Analysis: Correlation and Clustering

    Performing comprehensive analysis of acoustic index relationships:

    1. **Correlation Matrix**: Calculate pairwise correlations between all indices
    2. **Hierarchical Clustering**: Group indices by similarity to identify functional groups
    3. **Variance Inflation Factor**: Assess multicollinearity issues
    """
    )
    return


@app.cell
def _(df_indices, pd):
    if not df_indices.empty:
        # Calculate correlation matrix
        corr_matrix = df_indices.corr()

        print(f"Correlation matrix shape: {corr_matrix.shape}")
        print(f"Mean absolute correlation: {corr_matrix.abs().mean().mean():.3f}")

        # Find highly correlated pairs (>0.85 threshold from MVP plan)
        correlation_threshold = 0.85
        high_corr_pairs = []

        for i_col in range(len(corr_matrix.columns)):
            for j in range(i_col+1, len(corr_matrix.columns)):
                corr_val = abs(corr_matrix.iloc[i_col, j])
                if corr_val > correlation_threshold:
                    high_corr_pairs.append((
                        corr_matrix.columns[i_col], 
                        corr_matrix.columns[j], 
                        corr_val
                    ))

        print(f"\nFound {len(high_corr_pairs)} pairs with correlation > {correlation_threshold}")

        # Show top 10 highest correlations
        if high_corr_pairs:
            high_corr_df = pd.DataFrame(high_corr_pairs, columns=['Index1', 'Index2', 'Correlation'])
            high_corr_df = high_corr_df.sort_values('Correlation', ascending=False)
            print("\nTop 10 highest correlations:")
            print(high_corr_df.head(10))

    else:
        corr_matrix = pd.DataFrame()
        high_corr_pairs = []
        high_corr_df = pd.DataFrame()
        print("Cannot calculate correlations - no index data available")

    return corr_matrix, correlation_threshold


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Hierarchical Clustering of Indices

    Using hierarchical clustering to identify functional groups of acoustic indices.
    This helps us understand which indices measure similar acoustic properties.
    """
    )
    return


@app.cell
def _(corr_matrix, fcluster, linkage, np, pd, squareform):
    if not corr_matrix.empty:
        # Perform hierarchical clustering on correlation matrix
        # Convert correlation to distance (1 - |correlation|)
        distance_matrix = 1 - corr_matrix.abs()

        # Convert to condensed distance matrix for linkage
        condensed_distances = squareform(distance_matrix)

        # Perform hierarchical clustering
        linkage_matrix = linkage(condensed_distances, method='ward')

        # Determine optimal number of clusters
        # Try different numbers and see where we get reasonable cluster sizes
        n_clusters_range = range(5, 25)
        cluster_sizes = {}

        for n_clusters in n_clusters_range:
            clusters = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
            cluster_counts = pd.Series(clusters).value_counts().sort_values(ascending=False)
            cluster_sizes[n_clusters] = {
                'largest_cluster': cluster_counts.iloc[0],
                'smallest_cluster': cluster_counts.iloc[-1],
                'mean_size': cluster_counts.mean(),
                'n_singletons': (cluster_counts == 1).sum()
            }

        # Choose number of clusters (aiming for 15-20 final indices)
        target_clusters = 18  # This should give us ~15-20 representative indices
        cluster_labels = fcluster(linkage_matrix, target_clusters, criterion='maxclust')

        # Create cluster assignment dataframe
        cluster_df = pd.DataFrame({
            'index': corr_matrix.columns,
            'cluster': cluster_labels
        })

        cluster_summary = cluster_df.groupby('cluster').size().sort_values(ascending=False)
        print(f"Clustering with {target_clusters} clusters:")
        print(f"Cluster sizes: {cluster_summary.values}")
        print(f"Largest cluster: {cluster_summary.iloc[0]} indices")
        print(f"Smallest cluster: {cluster_summary.iloc[-1]} indices")

    else:
        distance_matrix = pd.DataFrame()
        linkage_matrix = np.array([])
        cluster_labels = np.array([])
        cluster_df = pd.DataFrame()
        cluster_summary = pd.Series()
        print("Cannot perform clustering - no correlation data available")

    return (
        cluster_df,
        cluster_summary,
        distance_matrix,
        linkage_matrix,
        target_clusters,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Index Reduction Strategy

    Selecting representative indices from each cluster based on:
    1. **Ecological relevance**: Choose indices with known biological significance
    2. **Vessel noise robustness**: Prefer indices less affected by vessel presence
    3. **Cluster centrality**: Select indices most representative of their cluster
    """
    )
    return


@app.cell
def _(
    acoustic_index_cols,
    cluster_df,
    corr_matrix,
    df_aligned,
    df_indices,
    np,
    pd,
    target_clusters,
):
    if not cluster_df.empty and not df_aligned.empty:
        # For each cluster, select the most representative index
        selected_indices = []
        selection_rationale = {}

        for cluster_id in sorted(cluster_df['cluster'].unique()):
            cluster_indices = cluster_df[cluster_df['cluster'] == cluster_id]['index'].tolist()

            if len(cluster_indices) == 1:
                # Single index in cluster - automatically selected
                selected_idx = cluster_indices[0]
                selection_rationale[selected_idx] = f"Only index in cluster {cluster_id}"
            else:
                # Multiple indices - need to choose representative
                # Calculate mean correlation with other indices in cluster
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
                    f"({len(cluster_indices)} indices, r̄={cluster_corr_means[best_idx_pos]:.3f})"
                )

            selected_indices.append(selected_idx)

        print(f"Selected {len(selected_indices)} representative indices from {target_clusters} clusters")
        print("\nSelected indices and rationale:")
        for idx in selected_indices[:10]:  # Show first 10
            print(f"  {idx}: {selection_rationale[idx]}")
        if len(selected_indices) > 10:
            print(f"  ... and {len(selected_indices) - 10} more")

        # Create reduced dataset
        df_indices_reduced = df_indices[selected_indices].copy()

        print(f"\nReduced from {len(acoustic_index_cols)} to {len(selected_indices)} indices")
        print(f"Reduction ratio: {len(selected_indices)/len(acoustic_index_cols):.2f}")

    else:
        selected_indices = []
        selection_rationale = {}
        df_indices_reduced = pd.DataFrame()
        print("Cannot perform index reduction - no clustering data available")

    return df_indices_reduced, selected_indices, selection_rationale


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Principal Component Analysis

    Performing PCA on the full index set to understand the major axes of acoustic variation
    and validate our clustering-based reduction approach.
    """
    )
    return


@app.cell
def _(PCA, StandardScaler, df_indices, df_indices_reduced, np):
    if not df_indices.empty:
        # Standardize the data for PCA
        scaler_full = StandardScaler()
        indices_scaled = scaler_full.fit_transform(df_indices.dropna())

        # Perform PCA on full index set
        pca_full = PCA()
        pca_components_full = pca_full.fit_transform(indices_scaled)

        # Calculate cumulative explained variance
        cumvar_full = np.cumsum(pca_full.explained_variance_ratio_)

        # Find number of components for 80%, 90%, 95% variance
        n_80 = np.argmax(cumvar_full >= 0.80) + 1
        n_90 = np.argmax(cumvar_full >= 0.90) + 1
        n_95 = np.argmax(cumvar_full >= 0.95) + 1

        print(f"PCA Results - Full Index Set ({len(df_indices.columns)} indices):")
        print(f"  Components for 80% variance: {n_80}")
        print(f"  Components for 90% variance: {n_90}")
        print(f"  Components for 95% variance: {n_95}")
        print(f"  First 5 components explain: {cumvar_full[4]:.1%} of variance")
        print(f"  First 10 components explain: {cumvar_full[9]:.1%} of variance")

        # PCA on reduced set for comparison
        if not df_indices_reduced.empty:
            scaler_reduced = StandardScaler()
            indices_reduced_scaled = scaler_reduced.fit_transform(df_indices_reduced.dropna())

            pca_reduced = PCA()
            pca_components_reduced = pca_reduced.fit_transform(indices_reduced_scaled)
            cumvar_reduced = np.cumsum(pca_reduced.explained_variance_ratio_)

            n_80_reduced = np.argmax(cumvar_reduced >= 0.80) + 1
            n_90_reduced = np.argmax(cumvar_reduced >= 0.90) + 1

            print(f"\nPCA Results - Reduced Index Set ({len(df_indices_reduced.columns)} indices):")
            print(f"  Components for 80% variance: {n_80_reduced}")
            print(f"  Components for 90% variance: {n_90_reduced}")
            print(f"  First 5 components explain: {cumvar_reduced[4]:.1%} of variance")

            # Compare variance preservation
            variance_preservation = cumvar_reduced[min(len(cumvar_reduced)-1, n_90-1)]
            print(f"  Variance preserved at {n_90} components: {variance_preservation:.1%}")

    else:
        pca_full = None
        pca_reduced = None
        print("Cannot perform PCA - no index data available")

    return cumvar_full, n_80, n_90, pca_components_full, pca_full


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Variance Inflation Factor Analysis

    Calculating VIF to assess multicollinearity in both the full and reduced index sets.
    High VIF values (>10) indicate problematic multicollinearity.
    """
    )
    return


@app.cell
def _(df_indices, df_indices_reduced, np, pd, variance_inflation_factor):
    def calculate_vif(df_data):
        """Calculate VIF for all variables in dataframe"""
        if df_data.empty:
            return pd.DataFrame()

        # Remove any rows with missing values
        df_clean = df_data.dropna()

        if df_clean.empty or len(df_clean.columns) < 2:
            return pd.DataFrame()

        try:
            vif_data = pd.DataFrame()
            vif_data["Variable"] = df_clean.columns
            vif_data["VIF"] = [
                variance_inflation_factor(df_clean.values, i) 
                for i in range(len(df_clean.columns))
            ]
            return vif_data.sort_values('VIF', ascending=False)
        except Exception as e:
            print(f"Error calculating VIF: {e}")
            return pd.DataFrame()

    # Calculate VIF for full index set (sample if too large)
    if not df_indices.empty:
        # If too many indices, sample for VIF calculation (VIF is computationally expensive)
        if len(df_indices.columns) > 30:
            print(f"Sampling 30 indices from {len(df_indices.columns)} for VIF calculation...")
            sample_indices = np.random.choice(df_indices.columns, 30, replace=False)
            vif_full = calculate_vif(df_indices[sample_indices])
            print("VIF calculated on sample of indices")
        else:
            vif_full = calculate_vif(df_indices)
            print("VIF calculated on full index set")

        if not vif_full.empty:
            print(f"\nFull Index Set VIF Summary:")
            print(f"  Mean VIF: {vif_full['VIF'].mean():.2f}")
            print(f"  Max VIF: {vif_full['VIF'].max():.2f}")
            print(f"  Variables with VIF > 10: {(vif_full['VIF'] > 10).sum()}")
            print(f"  Variables with VIF > 5: {(vif_full['VIF'] > 5).sum()}")
    else:
        vif_full = pd.DataFrame()

    # Calculate VIF for reduced set
    if not df_indices_reduced.empty:
        vif_reduced = calculate_vif(df_indices_reduced)

        if not vif_reduced.empty:
            print(f"\nReduced Index Set VIF Summary:")
            print(f"  Mean VIF: {vif_reduced['VIF'].mean():.2f}")
            print(f"  Max VIF: {vif_reduced['VIF'].max():.2f}")
            print(f"  Variables with VIF > 10: {(vif_reduced['VIF'] > 10).sum()}")
            print(f"  Variables with VIF > 5: {(vif_reduced['VIF'] > 5).sum()}")

            # Show highest VIF values
            print(f"\nTop 5 highest VIF values in reduced set:")
            print(vif_reduced.head())

    else:
        vif_reduced = pd.DataFrame()

    return (vif_reduced,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Index-Environment Relationships

    Analyzing how acoustic indices correlate with environmental variables and respond to vessel presence.
    This helps validate the ecological relevance of our selected indices.
    """
    )
    return


@app.cell
def _(data_dir, df_indices_reduced, np, pd, selected_indices, stats):
    # Load detection data for vessel analysis
    detection_file = data_dir / "02_detections_aligned_2021.parquet"
    
    env_corr_matrix = pd.DataFrame()  # Placeholder since we're not doing env analysis here
    vessel_stats = {}
    
    if detection_file.exists() and not df_indices_reduced.empty:
        df_detections = pd.read_parquet(detection_file)
        print(f"Loaded detection data for vessel analysis: {df_detections.shape}")
        
        # Vessel impact analysis
        if 'Vessel' in df_detections.columns:
            print(f"\n--- Vessel Impact Analysis ---")
            
            # Merge vessel data with indices data on datetime and station
            vessel_indices_combined = pd.merge(
                df_indices_reduced.reset_index(),
                df_detections[['datetime', 'station', 'Vessel']],
                on=['datetime', 'station'],
                how='left'
            ).set_index(df_indices_reduced.index)
            
            # Create binary vessel presence indicator
            vessel_present_binary = (vessel_indices_combined['Vessel'] > 0).astype(int)
            print(f"Vessel presence periods: {vessel_present_binary.sum()} / {len(vessel_present_binary)} ({vessel_present_binary.mean():.1%})")

            for idx in selected_indices:
                if idx in vessel_indices_combined.columns:
                    # Compare index values during vessel vs non-vessel periods
                    vessel_present_vals = vessel_indices_combined[vessel_present_binary == 1][idx].dropna()
                    vessel_absent_vals = vessel_indices_combined[vessel_present_binary == 0][idx].dropna()

                    if len(vessel_present_vals) > 10 and len(vessel_absent_vals) > 10:
                        # Calculate effect size (Cohen's d)
                        pooled_std = np.sqrt(
                            ((len(vessel_present_vals) - 1) * vessel_present_vals.var() + 
                             (len(vessel_absent_vals) - 1) * vessel_absent_vals.var()) /
                            (len(vessel_present_vals) + len(vessel_absent_vals) - 2)
                        )

                        if pooled_std > 0:
                            cohens_d = (vessel_present_vals.mean() - vessel_absent_vals.mean()) / pooled_std

                            # Statistical test
                            t_stat, p_val = stats.ttest_ind(vessel_present_vals, vessel_absent_vals)

                            vessel_stats[idx] = {
                                'mean_vessel': vessel_present_vals.mean(),
                                'mean_no_vessel': vessel_absent_vals.mean(),
                                'cohens_d': cohens_d,
                                'p_value': p_val,
                                'effect_magnitude': 'large' if abs(cohens_d) > 0.8 else 
                                                  'medium' if abs(cohens_d) > 0.5 else 'small'
                            }

            # Summary of vessel impacts
            if vessel_stats:
                print(f"Vessel impact analysis completed for {len(vessel_stats)} indices:")
                large_effects = [idx for idx, stats_dict in vessel_stats.items() 
                               if abs(stats_dict['cohens_d']) > 0.8]
                medium_effects = [idx for idx, stats_dict in vessel_stats.items() 
                                if 0.5 < abs(stats_dict['cohens_d']) <= 0.8]

                print(f"  Large effects (|d| > 0.8): {len(large_effects)}")
                print(f"  Medium effects (0.5 < |d| ≤ 0.8): {len(medium_effects)}")

                # Show most vessel-sensitive indices
                vessel_df = pd.DataFrame(vessel_stats).T
                vessel_df_sorted = vessel_df.reindex(vessel_df['cohens_d'].abs().sort_values(ascending=False).index)
                print(f"\nMost vessel-sensitive indices:")
                print(vessel_df_sorted[['cohens_d', 'effect_magnitude', 'p_value']].head())

        else:
            print("Vessel data not available in detection dataset")

    else:
        if not detection_file.exists():
            print(f"Detection file not found: {detection_file}")
        print("Vessel impact analysis skipped - focusing on index reduction")

    return env_corr_matrix, vessel_stats


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Static Plots Generation

    Creating publication-ready plots for the dashboard and documentation:

    1. **Correlation heatmap** with hierarchical clustering dendrogram
    2. **PCA biplot** with index loadings  
    3. **VIF comparison** before/after reduction
    4. **Index response to vessel presence** (box plots)
    5. **Seasonal patterns** for key retained indices
    6. **Station-wise index behavior** comparison
    """
    )
    return


@app.cell
def _(
    cluster_summary,
    corr_matrix,
    cumvar_full,
    output_dir_plots,
    pca_full,
    plt,
    sns,
    vif_reduced,
):
    # Plot 1: Correlation heatmap with clustering dendrogram
    if not corr_matrix.empty:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Acoustic Index Analysis Results', fontsize=16, y=0.95)

        # Correlation heatmap (subset for readability)
        n_show = min(20, len(corr_matrix))  # Show max 20x20 for readability
        corr_subset = corr_matrix.iloc[:n_show, :n_show]

        sns.heatmap(corr_subset, 
                   annot=False, 
                   cmap='RdBu_r', 
                   center=0,
                   square=True,
                   ax=axes[0,0])
        axes[0,0].set_title(f'Correlation Matrix (First {n_show} indices)')
        axes[0,0].tick_params(axis='both', which='major', labelsize=8)

        # PCA explained variance plot
        if pca_full is not None:
            axes[0,1].plot(range(1, min(21, len(cumvar_full)+1)), 
                          cumvar_full[:min(20, len(cumvar_full))], 
                          'bo-', linewidth=2)
            axes[0,1].axhline(y=0.8, color='r', linestyle='--', alpha=0.7, label='80% variance')
            axes[0,1].axhline(y=0.9, color='orange', linestyle='--', alpha=0.7, label='90% variance')
            axes[0,1].set_xlabel('Principal Component')
            axes[0,1].set_ylabel('Cumulative Explained Variance')
            axes[0,1].set_title('PCA Explained Variance')
            axes[0,1].legend()
            axes[0,1].grid(True, alpha=0.3)

        # Cluster sizes bar plot
        if not cluster_summary.empty:
            cluster_summary.head(10).plot(kind='bar', ax=axes[1,0])
            axes[1,0].set_title('Cluster Sizes (Top 10 clusters)')
            axes[1,0].set_xlabel('Cluster ID')
            axes[1,0].set_ylabel('Number of Indices')
            axes[1,0].tick_params(axis='x', rotation=0)

        # VIF comparison
        if not vif_reduced.empty:
            vif_data_plot = vif_reduced.head(10)  # Top 10 highest VIF
            axes[1,1].barh(range(len(vif_data_plot)), vif_data_plot['VIF'])
            axes[1,1].set_yticks(range(len(vif_data_plot)))
            axes[1,1].set_yticklabels(vif_data_plot['Variable'], fontsize=8)
            axes[1,1].set_xlabel('VIF Value')
            axes[1,1].set_title('VIF Values (Reduced Index Set)')
            axes[1,1].axvline(x=10, color='r', linestyle='--', alpha=0.7, label='VIF=10')
            axes[1,1].axvline(x=5, color='orange', linestyle='--', alpha=0.7, label='VIF=5')
            axes[1,1].legend()

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'index_analysis_overview.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Saved: index_analysis_overview.png")

    return


@app.cell
def _(
    corr_matrix,
    dendrogram,
    distance_matrix,
    linkage_matrix,
    np,
    output_dir_plots,
    plt,
    sns,
):
    # Plot 2: Detailed correlation heatmap with clustering
    if not corr_matrix.empty and not distance_matrix.empty:
        # Create clustered correlation matrix
        if len(linkage_matrix) > 0:
            plt.figure(figsize=(12, 10))

            # Create dendrogram to get order
            dendro = dendrogram(linkage_matrix, 
                              labels=corr_matrix.columns,
                              no_plot=True)
            dendro_order = dendro['leaves']

            # Reorder correlation matrix
            corr_ordered = corr_matrix.iloc[dendro_order, dendro_order]

            # Plot heatmap
            mask = np.triu(np.ones_like(corr_ordered, dtype=bool))
            sns.heatmap(corr_ordered, 
                       mask=mask,
                       annot=False, 
                       cmap='RdBu_r', 
                       center=0,
                       square=True,
                       cbar_kws={"shrink": .8})

            plt.title('Clustered Correlation Matrix (Full Index Set)')
            plt.xticks(rotation=90, fontsize=6)
            plt.yticks(rotation=0, fontsize=6)
            plt.tight_layout()
            plt.savefig(output_dir_plots / 'correlation_matrix_clustered.png', 
                       dpi=300, bbox_inches='tight')
            plt.show()

            print(f"Saved: correlation_matrix_clustered.png")

    return


@app.cell
def _(df_indices, output_dir_plots, pca_components_full, pca_full, plt):
    # Plot 3: PCA Biplot
    if pca_full is not None and not df_indices.empty:
        plt.figure(figsize=(12, 8))

        # Plot first two principal components
        plt.scatter(pca_components_full[:, 0], pca_components_full[:, 1], 
                   alpha=0.6, s=20)

        # Add loading vectors for first few indices
        feature_names = df_indices.columns[:min(20, len(df_indices.columns))]  # Show first 20
        for i, feature in enumerate(feature_names):
            if i < len(pca_full.components_[0]):
                plt.arrow(0, 0, 
                         pca_full.components_[0][i] * 3, 
                         pca_full.components_[1][i] * 3,
                         head_width=0.05, head_length=0.05, 
                         fc='red', ec='red', alpha=0.7)
                plt.text(pca_full.components_[0][i] * 3.2, 
                        pca_full.components_[1][i] * 3.2,
                        feature, fontsize=8, ha='center', va='center')

        plt.xlabel(f'PC1 ({pca_full.explained_variance_ratio_[0]:.1%} variance)')
        plt.ylabel(f'PC2 ({pca_full.explained_variance_ratio_[1]:.1%} variance)')
        plt.title('PCA Biplot - Acoustic Indices')
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'pca_biplot.png', dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Saved: pca_biplot.png")

    return


@app.cell
def _(df_aligned, np, output_dir_plots, pd, plt, vessel_stats):
    # Plot 4: Vessel impact analysis
    if vessel_stats and not df_aligned.empty:
        # Create vessel impact visualization
        fig, axes_vessel = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Vessel Impact on Acoustic Indices', fontsize=16)

        # Get top vessel-sensitive indices
        vessel_df_plot = pd.DataFrame(vessel_stats).T
        vessel_df_plot = vessel_df_plot.reindex(
            vessel_df_plot['cohens_d'].abs().sort_values(ascending=False).index
        )

        # Plot 1: Effect sizes
        top_indices = vessel_df_plot.head(10)
        y_pos = range(len(top_indices))

        bars = axes_vessel[0,0].barh(y_pos, top_indices['cohens_d'], 
                                    color=['red' if abs(d) > 0.8 else 'orange' if abs(d) > 0.5 else 'blue' 
                                          for d in top_indices['cohens_d']])
        axes_vessel[0,0].set_yticks(y_pos)
        axes_vessel[0,0].set_yticklabels([idx[:15] + '...' if len(idx) > 15 else idx 
                                        for idx in top_indices.index], fontsize=8)
        axes_vessel[0,0].set_xlabel("Cohen's d (Effect Size)")
        axes_vessel[0,0].set_title('Top 10 Vessel-Sensitive Indices')
        axes_vessel[0,0].axvline(x=0, color='black', linestyle='-', alpha=0.3)
        axes_vessel[0,0].axvline(x=0.5, color='orange', linestyle='--', alpha=0.7, label='Medium effect')
        axes_vessel[0,0].axvline(x=-0.5, color='orange', linestyle='--', alpha=0.7)
        axes_vessel[0,0].axvline(x=0.8, color='red', linestyle='--', alpha=0.7, label='Large effect')
        axes_vessel[0,0].axvline(x=-0.8, color='red', linestyle='--', alpha=0.7)
        axes_vessel[0,0].legend()

        # Plot 2: P-values
        axes_vessel[0,1].scatter(top_indices['cohens_d'], -np.log10(top_indices['p_value']))
        axes_vessel[0,1].set_xlabel("Cohen's d")
        axes_vessel[0,1].set_ylabel("-log10(p-value)")
        axes_vessel[0,1].set_title('Effect Size vs Statistical Significance')
        axes_vessel[0,1].axhline(y=-np.log10(0.05), color='red', linestyle='--', alpha=0.7, label='p=0.05')
        axes_vessel[0,1].axvline(x=0, color='black', linestyle='-', alpha=0.3)
        axes_vessel[0,1].legend()

        # Plot 3: Box plot for most vessel-sensitive index
        if len(vessel_df_plot) > 0:
            most_sensitive_idx = vessel_df_plot.index[0]
            if most_sensitive_idx in df_aligned.columns:
                vessel_present_data = df_aligned[df_aligned['vessel_present'] == 1][most_sensitive_idx]
                vessel_absent_data = df_aligned[df_aligned['vessel_present'] == 0][most_sensitive_idx]

                box_data = [vessel_absent_data.dropna(), vessel_present_data.dropna()]
                axes_vessel[1,0].boxplot(box_data, labels=['No Vessel', 'Vessel Present'])
                axes_vessel[1,0].set_ylabel('Index Value')
                axes_vessel[1,0].set_title(f'Most Vessel-Sensitive Index\n{most_sensitive_idx[:20]}...')

        # Plot 4: Effect size distribution
        effect_sizes = [abs(stats_dict['cohens_d']) for stats_dict in vessel_stats.values()]
        axes_vessel[1,1].hist(effect_sizes, bins=15, alpha=0.7, edgecolor='black')
        axes_vessel[1,1].axvline(x=0.5, color='orange', linestyle='--', alpha=0.7, label='Medium effect')
        axes_vessel[1,1].axvline(x=0.8, color='red', linestyle='--', alpha=0.7, label='Large effect')
        axes_vessel[1,1].set_xlabel('|Effect Size| (|Cohen\'s d|)')
        axes_vessel[1,1].set_ylabel('Frequency')
        axes_vessel[1,1].set_title('Distribution of Vessel Effect Sizes')
        axes_vessel[1,1].legend()

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'vessel_impact_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Saved: vessel_impact_analysis.png")

    return


@app.cell
def _(env_corr_matrix, output_dir_plots, plt, sns):
    # Plot 5: Environmental correlations heatmap
    if not env_corr_matrix.empty:
        plt.figure(figsize=(10, 8))

        # Create heatmap of index-environment correlations
        sns.heatmap(env_corr_matrix.T, 
                   annot=True, 
                   cmap='RdBu_r', 
                   center=0,
                   cbar_kws={"shrink": .8})

        plt.title('Index-Environment Correlations')
        plt.xlabel('Acoustic Indices')
        plt.ylabel('Environmental Variables')
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.yticks(rotation=0)

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'index_environment_correlations.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()

        print(f"Saved: index_environment_correlations.png")

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Results Summary and Output Saving

    Summarizing the index reduction results and saving the reduced dataset for use in downstream analyses.
    """
    )
    return


@app.cell
def _(
    acoustic_index_cols,
    correlation_threshold,
    cumvar_full,
    n_80,
    n_90,
    np,
    pca_full,
    pd,
    selected_indices,
    selection_rationale,
    target_clusters,
    vessel_stats,
    vif_reduced,
):
    # Create comprehensive summary
    summary_results = {
        'analysis_date': pd.Timestamp.now().isoformat(),
        'original_index_count': len(acoustic_index_cols) if acoustic_index_cols else 0,
        'reduced_index_count': len(selected_indices) if selected_indices else 0,
        'reduction_ratio': len(selected_indices) / len(acoustic_index_cols) if acoustic_index_cols and selected_indices else 0,
        'correlation_threshold': correlation_threshold,
        'target_clusters': target_clusters,
        'selected_indices': selected_indices,
        'selection_rationale': selection_rationale
    }

    # Add PCA results if available
    if pca_full is not None:
        summary_results.update({
            'pca_components_80pct': n_80,
            'pca_components_90pct': n_90,
            'first_5_components_variance': cumvar_full[4] if len(cumvar_full) > 4 else None,
            'first_10_components_variance': cumvar_full[9] if len(cumvar_full) > 9 else None
        })

    # Add VIF results if available
    if not vif_reduced.empty:
        summary_results.update({
            'mean_vif_reduced': vif_reduced['VIF'].mean(),
            'max_vif_reduced': vif_reduced['VIF'].max(),
            'high_vif_count': (vif_reduced['VIF'] > 10).sum()
        })

    # Add vessel impact results if available
    if vessel_stats:
        effect_sizes = [abs(stats_dict['cohens_d']) for stats_dict in vessel_stats.values()]
        summary_results.update({
            'vessel_analysis_indices': len(vessel_stats),
            'large_vessel_effects': sum(1 for e in effect_sizes if e > 0.8),
            'medium_vessel_effects': sum(1 for e in effect_sizes if 0.5 < e <= 0.8),
            'mean_vessel_effect_size': np.mean(effect_sizes)
        })

    print("=== ACOUSTIC INDEX REDUCTION SUMMARY ===")
    print(f"Analysis completed: {summary_results['analysis_date']}")
    print(f"Original indices: {summary_results['original_index_count']}")
    print(f"Reduced indices: {summary_results['reduced_index_count']}")
    print(f"Reduction ratio: {summary_results['reduction_ratio']:.2f}")

    if pca_full is not None:
        print(f"\nPCA Results:")
        print(f"  Components for 90% variance: {summary_results.get('pca_components_90pct', 'N/A')}")
        print(f"  First 10 components variance: {summary_results.get('first_10_components_variance', 'N/A'):.1%}")

    if not vif_reduced.empty:
        print(f"\nVIF Results (reduced set):")
        print(f"  Mean VIF: {summary_results.get('mean_vif_reduced', 'N/A'):.2f}")
        print(f"  Max VIF: {summary_results.get('max_vif_reduced', 'N/A'):.2f}")
        print(f"  High VIF count (>10): {summary_results.get('high_vif_count', 'N/A')}")

    if vessel_stats:
        print(f"\nVessel Impact Analysis:")
        print(f"  Indices analyzed: {summary_results.get('vessel_analysis_indices', 'N/A')}")
        print(f"  Large effects: {summary_results.get('large_vessel_effects', 'N/A')}")
        print(f"  Medium effects: {summary_results.get('medium_vessel_effects', 'N/A')}")

    return (summary_results,)


@app.cell
def _(
    Path,
    acoustic_index_cols,
    df_acoustic_indices,
    df_indices_reduced,
    np,
    output_dir_plots,
    pd,
    selected_indices,
    selection_rationale,
    summary_results,
):
    # Save the reduced dataset and analysis results
    output_data_dir = Path("../../data/processed")
    output_data_dir.mkdir(parents=True, exist_ok=True)

    if not df_indices_reduced.empty:
        # Save reduced indices dataset with identifiers
        reduced_with_ids = pd.concat([
            df_acoustic_indices[['datetime', 'station', 'year']],
            df_indices_reduced
        ], axis=1)
        
        reduced_with_ids.to_parquet(output_data_dir / "03_reduced_acoustic_indices.parquet")
        print(f"Saved reduced acoustic indices: {output_data_dir / '03_reduced_acoustic_indices.parquet'}")
        print(f"  Shape: {reduced_with_ids.shape}")
        print(f"  Columns: {len(selected_indices)} indices + 3 identifiers")

    # Save summary results as JSON
    import json
    with open(output_data_dir / "03_reduction_summary.json", 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        json_safe_summary = {}
        for key, value in summary_results.items():
            if isinstance(value, (np.integer, np.floating)):
                json_safe_summary[key] = value.item()
            elif isinstance(value, np.ndarray):
                json_safe_summary[key] = value.tolist()
            else:
                json_safe_summary[key] = value

        json.dump(json_safe_summary, f, indent=2, default=str)

    print(f"Saved analysis summary: {output_data_dir / '03_reduction_summary.json'}")

    # Save selected indices list as text file for reference
    with open(output_data_dir / "03_selected_indices.txt", 'w') as f:
        f.write("Selected Acoustic Indices for Analysis\n")
        f.write("=====================================\n\n")
        f.write(f"Reduced from {len(acoustic_index_cols)} to {len(selected_indices)} indices\n")
        f.write(f"Reduction ratio: {len(selected_indices)/len(acoustic_index_cols):.2f}\n\n")
        
        for i, idx in enumerate(selected_indices, 1):
            f.write(f"{i:2d}. {idx}\n")
            if idx in selection_rationale:
                f.write(f"    Rationale: {selection_rationale[idx]}\n\n")

    print(f"Saved selected indices list: {output_data_dir / '03_selected_indices.txt'}")

    print(f"\n=== OUTPUT FILES SAVED ===")
    print(f"Data files saved to: {output_data_dir}")
    print(f"Plot files saved to: {output_dir_plots}")
    print(f"\nFor downstream analysis, use:")
    print(f"  - 03_reduced_acoustic_indices.parquet (reduced indices with identifiers)")
    print(f"  - 02_detections_aligned_2021.parquet (for fish calling data)")
    print(f"  - 02_environmental_aligned_2021.parquet (for environmental variables)")
    print(f"  - 02_temporal_features_2021.parquet (for temporal features)")

    return


if __name__ == "__main__":
    app.run()
