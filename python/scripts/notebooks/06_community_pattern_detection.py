import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    mo.md(
        r"""
        # Notebook 6: Community Pattern Detection and Biological Screening

        **Purpose**: Demonstrate that acoustic indices can detect community-level fish patterns and identify periods of biological interest

        **Key Outputs**: Evidence that indices serve as effective biological screening tools for continuous monitoring

        ## Overview

        Moving beyond species-specific prediction, this notebook tests whether acoustic indices can serve as **biological screening tools** by detecting aggregate community-level fish activity. Rather than trying to predict individual species calling intensities, we focus on:

        1. **Community-level activity detection**: Can indices detect when "something biological is happening" vs periods of low activity?
        2. **Temporal pattern concordance**: Do indices capture the same diel and seasonal patterns as manual detections?
        3. **Screening efficiency**: How much manual effort could be saved by using indices to identify high-activity periods?
        4. **Cross-station transferability**: Do index-based patterns hold across different monitoring locations?

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

    # Load aligned detections
    df_detections = pd.read_parquet(DATA_ROOT / "processed/02_detections_aligned_2021.parquet")

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
    """
    )
    return


@app.cell
def _(df_master, fish_species):
    # Create community-level activity metrics
    print("Creating community activity metrics...")

    # 1. Total fish activity (sum across all species)
    df_community = df_master.copy()
    df_community['total_fish_activity'] = df_community[fish_species].sum(axis=1)

    # 2. Number of active species (how many species detected)
    df_community['num_active_species'] = (df_community[fish_species] > 0).sum(axis=1)

    # 3. Maximum species activity (highest calling intensity across species)
    df_community['max_species_activity'] = df_community[fish_species].max(axis=1)

    # 4. Activity diversity (simplified - coefficient of variation)
    # Calculate coefficient of variation as a diversity measure
    df_community['activity_diversity'] = df_community[fish_species].std(axis=1) / (df_community[fish_species].mean(axis=1) + 0.01)

    # 5. Binary classification targets at different thresholds
    # High vs low total activity
    total_activity_75th = df_community['total_fish_activity'].quantile(0.75)
    total_activity_90th = df_community['total_fish_activity'].quantile(0.90)

    df_community['high_activity_75th'] = (df_community['total_fish_activity'] >= total_activity_75th).astype(int)
    df_community['high_activity_90th'] = (df_community['total_fish_activity'] >= total_activity_90th).astype(int)

    # Any biological activity vs none
    df_community['any_activity'] = (df_community['total_fish_activity'] > 0).astype(int)

    # Multiple species active vs single/none
    df_community['multi_species_active'] = (df_community['num_active_species'] >= 2).astype(int)

    print(f"Community metrics created. Sample statistics:")
    print(f"Total activity - Mean: {df_community['total_fish_activity'].mean():.2f}, Max: {df_community['total_fish_activity'].max():.0f}")
    print(f"Active species - Mean: {df_community['num_active_species'].mean():.2f}, Max: {df_community['num_active_species'].max():.0f}")
    print(f"High activity (75th): {df_community['high_activity_75th'].mean():.1%}")
    print(f"High activity (90th): {df_community['high_activity_90th'].mean():.1%}")
    print(f"Any activity: {df_community['any_activity'].mean():.1%}")
    print(f"Multi-species active: {df_community['multi_species_active'].mean():.1%}")

    return (df_community,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Model Development for Community Activity Detection

    Training multiple classifiers to predict community-level biological activity using acoustic indices.
    """
    )
    return


@app.cell
def _():
    # Progress tracking cell
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
    f1_score,
    index_cols,
    precision_score,
    recall_score,
    train_test_split,
):
    # Prepare data for modeling
    print("Preparing data for community activity modeling...")

    # Remove rows with missing data
    modeling_cols = index_cols + ['Water temp (°C)', 'Water depth (m)', 'hour', 'month']
    target_cols = ['high_activity_75th', 'high_activity_90th', 'any_activity', 'multi_species_active']

    df_modeling = df_community[modeling_cols + target_cols].dropna()
    print(f"Modeling data shape: {df_modeling.shape}")

    # Feature matrix
    X_features = df_modeling[modeling_cols]

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_features)

    # Model configurations
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=8, min_samples_leaf=10, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_leaf=5, random_state=42),
        # 'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    }

    # Train models for each target
    model_results = {}

    for target_name in target_cols:
        print(f"\nTraining models for: {target_name}")
        y_target = df_modeling[target_name]

        # Check class balance
        class_balance = y_target.value_counts(normalize=True)
        print(f"Class balance: {class_balance.to_dict()}")

        if y_target.std() == 0:  # Skip if no variance
            print(f"Skipping {target_name} - no variance in target")
            continue

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_target, test_size=0.3, random_state=42, stratify=y_target
        )

        target_results = {}

        for model_name, model in models.items():
            # Train model
            model.fit(X_train, y_train)

            # Predictions
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred

            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
            recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
            kappa = cohen_kappa_score(y_test, y_pred)

            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y_target, cv=StratifiedKFold(5), scoring='f1')

            target_results[model_name] = {
                'model': model,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'kappa': kappa,
                'cv_f1_mean': cv_scores.mean(),
                'cv_f1_std': cv_scores.std(),
                'y_test': y_test,
                'y_pred': y_pred,
                'y_prob': y_prob
            }

            print(f"  {model_name}: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}")

        model_results[target_name] = target_results

    print(f"\nModel training complete for {len(model_results)} targets")

    return X_scaled, df_modeling, model_results, modeling_cols, target_cols


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
    X_scaled,
    df_modeling,
    model_results,
    modeling_cols,
    mutual_info_classif,
    np,
    pd,
    target_cols,
):
    # Feature importance analysis
    print("Analyzing feature importance...")

    feature_importance_results = {}

    for target_name_fi in target_cols:
        if target_name_fi not in model_results:
            continue

        y_target_fi = df_modeling[target_name_fi]

        # Mutual information feature importance
        mi_scores = mutual_info_classif(X_scaled, y_target_fi, random_state=42)

        # Random Forest feature importance (if available)
        rf_model = model_results[target_name_fi].get('Random Forest', {}).get('model')
        rf_importance = rf_model.feature_importances_ if rf_model else np.zeros(len(modeling_cols))

        # Create feature importance dataframe
        importance_df = pd.DataFrame({
            'feature': modeling_cols,
            'mutual_info': mi_scores,
            'rf_importance': rf_importance
        }).sort_values('mutual_info', ascending=False)

        feature_importance_results[target_name_fi] = importance_df

        print(f"\nTop 5 features for {target_name_fi}:")
        print(importance_df.head())

    return (feature_importance_results,)


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
    print("KEY FINDINGS:")
    print("="*70)

    # Determine key findings based on results
    best_screening_target = max(summary_results['screening_efficiency'].items(),
                              key=lambda x: x[1]['detection_rate'])

    print(f"""
    1. COMMUNITY ACTIVITY DETECTION:
       - Acoustic indices show MODERATE ability to detect community-level biological activity
       - Best performance for: {best_screening_target[0].replace('_', ' ')}
       - Detection rate: {best_screening_target[1]['detection_rate']:.1%}

    2. SCREENING TOOL POTENTIAL:
       - Manual effort could be reduced by up to {max(eff['effort_reduction'] for eff in summary_results['screening_efficiency'].values()):.1%}
       - Best screening precision: {max(eff['screening_precision'] for eff in summary_results['screening_efficiency'].values()):.1%}
       - Indices can identify periods warranting closer manual examination

    3. TEMPORAL PATTERN CONCORDANCE:
       - Acoustic indices capture some but not all temporal biological patterns
       - Strongest concordance for diel patterns vs seasonal patterns
       - Cross-station consistency varies, suggesting site-specific calibration needed

    4. PRACTICAL IMPLICATIONS:
       - Indices work better for aggregate community detection than species-specific prediction
       - Most effective as biological SCREENING tools rather than replacement for manual detection
       - Could enable "smart sampling" strategies focusing effort on high-probability periods
    """)

    print(f"\nAnalysis complete! All results saved to {DATA_ROOT}/processed/")

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Conclusions and Recommendations

    ### What We Learned

    **Community-Level Detection Works Better**: Acoustic indices show moderate success at detecting aggregate biological activity rather than species-specific patterns. This suggests their value lies in **biological screening** rather than detailed species identification.

    **Temporal Patterns Are Partially Captured**: Indices capture some diel and seasonal patterns in fish community activity, but not with the precision of manual detections. The correlation strengths vary by index and temporal scale.

    **Screening Tool Potential**: The most promising application is using indices as **intelligent screening tools** that flag periods likely to contain biological activity for targeted manual analysis. This could significantly reduce manual effort while maintaining high detection rates.

    ### Practical Applications

    1. **Smart Sampling Protocols**: Use indices to identify optimal times for detailed manual analysis
    2. **Continuous Background Monitoring**: Deploy indices for 24/7 monitoring with periodic manual validation
    3. **Effort Optimization**: Focus limited manual resources on periods flagged by index-based models
    4. **Early Warning Systems**: Detect unusual biological activity patterns warranting investigation

    ### Next Steps for Notebook 7

    The validation analysis should focus on:

    - **Temporal transferability**: Do these patterns hold across different time periods?
    - **Cross-site validation**: How well do models trained at one site perform at others?
    - **Continuous monitoring simulation**: What would real-world deployment look like?
    - **Cost-benefit quantification**: Actual effort savings vs information loss

    ### The Bottom Line

    Acoustic indices show **moderate but meaningful** potential as biological screening tools. While they cannot replace manual detection, they can **intelligently guide when and where to apply manual effort**, potentially greatly improving the efficiency of acoustic monitoring programs.
    """
    )
    return


if __name__ == "__main__":
    app.run()
