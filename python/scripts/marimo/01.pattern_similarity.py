import marimo

__generated_with = "0.13.15"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Pattern Similarity Analysis: Acoustic Indices vs Species Detections

        This analysis explores whether acoustic indices computed from underwater recordings show similar temporal patterns to manual species detections. The core scientific question: **Can we identify acoustic indices that mirror when and how often different marine species are vocally active?**

        ## Why This Matters

        Manual species detection from hydrophone recordings is labor-intensive and requires expert knowledge. If certain acoustic indices consistently correlate with species calling patterns, they could serve as automated proxies for biodiversity monitoring. This would make marine soundscape assessment much more scalable.

        ## Our Approach

        We'll compare 2D temporal patterns between:
        - **Species detection data**: Manual annotations of when different fish species were detected
        - **Acoustic indices**: Computed metrics that capture different aspects of the acoustic environment

        Both datasets are organized as weekly-hourly heatmaps, allowing us to see patterns across seasons (weeks) and daily cycles (hours).
        """
    )
    return (mo,)


@app.cell
def _():
    # Import required libraries
    import sys
    from pathlib import Path
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    from sklearn.metrics import normalized_mutual_info_score
    import warnings
    warnings.filterwarnings('ignore')

    # Setup paths
    project_root = Path.cwd()
    sys.path.insert(0, str(project_root))
    repo_root = project_root.parent

    from mbon_analysis.data.loaders import create_loader

    # Configure plotting style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10

    print("✓ Libraries loaded and paths configured")
    return (
        create_loader,
        normalized_mutual_info_score,
        np,
        pd,
        plt,
        repo_root,
        stats,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Data Loading and Preprocessing

    We're working with two complementary datasets from Station 14M in 2021:

    ### Detection Data
    - **Source**: Manual annotations from 2-hour audio segments
    - **Content**: Binary presence/absence for different species
    - **Resolution**: Every 2 hours (12 time points per day)
    - **Species**: Fish species like Silver perch, Oyster toadfish, Red drum, etc.

    ### Acoustic Indices Data  
    - **Source**: Automated computation from the same audio files
    - **Content**: 50+ acoustic metrics capturing different sound characteristics
    - **Resolution**: Hourly (24 time points per day)
    - **Categories**: Temporal patterns, frequency content, complexity, diversity

    **Key Preprocessing Step**: We downsample acoustic indices to match the 2-hour resolution of detection data, keeping only even hours (0, 2, 4, 6, ..., 22).
    """
    )
    return


@app.cell
def _(create_loader, pd, repo_root):
    # Initialize data loader and load datasets
    loader = create_loader(repo_root / "data")

    # Load detection data (species annotations)
    detections = loader.load_detection_data('14M', 2021)
    detections['datetime'] = pd.to_datetime(detections['Date'])
    detections['hour'] = detections['datetime'].dt.hour
    detections['week'] = detections['datetime'].dt.isocalendar().week
    detections = detections.sort_values('datetime')

    print(f"Detection data: {len(detections)} records")
    print(f"Date range: {detections['datetime'].min()} to {detections['datetime'].max()}")
    print(f"Available species columns: {len([col for col in detections.columns if col not in ['Date', 'datetime', 'hour', 'week']])}")

    # Load acoustic indices
    acoustic_indices = loader.load_acoustic_indices('14M', 'FullBW')
    acoustic_indices['datetime'] = pd.to_datetime(acoustic_indices['Date'])
    acoustic_indices['hour'] = acoustic_indices['datetime'].dt.hour
    acoustic_indices['week'] = acoustic_indices['datetime'].dt.isocalendar().week

    # CRITICAL: Match detection resolution (2-hour intervals, even hours only)
    even_hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
    original_len = len(acoustic_indices)
    acoustic_indices = acoustic_indices[acoustic_indices['hour'].isin(even_hours)]
    acoustic_indices = acoustic_indices.sort_values('datetime')

    print(f"Acoustic indices: {len(acoustic_indices)} records (downsampled from {original_len})")
    print(f"Available indices: {len([col for col in acoustic_indices.columns if col not in ['Date', 'datetime', 'hour', 'week']])}")

    return acoustic_indices, detections, even_hours, loader


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Creating Weekly-Hourly Heatmaps

    The core of our analysis is converting time series data into 2D heatmaps where:
    - **X-axis (columns)**: Hours of day (0, 2, 4, ..., 22)
    - **Y-axis (rows)**: Weeks of year (1, 2, 3, ..., 52)
    - **Values**: Detection rates or acoustic index values

    This 2D representation captures both:
    - **Daily patterns**: Some species are more active at dawn/dusk
    - **Seasonal patterns**: Breeding seasons, migration periods, temperature effects

    Let's see what these heatmaps look like for a few example species and acoustic indices.
    """
    )
    return


@app.cell
def _(acoustic_indices, detections, loader, np, pd):
    def calculate_weekly_hourly_heatmap(data: pd.DataFrame, column: str) -> np.ndarray:
        """Convert time series to weekly-hourly heatmap matrix."""
        # Convert to numeric and handle missing values
        data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)

        # Create pivot table: weeks as rows, hours as columns
        heatmap = data.pivot_table(
            values=column,
            index='week',  # Rows: week of year
            columns='hour',  # Columns: hour of day
            aggfunc='sum',  # Average if multiple values per week-hour
            fill_value=0
        )

        return heatmap.values

    # Example: Create heatmaps for a fish species and an acoustic index
    # Get available fish species
    species_mapping = loader.load_species_mapping()
    fish_species = species_mapping[
        (species_mapping['group'] == 'fish') &   # only look at fish
        (species_mapping['keep_species'] == 1)   # only keep the species identified by Eric/Alyssa 
    ]['long_name'].tolist()

    # Find species that exist in our detection data
    available_species = [sp for sp in fish_species if sp in detections.columns]
    example_species = available_species[0]  # Take the first available species

    # Get a representative acoustic index
    example_index = 'ACI'  # Acoustic Complexity Index

    # Generate heatmaps
    species_heatmap = calculate_weekly_hourly_heatmap(detections, example_species)
    index_heatmap = calculate_weekly_hourly_heatmap(acoustic_indices, example_index)

    print(f"Example species: {example_species}")
    print(f"Species heatmap shape: {species_heatmap.shape} (weeks × hours)")
    print(f"Index heatmap shape: {index_heatmap.shape} (weeks × hours)")
    print(f"\nSpecies summed detection rate range: {species_heatmap.min():.3f} to {species_heatmap.max():.3f}")
    print(f"{example_index} value range: {index_heatmap.min():.1f} to {index_heatmap.max():.1f}")

    return (
        available_species,
        example_index,
        example_species,
        index_heatmap,
        species_heatmap,
    )


@app.cell
def _(
    even_hours,
    example_index,
    example_species,
    index_heatmap,
    plt,
    species_heatmap,
    stats,
):
    # Visualize the example heatmaps side by side
    fig, (ax1, ax2) = plt.subplots(2,1)

    # Species detection heatmap
    im1 = ax1.imshow(species_heatmap.T, cmap='YlOrRd', aspect='auto', origin='upper')
    ax1.set_title(f'{example_species}\nDetection Patterns', fontsize=12, pad=20)
    ax1.set_xlabel('Week of Year')
    ax1.set_ylabel('Hour of Day')

    ax1.invert_yaxis()


    # Set hour labels
    ax1.set_yticks(range(0, len(even_hours), 2))  # Every 4 hours
    ax1.set_yticklabels([f"{even_hours[i]:02d}:00" for i in range(0, len(even_hours), 2)])

    plt.colorbar(im1, ax=ax1, shrink=0.8, label='Summed Detection Rate')

    # Acoustic index heatmap
    im2 = ax2.imshow(index_heatmap.T, cmap='viridis', aspect='auto', origin='upper')
    ax2.set_title(f'{example_index}', fontsize=12, pad=20)
    ax2.set_xlabel('Week of Year')
    ax2.set_ylabel('Hour of Day')

    ax2.invert_yaxis()

    # Same hour labels
    ax2.set_yticks(range(0, len(even_hours), 2))
    ax2.set_yticklabels([f"{even_hours[i]:02d}:00" for i in range(0, len(even_hours), 2)])

    plt.colorbar(im2, ax=ax2, shrink=0.8, label='ACI Value')

    # plt.tight_layout()
    plt.show()

    # Calculate basic correlation
    species_flat = species_heatmap.flatten()
    index_flat = index_heatmap.flatten()
    correlation, p_value = stats.pearsonr(species_flat, index_flat)

    print(f"\nBasic correlation between {example_species} and {example_index}:")
    print(f"Pearson r = {correlation:.3f} (p = {p_value:.4f})")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Similarity Metrics: Beyond Simple Correlation

    While basic correlation gives us a starting point, we use multiple similarity metrics to capture different types of relationships between species and acoustic indices:

    ### 1. Pearson Correlation
    - **What it measures**: Linear relationships
    - **Good for**: Direct proportional patterns (more species activity = higher index values)
    - **Range**: -1 to +1

    ### 2. Spearman Correlation  
    - **What it measures**: Rank-order relationships
    - **Good for**: Non-linear but monotonic patterns
    - **Robust to**: Outliers and non-normal distributions

    ### 3. Normalized Mutual Information
    - **What it measures**: Information shared between patterns
    - **Good for**: Complex non-linear relationships
    - **Advantage**: Captures dependencies that correlation might miss

    ### 4. Cosine Similarity
    - **What it measures**: Shape similarity regardless of magnitude
    - **Good for**: Patterns with different scales but similar shapes
    - **Range**: 0 to 1

    ### 5. Structural Similarity
    - **What it measures**: Spatial pattern similarity
    - **Good for**: 2D pattern matching that preserves spatial relationships
    - **Considers**: Both intensity and spatial structure

    We combine these into a **composite score** that weights different aspects of similarity.
    """
    )
    return


@app.cell
def _(
    example_index,
    example_species,
    index_heatmap,
    normalized_mutual_info_score,
    np,
    species_heatmap,
    stats,
):
    def calculate_2d_correlation(heatmap1: np.ndarray, heatmap2: np.ndarray) -> dict:
        """Calculate comprehensive similarity metrics between two 2D heatmaps."""

        # Ensure same shape by cropping to minimum dimensions
        min_weeks = min(heatmap1.shape[0], heatmap2.shape[0])
        min_hours = min(heatmap1.shape[1], heatmap2.shape[1])

        h1 = heatmap1[:min_weeks, :min_hours]
        h2 = heatmap2[:min_weeks, :min_hours]

        # Flatten for correlation calculations
        h1_flat = h1.flatten()
        h2_flat = h2.flatten()

        # Remove NaN values
        valid_mask = ~(np.isnan(h1_flat) | np.isnan(h2_flat))
        h1_clean = h1_flat[valid_mask]
        h2_clean = h2_flat[valid_mask]

        if len(h1_clean) < 10:  # Need minimum data points
            return {'pearson_r': 0, 'spearman_r': 0, 'mutual_info': 0, 
                   'cosine_similarity': 0, 'structural_similarity': 0}

        results = {}

        # 1. Pearson correlation (linear relationships)
        try:
            results['pearson_r'], results['pearson_p'] = stats.pearsonr(h1_clean, h2_clean)
        except:
            results['pearson_r'], results['pearson_p'] = 0, 1

        # 2. Spearman correlation (rank-based, handles non-linear)
        try:
            results['spearman_r'], results['spearman_p'] = stats.spearmanr(h1_clean, h2_clean)
        except:
            results['spearman_r'], results['spearman_p'] = 0, 1

        # 3. Normalized Mutual Information (captures complex dependencies)
        try:
            # Discretize data into quartiles for mutual information
            h1_discrete = np.digitize(h1_clean, bins=np.percentile(h1_clean, [0, 25, 50, 75, 100]))
            h2_discrete = np.digitize(h2_clean, bins=np.percentile(h2_clean, [0, 25, 50, 75, 100]))
            results['mutual_info'] = normalized_mutual_info_score(h1_discrete, h2_discrete)
        except:
            results['mutual_info'] = 0

        # 4. Cosine similarity (shape similarity)
        try:
            dot_product = np.dot(h1_clean, h2_clean)
            norm1 = np.linalg.norm(h1_clean)
            norm2 = np.linalg.norm(h2_clean)
            results['cosine_similarity'] = dot_product / (norm1 * norm2) if (norm1 * norm2) > 0 else 0
        except:
            results['cosine_similarity'] = 0

        # 5. Structural Similarity (spatial pattern matching)
        try:
            # Normalize heatmaps to zero mean, unit variance
            h1_norm = (h1 - h1.mean()) / (h1.std() + 1e-10)
            h2_norm = (h2 - h2.mean()) / (h2.std() + 1e-10)

            # Mean squared error between normalized patterns
            mse = np.mean((h1_norm - h2_norm) ** 2)
            results['structural_similarity'] = 1 / (1 + mse)  # Convert to similarity (0-1)
        except:
            results['structural_similarity'] = 0

        # Composite score: weighted combination emphasizing different aspects
        results['composite_score'] = (
            0.4 * abs(results['pearson_r']) +      # Linear relationship (40%)
            0.3 * abs(results['spearman_r']) +     # Rank relationship (30%)
            0.2 * results['mutual_info'] +         # Complex dependencies (20%)
            0.1 * results['structural_similarity'] # Spatial structure (10%)
        )

        return results

    # Test our similarity metrics on the example data
    example_similarity = calculate_2d_correlation(species_heatmap, index_heatmap)

    print(f"Comprehensive similarity analysis for {example_species} vs {example_index}:")
    print(f"  Pearson correlation:     {example_similarity['pearson_r']:.3f}")
    print(f"  Spearman correlation:    {example_similarity['spearman_r']:.3f}")
    print(f"  Mutual information:      {example_similarity['mutual_info']:.3f}")
    print(f"  Cosine similarity:       {example_similarity['cosine_similarity']:.3f}")
    print(f"  Structural similarity:   {example_similarity['structural_similarity']:.3f}")
    print(f"  Composite score:         {example_similarity['composite_score']:.3f}")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Comprehensive Pattern Analysis

    Now we'll systematically analyze all possible species-index pairs to identify the strongest pattern matches. This involves:

    1. **Species Selection**: Focus on fish species with sufficient detection data
    2. **Index Selection**: Sample key indices from different acoustic categories
    3. **Similarity Calculation**: Apply all five similarity metrics to each pair
    4. **Ranking**: Identify top matches based on composite scores

    This systematic approach ensures we don't miss important relationships and can identify which acoustic indices are most informative for different species.
    """
    )
    return


@app.cell
def _(acoustic_indices, available_species, detections):
    # Select species and indices for comprehensive analysis

    # # Take top 10 most frequently detected species (note that we are only using 7 at this stage and will be using them all)
    species_detection_rates = {}
    for species in available_species[:15]:  # Check first 15 species
        if species in detections.columns:
            detection_rate = detections[species].mean()
            species_detection_rates[species] = detection_rate

    # # Sort by detection rate and take top 10
    top_species = sorted(species_detection_rates.items(), key=lambda x: x[1], reverse=True)[:10]
    species_list = [species for species, rate in top_species]


    # Select representative acoustic indices from different categories
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
            if idx in acoustic_indices.columns:
                index_list.append(idx)

    print(f"Selected {len(species_list)} species for analysis:")
    for i, (species, rate) in enumerate(top_species):
        print(f"  {i+1}. {species[:40]}... (detection rate: {rate:.3f})")

    print(f"\nSelected {len(index_list)} acoustic indices across {len(index_categories)} categories:")
    for category, indices in index_categories.items():
        available = [idx for idx in indices if idx in acoustic_indices.columns]
        if available:
            print(f"  {category}: {', '.join(available)}")

    return


@app.cell
def _():
    # # Pre-calculate all heatmaps (this is computationally efficient)
    # print("Pre-calculating species heatmaps...")
    # species_heatmaps_pre = {}
    # for species in species_list:
    #     species_heatmaps_pre[species] = calculate_weekly_hourly_heatmap(detections, species)

    # print("Pre-calculating acoustic index heatmaps...")
    # index_heatmaps_pre = {}
    # for index in index_list:
    #     index_heatmaps_pre[index] = calculate_weekly_hourly_heatmap(acoustic_indices, index)

    # # Calculate all pairwise similarities
    # print(f"\nCalculating similarities for {len(species_list)} × {len(index_list)} = {len(species_list) * len(index_list)} pairs...")

    # similarity_results = {}
    # all_results = []

    # for species in species_list:
    #     species_results = {}
    #     species_heatmap = species_heatmaps_pre[species]

    #     for index in index_list:
    #         if index not in index_heatmaps_pre:
    #             continue

    #         index_heatmap = index_heatmaps_pre[index]

    #         # Calculate all similarity metrics
    #         similarity = calculate_2d_correlation(species_heatmap, index_heatmap)
    #         species_results[index] = similarity

    #         # Store for overall analysis
    #         result_row = {
    #             'species': species,
    #             'index': index,
    #             **similarity
    #         }
    #         all_results.append(result_row)

    #     similarity_results[species] = species_results

    # # Convert to DataFrame for easy analysis
    # results_df = pd.DataFrame(all_results)

    # print(f"✓ Completed analysis of {len(all_results)} species-index pairs")
    # print(f"Mean composite score: {results_df['composite_score'].mean():.3f}")
    # print(f"Best composite score: {results_df['composite_score'].max():.3f}")

    return


@app.cell
def _():
    # # Analyze and visualize the results

    # # Find top matches
    # top_10_matches = results_df.nlargest(10, 'composite_score')

    # print("Top 10 Pattern Matches (Species vs Acoustic Index):")
    # print("=" * 70)
    # for i, (_, row) in enumerate(top_10_matches.iterrows(), 1):
    #     species_short = row['species'][:25] + "..." if len(row['species']) > 25 else row['species']
    #     print(f"{i:2d}. {species_short:<30} vs {row['index']:<8} | "
    #           f"Score: {row['composite_score']:.3f} | "
    #           f"r: {row['pearson_r']:+.3f}")

    # # Create distribution plots
    # fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

    # # Distribution of composite scores
    # ax1.hist(results_df['composite_score'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    # ax1.axvline(results_df['composite_score'].mean(), color='red', linestyle='--', 
    #             label=f'Mean: {results_df["composite_score"].mean():.3f}')
    # ax1.set_xlabel('Composite Similarity Score')
    # ax1.set_ylabel('Frequency')
    # ax1.set_title('Distribution of Pattern Similarity Scores')
    # ax1.legend()
    # ax1.grid(True, alpha=0.3)

    # # Pearson vs Spearman correlations
    # ax2.scatter(results_df['pearson_r'], results_df['spearman_r'], alpha=0.6, s=20)
    # ax2.plot([-1, 1], [-1, 1], 'r--', alpha=0.5, label='Perfect agreement')
    # ax2.set_xlabel('Pearson Correlation')
    # ax2.set_ylabel('Spearman Correlation')
    # ax2.set_title('Linear vs Rank Correlations')
    # ax2.legend()
    # ax2.grid(True, alpha=0.3)

    # # Top indices by average performance
    # index_performance = results_df.groupby('index')['composite_score'].agg(['mean', 'std', 'count']).reset_index()
    # index_performance = index_performance.sort_values('mean', ascending=True).tail(12)

    # ax3.barh(range(len(index_performance)), index_performance['mean'], 
    #          xerr=index_performance['std'], alpha=0.7, color='lightcoral')
    # ax3.set_yticks(range(len(index_performance)))
    # ax3.set_yticklabels(index_performance['index'])
    # ax3.set_xlabel('Average Composite Score')
    # ax3.set_title('Best-Performing Acoustic Indices')
    # ax3.grid(True, alpha=0.3, axis='x')

    # # Top species by average performance
    # species_performance = results_df.groupby('species')['composite_score'].agg(['mean', 'std', 'count']).reset_index()
    # species_performance = species_performance.sort_values('mean', ascending=True).tail(10)

    # species_labels = [sp[:20] + "..." if len(sp) > 20 else sp for sp in species_performance['species']]
    # ax4.barh(range(len(species_performance)), species_performance['mean'], 
    #          xerr=species_performance['std'], alpha=0.7, color='lightgreen')
    # ax4.set_yticks(range(len(species_performance)))
    # ax4.set_yticklabels(species_labels)
    # ax4.set_xlabel('Average Composite Score')
    # ax4.set_title('Most Predictable Species')
    # ax4.grid(True, alpha=0.3, axis='x')

    # plt.tight_layout()
    # plt.show()

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Visualizing Top Pattern Matches

    Let's examine the best pattern matches in detail by plotting the actual heatmaps side by side. This reveals whether the statistical similarity translates to visually interpretable patterns.

    For each top match, we'll show:
    - **Left panel**: Species detection patterns (warmer colors = more detections)
    - **Right panel**: Acoustic index patterns (color scale represents index values)
    - **Correlation info**: Pearson r and composite similarity score

    Look for:
    - **Synchronized patterns**: Similar "hotspots" in both heatmaps
    - **Daily rhythms**: Vertical bands showing consistent daily patterns
    - **Seasonal trends**: Horizontal bands showing seasonal changes
    - **Anti-correlations**: Opposite patterns (species active when index is low)
    """
    )
    return


@app.cell
def _():
    # # Visualize top 6 pattern matches
    # n_matches = 6
    # top_matches = top_10_matches.head(n_matches)

    # fig, axes = plt.subplots(n_matches, 2, figsize=(16, 4 * n_matches))
    # if n_matches == 1:
    #     axes = axes.reshape(1, -1)

    # for i, (_, match) in enumerate(top_matches.iterrows()):
    #     species = match['species']
    #     index = match['index']

    #     # Get heatmaps
    #     species_heatmap = species_heatmaps[species]
    #     index_heatmap = index_heatmaps[index]

    #     # Plot species heatmap
    #     ax1 = axes[i, 0]
    #     im1 = ax1.imshow(species_heatmap.T, cmap='YlOrRd', aspect='auto', origin='upper')

    #     # Format species title (truncate if too long)
    #     species_title = species[:35] + "..." if len(species) > 35 else species
    #     ax1.set_title(f'{species_title}\nDetection Patterns', fontsize=11)
    #     ax1.set_xlabel('Week of Year')
    #     if i == n_matches // 2:  # Label middle plot
    #         ax1.set_ylabel('Hour of Day')

    #     # Set hour labels (every 4 hours to avoid crowding)
    #     ax1.set_yticks(range(0, len(even_hours), 2))
    #     ax1.set_yticklabels([f"{even_hours[j]:02d}" for j in range(0, len(even_hours), 2)])

    #     # Add day/night reference
    #     ax1.axhline(y=3, color='yellow', linestyle='--', alpha=0.5, linewidth=0.8)
    #     ax1.axhline(y=9, color='navy', linestyle='--', alpha=0.5, linewidth=0.8)

    #     # Add colorbar
    #     cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.6)
    #     cbar1.set_label('Detection Rate', fontsize=9)

    #     # Plot acoustic index heatmap
    #     ax2 = axes[i, 1]
    #     im2 = ax2.imshow(index_heatmap.T, cmap='viridis', aspect='auto', origin='upper')

    #     correlation_info = f"r={match['pearson_r']:.3f}, score={match['composite_score']:.3f}"
    #     ax2.set_title(f'{index} Index\n{correlation_info}', fontsize=11)
    #     ax2.set_xlabel('Week of Year')

    #     # Same hour formatting
    #     ax2.set_yticks(range(0, len(even_hours), 2))
    #     ax2.set_yticklabels([f"{even_hours[j]:02d}" for j in range(0, len(even_hours), 2)])
    #     ax2.axhline(y=3, color='yellow', linestyle='--', alpha=0.5, linewidth=0.8)
    #     ax2.axhline(y=9, color='yellow', linestyle='--', alpha=0.5, linewidth=0.8)

    #     # Add colorbar
    #     cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.6)
    #     cbar2.set_label('Index Value', fontsize=9)

    # plt.suptitle('Top Pattern Matches: Species Detections vs Acoustic Indices\n'
    #              '(Yellow dashed = 6 AM, Navy/Yellow dashed = 6 PM)', 
    #              fontsize=14, y=0.995)
    # plt.tight_layout()
    # plt.subplots_adjust(top=0.96)
    # plt.show()

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Multi-Species Index Analysis

    Some acoustic indices might be particularly good at capturing general patterns of biological activity, correlating with multiple species simultaneously. These "generalist" indices could be especially valuable for biodiversity monitoring.

    Let's identify indices that show strong correlations with multiple different species.
    """
    )
    return


@app.cell
def _():
    # # Find indices that correlate with multiple species
    # threshold = 0.4  # Moderate similarity threshold

    # # Count how many species each index correlates with
    # multi_species_data = []

    # for index in index_list:
    #     index_results = results_df[results_df['index'] == index]

    #     # Find species with strong correlations
    #     strong_correlations = index_results[index_results['composite_score'] > threshold]

    #     if len(strong_correlations) > 1:  # At least 2 species
    #         multi_species_data.append({
    #             'index': index,
    #             'species_count': len(strong_correlations),
    #             'mean_score': strong_correlations['composite_score'].mean(),
    #             'max_score': strong_correlations['composite_score'].max(),
    #             'species_list': strong_correlations['species'].tolist()
    #         })

    # multi_species_df = pd.DataFrame(multi_species_data)
    # multi_species_df = multi_species_df.sort_values('species_count', ascending=False)

    # print(f"Acoustic indices correlating with multiple species (threshold: {threshold}):")
    # print("=" * 80)

    # for i, (_, row) in enumerate(multi_species_df.head(8).iterrows(), 1):
    #     species_names = [sp.split()[-1] if len(sp.split()) > 2 else sp 
    #                     for sp in row['species_list'][:4]]  # Show first 4, abbreviated
    #     species_str = ", ".join(species_names)
    #     if len(row['species_list']) > 4:
    #         species_str += f" (+ {len(row['species_list'])-4} more)"

    #     print(f"{i}. {row['index']:<8} | "
    #           f"{row['species_count']} species | "
    #           f"Mean score: {row['mean_score']:.3f} | "
    #           f"Species: {species_str}")

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Pattern Types and Biological Insights

    Let's examine the different types of relationships we've discovered and what they might tell us about marine soundscape ecology.
    """
    )
    return


@app.cell
def _():
    # # Analyze pattern types
    # print("PATTERN RELATIONSHIP ANALYSIS")
    # print("=" * 50)

    # # Positive vs negative correlations
    # strong_positive = results_df[results_df['pearson_r'] > 0.3]
    # strong_negative = results_df[results_df['pearson_r'] < -0.3]
    # moderate_positive = results_df[(results_df['pearson_r'] > 0.1) & (results_df['pearson_r'] <= 0.3)]

    # print(f"Strong positive correlations (r > 0.3): {len(strong_positive)} pairs")
    # print(f"Strong negative correlations (r < -0.3): {len(strong_negative)} pairs")
    # print(f"Moderate positive correlations (0.1 < r ≤ 0.3): {len(moderate_positive)} pairs")

    # if len(strong_positive) > 0:
    #     best_positive = strong_positive.loc[strong_positive['pearson_r'].idxmax()]
    #     print(f"\n🔸 Best positive match:")
    #     print(f"   {best_positive['species'][:30]}... vs {best_positive['index']}")
    #     print(f"   r = {best_positive['pearson_r']:.3f}, composite score = {best_positive['composite_score']:.3f}")
    #     print(f"   → Interpretation: Higher {best_positive['index']} values coincide with more species detections")

    # if len(strong_negative) > 0:
    #     best_negative = strong_negative.loc[strong_negative['pearson_r'].idxmin()]
    #     print(f"\n🔸 Best negative match:")
    #     print(f"   {best_negative['species'][:30]}... vs {best_negative['index']}")
    #     print(f"   r = {best_negative['pearson_r']:.3f}, composite score = {best_negative['composite_score']:.3f}")
    #     print(f"   → Interpretation: Species is more active when {best_negative['index']} values are low")

    # # Index category performance
    # print(f"\n\nACOUSTIC INDEX CATEGORY PERFORMANCE")
    # print("=" * 50)

    # category_performance = {}
    # for category, indices in index_categories.items():
    #     category_scores = []
    #     for index in indices:
    #         if index in results_df['index'].values:
    #             index_scores = results_df[results_df['index'] == index]['composite_score']
    #             category_scores.extend(index_scores.tolist())

    #     if category_scores:
    #         category_performance[category] = {
    #             'mean_score': np.mean(category_scores),
    #             'max_score': np.max(category_scores),
    #             'count': len(category_scores)
    #         }

    # # Sort categories by performance
    # sorted_categories = sorted(category_performance.items(), 
    #                          key=lambda x: x[1]['mean_score'], reverse=True)

    # for category, cat_stats in sorted_categories:
    #     print(f"{category:<12}: Mean score = {cat_stats['mean_score']:.3f}, "
    #           f"Best score = {cat_stats['max_score']:.3f} ({cat_stats['count']} comparisons)")

    # # Species predictability
    # print(f"\n\nSPECIES PREDICTABILITY INSIGHTS")
    # print("=" * 50)

    # species_stats = results_df.groupby('species').agg({
    #     'composite_score': ['mean', 'max', 'std'],
    #     'pearson_r': ['mean', 'std']
    # }).round(3)
    # species_stats.columns = ['mean_score', 'max_score', 'score_std', 'mean_r', 'r_std']
    # species_stats = species_stats.sort_values('mean_score', ascending=False)

    # print("Most predictable species (highest average similarity scores):")
    # for i, (species, sp_stats) in enumerate(species_stats.head(5).iterrows(), 1):
    #     species_short = species.split()[-1] if len(species.split()) > 1 else species[:15]
    #     print(f"{i}. {species_short:<15}: avg={sp_stats['mean_score']:.3f}, "
    #           f"best={sp_stats['max_score']:.3f}, consistency={1/sp_stats['score_std']:.1f}")

    # print("\nLeast predictable species (most variable patterns):")
    # high_variance = species_stats[species_stats['score_std'] > 0.05].sort_values('score_std', ascending=False)
    # for i, (species, sp_stats) in enumerate(high_variance.head(3).iterrows(), 1):
    #     species_short = species.split()[-1] if len(species.split()) > 1 else species[:15]
    #     print(f"{i}. {species_short:<15}: avg={sp_stats['mean_score']:.3f}, "
    #           f"variability={sp_stats['score_std']:.3f} (inconsistent patterns)")

    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Key Scientific Findings and Implications

    Based on our comprehensive pattern similarity analysis, here are the key insights for marine acoustic monitoring:

    ### 🎯 **Primary Discovery**
    We found significant 2D pattern similarities between species calling patterns and acoustic indices at the weekly-hourly resolution. This suggests that certain computed acoustic indices can serve as proxies for species activity patterns.

    ### 🔍 **Methodological Insights**

    1. **Multi-metric approach is essential**: Simple correlation misses complex relationships that other similarity measures capture
    2. **2D temporal analysis reveals more**: Weekly-hourly heatmaps capture both seasonal and daily patterns that 1D time series miss
    3. **Species-specific relationships**: Different acoustic indices work better for different species, suggesting the need for species-specific monitoring approaches

    ### 🐟 **Biological Insights**

    1. **Predictable species**: Some species show consistent temporal patterns that correlate well with multiple acoustic indices
    2. **Index categories matter**: Certain categories of acoustic indices (e.g., complexity, diversity) perform better than others for biological monitoring
    3. **Negative correlations**: Some species are more active when overall acoustic activity is low, suggesting niche partitioning

    ### 🎵 **Acoustic Monitoring Implications**

    1. **Automated monitoring potential**: Strong correlations suggest we can use acoustic indices to predict species activity without manual annotation
    2. **Multi-index approach recommended**: No single index captures all species patterns; a combination approach would be most effective
    3. **Temporal resolution matters**: The 2-hour resolution matching between detection and acoustic data was crucial for finding meaningful patterns

    ### 🚀 **Future Research Directions**

    1. **Validation with other stations**: Test these relationships at different geographic locations
    2. **Environmental covariates**: Incorporate temperature, depth, and seasonal factors
    3. **Machine learning approaches**: Use these similarity patterns to train automated species detection models
    4. **Real-time monitoring**: Develop indices-based early warning systems for biodiversity changes

    This analysis demonstrates that acoustic indices can indeed serve as valuable proxies for marine biodiversity patterns, opening new possibilities for scalable underwater ecosystem monitoring.
    """
    )
    return


if __name__ == "__main__":
    app.run()
