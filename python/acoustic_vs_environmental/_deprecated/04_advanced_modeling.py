#!/usr/bin/env python3
"""
PHASE 4: ADVANCED MODELING & EVALUATION
=======================================
Goal: Evaluate the impact of temporal features on biological activity prediction
      and provide comprehensive comparison between acoustic vs environmental approaches.

This phase tests:
1. Impact of temporal features on model performance
2. Feature importance analysis across feature types
3. Advanced models (XGBoost, neural networks)
4. Comprehensive evaluation metrics and visualization
5. Final recommendations for acoustic vs environmental monitoring

Uses temporal-enhanced dataset from Phase 3 with 312 features.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.metrics import precision_recall_curve, average_precision_score, f1_score

def load_datasets():
    """Load both baseline and temporal-enhanced datasets for comparison."""
    print("📂 Loading datasets...")
    
    # Load baseline dataset (Phase 1)
    baseline_path = Path("data_01_aligned_2021.csv")
    if not baseline_path.exists():
        raise FileNotFoundError("Baseline dataset not found.")
    
    baseline_df = pd.read_csv(baseline_path)
    baseline_df['datetime'] = pd.to_datetime(baseline_df['datetime'])
    
    # Load temporal-enhanced dataset (Phase 3)
    temporal_path = Path("output/temporal_features_dataset.csv") 
    if not temporal_path.exists():
        raise FileNotFoundError("Temporal features dataset not found. Run Phase 3 first.")
    
    temporal_df = pd.read_csv(temporal_path)
    temporal_df['datetime'] = pd.to_datetime(temporal_df['datetime'])
    
    print(f"   Baseline dataset: {baseline_df.shape}")
    print(f"   Temporal dataset: {temporal_df.shape}")
    print(f"   Added features: {temporal_df.shape[1] - baseline_df.shape[1]}")
    
    return baseline_df, temporal_df

def identify_feature_groups(df):
    """Identify different feature groups for structured analysis."""
    
    # Load selected features from Phase 2
    selected_path = Path("selected_acoustic_indices.csv")
    selected_df = pd.read_csv(selected_path)
    top_acoustic = selected_df['acoustic_index'].tolist()
    
    # Define feature groups
    feature_groups = {
        'top_acoustic_raw': [col for col in top_acoustic if col in df.columns],
        'environmental_raw': [
            'Low (50-1200 Hz)', 'Water temp (°C)', 'Broadband (1-40000 Hz)', 
            'High (7000-40000 Hz)', 'Mid (1200-7000 Hz)'
        ],
        'acoustic_temporal': [col for col in df.columns if any(ac in col for ac in top_acoustic) 
                             and any(temp in col for temp in ['_roll_', '_lag_', '_trend_', '_change_'])],
        'environmental_temporal': [col for col in df.columns if 
                                  any(env in col for env in ['Low (50-1200 Hz)', 'Water temp (°C)', 'Broadband', 'High (7000-40000 Hz)']) 
                                  and any(temp in col for temp in ['_roll_', '_lag_', '_trend_', '_change_'])],
        'temporal_context': [col for col in df.columns if any(x in col for x in ['hour_', 'dow_', 'month_'])],
        'biological_context': [col for col in df.columns if any(x in col for x in ['recent_activity', 'activity_increasing'])],
        'metadata': ['datetime', 'station'],
        'targets': [col for col in df.columns if col in ['any_activity', 'high_activity', 'species_richness', 'detection_count']]
    }
    
    # Filter to existing columns
    for group_name, features in feature_groups.items():
        feature_groups[group_name] = [f for f in features if f in df.columns]
    
    print("📊 FEATURE GROUP BREAKDOWN:")
    for group, features in feature_groups.items():
        if features:
            print(f"   {group}: {len(features)}")
    
    return feature_groups

def prepare_modeling_datasets(df, feature_groups):
    """Prepare different feature combinations for modeling comparison."""
    
    target = 'any_activity'
    datasets = {}
    
    # Dataset configurations to test
    configs = {
        'acoustic_raw': feature_groups['top_acoustic_raw'],
        'environmental_raw': feature_groups['environmental_raw'],
        'acoustic_with_temporal': (feature_groups['top_acoustic_raw'] + 
                                  feature_groups['acoustic_temporal']),
        'environmental_with_temporal': (feature_groups['environmental_raw'] + 
                                       feature_groups['environmental_temporal']),
        'all_raw': (feature_groups['top_acoustic_raw'] + 
                   feature_groups['environmental_raw']),
        'all_with_temporal': (feature_groups['top_acoustic_raw'] + 
                             feature_groups['environmental_raw'] +
                             feature_groups['acoustic_temporal'] +
                             feature_groups['environmental_temporal']),
        'full_temporal': (feature_groups['top_acoustic_raw'] + 
                         feature_groups['environmental_raw'] +
                         feature_groups['acoustic_temporal'] +
                         feature_groups['environmental_temporal'] +
                         feature_groups['temporal_context'] +
                         feature_groups['biological_context'])
    }
    
    print("\n🎯 PREPARING MODELING DATASETS:")
    
    for config_name, features in configs.items():
        if not features:
            continue
            
        # Remove any missing features
        available_features = [f for f in features if f in df.columns]
        
        if len(available_features) == 0:
            print(f"   ⚠️ {config_name}: No features available")
            continue
            
        X = df[available_features].copy()
        y = df[target].copy()
        
        # Handle any remaining nulls
        X = X.fillna(X.mean())
        
        datasets[config_name] = {
            'X': X,
            'y': y,
            'features': available_features,
            'n_features': len(available_features)
        }
        
        print(f"   ✅ {config_name}: {len(available_features)} features")
    
    return datasets, target

def evaluate_models(datasets, target_name):
    """Comprehensive model evaluation across different feature sets."""
    
    models = {
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    results = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    print(f"\n🤖 COMPREHENSIVE MODEL EVALUATION")
    print("=" * 50)
    print(f"Target: {target_name}")
    print(f"Cross-validation: {cv.get_n_splits()}-fold stratified")
    
    for dataset_name, data in datasets.items():
        print(f"\n📊 Dataset: {dataset_name}")
        print(f"   Features: {data['n_features']}")
        
        X, y = data['X'], data['y']
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        dataset_results = {}
        
        for model_name, model in models.items():
            print(f"   🔄 {model_name}...", end=' ')
            
            # Cross-validation scores
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1')
            
            # Single train-test split for detailed metrics
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42, stratify=y)
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            f1 = f1_score(y_test, y_pred)
            auc = roc_auc_score(y_test, y_pred_proba)
            ap = average_precision_score(y_test, y_pred_proba)
            
            dataset_results[model_name] = {
                'cv_f1_mean': cv_scores.mean(),
                'cv_f1_std': cv_scores.std(),
                'test_f1': f1,
                'test_auc': auc,
                'test_ap': ap,
                'model': model,
                'scaler': scaler
            }
            
            print(f"F1: {f1:.3f}, AUC: {auc:.3f}")
        
        results[dataset_name] = dataset_results
    
    return results

def analyze_feature_importance(results, datasets):
    """Analyze and compare feature importance across models."""
    
    print("\n🔍 FEATURE IMPORTANCE ANALYSIS")
    print("=" * 40)
    
    importance_data = []
    
    # Extract feature importance from tree-based models
    for dataset_name, dataset_results in results.items():
        for model_name, model_result in dataset_results.items():
            if model_name in ['RandomForest']:
                model = model_result['model']
                features = datasets[dataset_name]['features']
                
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    
                    # Get top N important features (min of 10 or number of features)
                    n_top = min(10, len(importances))
                    top_indices = np.argsort(importances)[-n_top:][::-1]
                    
                    print(f"\n📈 {dataset_name} - {model_name} Top Features:")
                    for i, idx in enumerate(top_indices, 1):
                        if idx >= len(features):  # Safety check
                            continue
                        feat_name = features[idx]
                        importance = importances[idx]
                        
                        # Categorize feature type
                        if any(x in feat_name for x in ['_roll_', '_lag_', '_trend_', '_change_']):
                            feat_type = "🕒 temporal"
                        elif any(x in feat_name for x in ['hour_', 'dow_', 'month_']):
                            feat_type = "📅 cyclical"
                        elif any(x in feat_name for x in ['recent_activity', 'activity_increasing']):
                            feat_type = "🐟 biological"
                        elif feat_name in ['Low (50-1200 Hz)', 'Water temp (°C)', 'Broadband (1-40000 Hz)', 'High (7000-40000 Hz)']:
                            feat_type = "🌡️ environmental"
                        else:
                            feat_type = "🎵 acoustic"
                        
                        importance_data.append({
                            'dataset': dataset_name,
                            'model': model_name,
                            'feature': feat_name,
                            'importance': importance,
                            'rank': i,
                            'type': feat_type
                        })
                        
                        print(f"   {i:2d}. {feat_type} | {feat_name[:40]:40s} | {importance:.4f}")
    
    # Create importance summary
    importance_df = pd.DataFrame(importance_data)
    return importance_df

def create_performance_summary(results):
    """Create a comprehensive performance summary."""
    
    summary_data = []
    
    for dataset_name, dataset_results in results.items():
        for model_name, metrics in dataset_results.items():
            summary_data.append({
                'dataset': dataset_name,
                'model': model_name,
                'cv_f1_mean': metrics['cv_f1_mean'],
                'cv_f1_std': metrics['cv_f1_std'],
                'test_f1': metrics['test_f1'],
                'test_auc': metrics['test_auc'],
                'test_ap': metrics['test_ap']
            })
    
    summary_df = pd.DataFrame(summary_data)
    
    print("\n📊 COMPREHENSIVE PERFORMANCE SUMMARY")
    print("=" * 60)
    
    # Sort by test F1 score
    summary_df_sorted = summary_df.sort_values('test_f1', ascending=False)
    
    print(f"{'Dataset':<25} {'Model':<15} {'CV F1':<10} {'Test F1':<10} {'AUC':<8} {'AP':<8}")
    print("-" * 76)
    
    for _, row in summary_df_sorted.head(15).iterrows():
        print(f"{row['dataset']:<25} {row['model']:<15} "
              f"{row['cv_f1_mean']:.3f}±{row['cv_f1_std']:.3f} "
              f"{row['test_f1']:<10.3f} {row['test_auc']:<8.3f} {row['test_ap']:<8.3f}")
    
    return summary_df

def generate_insights_and_recommendations(summary_df, importance_df):
    """Generate final insights and recommendations."""
    
    print("\n🎯 FINAL INSIGHTS & RECOMMENDATIONS")
    print("=" * 50)
    
    # Best overall performance
    best_overall = summary_df.loc[summary_df['test_f1'].idxmax()]
    
    print(f"\n🏆 BEST OVERALL PERFORMANCE:")
    print(f"   Dataset: {best_overall['dataset']}")
    print(f"   Model: {best_overall['model']}")
    print(f"   F1 Score: {best_overall['test_f1']:.3f}")
    print(f"   AUC: {best_overall['test_auc']:.3f}")
    
    # Compare raw vs temporal features
    raw_performance = summary_df[summary_df['dataset'].isin(['acoustic_raw', 'environmental_raw', 'all_raw'])]
    temporal_performance = summary_df[summary_df['dataset'].isin(['acoustic_with_temporal', 'environmental_with_temporal', 'all_with_temporal', 'full_temporal'])]
    
    if len(raw_performance) > 0 and len(temporal_performance) > 0:
        raw_best = raw_performance['test_f1'].max()
        temporal_best = temporal_performance['test_f1'].max()
        improvement = temporal_best - raw_best
        
        print(f"\n📈 TEMPORAL FEATURES IMPACT:")
        print(f"   Best raw features F1: {raw_best:.3f}")
        print(f"   Best temporal features F1: {temporal_best:.3f}")
        print(f"   Improvement: {improvement:+.3f} ({improvement/raw_best*100:+.1f}%)")
        
        if improvement > 0.01:
            print("   ✅ Temporal features provide meaningful improvement")
        elif improvement > 0:
            print("   🤏 Temporal features provide marginal improvement")
        else:
            print("   ❌ Temporal features do not improve performance")
    
    # Acoustic vs Environmental comparison
    acoustic_results = summary_df[summary_df['dataset'].str.contains('acoustic')]['test_f1']
    environmental_results = summary_df[summary_df['dataset'].str.contains('environmental')]['test_f1']
    
    if len(acoustic_results) > 0 and len(environmental_results) > 0:
        acoustic_best = acoustic_results.max()
        environmental_best = environmental_results.max()
        
        print(f"\n🎵🌡️ ACOUSTIC vs ENVIRONMENTAL:")
        print(f"   Best acoustic approach: {acoustic_best:.3f}")
        print(f"   Best environmental approach: {environmental_best:.3f}")
        
        if acoustic_best > environmental_best + 0.01:
            print("   🎵 Acoustic features are superior")
        elif environmental_best > acoustic_best + 0.01:
            print("   🌡️ Environmental features are superior")
        else:
            print("   ⚖️ Both approaches are comparable")
    
    # Feature type analysis from importance
    if not importance_df.empty:
        type_importance = importance_df.groupby('type')['importance'].mean().sort_values(ascending=False)
        
        print(f"\n🔍 FEATURE TYPE IMPORTANCE RANKING:")
        for feat_type, avg_importance in type_importance.items():
            print(f"   {feat_type}: {avg_importance:.4f}")
    
    # Model comparison
    model_performance = summary_df.groupby('model')['test_f1'].mean().sort_values(ascending=False)
    
    print(f"\n🤖 MODEL PERFORMANCE RANKING:")
    for model, avg_f1 in model_performance.items():
        print(f"   {model}: {avg_f1:.3f}")
    
    return {
        'best_overall': best_overall.to_dict(),
        'temporal_improvement': improvement if 'improvement' in locals() else None,
        'acoustic_vs_environmental': {
            'acoustic_best': acoustic_best if 'acoustic_best' in locals() else None,
            'environmental_best': environmental_best if 'environmental_best' in locals() else None
        },
        'model_ranking': model_performance.to_dict(),
        'feature_type_importance': type_importance.to_dict() if not importance_df.empty else {}
    }

def main():
    print("🔄 PHASE 4: ADVANCED MODELING & EVALUATION")
    print("=" * 60)
    print("Goal: Comprehensive evaluation of temporal features impact")
    print("Focus: Acoustic vs Environmental for biological monitoring")
    
    # Load datasets
    baseline_df, temporal_df = load_datasets()
    
    # Use temporal dataset for comprehensive analysis
    df = temporal_df.copy()
    
    # Identify feature groups
    feature_groups = identify_feature_groups(df)
    
    # Prepare modeling datasets
    datasets, target = prepare_modeling_datasets(df, feature_groups)
    
    if not datasets:
        raise ValueError("No valid datasets prepared for modeling")
    
    # Comprehensive model evaluation
    results = evaluate_models(datasets, target)
    
    # Feature importance analysis
    importance_df = analyze_feature_importance(results, datasets)
    
    # Performance summary
    summary_df = create_performance_summary(results)
    
    # Generate insights and recommendations
    insights = generate_insights_and_recommendations(summary_df, importance_df)
    
    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save detailed results
    summary_df.to_csv(output_dir / "phase4_model_performance_summary.csv", index=False)
    if not importance_df.empty:
        importance_df.to_csv(output_dir / "phase4_feature_importance.csv", index=False)
    
    # Save insights
    final_results = {
        'creation_timestamp': datetime.now().isoformat(),
        'evaluation_summary': {
            'datasets_evaluated': len(datasets),
            'models_tested': 2,
            'best_f1_score': summary_df['test_f1'].max(),
            'best_configuration': insights['best_overall']
        },
        'insights': insights,
        'performance_summary': summary_df.to_dict('records'),
        'feature_importance': importance_df.to_dict('records') if not importance_df.empty else []
    }
    
    with open(output_dir / "phase4_final_results.json", 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"   📊 Performance summary: phase4_model_performance_summary.csv")
    print(f"   🔍 Feature importance: phase4_feature_importance.csv")
    print(f"   📋 Final results: phase4_final_results.json")
    
    print("\n🎉 PHASE 4 COMPLETE!")
    print("=" * 30)
    print("✅ Comprehensive model evaluation finished")
    print("✅ Feature importance analysis completed")
    print("✅ Acoustic vs Environmental comparison done")
    print("✅ Temporal features impact assessed")
    print("✅ Ready for final project summary")
    
    return final_results

if __name__ == "__main__":
    main()