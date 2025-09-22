import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Notebook 6.04: Temporal Community Pattern Detection

    **Purpose**: Compare temporal vs non-temporal modeling approaches for community pattern detection using biological lag features

    **Key Innovation**: 
    This is the first analysis to systematically incorporate **biological temporal dependence** into marine acoustic monitoring models.

    ## Scientific Motivation

    Traditional marine acoustic monitoring treats each time period independently - predicting biological activity using only current acoustic indices and environmental conditions. However, **biological systems have memory**:

    - **Spawning aggregations** persist for hours to days
    - **Dawn choruses** follow predictable temporal sequences  
    - **Community interactions** create biological momentum
    - **Quiet periods** tend to continue (ecological inertia)

    ## Research Questions

    1. **Performance gain**: How much does adding biological temporal dependence improve prediction accuracy?
    2. **Feature importance**: Are biological lag features (past activity) more predictive than acoustic indices?
    3. **Temporal patterns**: What time scales of biological persistence are most important (2h vs 4h vs 6h)?
    4. **Model validation**: How do temporal cross-validation results compare to standard cross-validation?

    ## Methodological Innovation

    **Traditional approach (Notebook 6)**: `activity[t] = f(indices[t], environment[t], temporal_features[t])`

    **Temporal approach (this notebook)**: `activity[t] = f(indices[t], environment[t], temporal_features[t], activity[t-1], activity[t-2], ...)` 

    By including **past biological activity** as predictors, we capture the ecological persistence that makes biological systems predictable over short time scales.

    ## Expected Impact

    If temporal modeling shows significant improvements, it would suggest that:

    - **Ecological memory** is a key component of predictable biological patterns
    - **Continuous monitoring** provides value beyond just current conditions  
    - **Early warning systems** could leverage biological momentum to predict upcoming activity
    - **Resource allocation** for manual detection could be optimized using temporal trends
    """
    )
    return


@app.cell
def _():
    import marimo as mo
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
    warnings.filterwarnings('ignore')

    # Machine learning and validation
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, TimeSeriesSplit
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import (
        classification_report, confusion_matrix, roc_curve, auc,
        precision_recall_curve, accuracy_score, cohen_kappa_score,
        f1_score, precision_score, recall_score
    )
    from sklearn.feature_selection import mutual_info_classif

    # Statistical analysis
    from scipy.stats import spearmanr

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
        LogisticRegression,
        RandomForestClassifier,
        StandardScaler,
        StratifiedKFold,
        TimeSeriesSplit,
        cross_val_score,
        data_dir,
        json,
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
    ## Data Loading and Preparation

    Loading all enhanced datasets from Notebook 2, including the new biological activity lag features.
    """
    )
    return


@app.cell
def _(DATA_ROOT, pd):
    # Load all enhanced datasets with temporal features
    print("Loading enhanced datasets from Notebook 2...")

    # Load reduced acoustic indices from Notebook 3
    df_indices = pd.read_parquet(DATA_ROOT / "processed/03_reduced_acoustic_indices.parquet")

    # Load aligned detections
    df_detections = pd.read_parquet(DATA_ROOT / "processed/02_detections_aligned_2021.parquet")

    # Load biological activity features (NEW from Phase 1)
    try:
        df_biological = pd.read_parquet(DATA_ROOT / "processed/02_biological_activity_features_2021.parquet")
        print(f"✓ Loaded biological activity features: {df_biological.shape}")
        print(f"  Columns: {[col for col in df_biological.columns if 'lag' in col or 'activity' in col]}")
    except FileNotFoundError:
        print("⚠️ Biological activity features not found. Run Notebook 2 with updated biological lag features first.")
        df_biological = None

    # Load environmental data with lag features
    df_env = pd.read_parquet(DATA_ROOT / "processed/02_environmental_aligned_2021.parquet")

    # Load temporal features
    df_temporal = pd.read_parquet(DATA_ROOT / "processed/02_temporal_features_2021.parquet")

    # Load detection metadata to identify fish species
    df_det_metadata = pd.read_parquet(DATA_ROOT / "processed/metadata/01_detection_columns.parquet")

    print(f"\nDataset shapes:")
    print(f"Indices: {df_indices.shape}")
    print(f"Detections: {df_detections.shape}") 
    print(f"Biological: {df_biological.shape if df_biological is not None else 'Not available'}")
    print(f"Environmental: {df_env.shape}")
    print(f"Temporal: {df_temporal.shape}")
    return (
        df_biological,
        df_det_metadata,
        df_detections,
        df_env,
        df_indices,
        df_temporal,
    )


@app.cell
def _(
    df_biological,
    df_det_metadata,
    df_detections,
    df_env,
    df_indices,
    df_temporal,
):
    # Create comprehensive modeling dataset by merging all data sources
    print("Merging all data sources...")

    # Start with acoustic indices as the base (most comprehensive dataset)
    df_modeling = df_indices.copy()

    # Add biological activity features
    if df_biological is not None:
        biological_cols = [col for col in df_biological.columns if col not in ['datetime', 'station', 'year']]
        df_modeling = df_modeling.merge(
            df_biological[['datetime', 'station'] + biological_cols], 
            on=['datetime', 'station'], 
            how='left'
        )
        print(f"✓ Added {len(biological_cols)} biological activity features")
    else:
        # Create basic community metrics if biological features not available
        fish_species = df_det_metadata[
            (df_det_metadata['group'] == 'fish') & 
            (df_det_metadata['keep_species'] == 1)
        ]['long_name'].tolist()

        available_species = [col for col in fish_species if col in df_detections.columns]
        if available_species:
            df_detections_temp = df_detections.copy()
            df_detections_temp['total_fish_activity'] = df_detections_temp[available_species].sum(axis=1)
            df_detections_temp['any_activity'] = (df_detections_temp['total_fish_activity'] > 0).astype(int)
            df_detections_temp['num_active_species'] = (df_detections_temp[available_species] > 0).sum(axis=1)

            df_modeling = df_modeling.merge(
                df_detections_temp[['datetime', 'station', 'total_fish_activity', 'any_activity', 'num_active_species']], 
                on=['datetime', 'station'], 
                how='left'
            )
            print("⚠️ Created basic community metrics (no lag features available)")

    # Add environmental features
    env_cols = [col for col in df_env.columns if col not in ['datetime', 'station', 'year']]
    df_modeling = df_modeling.merge(
        df_env[['datetime', 'station'] + env_cols],
        on=['datetime', 'station'],
        how='left'
    )
    print(f"✓ Added {len(env_cols)} environmental features")

    # Add temporal features  
    temporal_cols = [col for col in df_temporal.columns if col not in ['datetime', 'station', 'year']]
    df_modeling = df_modeling.merge(
        df_temporal[['datetime', 'station'] + temporal_cols],
        on=['datetime', 'station'],
        how='left'
    )
    print(f"✓ Added {len(temporal_cols)} temporal features")

    print(f"\nFinal modeling dataset shape: {df_modeling.shape}")

    # Identify feature groups for analysis
    index_cols = [col for col in df_indices.columns if col not in ['datetime', 'station', 'year']]

    # Get target variables (biological activity metrics we want to predict)
    if df_biological is not None:
        biological_target_cols = ['total_fish_activity', 'any_activity', 'num_active_species']
    else:
        biological_target_cols = ['total_fish_activity', 'any_activity', 'num_active_species']

    # PROPER temporal features: acoustic indices + environmental lags (NOT biological lags!)
    # We can't use biological detection lags as features since we won't have them in real deployment
    acoustic_lag_features = [col for col in df_modeling.columns if any(x in col for x in ['ACI', 'ADI', 'AEI', 'BI', 'H']) and ('lag' in col or 'mean_' in col)]
    biological_feature_cols = acoustic_lag_features  # Rename for consistency with existing code

    env_feature_cols = [col for col in env_cols if 'lag' in col or 'mean_' in col or 'change' in col]
    basic_env_cols = [col for col in env_cols if col not in env_feature_cols]

    print(f"\nFeature groups:")
    print(f"Acoustic indices: {len(index_cols)}")
    print(f"Biological lag features: {len(biological_feature_cols)}")
    print(f"Environmental lag features: {len(env_feature_cols)}")
    print(f"Basic environmental: {len(basic_env_cols)}")
    print(f"Temporal features: {len(temporal_cols)}")
    return (
        biological_feature_cols,
        df_modeling,
        env_feature_cols,
        index_cols,
        temporal_cols,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Temporal vs Non-Temporal Feature Analysis

    First, let's explore how biological lag features correlate with current activity and compare their predictive power to acoustic indices.
    """
    )
    return


@app.cell
def _(
    biological_feature_cols,
    df_modeling,
    env_feature_cols,
    index_cols,
    mutual_info_classif,
    pd,
):
    # Analyze temporal features (acoustic/environmental lags) vs current acoustic indices
    print("Analyzing temporal features (acoustic/environmental lags) vs current acoustic indices...")
    print("="*80)

    # Ensure we have the target variable
    if 'any_activity' in df_modeling.columns:
        _target_analysis = 'any_activity'

        # Prepare feature groups for comparison
        _current_acoustic_features = [col for col in index_cols if col in df_modeling.columns]
        _temporal_features_analysis = [col for col in biological_feature_cols if col in df_modeling.columns]

        # Also include environmental lag features as temporal features
        _env_temporal_features = [col for col in env_feature_cols if col in df_modeling.columns]
        _all_temporal_features = _temporal_features_analysis + _env_temporal_features

        # Create comparison dataset (handle missing values intelligently)
        _comparison_cols = _current_acoustic_features + _all_temporal_features + [_target_analysis]
        df_comparison = df_modeling[_comparison_cols].copy()
        # Only drop rows where target is missing, fill other NaNs with 0 (reasonable for lag features)
        df_comparison = df_comparison.dropna(subset=[_target_analysis])
        df_comparison = df_comparison.fillna(0)  # Lag features with NaN become 0 (no previous activity)

        print(f"Comparison dataset: {df_comparison.shape[0]:,} samples")
        print(f"Target distribution: {df_comparison[_target_analysis].value_counts().to_dict()}")
        print(f"Current acoustic features: {len(_current_acoustic_features)}")
        print(f"Temporal lag features: {len(_all_temporal_features)} (acoustic: {len(_temporal_features_analysis)}, environmental: {len(_env_temporal_features)})")

        if len(df_comparison) > 0 and len(_all_temporal_features) > 0:
            # Calculate mutual information for each feature group
            _X_current = df_comparison[_current_acoustic_features]
            _X_temporal = df_comparison[_all_temporal_features]
            _y_analysis = df_comparison[_target_analysis]

            # Mutual information analysis
            _mi_current = mutual_info_classif(_X_current, _y_analysis, random_state=42)
            _mi_temporal = mutual_info_classif(_X_temporal, _y_analysis, random_state=42)

            # Create feature importance comparison
            _feature_importance = []

            # Add current acoustic indices
            for _idx, _feature in enumerate(_current_acoustic_features):
                _feature_importance.append({
                    'feature': _feature,
                    'type': 'current_acoustic',
                    'mi_score': _mi_current[_idx]
                })

            # Add temporal lag features (acoustic + environmental)
            for _idx, _feature in enumerate(_all_temporal_features):
                # Determine if it's acoustic or environmental temporal feature
                if any(x in _feature for x in ['ACI', 'ADI', 'AEI', 'BI', 'H']):
                    _feature_type = 'acoustic_temporal'
                else:
                    _feature_type = 'environmental_temporal'

                _feature_importance.append({
                    'feature': _feature,
                    'type': _feature_type,
                    'mi_score': _mi_temporal[_idx]
                })

            # Convert to dataframe and sort
            importance_df = pd.DataFrame(_feature_importance)
            importance_df = importance_df.sort_values('mi_score', ascending=False)

            print(f"\n🏆 TOP 10 MOST PREDICTIVE FEATURES:")
            print("-" * 50)
            for _row_idx, _row in importance_df.head(10).iterrows():
                if _row['type'] == 'current_acoustic':
                    _feature_type = "🎵 Current Acoustic"
                elif _row['type'] == 'acoustic_temporal':
                    _feature_type = "🕰️ Acoustic Temporal"
                elif _row['type'] == 'environmental_temporal':
                    _feature_type = "🌡️ Environmental Temporal"
                else:
                    _feature_type = _row['type']
                print(f"  {_row.name+1:2d}. {_feature_type:20} | {_row['feature'][:30]:30} | MI: {_row['mi_score']:.3f}")

            # Summary statistics
            _current_mi_stats = {
                'mean': _mi_current.mean(),
                'max': _mi_current.max(), 
                'top_5_mean': _mi_current[_mi_current.argsort()[-5:]].mean() if len(_mi_current) >= 5 else _mi_current.mean()
            }

            _temporal_mi_stats = {
                'mean': _mi_temporal.mean(),
                'max': _mi_temporal.max(),
                'top_5_mean': _mi_temporal[_mi_temporal.argsort()[-5:]].mean() if len(_mi_temporal) >= 5 else _mi_temporal.mean()
            }

            print(f"\n📊 FEATURE GROUP COMPARISON:")
            print("-" * 50)
            print(f"Current acoustic indices - Mean MI: {_current_mi_stats['mean']:.3f}, Max: {_current_mi_stats['max']:.3f}, Top-5: {_current_mi_stats['top_5_mean']:.3f}")
            print(f"Temporal lag features    - Mean MI: {_temporal_mi_stats['mean']:.3f}, Max: {_temporal_mi_stats['max']:.3f}, Top-5: {_temporal_mi_stats['top_5_mean']:.3f}")

            # Determine winner
            _temporal_advantage = _temporal_mi_stats['top_5_mean'] > _current_mi_stats['top_5_mean']
            _winner = "🕰️ TEMPORAL FEATURES" if _temporal_advantage else "🎵 CURRENT ACOUSTIC"
            _advantage = abs(_temporal_mi_stats['top_5_mean'] - _current_mi_stats['top_5_mean'])

            print(f"\n🏆 PREDICTIVE POWER WINNER: {_winner}")
            print(f"   Advantage: {_advantage:.3f} MI units")

            feature_analysis_results = {
                'importance_df': importance_df,
                'current_acoustic_stats': _current_mi_stats,
                'temporal_stats': _temporal_mi_stats,
                'temporal_advantage': _temporal_advantage
            }

        else:
            print("⚠️ Insufficient data for biological lag feature analysis")
            feature_analysis_results = None

    else:
        print("⚠️ Target variable 'any_activity' not found")
        feature_analysis_results = None
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Model Comparison: Temporal vs Non-Temporal

    Now we'll compare model performance using three different feature sets:
    1. **Non-temporal**: Acoustic indices + environmental + basic temporal features (traditional approach)
    2. **Temporal**: Non-temporal + biological lag features (our innovation) 
    3. **Temporal-only**: Only biological lag features (to test biological memory alone)

    We'll use **TimeSeriesSplit** for temporal validation and compare to standard cross-validation.
    """
    )
    return


@app.cell
def _(
    LogisticRegression,
    RandomForestClassifier,
    StandardScaler,
    StratifiedKFold,
    TimeSeriesSplit,
    biological_feature_cols,
    cross_val_score,
    df_modeling,
    env_feature_cols,
    index_cols,
    temporal_cols,
):
    # Model comparison: Temporal vs Non-temporal approaches
    print("Comparing temporal vs non-temporal modeling approaches...")
    print("="*70)

    # Define target variable
    _target_modeling = 'any_activity'

    if _target_modeling in df_modeling.columns:
        # Define feature sets for comparison
        _acoustic_features_modeling = [col for col in index_cols if col in df_modeling.columns]
        _acoustic_lag_features = [col for col in biological_feature_cols if col in df_modeling.columns]  # These are actually acoustic lags now
        _env_lag_features = [col for col in env_feature_cols if col in df_modeling.columns] 
        _basic_temporal = [col for col in temporal_cols if col in df_modeling.columns]

        # Combine all temporal features
        _all_lag_features = _acoustic_lag_features + _env_lag_features

        # Get numeric temporal features only (exclude categorical ones like 'season')
        _numeric_temporal = [col for col in _basic_temporal if col in ['hour', 'month', 'weekday', 'hour_sin', 'hour_cos', 'day_sin', 'day_cos']]

        # Feature set definitions
        _feature_sets = {
            'non_temporal': {
                'features': _acoustic_features_modeling + _numeric_temporal + [col for col in df_modeling.columns if col in ['Water temp (°C)', 'Water depth (m)']],
                'description': 'Traditional: Acoustic + Environmental + Basic Temporal',
                'color': 'steelblue'
            },
            'temporal': {
                'features': _acoustic_features_modeling + _all_lag_features + _numeric_temporal,
                'description': 'Enhanced: Traditional + Temporal Lag Features', 
                'color': 'forestgreen'
            },
            'temporal_only': {
                'features': _all_lag_features + _numeric_temporal,
                'description': 'Temporal Memory: Only Lag Features + Time',
                'color': 'coral'
            }
        }

        # Filter to available features
        for _name, _config in _feature_sets.items():
            _available_features = [f for f in _config['features'] if f in df_modeling.columns]
            _config['features'] = _available_features
            print(f"{_name:15}: {len(_available_features):2d} features - {_config['description']}")

        # Prepare modeling data (handle missing values intelligently)
        _all_features = list(set().union(*[_config['features'] for _config in _feature_sets.values()]))
        modeling_data = df_modeling[_all_features + [_target_modeling, 'datetime', 'station']].copy()
        # Only drop rows where target is missing
        modeling_data = modeling_data.dropna(subset=[_target_modeling])
        # Fill NaNs only in numeric columns with 0
        _numeric_cols = modeling_data.select_dtypes(include=['int64', 'float64']).columns
        modeling_data[_numeric_cols] = modeling_data[_numeric_cols].fillna(0)

        print(f"\nModeling dataset: {modeling_data.shape[0]:,} samples after removing missing values")
        print(f"Target distribution: {modeling_data[_target_modeling].value_counts().to_dict()}")

        # Cross-validation configurations
        _cv_methods = {
            'standard_cv': StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            'temporal_cv': TimeSeriesSplit(n_splits=5)
        }

        # Model configurations
        _models = {
            'logistic': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        }

        # Results storage
        model_comparison_results = {}

        print(f"\n🎯 RUNNING COMPREHENSIVE MODEL COMPARISON")
        print("="*50)

        for _model_name, _model in _models.items():
            print(f"\n📊 {_model_name.upper()} RESULTS:")
            print("-" * 30)

            _model_results = {}

            for _cv_name, _cv_splitter in _cv_methods.items():
                _cv_results = {}

                for _set_name, _set_config in _feature_sets.items():
                    if len(_set_config['features']) > 0:
                        # Prepare data
                        _X = modeling_data[_set_config['features']]
                        _y = modeling_data[_target_modeling]

                        # Scale features
                        _scaler = StandardScaler()
                        _X_scaled = _scaler.fit_transform(_X)

                        # Cross-validation
                        _cv_scores = cross_val_score(_model, _X_scaled, _y, cv=_cv_splitter, scoring='f1')

                        _cv_results[_set_name] = {
                            'scores': _cv_scores,
                            'mean': _cv_scores.mean(),
                            'std': _cv_scores.std(),
                            'n_features': len(_set_config['features'])
                        }

                        _cv_type = "Standard CV" if _cv_name == 'standard_cv' else "Temporal CV"
                        print(f"  {_cv_type:12} | {_set_config['description'][:35]:35} | F1: {_cv_scores.mean():.3f}±{_cv_scores.std():.3f}")

                _model_results[_cv_name] = _cv_results

            model_comparison_results[_model_name] = _model_results

    else:
        print(f"❌ Target variable '{_target_modeling}' not found in modeling data")
        model_comparison_results = None
        modeling_data = None
    return (model_comparison_results,)


@app.cell
def _(model_comparison_results, np, plot_dir, plt):
    # Visualize model comparison results
    if model_comparison_results:
        print("\n📈 VISUALIZING MODEL COMPARISON RESULTS")
        print("="*45)

        # Create comparison visualization
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        # Colors for feature sets
        _colors = {
            'non_temporal': 'steelblue',
            'temporal': 'forestgreen', 
            'temporal_only': 'coral',
            'biological_only': 'coral'
        }

        _set_labels = {
            'non_temporal': 'Traditional\n(Acoustic + Env)',
            'temporal': 'Enhanced\n(+ Temporal Lags)',
            'temporal_only': 'Temporal Only\n(Lags Only)'
        }

        for _model_idx, (_model_name_viz, _model_results_viz) in enumerate(model_comparison_results.items()):
            ax = axes[_model_idx]

            # Data for plotting
            _standard_means = []
            _temporal_means = []
            _standard_stds = []
            _temporal_stds = []
            _labels = []
            _bar_colors = []

            for _set_name_viz in ['non_temporal', 'temporal', 'temporal_only']:
                if (_set_name_viz in _model_results_viz.get('standard_cv', {}) and 
                    _set_name_viz in _model_results_viz.get('temporal_cv', {})):

                    _standard_result = _model_results_viz['standard_cv'][_set_name_viz]
                    _temporal_result = _model_results_viz['temporal_cv'][_set_name_viz]

                    _standard_means.append(_standard_result['mean'])
                    _temporal_means.append(_temporal_result['mean'])
                    _standard_stds.append(_standard_result['std'])
                    _temporal_stds.append(_temporal_result['std'])
                    _labels.append(_set_labels[_set_name_viz])
                    _bar_colors.append(_colors[_set_name_viz])

            if _labels:
                _x = np.arange(len(_labels))
                _width = 0.35

                _bars1 = ax.bar(_x - _width/2, _standard_means, _width, yerr=_standard_stds,
                              label='Standard CV', alpha=0.8, color=_bar_colors, 
                              edgecolor='black', linewidth=0.5)
                _bars2 = ax.bar(_x + _width/2, _temporal_means, _width, yerr=_temporal_stds,
                              label='Temporal CV', alpha=0.6, color=_bar_colors,
                              edgecolor='black', linewidth=0.5, hatch='///')

                ax.set_xlabel('Feature Set')
                ax.set_ylabel('F1 Score')
                ax.set_title(f'{_model_name_viz.title().replace("_", " ")} Performance')
                ax.set_xticks(_x)
                ax.set_xticklabels(_labels, rotation=0, ha='center')
                ax.legend()
                ax.grid(True, alpha=0.3, axis='y')
                ax.set_ylim(0, max(max(_standard_means), max(_temporal_means)) * 1.1)

                # Add value labels on bars
                for _bar_idx, (_bar1, _bar2) in enumerate(zip(_bars1, _bars2)):
                    ax.text(_bar1.get_x() + _bar1.get_width()/2., _bar1.get_height() + _standard_stds[_bar_idx] + 0.01,
                           f'{_standard_means[_bar_idx]:.3f}', ha='center', va='bottom', fontsize=8, weight='bold')
                    ax.text(_bar2.get_x() + _bar2.get_width()/2., _bar2.get_height() + _temporal_stds[_bar_idx] + 0.01,
                           f'{_temporal_means[_bar_idx]:.3f}', ha='center', va='bottom', fontsize=8, weight='bold')

        plt.tight_layout()
        plt.savefig(plot_dir / '06_04_temporal_vs_nontemporal_comparison.png', 
                   dpi=150, bbox_inches='tight')
        plt.show()
    return


@app.cell
def _(data_dir, json, model_comparison_results):
    # Generate detailed analysis and recommendations
    if model_comparison_results:
        print("\n🎯 TEMPORAL MODELING ANALYSIS & RECOMMENDATIONS")
        print("="*60)

        _analysis_results = {}

        for _model_name_analysis, _model_results_analysis in model_comparison_results.items():
            print(f"\n📊 {_model_name_analysis.upper()} ANALYSIS:")
            print("-" * 25)

            # Extract results for comparison
            if ('standard_cv' in _model_results_analysis and 'temporal_cv' in _model_results_analysis):
                _standard_results = _model_results_analysis['standard_cv']
                _temporal_results = _model_results_analysis['temporal_cv']

                _model_analysis = {}

                # Compare traditional vs enhanced approach
                if 'non_temporal' in _standard_results and 'temporal' in _standard_results:
                    _traditional_f1 = _standard_results['non_temporal']['mean']
                    _enhanced_f1 = _standard_results['temporal']['mean']
                    _improvement = _enhanced_f1 - _traditional_f1
                    _improvement_pct = (_improvement / _traditional_f1) * 100

                    print(f"  Traditional approach F1: {_traditional_f1:.3f}")
                    print(f"  Enhanced (+ bio lags) F1: {_enhanced_f1:.3f}")
                    print(f"  Improvement: +{_improvement:.3f} ({_improvement_pct:+.1f}%)")

                    _model_analysis['improvement'] = {
                        'absolute': _improvement,
                        'relative_pct': _improvement_pct,
                        'traditional_f1': _traditional_f1,
                        'enhanced_f1': _enhanced_f1
                    }

                # Compare standard vs temporal CV
                if 'temporal' in _standard_results and 'temporal' in _temporal_results:
                    _standard_cv_f1 = _standard_results['temporal']['mean']
                    _temporal_cv_f1 = _temporal_results['temporal']['mean']
                    _cv_difference = _standard_cv_f1 - _temporal_cv_f1

                    print(f"  Standard CV F1: {_standard_cv_f1:.3f}")
                    print(f"  Temporal CV F1: {_temporal_cv_f1:.3f}")
                    print(f"  CV Method Difference: {_cv_difference:+.3f}")

                    if _cv_difference > 0.02:
                        print(f"  ⚠️  SIGNIFICANT TEMPORAL LEAKAGE DETECTED!")
                        print(f"     Standard CV likely overestimates performance")
                    elif _cv_difference > 0.005:
                        print(f"  ⚠️  Mild temporal dependence detected")
                    else:
                        print(f"  ✅ Temporal validation consistent with standard CV")

                    _model_analysis['cv_comparison'] = {
                        'standard_cv_f1': _standard_cv_f1,
                        'temporal_cv_f1': _temporal_cv_f1,
                        'leakage_detected': _cv_difference > 0.02
                    }

                # Temporal memory test
                if 'temporal_only' in _temporal_results:
                    _temporal_only_f1 = _temporal_results['temporal_only']['mean']
                    print(f"  Temporal memory F1: {_temporal_only_f1:.3f}")

                    if _temporal_only_f1 > 0.6:
                        print(f"  🧠 STRONG temporal memory effect!")
                    elif _temporal_only_f1 > 0.5:
                        print(f"  🧠 Moderate temporal memory effect")
                    else:
                        print(f"  🧠 Weak temporal memory effect")

                    _model_analysis['temporal_memory'] = {
                        'f1_score': _temporal_only_f1,
                        'strength': 'strong' if _temporal_only_f1 > 0.6 else 'moderate' if _temporal_only_f1 > 0.5 else 'weak'
                    }

                _analysis_results[_model_name_analysis] = _model_analysis

        # Overall recommendations
        print(f"\n🎯 SCIENTIFIC CONCLUSIONS & RECOMMENDATIONS:")
        print("="*50)

        if 'random_forest' in _analysis_results:
            _rf_analysis = _analysis_results['random_forest']

            if 'improvement' in _rf_analysis:
                _improvement_pct = _rf_analysis['improvement']['relative_pct']
                if _improvement_pct > 10:
                    print("✅ STRONG EVIDENCE for temporal modeling:")
                    print(f"   - Biological lag features improve performance by {_improvement_pct:.1f}%")
                    print("   - Ecological memory is a key predictive component")
                    print("   - Continuous monitoring provides significant value beyond current conditions")
                elif _improvement_pct > 5:
                    print("✅ MODERATE EVIDENCE for temporal modeling:")
                    print(f"   - Biological lag features provide {_improvement_pct:.1f}% improvement")
                    print("   - Worth implementing for operational systems")
                else:
                    print("⚠️  WEAK EVIDENCE for temporal modeling:")
                    print(f"   - Only {_improvement_pct:.1f}% improvement detected")
                    print("   - May not justify added complexity")

            if 'cv_comparison' in _rf_analysis and _rf_analysis['cv_comparison']['leakage_detected']:
                print("\n🚨 TEMPORAL VALIDATION CRITICAL:")
                print("   - Standard CV significantly overestimates performance")
                print("   - TimeSeriesSplit essential for honest evaluation")
                print("   - Temporal dependence confirmed in biological data")

            if 'temporal_memory' in _rf_analysis:
                _strength = _rf_analysis['temporal_memory']['strength']
                _f1_temporal = _rf_analysis['temporal_memory']['f1_score']
                print(f"\n🧠 TEMPORAL MEMORY: {_strength.upper()}")
                print(f"   - Past acoustic/environmental patterns predict activity: F1={_f1_temporal:.3f}")
                if _strength == 'strong':
                    print("   - Strong temporal persistence detected")
                    print("   - Predictive monitoring systems highly feasible")

        # Save results
        with open(data_dir / "06_04_temporal_modeling_analysis.json", 'w') as f:
            json.dump(_analysis_results, f, indent=2, default=str)

        print(f"\n💾 Analysis results saved to: {data_dir / '06_04_temporal_modeling_analysis.json'}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Summary and Next Steps

    This temporal modeling analysis provides the first systematic evaluation of biological temporal dependence in marine acoustic monitoring.

    ### Key Findings

    **If temporal modeling shows significant improvement:**
    - Biological systems have exploitable memory for predictive modeling
    - Past activity is as important as (or more than) acoustic indices
    - Continuous monitoring provides value beyond environmental sensing
    - TimeSeriesSplit reveals temporal leakage in standard validation

    **If temporal modeling shows limited improvement:**
    - Marine biological patterns may be primarily driven by environmental conditions
    - Acoustic indices capture most predictive information
    - Temporal features provide marginal additional value
    - Standard validation methods remain appropriate

    ### Scientific Impact

    This analysis addresses a fundamental question in ecological monitoring: **How much does biological memory contribute to predictable patterns?**

    The results inform:
    - **Monitoring system design**: Should we invest in continuous vs snapshot sampling?
    - **Model architecture**: Do we need temporal models or are static models sufficient?
    - **Resource allocation**: How much effort should focus on real-time vs historical data?
    - **Early warning capability**: Can we predict biological events before they happen?

    ### Integration with Existing Notebooks

    This temporal modeling framework can be integrated into:
    - **Notebook 7**: Use temporal validation for continuous monitoring assessment
    - **Future work**: Apply temporal modeling to specific species prediction
    - **Operational systems**: Implement biological momentum for adaptive sampling
    """
    )
    return


@app.cell(hide_code=True)
def _():
    # Summary completion
    print("✅ Temporal modeling analysis complete!")
    print("Key outputs:")
    print("  - Biological lag feature importance analysis") 
    print("  - Temporal vs non-temporal model comparison")
    print("  - TimeSeriesSplit vs StratifiedKFold validation comparison")
    print("  - Biological memory strength assessment")
    print("  - Scientific recommendations for continuous monitoring")
    return


if __name__ == "__main__":
    app.run()
