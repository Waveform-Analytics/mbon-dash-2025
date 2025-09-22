#!/usr/bin/env python3
"""
Analyze whether acoustic indices provide value beyond environmental variables
for predicting biological activity.

Key question: Are acoustic indices helping predict bio activity, or is it 
mostly environmental variables doing the work?
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_classif
import warnings
warnings.filterwarnings('ignore')

def main():
    # Load data
    data_dir = Path('../data')
    
    print("🔍 ACOUSTIC vs ENVIRONMENTAL ANALYSIS")
    print("="*50)
    print("Question: Do acoustic indices help predict biological activity")
    print("beyond what environmental variables already tell us?")
    print()
    
    # Load the processed data from notebook 2
    try:
        indices_df = pd.read_parquet(data_dir / 'processed' / '02_acoustic_indices_aligned_2021.parquet')
        bio_df = pd.read_parquet(data_dir / 'processed' / '02_biological_activity_features_2021.parquet')
        env_df = pd.read_parquet(data_dir / 'processed' / '02_environmental_aligned_2021.parquet')
        temporal_df = pd.read_parquet(data_dir / 'processed' / '02_temporal_features_2021.parquet')
        
        print(f"✓ Loaded enhanced datasets")
        print(f"  Indices: {indices_df.shape}")
        print(f"  Biological: {bio_df.shape}")
        print(f"  Environmental: {env_df.shape}")
        print(f"  Temporal: {temporal_df.shape}")
        
    except FileNotFoundError as e:
        print(f"❌ Could not load enhanced datasets: {e}")
        return
    
    # Merge data
    merged = indices_df.copy()
    merged = merged.merge(bio_df[['total_fish_activity', 'any_activity']], 
                         left_index=True, right_index=True, how='left')
    merged = merged.merge(env_df, left_index=True, right_index=True, how='left')
    merged = merged.merge(temporal_df, left_index=True, right_index=True, how='left')
    
    # Clean data
    merged = merged.dropna()
    target = 'any_activity'
    
    print(f"\n📊 DATASET OVERVIEW")
    print(f"Final dataset shape: {merged.shape}")
    print(f"Target '{target}' distribution: {merged[target].value_counts().to_dict()}")
    
    # Define feature groups based on actual column names
    # Key acoustic indices from the literature
    acoustic_indices = [col for col in merged.columns if col in [
        'ACI', 'ADI', 'AEI', 'BI', 'ENRf', 'NDSI', 'AnthroEnergy', 'BioEnergy',
        'H_Renyi', 'H_Shannon', 'RAOQ', 'AGI'
    ]]
    
    # Environmental base features (current conditions)
    environmental_base = [col for col in merged.columns if col in [
        'Water temp (°C)', 'Water depth (m)', 'Broadband (1-40000 Hz)', 
        'Low (50-1200 Hz)', 'High (7000-40000 Hz)'
    ]]
    
    # Environmental temporal lags and moving averages
    environmental_temporal = [col for col in merged.columns 
                            if ('lag' in col or 'mean' in col or 'change' in col) and 
                               any(base in col for base in ['temp', 'depth', 'spl', 'broadband'])]
    
    # Temporal cyclical features (convert categorical to dummy variables later)
    temporal_cyclical = [col for col in merged.columns if col in [
        'hour', 'day_of_year', 'month', 'weekday', 'week_of_year',
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos'
    ]]
    
    # Handle categorical variables by creating dummy variables
    categorical_features = []
    if 'season' in merged.columns:
        season_dummies = pd.get_dummies(merged['season'], prefix='season')
        merged = pd.concat([merged, season_dummies], axis=1)
        categorical_features.extend(season_dummies.columns.tolist())
    
    if 'time_period' in merged.columns:
        time_period_dummies = pd.get_dummies(merged['time_period'], prefix='time_period')
        merged = pd.concat([merged, time_period_dummies], axis=1)
        categorical_features.extend(time_period_dummies.columns.tolist())
    
    if 'station' in merged.columns:
        station_dummies = pd.get_dummies(merged['station'], prefix='station')
        merged = pd.concat([merged, station_dummies], axis=1)
        categorical_features.extend(station_dummies.columns.tolist())
    
    print(f"\n🎯 FEATURE GROUP SIZES:")
    print(f"  Acoustic indices: {len(acoustic_indices)} features")
    print(f"  Environmental (base): {len(environmental_base)} features")
    print(f"  Environmental (temporal): {len(environmental_temporal)} features")
    print(f"  Temporal (cyclical): {len(temporal_cyclical)} features")
    print(f"  Categorical (dummies): {len(categorical_features)} features")
    
    print(f"\n📋 ACTUAL FEATURES FOUND:")
    if acoustic_indices:
        print(f"  Acoustic: {acoustic_indices}")
    if environmental_base:
        print(f"  Env base: {environmental_base}")
    if environmental_temporal:
        print(f"  Env temporal: {environmental_temporal[:5]}{'...' if len(environmental_temporal) > 5 else ''}")
    if categorical_features:
        print(f"  Categorical: {categorical_features}")
    
    # Feature importance analysis
    print(f"\n🔍 MUTUAL INFORMATION ANALYSIS")
    print("="*40)
    
    all_features = acoustic_indices + environmental_base + environmental_temporal + temporal_cyclical + categorical_features
    X = merged[all_features]
    y = merged[target]
    
    # Calculate mutual information
    mi_scores = mutual_info_classif(X, y, random_state=42)
    mi_df = pd.DataFrame({
        'feature': all_features,
        'mi_score': mi_scores,
        'group': (['acoustic'] * len(acoustic_indices) + 
                 ['env_base'] * len(environmental_base) +
                 ['env_temporal'] * len(environmental_temporal) +
                 ['temporal'] * len(temporal_cyclical) +
                 ['categorical'] * len(categorical_features))
    }).sort_values('mi_score', ascending=False)
    
    print("🏆 TOP 15 MOST PREDICTIVE FEATURES:")
    print("-" * 50)
    for i, (_, row) in enumerate(mi_df.head(15).iterrows(), 1):
        group_emoji = {'acoustic': '🎵', 'env_base': '🌡️', 'env_temporal': '🕰️', 'temporal': '⏰', 'categorical': '📅'}
        print(f"{i:3d}. {group_emoji.get(row['group'], '❓')} {row['group']:12} | {row['feature']:25} | MI: {row['mi_score']:.3f}")
    
    # Group-level analysis
    print(f"\n📊 GROUP-LEVEL PREDICTIVE POWER:")
    print("-" * 40)
    group_stats = mi_df.groupby('group')['mi_score'].agg(['count', 'mean', 'max', 'sum']).round(3)
    group_stats['top5_mean'] = mi_df.groupby('group').head(5).groupby('group')['mi_score'].mean().round(3)
    
    for group, stats in group_stats.iterrows():
        group_emoji = {'acoustic': '🎵', 'env_base': '🌡️', 'env_temporal': '🕰️', 'temporal': '⏰', 'categorical': '📅'}
        print(f"{group_emoji.get(group, '❓')} {group:12} | Features: {int(stats['count']):2d} | Mean: {stats['mean']:.3f} | Max: {stats['max']:.3f} | Top5: {stats['top5_mean']:.3f}")
    
    # Model comparison: Isolate acoustic vs environmental contribution
    print(f"\n🤖 MODEL PERFORMANCE COMPARISON")
    print("="*45)
    
    models = {
        'Logistic': LogisticRegression(random_state=42, max_iter=1000),
        'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    }
    
    feature_sets = {
        'acoustic_only': {
            'features': acoustic_indices,
            'description': 'Acoustic Indices Only'
        },
        'environmental_only': {
            'features': environmental_base + environmental_temporal + temporal_cyclical + categorical_features,
            'description': 'Environmental + Temporal Only'
        },
        'env_base_only': {
            'features': environmental_base + temporal_cyclical + categorical_features,
            'description': 'Basic Environmental + Temporal'
        },
        'combined': {
            'features': acoustic_indices + environmental_base + environmental_temporal + temporal_cyclical + categorical_features,
            'description': 'All Features Combined'
        }
    }
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    
    for model_name, model in models.items():
        print(f"\n📈 {model_name.upper()} RESULTS:")
        print("-" * 30)
        
        model_results = {}
        
        for set_name, set_config in feature_sets.items():
            if len(set_config['features']) > 0:
                X_subset = merged[set_config['features']]
                
                # Scale features
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_subset)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1')
                
                model_results[set_name] = {
                    'mean_f1': cv_scores.mean(),
                    'std_f1': cv_scores.std(),
                    'n_features': len(set_config['features'])
                }
                
                print(f"  {set_config['description']:28} | F1: {cv_scores.mean():.3f}±{cv_scores.std():.3f} | Features: {len(set_config['features']):2d}")
        
        results[model_name] = model_results
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print("="*30)
    
    # Calculate acoustic contribution
    for model_name in models.keys():
        if all(key in results[model_name] for key in ['acoustic_only', 'environmental_only', 'combined']):
            acoustic_f1 = results[model_name]['acoustic_only']['mean_f1']
            env_f1 = results[model_name]['environmental_only']['mean_f1']
            combined_f1 = results[model_name]['combined']['mean_f1']
            
            acoustic_vs_env = acoustic_f1 - env_f1
            synergy = combined_f1 - max(acoustic_f1, env_f1)
            
            print(f"\n🤖 {model_name}:")
            print(f"  Acoustic only:      F1 = {acoustic_f1:.3f}")
            print(f"  Environmental only: F1 = {env_f1:.3f}")
            print(f"  Combined:          F1 = {combined_f1:.3f}")
            print(f"  Acoustic advantage: {acoustic_vs_env:+.3f}")
            print(f"  Synergy bonus:     {synergy:+.3f}")
            
            if acoustic_f1 > env_f1:
                print(f"  🏆 ACOUSTIC indices are MORE predictive!")
            elif env_f1 > acoustic_f1:
                print(f"  🌡️  ENVIRONMENTAL features are MORE predictive!")
            else:
                print(f"  🤝 Equal predictive power")
    
    # Final verdict
    print(f"\n📋 FINAL VERDICT:")
    print("-" * 20)
    
    # Check if acoustic indices add meaningful value
    best_env_only = max([results[model]['environmental_only']['mean_f1'] 
                        for model in results.keys()])
    best_combined = max([results[model]['combined']['mean_f1'] 
                        for model in results.keys()])
    
    improvement = best_combined - best_env_only
    improvement_pct = (improvement / best_env_only) * 100
    
    print(f"Best environmental-only F1:    {best_env_only:.3f}")
    print(f"Best combined F1:             {best_combined:.3f}")
    print(f"Improvement from acoustics:    {improvement:+.3f} ({improvement_pct:+.1f}%)")
    
    # Top acoustic features vs top environmental
    top_acoustic_mi = mi_df[mi_df['group'] == 'acoustic']['mi_score'].max()
    top_env_mi = mi_df[mi_df['group'].isin(['env_base', 'env_temporal'])]['mi_score'].max()
    
    print(f"\nTop acoustic feature MI:       {top_acoustic_mi:.3f}")
    print(f"Top environmental feature MI:  {top_env_mi:.3f}")
    
    if improvement > 0.01:  # 1% improvement threshold
        print(f"\n✅ ACOUSTIC INDICES ARE VALUABLE!")
        print(f"   They provide {improvement_pct:.1f}% improvement beyond environmental data")
    else:
        print(f"\n⚠️  ACOUSTIC INDICES PROVIDE LIMITED VALUE")
        print(f"   Environmental features dominate prediction")
        
        if top_acoustic_mi > 0.05:
            print(f"   However, some acoustic features show individual promise (MI={top_acoustic_mi:.3f})")

if __name__ == "__main__":
    main()