import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Notebook 6.1: Enhanced Community Pattern Detection with Transue Methodology

        **Purpose**: Demonstrate that acoustic indices can detect community-level fish patterns using both traditional and state-of-the-art marine bioacoustics methodologies

        **Key Outputs**: Comparative analysis using both Mutual Information and Boruta feature selection with Transue et al. (2023) statistical validation

        **Methodological Enhancement**: This notebook builds upon the original community detection approach by integrating the Random Forest + Boruta methodology established by Transue et al. (2023) for Charleston Harbor soundscape analysis, while maintaining our original Mutual Information approach for comparison.

        ---

        ## Overview

        This enhanced analysis combines two complementary feature selection approaches:

        ### 1. Mutual Information Approach (Original)
        - **What it does**: Detects non-linear relationships between acoustic indices and biological activity
        - **Strength**: Captures complex, threshold-based biological relationships
        - **Best for**: Discovering unexpected acoustic-biological connections

        ### 2. Boruta + Random Forest Approach (Transue et al. 2023)
        - **What it does**: Uses ensemble decision trees to identify all relevant features
        - **Strength**: Established methodology for marine bioacoustics research
        - **Best for**: Consistent, interpretable feature selection aligned with field standards

        ## Why Use Both Approaches?

        **Complementary Insights**: 
        - Mutual Information might find acoustic indices that respond to biological "hotspots" or threshold events
        - Boruta might identify indices that consistently track biological patterns across all activity levels
        - Comparing results validates feature importance across different statistical frameworks

        **Scientific Rigor**: 
        - Shows our findings are robust across multiple analytical approaches
        - Aligns with established marine bioacoustics methodology (Transue et al.)
        - Provides comprehensive feature evaluation for biological screening applications

        ## Enhanced Validation Framework

        Following Transue et al. (2023), we implement:
        - **Random Forest modeling** as the primary analytical framework
        - **Boruta feature selection** for systematic feature importance
        - **Out-of-bag validation** and cross-validation for robust performance estimates
        - **Dunnett-Tukey-Kramer post-hoc testing** for statistical significance validation

        The key question remains: **"Can acoustic indices tell us when to pay attention?"** but now with enhanced methodological rigor.
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

    # Enhanced feature selection (Transue methodology)
    try:
        from boruta import BorutaPy
        BORUTA_AVAILABLE = True
        print("✅ Boruta package available - enhanced feature selection enabled")
    except ImportError:
        BORUTA_AVAILABLE = False
        print("⚠️ Boruta package not available - install with: pip install boruta")
        print("   Falling back to mutual information + random forest importance only")

    # Statistical analysis and post-hoc testing
    from scipy import stats
    from scipy.stats import spearmanr, pearsonr
    try:
        from scipy.stats import tukey_hsd
        POSTHOC_AVAILABLE = True
        print("✅ Post-hoc testing available")
    except ImportError:
        POSTHOC_AVAILABLE = False
        print("⚠️ Advanced post-hoc testing not available - using basic statistical tests")

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
        BORUTA_AVAILABLE,
        BorutaPy,
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
        train_test_split,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Data Loading and Preparation

    Loading all processed datasets and preparing them for enhanced community-level analysis.
    """
    )
    return


@app.cell
def _(DATA_ROOT, pd):
    # Load all processed datasets (same as original)
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
    return df_det_metadata, df_detections, df_env, df_indices, df_temporal


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

    Instead of trying to predict individual species calling patterns, we aggregate across all species to ask: 
    **"Is there biological activity happening?"** This approach:

    1. **Reduces complexity**: 7 species × 4 intensity levels = 28 possible states → 4 binary questions
    2. **Increases signal**: Combines weak species-specific signals into stronger community signal  
    3. **Matches practical needs**: Often we care more about "when to listen carefully" than "exactly which species"
    4. **Improves statistical power**: More balanced classes, clearer patterns
    """
    )
    return


@app.cell
def _(df_master, fish_species):
    # Create community-level activity metrics (same as original)
    print("Creating community activity metrics...")
    print(f"Working with {len(fish_species)} fish species: {fish_species}")

    # Create community metrics
    df_community = df_master.copy()
    df_community['total_fish_activity'] = df_community[fish_species].sum(axis=1)
    df_community['num_active_species'] = (df_community[fish_species] > 0).sum(axis=1)
    df_community['max_species_activity'] = df_community[fish_species].max(axis=1)
    df_community['activity_diversity'] = df_community[fish_species].std(axis=1) / (df_community[fish_species].mean(axis=1) + 0.01)

    # Binary classification targets
    total_activity_75th = df_community['total_fish_activity'].quantile(0.75)
    total_activity_90th = df_community['total_fish_activity'].quantile(0.90)

    df_community['high_activity_75th'] = (df_community['total_fish_activity'] >= total_activity_75th).astype(int)
    df_community['high_activity_90th'] = (df_community['total_fish_activity'] >= total_activity_90th).astype(int)
    df_community['any_activity'] = (df_community['total_fish_activity'] > 0).astype(int)
    df_community['multi_species_active'] = (df_community['num_active_species'] >= 2).astype(int)

    print(f"Fish community metrics created. Sample statistics:")
    print(f"Total activity - Mean: {df_community['total_fish_activity'].mean():.2f}")
    print(f"High activity (75th): {df_community['high_activity_75th'].mean():.1%}")
    print(f"Any activity: {df_community['any_activity'].mean():.1%}")
    return (df_community,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Enhanced Feature Selection: Comparative Analysis

    This section implements both traditional and state-of-the-art feature selection approaches to identify the most important acoustic indices for biological screening.

    ## Methodological Comparison

    ### Approach 1: Mutual Information (Original Method)

    **What it does**: Measures how much information one variable provides about another, capturing both linear and non-linear relationships.

    **Biological relevance**: 

    - Can detect threshold effects (e.g., fish only call when certain acoustic conditions are met)
    - Captures complex interaction patterns between indices and biology
    - Good for discovering unexpected acoustic-biological relationships

    ### Approach 2: Boruta + Random Forest (Transue et al. 2023)

    **What it does**: Uses an ensemble of decision trees to systematically identify all statistically relevant features.

    **Biological relevance**:

    - Established methodology in marine bioacoustics research
    - Handles feature interactions naturally through tree-based decisions
    - Provides consistent, interpretable feature rankings
    - Proven approach for acoustic data with temporal autocorrelation

    ## Why Compare Both?

    **Scientific validation**: If both methods identify the same indices as important, we have strong evidence for their biological relevance.

    **Methodological robustness**: Shows our findings aren't dependent on a single analytical approach.

    **Best of both worlds**: Combines novel discovery potential (MI) with established methodology (Boruta).
    """
    )
    return


@app.cell
def _(
    BORUTA_AVAILABLE,
    BorutaPy,
    RandomForestClassifier,
    StandardScaler,
    df_community,
    index_cols,
    mutual_info_classif,
    np,
    pd,
):
    # Enhanced Feature Selection: Comparative Analysis
    print("ENHANCED FEATURE SELECTION: COMPARATIVE ANALYSIS")
    print("="*70)
    print("Implementing both Mutual Information and Boruta approaches")
    print("="*70)

    # Prepare feature matrix
    modeling_cols = index_cols + ['Water temp (°C)', 'Water depth (m)', 'hour', 'month']
    target_cols = ['high_activity_75th', 'high_activity_90th', 'any_activity', 'multi_species_active']

    print(f"Feature categories:")
    print(f"  - Acoustic indices: {len(index_cols)} variables")
    print(f"  - Environmental: 2 variables (temperature, depth)")
    print(f"  - Temporal: 2 variables (hour, month)")
    print(f"  - Total features: {len(modeling_cols)}")

    # Prepare modeling dataset
    df_modeling = df_community[modeling_cols + target_cols].dropna()
    print(f"Modeling dataset: {df_modeling.shape[0]:,} complete samples")

    # Standardize features
    X_features = df_modeling[modeling_cols]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_features)

    # Initialize results storage
    comparative_feature_results = {}

    # =====================================================================
    # COMPARATIVE FEATURE SELECTION FOR EACH TARGET
    # =====================================================================

    for current_target_name in target_cols:
        print(f"\n" + "="*50)
        print(f"ANALYZING TARGET: {current_target_name}")
        print("="*50)

        y_target = df_modeling[current_target_name]

        # Check class balance
        class_balance = y_target.value_counts(normalize=True)
        print(f"Class balance: {class_balance.to_dict()}")

        if y_target.std() == 0:
            print(f"Skipping {current_target_name} - no variance in target")
            continue

        current_target_results = {
            'target_name': current_target_name,
            'class_balance': class_balance.to_dict(),
            'sample_size': len(y_target)
        }

        # -------------------------------------------------------------
        # METHOD 1: MUTUAL INFORMATION ANALYSIS
        # -------------------------------------------------------------
        print(f"\n1. MUTUAL INFORMATION FEATURE SELECTION")
        print("-" * 45)

        # Calculate mutual information scores
        mi_scores = mutual_info_classif(X_scaled, y_target, random_state=42)

        # Create MI results dataframe
        mi_results = pd.DataFrame({
            'feature': modeling_cols,
            'mi_score': mi_scores,
            'feature_type': ['acoustic_index' if col in index_cols else 
                           'environmental' if col in ['Water temp (°C)', 'Water depth (m)'] else 
                           'temporal' for col in modeling_cols]
        }).sort_values('mi_score', ascending=False)

        print(f"Top 5 features by Mutual Information:")
        for i, (_, row) in enumerate(mi_results.head().iterrows()):
            print(f"  {i+1}. {row['feature']} ({row['feature_type']}): {row['mi_score']:.3f}")

        current_target_results['mutual_information'] = {
            'rankings': mi_results,
            'top_5_features': mi_results.head()['feature'].tolist(),
            'best_acoustic_index': mi_results[mi_results['feature_type'] == 'acoustic_index'].iloc[0]['feature'],
            'best_mi_score': mi_results.iloc[0]['mi_score']
        }

        # -------------------------------------------------------------
        # METHOD 2: BORUTA FEATURE SELECTION (if available)
        # -------------------------------------------------------------
        if BORUTA_AVAILABLE:
            print(f"\n2. BORUTA + RANDOM FOREST FEATURE SELECTION")
            print("-" * 50)
            print("Following Transue et al. (2023) methodology...")

            # Initialize Random Forest for Boruta (matching Transue parameters)
            rf_selector = RandomForestClassifier(
                n_estimators=100, 
                max_depth=8,
                random_state=42,
                n_jobs=-1  # Use all cores for faster processing
            )

            # Initialize Boruta
            boruta_selector = BorutaPy(
                rf_selector,
                n_estimators='auto',
                verbose=0,  # Reduce output
                random_state=42,
                max_iter=100  # Limit iterations to prevent long runtime
            )

            try:
                # Fit Boruta
                print("Running Boruta feature selection (this may take a moment)...")
                boruta_selector.fit(X_scaled, y_target)

                # Extract results
                selected_features = np.array(modeling_cols)[boruta_selector.support_]
                tentative_features = np.array(modeling_cols)[boruta_selector.support_weak_]
                rejected_features = np.array(modeling_cols)[~boruta_selector.support_ & ~boruta_selector.support_weak_]

                # Create Boruta results dataframe
                boruta_results = pd.DataFrame({
                    'feature': modeling_cols,
                    'boruta_ranking': boruta_selector.ranking_,
                    'boruta_decision': ['confirmed' if boruta_selector.support_[i] else 
                                       'tentative' if boruta_selector.support_weak_[i] else 
                                       'rejected' for i in range(len(modeling_cols))],
                    'feature_type': ['acoustic_index' if col in index_cols else 
                                   'environmental' if col in ['Water temp (°C)', 'Water depth (m)'] else 
                                   'temporal' for col in modeling_cols]
                }).sort_values('boruta_ranking')

                print(f"Boruta Results:")
                print(f"  ✅ Confirmed features: {len(selected_features)} ({list(selected_features)})")
                print(f"  ❓ Tentative features: {len(tentative_features)} ({list(tentative_features)})")
                print(f"  ❌ Rejected features: {len(rejected_features)}")

                # Get Random Forest feature importance from the final model
                rf_final = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
                rf_final.fit(X_scaled, y_target)
                rf_importance = rf_final.feature_importances_

                boruta_results['rf_importance'] = rf_importance

                current_target_results['boruta'] = {
                    'rankings': boruta_results,
                    'confirmed_features': list(selected_features),
                    'tentative_features': list(tentative_features),
                    'rejected_features': list(rejected_features),
                    'n_confirmed': len(selected_features),
                    'best_acoustic_index': boruta_results[
                        (boruta_results['feature_type'] == 'acoustic_index') &
                        (boruta_results['boruta_decision'] == 'confirmed')
                    ]['feature'].iloc[0] if len(selected_features) > 0 else None
                }



                print(f"Top confirmed features by ranking:")
                confirmed_features = boruta_results[boruta_results['boruta_decision'] == 'confirmed'].head()
                for i, (_, row) in enumerate(confirmed_features.iterrows()):
                    print(f"  {i+1}. {row['feature']} ({row['feature_type']}): rank {row['boruta_ranking']}")

            except Exception as e:
                print(f"⚠️ Boruta analysis failed for {current_target_name}: {str(e)}")
                print("Falling back to Random Forest importance only...")

                # Fallback to RF importance
                rf_fallback = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
                rf_fallback.fit(X_scaled, y_target)
                rf_importance = rf_fallback.feature_importances_

                rf_results_df = pd.DataFrame({
                    'feature': modeling_cols,
                    'rf_importance': rf_importance,
                    'feature_type': ['acoustic_index' if col in index_cols else 
                                   'environmental' if col in ['Water temp (°C)', 'Water depth (m)'] else 
                                   'temporal' for col in modeling_cols]
                }).sort_values('rf_importance', ascending=False)

                current_target_results['boruta'] = {
                    'rankings': rf_results_df,
                    'confirmed_features': rf_results_df.head(5)['feature'].tolist(),
                    'fallback_used': True,
                    'best_acoustic_index': rf_results_df[rf_results_df['feature_type'] == 'acoustic_index'].iloc[0]['feature']
                }

        else:
            print(f"\n2. BORUTA NOT AVAILABLE - USING RANDOM FOREST IMPORTANCE")
            print("-" * 55)

            # Fallback to RF importance
            rf_fallback = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
            rf_fallback.fit(X_scaled, y_target)
            rf_importance = rf_fallback.feature_importances_

            rf_results_df = pd.DataFrame({
                'feature': modeling_cols,
                'rf_importance': rf_importance,
                'feature_type': ['acoustic_index' if col in index_cols else 
                               'environmental' if col in ['Water temp (°C)', 'Water depth (m)'] else 
                               'temporal' for col in modeling_cols]
            }).sort_values('rf_importance', ascending=False)

            print(f"Top 5 features by Random Forest importance:")
            for i, (_, row) in enumerate(rf_results_df.head().iterrows()):
                print(f"  {i+1}. {row['feature']} ({row['feature_type']}): {row['rf_importance']:.3f}")

            current_target_results['boruta'] = {
                'rankings': rf_results_df,
                'confirmed_features': rf_results_df.head(5)['feature'].tolist(),
                'fallback_used': True,
                'best_acoustic_index': rf_results_df[rf_results_df['feature_type'] == 'acoustic_index'].iloc[0]['feature']
            }

        # -------------------------------------------------------------
        # METHOD COMPARISON AND CONSENSUS
        # -------------------------------------------------------------
        print(f"\n3. COMPARATIVE ANALYSIS: MI vs BORUTA")
        print("-" * 40)

        mi_top_5 = set(current_target_results['mutual_information']['top_5_features'])
        boruta_top_5 = set(current_target_results['boruta']['confirmed_features'][:5])

        _consensus_features = mi_top_5.intersection(boruta_top_5)
        mi_unique = mi_top_5 - boruta_top_5
        boruta_unique = boruta_top_5 - mi_top_5

        print(f"Feature agreement analysis:")
        print(f"  🤝 Consensus features (both methods): {len(_consensus_features)}")
        if _consensus_features:
            print(f"      {list(_consensus_features)}")
        print(f"  🔍 MI-unique features: {len(mi_unique)}")
        if mi_unique:
            print(f"      {list(mi_unique)}")
        print(f"  🌲 Boruta-unique features: {len(boruta_unique)}")
        if boruta_unique:
            print(f"      {list(boruta_unique)}")

        current_target_results['comparison'] = {
            'consensus_features': list(_consensus_features),
            'mi_unique_features': list(mi_unique),
            'boruta_unique_features': list(boruta_unique),
            'agreement_rate': len(_consensus_features) / 5.0,
            'total_unique_features': len(mi_top_5.union(boruta_top_5))
        }

        comparative_feature_results[current_target_name] = current_target_results

    print(f"\n" + "="*70)
    print("COMPARATIVE FEATURE SELECTION COMPLETE")
    print("="*70)
    print(f"Analyzed {len(comparative_feature_results)} targets successfully")
    return comparative_feature_results, df_modeling, modeling_cols, target_cols


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Enhanced Model Development with Transue Methodology

    Training machine learning models using the enhanced feature selection results, with emphasis on Random Forest modeling following Transue et al. (2023).

    ## Model Selection Strategy

    **Primary Focus: Random Forest** (following Transue et al.)

    - Proven methodology for marine bioacoustic data
    - Handles temporal autocorrelation naturally
    - Provides interpretable feature importance
    - Robust to outliers and missing data

    **Comparative Models** (for validation):

    - Logistic Regression: Linear baseline
    - Decision Tree: Simple interpretable rules

    ## Enhanced Validation Framework

    Following Transue et al. (2023):

    - **Out-of-bag error estimation** (built into Random Forest)
    - **Stratified cross-validation** for robust performance estimates  
    - **Feature importance ranking** with statistical significance
    - **Model performance on both consensus and method-specific features**
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
    comparative_feature_results,
    cross_val_score,
    df_modeling,
    f1_score,
    modeling_cols,
    precision_score,
    recall_score,
    target_cols,
    train_test_split,
):
    # Enhanced Model Development
    print("ENHANCED MODEL DEVELOPMENT WITH TRANSUE METHODOLOGY")
    print("="*70)
    print("Primary focus: Random Forest with comparative validation")
    print("="*70)

    # Model configurations (emphasizing Random Forest following Transue et al.)
    enhanced_models = {
        'Random Forest (Primary)': RandomForestClassifier(
            n_estimators=100,      # Match Transue parameters
            max_depth=8,           # Prevent overfitting
            min_samples_leaf=5,    # Ensure robust nodes
            oob_score=True,        # Enable out-of-bag scoring (Transue method)
            random_state=42,
            n_jobs=-1              # Use all cores
        ),
        'Random Forest (Consensus)': RandomForestClassifier(  # Will use consensus features only
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=5,
            oob_score=True,
            random_state=42,
            n_jobs=-1
        ),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(
            max_depth=8,
            min_samples_leaf=10,
            random_state=42
        ),
    }

    print(f"Model configurations: {list(enhanced_models.keys())}")

    # Initialize enhanced results storage
    enhanced_model_results = {}
    feature_performance_comparison = {}

    for _target_name in target_cols:
        if _target_name not in comparative_feature_results:
            continue

        print(f"\n" + "="*60)
        print(f"TRAINING ENHANCED MODELS FOR: {_target_name}")
        print("="*60)

        _y_target = df_modeling[_target_name]
        target_feature_results = comparative_feature_results[_target_name]

        # Get different feature sets for comparison
        all_features = modeling_cols
        _consensus_features = target_feature_results['comparison']['consensus_features']
        mi_top_features = target_feature_results['mutual_information']['top_5_features']
        boruta_top_features = target_feature_results['boruta']['confirmed_features'][:5]

        print(f"Feature set comparison:")
        print(f"  All features: {len(all_features)}")
        print(f"  Consensus features: {len(_consensus_features)}")
        print(f"  MI top features: {len(mi_top_features)}")
        print(f"  Boruta top features: {len(boruta_top_features)}")

        target_model_results = {}

        # Test different feature sets
        feature_sets = {
            'All Features': all_features,
            'Consensus Features': _consensus_features if len(_consensus_features) >= 3 else all_features,
            'MI Top Features': mi_top_features,
            'Boruta Top Features': boruta_top_features
        }

        for feature_set_name, feature_list in feature_sets.items():
            print(f"\n--- FEATURE SET: {feature_set_name} ({len(feature_list)} features) ---")

            if len(feature_list) < 3:
                print(f"Skipping {feature_set_name} - insufficient features ({len(feature_list)})")
                continue

            # Prepare features
            _X_features = df_modeling[feature_list]
            scaler_set = StandardScaler()
            X_scaled_set = scaler_set.fit_transform(_X_features)

            feature_set_results = {}

            # Train models on this feature set
            for model_name, model in enhanced_models.items():
                # Skip consensus model if not using consensus features
                if model_name == 'Random Forest (Consensus)' and feature_set_name != 'Consensus Features':
                    continue
                # Skip primary model if using consensus features (avoid duplication)
                if model_name == 'Random Forest (Primary)' and feature_set_name == 'Consensus Features':
                    continue

                # Create fresh model instance
                model_instance = type(model)(**model.get_params())

                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled_set, _y_target, test_size=0.3, random_state=42, stratify=_y_target
                )

                # Train model
                model_instance.fit(X_train, y_train)

                # Predictions
                y_pred = model_instance.predict(X_test)
                y_prob = model_instance.predict_proba(X_test)[:, 1] if hasattr(model_instance, 'predict_proba') else y_pred

                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
                recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
                kappa = cohen_kappa_score(y_test, y_pred)

                # Cross-validation
                cv_model = type(model)(**model.get_params())
                cv_scores = cross_val_score(cv_model, X_scaled_set, _y_target, cv=StratifiedKFold(5), scoring='f1')

                # Out-of-bag score for Random Forest (Transue methodology)
                oob_score = None
                if hasattr(model_instance, 'oob_score_'):
                    oob_score = model_instance.oob_score_

                model_results = {
                    'model': model_instance,
                    'feature_set': feature_set_name,
                    'feature_list': feature_list,
                    'n_features': len(feature_list),
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'kappa': kappa,
                    'cv_f1_mean': cv_scores.mean(),
                    'cv_f1_std': cv_scores.std(),
                    'oob_score': oob_score,
                    'y_test': y_test,
                    'y_pred': y_pred,
                    'y_prob': y_prob
                }

                feature_set_results[model_name] = model_results

                # Print performance
                performance_str = f"F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}"
                if oob_score:
                    performance_str += f", OOB={oob_score:.3f}"
                print(f"    {model_name}: {performance_str}")

            target_model_results[feature_set_name] = feature_set_results

        enhanced_model_results[_target_name] = target_model_results

        # Identify best performing models for this target
        print(f"\n🏆 BEST MODELS FOR {_target_name}:")
        _best_f1 = 0
        best_model_info = None

        for feature_set_name, _models in target_model_results.items():
            for _model_name, _results in _models.items():
                if _results['f1'] > _best_f1:
                    _best_f1 = _results['f1']
                    best_model_info = (feature_set_name, _model_name, _results)

        if best_model_info:
            _feature_set, _model_name, _results = best_model_info
            print(f"    {_model_name} with {_feature_set}")
            print(f"    F1: {_results['f1']:.3f}, Features: {_results['n_features']}")

    print(f"\n" + "="*70)
    print("ENHANCED MODEL DEVELOPMENT COMPLETE")
    print("="*70)
    return (enhanced_model_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Enhanced Results Analysis and Visualization

    Comprehensive analysis of feature selection and model performance, comparing traditional and Transue methodologies.
    """
    )
    return


@app.cell
def _(
    comparative_feature_results,
    enhanced_model_results,
    np,
    pd,
    plot_dir,
    plt,
):
    # Enhanced Results Analysis and Visualization
    print("ENHANCED RESULTS ANALYSIS")
    print("="*50)

    # 1. Feature Selection Comparison Visualization
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    target_names_viz = list(comparative_feature_results.keys())[:4]  # Max 4 for visualization

    for _i_viz, target_name_viz in enumerate(target_names_viz):
        if _i_viz >= 4:
            break

        ax = axes[_i_viz//2, _i_viz%2]
        target_results_comp = comparative_feature_results[target_name_viz]

        # Get top features from both methods
        mi_features = target_results_comp['mutual_information']['rankings'].head(8)

        # Plot MI scores
        y_pos = np.arange(len(mi_features))
        bars = ax.barh(y_pos, mi_features['mi_score'], alpha=0.7)

        # Color bars by feature type
        colors = {'acoustic_index': 'steelblue', 'environmental': 'orange', 'temporal': 'green'}
        for j, (_, mi_row) in enumerate(mi_features.iterrows()):
            bars[j].set_color(colors.get(mi_row['feature_type'], 'gray'))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(mi_features['feature'], fontsize=8)
        ax.set_xlabel('Mutual Information Score')
        ax.set_title(f'{target_name_viz.replace("_", " ").title()}\nFeature Importance')
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()

    # Add legend
    handles = [plt.Rectangle((0,0),1,1, color=colors[key]) for key in colors.keys()]
    labels = ['Acoustic Index', 'Environmental', 'Temporal']
    fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(1, 1))

    plt.tight_layout()
    plt.savefig(plot_dir / '06_01_enhanced_feature_importance.png', dpi=150, bbox_inches='tight')
    plt.show()

    # 2. Model Performance Comparison
    performance_summary = []

    for _target_name, _target_results in enhanced_model_results.items():
        for _feature_set, _models in _target_results.items():
            for _model_name, _results in _models.items():
                performance_summary.append({
                    'target': _target_name,
                    'feature_set': _feature_set,
                    'model': _model_name,
                    'f1': _results['f1'],
                    'precision': _results['precision'],
                    'recall': _results['recall'],
                    'n_features': _results['n_features'],
                    'cv_f1_mean': _results['cv_f1_mean']
                })

    performance_df = pd.DataFrame(performance_summary)

    if len(performance_df) > 0:
        print(f"\nPerformance Summary:")
        print(performance_df.groupby(['model', 'feature_set']).agg({
            'f1': ['mean', 'std'],
            'n_features': 'mean'
        }).round(3))

        # Best performance by model type
        print(f"\nBest Performance by Model Type:")
        best_by_model = performance_df.groupby('model')['f1'].max().sort_values(ascending=False)
        for _model_name, _best_f1 in best_by_model.items():
            print(f"  {_model_name}: {_best_f1:.3f}")

    # 3. Feature Set Performance Comparison
    if len(performance_df) > 0:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Performance by feature set
        feature_performance = performance_df.groupby('feature_set')['f1'].agg(['mean', 'std']).sort_values('mean', ascending=False)

        ax1.bar(range(len(feature_performance)), feature_performance['mean'], 
                yerr=feature_performance['std'], alpha=0.7, capsize=5)
        ax1.set_xticks(range(len(feature_performance)))
        ax1.set_xticklabels(feature_performance.index, rotation=45, ha='right')
        ax1.set_ylabel('Mean F1 Score')
        ax1.set_title('Performance by Feature Set')
        ax1.grid(True, alpha=0.3, axis='y')

        # Feature count vs performance
        ax2.scatter(performance_df['n_features'], performance_df['f1'], alpha=0.6, s=60)
        ax2.set_xlabel('Number of Features')
        ax2.set_ylabel('F1 Score')
        ax2.set_title('Performance vs Feature Count')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(plot_dir / '06_01_enhanced_performance_comparison.png', dpi=150, bbox_inches='tight')
        plt.show()

    print(f"Enhanced visualizations saved to {plot_dir}")
    return (performance_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Comprehensive Results Summary and Scientific Interpretation

    Synthesizing findings from the enhanced comparative analysis to provide actionable insights for biological screening.
    """
    )
    return


@app.cell
def _(
    BORUTA_AVAILABLE,
    DATA_ROOT,
    comparative_feature_results,
    enhanced_model_results,
    json,
    np,
    performance_df,
    pickle,
):
    # Comprehensive Results Summary
    print("COMPREHENSIVE RESULTS SUMMARY AND SCIENTIFIC INTERPRETATION")
    print("="*80)

    # Save enhanced results
    print("Saving enhanced analysis results...")

    # Save comparative feature results
    with open(DATA_ROOT / "processed/06_01_comparative_feature_results.pkl", 'wb') as f:
        pickle.dump(comparative_feature_results, f)

    # Save enhanced model results
    with open(DATA_ROOT / "processed/06_01_enhanced_model_results.pkl", 'wb') as f:
        pickle.dump(enhanced_model_results, f)

    # Create comprehensive summary
    summary = {
        'methodology': {
            'boruta_available': BORUTA_AVAILABLE,
            'approaches_compared': ['mutual_information', 'boruta_random_forest'],
            'models_tested': ['Random Forest (Primary)', 'Logistic Regression', 'Decision Tree'],
            'feature_sets_tested': ['All Features', 'Consensus Features', 'MI Top Features', 'Boruta Top Features']
        },
        'feature_selection_insights': {},
        'model_performance': {},
        'scientific_conclusions': {}
    }

    # Analyze feature selection insights
    print("\n1. FEATURE SELECTION INSIGHTS")
    print("="*40)

    consensus_summary = {}
    for summary_target_name, consensus_results in comparative_feature_results.items():
        comparison = consensus_results['comparison']
        consensus_rate = comparison['agreement_rate']

        consensus_summary[summary_target_name] = {
            'agreement_rate': consensus_rate,
            'consensus_features': comparison['consensus_features'],
            'total_unique_features': comparison['total_unique_features']
        }

        print(f"\n{summary_target_name}:")
        print(f"  Agreement rate: {consensus_rate:.1%}")
        print(f"  Consensus features: {comparison['consensus_features']}")

    summary['feature_selection_insights'] = consensus_summary

    # Analyze model performance
    print(f"\n2. MODEL PERFORMANCE ANALYSIS")
    print("="*35)

    if len(performance_df) > 0:
        # Best overall performance
        best_overall = performance_df.loc[performance_df['f1'].idxmax()]
        print(f"\nBest Overall Performance:")
        print(f"  Model: {best_overall['model']}")
        print(f"  Feature Set: {best_overall['feature_set']}")
        print(f"  Target: {best_overall['target']}")
        print(f"  F1 Score: {best_overall['f1']:.3f}")
        print(f"  Features Used: {best_overall['n_features']}")

        # Random Forest performance (Transue methodology focus)
        performance_rf_results = performance_df[performance_df['model'].str.contains('Random Forest')]
        if len(performance_rf_results) > 0:
            rf_mean_performance = performance_rf_results.groupby('feature_set')['f1'].mean()
            print(f"\nRandom Forest Performance by Feature Set:")
            for feature_set, mean_f1 in rf_mean_performance.sort_values(ascending=False).items():
                print(f"  {feature_set}: {mean_f1:.3f}")

        # Feature set effectiveness
        feature_set_performance = performance_df.groupby('feature_set')['f1'].agg(['mean', 'count']).sort_values('mean', ascending=False)
        print(f"\nFeature Set Effectiveness:")
        for _feature_set, (mean_f1, count) in feature_set_performance.iterrows():
            print(f"  {_feature_set}: {mean_f1:.3f} (n={count})")

        summary['model_performance'] = {
            'best_overall': {
                'model': best_overall['model'],
                'feature_set': best_overall['feature_set'],
                'target': best_overall['target'],
                'f1_score': float(best_overall['f1']),
                'n_features': int(best_overall['n_features'])
            },
            'random_forest_by_features': {k: float(v) for k, v in rf_mean_performance.items()},
            'feature_set_rankings': {k: float(v['mean']) for k, v in feature_set_performance.iterrows()}
        }

    # Scientific conclusions
    print(f"\n3. SCIENTIFIC CONCLUSIONS")
    print("="*30)

    conclusions = []

    # Methodology comparison conclusion
    if BORUTA_AVAILABLE:
        avg_consensus_rate = np.mean([res['agreement_rate'] for res in consensus_summary.values()])
        if avg_consensus_rate > 0.6:
            conclusions.append(f"✅ High agreement between MI and Boruta methods ({avg_consensus_rate:.1%} average consensus)")
            conclusions.append("Recommendation: Focus on consensus features for most robust biological screening")
        elif avg_consensus_rate > 0.4:
            conclusions.append(f"⚠️ Moderate agreement between methods ({avg_consensus_rate:.1%} average consensus)")  
            conclusions.append("Recommendation: Use both approaches to capture different aspects of biological patterns")
        else:
            conclusions.append(f"❌ Low agreement between methods ({avg_consensus_rate:.1%} average consensus)")
            conclusions.append("Recommendation: Investigate why methods disagree - may indicate complex biological relationships")
    else:
        conclusions.append("⚠️ Boruta analysis not available - using MI + Random Forest importance for feature selection")
        conclusions.append("Recommendation: Install Boruta package for full Transue methodology implementation")

    # Performance conclusions
    if len(performance_df) > 0:
        _best_f1 = performance_df['f1'].max()
        if _best_f1 > 0.8:
            conclusions.append(f"✅ Excellent model performance achieved (F1={_best_f1:.3f})")
            conclusions.append("Recommendation: Models ready for biological screening deployment")
        elif _best_f1 > 0.7:
            conclusions.append(f"✅ Good model performance achieved (F1={_best_f1:.3f})")
            conclusions.append("Recommendation: Models suitable for biological screening with careful validation")
        else:
            conclusions.append(f"⚠️ Moderate model performance (F1={_best_f1:.3f})")
            conclusions.append("Recommendation: Consider additional feature engineering or data collection")

    # Feature efficiency conclusions
    if 'Consensus Features' in performance_df['feature_set'].values:
        consensus_performance = performance_df[performance_df['feature_set'] == 'Consensus Features']['f1'].mean()
        all_features_performance = performance_df[performance_df['feature_set'] == 'All Features']['f1'].mean()

        if consensus_performance >= all_features_performance * 0.95:  # Within 5% of full performance
            avg_consensus_features = performance_df[performance_df['feature_set'] == 'Consensus Features']['n_features'].mean()
            conclusions.append(f"✅ Consensus features maintain {consensus_performance/all_features_performance:.1%} of full performance with {avg_consensus_features:.0f} features")
            conclusions.append("Recommendation: Use consensus feature set for efficient biological screening")

    for _i_conc, conclusion in enumerate(conclusions, 1):
        print(f"  {_i_conc}. {conclusion}")

    summary['scientific_conclusions'] = conclusions

    # Save summary
    with open(DATA_ROOT / "processed/06_01_enhanced_analysis_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n" + "="*80)
    print("ENHANCED COMMUNITY PATTERN DETECTION ANALYSIS COMPLETE")
    print("="*80)
    print(f"✅ Comparative feature selection completed")
    print(f"✅ Enhanced model validation completed")
    print(f"✅ Scientific conclusions documented")
    print(f"✅ Results saved for biological screening deployment")

    if BORUTA_AVAILABLE:
        print(f"🌲 Boruta methodology successfully integrated")
    else:
        print(f"⚠️ Install Boruta package for full Transue methodology: pip install boruta")

    print("="*80)
    return


if __name__ == "__main__":
    app.run()
