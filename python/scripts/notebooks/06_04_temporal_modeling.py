import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Notebook 6.04: Temporal Community Pattern Detection

        **Purpose**: Compare temporal vs non-temporal modeling approaches for community pattern detection using biological lag features

        **Key Innovation**: This is the first analysis to systematically incorporate **biological temporal dependence** into marine acoustic monitoring models.

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

    if df_biological is not None:
        biological_feature_cols = [col for col in biological_cols if 'lag' in col or 'mean_' in col]
        biological_target_cols = ['total_fish_activity', 'any_activity', 'num_active_species']
    else:
        biological_feature_cols = []
        biological_target_cols = ['total_fish_activity', 'any_activity', 'num_active_species']

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
    index_cols,
    mutual_info_classif,
    pd,
):
    # Analyze biological lag features vs acoustic indices
    print("Analyzing biological lag features vs acoustic indices...")
    print("="*60)

    # Ensure we have the target variable
    if 'any_activity' in df_modeling.columns:
        target = 'any_activity'

        # Prepare feature groups for comparison
        acoustic_features = [col for col in index_cols if col in df_modeling.columns]
        biological_features = [col for col in biological_feature_cols if col in df_modeling.columns]

        # Create comparison dataset (drop rows with missing values)
        comparison_cols = acoustic_features + biological_features + [target]
        df_comparison = df_modeling[comparison_cols].dropna()

        print(f"Comparison dataset: {df_comparison.shape[0]:,} samples")
        print(f"Target distribution: {df_comparison[target].value_counts().to_dict()}")

        if len(df_comparison) > 0 and len(biological_features) > 0:
            # Calculate mutual information for each feature group
            X_acoustic = df_comparison[acoustic_features]
            X_biological = df_comparison[biological_features]
            y = df_comparison[target]

            # Mutual information analysis
            mi_acoustic = mutual_info_classif(X_acoustic, y, random_state=42)
            mi_biological = mutual_info_classif(X_biological, y, random_state=42)

            # Create feature importance comparison
            feature_importance = []

            # Add acoustic indices
            for i, feature in enumerate(acoustic_features):
                feature_importance.append({
                    'feature': feature,
                    'type': 'acoustic_index',
                    'mi_score': mi_acoustic[i]
                })

            # Add biological lag features
            for i, feature in enumerate(biological_features):
                feature_importance.append({
                    'feature': feature,
                    'type': 'biological_lag',
                    'mi_score': mi_biological[i]
                })

            # Convert to dataframe and sort
            importance_df = pd.DataFrame(feature_importance)
            importance_df = importance_df.sort_values('mi_score', ascending=False)

            print(f"\n🏆 TOP 10 MOST PREDICTIVE FEATURES:")
            print("-" * 50)
            for i, row in importance_df.head(10).iterrows():
                feature_type = "🎵 Acoustic" if row['type'] == 'acoustic_index' else "🕰️ Biological Lag"
                print(f"  {row.name+1:2d}. {feature_type:15} | {row['feature'][:35]:35} | MI: {row['mi_score']:.3f}")

            # Summary statistics
            acoustic_mi_stats = {
                'mean': mi_acoustic.mean(),
                'max': mi_acoustic.max(), 
                'top_5_mean': mi_acoustic[mi_acoustic.argsort()[-5:]].mean()
            }

            biological_mi_stats = {
                'mean': mi_biological.mean(),
                'max': mi_biological.max(),
                'top_5_mean': mi_biological[mi_biological.argsort()[-5:]].mean()
            }

            print(f"\n📊 FEATURE GROUP COMPARISON:")
            print("-" * 40)
            print(f"Acoustic indices     - Mean MI: {acoustic_mi_stats['mean']:.3f}, Max: {acoustic_mi_stats['max']:.3f}, Top-5: {acoustic_mi_stats['top_5_mean']:.3f}")
            print(f"Biological lag       - Mean MI: {biological_mi_stats['mean']:.3f}, Max: {biological_mi_stats['max']:.3f}, Top-5: {biological_mi_stats['top_5_mean']:.3f}")

            # Determine winner
            bio_advantage = biological_mi_stats['top_5_mean'] > acoustic_mi_stats['top_5_mean']
            winner = "🕰️ BIOLOGICAL LAG" if bio_advantage else "🎵 ACOUSTIC INDICES"
            advantage = abs(biological_mi_stats['top_5_mean'] - acoustic_mi_stats['top_5_mean'])

            print(f"\n🏆 PREDICTIVE POWER WINNER: {winner}")
            print(f"   Advantage: {advantage:.3f} MI units")

            feature_analysis_results = {
                'importance_df': importance_df,
                'acoustic_stats': acoustic_mi_stats,
                'biological_stats': biological_mi_stats,
                'biological_advantage': bio_advantage
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
    target = 'any_activity'

    if target in df_modeling.columns:
        # Define feature sets for comparison
        acoustic_features = [col for col in index_cols if col in df_modeling.columns]
        biological_lag_features = [col for col in biological_feature_cols if col in df_modeling.columns]
        env_lag_features = [col for col in env_feature_cols if col in df_modeling.columns] 
        basic_temporal = [col for col in temporal_cols if col in df_modeling.columns]

        # Feature set definitions
        feature_sets = {
            'non_temporal': {
                'features': acoustic_features + ['hour', 'month'] + [col for col in df_modeling.columns if col in ['Water temp (°C)', 'Water depth (m)']],
                'description': 'Traditional: Acoustic + Environmental + Basic Temporal',
                'color': 'steelblue'
            },
            'temporal': {
                'features': acoustic_features + biological_lag_features + env_lag_features + basic_temporal,
                'description': 'Enhanced: Traditional + Biological Lag Features', 
                'color': 'forestgreen'
            },
            'biological_only': {
                'features': biological_lag_features + ['hour', 'month'],
                'description': 'Biological Memory: Only Lag Features + Time',
                'color': 'coral'
            }
        }

        # Filter to available features
        for name, config in feature_sets.items():
            available_features = [f for f in config['features'] if f in df_modeling.columns]
            config['features'] = available_features
            print(f"{name:15}: {len(available_features):2d} features - {config['description']}")

        # Prepare modeling data
        all_features = list(set().union(*[config['features'] for config in feature_sets.values()]))
        modeling_data = df_modeling[all_features + [target, 'datetime', 'station']].dropna()

        print(f"\nModeling dataset: {modeling_data.shape[0]:,} samples after removing missing values")
        print(f"Target distribution: {modeling_data[target].value_counts().to_dict()}")

        # Cross-validation configurations
        cv_methods = {
            'standard_cv': StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            'temporal_cv': TimeSeriesSplit(n_splits=5)
        }

        # Model configurations
        models = {
            'logistic': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        }

        # Results storage
        model_comparison_results = {}

        print(f"\n🎯 RUNNING COMPREHENSIVE MODEL COMPARISON")
        print("="*50)

        for model_name, model in models.items():
            print(f"\n📊 {model_name.upper()} RESULTS:")
            print("-" * 30)

            model_results = {}

            for cv_name, cv_splitter in cv_methods.items():
                cv_results = {}

                for set_name, set_config in feature_sets.items():
                    if len(set_config['features']) > 0:
                        # Prepare data
                        X = modeling_data[set_config['features']]
                        y = modeling_data[target]

                        # Scale features
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)

                        # Cross-validation
                        cv_scores = cross_val_score(model, X_scaled, y, cv=cv_splitter, scoring='f1')

                        cv_results[set_name] = {
                            'scores': cv_scores,
                            'mean': cv_scores.mean(),
                            'std': cv_scores.std(),
                            'n_features': len(set_config['features'])
                        }

                        cv_type = "Standard CV" if cv_name == 'standard_cv' else "Temporal CV"
                        print(f"  {cv_type:12} | {set_config['description'][:35]:35} | F1: {cv_scores.mean():.3f}±{cv_scores.std():.3f}")

                model_results[cv_name] = cv_results

            model_comparison_results[model_name] = model_results

    else:
        print(f"❌ Target variable '{target}' not found in modeling data")
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
        colors = {
            'non_temporal': 'steelblue',
            'temporal': 'forestgreen', 
            'biological_only': 'coral'
        }

        set_labels = {
            'non_temporal': 'Traditional\n(Acoustic + Env)',
            'temporal': 'Enhanced\n(+ Bio Lags)',
            'biological_only': 'Bio Memory\n(Lags Only)'
        }

        for model_idx, (model_name, model_results) in enumerate(model_comparison_results.items()):
            ax = axes[model_idx]

            # Data for plotting
            standard_means = []
            temporal_means = []
            standard_stds = []
            temporal_stds = []
            labels = []
            bar_colors = []

            for set_name in ['non_temporal', 'temporal', 'biological_only']:
                if (set_name in model_results.get('standard_cv', {}) and 
                    set_name in model_results.get('temporal_cv', {})):

                    standard_result = model_results['standard_cv'][set_name]
                    temporal_result = model_results['temporal_cv'][set_name]

                    standard_means.append(standard_result['mean'])
                    temporal_means.append(temporal_result['mean'])
                    standard_stds.append(standard_result['std'])
                    temporal_stds.append(temporal_result['std'])
                    labels.append(set_labels[set_name])
                    bar_colors.append(colors[set_name])

            if labels:
                x = np.arange(len(labels))
                width = 0.35

                bars1 = ax.bar(x - width/2, standard_means, width, yerr=standard_stds,
                              label='Standard CV', alpha=0.8, color=bar_colors, 
                              edgecolor='black', linewidth=0.5)
                bars2 = ax.bar(x + width/2, temporal_means, width, yerr=temporal_stds,
                              label='Temporal CV', alpha=0.6, color=bar_colors,
                              edgecolor='black', linewidth=0.5, hatch='///')

                ax.set_xlabel('Feature Set')
                ax.set_ylabel('F1 Score')
                ax.set_title(f'{model_name.title().replace("_", " ")} Performance')
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=0, ha='center')
                ax.legend()
                ax.grid(True, alpha=0.3, axis='y')
                ax.set_ylim(0, max(max(standard_means), max(temporal_means)) * 1.1)

                # Add value labels on bars
                for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
                    ax.text(bar1.get_x() + bar1.get_width()/2., bar1.get_height() + standard_stds[i] + 0.01,
                           f'{standard_means[i]:.3f}', ha='center', va='bottom', fontsize=8, weight='bold')
                    ax.text(bar2.get_x() + bar2.get_width()/2., bar2.get_height() + temporal_stds[i] + 0.01,
                           f'{temporal_means[i]:.3f}', ha='center', va='bottom', fontsize=8, weight='bold')

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

        analysis_results = {}

        for model_name, model_results in model_comparison_results.items():
            print(f"\n📊 {model_name.upper()} ANALYSIS:")
            print("-" * 25)

            # Extract results for comparison
            if ('standard_cv' in model_results and 'temporal_cv' in model_results):
                standard_results = model_results['standard_cv']
                temporal_results = model_results['temporal_cv']

                model_analysis = {}

                # Compare traditional vs enhanced approach
                if 'non_temporal' in standard_results and 'temporal' in standard_results:
                    traditional_f1 = standard_results['non_temporal']['mean']
                    enhanced_f1 = standard_results['temporal']['mean']
                    improvement = enhanced_f1 - traditional_f1
                    improvement_pct = (improvement / traditional_f1) * 100

                    print(f"  Traditional approach F1: {traditional_f1:.3f}")
                    print(f"  Enhanced (+ bio lags) F1: {enhanced_f1:.3f}")
                    print(f"  Improvement: +{improvement:.3f} ({improvement_pct:+.1f}%)")

                    model_analysis['improvement'] = {
                        'absolute': improvement,
                        'relative_pct': improvement_pct,
                        'traditional_f1': traditional_f1,
                        'enhanced_f1': enhanced_f1
                    }

                # Compare standard vs temporal CV
                if 'temporal' in standard_results and 'temporal' in temporal_results:
                    standard_cv_f1 = standard_results['temporal']['mean']
                    temporal_cv_f1 = temporal_results['temporal']['mean']
                    cv_difference = standard_cv_f1 - temporal_cv_f1

                    print(f"  Standard CV F1: {standard_cv_f1:.3f}")
                    print(f"  Temporal CV F1: {temporal_cv_f1:.3f}")
                    print(f"  CV Method Difference: {cv_difference:+.3f}")

                    if cv_difference > 0.02:
                        print(f"  ⚠️  SIGNIFICANT TEMPORAL LEAKAGE DETECTED!")
                        print(f"     Standard CV likely overestimates performance")
                    elif cv_difference > 0.005:
                        print(f"  ⚠️  Mild temporal dependence detected")
                    else:
                        print(f"  ✅ Temporal validation consistent with standard CV")

                    model_analysis['cv_comparison'] = {
                        'standard_cv_f1': standard_cv_f1,
                        'temporal_cv_f1': temporal_cv_f1,
                        'leakage_detected': cv_difference > 0.02
                    }

                # Biological memory test
                if 'biological_only' in temporal_results:
                    bio_only_f1 = temporal_results['biological_only']['mean']
                    print(f"  Biological memory F1: {bio_only_f1:.3f}")

                    if bio_only_f1 > 0.6:
                        print(f"  🧠 STRONG biological memory effect!")
                    elif bio_only_f1 > 0.5:
                        print(f"  🧠 Moderate biological memory effect")
                    else:
                        print(f"  🧠 Weak biological memory effect")

                    model_analysis['biological_memory'] = {
                        'f1_score': bio_only_f1,
                        'strength': 'strong' if bio_only_f1 > 0.6 else 'moderate' if bio_only_f1 > 0.5 else 'weak'
                    }

                analysis_results[model_name] = model_analysis

        # Overall recommendations
        print(f"\n🎯 SCIENTIFIC CONCLUSIONS & RECOMMENDATIONS:")
        print("="*50)

        if 'random_forest' in analysis_results:
            rf_analysis = analysis_results['random_forest']

            if 'improvement' in rf_analysis:
                improvement_pct = rf_analysis['improvement']['relative_pct']
                if improvement_pct > 10:
                    print("✅ STRONG EVIDENCE for temporal modeling:")
                    print(f"   - Biological lag features improve performance by {improvement_pct:.1f}%")
                    print("   - Ecological memory is a key predictive component")
                    print("   - Continuous monitoring provides significant value beyond current conditions")
                elif improvement_pct > 5:
                    print("✅ MODERATE EVIDENCE for temporal modeling:")
                    print(f"   - Biological lag features provide {improvement_pct:.1f}% improvement")
                    print("   - Worth implementing for operational systems")
                else:
                    print("⚠️  WEAK EVIDENCE for temporal modeling:")
                    print(f"   - Only {improvement_pct:.1f}% improvement detected")
                    print("   - May not justify added complexity")

            if 'cv_comparison' in rf_analysis and rf_analysis['cv_comparison']['leakage_detected']:
                print("\n🚨 TEMPORAL VALIDATION CRITICAL:")
                print("   - Standard CV significantly overestimates performance")
                print("   - TimeSeriesSplit essential for honest evaluation")
                print("   - Temporal dependence confirmed in biological data")

            if 'biological_memory' in rf_analysis:
                strength = rf_analysis['biological_memory']['strength']
                f1_bio = rf_analysis['biological_memory']['f1_score']
                print(f"\n🧠 BIOLOGICAL MEMORY: {strength.upper()}")
                print(f"   - Past activity alone predicts current activity: F1={f1_bio:.3f}")
                if strength == 'strong':
                    print("   - Strong ecological persistence detected")
                    print("   - Early warning systems highly feasible")

        # Save results
        with open(data_dir / "06_04_temporal_modeling_analysis.json", 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)

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
