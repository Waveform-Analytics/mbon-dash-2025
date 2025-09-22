import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Notebook 6.2: Standardized Feature Selection Analysis

        **Purpose**: Standardize the feature selection pipeline to diagnose differences between Mutual Information and Boruta methods

        **Key Focus**: Ensure both methods use identical data, preprocessing, and random seeds to enable fair comparison

        ---

        ## Diagnostic Questions

        1. **Are both methods using the same target variable?**
        2. **Are both methods using the same preprocessed data?**
        3. **Are both methods using the same random seeds?**
        4. **Do the methods find complementary or conflicting information?**

        ## Standardization Protocol

        - **Single target variable** for direct comparison
        - **Identical preprocessing** pipeline for both methods
        - **Fixed random seeds** across all analyses
        - **Cross-validation** of both feature sets
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

    # Machine learning
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
    from sklearn.feature_selection import mutual_info_classif

    # Boruta
    try:
        from boruta import BorutaPy
        BORUTA_AVAILABLE = True
        print("✅ Boruta package available")
    except ImportError:
        BORUTA_AVAILABLE = False
        print("⚠️ Boruta package not available - install with: pip install boruta")

    # Find project root
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    DATA_ROOT = project_root / "data"
    plot_dir = DATA_ROOT.parent / "dashboard/public/views/notebooks"
    plot_dir.mkdir(exist_ok=True, parents=True)

    print("Libraries loaded successfully")
    print(f"Data root: {DATA_ROOT}")
    return (
        BORUTA_AVAILABLE,
        BorutaPy,
        DATA_ROOT,
        RandomForestClassifier,
        StandardScaler,
        StratifiedKFold,
        cross_val_score,
        mutual_info_classif,
        np,
        pd,
        plot_dir,
        plt,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Data Loading and Master Dataset Creation

        Loading the same datasets used in the enhanced community analysis.
        """
    )
    return


@app.cell
def _(DATA_ROOT, pd):
    # Load all processed datasets
    print("Loading processed datasets...")

    # Load acoustic indices
    df_indices = pd.read_parquet(DATA_ROOT / "processed/03_reduced_acoustic_indices.parquet")

    # Load detections
    df_detections = pd.read_parquet(DATA_ROOT / "processed/02_detections_aligned_2021.parquet")

    # Load environmental data
    df_env = pd.read_parquet(DATA_ROOT / "processed/02_environmental_aligned_2021.parquet")

    # Load temporal features
    df_temporal = pd.read_parquet(DATA_ROOT / "processed/02_temporal_features_2021.parquet")

    print(f"Indices shape: {df_indices.shape}")
    print(f"Detections shape: {df_detections.shape}")
    print(f"Environmental shape: {df_env.shape}")
    print(f"Temporal features shape: {df_temporal.shape}")

    return df_detections, df_env, df_indices, df_temporal


@app.cell
def _(df_detections, df_env, df_indices, df_temporal):
    # Recreate master dataset exactly as in original analysis
    print("Creating master dataset...")

    # Identify fish species directly from known columns
    fish_species = [
        'Silver perch', 'Oyster toadfish boat whistle', 'Oyster toadfish grunt', 
        'Black drum', 'Spotted seatrout', 'Red drum', 'Atlantic croaker'
    ]
    print(f"Fish species columns ({len(fish_species)}): {fish_species}")

    # Get acoustic index columns (exclude year, datetime, station)
    index_cols = [col for col in df_indices.columns if col not in ['datetime', 'station', 'year']]
    print(f"Acoustic index columns ({len(index_cols)}): {index_cols[:5]}...")

    # Create master dataset by merging all components
    df_master = df_indices.copy()

    # Merge detections
    df_master = df_master.merge(
        df_detections[['datetime', 'station'] + fish_species],
        on=['datetime', 'station'],
        how='left'
    )

    # Merge environmental
    df_master = df_master.merge(
        df_env[['datetime', 'station', 'Water temp (°C)', 'Water depth (m)']],
        on=['datetime', 'station'],
        how='left'
    )

    # Merge temporal
    df_master = df_master.merge(
        df_temporal[['datetime', 'station', 'hour', 'month']],
        on=['datetime', 'station'],
        how='left'
    )

    print(f"Master dataset shape: {df_master.shape}")

    # Create community activity metrics (same as original)
    df_community = df_master.copy()
    df_community['total_fish_activity'] = df_community[fish_species].sum(axis=1)
    df_community['num_active_species'] = (df_community[fish_species] > 0).sum(axis=1)
    df_community['any_activity'] = (df_community['total_fish_activity'] > 0).astype(int)

    # Create high activity threshold (75th percentile)
    activity_75th = df_community['total_fish_activity'].quantile(0.75)
    df_community['high_activity_75th'] = (df_community['total_fish_activity'] >= activity_75th).astype(int)

    print(f"Community metrics created:")
    print(f"  Total activity range: {df_community['total_fish_activity'].min():.0f} to {df_community['total_fish_activity'].max():.0f}")
    print(f"  Any activity: {df_community['any_activity'].mean():.1%} of periods")
    print(f"  High activity (75th): {df_community['high_activity_75th'].mean():.1%} of periods")

    return df_community, index_cols


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Standardized Feature Selection Analysis

        **Single Target Focus**: We'll analyze `high_activity_75th` as the target to enable direct comparison between methods.

        **Identical Pipeline**: Both methods will use the exact same preprocessed data and random seeds.
        """
    )
    return


@app.cell
def _(StandardScaler, df_community, index_cols):
    # STANDARDIZED FEATURE SELECTION PIPELINE
    print("="*80)
    print("STANDARDIZED FEATURE SELECTION ANALYSIS")
    print("="*80)

    # Define single target for comparison
    target_name = 'high_activity_75th'
    print(f"Target variable: {target_name}")

    # Define modeling features (same as original)
    modeling_cols = (
        index_cols + 
        ['Water temp (°C)', 'Water depth (m)', 'hour', 'month']
    )
    print(f"Total features: {len(modeling_cols)}")

    # Prepare standardized dataset
    df_modeling = df_community[modeling_cols + [target_name]].dropna()
    print(f"Modeling dataset: {df_modeling.shape[0]:,} complete samples")
    print(f"Data completeness: {len(df_modeling)/len(df_community):.1%}")

    # Feature matrix and target
    X = df_modeling[modeling_cols].values
    y = df_modeling[target_name].values

    # CRITICAL: Standardize data ONCE for both methods
    print("\nStandardizing features for both methods...")
    scaler = StandardScaler()  # StandardScaler doesn't take random_state
    X_scaled = scaler.fit_transform(X)

    print(f"Before scaling - Feature ranges:")
    print(f"  Temperature: {df_modeling['Water temp (°C)'].min():.1f} to {df_modeling['Water temp (°C)'].max():.1f}")
    print(f"  First index: {df_modeling[index_cols[0]].min():.3f} to {df_modeling[index_cols[0]].max():.3f}")
    print(f"After scaling - All features normalized to mean≈0, std≈1")

    # Target distribution
    print(f"\nTarget distribution:")
    print(f"  Class 0 (low activity): {(y==0).sum():,} samples ({(y==0).mean():.1%})")
    print(f"  Class 1 (high activity): {(y==1).sum():,} samples ({(y==1).mean():.1%})")

    return X_scaled, modeling_cols, y


@app.cell
def _(X_scaled, modeling_cols, mutual_info_classif, pd, y):
    # METHOD 1: MUTUAL INFORMATION (Standardized)
    print("\n" + "="*60)
    print("METHOD 1: MUTUAL INFORMATION ANALYSIS")
    print("="*60)

    # Fixed random seed for reproducibility
    RANDOM_SEED = 42

    # Calculate MI scores with fixed seed
    print("Computing mutual information scores...")
    mi_scores = mutual_info_classif(X_scaled, y, random_state=RANDOM_SEED)

    # Create results dataframe
    mi_results = pd.DataFrame({
        'feature': modeling_cols,
        'mi_score': mi_scores,
        'method': 'mutual_information'
    }).sort_values('mi_score', ascending=False)

    # Get top 5 features
    mi_top_5_features = mi_results.head(5)['feature'].tolist()

    print(f"Top 5 Mutual Information features:")
    for mi_i, (_, row) in enumerate(mi_results.head(5).iterrows()):
        print(f"  {mi_i+1}. {row['feature']}: {row['mi_score']:.4f}")

    print(f"\nMI feature summary:")
    print(f"  Highest scoring feature: {mi_results.iloc[0]['feature']} ({mi_results.iloc[0]['mi_score']:.4f})")
    print(f"  Mean MI score: {mi_scores.mean():.4f}")
    print(f"  MI score std: {mi_scores.std():.4f}")

    return RANDOM_SEED, mi_results, mi_top_5_features


@app.cell
def _(
    BORUTA_AVAILABLE,
    BorutaPy,
    RANDOM_SEED,
    RandomForestClassifier,
    X_scaled,
    modeling_cols,
    np,
    pd,
    y,
):
    # METHOD 2: BORUTA + RANDOM FOREST (Standardized)
    print("\n" + "="*60)
    print("METHOD 2: BORUTA + RANDOM FOREST ANALYSIS")  
    print("="*60)

    if not BORUTA_AVAILABLE:
        print("⚠️ Boruta not available - skipping this analysis")
        boruta_results = None
        boruta_top_5_features = []
        boruta_confirmed_features = []
    else:
        # Initialize Random Forest with IDENTICAL parameters and seed
        print("Initializing Random Forest for Boruta...")
        rf_for_boruta = RandomForestClassifier(
            n_estimators=100,
            max_depth=8, 
            random_state=RANDOM_SEED,  # Same seed as MI
            n_jobs=1  # Single thread for reproducibility
        )

        # Initialize Boruta with same seed
        print("Initializing Boruta selector...")
        boruta_selector = BorutaPy(
            rf_for_boruta,
            n_estimators='auto',
            verbose=1,  # Show progress
            random_state=RANDOM_SEED,  # Same seed as MI
            max_iter=50  # Reasonable limit
        )

        try:
            # Fit Boruta on IDENTICAL data
            print("Running Boruta feature selection...")
            print("(This may take a few minutes - using identical data as MI)")
            boruta_selector.fit(X_scaled, y)  # Same X_scaled and y as MI

            # Extract results
            confirmed_mask = boruta_selector.support_
            tentative_mask = boruta_selector.support_weak_

            boruta_confirmed_features = np.array(modeling_cols)[confirmed_mask].tolist()
            boruta_tentative_features = np.array(modeling_cols)[tentative_mask].tolist() 
            boruta_rejected_features = np.array(modeling_cols)[~confirmed_mask & ~tentative_mask].tolist()

            # Get feature rankings
            boruta_rankings = boruta_selector.ranking_

            # Create results dataframe
            boruta_results = pd.DataFrame({
                'feature': modeling_cols,
                'boruta_ranking': boruta_rankings,
                'boruta_decision': ['confirmed' if confirmed_mask[i] else
                                   'tentative' if tentative_mask[i] else
                                   'rejected' for i in range(len(modeling_cols))],
                'method': 'boruta'
            }).sort_values('boruta_ranking')

            # Top 5 features (confirmed + best tentative if needed)
            if len(boruta_confirmed_features) >= 5:
                boruta_top_5_features = boruta_confirmed_features[:5]
            else:
                # Include tentative features to get top 5
                all_selected = boruta_confirmed_features + boruta_tentative_features
                boruta_top_5_features = all_selected[:5]

            print(f"Boruta Results:")
            print(f"  ✅ Confirmed features: {len(boruta_confirmed_features)}")
            if boruta_confirmed_features:
                print(f"      {boruta_confirmed_features}")
            print(f"  ❓ Tentative features: {len(boruta_tentative_features)}")  
            if boruta_tentative_features:
                print(f"      {boruta_tentative_features}")
            print(f"  ❌ Rejected features: {len(boruta_rejected_features)}")

            print(f"\nTop 5 Boruta features (confirmed + tentative):")
            for boruta_i, feature in enumerate(boruta_top_5_features):
                ranking = boruta_results[boruta_results['feature'] == feature]['boruta_ranking'].iloc[0]
                decision = boruta_results[boruta_results['feature'] == feature]['boruta_decision'].iloc[0]
                print(f"  {boruta_i+1}. {feature}: rank {ranking} ({decision})")

        except Exception as e:
            print(f"❌ Boruta analysis failed: {str(e)}")
            print("This could be due to data characteristics or computational limits")
            boruta_results = None
            boruta_top_5_features = []
            boruta_confirmed_features = []

    return boruta_results, boruta_top_5_features


@app.cell
def _(boruta_top_5_features, mi_top_5_features):
    # STANDARDIZED COMPARISON ANALYSIS
    print("\n" + "="*80)
    print("STANDARDIZED COMPARISON: MUTUAL INFORMATION vs BORUTA")
    print("="*80)

    # Convert to sets for comparison (handling numpy strings)
    mi_set = set(str(f) for f in mi_top_5_features)
    boruta_set = set(str(f) for f in boruta_top_5_features)

    # Find overlaps and unique features
    consensus_features = mi_set.intersection(boruta_set)
    mi_unique = mi_set - boruta_set
    boruta_unique = boruta_set - mi_set

    print(f"FEATURE AGREEMENT ANALYSIS:")
    print(f"{'='*50}")
    print(f"🤝 Consensus features (both methods): {len(consensus_features)}")
    if consensus_features:
        print(f"    {list(consensus_features)}")
    print(f"🔍 MI-unique features: {len(mi_unique)}")  
    if mi_unique:
        print(f"    {list(mi_unique)}")
    print(f"🌲 Boruta-unique features: {len(boruta_unique)}")
    if boruta_unique:
        print(f"    {list(boruta_unique)}")

    # Calculate agreement metrics
    total_unique_features = len(mi_set.union(boruta_set))
    agreement_rate = len(consensus_features) / 5.0  # Out of top 5
    jaccard_similarity = len(consensus_features) / total_unique_features if total_unique_features > 0 else 0

    print(f"\nAGREEMENT METRICS:")
    print(f"{'='*30}")
    print(f"Agreement rate (consensus/5): {agreement_rate:.1%}")
    print(f"Jaccard similarity: {jaccard_similarity:.3f}")
    print(f"Total unique features across methods: {total_unique_features}")

    # Diagnostic insights
    print(f"\nDIAGNOSTIC INSIGHTS:")
    print(f"{'='*30}")
    if agreement_rate >= 0.6:
        print("✅ HIGH AGREEMENT: Methods identify similar important features")
    elif agreement_rate >= 0.2:
        print("⚠️ MODERATE AGREEMENT: Methods find some overlapping features")
    else:
        print("❌ LOW AGREEMENT: Methods identify largely different features")
        print("   This suggests either:")
        print("   - Complementary feature importance (both valid)")
        print("   - Different aspects of the biological signal")
        print("   - Potential methodological issues")

    comparison_results = {
        'consensus_features': list(consensus_features),
        'mi_unique': list(mi_unique),
        'boruta_unique': list(boruta_unique),
        'agreement_rate': agreement_rate,
        'jaccard_similarity': jaccard_similarity,
        'total_unique_features': total_unique_features
    }

    return (
        agreement_rate,
        comparison_results,
        jaccard_similarity,
        total_unique_features,
    )


@app.cell
def _(
    RANDOM_SEED,
    RandomForestClassifier,
    StratifiedKFold,
    X_scaled,
    boruta_top_5_features,
    comparison_results,
    cross_val_score,
    mi_top_5_features,
    modeling_cols,
    y,
):
    # CROSS-VALIDATION PERFORMANCE COMPARISON
    print("\n" + "="*80)
    print("CROSS-VALIDATION PERFORMANCE COMPARISON")
    print("="*80)

    # Test different feature sets with identical model and CV setup
    cv_folds = 5
    cv_random_state = RANDOM_SEED

    # Initialize identical model for all tests
    test_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=RANDOM_SEED,
        n_jobs=1
    )

    # Initialize CV splitter with same random state
    cv_splitter = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=cv_random_state)

    performance_results = {}

    # Test 1: All features (baseline)
    print("Testing feature set performance...")
    all_features_idx = list(range(len(modeling_cols)))
    cv_scores_all = cross_val_score(test_model, X_scaled, y, cv=cv_splitter, scoring='f1')
    performance_results['all_features'] = {
        'features': modeling_cols,
        'n_features': len(modeling_cols),
        'f1_mean': cv_scores_all.mean(),
        'f1_std': cv_scores_all.std(),
        'cv_scores': cv_scores_all
    }

    # Test 2: MI top 5 features
    if len(mi_top_5_features) > 0:
        mi_feature_idx = [modeling_cols.index(f) for f in mi_top_5_features if f in modeling_cols]
        if len(mi_feature_idx) > 0:
            cv_scores_mi = cross_val_score(test_model, X_scaled[:, mi_feature_idx], y, cv=cv_splitter, scoring='f1')
            performance_results['mi_features'] = {
                'features': mi_top_5_features,
                'n_features': len(mi_top_5_features),
                'f1_mean': cv_scores_mi.mean(),
                'f1_std': cv_scores_mi.std(),
                'cv_scores': cv_scores_mi
            }

    # Test 3: Boruta top 5 features  
    if len(boruta_top_5_features) > 0:
        boruta_feature_idx = [modeling_cols.index(f) for f in boruta_top_5_features if f in modeling_cols]
        if len(boruta_feature_idx) > 0:
            cv_scores_boruta = cross_val_score(test_model, X_scaled[:, boruta_feature_idx], y, cv=cv_splitter, scoring='f1')
            performance_results['boruta_features'] = {
                'features': boruta_top_5_features,
                'n_features': len(boruta_top_5_features),
                'f1_mean': cv_scores_boruta.mean(),
                'f1_std': cv_scores_boruta.std(),
                'cv_scores': cv_scores_boruta
            }

    # Test 4: Consensus features (if any)
    if len(comparison_results['consensus_features']) > 0:
        consensus_feature_idx = [modeling_cols.index(f) for f in comparison_results['consensus_features'] if f in modeling_cols]
        if len(consensus_feature_idx) > 0:
            cv_scores_consensus = cross_val_score(test_model, X_scaled[:, consensus_feature_idx], y, cv=cv_splitter, scoring='f1')
            performance_results['consensus_features'] = {
                'features': comparison_results['consensus_features'],
                'n_features': len(comparison_results['consensus_features']),
                'f1_mean': cv_scores_consensus.mean(),
                'f1_std': cv_scores_consensus.std(),
                'cv_scores': cv_scores_consensus
            }

    # Display results
    print(f"PERFORMANCE COMPARISON RESULTS:")
    print(f"{'='*50}")
    for feature_set_name, results in performance_results.items():
        print(f"{feature_set_name.upper()}:")
        print(f"  Features ({results['n_features']}): {results['features'][:3]}{'...' if results['n_features'] > 3 else ''}")
        print(f"  F1 Score: {results['f1_mean']:.3f} ± {results['f1_std']:.3f}")
        print(f"  CV Scores: {[f'{score:.3f}' for score in results['cv_scores']]}")
        print()

    # Find best performing feature set
    if len(performance_results) > 1:
        best_feature_set = max(performance_results.keys(), 
                              key=lambda x: performance_results[x]['f1_mean'])
        print(f"BEST PERFORMING FEATURE SET: {best_feature_set.upper()}")
        print(f"F1 Score: {performance_results[best_feature_set]['f1_mean']:.3f}")

    return (performance_results,)


@app.cell
def _(
    boruta_results,
    boruta_top_5_features,
    comparison_results,
    mi_results,
    mi_top_5_features,
    performance_results,
    plot_dir,
    plt,
):
    # VISUALIZATION: FEATURE IMPORTANCE COMPARISON
    print("\n" + "="*80)
    print("CREATING FEATURE IMPORTANCE VISUALIZATIONS")
    print("="*80)

    # Create comprehensive comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Plot 1: MI scores
    ax1 = axes[0, 0]
    top_mi = mi_results.head(10)
    bars1 = ax1.barh(range(len(top_mi)), top_mi['mi_score'], color='steelblue', alpha=0.7)
    ax1.set_yticks(range(len(top_mi)))
    ax1.set_yticklabels(top_mi['feature'], fontsize=10)
    ax1.set_xlabel('Mutual Information Score')
    ax1.set_title('Top 10 Features: Mutual Information')
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()

    # Add value labels on bars
    for bar_i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontsize=9)

    # Plot 2: Boruta rankings (if available)
    ax2 = axes[0, 1]
    if boruta_results is not None:
        # Show confirmed and tentative features
        boruta_top = boruta_results[boruta_results['boruta_decision'].isin(['confirmed', 'tentative'])].head(10)
        colors = ['green' if x == 'confirmed' else 'orange' for x in boruta_top['boruta_decision']]
        bars2 = ax2.barh(range(len(boruta_top)), 1/boruta_top['boruta_ranking'], color=colors, alpha=0.7)
        ax2.set_yticks(range(len(boruta_top)))
        ax2.set_yticklabels(boruta_top['feature'], fontsize=10)
        ax2.set_xlabel('Inverse Ranking (1/rank)')
        ax2.set_title('Top 10 Features: Boruta Selection')
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()

        # Add ranking labels
        for rank_i, (bar, rank) in enumerate(zip(bars2, boruta_top['boruta_ranking'])):
            width = bar.get_width()
            ax2.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                    f'#{int(rank)}', ha='left', va='center', fontsize=9)
    else:
        ax2.text(0.5, 0.5, 'Boruta Not Available', ha='center', va='center', 
                transform=ax2.transAxes, fontsize=14)
        ax2.set_title('Boruta Feature Selection')

    # Plot 3: Performance comparison
    ax3 = axes[1, 0]
    from matplotlib.patches import Patch

    # Prepare data for performance plot
    perf_data = []
    perf_labels = []
    perf_colors = []

    if 'all_features' in performance_results:
        perf_data.append(performance_results['all_features']['f1_mean'])
        perf_labels.append(f"All Features ({performance_results['all_features']['n_features']})")
        perf_colors.append('gray')

    if 'mi_features' in performance_results:
        perf_data.append(performance_results['mi_features']['f1_mean'])
        perf_labels.append(f"MI Features ({performance_results['mi_features']['n_features']})")
        perf_colors.append('steelblue')

    if 'boruta_features' in performance_results:
        perf_data.append(performance_results['boruta_features']['f1_mean'])
        perf_labels.append(f"Boruta Features ({performance_results['boruta_features']['n_features']})")
        perf_colors.append('green')

    if 'consensus_features' in performance_results:
        perf_data.append(performance_results['consensus_features']['f1_mean'])
        perf_labels.append(f"Consensus Features ({performance_results['consensus_features']['n_features']})")
        perf_colors.append('purple')

    if perf_data:
        bars3 = ax3.bar(range(len(perf_data)), perf_data, color=perf_colors, alpha=0.7)
        ax3.set_xticks(range(len(perf_data)))
        ax3.set_xticklabels(perf_labels, rotation=45, ha='right')
        ax3.set_ylabel('F1 Score (CV Mean)')
        ax3.set_title('Cross-Validation Performance Comparison')
        ax3.grid(axis='y', alpha=0.3)

        # Add error bars if available
        if 'std' in str(performance_results):
            error_bars = []
            for key in ['all_features', 'mi_features', 'boruta_features', 'consensus_features']:
                if key in performance_results:
                    error_bars.append(performance_results[key]['f1_std'])
            if error_bars:
                ax3.errorbar(range(len(perf_data)), perf_data, yerr=error_bars[:len(perf_data)], 
                           fmt='none', color='black', capsize=3)

        # Add value labels on bars
        for perf_i, bar in enumerate(bars3):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=10)

    # Plot 4: Feature overlap visualization
    ax4 = axes[1, 1]

    # Create Venn-like visualization
    if len(mi_top_5_features) > 0 and len(boruta_top_5_features) > 0:
        # Simple overlap bar chart
        overlap_data = [
            len(comparison_results['mi_unique']),
            len(comparison_results['consensus_features']), 
            len(comparison_results['boruta_unique'])
        ]
        overlap_labels = ['MI Only', 'Both Methods', 'Boruta Only']
        overlap_colors = ['steelblue', 'purple', 'green']

        bars4 = ax4.bar(overlap_labels, overlap_data, color=overlap_colors, alpha=0.7)
        ax4.set_ylabel('Number of Features')
        ax4.set_title('Feature Selection Overlap')
        ax4.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig(plot_dir / '06_02_standardized_feature_selection_comparison.png', 
                dpi=150, bbox_inches='tight')
    plt.show()

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Summary and Diagnostic Conclusions

        Standardized analysis results and recommendations for resolving feature selection differences.
        """
    )
    return


@app.cell
def _(
    agreement_rate,
    jaccard_similarity,
    performance_results,
    total_unique_features,
):
    # FINAL DIAGNOSTIC SUMMARY
    print("="*80)
    print("STANDARDIZED FEATURE SELECTION: DIAGNOSTIC SUMMARY")
    print("="*80)

    print(f"\n📊 QUANTITATIVE RESULTS:")
    print(f"{'='*30}")
    print(f"Feature Agreement Rate: {agreement_rate:.1%}")
    print(f"Jaccard Similarity: {jaccard_similarity:.3f}")
    print(f"Total Unique Features: {total_unique_features}")

    print(f"\n🔍 DIAGNOSTIC CONCLUSIONS:")
    print(f"{'='*30}")

    # Determine primary cause of disagreement
    if agreement_rate < 0.3:
        print("❌ PRIMARY ISSUE: Low feature agreement indicates:")
        print("   1. Methods capture DIFFERENT aspects of biological signal")
        print("   2. Non-linear vs linear feature relationships") 
        print("   3. Ensemble vs univariate feature selection")
        print("\n   INTERPRETATION: This is likely METHODOLOGICAL, not problematic")

    elif agreement_rate < 0.6:
        print("⚠️ MODERATE DISAGREEMENT suggests:")
        print("   1. Complementary feature selection approaches")
        print("   2. Some shared signal, some method-specific insights")
        print("   3. Potential for feature combination strategies")

    else:
        print("✅ HIGH AGREEMENT indicates:")
        print("   1. Robust feature importance across methods")
        print("   2. Strong biological signal in selected features")
        print("   3. Consistent analytical conclusions")

    # Performance-based recommendations
    print(f"\n🎯 PERFORMANCE-BASED RECOMMENDATIONS:")
    print(f"{'='*40}")

    if 'mi_features' in performance_results and 'boruta_features' in performance_results:
        mi_perf = performance_results['mi_features']['f1_mean']
        boruta_perf = performance_results['boruta_features']['f1_mean']

        if abs(mi_perf - boruta_perf) < 0.02:
            print("✅ SIMILAR PERFORMANCE: Both methods yield comparable results")
            print("   → Recommendation: Use consensus features + best performers")

        elif mi_perf > boruta_perf:
            print("📈 MI OUTPERFORMS: Mutual Information features perform better")
            print(f"   → MI F1: {mi_perf:.3f} vs Boruta F1: {boruta_perf:.3f}")
            print("   → Recommendation: Prioritize MI-selected features")

        else:
            print("🌲 BORUTA OUTPERFORMS: Random Forest features perform better")
            print(f"   → Boruta F1: {boruta_perf:.3f} vs MI F1: {mi_perf:.3f}")
            print("   → Recommendation: Prioritize Boruta-selected features")

    # Scientific interpretation
    print(f"\n🧬 BIOLOGICAL INTERPRETATION:")
    print(f"{'='*35}")
    print("The disagreement between methods may reflect:")
    print("• MI: Captures threshold/non-linear biological responses")
    print("• Boruta: Identifies consistent predictive patterns")
    print("• Both valid: Different aspects of acoustic-biological relationships")

    print(f"\n📋 NEXT STEPS:")
    print(f"{'='*15}")
    print("1. ✅ Standardization complete - methods now comparable")
    print("2. 🔄 Test combined feature sets (MI + Boruta)")
    print("3. 📊 Validate on independent data/time periods") 
    print("4. 🔬 Examine biological relevance of unique features")
    print("5. 📖 Document methodological differences for publication")

    return


if __name__ == "__main__":
    app.run()
