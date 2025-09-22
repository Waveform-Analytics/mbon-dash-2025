#!/usr/bin/env python3
"""
PHASE 5: SPECIES-SPECIFIC ANALYSIS (CORRECTED)
==============================================
Goal: Fix data leakage issues and test acoustic vs environmental features
      for individual species detection, where acoustic indices may be more valuable.

Critical fixes:
1. Remove biological context features (data leakage)  
2. Test species-specific models instead of just community-level
3. Proper comparison of acoustic vs environmental predictive power

This addresses the key questions:
- Do acoustic indices help predict specific species beyond environmental data?
- Which species benefit most from acoustic vs environmental features?
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, roc_auc_score, average_precision_score
from sklearn.feature_selection import mutual_info_classif

def load_datasets():
    """Load the temporal-enhanced dataset but remove data leakage features."""
    print("📂 Loading temporal dataset...")
    
    temporal_path = Path("output/temporal_features_dataset.csv") 
    if not temporal_path.exists():
        raise FileNotFoundError("Temporal features dataset not found. Run Phase 3 first.")
    
    df = pd.read_csv(temporal_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    print(f"   Loaded dataset: {df.shape}")
    
    # CRITICAL: Remove biological context features (data leakage)
    biological_leak_cols = [col for col in df.columns if any(x in col for x in ['recent_activity', 'activity_increasing'])]
    
    if biological_leak_cols:
        print(f"🚫 REMOVING DATA LEAKAGE: {len(biological_leak_cols)} biological context features")
        df = df.drop(columns=biological_leak_cols)
        print(f"   Clean dataset: {df.shape}")
    
    return df

def identify_species_and_features(df):
    """Identify species targets and feature groups without data leakage."""
    
    # Load selected acoustic features
    selected_path = Path("selected_acoustic_indices.csv")
    if selected_path.exists():
        selected_df = pd.read_csv(selected_path)
        top_acoustic = selected_df['acoustic_index'].tolist()
    else:
        print("⚠️ Using all acoustic features (selected indices not found)")
        acoustic_cols = [col for col in df.columns if not any(x in col for x in ['datetime', 'station', 'temp', 'depth', 'Hz', '_roll_', '_lag_', '_trend_', '_change_', 'hour_', 'dow_', 'month_'])]
        top_acoustic = [col for col in acoustic_cols if col not in ['total_fish_activity', 'any_activity', 'high_activity', 'num_active_species']]
    
    # Identify species columns (individual species detection targets)
    species_cols = ['Red drum', 'Bottlenose dolphin echolocation', 'Oyster toadfish grunt', 
                   'Atlantic croaker', 'Black drum', 'Bottlenose dolphin burst pulses',
                   'Bottlenose dolphin whistles', 'Oyster toadfish boat whistle', 
                   'Spotted seatrout', 'Silver perch', 'Vessel']
    
    available_species = [col for col in species_cols if col in df.columns]
    
    # Feature groups (NO biological context features)
    feature_groups = {
        'acoustic_raw': [col for col in top_acoustic if col in df.columns],
        'environmental_raw': [
            'Low (50-1200 Hz)', 'Water temp (°C)', 'Broadband (1-40000 Hz)', 
            'High (7000-40000 Hz)', 'Mid (1200-7000 Hz)', 'Water depth (m)'
        ],
        'acoustic_temporal': [col for col in df.columns if any(ac in col for ac in top_acoustic) 
                             and any(temp in col for temp in ['_roll_', '_lag_', '_trend_', '_change_'])],
        'environmental_temporal': [col for col in df.columns if 
                                  any(env in col for env in ['Low (50-1200 Hz)', 'Water temp (°C)', 'Broadband', 'High (7000-40000 Hz)', 'Water depth']) 
                                  and any(temp in col for temp in ['_roll_', '_lag_', '_trend_', '_change_'])],
        'temporal_context': [col for col in df.columns if any(x in col for x in ['hour_', 'dow_', 'month_'])],
        'metadata': ['datetime', 'station']
    }
    
    # Filter to existing columns
    for group_name, features in feature_groups.items():
        feature_groups[group_name] = [f for f in features if f in df.columns]
    
    print("📊 CORRECTED FEATURE GROUP BREAKDOWN:")
    for group, features in feature_groups.items():
        if features:
            print(f"   {group}: {len(features)}")
    
    print(f"\n🐟 SPECIES TARGETS IDENTIFIED: {len(available_species)}")
    for species in available_species:
        if species in df.columns:
            # Convert to numeric, handling any string values
            df[species] = pd.to_numeric(df[species], errors='coerce').fillna(0)
            count = (df[species] > 0).sum()
            total = len(df)
            print(f"   {species}: {count}/{total} ({count/total:.1%} detection rate)")
        else:
            print(f"   {species}: Not found in dataset")
    
    return available_species, feature_groups

def evaluate_species_specific(df, species_list, feature_groups):
    """Evaluate acoustic vs environmental features for each species."""
    
    # Dataset configurations (without biological leakage)
    configs = {
        'environmental_only': feature_groups['environmental_raw'],
        'acoustic_only': feature_groups['acoustic_raw'],
        'environmental_with_temporal': (feature_groups['environmental_raw'] + 
                                       feature_groups['environmental_temporal']),
        'acoustic_with_temporal': (feature_groups['acoustic_raw'] + 
                                  feature_groups['acoustic_temporal']),
        'combined_raw': (feature_groups['environmental_raw'] + 
                        feature_groups['acoustic_raw']),
        'combined_with_temporal': (feature_groups['environmental_raw'] + 
                                  feature_groups['acoustic_raw'] +
                                  feature_groups['environmental_temporal'] +
                                  feature_groups['acoustic_temporal']),
        'full_features': (feature_groups['environmental_raw'] + 
                         feature_groups['acoustic_raw'] +
                         feature_groups['environmental_temporal'] +
                         feature_groups['acoustic_temporal'] +
                         feature_groups['temporal_context'])
    }
    
    models = {
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    results = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    print(f"\n🎯 SPECIES-SPECIFIC EVALUATION")
    print("=" * 60)
    
    for species in species_list:
        if species not in df.columns:
            continue
            
        # Skip species with very low detection rates
        detection_rate = (df[species] > 0).mean()
        if detection_rate < 0.01:  # Less than 1%
            print(f"⏭️ Skipping {species}: detection rate too low ({detection_rate:.1%})")
            continue
        
        print(f"\n🐟 ANALYZING: {species}")
        print(f"   Detection rate: {detection_rate:.1%}")
        
        y = (df[species] > 0).astype(int)  # Binary presence/absence
        
        species_results = {}
        
        for config_name, features in configs.items():
            # Filter to available features
            available_features = [f for f in features if f in df.columns]
            if len(available_features) == 0:
                continue
            
            X = df[available_features].copy()
            X = X.fillna(X.mean())
            
            # Skip if insufficient positive samples
            if y.sum() < 20:
                continue
                
            config_results = {}
            
            for model_name, model in models.items():
                try:
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    
                    # Cross-validation F1 scores
                    cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1')
                    
                    # Single split for detailed metrics
                    X_train, X_test, y_train, y_test = train_test_split(
                        X_scaled, y, test_size=0.2, random_state=42, stratify=y)
                    
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    y_pred_proba = model.predict_proba(X_test)[:, 1]
                    
                    f1 = f1_score(y_test, y_pred)
                    auc = roc_auc_score(y_test, y_pred_proba)
                    ap = average_precision_score(y_test, y_pred_proba)
                    
                    config_results[model_name] = {
                        'cv_f1_mean': cv_scores.mean(),
                        'cv_f1_std': cv_scores.std(),
                        'test_f1': f1,
                        'test_auc': auc,
                        'test_ap': ap,
                        'n_features': len(available_features)
                    }
                    
                except Exception as e:
                    print(f"     ⚠️ {model_name} failed for {config_name}: {str(e)[:50]}...")
                    continue
            
            species_results[config_name] = config_results
        
        results[species] = species_results
        
        # Print best results for this species
        if species_results:
            best_f1 = 0
            best_config = ""
            for config, models_result in species_results.items():
                for model, metrics in models_result.items():
                    if metrics['test_f1'] > best_f1:
                        best_f1 = metrics['test_f1']
                        best_config = f"{config} + {model}"
            
            print(f"   🏆 Best: {best_config} (F1: {best_f1:.3f})")
    
    return results

def analyze_acoustic_vs_environmental_value(results):
    """Analyze where acoustic indices add value beyond environmental features."""
    
    print(f"\n🔍 ACOUSTIC vs ENVIRONMENTAL VALUE ANALYSIS")
    print("=" * 60)
    
    summary_data = []
    
    for species, species_results in results.items():
        species_summary = {'species': species}
        
        # Extract best performance for each approach
        env_best = 0
        acoustic_best = 0
        combined_best = 0
        
        for config, models_result in species_results.items():
            for model, metrics in models_result.items():
                f1 = metrics['test_f1']
                
                if 'environmental' in config and 'acoustic' not in config:
                    env_best = max(env_best, f1)
                elif 'acoustic' in config and 'environmental' not in config:
                    acoustic_best = max(acoustic_best, f1)
                elif 'combined' in config or 'full' in config:
                    combined_best = max(combined_best, f1)
        
        species_summary.update({
            'environmental_best': env_best,
            'acoustic_best': acoustic_best,
            'combined_best': combined_best,
            'acoustic_advantage': acoustic_best - env_best,
            'synergy_gain': combined_best - max(env_best, acoustic_best)
        })
        
        summary_data.append(species_summary)
    
    summary_df = pd.DataFrame(summary_data)
    
    print("\n📊 SPECIES-SPECIFIC PERFORMANCE COMPARISON:")
    print("-" * 100)
    print(f"{'Species':<30} {'Env Best':<10} {'Acoustic Best':<14} {'Combined Best':<14} {'Acoustic Gain':<14} {'Synergy':<10}")
    print("-" * 100)
    
    for _, row in summary_df.iterrows():
        species_short = row['species'][:28] + ".." if len(row['species']) > 30 else row['species']
        print(f"{species_short:<30} {row['environmental_best']:<10.3f} "
              f"{row['acoustic_best']:<14.3f} {row['combined_best']:<14.3f} "
              f"{row['acoustic_advantage']:+<14.3f} {row['synergy_gain']:+<10.3f}")
    
    # Summary insights
    meaningful_acoustic_gain = (summary_df['acoustic_advantage'] > 0.02).sum()
    meaningful_synergy = (summary_df['synergy_gain'] > 0.02).sum()
    
    print(f"\n💡 KEY INSIGHTS:")
    print(f"   Species with meaningful acoustic advantage (>0.02 F1): {meaningful_acoustic_gain}/{len(summary_df)}")
    print(f"   Species with meaningful synergy (>0.02 F1): {meaningful_synergy}/{len(summary_df)}")
    
    # Identify best candidates for acoustic monitoring
    acoustic_winners = summary_df[summary_df['acoustic_advantage'] > 0.02].sort_values('acoustic_advantage', ascending=False)
    if len(acoustic_winners) > 0:
        print(f"\n🎵 SPECIES THAT BENEFIT FROM ACOUSTIC INDICES:")
        for _, row in acoustic_winners.iterrows():
            print(f"   {row['species']}: +{row['acoustic_advantage']:.3f} F1 improvement")
    else:
        print(f"\n🌡️ ENVIRONMENTAL FEATURES SUFFICIENT: No species show meaningful acoustic advantage")
    
    return summary_df

def main():
    print("🔄 PHASE 5: CORRECTED SPECIES-SPECIFIC ANALYSIS")
    print("=" * 70)
    print("Goal: Test acoustic vs environmental value for individual species")
    print("Fixes: Remove data leakage, focus on species-specific detection")
    
    # Load corrected dataset
    df = load_datasets()
    
    # Identify species and clean feature groups
    species_list, feature_groups = identify_species_and_features(df)
    
    # Species-specific evaluation
    results = evaluate_species_specific(df, species_list, feature_groups)
    
    # Analyze acoustic vs environmental value
    summary_df = analyze_acoustic_vs_environmental_value(results)
    
    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save detailed results
    with open(output_dir / "phase5_species_specific_results.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save summary
    summary_df.to_csv(output_dir / "phase5_species_comparison.csv", index=False)
    
    # Save insights
    insights = {
        'creation_timestamp': datetime.now().isoformat(),
        'analysis_type': 'species_specific_corrected',
        'data_leakage_removed': True,
        'species_analyzed': len([s for s in species_list if s in results]),
        'key_findings': {
            'species_with_acoustic_advantage': int((summary_df['acoustic_advantage'] > 0.02).sum()),
            'species_with_synergy': int((summary_df['synergy_gain'] > 0.02).sum()),
            'best_acoustic_species': summary_df.loc[summary_df['acoustic_advantage'].idxmax()]['species'] if len(summary_df) > 0 else None,
            'max_acoustic_advantage': float(summary_df['acoustic_advantage'].max()) if len(summary_df) > 0 else 0
        },
        'recommendation': 'environmental_sufficient' if (summary_df['acoustic_advantage'] > 0.02).sum() == 0 else 'species_specific_acoustic_value'
    }
    
    with open(output_dir / "phase5_corrected_insights.json", 'w') as f:
        json.dump(insights, f, indent=2, default=str)
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"   📊 Species comparison: phase5_species_comparison.csv")
    print(f"   📋 Detailed results: phase5_species_specific_results.json")
    print(f"   💡 Insights: phase5_corrected_insights.json")
    
    print("\n🎉 PHASE 5 COMPLETE!")
    print("=" * 30)
    print("✅ Data leakage issues corrected")
    print("✅ Species-specific analysis completed")
    print("✅ Acoustic vs environmental value assessed")
    print("✅ Ready for final recommendations")
    
    return results, summary_df

if __name__ == "__main__":
    main()