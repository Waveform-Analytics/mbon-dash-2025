import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Notebook 6: Community Pattern Detection and Biological Screening

        **Purpose**: Demonstrate that acoustic indices can detect community-level fish patterns and identify periods of biological interest

        **Key Outputs**: Evidence that indices serve as effective biological screening tools for continuous monitoring

        ---

        **📝 Research Timeline Note**: This notebook was originally developed to analyze fish-only community patterns. During the research process (documented in Notebook 08), we discovered that dolphin data had been flowing through the pipeline all along, but with incompatible metrics. This notebook was subsequently updated to include comparative marine community analysis (fish + dolphins) alongside the original fish-only analysis. This represents the authentic, iterative nature of the research process - showing both the original approach and how new discoveries led to enhanced methods.

        **🔄 If you're following the research journey chronologically**: This notebook can be run independently for fish-only analysis, but the marine community features require running Notebook 08 first to generate the dolphin intensity conversion and marine community metrics.

        ---

        ## Overview

        Moving beyond species-specific prediction, this notebook tests whether acoustic indices can serve as **biological screening tools** by detecting aggregate community-level fish activity. Rather than trying to predict individual species calling intensities, we focus on:

        1. **Community-level activity detection**: Can indices detect when "something biological is happening" vs periods of low activity?
        2. **Temporal pattern concordance**: Do indices capture the same diel and seasonal patterns as manual detections?
        3. **Screening efficiency**: How much manual effort could be saved by using indices to identify high-activity periods?
        4. **Cross-station transferability**: Do index-based patterns hold across different monitoring locations?

        ## Methodological Approach

        ### Community Metrics Design
        We create several aggregate metrics that summarize biological activity across all fish species:

        - **Total activity**: Sum of calling intensities across all species (captures overall biological "energy")
        - **Number of active species**: Count of species calling in each period (community richness proxy)
        - **Maximum activity**: Peak calling intensity across species (dominant biological signal)
        - **Activity diversity**: Variation in calling patterns (community evenness proxy)

        ### Binary Classification Strategy
        Instead of predicting exact calling intensities (0-3 scale), we convert community activity into binary classification problems:

        - **Any activity vs none**: Basic biological presence/absence detection
        - **High activity (75th/90th percentile)**: Periods of exceptional biological interest
        - **Multi-species active**: Complex community interactions vs single-species events

        ### Machine Learning Models
        We test multiple classification algorithms to find the best approach:

        - **Logistic Regression**: Linear baseline, interpretable coefficients
        - **Decision Tree**: Non-linear, rule-based, highly interpretable
        - **Random Forest**: Ensemble method, handles feature interactions, robust to overfitting
        - Attempted **Gradient Boosting** but it took too much time/compute for this analysis

        ### Evaluation Focus
        Rather than just accuracy, we emphasize **screening performance**:

        - **Effort reduction**: How much manual work can be saved?
        - **Detection rate**: What percentage of biological activity is captured?
        - **Precision**: When the model flags a period, how often is it actually active?

        ## Why This Matters

        If acoustic indices can reliably detect periods of biological interest, they could serve as **intelligent screening tools** that guide targeted manual detection efforts. This would enable:

        - **Continuous biological monitoring** at scales impossible with manual detection alone
        - **Efficient allocation of manual effort** to periods most likely to contain biological activity
        - **Early detection of biological events** like spawning aggregations or community shifts
        - **Cost-effective long-term monitoring** with minimal ongoing human effort

        The key question: **"Can acoustic indices tell us when to pay attention?"**
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
    import json
    import pickle
    warnings.filterwarnings('ignore')

    # Machine learning
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, TimeSeriesSplit
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, RobustScaler
    from sklearn.metrics import (
        classification_report, confusion_matrix, roc_curve, auc,
        precision_recall_curve, accuracy_score, cohen_kappa_score,
        f1_score, precision_score, recall_score
    )
    from sklearn.feature_selection import mutual_info_classif, SelectKBest

    # Statistical analysis
    from scipy import stats
    from scipy.stats import spearmanr, pearsonr

    # Set plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    # Data directories
    DATA_ROOT = project_root / "data"
    data_dir = DATA_ROOT / "processed"
    plot_dir = DATA_ROOT.parent / "dashboard/public/views/notebooks"
    plot_dir.mkdir(exist_ok=True, parents=True)

    print("Libraries loaded successfully")
    print(f"Data root: {DATA_ROOT}")
    print(f"Plot directory: {plot_dir}")
    return (
        DATA_ROOT,
        DecisionTreeClassifier,
        LogisticRegression,
        RandomForestClassifier,
        StandardScaler,
        StratifiedKFold,
        accuracy_score,
        cohen_kappa_score,
        cross_val_score,
        f1_score,
        json,
        mutual_info_classif,
        np,
        pd,
        pickle,
        plot_dir,
        plt,
        precision_score,
        recall_score,
        spearmanr,
        train_test_split,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Data Loading and Preparation

    Loading all processed datasets and preparing them for community-level analysis.
    """
    )
    return


@app.cell
def _(DATA_ROOT, pd):
    # Load all processed datasets
    print("Loading processed datasets...")

    # Load reduced acoustic indices from Notebook 3
    df_indices = pd.read_parquet(DATA_ROOT / "processed/03_reduced_acoustic_indices.parquet")

    # Load aligned detections (original fish-only data)
    df_detections = pd.read_parquet(DATA_ROOT / "processed/02_detections_aligned_2021.parquet")

    # Load enhanced marine community data (fish + dolphins from notebook 08)
    marine_community_file = DATA_ROOT / "processed/02_detections_with_marine_community.parquet"
    if marine_community_file.exists():
        df_marine_community = pd.read_parquet(marine_community_file)
        print(f"✅ Loaded enhanced marine community data: {df_marine_community.shape}")
    else:
        print(f"⚠️ Marine community data not found: {marine_community_file}")
        print("Run notebook 08 first to generate marine community metrics")
        df_marine_community = None

    # Load environmental data
    df_env = pd.read_parquet(DATA_ROOT / "processed/02_environmental_aligned_2021.parquet")

    # Load temporal features
    df_temporal = pd.read_parquet(DATA_ROOT / "processed/02_temporal_features_2021.parquet")

    # Load detection metadata to identify fish species
    df_det_metadata = pd.read_parquet(DATA_ROOT / "processed/metadata/01_detection_columns.parquet")

    print(f"Indices shape: {df_indices.shape}")
    print(f"Detections shape: {df_detections.shape}")
    print(f"Environmental shape: {df_env.shape}") 
    print(f"Temporal features shape: {df_temporal.shape}")
    return (
        df_det_metadata,
        df_detections,
        df_env,
        df_indices,
        df_marine_community,
        df_temporal,
    )


@app.cell
def _(df_det_metadata, df_detections, df_env, df_indices, df_temporal):
    # Get fish species columns
    fish_species = df_det_metadata[
        (df_det_metadata['group'] == 'fish') &
        (df_det_metadata['keep_species'] == 1)
    ]['long_name'].tolist()

    # Get acoustic index columns (exclude metadata)
    index_cols = [col for col in df_indices.columns
                  if col not in ['datetime', 'station', 'year']]

    # Merge all datasets
    df_master = df_indices.merge(
        df_detections[['datetime', 'station', 'year'] + fish_species],
        on=['datetime', 'station', 'year'],
        how='left'
    )

    df_master = df_master.merge(
        df_env[['datetime', 'station', 'year', 'Water temp (°C)', 'Water depth (m)',
                'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']],
        on=['datetime', 'station', 'year'],
        how='left'
    )

    df_master = df_master.merge(
        df_temporal[['datetime', 'station', 'year', 'hour', 'month', 'season', 'time_period']],
        on=['datetime', 'station', 'year'],
        how='left'
    )

    # Rename time_period to diel_period for consistency
    df_master = df_master.rename(columns={'time_period': 'diel_period'})

    print(f"Master dataset shape: {df_master.shape}")
    print(f"Fish species columns ({len(fish_species)}): {fish_species}")
    print(f"Acoustic index columns ({len(index_cols)}): {index_cols[:5]}...")
    return df_master, fish_species, index_cols


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Community Activity Metrics Creation

    Creating aggregate community-level metrics that move beyond species-specific analysis.

    ## Strategy: From Species-Specific to Community-Level Analysis

    Instead of trying to predict individual species calling patterns (which showed limited success in earlier analyses),
    we aggregate across all species to ask: **"Is there biological activity happening?"** This approach:

    1. **Reduces complexity**: 7 species × 4 intensity levels = 28 possible states → 4 binary questions
    2. **Increases signal**: Combines weak species-specific signals into stronger community signal
    3. **Matches practical needs**: Often we care more about "when to listen carefully" than "exactly which species"
    4. **Improves statistical power**: More balanced classes, clearer patterns
    """
    )
    return


@app.cell
def _(
    df_env,
    df_indices,
    df_marine_community,
    df_master,
    df_temporal,
    fish_species,
):
    # Create community-level activity metrics
    print("Creating community activity metrics...")
    print(f"Working with {len(fish_species)} fish species: {fish_species}")

    # 1. Total fish activity (sum across all species)
    # This captures the overall "biological energy" in each 2-hour period
    # Range: 0 (no calling) to 21 (all species calling at maximum intensity)
    df_community = df_master.copy()
    df_community['total_fish_activity'] = df_community[fish_species].sum(axis=1)
    print(f"Total activity range: {df_community['total_fish_activity'].min():.0f} to {df_community['total_fish_activity'].max():.0f}")

    # 2. Number of active species (how many species detected)
    # This measures community richness - are multiple species active simultaneously?
    # Range: 0 (no species) to 7 (all species calling)
    df_community['num_active_species'] = (df_community[fish_species] > 0).sum(axis=1)
    print(f"Active species range: {df_community['num_active_species'].min():.0f} to {df_community['num_active_species'].max():.0f}")

    # 3. Maximum species activity (highest calling intensity across species)
    # This captures the strength of the dominant biological signal
    # Range: 0 (no activity) to 3 (maximum intensity from at least one species)
    df_community['max_species_activity'] = df_community[fish_species].max(axis=1)
    print(f"Maximum activity range: {df_community['max_species_activity'].min():.0f} to {df_community['max_species_activity'].max():.0f}")

    # 4. Activity diversity (simplified - coefficient of variation)
    # This measures how evenly distributed calling is across species
    # High values = one species dominates, Low values = multiple species calling similarly
    df_community['activity_diversity'] = df_community[fish_species].std(axis=1) / (df_community[fish_species].mean(axis=1) + 0.01)

    print("\n" + "="*60)
    print("CREATING BINARY CLASSIFICATION TARGETS")
    print("="*60)
    print("Converting continuous community metrics into binary screening questions:")

    # 5. Binary classification targets at different thresholds
    # These represent different "screening sensitivity" levels

    # High vs low total activity (75th percentile threshold)
    # Question: "Is this a period of elevated biological activity?"
    total_activity_75th = df_community['total_fish_activity'].quantile(0.75)
    df_community['high_activity_75th'] = (df_community['total_fish_activity'] >= total_activity_75th).astype(int)
    print(f"High activity (75th percentile, threshold={total_activity_75th:.1f}): {df_community['high_activity_75th'].mean():.1%} of periods")

    # Very high activity (90th percentile threshold)
    # Question: "Is this a period of exceptional biological interest?"
    total_activity_90th = df_community['total_fish_activity'].quantile(0.90)
    df_community['high_activity_90th'] = (df_community['total_fish_activity'] >= total_activity_90th).astype(int)
    print(f"Very high activity (90th percentile, threshold={total_activity_90th:.1f}): {df_community['high_activity_90th'].mean():.1%} of periods")

    # Any biological activity vs none
    # Question: "Is there any fish calling happening at all?"
    df_community['any_activity'] = (df_community['total_fish_activity'] > 0).astype(int)
    print(f"Any activity (threshold=0): {df_community['any_activity'].mean():.1%} of periods")

    # Multiple species active vs single/none
    # Question: "Are multiple species interacting/calling together?"
    df_community['multi_species_active'] = (df_community['num_active_species'] >= 2).astype(int)
    print(f"Multi-species activity (≥2 species): {df_community['multi_species_active'].mean():.1%} of periods")

    print(f"Fish community metrics created. Sample statistics:")
    print(f"Total activity - Mean: {df_community['total_fish_activity'].mean():.2f}, Max: {df_community['total_fish_activity'].max():.0f}")
    print(f"Active species - Mean: {df_community['num_active_species'].mean():.2f}, Max: {df_community['num_active_species'].max():.0f}")
    print(f"High activity (75th): {df_community['high_activity_75th'].mean():.1%}")
    print(f"High activity (90th): {df_community['high_activity_90th'].mean():.1%}")
    print(f"Any activity: {df_community['any_activity'].mean():.1%}")
    print(f"Multi-species active: {df_community['multi_species_active'].mean():.1%}")

    # ====================================================================
    # MARINE COMMUNITY METRICS (Fish + Dolphins)
    # ====================================================================

    df_marine = None
    marine_activity_75th = None
    marine_activity_90th = None

    if df_marine_community is not None:
        print("\n" + "="*70)
        print("CREATING MARINE COMMUNITY METRICS (FISH + DOLPHINS)")
        print("="*70)

        # Create marine master dataset by merging with enhanced marine community data
        # Use the marine community data which includes fish + dolphin metrics

        # First, get marine species columns from marine community data
        marine_species_cols = [col for col in df_marine_community.columns 
                             if col not in ['datetime', 'station', 'year', 'total_fish_intensity',
                                          'num_active_fish_species', 'max_fish_intensity',
                                          'dolphin_count', 'dolphin_intensity', 'total_marine_intensity',
                                          'num_active_marine_species', 'max_marine_intensity']]

        # Get just the fish species from the marine data (should match fish_species)
        marine_fish_species = [col for col in marine_species_cols if col in fish_species]

        print(f"Creating marine community dataset with {len(marine_fish_species)} fish species + dolphins")

        # Create marine master dataset
        df_marine_master = df_indices.merge(
            df_marine_community[['datetime', 'station', 'year'] + marine_fish_species + 
                               ['dolphin_intensity', 'total_marine_intensity', 
                                'num_active_marine_species', 'max_marine_intensity']],
            on=['datetime', 'station', 'year'],
            how='left'
        )

        # Merge with environmental and temporal data (same as fish-only)
        df_marine_master = df_marine_master.merge(
            df_env[['datetime', 'station', 'year', 'Water temp (°C)', 'Water depth (m)',
                    'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)']],
            on=['datetime', 'station', 'year'],
            how='left'
        )

        df_marine_master = df_marine_master.merge(
            df_temporal[['datetime', 'station', 'year', 'hour', 'month', 'season', 'time_period']],
            on=['datetime', 'station', 'year'],
            how='left'
        )

        # Rename time_period to diel_period for consistency
        df_marine_master = df_marine_master.rename(columns={'time_period': 'diel_period'})

        print(f"Marine master dataset shape: {df_marine_master.shape}")

        # Create marine community dataset
        df_marine = df_marine_master.copy()

        # Use the pre-computed marine community metrics from notebook 08
        print("Using pre-computed marine community metrics from notebook 08...")

        # Rename marine metrics to match fish naming convention for consistency
        df_marine['total_marine_activity'] = df_marine['total_marine_intensity']
        df_marine['num_active_marine_species'] = df_marine['num_active_marine_species']
        df_marine['max_marine_activity'] = df_marine['max_marine_intensity']

        # Add dolphin-specific metrics
        df_marine['dolphin_activity'] = df_marine['dolphin_intensity']

        # Calculate activity diversity for marine community
        all_marine_species = marine_fish_species + ['dolphin_intensity']
        df_marine['marine_activity_diversity'] = df_marine[all_marine_species].std(axis=1) / (df_marine[all_marine_species].mean(axis=1) + 0.01)

        print(f"Marine activity range: {df_marine['total_marine_activity'].min():.0f} to {df_marine['total_marine_activity'].max():.0f}")
        print(f"Marine species range: {df_marine['num_active_marine_species'].min():.0f} to {df_marine['num_active_marine_species'].max():.0f}")
        print(f"Dolphin activity range: {df_marine['dolphin_activity'].min():.0f} to {df_marine['dolphin_activity'].max():.0f}")

        # Create binary classification targets for marine community
        print("\nCreating marine community binary classification targets...")

        # High vs low marine activity (75th percentile threshold)
        marine_activity_75th = df_marine['total_marine_activity'].quantile(0.75)
        df_marine['high_marine_activity_75th'] = (df_marine['total_marine_activity'] >= marine_activity_75th).astype(int)
        print(f"High marine activity (75th percentile, threshold={marine_activity_75th:.1f}): {df_marine['high_marine_activity_75th'].mean():.1%} of periods")

        # Very high marine activity (90th percentile threshold)
        marine_activity_90th = df_marine['total_marine_activity'].quantile(0.90)
        df_marine['high_marine_activity_90th'] = (df_marine['total_marine_activity'] >= marine_activity_90th).astype(int)
        print(f"Very high marine activity (90th percentile, threshold={marine_activity_90th:.1f}): {df_marine['high_marine_activity_90th'].mean():.1%} of periods")

        # Any marine biological activity vs none
        df_marine['any_marine_activity'] = (df_marine['total_marine_activity'] > 0).astype(int)
        print(f"Any marine activity (threshold=0): {df_marine['any_marine_activity'].mean():.1%} of periods")

        # Multiple marine species active vs single/none  
        df_marine['multi_marine_species_active'] = (df_marine['num_active_marine_species'] >= 2).astype(int)
        print(f"Multi-species marine activity (≥2 species): {df_marine['multi_marine_species_active'].mean():.1%} of periods")

        # Dolphin-specific targets
        df_marine['dolphin_present'] = (df_marine['dolphin_activity'] > 0).astype(int)
        print(f"Dolphin presence: {df_marine['dolphin_present'].mean():.1%} of periods")

        print(f"\nMarine community metrics created. Sample statistics:")
        print(f"Total marine activity - Mean: {df_marine['total_marine_activity'].mean():.2f}, Max: {df_marine['total_marine_activity'].max():.0f}")
        print(f"Active marine species - Mean: {df_marine['num_active_marine_species'].mean():.2f}, Max: {df_marine['num_active_marine_species'].max():.0f}")
        print(f"Dolphin activity - Mean: {df_marine['dolphin_activity'].mean():.2f}, Max: {df_marine['dolphin_activity'].max():.0f}")
        print(f"High marine activity (75th): {df_marine['high_marine_activity_75th'].mean():.1%}")
        print(f"High marine activity (90th): {df_marine['high_marine_activity_90th'].mean():.1%}")

        # Comparison between fish-only and marine community
        print("\n" + "="*50)
        print("FISH vs MARINE COMMUNITY COMPARISON")
        print("="*50)

        # Match periods between datasets for fair comparison
        common_indices = df_community.index.intersection(df_marine.index)

        if len(common_indices) > 0:
            fish_mean = df_community.loc[common_indices, 'total_fish_activity'].mean()
            marine_mean = df_marine.loc[common_indices, 'total_marine_activity'].mean()

            print(f"Mean activity comparison (matched periods, n={len(common_indices):,}):")
            print(f"  Fish-only community: {fish_mean:.2f}")
            print(f"  Marine community (fish + dolphins): {marine_mean:.2f}")
            print(f"  Marine enhancement: +{((marine_mean - fish_mean) / fish_mean * 100):.1f}%")

            fish_high_75 = df_community.loc[common_indices, 'high_activity_75th'].mean()
            marine_high_75 = df_marine.loc[common_indices, 'high_marine_activity_75th'].mean()

            print(f"High activity periods (75th percentile):")
            print(f"  Fish-only: {fish_high_75:.1%}")
            print(f"  Marine: {marine_high_75:.1%}")

    else:
        print("\n⚠️ Marine community data not available - skipping marine metrics")
        print("Run notebook 07 first to generate enhanced marine community dataset")
    return df_community, df_marine


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Model Development for Community Activity Detection

    Training multiple classifiers to predict community-level biological activity using acoustic indices.

    ## Machine Learning Algorithms Explained

    We test four different classification algorithms, each with distinct strengths for biological screening:

    ### 1. Logistic Regression
    - **How it works**: Linear combination of features → probability via sigmoid function
    - **Strengths**: Fast, interpretable coefficients, stable predictions
    - **Best for**: Understanding which indices have linear relationships with biology
    - **Interpretation**: Coefficient sign/magnitude shows feature importance and direction

    ### 2. Decision Tree

    - **How it works**: Sequential yes/no questions creating rule-based decisions
    - **Strengths**: Highly interpretable, handles non-linear patterns, no assumptions about data distribution
    - **Best for**: Creating simple screening rules (e.g., "if index X > threshold AND temperature > Y, then high activity")
    - **Interpretation**: Tree branches show exact decision logic

    ### 3. Random Forest

    - **How it works**: Combines predictions from 100 different decision trees
    - **Strengths**: Handles complex interactions, resistant to overfitting, robust to outliers
    - **Best for**: Maximizing predictive performance while maintaining some interpretability
    - **Interpretation**: Feature importance ranks show which indices contribute most to predictions

    ### 4. Gradient Boosting  ** not implemented due to computational constraints

    - **How it works**: Sequentially builds models, each correcting previous model's mistakes
    - **Strengths**: Often highest accuracy, excellent at detecting subtle patterns
    - **Best for**: Maximum screening performance when interpretability is less critical
    - **Interpretation**: Feature importance shows cumulative contribution across all boosting iterations

    ## Evaluation Strategy

    For biological screening, we care more about **practical performance** than traditional accuracy:

    - **F1 Score**: Balances precision (few false alarms) with recall (catch most activity)
    - **Cross-validation**: 5-fold stratified to ensure robust performance estimates
    - **Class balance**: Account for unequal representation of active vs inactive periods
    """
    )
    return


@app.cell
def _(
    DecisionTreeClassifier,
    LogisticRegression,
    RandomForestClassifier,
    StandardScaler,
    StratifiedKFold,
    accuracy_score,
    cohen_kappa_score,
    cross_val_score,
    df_community,
    df_marine,
    f1_score,
    index_cols,
    precision_score,
    recall_score,
    train_test_split,
):
    # Prepare data for comparative community activity modeling
    print("Preparing data for COMPARATIVE community activity modeling...")
    print("="*80)
    print("Training models for both fish-only and marine (fish + dolphin) communities")
    print("="*80)

    # Feature Selection Strategy
    # Combine acoustic indices with key environmental and temporal variables
    # This tests whether indices add value beyond simple environmental predictors
    modeling_cols = index_cols + ['Water temp (°C)', 'Water depth (m)', 'hour', 'month']

    # Define target sets for both community types
    fish_target_cols = ['high_activity_75th', 'high_activity_90th', 'any_activity', 'multi_species_active']
    marine_target_cols = ['high_marine_activity_75th', 'high_marine_activity_90th', 'any_marine_activity', 'multi_marine_species_active', 'dolphin_present']

    print(f"Feature categories:")
    print(f"  - Acoustic indices: {len(index_cols)} variables")
    print(f"  - Environmental: 2 variables (temperature, depth)")
    print(f"  - Temporal: 2 variables (hour, month)")
    print(f"  - Total features: {len(modeling_cols)}")

    print(f"\nTarget categories:")
    print(f"  - Fish-only community: {len(fish_target_cols)} targets")
    print(f"  - Marine community: {len(marine_target_cols)} targets")

    # Model configurations with biological screening in mind
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(
            max_depth=8,           # Prevent overfitting while allowing complexity
            min_samples_leaf=10,   # Ensure robust leaf nodes
            random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=100,      # Good balance of performance vs speed
            max_depth=8,           # Match decision tree depth
            min_samples_leaf=5,    # Allow slightly smaller leaves in ensemble
            random_state=42
        ),
    }
    print(f"Models configured: {list(models.keys())}")

    # Initialize results storage
    all_model_results = {}
    all_modeling_datasets = {}
    all_scalers = {}

    # =====================================================================
    # FISH-ONLY COMMUNITY MODELING
    # =====================================================================

    print("\n" + "="*60)
    print("FISH-ONLY COMMUNITY MODEL TRAINING")
    print("="*60)

    # Prepare fish-only dataset
    df_fish_modeling = df_community[modeling_cols + fish_target_cols].dropna()
    print(f"Fish modeling dataset: {df_fish_modeling.shape[0]:,} complete samples")
    print(f"Fish data completeness: {len(df_fish_modeling)/len(df_community):.1%} of original data")

    # Feature matrix preparation for fish
    X_fish_features = df_fish_modeling[modeling_cols]

    # Standardization for fish data
    print(f"\nStandardizing fish community features...")
    print(f"Before scaling - Temperature range: {X_fish_features['Water temp (°C)'].min():.1f} to {X_fish_features['Water temp (°C)'].max():.1f}")
    if 'ACTspFract' in X_fish_features.columns:
        print(f"Before scaling - ACTspFract range: {X_fish_features['ACTspFract'].min():.3f} to {X_fish_features['ACTspFract'].max():.3f}")

    scaler_fish = StandardScaler()
    X_fish_scaled = scaler_fish.fit_transform(X_fish_features)
    print(f"After scaling - All features have mean≈0, std≈1")

    # Store fish datasets and scaler
    all_modeling_datasets['fish'] = df_fish_modeling
    all_scalers['fish'] = scaler_fish

    # Train fish models
    fish_model_results = {}

    for target_name in fish_target_cols:
        print(f"\nTraining fish models for: {target_name}")
        y_target = df_fish_modeling[target_name]

        # Check class balance
        class_balance = y_target.value_counts(normalize=True)
        print(f"Class balance: {class_balance.to_dict()}")

        if y_target.std() == 0:  # Skip if no variance
            print(f"Skipping {target_name} - no variance in target")
            continue

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_fish_scaled, y_target, test_size=0.3, random_state=42, stratify=y_target
        )

        target_results = {}

        for model_name, model in models.items():
            # Create fresh model instance
            model_instance = type(model)(**model.get_params())

            # Train model
            model_instance.fit(X_train, y_train)

            # Predictions
            y_pred = model_instance.predict(X_test)
            y_prob = model_instance.predict_proba(X_test)[:, 1] if hasattr(model_instance, 'predict_proba') else y_pred

            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
            recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
            kappa = cohen_kappa_score(y_test, y_pred)

            # Cross-validation
            cv_model = type(model)(**model.get_params())
            cv_scores = cross_val_score(cv_model, X_fish_scaled, y_target, cv=StratifiedKFold(5), scoring='f1')

            target_results[model_name] = {
                'model': model_instance,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'kappa': kappa,
                'cv_f1_mean': cv_scores.mean(),
                'cv_f1_std': cv_scores.std(),
                'y_test': y_test,
                'y_pred': y_pred,
                'y_prob': y_prob,
                'community_type': 'fish'
            }

            print(f"  {model_name}: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")

        fish_model_results[target_name] = target_results

    all_model_results['fish'] = fish_model_results

    # =====================================================================
    # MARINE COMMUNITY MODELING (if available)
    # =====================================================================

    marine_model_results = {}
    X_marine_scaled = None
    df_marine_modeling = None
    scaler_marine = None

    if df_marine is not None:
        print("\n" + "="*60)
        print("MARINE COMMUNITY (FISH + DOLPHIN) MODEL TRAINING")
        print("="*60)

        # Prepare marine dataset
        df_marine_modeling = df_marine[modeling_cols + marine_target_cols].dropna()
        print(f"Marine modeling dataset: {df_marine_modeling.shape[0]:,} complete samples")
        print(f"Marine data completeness: {len(df_marine_modeling)/len(df_marine):.1%} of original marine data")

        # Feature matrix preparation for marine
        X_marine_features = df_marine_modeling[modeling_cols]

        # Standardization for marine data
        print(f"\nStandardizing marine community features...")
        print(f"Before scaling - Temperature range: {X_marine_features['Water temp (°C)'].min():.1f} to {X_marine_features['Water temp (°C)'].max():.1f}")
        if 'ACTspFract' in X_marine_features.columns:
            print(f"Before scaling - ACTspFract range: {X_marine_features['ACTspFract'].min():.3f} to {X_marine_features['ACTspFract'].max():.3f}")

        scaler_marine = StandardScaler()
        X_marine_scaled = scaler_marine.fit_transform(X_marine_features)
        print(f"After scaling - All features have mean≈0, std≈1")

        # Store marine datasets and scaler
        all_modeling_datasets['marine'] = df_marine_modeling
        all_scalers['marine'] = scaler_marine

        # Train marine models
        for target_name in marine_target_cols:
            print(f"\nTraining marine models for: {target_name}")
            y_target = df_marine_modeling[target_name]

            # Check class balance
            class_balance = y_target.value_counts(normalize=True)
            print(f"Class balance: {class_balance.to_dict()}")

            if y_target.std() == 0:  # Skip if no variance
                print(f"Skipping {target_name} - no variance in target")
                continue

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_marine_scaled, y_target, test_size=0.3, random_state=42, stratify=y_target
            )

            target_results = {}

            for model_name, model in models.items():
                # Create fresh model instance
                model_instance = type(model)(**model.get_params())

                # Train model
                model_instance.fit(X_train, y_train)

                # Predictions
                y_pred = model_instance.predict(X_test)
                y_prob = model_instance.predict_proba(X_test)[:, 1] if hasattr(model_instance, 'predict_proba') else y_pred

                # Metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
                recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
                kappa = cohen_kappa_score(y_test, y_pred)

                # Cross-validation
                cv_model = type(model)(**model.get_params())
                cv_scores = cross_val_score(cv_model, X_marine_scaled, y_target, cv=StratifiedKFold(5), scoring='f1')

                target_results[model_name] = {
                    'model': model_instance,
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'kappa': kappa,
                    'cv_f1_mean': cv_scores.mean(),
                    'cv_f1_std': cv_scores.std(),
                    'y_test': y_test,
                    'y_pred': y_pred,
                    'y_prob': y_prob,
                    'community_type': 'marine'
                }

                print(f"  {model_name}: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")

            marine_model_results[target_name] = target_results

        all_model_results['marine'] = marine_model_results

    else:
        print("\n⚠️ Marine community data not available - training fish-only models only")

    # =====================================================================
    # COMPARATIVE SUMMARY
    # =====================================================================

    print("\n" + "="*80)
    print("COMPARATIVE MODELING SUMMARY")
    print("="*80)

    print(f"Fish-only community: {len(fish_model_results)} targets trained")
    if marine_model_results:
        print(f"Marine community: {len(marine_model_results)} targets trained")
        print(f"Total model training runs: {(len(fish_model_results) + len(marine_model_results)) * len(models)}")
    else:
        print(f"Marine community: Not available")
        print(f"Total model training runs: {len(fish_model_results) * len(models)}")

    print(f"\nModel training complete!")
    return (
        X_fish_scaled,
        X_marine_scaled,
        all_model_results,
        all_modeling_datasets,
        fish_target_cols,
        marine_target_cols,
        modeling_cols,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Feature Importance Analysis

    Understanding which acoustic indices and environmental variables are most important for detecting community activity.
    """
    )
    return


@app.cell
def _(
    X_fish_scaled,
    X_marine_scaled,
    all_model_results,
    all_modeling_datasets,
    fish_target_cols,
    marine_target_cols,
    modeling_cols,
    mutual_info_classif,
    np,
    pd,
):
    # Feature importance analysis for both community types
    print("Analyzing feature importance for both community types...")
    print("="*70)

    all_feature_importance_results = {}

    # =====================================================================
    # FISH COMMUNITY FEATURE IMPORTANCE
    # =====================================================================

    print("\nFISH COMMUNITY FEATURE IMPORTANCE")
    print("="*50)

    fish_feature_importance = {}

    if 'fish' in all_model_results and X_fish_scaled is not None:
        _df_fish_modeling = all_modeling_datasets['fish']

        for target_name in fish_target_cols:
            if target_name not in all_model_results['fish']:
                continue

            _y_target = _df_fish_modeling[target_name]

            # Mutual information feature importance
            mi_scores = mutual_info_classif(X_fish_scaled, _y_target, random_state=42)

            # Random Forest feature importance (if available)
            rf_model = all_model_results['fish'][target_name].get('Random Forest', {}).get('model')
            rf_importance = rf_model.feature_importances_ if rf_model else np.zeros(len(modeling_cols))

            # Create feature importance dataframe
            importance_df = pd.DataFrame({
                'feature': modeling_cols,
                'mutual_info': mi_scores,
                'rf_importance': rf_importance,
                'community_type': 'fish',
                'target': target_name
            }).sort_values('mutual_info', ascending=False)

            fish_feature_importance[target_name] = importance_df

            print(f"\nTop 5 features for FISH {target_name}:")
            print(importance_df[['feature', 'mutual_info', 'rf_importance']].head())

        all_feature_importance_results['fish'] = fish_feature_importance

    # =====================================================================
    # MARINE COMMUNITY FEATURE IMPORTANCE
    # =====================================================================

    marine_feature_importance = {}

    if 'marine' in all_model_results and X_marine_scaled is not None:
        print("\nMARINE COMMUNITY FEATURE IMPORTANCE")
        print("="*50)

        _df_marine_modeling = all_modeling_datasets['marine']

        for _target_name in marine_target_cols:
            if _target_name not in all_model_results['marine']:
                continue

            _y_target = _df_marine_modeling[_target_name]

            # Mutual information feature importance
            mi_scores = mutual_info_classif(X_marine_scaled, _y_target, random_state=42)

            # Random Forest feature importance (if available)
            rf_model = all_model_results['marine'][_target_name].get('Random Forest', {}).get('model')
            rf_importance = rf_model.feature_importances_ if rf_model else np.zeros(len(modeling_cols))

            # Create feature importance dataframe
            importance_df = pd.DataFrame({
                'feature': modeling_cols,
                'mutual_info': mi_scores,
                'rf_importance': rf_importance,
                'community_type': 'marine', 
                'target': _target_name
            }).sort_values('mutual_info', ascending=False)

            marine_feature_importance[_target_name] = importance_df

            print(f"\nTop 5 features for MARINE {_target_name}:")
            print(importance_df[['feature', 'mutual_info', 'rf_importance']].head())

        all_feature_importance_results['marine'] = marine_feature_importance

    else:
        print("\nMarine community feature importance not available - marine data not loaded")

    # =====================================================================
    # COMPARATIVE FEATURE IMPORTANCE SUMMARY
    # =====================================================================

    print("\n" + "="*70)
    print("COMPARATIVE FEATURE IMPORTANCE SUMMARY")
    print("="*70)

    # Find common high-importance features across both communities
    if 'fish' in all_feature_importance_results and 'marine' in all_feature_importance_results:
        print("\nComparing feature importance between fish-only and marine communities...")

        # Get top features from comparable targets
        _fish_high_activity = fish_feature_importance.get('high_activity_75th')
        _marine_high_activity = marine_feature_importance.get('high_marine_activity_75th')

        if _fish_high_activity is not None and _marine_high_activity is not None:
            fish_top_5 = set(_fish_high_activity.head(5)['feature'])
            marine_top_5 = set(_marine_high_activity.head(5)['feature'])

            common_features = fish_top_5.intersection(marine_top_5)
            fish_unique = fish_top_5 - marine_top_5
            _marine_unique = marine_top_5 - fish_top_5

            print(f"\nFeature importance comparison (high activity targets):")
            print(f"Common top-5 features: {list(common_features)}")
            print(f"Fish-only top-5 unique: {list(fish_unique)}")
            print(f"Marine top-5 unique: {list(_marine_unique)}")
    return (all_feature_importance_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Comparative Model Performance Analysis

    Comparing fish-only vs. marine community model performance to understand the value of including dolphins in biological screening.
    """
    )
    return


@app.cell
def _(all_model_results, pd):
    # Comparative model performance analysis
    print("COMPARATIVE MODEL PERFORMANCE ANALYSIS")
    print("="*60)

    performance_results = []

    # Collect all performance metrics
    for community_type, community_results in all_model_results.items():
        for _target_name_perf, _target_results in community_results.items():
            for _model_name, _results in _target_results.items():
                performance_results.append({
                    'community_type': community_type,
                    'target': _target_name_perf,
                    'model': _model_name,
                    'accuracy': _results['accuracy'],
                    'precision': _results['precision'],
                    'recall': _results['recall'],
                    'f1': _results['f1'],
                    'kappa': _results['kappa'],
                    'cv_f1_mean': _results['cv_f1_mean'],
                    'cv_f1_std': _results['cv_f1_std']
                })

    # Convert to DataFrame for easier analysis
    performance_df = pd.DataFrame(performance_results)

    if len(performance_df) > 0:
        print(f"\nPerformance summary across {len(performance_df)} model runs:")
        print(performance_df.groupby(['community_type', 'model']).agg({
            'f1': ['mean', 'std'],
            'accuracy': ['mean', 'std'],
            'precision': ['mean', 'std'],
            'recall': ['mean', 'std']
        }).round(3))

        # Compare fish vs marine performance if both available
        if 'fish' in all_model_results and 'marine' in all_model_results:
            print("\n" + "="*50)
            print("FISH vs MARINE COMMUNITY PERFORMANCE COMPARISON")
            print("="*50)

            # Compare equivalent targets (high activity 75th percentile)
            fish_high_activity = performance_df[
                (performance_df['community_type'] == 'fish') & 
                (performance_df['target'] == 'high_activity_75th')
            ]

            marine_high_activity = performance_df[
                (performance_df['community_type'] == 'marine') & 
                (performance_df['target'] == 'high_marine_activity_75th')
            ]

            if len(fish_high_activity) > 0 and len(marine_high_activity) > 0:
                print("\nHigh Activity Detection (75th percentile threshold):")
                print("\nFish-only community performance:")
                print(fish_high_activity[['model', 'f1', 'precision', 'recall']].round(3))

                print("\nMarine community (fish + dolphin) performance:")
                print(marine_high_activity[['model', 'f1', 'precision', 'recall']].round(3))

                # Calculate improvement
                fish_mean_f1 = fish_high_activity['f1'].mean()
                marine_mean_f1 = marine_high_activity['f1'].mean()

                improvement = ((marine_mean_f1 - fish_mean_f1) / fish_mean_f1) * 100

                print(f"\nOverall F1 Score Comparison:")
                print(f"Fish-only community: {fish_mean_f1:.3f}")
                print(f"Marine community: {marine_mean_f1:.3f}")
                print(f"Improvement with dolphins: {improvement:+.1f}%")

            # Dolphin-specific analysis
            dolphin_results = performance_df[
                (performance_df['community_type'] == 'marine') & 
                (performance_df['target'] == 'dolphin_present')
            ]

            if len(dolphin_results) > 0:
                print("\n" + "-"*40)
                print("DOLPHIN PRESENCE DETECTION PERFORMANCE")
                print("-"*40)
                print(dolphin_results[['model', 'f1', 'precision', 'recall']].round(3))

                best_dolphin_model = dolphin_results.loc[dolphin_results['f1'].idxmax()]
                print(f"\nBest model for dolphin detection: {best_dolphin_model['model']} (F1={best_dolphin_model['f1']:.3f})")

    else:
        print("No performance results available for comparison")
    return (performance_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Temporal Pattern Concordance Analysis

    Comparing how well acoustic indices capture the same temporal patterns (diel and seasonal) as manual detections for both fish-only and marine communities.
    """
    )
    return


@app.cell
def _(df_community, df_marine, modeling_cols, pd, spearmanr):
    # Temporal pattern concordance analysis
    print("TEMPORAL PATTERN CONCORDANCE ANALYSIS")
    print("="*60)

    # Get top 10 acoustic indices for manageable analysis
    index_cols_subset = [col for col in modeling_cols if col not in ['Water temp (°C)', 'Water depth (m)', 'hour', 'month']][:10]

    all_concordance_results = {}

    # =====================================================================
    # FISH COMMUNITY TEMPORAL PATTERNS
    # =====================================================================

    print("\nFISH COMMUNITY TEMPORAL PATTERNS")
    print("="*40)

    # 1. Fish Diel Pattern Analysis
    fish_diel_patterns = df_community.groupby('hour').agg({
        'total_fish_activity': 'mean',
        'num_active_species': 'mean',
        **{idx: 'mean' for idx in index_cols_subset}
    }).reset_index()

    # 2. Fish Seasonal Pattern Analysis  
    fish_seasonal_patterns = df_community.groupby('month').agg({
        'total_fish_activity': 'mean',
        'num_active_species': 'mean', 
        **{idx: 'mean' for idx in index_cols_subset}
    }).reset_index()

    # Calculate fish correlations
    fish_diel_correlations = {}
    fish_seasonal_correlations = {}

    for idx in index_cols_subset:
        # Diel correlations
        diel_corr, diel_p = spearmanr(fish_diel_patterns['total_fish_activity'], fish_diel_patterns[idx])
        fish_diel_correlations[idx] = {'correlation': diel_corr, 'p_value': diel_p}

        # Seasonal correlations
        seasonal_corr, seasonal_p = spearmanr(fish_seasonal_patterns['total_fish_activity'], fish_seasonal_patterns[idx])
        fish_seasonal_correlations[idx] = {'correlation': seasonal_corr, 'p_value': seasonal_p}

    # Convert to dataframes
    fish_diel_corr_df = pd.DataFrame(fish_diel_correlations).T.sort_values('correlation', key=abs, ascending=False)
    fish_seasonal_corr_df = pd.DataFrame(fish_seasonal_correlations).T.sort_values('correlation', key=abs, ascending=False)

    print("\nTop 5 indices for FISH diel pattern concordance:")
    print(fish_diel_corr_df.head().round(3))

    print("\nTop 5 indices for FISH seasonal pattern concordance:")
    print(fish_seasonal_corr_df.head().round(3))

    all_concordance_results['fish'] = {
        'diel_patterns': fish_diel_patterns,
        'seasonal_patterns': fish_seasonal_patterns,
        'diel_correlations': fish_diel_corr_df,
        'seasonal_correlations': fish_seasonal_corr_df
    }

    # =====================================================================
    # MARINE COMMUNITY TEMPORAL PATTERNS (if available)
    # =====================================================================

    if df_marine is not None:
        print("\nMARINE COMMUNITY TEMPORAL PATTERNS")
        print("="*40)

        # 1. Marine Diel Pattern Analysis
        marine_diel_patterns = df_marine.groupby('hour').agg({
            'total_marine_activity': 'mean',
            'num_active_marine_species': 'mean',
            'dolphin_activity': 'mean',
            **{idx: 'mean' for idx in index_cols_subset}
        }).reset_index()

        # 2. Marine Seasonal Pattern Analysis
        marine_seasonal_patterns = df_marine.groupby('month').agg({
            'total_marine_activity': 'mean', 
            'num_active_marine_species': 'mean',
            'dolphin_activity': 'mean',
            **{idx: 'mean' for idx in index_cols_subset}
        }).reset_index()

        # Calculate marine correlations
        marine_diel_correlations = {}
        marine_seasonal_correlations = {}

        for idx in index_cols_subset:
            # Diel correlations
            diel_corr, diel_p = spearmanr(marine_diel_patterns['total_marine_activity'], marine_diel_patterns[idx])
            marine_diel_correlations[idx] = {'correlation': diel_corr, 'p_value': diel_p}

            # Seasonal correlations
            seasonal_corr, seasonal_p = spearmanr(marine_seasonal_patterns['total_marine_activity'], marine_seasonal_patterns[idx])
            marine_seasonal_correlations[idx] = {'correlation': seasonal_corr, 'p_value': seasonal_p}

        # Convert to dataframes
        marine_diel_corr_df = pd.DataFrame(marine_diel_correlations).T.sort_values('correlation', key=abs, ascending=False)
        marine_seasonal_corr_df = pd.DataFrame(marine_seasonal_correlations).T.sort_values('correlation', key=abs, ascending=False)

        print("\nTop 5 indices for MARINE diel pattern concordance:")
        print(marine_diel_corr_df.head().round(3))

        print("\nTop 5 indices for MARINE seasonal pattern concordance:")
        print(marine_seasonal_corr_df.head().round(3))

        all_concordance_results['marine'] = {
            'diel_patterns': marine_diel_patterns,
            'seasonal_patterns': marine_seasonal_patterns,
            'diel_correlations': marine_diel_corr_df,
            'seasonal_correlations': marine_seasonal_corr_df
        }

        # =====================================================================
        # COMPARATIVE CONCORDANCE ANALYSIS
        # =====================================================================

        print("\n" + "="*60)
        print("FISH vs MARINE TEMPORAL CONCORDANCE COMPARISON")
        print("="*60)

        # Compare which indices are most consistent between fish and marine patterns
        common_diel_indices = set(fish_diel_corr_df.head(5).index).intersection(set(marine_diel_corr_df.head(5).index))
        common_seasonal_indices = set(fish_seasonal_corr_df.head(5).index).intersection(set(marine_seasonal_corr_df.head(5).index))

        print(f"\nCommon top-5 diel pattern indices: {list(common_diel_indices)}")
        print(f"Common top-5 seasonal pattern indices: {list(common_seasonal_indices)}")

        # Calculate concordance improvement with marine data
        fish_diel_mean_concordance = abs(fish_diel_corr_df.head(5)['correlation']).mean()
        marine_diel_mean_concordance = abs(marine_diel_corr_df.head(5)['correlation']).mean()

        diel_improvement = ((marine_diel_mean_concordance - fish_diel_mean_concordance) / fish_diel_mean_concordance) * 100

        print(f"\nDiel pattern concordance comparison:")
        print(f"Fish-only mean |correlation|: {fish_diel_mean_concordance:.3f}")
        print(f"Marine mean |correlation|: {marine_diel_mean_concordance:.3f}")
        print(f"Improvement with dolphins: {diel_improvement:+.1f}%")

    else:
        print("\nMarine community temporal analysis not available - marine data not loaded")
    return (all_concordance_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Final Analysis Summary and Recommendations

    Synthesizing findings from the comparative fish-only vs. marine community analysis to provide actionable insights for biological screening and monitoring.
    """
    )
    return


@app.cell
def _(
    all_concordance_results,
    all_feature_importance_results,
    all_model_results,
    performance_df,
):
    # Final analysis summary and recommendations
    print("FINAL ANALYSIS SUMMARY AND RECOMMENDATIONS")
    print("="*80)

    recommendations = []

    # 1. Model Performance Assessment
    if len(performance_df) > 0:
        print("\n1. MODEL PERFORMANCE ASSESSMENT")
        print("="*40)

        # Overall best performers
        best_models = performance_df.loc[performance_df.groupby(['community_type'])['f1'].idxmax()]

        for _, row in best_models.iterrows():
            print(f"Best {row['community_type']} model: {row['model']} for {row['target']} (F1={row['f1']:.3f})")

        # Marine vs Fish comparison
        if 'fish' in all_model_results and 'marine' in all_model_results:
            fish_results = performance_df[performance_df['community_type'] == 'fish']
            marine_results = performance_df[performance_df['community_type'] == 'marine']

            fish_mean_f1 = fish_results['f1'].mean()
            marine_mean_f1 = marine_results['f1'].mean()

            if marine_mean_f1 > fish_mean_f1:
                improvement = ((marine_mean_f1 - fish_mean_f1) / fish_mean_f1) * 100
                recommendations.append(
                    f"✅ Marine community models show {improvement:.1f}% average improvement over fish-only models"
                )
                recommendations.append(
                    "Recommendation: Include dolphin data in biological screening models for enhanced performance"
                )
            else:
                decline = ((fish_mean_f1 - marine_mean_f1) / fish_mean_f1) * 100
                recommendations.append(
                    f"⚠️ Marine community models show {decline:.1f}% average decline vs fish-only models"
                )
                recommendations.append(
                    "Recommendation: Evaluate if dolphin integration method needs refinement"
                )

    # 2. Feature Importance Insights
    print("\n2. FEATURE IMPORTANCE INSIGHTS")
    print("="*40)

    if 'fish' in all_feature_importance_results and 'marine' in all_feature_importance_results:
        # Find most stable features across both community types
        fish_features = all_feature_importance_results['fish']
        marine_features = all_feature_importance_results['marine']

        # Get high activity features as representative
        if 'high_activity_75th' in fish_features and 'high_marine_activity_75th' in marine_features:
            fish_top_features = set(fish_features['high_activity_75th'].head(5)['feature'])
            marine_top_features = set(marine_features['high_marine_activity_75th'].head(5)['feature'])

            stable_features = fish_top_features.intersection(marine_top_features)

            if len(stable_features) > 0:
                print(f"Most stable acoustic indices across both communities: {list(stable_features)}")
                recommendations.append(
                    f"Recommendation: Prioritize these {len(stable_features)} acoustic indices for robust biological screening"
                )

            marine_unique = marine_top_features - fish_top_features
            if len(marine_unique) > 0:
                print(f"Indices uniquely important for marine community: {list(marine_unique)}")
                recommendations.append(
                    "Recommendation: Consider marine-specific indices when dolphin activity is suspected"
                )

    # 3. Temporal Pattern Insights
    print("\n3. TEMPORAL PATTERN INSIGHTS")
    print("="*40)

    if 'fish' in all_concordance_results and 'marine' in all_concordance_results:
        fish_concordance = all_concordance_results['fish']
        marine_concordance = all_concordance_results['marine']

        # Compare mean concordance strengths
        fish_diel_strength = abs(fish_concordance['diel_correlations'].head(3)['correlation']).mean()
        marine_diel_strength = abs(marine_concordance['diel_correlations'].head(3)['correlation']).mean()

        print(f"Fish community diel pattern strength: {fish_diel_strength:.3f}")
        print(f"Marine community diel pattern strength: {marine_diel_strength:.3f}")

        if marine_diel_strength > fish_diel_strength:
            recommendations.append(
                "✅ Marine community shows stronger temporal pattern concordance - dolphins enhance signal detectability"
            )

        # Get best temporal indices
        best_diel_index = marine_concordance['diel_correlations'].index[0]
        best_seasonal_index = marine_concordance['seasonal_correlations'].index[0]

        recommendations.append(
            f"Recommendation: Use {best_diel_index} for diel pattern detection and {best_seasonal_index} for seasonal monitoring"
        )

    # 4. Practical Implementation Recommendations
    print("\n4. PRACTICAL IMPLEMENTATION RECOMMENDATIONS")
    print("="*50)

    if len(recommendations) > 0:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

    # 5. Next Steps
    print("\n5. RECOMMENDED NEXT STEPS")
    print("="*30)

    next_steps = [
        "Deploy best-performing models on new acoustic data for validation",
        "Implement real-time biological activity screening using identified key indices",
        "Develop automated alerting system for high marine activity periods",
        "Create dashboard visualization of temporal patterns for monitoring staff",
        "Plan targeted manual validation during predicted high-activity periods",
    ]

    if 'marine' in all_model_results:
        next_steps.append("Evaluate dolphin detection performance in different environmental conditions")
        next_steps.append("Investigate seasonal patterns in marine community interactions")

    for i, step in enumerate(next_steps, 1):
        print(f"{i}. {step}")

    print(f"\n" + "="*80)
    print("COMPARATIVE ANALYSIS COMPLETE ✅")
    print(f"Marine community integration {'successful' if 'marine' in all_model_results else 'pending'}")
    print(f"Ready for biological screening deployment")
    print("="*80)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Temporal Pattern Concordance Analysis

    Comparing how well acoustic indices capture the same temporal patterns (diel and seasonal) as manual detections.
    """
    )
    return


@app.cell
def _(df_community, index_cols, pd, spearmanr):
    # Temporal pattern concordance analysis
    print("Analyzing temporal pattern concordance...")

    # 1. Diel Pattern Analysis
    diel_patterns = df_community.groupby('hour').agg({
        'total_fish_activity': 'mean',
        'num_active_species': 'mean',
        **{idx: 'mean' for idx in index_cols[:10]}  # Top 10 indices for manageable analysis
    }).reset_index()

    # 2. Seasonal Pattern Analysis
    seasonal_patterns = df_community.groupby('month').agg({
        'total_fish_activity': 'mean',
        'num_active_species': 'mean',
        **{idx: 'mean' for idx in index_cols[:10]}
    }).reset_index()

    # 3. Calculate correlations between fish activity and indices across time
    diel_correlations = {}
    seasonal_correlations = {}

    # Diel correlations
    for idx in index_cols[:10]:
        diel_corr, diel_p = spearmanr(diel_patterns['total_fish_activity'], diel_patterns[idx])
        diel_correlations[idx] = {'correlation': diel_corr, 'p_value': diel_p}

    # Seasonal correlations
    for idx in index_cols[:10]:
        seasonal_corr, seasonal_p = spearmanr(seasonal_patterns['total_fish_activity'], seasonal_patterns[idx])
        seasonal_correlations[idx] = {'correlation': seasonal_corr, 'p_value': seasonal_p}

    # Convert to dataframes
    diel_corr_df = pd.DataFrame(diel_correlations).T
    seasonal_corr_df = pd.DataFrame(seasonal_correlations).T

    # Sort by correlation strength
    diel_corr_df = diel_corr_df.reindex(diel_corr_df['correlation'].abs().sort_values(ascending=False).index)
    seasonal_corr_df = seasonal_corr_df.reindex(seasonal_corr_df['correlation'].abs().sort_values(ascending=False).index)

    print("Top diel pattern correlations (indices vs fish activity):")
    print(diel_corr_df.head())

    print("\nTop seasonal pattern correlations (indices vs fish activity):")
    print(seasonal_corr_df.head())

    # 4. Cross-station pattern consistency
    station_consistency = {}
    for station in df_community['station'].unique():
        station_data = df_community[df_community['station'] == station]

        # Calculate hourly patterns for this station
        station_diel = station_data.groupby('hour')['total_fish_activity'].mean()
        station_seasonal = station_data.groupby('month')['total_fish_activity'].mean()

        station_consistency[station] = {
            'diel_pattern': station_diel,
            'seasonal_pattern': station_seasonal
        }

    print(f"\nCross-station analysis complete for {len(station_consistency)} stations")
    return (
        diel_corr_df,
        diel_patterns,
        seasonal_corr_df,
        seasonal_patterns,
        station_consistency,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Biological Screening Performance Evaluation

    Evaluating how effectively acoustic indices can screen for periods of biological interest.

    ## Screening Performance Metrics Explained

    Traditional machine learning focuses on accuracy, but biological screening requires different metrics:

    ### Key Metrics for Biological Applications

    **1. Detection Rate (Recall)**

    - **Definition**: Percentage of actual biological activity periods that the model correctly identifies
    - **Why it matters**: Missing biological activity = lost scientific data
    - **Target**: >80% for practical screening applications

    **2. Screening Precision**

    - **Definition**: When the model flags a period as "high activity," how often is it actually active?
    - **Why it matters**: False alarms waste manual effort
    - **Target**: >70% to maintain efficiency gains

    **3. Effort Reduction**

    - **Definition**: Percentage of data that can be skipped without manual analysis
    - **Why it matters**: This is the primary value proposition - saving time and money
    - **Target**: >50% reduction to justify deployment costs

    **4. F1 Score**

    - **Definition**: Harmonic mean of precision and recall (balances both)
    - **Why it matters**: Single metric for comparing models
    - **Target**: >0.7 for good performance, >0.8 for excellent

    ## Real-World Translation

    A screening system with 80% detection rate, 75% precision, and 60% effort reduction means:

    - Analyze only 40% of your data manually
    - Catch 80% of all biological activity
    - When you do analyze a flagged period, it's biologically interesting 75% of the time
    - Save ~60% of analysis time while maintaining most scientific value
    """
    )
    return


@app.cell
def _(model_results, np):
    # Biological screening performance evaluation
    print("Evaluating biological screening performance...")

    screening_results = {}

    for target_name_screen, target_models in model_results.items():
        print(f"\nScreening evaluation for: {target_name_screen}")

        # Get best performing model (highest F1 score)
        best_model_name = max(target_models.keys(),
                            key=lambda x: target_models[x]['f1'])
        best_model_results = target_models[best_model_name]

        print(f"Best model: {best_model_name} (F1: {best_model_results['f1']:.3f})")

        # Screening efficiency analysis
        y_true_screen = best_model_results['y_test']
        y_pred_screen = best_model_results['y_pred']
        y_prob_screen = best_model_results['y_prob']

        # Calculate efficiency metrics
        true_positives = np.sum((y_true_screen == 1) & (y_pred_screen == 1))
        false_positives = np.sum((y_true_screen == 0) & (y_pred_screen == 1))
        true_negatives = np.sum((y_true_screen == 0) & (y_pred_screen == 0))
        false_negatives = np.sum((y_true_screen == 1) & (y_pred_screen == 0))

        # Screening efficiency: how much effort could be saved?
        total_periods = len(y_true_screen)
        flagged_periods = np.sum(y_pred_screen == 1)
        actual_active_periods = np.sum(y_true_screen == 1)

        # If we only manually check flagged periods, what's the efficiency?
        effort_reduction = (total_periods - flagged_periods) / total_periods
        detection_rate = true_positives / actual_active_periods if actual_active_periods > 0 else 0

        # Precision in screening context: of flagged periods, how many are actually active?
        screening_precision = true_positives / flagged_periods if flagged_periods > 0 else 0

        screening_results[target_name_screen] = {
            'best_model': best_model_name,
            'f1_score': best_model_results['f1'],
            'precision': best_model_results['precision'],
            'recall': best_model_results['recall'],
            'effort_reduction': effort_reduction,
            'detection_rate': detection_rate,
            'screening_precision': screening_precision,
            'total_periods': total_periods,
            'flagged_periods': flagged_periods,
            'actual_active_periods': actual_active_periods,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }

        print(f"  Effort reduction: {effort_reduction:.1%}")
        print(f"  Detection rate: {detection_rate:.1%}")
        print(f"  Screening precision: {screening_precision:.1%}")

    # Overall screening assessment
    print("\n" + "="*60)
    print("BIOLOGICAL SCREENING ASSESSMENT SUMMARY")
    print("="*60)

    for target_name_summary, results in screening_results.items():
        print(f"\n{target_name_summary.upper()}:")
        print(f"  Best Model: {results['best_model']}")
        print(f"  F1 Score: {results['f1_score']:.3f}")
        print(f"  Manual Effort Reduction: {results['effort_reduction']:.1%}")
        print(f"  Biological Detection Rate: {results['detection_rate']:.1%}")
        print(f"  Screening Precision: {results['screening_precision']:.1%}")
    return (screening_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Visualization: Community Patterns and Screening Performance

    Creating comprehensive visualizations to show community pattern detection and screening tool performance.
    """
    )
    return


@app.cell
def _(
    diel_corr_df,
    diel_patterns,
    feature_importance_results,
    np,
    plot_dir,
    plt,
    screening_results,
    seasonal_patterns,
    station_consistency,
):
    # Create comprehensive visualizations
    print("Creating community pattern and screening visualizations...")

    # 1. Diel Pattern Concordance
    plt.figure(figsize=(12, 8))

    # Main fish activity pattern
    plt.subplot(2, 2, 1)
    plt.plot(diel_patterns['hour'], diel_patterns['total_fish_activity'], 'bo-', linewidth=2, label='Fish Activity')
    plt.xlabel('Hour of Day')
    plt.ylabel('Mean Total Fish Activity')
    plt.title('Diel Pattern: Community Fish Activity')
    plt.grid(True, alpha=0.3)
    plt.xticks(range(0, 24, 4))

    # Top correlated index
    plt.subplot(2, 2, 2)
    if len(diel_corr_df) > 0:
        top_index = diel_corr_df.index[0]
        plt.plot(diel_patterns['hour'], diel_patterns[top_index], 'ro-', linewidth=2, label=f'{top_index}')
        plt.xlabel('Hour of Day')
        plt.ylabel(f'Mean {top_index}')
        plt.title(f'Diel Pattern: Best Index ({top_index})\nCorrelation: {diel_corr_df.iloc[0]["correlation"]:.3f}')
        plt.grid(True, alpha=0.3)
        plt.xticks(range(0, 24, 4))

    # Seasonal patterns
    plt.subplot(2, 2, 3)
    plt.plot(seasonal_patterns['month'], seasonal_patterns['total_fish_activity'], 'go-', linewidth=2)
    plt.xlabel('Month')
    plt.ylabel('Mean Total Fish Activity')
    plt.title('Seasonal Pattern: Community Fish Activity')
    plt.grid(True, alpha=0.3)
    plt.xticks(range(1, 13))

    # Cross-station comparison
    plt.subplot(2, 2, 4)
    for station_viz, patterns in station_consistency.items():
        plt.plot(patterns['diel_pattern'].index, patterns['diel_pattern'].values,
                'o-', alpha=0.7, label=f'Station {station_viz}')
    plt.xlabel('Hour of Day')
    plt.ylabel('Mean Fish Activity')
    plt.title('Cross-Station Diel Patterns')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(range(0, 24, 4))

    plt.tight_layout()
    plt.savefig(plot_dir / '06_temporal_pattern_concordance.png', dpi=150, bbox_inches='tight')
    plt.show()

    # 2. Feature Importance Comparison
    if len(feature_importance_results) > 0:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.ravel()

        for i, (target_name_viz, importance_df_viz) in enumerate(feature_importance_results.items()):
            if i >= 4:  # Max 4 subplots
                break

            ax = axes[i]
            top_features = importance_df_viz.head(8)

            y_pos = range(len(top_features))
            ax.barh(y_pos, top_features['mutual_info'], alpha=0.7, color='steelblue')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_features['feature'], fontsize=8)
            ax.set_xlabel('Mutual Information Score')
            ax.set_title(f'Feature Importance: {target_name_viz}')
            ax.grid(True, alpha=0.3, axis='x')
            ax.invert_yaxis()

        plt.tight_layout()
        plt.savefig(plot_dir / '06_feature_importance.png', dpi=150, bbox_inches='tight')
        plt.show()

    # 3. Screening Performance Summary
    plt.figure(figsize=(12, 6))

    # Performance metrics
    plt.subplot(1, 2, 1)
    metrics = ['f1_score', 'precision', 'recall']
    target_names = list(screening_results.keys())

    x_pos = np.arange(len(target_names))
    width = 0.25

    for i, metric in enumerate(metrics):
        values = [screening_results[target][metric] for target in target_names]
        plt.bar(x_pos + i*width, values, width, alpha=0.7, label=metric.replace('_', ' ').title())

    plt.xlabel('Target Classification')
    plt.ylabel('Score')
    plt.title('Model Performance by Target')
    plt.xticks(x_pos + width, [name.replace('_', ' ').title() for name in target_names], rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.ylim(0, 1)

    # Efficiency metrics
    plt.subplot(1, 2, 2)
    efficiency_metrics = ['effort_reduction', 'detection_rate', 'screening_precision']

    for i, metric in enumerate(efficiency_metrics):
        values = [screening_results[target][metric] for target in target_names]
        plt.bar(x_pos + i*width, values, width, alpha=0.7, label=metric.replace('_', ' ').title())

    plt.xlabel('Target Classification')
    plt.ylabel('Rate')
    plt.title('Screening Efficiency by Target')
    plt.xticks(x_pos + width, [name.replace('_', ' ').title() for name in target_names], rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    plt.ylim(0, 1)

    plt.tight_layout()
    plt.savefig(plot_dir / '06_screening_performance.png', dpi=150, bbox_inches='tight')
    plt.show()

    print(f"Community pattern visualizations saved to {plot_dir}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Results Summary and Interpretation

    Synthesizing findings on community pattern detection and biological screening effectiveness.
    """
    )
    return


@app.cell
def _():
    # Progress tracking cell
    return


@app.cell(hide_code=True)
def _(
    DATA_ROOT,
    df_community,
    diel_corr_df,
    feature_importance_results,
    json,
    model_results,
    pickle,
    screening_results,
    seasonal_corr_df,
):
    # Save all results and create comprehensive summary
    print("Saving results and creating comprehensive summary...")

    # Save processed data
    df_community.to_parquet(DATA_ROOT / "processed/06_community_activity_data.parquet")

    # Save model results
    with open(DATA_ROOT / "processed/06_community_models.pkl", 'wb') as f:
        pickle.dump(model_results, f)

    # Save feature importance
    for target_name_save, importance_df_save in feature_importance_results.items():
        filename = f"06_feature_importance_{target_name_save}.parquet"
        importance_df_save.to_parquet(DATA_ROOT / "processed" / filename)

    # Save temporal concordance results
    diel_corr_df.to_parquet(DATA_ROOT / "processed/06_diel_correlations.parquet")
    seasonal_corr_df.to_parquet(DATA_ROOT / "processed/06_seasonal_correlations.parquet")

    # Create comprehensive summary
    summary_results = {
        'community_metrics': {
            'total_samples': len(df_community),
            'mean_total_activity': float(df_community['total_fish_activity'].mean()),
            'mean_active_species': float(df_community['num_active_species'].mean()),
            'any_activity_rate': float(df_community['any_activity'].mean()),
            'high_activity_75th_rate': float(df_community['high_activity_75th'].mean()),
            'high_activity_90th_rate': float(df_community['high_activity_90th'].mean())
        },
        'model_performance': {
            target: {
                'best_model': results['best_model'],
                'f1_score': float(results['f1_score']),
                'precision': float(results['precision']),
                'recall': float(results['recall'])
            }
            for target, results in screening_results.items()
        },
        'screening_efficiency': {
            target: {
                'effort_reduction': float(results['effort_reduction']),
                'detection_rate': float(results['detection_rate']),
                'screening_precision': float(results['screening_precision'])
            }
            for target, results in screening_results.items()
        },
        'temporal_concordance': {
            'best_diel_correlation': {
                'index': diel_corr_df.index[0] if len(diel_corr_df) > 0 else None,
                'correlation': float(diel_corr_df.iloc[0]['correlation']) if len(diel_corr_df) > 0 else None
            },
            'best_seasonal_correlation': {
                'index': seasonal_corr_df.index[0] if len(seasonal_corr_df) > 0 else None,
                'correlation': float(seasonal_corr_df.iloc[0]['correlation']) if len(seasonal_corr_df) > 0 else None
            }
        }
    }

    # Save summary
    with open(DATA_ROOT / "processed/06_community_analysis_summary.json", 'w') as f:
        json.dump(summary_results, f, indent=2)

    print("="*70)
    print("COMMUNITY PATTERN DETECTION AND BIOLOGICAL SCREENING SUMMARY")
    print("="*70)

    print(f"\nDATASET OVERVIEW:")
    print(f"  - Total samples analyzed: {summary_results['community_metrics']['total_samples']:,}")
    print(f"  - Mean total fish activity: {summary_results['community_metrics']['mean_total_activity']:.2f}")
    print(f"  - Mean active species per period: {summary_results['community_metrics']['mean_active_species']:.2f}")
    print(f"  - Periods with any activity: {summary_results['community_metrics']['any_activity_rate']:.1%}")

    print(f"\nMODEL PERFORMANCE (COMMUNITY ACTIVITY DETECTION):")
    for target, performance in summary_results['model_performance'].items():
        print(f"  {target.replace('_', ' ').title()}:")
        print(f"    - Best Model: {performance['best_model']}")
        print(f"    - F1 Score: {performance['f1_score']:.3f}")
        print(f"    - Precision: {performance['precision']:.3f}")
        print(f"    - Recall: {performance['recall']:.3f}")

    print(f"\nBIOLOGICAL SCREENING EFFICIENCY:")
    for target, efficiency in summary_results['screening_efficiency'].items():
        print(f"  {target.replace('_', ' ').title()}:")
        print(f"    - Manual Effort Reduction: {efficiency['effort_reduction']:.1%}")
        print(f"    - Biological Detection Rate: {efficiency['detection_rate']:.1%}")
        print(f"    - Screening Precision: {efficiency['screening_precision']:.1%}")

    print(f"\nTEMPORAL PATTERN CONCORDANCE:")
    if summary_results['temporal_concordance']['best_diel_correlation']['index']:
        print(f"  - Best Diel Pattern Match: {summary_results['temporal_concordance']['best_diel_correlation']['index']}")
        print(f"    Correlation: {summary_results['temporal_concordance']['best_diel_correlation']['correlation']:.3f}")
    if summary_results['temporal_concordance']['best_seasonal_correlation']['index']:
        print(f"  - Best Seasonal Pattern Match: {summary_results['temporal_concordance']['best_seasonal_correlation']['index']}")
        print(f"    Correlation: {summary_results['temporal_concordance']['best_seasonal_correlation']['correlation']:.3f}")

    print("\n" + "="*70)
    print("COMPREHENSIVE SCIENTIFIC INTERPRETATION")
    print("="*70)

    # Determine key findings based on results
    best_screening_target = max(summary_results['screening_efficiency'].items(),
                              key=lambda x: x[1]['detection_rate'])

    best_f1_target = max(summary_results['model_performance'].items(),
                        key=lambda x: x[1]['f1_score'])

    print(f"""
    ## 1. COMMUNITY ACTIVITY DETECTION PERFORMANCE

    **Primary Finding**: Within this study system, acoustic indices show promising ability to detect community-level biological activity

    **Best Overall Performance**: {best_f1_target[0].replace('_', ' ').title()}
    - F1 Score: {best_f1_target[1]['f1_score']:.3f} (Good performance - above 0.8 indicates strong model performance)
    - Precision: {best_f1_target[1]['precision']:.3f} (When model predicts activity, it's correct {best_f1_target[1]['precision']:.1%} of the time)
    - Recall: {best_f1_target[1]['recall']:.3f} (Detects {best_f1_target[1]['recall']:.1%} of actual biological activity periods)

    **Biological Interpretation**: In this dataset, the model shows ability to distinguish between periods when fish are
    calling vs when they are not. This suggests potential for acoustic monitoring applications, though validation across
    different systems and environments is needed.

    ## 2. BIOLOGICAL SCREENING TOOL POTENTIAL

    **Primary Finding**: Results suggest indices may serve as screening tools for manual effort guidance in this study system

    **Best Screening Performance**: {best_screening_target[0].replace('_', ' ').title()}
    - Detection Rate: {best_screening_target[1]['detection_rate']:.1%} (Detects most biological activity in this dataset)
    - Screening Precision: {best_screening_target[1]['screening_precision']:.1%} (Relatively low false alarm rate)
    - Effort Reduction: {best_screening_target[1]['effort_reduction']:.1%} (Potential workload savings)

    **Potential Application**: Based on these results, a researcher might:
    1. Run acoustic indices on 100 hours of recordings from similar environments
    2. Model flags ~{100 - best_screening_target[1]['effort_reduction']*100:.0f} hours as "high interest"
    3. Manual analysis of only those {100 - best_screening_target[1]['effort_reduction']*100:.0f} hours could potentially catch {best_screening_target[1]['detection_rate']:.0f}% of biological activity
    4. This approach could save {best_screening_target[1]['effort_reduction']:.0f}% of manual effort while missing {100-best_screening_target[1]['detection_rate']:.0f}% of activity

    **Important caveat**: These projections are based on one study system and require validation across different
    environments, acoustic setups, and fish communities before operational deployment.

    ## 3. TEMPORAL PATTERN CONCORDANCE ANALYSIS

    **Diel Pattern Matching**: {summary_results['temporal_concordance']['best_diel_correlation']['index']}
    - Correlation: {summary_results['temporal_concordance']['best_diel_correlation']['correlation']:.3f}
    - Interpretation: {"Strong negative correlation - index decreases when fish activity increases during day" if summary_results['temporal_concordance']['best_diel_correlation']['correlation'] < -0.7 else "Strong positive correlation - index tracks fish activity patterns"}

    **Seasonal Pattern Matching**: {summary_results['temporal_concordance']['best_seasonal_correlation']['index']}
    - Correlation: {summary_results['temporal_concordance']['best_seasonal_correlation']['correlation']:.3f}
    - Interpretation: {"Very strong negative correlation - index shows opposite seasonal pattern to fish" if summary_results['temporal_concordance']['best_seasonal_correlation']['correlation'] < -0.8 else "Strong correlation with fish seasonal patterns"}

    **Biological Significance**: Some acoustic indices show correlations with fish calling temporal patterns in this dataset.
    This suggests they may be capturing biological phenomena rather than just acoustic noise, though this relationship
    requires validation across different systems and temporal scales.

    ## 4. FEATURE IMPORTANCE INSIGHTS

    **Most Important Predictors** (across all models):
    1. Month (seasonal patterns) - Captures spawning cycles and temperature-driven behavior
    2. Water temperature - Direct physiological driver of fish activity
    3. Acoustic indices (ENRf, VARf, NBPEAKS) - Capture acoustic characteristics of biological sounds

    **Scientific Interpretation**: The models rely on biologically sensible variables in this study system. The combination of
    seasonal timing, environmental conditions, and acoustic features shows predictive potential, though the generalizability
    of these relationships across different marine environments remains to be tested.

    ## 5. COMPARISON TO SPECIES-SPECIFIC APPROACHES

    **Why Community-Level May Work Better (in this system)**:
    - Individual species showed weak, irregular calling patterns in this dataset
    - Aggregating across species appears to amplify consistent biological signal
    - May reduce noise from species-specific behavioral variation
    - Could match practical monitoring needs (detect biological activity, then investigate specifics)

    **Working hypothesis**: Like using a motion detector vs identifying specific animals - the former may be
    more reliable for knowing "when something biological is happening" in marine acoustic monitoring

    ## 6. PRACTICAL IMPLEMENTATION RECOMMENDATIONS

    **Potential Applications (requiring further validation)**:
    1. **Smart Sampling Protocols**: Indices might help identify optimal times for manual analysis
    2. **Background Monitoring**: Could enable more continuous biological activity tracking
    3. **Site Assessment**: May help characterize biological activity patterns at new locations
    4. **Quality Control**: Could flag unusual periods in long-term datasets for examination

    **Suggested Development Strategy**:
    - Test Random Forest or similar ensemble methods for performance
    - Focus initial validation on "any activity" detection for general screening
    - Evaluate "high activity" thresholds for identifying exceptional biological events
    - Calibrate thresholds based on acceptable false positive/negative rates for specific applications
    - Validate approach across different study systems before operational deployment

    ## 7. STUDY SIGNIFICANCE AND LIMITATIONS

    **Study Contribution**: This analysis demonstrates that acoustic indices show potential for community-level
    biological activity detection in this marine environment, suggesting possible applications as screening tools.

    **Potential Impact**: If validated across different systems, this approach might enable more efficient
    acoustic monitoring by reducing manual analysis bottlenecks. However, broader application requires
    extensive testing across different marine environments, fish communities, and acoustic setups.

    **Study Scope**: Results based on {summary_results['community_metrics']['total_samples']:,} samples from
    one study system across a full annual cycle with multiple stations. While this provides a solid foundation,
    generalizability to other marine environments requires further investigation.

    **Next Steps for Validation**:
    - Literature review of existing acoustic monitoring approaches
    - Cross-site validation with independent datasets
    - Comparison with other automated detection methods
    - Testing across different fish communities and acoustic environments
    """)

    print(f"\nAnalysis complete! All results saved to {DATA_ROOT}/processed/")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Conclusions and Recommendations

    ### What We Learned

    **Community-Level Detection Shows Promise**: In this study system, acoustic indices showed better success at detecting aggregate biological activity rather than species-specific patterns. This suggests their potential value may lie in **biological screening** rather than detailed species identification, though this requires validation across different environments.

    **Temporal Patterns Show Some Concordance**: Some indices capture diel and seasonal patterns that correlate with fish community activity, though not with the precision of manual detections. The correlation strengths vary by index and temporal scale, and the generalizability of these patterns is unknown.

    **Screening Tool Potential**: The most promising application appears to be using indices as **screening tools** that flag periods likely to contain biological activity for targeted manual analysis. This could potentially reduce manual effort while maintaining detection rates, but operational effectiveness requires validation in real-world deployment scenarios.

    ### Potential Applications (Requiring Validation)

    1. **Smart Sampling Protocols**: Indices might help identify optimal times for detailed manual analysis
    2. **Background Monitoring**: Could enable more continuous monitoring with periodic manual validation
    3. **Effort Optimization**: May help focus limited manual resources on periods flagged by models
    4. **Pattern Detection**: Could help detect unusual biological activity patterns warranting investigation

    ### Next Steps for Notebook 7

    The validation analysis should focus on:

    - **Temporal transferability**: Do these patterns hold across different time periods?
    - **Cross-site validation**: How well do models trained at one site perform at others?
    - **Continuous monitoring simulation**: What would real-world deployment look like?
    - **Cost-benefit quantification**: Actual effort savings vs information loss

    ### The Bottom Line

    In this study system, acoustic indices show **promising potential** as biological screening tools. While they cannot replace manual detection, they may be able to **help guide when and where to apply manual effort**. However, this potential must be validated across different marine environments, fish communities, and operational contexts before concluding that they can improve the efficiency of acoustic monitoring programs more broadly.

    **Critical next steps**: Cross-system validation, comparison with existing methods, and operational testing are essential before broader implementation.
    """
    )
    return


if __name__ == "__main__":
    app.run()
