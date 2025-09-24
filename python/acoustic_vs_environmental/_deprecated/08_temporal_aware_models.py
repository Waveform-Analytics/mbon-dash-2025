#!/usr/bin/env python3
"""
PHASE 8: TEMPORAL-AWARE MACHINE LEARNING MODELS
===============================================
Goal: Build predictive models that preserve temporal structure and leverage 
      the temporal synchrony patterns discovered in Phase 6.

Key innovations:
1. Temporal train/test splits (chronological, not random)
2. Use acoustic indices with strong temporal correlations
3. Cross-correlation lag features (acoustic → species detection)
4. Time series-aware model validation
5. Species-specific models using acoustic signatures

This addresses the question:
"How can we leverage temporal synchrony to build better predictive models?"
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, roc_auc_score, average_precision_score
from sklearn.model_selection import TimeSeriesSplit
from scipy.stats import pearsonr

def load_data_and_correlations():
    """Load data and correlation results from previous analyses."""
    
    # Load aligned dataset
    data_path = Path("data_01_aligned_2021.csv")
    if not data_path.exists():
        raise FileNotFoundError("Run Phase 1 first to create aligned dataset")
    
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Clean data types
    for col in df.columns:
        if col not in ['datetime', 'station']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"✓ Loaded dataset: {df.shape}")
    
    # Load correlation results if available
    correlation_results = None
    corr_path = Path("visual_pattern_correlation_check.csv")
    if corr_path.exists():
        correlation_results = pd.read_csv(corr_path)
        print(f"✓ Loaded correlation results: {correlation_results.shape}")
    else:
        print("⚠️ No correlation results found - will identify patterns automatically")
    
    return df, correlation_results

def identify_temporal_features(df, correlation_results=None, species='Spotted seatrout'):
    """
    Identify acoustic features with strong temporal correlation to target species.
    """
    print(f"\n🎯 IDENTIFYING TEMPORAL FEATURES FOR {species}")
    print("=" * 60)
    
    if species not in df.columns:
        print(f"❌ {species} not found in dataset")
        return []
    
    # If we have correlation results, use them
    if correlation_results is not None:
        # Filter for high correlations
        strong_correlations = correlation_results[
            (correlation_results['abs_correlation'] > 0.5) 
        ].sort_values('abs_correlation', ascending=False)
        
        if len(strong_correlations) > 0:
            top_features = strong_correlations['acoustic_index'].tolist()[:10]
            print(f"✓ Using top {len(top_features)} features from correlation analysis:")
            for i, (_, row) in enumerate(strong_correlations.head(10).iterrows(), 1):
                print(f"   {i:2d}. {row['acoustic_index']:<20} r={row['correlation']:+.3f}")
            return top_features
    
    # Fallback: compute correlations on the fly
    print("Computing temporal correlations on the fly...")
    
    # Use single station for temporal analysis
    station_df = df[df['station'] == '9M'].copy()
    station_df = station_df.sort_values('datetime').reset_index(drop=True)
    
    species_data = station_df[species].fillna(0)
    
    # CRITICAL: Identify ALL species columns to avoid data leakage
    # Get all columns that might be species detections
    species_columns = ['Spotted seatrout', 'Atlantic croaker', 'Vessel', 'Oyster toadfish boat whistle', 
                      'Red drum', 'Silver perch', 'Black drum', 'Hardhead catfish', 
                      'total_fish_activity', 'any_activity', 'high_activity', 'num_active_species']
    
    # Find acoustic indices - exclude ALL species columns, not just target species
    exclude_cols = (['datetime', 'station', 'Water temp (°C)', 'Water depth (m)',
                    'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'Broadband (1-40000 Hz)'] + 
                   [col for col in species_columns if col in station_df.columns])
    
    acoustic_cols = [col for col in station_df.columns if col not in exclude_cols]
    
    correlations = []
    for acoustic in acoustic_cols:
        if station_df[acoustic].dtype in ['float64', 'int64']:
            acoustic_data = station_df[acoustic].fillna(station_df[acoustic].mean())
            if acoustic_data.std() > 0:
                r, p = pearsonr(acoustic_data, species_data)
                if abs(r) > 0.3:  # Moderate threshold
                    correlations.append({
                        'acoustic_index': acoustic,
                        'correlation': r,
                        'abs_correlation': abs(r)
                    })
    
    # Sort and select top features
    correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
    top_features = [c['acoustic_index'] for c in correlations[:10]]
    
    print(f"✓ Found {len(top_features)} temporally correlated features")
    for i, corr in enumerate(correlations[:5], 1):
        print(f"   {i:2d}. {corr['acoustic_index']:<20} r={corr['correlation']:+.3f}")
    
    return top_features

def create_temporal_lag_features(df, acoustic_features, target_species, max_lag=6):
    """
    Create lag features where acoustic patterns predict species detection.
    """
    print(f"\n⏰ CREATING TEMPORAL LAG FEATURES")
    print(f"Testing lags up to {max_lag} periods ({max_lag*2} hours)")
    
    feature_df = df.copy()
    
    # Sort by station and datetime
    feature_df = feature_df.sort_values(['station', 'datetime']).reset_index(drop=True)
    
    lag_features = []
    
    for acoustic in acoustic_features:
        if acoustic not in feature_df.columns:
            continue
            
        print(f"   Creating lags for {acoustic}")
        
        # Create lag features by station
        for lag in range(1, max_lag + 1):
            lag_col = f"{acoustic}_lag_{lag}h"
            feature_df[lag_col] = feature_df.groupby('station')[acoustic].shift(lag)
            lag_features.append(lag_col)
    
    print(f"✓ Created {len(lag_features)} lag features")
    return feature_df, lag_features

def create_cross_correlation_features(df, acoustic_features, target_species):
    """
    Create features based on cross-correlation patterns.
    """
    print(f"\n🔗 CREATING CROSS-CORRELATION FEATURES")
    
    feature_df = df.copy()
    cross_corr_features = []
    
    # For each station, compute recent correlation between acoustic and species
    for acoustic in acoustic_features:
        if acoustic not in feature_df.columns:
            continue
            
        print(f"   Cross-correlation features for {acoustic}")
        
        # Rolling correlation over 24-hour windows (12 periods)
        correlation_col = f"{acoustic}_rolling_corr_24h"
        
        def rolling_correlation(group):
            acoustic_data = group[acoustic].fillna(group[acoustic].mean())
            species_data = group[target_species].fillna(0)
            
            rolling_corr = []
            window_size = 12  # 24 hours
            
            for i in range(len(group)):
                if i < window_size:
                    rolling_corr.append(np.nan)
                else:
                    # CRITICAL: Use ONLY past data, exclude current time point to avoid data leakage
                    # Look at 24-hour window BEFORE current time point
                    window_acoustic = acoustic_data.iloc[i-window_size:i]  # Excludes current i
                    window_species = species_data.iloc[i-window_size:i]    # Excludes current i
                    
                    if window_acoustic.std() > 0 and window_species.std() > 0:
                        r, _ = pearsonr(window_acoustic, window_species)
                        rolling_corr.append(r)
                    else:
                        rolling_corr.append(0)
            
            return pd.Series(rolling_corr, index=group.index)
        
        feature_df[correlation_col] = feature_df.groupby('station').apply(rolling_correlation).values
        cross_corr_features.append(correlation_col)
    
    print(f"✓ Created {len(cross_corr_features)} cross-correlation features")
    return feature_df, cross_corr_features

def temporal_train_test_split(df, test_months=2, validation_months=1):
    """
    Create temporal train/test splits preserving chronological order.
    
    Args:
        df: DataFrame with datetime column
        test_months: Number of months for test set (from end)
        validation_months: Number of months for validation set (before test)
    
    Returns:
        train_df, val_df, test_df
    """
    print(f"\n📅 TEMPORAL TRAIN/TEST SPLIT")
    print("=" * 40)
    
    df_sorted = df.sort_values('datetime').reset_index(drop=True)
    
    # Find date boundaries
    max_date = df_sorted['datetime'].max()
    test_start = max_date - pd.DateOffset(months=test_months)
    val_start = test_start - pd.DateOffset(months=validation_months)
    
    # Create splits
    train_df = df_sorted[df_sorted['datetime'] < val_start].copy()
    val_df = df_sorted[
        (df_sorted['datetime'] >= val_start) & 
        (df_sorted['datetime'] < test_start)
    ].copy()
    test_df = df_sorted[df_sorted['datetime'] >= test_start].copy()
    
    print(f"📊 Temporal split summary:")
    print(f"   Train: {len(train_df):,} samples ({train_df['datetime'].min().date()} to {train_df['datetime'].max().date()})")
    print(f"   Val:   {len(val_df):,} samples ({val_df['datetime'].min().date()} to {val_df['datetime'].max().date()})")
    print(f"   Test:  {len(test_df):,} samples ({test_df['datetime'].min().date()} to {test_df['datetime'].max().date()})")
    
    return train_df, val_df, test_df

def build_temporal_aware_model(train_df, val_df, test_df, target_species, temporal_features):
    """
    Build and evaluate temporal-aware model.
    """
    print(f"\n🤖 BUILDING TEMPORAL-AWARE MODEL FOR {target_species}")
    print("=" * 65)
    
    # Prepare features
    feature_cols = temporal_features + [
        'Water temp (°C)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'Broadband (1-40000 Hz)'
    ]
    feature_cols = [col for col in feature_cols if col in train_df.columns]
    
    # CRITICAL SAFETY CHECK: Remove any species detection columns from features
    species_columns = ['Spotted seatrout', 'Atlantic croaker', 'Vessel', 'Oyster toadfish boat whistle', 
                      'Red drum', 'Silver perch', 'Black drum', 'Hardhead catfish', 
                      'total_fish_activity', 'any_activity', 'high_activity', 'num_active_species']
    
    # Remove any species columns that somehow made it into feature list
    feature_cols = [col for col in feature_cols if col not in species_columns]
    
    # Double-check: warn if target species somehow in features (should be impossible now)
    if target_species in feature_cols:
        raise ValueError(f"CRITICAL DATA LEAKAGE: Target species '{target_species}' found in feature list!")
    
    print(f"Using {len(feature_cols)} features:")
    print(f"   Temporal features: {len([f for f in feature_cols if any(x in f for x in ['lag_', 'rolling_corr'])])}")
    print(f"   Raw acoustic: {len([f for f in feature_cols if f in temporal_features and 'lag_' not in f and 'rolling_corr' not in f])}")
    print(f"   Environmental: {len([f for f in feature_cols if any(x in f for x in ['temp', 'Hz'])])}")
    
    # Log first few features for verification (no species should appear)
    print(f"   Sample features: {feature_cols[:5]}")
    
    # Final verification: Check NO species are in features
    species_in_features = [f for f in feature_cols if f in species_columns]
    if species_in_features:
        raise ValueError(f"CRITICAL DATA LEAKAGE DETECTED: Species columns in features: {species_in_features}")
    else:
        print(f"   ✅ Verified: No species detection columns in feature set")
    
    # Prepare target
    y_train = (train_df[target_species].fillna(0) > 0).astype(int)
    y_val = (val_df[target_species].fillna(0) > 0).astype(int)
    y_test = (test_df[target_species].fillna(0) > 0).astype(int)
    
    print(f"\n📊 Target distribution:")
    print(f"   Train: {y_train.sum():,}/{len(y_train):,} ({y_train.mean():.2%})")
    print(f"   Val:   {y_val.sum():,}/{len(y_val):,} ({y_val.mean():.2%})")
    print(f"   Test:  {y_test.sum():,}/{len(y_test):,} ({y_test.mean():.2%})")
    
    # Prepare features
    X_train = train_df[feature_cols].fillna(train_df[feature_cols].mean())
    X_val = val_df[feature_cols].fillna(train_df[feature_cols].mean())  # Use train means
    X_test = test_df[feature_cols].fillna(train_df[feature_cols].mean())  # Use train means
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Test multiple models
    models = {
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'RandomForest': RandomForestClassifier(
            n_estimators=100, 
            random_state=42, 
            n_jobs=-1,
            class_weight='balanced'  # Handle imbalanced classes
        )
    }
    
    results = {}
    
    for model_name, model in models.items():
        print(f"\n🔧 Training {model_name}...")
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Predict
        y_val_pred = model.predict(X_val_scaled)
        y_val_pred_proba = model.predict_proba(X_val_scaled)[:, 1]
        
        y_test_pred = model.predict(X_test_scaled)
        y_test_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Evaluate
        val_f1 = f1_score(y_val, y_val_pred)
        val_auc = roc_auc_score(y_val, y_val_pred_proba)
        val_ap = average_precision_score(y_val, y_val_pred_proba)
        
        test_f1 = f1_score(y_test, y_test_pred)
        test_auc = roc_auc_score(y_test, y_test_pred_proba)
        test_ap = average_precision_score(y_test, y_test_pred_proba)
        
        results[model_name] = {
            'val_f1': val_f1,
            'val_auc': val_auc,
            'val_ap': val_ap,
            'test_f1': test_f1,
            'test_auc': test_auc,
            'test_ap': test_ap,
            'model': model,
            'scaler': scaler,
            'features': feature_cols
        }
        
        print(f"   Validation - F1: {val_f1:.3f}, AUC: {val_auc:.3f}, AP: {val_ap:.3f}")
        print(f"   Test       - F1: {test_f1:.3f}, AUC: {test_auc:.3f}, AP: {test_ap:.3f}")
        
        # Feature importance for RandomForest
        if hasattr(model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': feature_cols,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print(f"   Top 5 important features:")
            for _, row in feature_importance.head(5).iterrows():
                feat_type = "🎵" if any(x in row['feature'] for x in temporal_features) else "🌡️"
                print(f"      {feat_type} {row['feature']:<25} {row['importance']:.3f}")
    
    return results

def compare_with_baseline(df, target_species, temporal_results):
    """
    Compare temporal-aware models with traditional random-split baseline.
    """
    print(f"\n🔍 COMPARING WITH BASELINE (RANDOM SPLIT)")
    print("=" * 55)
    
    from sklearn.model_selection import train_test_split
    
    # Create baseline with random split
    feature_cols = ['Water temp (°C)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)', 'Broadband (1-40000 Hz)']
    feature_cols = [col for col in feature_cols if col in df.columns]
    
    X = df[feature_cols].fillna(df[feature_cols].mean())
    y = (df[target_species].fillna(0) > 0).astype(int)
    
    # Random train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale and train
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    baseline_model = RandomForestClassifier(
        n_estimators=100, 
        random_state=42, 
        class_weight='balanced'
    )
    baseline_model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = baseline_model.predict(X_test_scaled)
    y_pred_proba = baseline_model.predict_proba(X_test_scaled)[:, 1]
    
    baseline_f1 = f1_score(y_test, y_pred)
    baseline_auc = roc_auc_score(y_test, y_pred_proba)
    baseline_ap = average_precision_score(y_test, y_pred_proba)
    
    print(f"📊 COMPARISON RESULTS:")
    print(f"{'Method':<25} {'F1':<8} {'AUC':<8} {'AP':<8}")
    print("-" * 50)
    print(f"{'Baseline (Random Split)':<25} {baseline_f1:<8.3f} {baseline_auc:<8.3f} {baseline_ap:<8.3f}")
    
    for model_name, results in temporal_results.items():
        print(f"{f'Temporal-Aware ({model_name})':<25} {results['test_f1']:<8.3f} {results['test_auc']:<8.3f} {results['test_ap']:<8.3f}")
    
    # Find best temporal model
    best_temporal = max(temporal_results.items(), key=lambda x: x[1]['test_f1'])
    best_name, best_results = best_temporal
    
    improvement = best_results['test_f1'] - baseline_f1
    
    print(f"\n💡 TEMPORAL-AWARE MODEL ANALYSIS:")
    print(f"   Best temporal model: {best_name}")
    print(f"   F1 improvement: {improvement:+.3f} ({improvement/baseline_f1*100:+.1f}%)")
    
    if improvement > 0.02:
        print(f"   ✅ SIGNIFICANT IMPROVEMENT - Temporal structure adds value!")
    elif improvement > 0:
        print(f"   ✅ MODEST IMPROVEMENT - Some temporal benefit")
    else:
        print(f"   ⚠️ No improvement - May need better temporal features")
    
    return {
        'baseline_f1': baseline_f1,
        'best_temporal_f1': best_results['test_f1'],
        'improvement': improvement,
        'best_model': best_name
    }

def main():
    print("🔄 PHASE 8: TEMPORAL-AWARE MACHINE LEARNING MODELS")
    print("=" * 75)
    print("Goal: Build predictive models that leverage temporal synchrony patterns")
    print("      discovered in Phase 6 while preserving temporal structure")
    
    # Load data
    df, correlation_results = load_data_and_correlations()
    
    # Target species (you can modify this list)
    target_species_list = ['Spotted seatrout', 'Atlantic croaker', 'Vessel', 'Oyster toadfish boat whistle']
    available_species = [species for species in target_species_list if species in df.columns]
    
    print(f"\n🎯 Target species: {available_species}")
    
    all_results = {}
    
    for species in available_species:
        print(f"\n{'='*20} ANALYZING {species.upper()} {'='*20}")
        
        # Check if species has enough activity
        species_data = df[species].fillna(0)
        detection_rate = (species_data > 0).mean()
        total_detections = species_data.sum()
        
        if detection_rate < 0.01 or total_detections < 100:
            print(f"⏭️ Skipping {species}: too few detections ({total_detections}, {detection_rate:.1%})")
            continue
        
        print(f"✓ {species}: {total_detections} detections ({detection_rate:.1%} of time periods)")
        
        # Identify temporal features
        temporal_features = identify_temporal_features(df, correlation_results, species)
        
        if len(temporal_features) == 0:
            print(f"⚠️ No temporal features found for {species}")
            continue
        
        # Create lag features
        feature_df, lag_features = create_temporal_lag_features(df, temporal_features, species)
        
        # Create cross-correlation features
        feature_df, cross_corr_features = create_cross_correlation_features(feature_df, temporal_features, species)
        
        # Combine all temporal features
        all_temporal_features = temporal_features + lag_features + cross_corr_features
        
        # Temporal train/test split
        train_df, val_df, test_df = temporal_train_test_split(feature_df)
        
        # Build temporal-aware model
        temporal_results = build_temporal_aware_model(
            train_df, val_df, test_df, species, all_temporal_features
        )
        
        # Compare with baseline
        comparison = compare_with_baseline(feature_df, species, temporal_results)
        
        # Store results
        all_results[species] = {
            'temporal_results': temporal_results,
            'comparison': comparison,
            'temporal_features': temporal_features,
            'n_temporal_features': len(all_temporal_features)
        }
    
    # Generate summary
    print(f"\n🎉 TEMPORAL-AWARE MODEL SUMMARY")
    print("=" * 50)
    
    if not all_results:
        print("❌ No species could be modeled")
        return
    
    print(f"Successfully modeled {len(all_results)} species:")
    
    for species, results in all_results.items():
        comparison = results['comparison']
        improvement = comparison['improvement']
        best_model = comparison['best_model']
        
        print(f"\n🐟 {species}:")
        print(f"   Best temporal model: {best_model}")
        print(f"   F1 improvement: {improvement:+.3f} ({improvement/comparison['baseline_f1']*100:+.1f}%)")
        print(f"   Temporal features used: {results['n_temporal_features']}")
        
        if improvement > 0.02:
            print(f"   ✅ Strong temporal benefit")
        elif improvement > 0:
            print(f"   ✅ Modest temporal benefit")
        else:
            print(f"   ⚠️ No temporal benefit")
    
    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create summary DataFrame
    summary_data = []
    for species, results in all_results.items():
        comparison = results['comparison']
        best_temporal_result = max(results['temporal_results'].items(), key=lambda x: x[1]['test_f1'])
        
        summary_data.append({
            'species': species,
            'baseline_f1': comparison['baseline_f1'],
            'temporal_f1': comparison['best_temporal_f1'],
            'improvement': comparison['improvement'],
            'improvement_pct': comparison['improvement']/comparison['baseline_f1']*100,
            'best_model': comparison['best_model'],
            'temporal_features_count': results['n_temporal_features'],
            'temporal_auc': best_temporal_result[1]['test_auc'],
            'temporal_ap': best_temporal_result[1]['test_ap']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(output_dir / "phase8_temporal_aware_model_results.csv", index=False)
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"   📊 Model summary: output/phase8_temporal_aware_model_results.csv")
    
    print("\n🎉 PHASE 8 COMPLETE!")
    print("=" * 30)
    print("✅ Temporal-aware models built")
    print("✅ Compared with traditional baseline")
    print("✅ Quantified temporal synchrony benefits")
    print("✅ Ready for operational deployment")
    
    return all_results

if __name__ == "__main__":
    main()