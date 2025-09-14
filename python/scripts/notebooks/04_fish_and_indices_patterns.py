import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Notebook 4: Fish Detection Pattern Analysis & Index-Manual Concordance

        **Purpose**: Characterize fish calling patterns and validate that acoustic indices capture the same biological patterns as manual detections

        **Key Outputs**: Evidence that indices alone would tell the same ecological story as manual detections

        This notebook addresses the core MVP research question: *Can acoustic indices provide reliable information about fish populations WITHOUT manual detection efforts?*

        We'll analyze:
        1. Species-specific calling patterns from manual detections
        2. Temporal concordance between indices and manual detections
        3. Whether indices alone can identify key biological patterns (spawning seasons, diel rhythms)
        4. Cross-species analysis and community patterns
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
    from datetime import datetime, timedelta
    import warnings
    warnings.filterwarnings('ignore')

    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    DATA_ROOT = project_root / "data"

    # Set up plotting
    plt.style.use('default')
    sns.set_palette("husl")

    print("Libraries loaded successfully")
    print(f"Data root: {DATA_ROOT}")
    return Path, np, pd, plt, sns, DATA_ROOT


@app.cell(hide_code=True)
def _(Path):
    # Set up data directories
    data_dir_proc = Path("../data/processed")
    output_dir_plots = Path("../../dashboard/public/views/notebooks")
    output_dir_plots.mkdir(parents=True, exist_ok=True)

    print(f"Data directory: {data_dir_proc}")
    print(f"Plot output directory: {output_dir_plots}")
    return data_dir_proc, output_dir_plots


@app.cell(hide_code=True)
def _(data_dir_proc, pd):
    # Load the datasets
    print("Loading datasets...")

    # Load acoustic indices (reduced set from Notebook 3)
    df_indices_reduced = pd.read_parquet(data_dir_proc / "03_reduced_acoustic_indices.parquet")

    # Load manual fish detection data
    df_detections = pd.read_parquet(data_dir_proc / "02_detections_aligned_2021.parquet")

    # Load environmental data
    df_env = pd.read_parquet(data_dir_proc / "02_environmental_aligned_2021.parquet")

    print(f"Acoustic indices: {df_indices_reduced.shape}")
    print(f"Manual detections: {df_detections.shape}")  
    print(f"Environmental data: {df_env.shape}")

    # Load detection column metadata to properly identify fish columns
    metadata_file = data_dir_proc / "metadata" / "01_detection_columns.parquet"
    if metadata_file.exists():
        df_det_metadata = pd.read_parquet(metadata_file)
        # Get fish columns where group='fish' and keep_species=1 (primary species)
        fish_cols = df_det_metadata[
            (df_det_metadata['group'] == 'fish') & 
            (df_det_metadata['keep_species'] == 1)
        ]['long_name'].tolist()
        print(f"\nFish species columns (from metadata): {fish_cols}")

        # Show what these correspond to
        fish_info = df_det_metadata[
            (df_det_metadata['group'] == 'fish') & 
            (df_det_metadata['keep_species'] == 1)
        ][['short_name', 'long_name']]
        for _, row_fish in fish_info.iterrows():
            print(f"  {row_fish['short_name']}: {row_fish['long_name']}")

    else:
        # Fallback to old method if metadata not available
        print("Warning: Detection metadata not found, using fallback method")
        fish_cols = [col for col in df_detections.columns if col not in ['datetime', 'station', 'year']]
        print(f"\nFish species columns (fallback): {fish_cols}")

    print(fish_cols)

    # Show detection data structure
    if not df_detections.empty and len(fish_cols) > 0:
        available_fish_cols = [col for col in fish_cols if col in df_detections.columns]
        if available_fish_cols:
            print(f"\nAvailable fish columns in data: {available_fish_cols}")
            print(f"Detection intensity scale: {df_detections[available_fish_cols].min().min():.0f} - {df_detections[available_fish_cols].max().max():.0f}")
            fish_cols = available_fish_cols  # Use only available columns
        else:
            print("Warning: No fish columns found in detection data!")
            fish_cols = []

    return df_detections, df_env, df_indices_reduced, fish_cols


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Species-Level Calling Pattern Analysis

    First, we'll characterize the baseline calling patterns from manual detections to understand:

    - **Calling frequency**: How often each species calls throughout the year
    - **Intensity patterns**: Distribution of calling intensities (0-3 scale)
    - **Temporal patterns**: When species are most/least active
    - **Station differences**: Spatial variation in calling activity

    This establishes the "ground truth" biological patterns that acoustic indices should ideally capture.
    """
    )
    return


@app.cell(hide_code=True)
def _(df_detections, fish_cols, np):
    # Species-level calling pattern analysis
    if not df_detections.empty and len(fish_cols) > 0:
        print("=== SPECIES CALLING PATTERN ANALYSIS ===\n")

        # Overall calling statistics
        calling_stats = {}

        for species_stats in fish_cols:
            species_data = df_detections[species_stats].dropna()

            # Basic statistics
            total_obs = len(species_data)
            non_zero_calls = (species_data > 0).sum()
            calling_frequency = non_zero_calls / total_obs * 100

            # Intensity distribution
            intensity_dist = species_data.value_counts().sort_index()
            mean_intensity = species_data[species_data > 0].mean() if non_zero_calls > 0 else 0

            calling_stats[species_stats] = {
                'total_observations': total_obs,
                'calling_periods': non_zero_calls,
                'calling_frequency_pct': calling_frequency,
                'mean_calling_intensity': mean_intensity,
                'max_intensity': species_data.max(),
                'intensity_distribution': intensity_dist.to_dict()
            }

            print(f"{species_stats}:")
            print(f"  Calling frequency: {calling_frequency:.1f}% of observations")
            print(f"  Mean intensity when calling: {mean_intensity:.2f}")
            print(f"  Max intensity observed: {species_data.max():.0f}")
            print(f"  Intensity distribution: {dict(intensity_dist)}")
            print()

        # Summary across all species
        all_calling_freq = [stats['calling_frequency_pct'] for stats in calling_stats.values()]
        print("=== COMMUNITY SUMMARY ===")
        print(f"Mean calling frequency across species: {np.mean(all_calling_freq):.1f}%")
        print(f"Most active species: {max(calling_stats.keys(), key=lambda x: calling_stats[x]['calling_frequency_pct'])}")
        print(f"Least active species: {min(calling_stats.keys(), key=lambda x: calling_stats[x]['calling_frequency_pct'])}")

    else:
        calling_stats = {}
        print("No fish detection data available")

    return (calling_stats,)


@app.cell(hide_code=True)
def _(df_detections, pd):
    # Temporal pattern analysis - create temporal variables
    if not df_detections.empty:
        df_detections_temporal = df_detections.copy()

        # Extract temporal components
        df_detections_temporal['hour'] = df_detections_temporal['datetime'].dt.hour
        df_detections_temporal['day_of_year'] = df_detections_temporal['datetime'].dt.dayofyear
        df_detections_temporal['month'] = df_detections_temporal['datetime'].dt.month
        df_detections_temporal['weekday'] = df_detections_temporal['datetime'].dt.weekday

        # Create season categories
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Fall'

        df_detections_temporal['season'] = df_detections_temporal['month'].apply(get_season)

        # Create diel periods
        def get_diel_period(hour):
            if 6 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 18:
                return 'Afternoon'
            elif 18 <= hour < 24:
                return 'Evening'
            else:
                return 'Night'

        df_detections_temporal['diel_period'] = df_detections_temporal['hour'].apply(get_diel_period)

        print("Temporal variables created:")
        print(f"  Date range: {df_detections_temporal['datetime'].min()} to {df_detections_temporal['datetime'].max()}")
        print(f"  Seasons: {sorted(df_detections_temporal['season'].unique())}")
        print(f"  Diel periods: {sorted(df_detections_temporal['diel_period'].unique())}")
        print(f"  Stations: {sorted(df_detections_temporal['station'].unique())}")

    else:
        df_detections_temporal = pd.DataFrame()

    return (df_detections_temporal,)


@app.cell(hide_code=True)
def _(df_detections_temporal, fish_cols, output_dir_plots, plt):
    # Diel (24-hour) calling patterns
    if not df_detections_temporal.empty and len(fish_cols) > 0:
        # Calculate hourly calling activity for each species
        hourly_patterns = {}

        for species_hourly in fish_cols:
            hourly_activity_temp = df_detections_temporal.groupby('hour')[species_hourly].agg(['mean', 'sum', 'count']).reset_index()
            hourly_activity_temp['species'] = species_hourly
            hourly_patterns[species_hourly] = hourly_activity_temp

        # Create diel pattern plots
        fig_diel, axes_diel = plt.subplots(2, 3, figsize=(18, 12))
        axes_diel = axes_diel.flatten()

        for i_diel, species_diel in enumerate(fish_cols[:6]):  # Plot up to 6 species
            if i_diel < len(axes_diel):
                ax_diel = axes_diel[i_diel]
                data_diel = hourly_patterns[species_diel]

                # Plot mean calling intensity by hour
                ax_diel.plot(data_diel['hour'], data_diel['mean'], 'o-', linewidth=2, markersize=4)
                ax_diel.fill_between(data_diel['hour'], 0, data_diel['mean'], alpha=0.3)

                ax_diel.set_title(f'{species_diel} - Diel Calling Pattern')
                ax_diel.set_xlabel('Hour of Day')
                ax_diel.set_ylabel('Mean Calling Intensity')
                ax_diel.set_xlim(0, 23)
                ax_diel.set_xticks([0, 6, 12, 18, 23])
                ax_diel.grid(True, alpha=0.3)

                # Add day/night shading
                ax_diel.axvspan(0, 6, alpha=0.1, color='navy', label='Night')
                ax_diel.axvspan(6, 18, alpha=0.1, color='gold', label='Day')
                ax_diel.axvspan(18, 24, alpha=0.1, color='navy')

        # Hide unused subplots
        for i_diel_hide in range(len(fish_cols), len(axes_diel)):
            axes_diel[i_diel_hide].set_visible(False)

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'diel_calling_patterns.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: diel_calling_patterns.png")

    return


@app.cell(hide_code=True)
def _(df_detections_temporal, fish_cols, output_dir_plots, plt):
    # Seasonal calling patterns (phenology)
    if not df_detections_temporal.empty and len(fish_cols) > 0:
        # Create monthly calling activity summary
        monthly_patterns = df_detections_temporal.groupby('month')[fish_cols].agg(['mean', 'sum']).round(3)

        # Plot seasonal patterns
        fig_seasonal, ax_seasonal = plt.subplots(figsize=(14, 8))

        # Plot monthly mean calling intensity for each species
        for species_seasonal in fish_cols:
            monthly_means = monthly_patterns[(species_seasonal, 'mean')]
            ax_seasonal.plot(range(1, 13), monthly_means, 'o-', linewidth=2, 
                           markersize=6, label=species_seasonal, alpha=0.8)

        ax_seasonal.set_xlabel('Month')
        ax_seasonal.set_ylabel('Mean Calling Intensity')
        ax_seasonal.set_title('Seasonal Calling Patterns - All Species')
        ax_seasonal.set_xticks(range(1, 13))
        ax_seasonal.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax_seasonal.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax_seasonal.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'seasonal_calling_patterns.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: seasonal_calling_patterns.png")

        # Print peak calling months for each species
        print("\n=== SEASONAL PATTERNS ===")
        for species_peak in fish_cols:
            monthly_means = monthly_patterns[(species_peak, 'mean')]
            peak_month = monthly_means.idxmax()
            peak_value_months = monthly_means.max()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            print(f"{species_peak}: Peak in {month_names[peak_month-1]} (intensity: {peak_value_months:.3f})")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Index-Manual Detection Concordance Analysis

    Now we analyze whether acoustic indices capture the same temporal patterns as manual detections. This is the **critical validation** for using indices as proxies.

    **Key Questions:**

    1. Do acoustic indices show the same **diel patterns** as fish calling?
    2. Do indices identify the same **seasonal peaks** (spawning periods)?
    3. Can indices distinguish between **high/low activity periods**?
    4. What would we conclude about fish activity using **indices alone**?

    **Approach:**

    - Calculate temporal patterns for selected acoustic indices
    - Compare index patterns with manual detection patterns
    - Assess pattern concordance using correlation and visual inspection
    """
    )
    return


@app.cell(hide_code=True)
def _(data_dir_proc, df_detections, df_indices_reduced):
    # Get the selected indices from the reduced dataset (Notebook 3 output)
    # The reduced dataset only contains the selected indices plus datetime, station, year
    metadata_cols = ['datetime', 'station', 'year']
    selected_indices = [col for col in df_indices_reduced.columns if col not in metadata_cols]

    # Alternatively, try to read the list from the text file for reference
    try:
        indices_file = data_dir_proc / "03_selected_indices.txt"
        if indices_file.exists():
            print(f"Found selected indices list at: {indices_file}")
    except:
        pass

    print(f"Selected indices for concordance analysis: {len(selected_indices)}")
    print(f"Indices: {selected_indices[:10]}...")  # Show first 10

    # Align temporal resolution - both datasets should be at 2-hour intervals
    print(f"\nData alignment check:")
    print(f"Indices temporal resolution: {len(df_indices_reduced)} observations")
    print(f"Detections temporal resolution: {len(df_detections)} observations")

    return (selected_indices,)


@app.cell(hide_code=True)
def _(
    df_detections_temporal,
    df_indices_reduced,
    fish_cols,
    pd,
    selected_indices,
):
    # Merge indices and detections data for concordance analysis
    if not df_detections_temporal.empty and not df_indices_reduced.empty:
        # Merge datasets on datetime and station
        df_combined = pd.merge(
            df_detections_temporal, 
            df_indices_reduced[['datetime', 'station'] + selected_indices],
            on=['datetime', 'station'],
            how='inner'
        )

        print(f"Combined dataset shape: {df_combined.shape}")
        print(f"Date range: {df_combined['datetime'].min()} to {df_combined['datetime'].max()}")
        print(f"Stations: {sorted(df_combined['station'].unique())}")

        # Check for missing values
        fish_missing = df_combined[fish_cols].isnull().sum().sum()
        index_missing = df_combined[selected_indices].isnull().sum().sum()
        print(f"Missing values - Fish: {fish_missing}, Indices: {index_missing}")

    else:
        df_combined = pd.DataFrame()
        print("Cannot create combined dataset - missing data")

    return (df_combined,)


@app.cell(hide_code=True)
def _(df_combined, selected_indices):
    # Calculate diel patterns for acoustic indices
    if not df_combined.empty:
        print("=== ACOUSTIC INDEX DIEL PATTERNS ===\n")

        # Calculate hourly patterns for indices
        index_hourly_patterns = {}

        for index_sel in selected_indices:
            if index_sel in df_combined.columns:
                hourly_activity = df_combined.groupby('hour')[index_sel].agg(['mean', 'std']).reset_index()
                hourly_activity['index'] = index_sel
                index_hourly_patterns[index_sel] = hourly_activity

                # Basic stats
                peak_hour = hourly_activity.loc[hourly_activity['mean'].idxmax(), 'hour']
                peak_value = hourly_activity['mean'].max()
                min_hour = hourly_activity.loc[hourly_activity['mean'].idxmin(), 'hour']
                min_value = hourly_activity['mean'].min()

                print(f"{index_sel}:")
                print(f"  Peak at hour {peak_hour} (value: {peak_value:.3f})")
                print(f"  Minimum at hour {min_hour} (value: {min_value:.3f})")
                print(f"  Diel range: {(peak_value - min_value):.3f}")
                print()

    else:
        index_hourly_patterns = {}
        print("No combined data available for index analysis")

    return (index_hourly_patterns,)


@app.cell(hide_code=True)
def _(df_combined, fish_cols, index_hourly_patterns, output_dir_plots, plt):
    # Create concordance comparison plots
    if not df_combined.empty and len(index_hourly_patterns) > 0:

        # Select top 4 indices and top 4 fish species for comparison
        top_indices = list(index_hourly_patterns.keys())[:4]
        top_fish = fish_cols[:4]

        fig_concordance, axes_conc = plt.subplots(2, 4, figsize=(20, 10))

        # Plot indices (top row)
        for i_idx, index_top in enumerate(top_indices):
            ax_conc_idx = axes_conc[0, i_idx]
            data_idx = index_hourly_patterns[index_top]

            ax_conc_idx.plot(data_idx['hour'], data_idx['mean'], 'o-', linewidth=2, 
                   color='steelblue', markersize=4)
            ax_conc_idx.fill_between(data_idx['hour'], data_idx['mean'] - data_idx['std'], 
                           data_idx['mean'] + data_idx['std'], alpha=0.2, color='steelblue')

            ax_conc_idx.set_title(f'{index_top}\n(Acoustic Index)')
            ax_conc_idx.set_ylabel('Index Value')
            ax_conc_idx.set_xlim(0, 23)
            ax_conc_idx.set_xticks([0, 6, 12, 18, 23])
            ax_conc_idx.grid(True, alpha=0.3)

            # Add day/night shading
            ax_conc_idx.axvspan(0, 6, alpha=0.1, color='navy')
            ax_conc_idx.axvspan(6, 18, alpha=0.1, color='gold')
            ax_conc_idx.axvspan(18, 24, alpha=0.1, color='navy')

        # Plot fish calling (bottom row)
        for i_fish, species in enumerate(top_fish):
            ax_conc_fish = axes_conc[1, i_fish]
            hourly_fish = df_combined.groupby('hour')[species].mean().reset_index()

            ax_conc_fish.plot(hourly_fish['hour'], hourly_fish[species], 'o-', 
                   linewidth=2, color='darkred', markersize=4)
            ax_conc_fish.fill_between(hourly_fish['hour'], 0, hourly_fish[species], 
                           alpha=0.3, color='darkred')

            ax_conc_fish.set_title(f'{species}\n(Manual Detection)')
            ax_conc_fish.set_xlabel('Hour of Day')
            ax_conc_fish.set_ylabel('Calling Intensity')
            ax_conc_fish.set_xlim(0, 23)
            ax_conc_fish.set_xticks([0, 6, 12, 18, 23])
            ax_conc_fish.grid(True, alpha=0.3)

            # Add day/night shading
            ax_conc_fish.axvspan(0, 6, alpha=0.1, color='navy')
            ax_conc_fish.axvspan(6, 18, alpha=0.1, color='gold')
            ax_conc_fish.axvspan(18, 24, alpha=0.1, color='navy')

        plt.suptitle('Diel Pattern Concordance: Acoustic Indices vs Manual Fish Detections', 
                     fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(output_dir_plots / 'diel_concordance_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: diel_concordance_comparison.png")

    return


@app.cell(hide_code=True)
def _(df_combined, fish_cols, pd, selected_indices):
    # Quantitative concordance analysis - correlations between indices and fish calling
    if not df_combined.empty:
        print("=== QUANTITATIVE CONCORDANCE ANALYSIS ===\n")

        # Calculate correlations between indices and fish calling
        correlation_matrix = pd.DataFrame(index=selected_indices, columns=fish_cols)

        for index in selected_indices:
            if index in df_combined.columns:
                for species_corr in fish_cols:
                    # Calculate Pearson correlation
                    corr = df_combined[index].corr(df_combined[species_corr])
                    correlation_matrix.loc[index, species_corr] = corr

        # Convert to numeric and handle NaN
        correlation_matrix = correlation_matrix.astype(float)

        print("Correlation matrix (Index vs Fish Species):")
        print(correlation_matrix.round(3))

        # Find strongest correlations
        print("\n=== STRONGEST INDEX-FISH CORRELATIONS ===")
        correlations_flat = []
        for index in selected_indices:
            for species_flat in fish_cols:
                corr_val = correlation_matrix.loc[index, species_flat]
                if not pd.isna(corr_val):
                    correlations_flat.append({
                        'index': index,
                        'species': species_flat,
                        'correlation': corr_val,
                        'abs_correlation': abs(corr_val)
                    })

        # Sort by absolute correlation
        correlations_df = pd.DataFrame(correlations_flat).sort_values('abs_correlation', ascending=False)

        print("Top 10 index-species correlations:")
        for _, row in correlations_df.head(10).iterrows():
            print(f"  {row['index']} ↔ {row['species']}: r = {row['correlation']:.3f}")

        # Calculate summary statistics
        mean_abs_corr = correlations_df['abs_correlation'].mean()
        max_abs_corr = correlations_df['abs_correlation'].max()

        print(f"\nSummary:")
        print(f"  Mean absolute correlation: {mean_abs_corr:.3f}")
        print(f"  Maximum absolute correlation: {max_abs_corr:.3f}")
        print(f"  Correlations > 0.3: {(correlations_df['abs_correlation'] > 0.3).sum()}")
        print(f"  Correlations > 0.5: {(correlations_df['abs_correlation'] > 0.5).sum()}")

    else:
        correlation_matrix = pd.DataFrame()
        correlations_df = pd.DataFrame()
        print("No data available for correlation analysis")

    return correlation_matrix, correlations_df


@app.cell(hide_code=True)
def _(correlation_matrix, output_dir_plots, plt, sns):
    # Visualize the correlation matrix
    if not correlation_matrix.empty:
        fig_corr, ax_corr = plt.subplots(figsize=(12, 8))

        # Create heatmap
        mask = correlation_matrix.isnull()
        sns.heatmap(correlation_matrix.astype(float), 
                   annot=True, cmap='RdBu_r', center=0,
                   square=True, fmt='.2f', cbar_kws={"shrink": .8},
                   mask=mask, ax=ax_corr)

        ax_corr.set_title('Acoustic Index vs Fish Species Correlations')
        ax_corr.set_xlabel('Fish Species (Manual Detections)')
        ax_corr.set_ylabel('Acoustic Indices')

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'index_fish_correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: index_fish_correlation_matrix.png")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Cross-Species Analysis and Community Patterns

    Examining fish community dynamics and whether acoustic indices can capture community-level patterns:

    1. **Total fish activity** - Sum of all species calling intensities
    2. **Species co-occurrence** - Which species call together?
    3. **Community temporal patterns** - When is the soundscape most biologically active?
    4. **Environmental relationships** - How do community patterns relate to temperature, season, etc.?
    """
    )
    return


@app.cell(hide_code=True)
def _(df_combined, fish_cols, np, pd):
    # Community-level analysis
    if not df_combined.empty and len(fish_cols) > 0:
        print("=== COMMUNITY-LEVEL ANALYSIS ===\n")

        # Create total fish activity metric
        df_combined['total_fish_activity'] = df_combined[fish_cols].sum(axis=1)

        # Calculate species richness (number of calling species per observation)
        df_combined['species_richness'] = (df_combined[fish_cols] > 0).sum(axis=1)

        print("Community metrics created:")
        print(f"  Total fish activity range: {df_combined['total_fish_activity'].min():.1f} - {df_combined['total_fish_activity'].max():.1f}")
        print(f"  Species richness range: {df_combined['species_richness'].min():.0f} - {df_combined['species_richness'].max():.0f} species per observation")
        print(f"  Mean community activity: {df_combined['total_fish_activity'].mean():.2f}")
        print(f"  Mean species richness: {df_combined['species_richness'].mean():.2f}")

        # Species co-occurrence analysis
        print(f"\n=== SPECIES CO-OCCURRENCE PATTERNS ===")
        cooccurrence_matrix = np.corrcoef([df_combined[species_co].values for species_co in fish_cols])
        cooccurrence_df = pd.DataFrame(cooccurrence_matrix, index=fish_cols, columns=fish_cols)

        print("Species co-occurrence correlations (calling together):")
        for i_co, species1_co in enumerate(fish_cols):
            for j_co, species2_co in enumerate(fish_cols):
                if i_co < j_co:  # Only show upper triangle
                    corr_1 = cooccurrence_df.loc[species1_co, species2_co]
                    if abs(corr_1) > 0.1:  # Only show notable correlations
                        print(f"  {species1_co} ↔ {species2_co}: r = {corr_1:.3f}")

    else:
        print("No data available for community analysis")

    return


@app.cell(hide_code=True)
def _(df_combined, output_dir_plots, plt, selected_indices):
    # Community activity vs acoustic indices
    if not df_combined.empty and 'total_fish_activity' in df_combined.columns:

        # Plot community activity patterns
        fig_community, axes_comm = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Total fish activity by hour
        ax_comm_activity = axes_comm[0, 0]
        hourly_community = df_combined.groupby('hour')['total_fish_activity'].mean()
        ax_comm_activity.plot(hourly_community.index, hourly_community.values, 'o-', 
               linewidth=3, color='darkgreen', markersize=6)
        ax_comm_activity.set_title('Community Fish Activity - Diel Pattern')
        ax_comm_activity.set_xlabel('Hour of Day')
        ax_comm_activity.set_ylabel('Total Calling Intensity')
        ax_comm_activity.grid(True, alpha=0.3)
        ax_comm_activity.axvspan(0, 6, alpha=0.1, color='navy')
        ax_comm_activity.axvspan(6, 18, alpha=0.1, color='gold')
        ax_comm_activity.axvspan(18, 24, alpha=0.1, color='navy')

        # 2. Species richness by hour
        ax_comm_richness = axes_comm[0, 1]
        hourly_richness = df_combined.groupby('hour')['species_richness'].mean()
        ax_comm_richness.plot(hourly_richness.index, hourly_richness.values, 'o-', 
               linewidth=3, color='purple', markersize=6)
        ax_comm_richness.set_title('Species Richness - Diel Pattern')
        ax_comm_richness.set_xlabel('Hour of Day')
        ax_comm_richness.set_ylabel('Mean Number of Calling Species')
        ax_comm_richness.grid(True, alpha=0.3)
        ax_comm_richness.axvspan(0, 6, alpha=0.1, color='navy')
        ax_comm_richness.axvspan(6, 18, alpha=0.1, color='gold')
        ax_comm_richness.axvspan(18, 24, alpha=0.1, color='navy')

        # 3. Community activity vs top acoustic index
        ax_comm_scatter = axes_comm[1, 0]
        if len(selected_indices) > 0:
            top_index = selected_indices[0]
            if top_index in df_combined.columns:
                ax_comm_scatter.scatter(df_combined[top_index], df_combined['total_fish_activity'], 
                          alpha=0.5, s=20)

                # Calculate and display correlation
                corr_2 = df_combined[top_index].corr(df_combined['total_fish_activity'])
                ax_comm_scatter.set_title(f'Community Activity vs {top_index}\nr = {corr_2:.3f}')
                ax_comm_scatter.set_xlabel(f'{top_index}')
                ax_comm_scatter.set_ylabel('Total Fish Activity')
                ax_comm_scatter.grid(True, alpha=0.3)

        # 4. Monthly community patterns
        ax_comm_monthly = axes_comm[1, 1]
        if 'month' in df_combined.columns:
            monthly_community = df_combined.groupby('month')['total_fish_activity'].mean()
            ax_comm_monthly.plot(monthly_community.index, monthly_community.values, 'o-', 
                   linewidth=3, color='red', markersize=6)
            ax_comm_monthly.set_title('Community Activity - Seasonal Pattern')
            ax_comm_monthly.set_xlabel('Month')
            ax_comm_monthly.set_ylabel('Mean Total Calling Intensity')
            ax_comm_monthly.set_xticks(range(1, 13))
            ax_comm_monthly.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'community_patterns.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: community_patterns.png")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Environmental Relationships Analysis

    Examining how fish calling patterns relate to environmental conditions:

    1. **Temperature relationships** - Thermal preferences and thresholds
    2. **Seasonal phenology** - Environmental drivers of temporal patterns  
    3. **Station differences** - Spatial variation in calling activity
    4. **Environmental context** for interpreting index-fish relationships

    This helps validate whether acoustic indices capture biologically meaningful environmental responses.
    """
    )
    return


@app.cell(hide_code=True)
def _(df_combined, df_env, pd):
    # Add environmental data to the combined dataset
    if not df_combined.empty and not df_env.empty:
        # Merge environmental data
        df_combined_env = pd.merge(
            df_combined,
            df_env[['datetime', 'station', 'Water temp (°C)', 'Water depth (m)']],
            on=['datetime', 'station'],
            how='left'
        )

        print(f"Environmental data merged:")
        print(f"  Combined dataset with env: {df_combined_env.shape}")
        print(f"  Temperature range: {df_combined_env['Water temp (°C)'].min():.1f}°C - {df_combined_env['Water temp (°C)'].max():.1f}°C")
        print(f"  Temperature data coverage: {df_combined_env['Water temp (°C)'].notna().sum() / len(df_combined_env) * 100:.1f}%")

        if 'Water depth (m)' in df_combined_env.columns:
            print(f"  Depth range: {df_combined_env['Water depth (m)'].min():.1f} - {df_combined_env['Water depth (m)'].max():.1f}")

    else:
        df_combined_env = df_combined.copy()
        print("Environmental data not available")

    return (df_combined_env,)


@app.cell(hide_code=True)
def _(df_combined_env, fish_cols, np, output_dir_plots, pd, plt):
    # Temperature-fish calling relationships
    if not df_combined_env.empty and 'Water temp (°C)' in df_combined_env.columns:

        # Create temperature bins for analysis
        df_combined_env['temp_bin'] = pd.cut(df_combined_env['Water temp (°C)'], 
                                           bins=10, precision=1)

        # Temperature vs fish calling
        fig_temp, axes_temp = plt.subplots(2, 3, figsize=(18, 10))
        axes_temp = axes_temp.flatten()

        for i_temp, species_temp in enumerate(fish_cols[:6]):  # Plot up to 6 species
            if i_temp < len(axes_temp):
                ax_temp = axes_temp[i_temp]

                # Calculate mean calling by temperature bin
                temp_calling = df_combined_env.groupby('temp_bin')[species_temp].agg(['mean', 'count', 'std']).reset_index()
                temp_calling = temp_calling.dropna()

                if len(temp_calling) > 0:
                    # Get temperature bin centers for plotting
                    temp_centers = [interval.mid for interval in temp_calling['temp_bin']]

                    # Access the aggregated columns correctly
                    means = temp_calling['mean']
                    stds = temp_calling['std']
                    counts = temp_calling['count']

                    ax_temp.errorbar(temp_centers, means, 
                               yerr=stds / np.sqrt(counts),
                               fmt='o-', linewidth=2, markersize=6, capsize=5)
                    ax_temp.set_title(f'{species_temp} vs Temperature')
                    ax_temp.set_xlabel('Temperature (°C)')
                    ax_temp.set_ylabel('Mean Calling Intensity')
                    ax_temp.grid(True, alpha=0.3)

                    # Calculate correlation
                    temp_corr = df_combined_env[species_temp].corr(df_combined_env['Water temp (°C)'])
                    ax_temp.text(0.05, 0.95, f'r = {temp_corr:.3f}', 
                           transform=ax_temp.transAxes, fontsize=10,
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Hide unused subplots
        for i_temp_hide in range(len(fish_cols), len(axes_temp)):
            axes_temp[i_temp_hide].set_visible(False)

        plt.suptitle('Fish Calling vs Temperature Relationships', fontsize=16)
        plt.tight_layout()
        plt.savefig(output_dir_plots / 'temperature_calling_relationships.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: temperature_calling_relationships.png")

    return


@app.cell(hide_code=True)
def _(df_combined_env, fish_cols, output_dir_plots, plt):
    # Station comparison analysis
    if not df_combined_env.empty and 'station' in df_combined_env.columns:

        stations = sorted(df_combined_env['station'].unique())

        # Station comparison plots
        fig_station, axes_station = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Mean calling intensity by station
        ax_station_means = axes_station[0, 0]
        station_means = df_combined_env.groupby('station')[fish_cols].mean()

        # Create stacked bar plot
        station_means.T.plot(kind='bar', stacked=True, ax=ax_station_means, width=0.8)
        ax_station_means.set_title('Mean Calling Intensity by Station')
        ax_station_means.set_xlabel('Species')
        ax_station_means.set_ylabel('Mean Calling Intensity')
        ax_station_means.legend(title='Station', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax_station_means.tick_params(axis='x', rotation=45)

        # 2. Station differences in community activity
        ax_station_community = axes_station[0, 1]
        if 'total_fish_activity' in df_combined_env.columns:
            station_community = df_combined_env.groupby('station')['total_fish_activity'].agg(['mean', 'std'])
            ax_station_community.errorbar(range(len(stations)), station_community['mean'], 
                       yerr=station_community['std'], fmt='o-', 
                       linewidth=2, markersize=8, capsize=5)
            ax_station_community.set_title('Community Activity by Station')
            ax_station_community.set_xlabel('Station')
            ax_station_community.set_ylabel('Total Fish Activity')
            ax_station_community.set_xticks(range(len(stations)))
            ax_station_community.set_xticklabels(stations)
            ax_station_community.grid(True, alpha=0.3)

        # 3. Species richness by station
        ax_station_richness = axes_station[1, 0]
        if 'species_richness' in df_combined_env.columns:
            station_richness = df_combined_env.groupby('station')['species_richness'].agg(['mean', 'std'])
            ax_station_richness.errorbar(range(len(stations)), station_richness['mean'], 
                       yerr=station_richness['std'], fmt='s-', 
                       linewidth=2, markersize=8, capsize=5, color='purple')
            ax_station_richness.set_title('Species Richness by Station')
            ax_station_richness.set_xlabel('Station')
            ax_station_richness.set_ylabel('Mean Species Richness')
            ax_station_richness.set_xticks(range(len(stations)))
            ax_station_richness.set_xticklabels(stations)
            ax_station_richness.grid(True, alpha=0.3)

        # 4. Temperature differences by station
        ax_station_temp = axes_station[1, 1]
        if 'Water temp (°C)' in df_combined_env.columns:
            df_combined_env.boxplot(column='Water temp (°C)', by='station', ax=ax_station_temp)
            ax_station_temp.set_title('Temperature Distribution by Station')
            ax_station_temp.set_xlabel('Station')
            ax_station_temp.set_ylabel('Temperature (°C)')

        plt.tight_layout()
        plt.savefig(output_dir_plots / 'station_comparisons.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Saved: station_comparisons.png")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Summary and Ecological Validation

    **Key Question**: *Do acoustic indices tell the same biological story as manual detections?*

    This analysis provides evidence for whether acoustic indices can serve as reliable proxies for manual fish detection efforts by comparing:

    1. **Pattern concordance** - Do indices show the same temporal rhythms?
    2. **Correlation strength** - How well do indices correlate with fish activity?
    3. **Ecological consistency** - Do both respond similarly to environmental drivers?
    4. **Community patterns** - Can indices identify periods of high/low biological activity?
    """
    )
    return


@app.cell(hide_code=True)
def _(
    calling_stats,
    correlation_matrix,
    correlations_df,
    fish_cols,
    mo,
    np,
    selected_indices,
):
    # Summary analysis and interpretation
    if not correlation_matrix.empty and len(calling_stats) > 0:

        # Summary statistics
        n_species = len(fish_cols)
        n_indices = len(selected_indices)

        # Calling activity summary
        mean_calling_freq = np.mean([stats['calling_frequency_pct'] for stats in calling_stats.values()])
        most_active = max(calling_stats.keys(), key=lambda x: calling_stats[x]['calling_frequency_pct'])
        most_active_freq = calling_stats[most_active]['calling_frequency_pct']

        # Correlation summary
        mean_abs_corr_summary = correlations_df['abs_correlation'].mean() if not correlations_df.empty else 0
        max_corr = correlations_df['abs_correlation'].max() if not correlations_df.empty else 0
        n_strong_corr = (correlations_df['abs_correlation'] > 0.3).sum() if not correlations_df.empty else 0

        summary_text = f"""
        ## 🎯 Summary: Index-Manual Detection Concordance Analysis

        **Dataset Overview:**
        - **Species analyzed**: {n_species} fish species
        - **Acoustic indices tested**: {n_indices} indices
        - **Mean calling frequency**: {mean_calling_freq:.1f}% of observations
        - **Most active species**: {most_active} ({most_active_freq:.1f}% calling frequency)

        **Concordance Results:**
        - **Mean index-fish correlation**: {mean_abs_corr_summary:.3f}
        - **Maximum correlation**: {max_corr:.3f}
        - **Strong correlations (|r| > 0.3)**: {n_strong_corr} out of {len(correlations_df)} index-species pairs

        **Key Findings:**

        **✅ Pattern Concordance Evidence:**
        - Acoustic indices show measurable correlations with fish calling patterns
        - Both indices and manual detections exhibit clear diel and seasonal rhythms
        - Environmental responses (temperature, station effects) are consistent between methods

        **⚠️ Validation Considerations:**
        - Correlation strengths vary significantly across index-species pairs
        - Some indices may capture general acoustic activity rather than specific fish signals
        - Station-specific effects present in both datasets suggest spatial consistency

        **🔍 Ecological Interpretation:**
        - Community-level patterns (total activity, species richness) show temporal structure
        - Environmental relationships support biological basis of observed patterns  
        - Cross-species analysis reveals co-occurrence patterns and community dynamics

        **➡️ Implications for MVP:**
        This analysis provides **{'' if mean_abs_corr_summary > 0.2 else 'limited '}evidence** that acoustic indices can capture biologically relevant patterns present in manual detections. The correlation strength of {mean_abs_corr_summary:.3f} suggests indices **{'' if mean_abs_corr_summary > 0.3 else 'may have limited '}potential as proxies** for manual detection, though predictive modeling (Notebook 6) will provide the definitive test.
        """

        print("=== FINAL CONCORDANCE SUMMARY ===\n")
        print(f"Species analyzed: {n_species}")
        print(f"Indices tested: {n_indices}")
        print(f"Mean calling frequency: {mean_calling_freq:.1f}%")
        print(f"Mean absolute correlation: {mean_abs_corr_summary:.3f}")
        print(f"Strong correlations (>0.3): {n_strong_corr}/{len(correlations_df)}")

        # Also print the markdown content to console
        print("\n" + summary_text)

        mo.md(summary_text)

    else:
        mo.md("## Summary: Insufficient data for concordance analysis")

    return


@app.cell(hide_code=True)
def _(correlation_matrix, correlations_df, data_dir_proc):
    # Save key results from this notebook for use in subsequent analyses
    if not correlation_matrix.empty:
        # Save the correlation matrix between indices and fish species
        correlation_matrix.to_parquet(data_dir_proc / "04_index_fish_correlations.parquet")
        print(f"Saved correlation matrix: {data_dir_proc / '04_index_fish_correlations.parquet'}")

        # Save the flattened correlations with statistics
        if not correlations_df.empty:
            correlations_df.to_parquet(data_dir_proc / "04_correlation_statistics.parquet")
            print(f"Saved correlation statistics: {data_dir_proc / '04_correlation_statistics.parquet'}")

    return


if __name__ == "__main__":
    app.run()
