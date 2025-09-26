#!/usr/bin/env python3
"""
Script 4: Feature Importance Analysis
====================================

Purpose: Assess feature importance using methods appropriate for seasonal data
Key Question: Which feature categories matter most beyond the seasonal/diel baseline?

This script implements conditional mutual information analysis to determine which feature
categories (environmental, SPL, acoustic indices) provide biological information beyond
the seasonal and diel baseline patterns. It focuses on community metrics from Script 3
rather than individual species.

Key Outputs:
- data/processed/conditional_importance_results.parquet - Conditional MI rankings by feature category  
- data/processed/effort_lift_analysis.json - Detection efficiency improvements by feature type
- fresh_start_figures/04_conditional_importance_comparison.png - Bar chart of conditional MI by feature category
- fresh_start_figures/04_effort_lift_curves.png - Detection efficiency curves
- fresh_start_figures/04_cross_station_consistency.png - Stability across stations

Reference Sources:
- python/scripts/notebooks/06_02_standardized_feature_selection.py - Feature selection methods
- python/acoustic_vs_environmental/02_baseline_comparison.py - Feature importance patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Statistical analysis imports
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_regression
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import itertools

def find_project_root():
    """Find main project root (mbon-dash-2025) by looking for data/raw folder structure"""
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data" / "raw").exists() and project_root != project_root.parent:
        project_root = project_root.parent
    return project_root

# Set up paths: input and output both use main project data folder
PROJECT_ROOT = find_project_root()
DATA_ROOT = PROJECT_ROOT / "data"
INPUT_DIR = DATA_ROOT / "processed"  # Main project processed folder
OUTPUT_DIR = DATA_ROOT / "processed"  # Main project processed folder
FIGURE_DIR = DATA_ROOT / "processed" / "fresh_start_figures"  # Figures subfolder

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

print("="*60)
print("SCRIPT 4: FEATURE IMPORTANCE ANALYSIS")
print("="*60)
print(f"Project root: {PROJECT_ROOT}")
print(f"Input directory: {INPUT_DIR}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Figure directory: {FIGURE_DIR}")
print()

def load_analysis_datasets():
    """Load community metrics, aligned dataset, and acoustic indices"""
    print("1. LOADING ANALYSIS DATASETS")
    print("-" * 40)
    
    # Load community metrics (our targets)
    metrics_file = INPUT_DIR / "community_metrics.parquet"
    if not metrics_file.exists():
        raise FileNotFoundError(f"Community metrics not found: {metrics_file}\nPlease run Script 3 first.")
    
    df_metrics = pd.read_parquet(metrics_file)
    print(f"✓ Loaded community metrics: {df_metrics.shape}")
    
    # Load aligned dataset for environmental data
    aligned_file = INPUT_DIR / "aligned_dataset_2021.parquet"
    if not aligned_file.exists():
        raise FileNotFoundError(f"Aligned dataset not found: {aligned_file}\nPlease run Script 1 first.")
    
    df_aligned = pd.read_parquet(aligned_file)
    print(f"✓ Loaded aligned dataset: {df_aligned.shape}")
    
    # Load acoustic indices
    indices_data = {}
    stations = ['9M', '14M', '37M']
    year = 2021
    
    for station in stations:
        file_path = DATA_ROOT / "raw" / "indices" / f"Acoustic_Indices_{station}_{year}_FullBW_v2_Final.csv"
        if file_path.exists():
            try:
                df_idx = pd.read_csv(file_path)
                df_idx['datetime'] = pd.to_datetime(df_idx['Date'], errors='coerce')
                df_idx['station'] = station
                indices_data[station] = df_idx
                print(f"✓ Loaded acoustic indices {station}: {len(df_idx)} rows")
            except Exception as e:
                print(f"✗ Error loading indices {station}: {e}")
        else:
            print(f"✗ Indices file not found for {station}")
    
    # Combine acoustic indices
    if indices_data:
        df_indices = pd.concat(indices_data.values(), ignore_index=True)
        print(f"✓ Combined acoustic indices: {df_indices.shape}")
    else:
        df_indices = pd.DataFrame()
        print("⚠️ No acoustic indices loaded")
    
    print(f"Date range: {df_metrics['datetime'].min()} to {df_metrics['datetime'].max()}")
    print(f"Stations: {sorted(df_metrics['station'].unique())}")
    print()
    
    return df_metrics, df_aligned, df_indices

def identify_feature_categories(df_metrics, df_aligned, df_indices):
    """Identify and categorize features into ENV, SPL, and acoustic index categories"""
    print("2. IDENTIFYING FEATURE CATEGORIES")
    print("-" * 40)
    
    # Baseline temporal features (always included)
    baseline_features = ['hour_of_day', 'day_of_year', 'month', 'season', 'station']
    baseline_available = [f for f in baseline_features if f in df_metrics.columns]
    
    # Environmental features
    environmental_features = []
    env_patterns = ['temp', 'depth', 'pressure', 'salinity', 'ph', 'oxygen', 'turbidity']
    for pattern in env_patterns:
        matching = [col for col in df_aligned.columns if pattern.lower() in col.lower()]
        environmental_features.extend(matching)
    
    # SPL features  
    spl_features = []
    spl_patterns = ['spl', 'level', 'broadband', 'low_freq', 'high_freq']
    for pattern in spl_patterns:
        matching_aligned = [col for col in df_aligned.columns if pattern.lower() in col.lower()]
        matching_metrics = [col for col in df_metrics.columns if pattern.lower() in col.lower()]
        spl_features.extend(matching_aligned + matching_metrics)
    
    # Acoustic index features
    acoustic_index_features = []
    if not df_indices.empty:
        exclude_cols = ['Date', 'Time', 'station', 'datetime', 'year', 'month', 'day', 
                       'hour', 'minute', 'second', 'File', 'Deployment ID']
        acoustic_index_features = [col for col in df_indices.columns 
                                 if col not in exclude_cols and df_indices[col].dtype in ['float64', 'int64']]
    
    # Community target variables (what we want to predict)
    target_features = [
        'total_fish_intensity', 'fish_species_richness', 'total_dolphin_activity',
        'total_biological_activity', 'any_fish_activity', 'fish_activity_75th', 'fish_activity_90th'
    ]
    target_available = [f for f in target_features if f in df_metrics.columns]
    
    print(f"Feature categories identified:")
    print(f"  Baseline (temporal): {len(baseline_available)} features")
    print(f"  Environmental: {len(environmental_features)} features")
    print(f"  SPL: {len(spl_features)} features") 
    print(f"  Acoustic indices: {len(acoustic_index_features)} features")
    print(f"  Community targets: {len(target_available)} targets")
    
    print(f"\nBaseline features: {baseline_available}")
    print(f"Environmental features: {environmental_features[:5]}{'...' if len(environmental_features) > 5 else ''}")
    print(f"SPL features: {spl_features[:5]}{'...' if len(spl_features) > 5 else ''}")
    print(f"Acoustic index features: {acoustic_index_features[:5]}{'...' if len(acoustic_index_features) > 5 else ''}")
    print(f"Target features: {target_available}")
    print()
    
    feature_categories = {
        'baseline': baseline_available,
        'environmental': environmental_features,
        'spl': spl_features,
        'acoustic_indices': acoustic_index_features,
        'targets': target_available
    }
    
    return feature_categories

def create_analysis_dataset(df_metrics, df_aligned, df_indices, feature_categories):
    """Create unified analysis dataset with all features"""
    print("3. CREATING UNIFIED ANALYSIS DATASET")
    print("-" * 45)
    
    # Start with community metrics as base
    df_analysis = df_metrics.copy()
    print(f"Base dataset (community metrics): {df_analysis.shape}")
    
    # Add environmental features from aligned dataset if available
    env_features = feature_categories['environmental']
    if env_features:
        env_data = df_aligned[['datetime', 'station'] + env_features].drop_duplicates()
        df_analysis = pd.merge(df_analysis, env_data, on=['datetime', 'station'], how='left')
        print(f"After adding environmental features: {df_analysis.shape}")
    
    # Add SPL features from aligned dataset if available
    spl_features = [f for f in feature_categories['spl'] if f in df_aligned.columns]
    if spl_features:
        spl_data = df_aligned[['datetime', 'station'] + spl_features].drop_duplicates()
        df_analysis = pd.merge(df_analysis, spl_data, on=['datetime', 'station'], how='left')
        print(f"After adding SPL features: {df_analysis.shape}")
    
    # Add acoustic indices if available
    if not df_indices.empty and feature_categories['acoustic_indices']:
        # Aggregate indices to 2-hour intervals to match community metrics
        df_indices_agg = df_indices.copy()
        df_indices_agg['hour_2'] = (df_indices_agg['datetime'].dt.hour // 2) * 2
        df_indices_agg['date'] = df_indices_agg['datetime'].dt.date
        
        # Create matching datetime
        df_indices_agg['datetime_2h'] = pd.to_datetime(
            df_indices_agg['date'].astype(str) + ' ' + df_indices_agg['hour_2'].astype(str) + ':00:00'
        )
        
        # Aggregate indices to 2-hour means
        agg_dict = {col: 'mean' for col in feature_categories['acoustic_indices']}
        indices_2h = df_indices_agg.groupby(['datetime_2h', 'station']).agg(agg_dict).reset_index()
        indices_2h = indices_2h.rename(columns={'datetime_2h': 'datetime'})
        
        df_analysis = pd.merge(df_analysis, indices_2h, on=['datetime', 'station'], how='left')
        print(f"After adding acoustic indices: {df_analysis.shape}")
    
    # Create encoded station features for modeling
    station_dummies = pd.get_dummies(df_analysis['station'], prefix='station')
    df_analysis = pd.concat([df_analysis, station_dummies], axis=1)
    
    # Create encoded season features
    if 'season' in df_analysis.columns:
        season_dummies = pd.get_dummies(df_analysis['season'], prefix='season')
        df_analysis = pd.concat([df_analysis, season_dummies], axis=1)
    
    print(f"Final analysis dataset: {df_analysis.shape}")
    print(f"Missing data summary:")
    missing_pct = (df_analysis.isnull().sum() / len(df_analysis) * 100).sort_values(ascending=False)
    print(missing_pct[missing_pct > 0].head(10))
    print()
    
    return df_analysis

def calculate_conditional_mutual_information(df_analysis, feature_categories):
    """Calculate conditional mutual information: I(feature; biology | season, hour, station)"""
    print("4. CALCULATING CONDITIONAL MUTUAL INFORMATION")
    print("-" * 50)
    
    results = []
    targets = feature_categories['targets']
    
    # Define baseline conditioning variables
    baseline_vars = ['hour_of_day', 'day_of_year', 'month']
    baseline_vars = [v for v in baseline_vars if v in df_analysis.columns]
    
    # Add station dummy variables to baseline
    station_vars = [col for col in df_analysis.columns if col.startswith('station_')]
    baseline_vars.extend(station_vars)
    
    # Define feature groups to test
    feature_groups = {
        'ENV_only': feature_categories['environmental'],
        'SPL_only': feature_categories['spl'], 
        'INDEX_only': feature_categories['acoustic_indices'],
        'ENV+SPL': feature_categories['environmental'] + feature_categories['spl'],
        'ENV+INDEX': feature_categories['environmental'] + feature_categories['acoustic_indices'],
        'SPL+INDEX': feature_categories['spl'] + feature_categories['acoustic_indices'],
        'ENV+SPL+INDEX': feature_categories['environmental'] + feature_categories['spl'] + feature_categories['acoustic_indices']
    }
    
    print(f"Testing {len(feature_groups)} feature group combinations against {len(targets)} targets")
    print(f"Baseline conditioning variables: {len(baseline_vars)} features")
    
    for target in targets:
        if target not in df_analysis.columns:
            continue
            
        print(f"\nAnalyzing target: {target}")
        
        # Prepare target data
        valid_data = df_analysis[[target] + baseline_vars + 
                                feature_categories['environmental'] + 
                                feature_categories['spl'] + 
                                feature_categories['acoustic_indices']].dropna()
        
        if len(valid_data) < 100:  # Need sufficient data
            print(f"  ⚠️ Insufficient data: {len(valid_data)} samples")
            continue
            
        y = valid_data[target].values
        baseline_X = valid_data[baseline_vars].values
        
        print(f"  Valid samples: {len(valid_data)}")
        
        # Calculate baseline mutual information
        baseline_mi = mutual_info_regression(baseline_X, y, random_state=42)[0] if len(baseline_X) > 0 else 0
        
        for group_name, features in feature_groups.items():
            if not features:  # Skip empty feature groups
                continue
                
            # Check which features are actually available
            available_features = [f for f in features if f in valid_data.columns]
            if not available_features:
                continue
                
            try:
                # Combined features: baseline + group features
                combined_features = baseline_vars + available_features
                combined_X = valid_data[combined_features].values
                
                # Calculate mutual information with combined features
                combined_mi = mutual_info_regression(combined_X, y, random_state=42)[0]
                
                # Conditional MI is the improvement over baseline
                conditional_mi = combined_mi - baseline_mi
                
                results.append({
                    'target': target,
                    'feature_group': group_name,
                    'baseline_mi': baseline_mi,
                    'combined_mi': combined_mi,
                    'conditional_mi': conditional_mi,
                    'mi_improvement': conditional_mi / (baseline_mi + 1e-8),  # Avoid division by zero
                    'n_features': len(available_features),
                    'n_samples': len(valid_data)
                })
                
                print(f"    {group_name}: conditional MI = {conditional_mi:.4f} (improvement: {conditional_mi/(baseline_mi + 1e-8):.2f}x)")
                
            except Exception as e:
                print(f"    ⚠️ Error with {group_name}: {e}")
    
    results_df = pd.DataFrame(results)
    print(f"\nConditional MI analysis complete: {len(results_df)} results")
    print()
    
    return results_df

def calculate_effort_lift_analysis(df_analysis, feature_categories, results_df):
    """Calculate detection efficiency improvements at different effort levels"""
    print("5. CALCULATING EFFORT-LIFT ANALYSIS")
    print("-" * 40)
    
    effort_results = {}
    targets = feature_categories['targets']
    effort_levels = [0.1, 0.2, 0.3, 0.4, 0.5]  # 10%, 20%, 30%, 40%, 50% effort
    
    # Feature groups to test
    feature_groups = {
        'Baseline': ['hour_of_day', 'day_of_year', 'month'] + 
                   [col for col in df_analysis.columns if col.startswith('station_')],
        'ENV': feature_categories['environmental'],
        'SPL': feature_categories['spl'],
        'INDEX': feature_categories['acoustic_indices'],
        'ENV+SPL': feature_categories['environmental'] + feature_categories['spl'],
        'ENV+INDEX': feature_categories['environmental'] + feature_categories['acoustic_indices'],
        'ALL': feature_categories['environmental'] + feature_categories['spl'] + feature_categories['acoustic_indices']
    }
    
    for target in targets[:3]:  # Limit to top 3 targets for computational efficiency
        if target not in df_analysis.columns:
            continue
            
        print(f"\nAnalyzing effort-lift for target: {target}")
        
        # Prepare data
        all_features = list(set(
            [f for group_features in feature_groups.values() for f in group_features if f in df_analysis.columns]
        ))
        
        valid_data = df_analysis[[target] + all_features].dropna()
        if len(valid_data) < 200:
            print(f"  ⚠️ Insufficient data: {len(valid_data)} samples")
            continue
        
        y = valid_data[target].values
        
        target_results = {}
        
        for group_name, features in feature_groups.items():
            available_features = [f for f in features if f in valid_data.columns]
            if not available_features:
                continue
                
            try:
                X = valid_data[available_features].values
                
                # Train simple random forest for ranking
                rf = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
                rf.fit(X, y)
                
                # Get predictions (proxy for biological activity likelihood)
                predictions = rf.predict(X)
                
                # Calculate lift at different effort levels
                group_lift = []
                for effort in effort_levels:
                    # Select top effort% of predictions
                    n_select = int(len(predictions) * effort)
                    top_indices = np.argsort(predictions)[-n_select:]
                    
                    # Calculate biological activity capture rate
                    selected_activity = y[top_indices].sum()
                    total_activity = y.sum()
                    
                    capture_rate = selected_activity / total_activity if total_activity > 0 else 0
                    lift = capture_rate / effort if effort > 0 else 0
                    
                    group_lift.append({
                        'effort_level': effort,
                        'capture_rate': capture_rate,
                        'lift': lift
                    })
                
                target_results[group_name] = group_lift
                print(f"  ✓ {group_name}: 20% effort captures {target_results[group_name][1]['capture_rate']:.1%} of activity")
                
            except Exception as e:
                print(f"  ⚠️ Error with {group_name}: {e}")
        
        effort_results[target] = target_results
    
    print(f"\nEffort-lift analysis complete for {len(effort_results)} targets")
    print()
    
    return effort_results

def create_conditional_importance_plot(results_df):
    """Create bar chart showing conditional MI by feature category"""
    print("6. CREATING CONDITIONAL IMPORTANCE COMPARISON PLOT")
    print("-" * 55)
    
    if results_df.empty:
        print("⚠️ No results to plot")
        return None
    
    # Average conditional MI across targets for each feature group
    avg_results = results_df.groupby('feature_group').agg({
        'conditional_mi': ['mean', 'std'],
        'mi_improvement': ['mean', 'std'],
        'n_samples': 'mean'
    }).reset_index()
    
    # Flatten column names
    avg_results.columns = ['feature_group', 'conditional_mi_mean', 'conditional_mi_std',
                          'mi_improvement_mean', 'mi_improvement_std', 'n_samples_mean']
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Conditional MI by feature group
    bars1 = ax1.bar(range(len(avg_results)), avg_results['conditional_mi_mean'],
                    yerr=avg_results['conditional_mi_std'], capsize=5, 
                    color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum', 'orange', 'pink'])
    
    ax1.set_title('Conditional Mutual Information by Feature Category\n(Information Beyond Seasonal/Diel Baseline)', 
                 fontweight='bold', pad=20)
    ax1.set_xlabel('Feature Category')
    ax1.set_ylabel('Conditional Mutual Information')
    ax1.set_xticks(range(len(avg_results)))
    ax1.set_xticklabels(avg_results['feature_group'], rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars1):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + avg_results.iloc[i]['conditional_mi_std'],
                f'{height:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: MI improvement factor
    bars2 = ax2.bar(range(len(avg_results)), avg_results['mi_improvement_mean'],
                    yerr=avg_results['mi_improvement_std'], capsize=5,
                    color=['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum', 'orange', 'pink'])
    
    ax2.set_title('Mutual Information Improvement Factor\n(Relative to Baseline)', 
                 fontweight='bold', pad=20)
    ax2.set_xlabel('Feature Category')
    ax2.set_ylabel('MI Improvement Factor')
    ax2.set_xticks(range(len(avg_results)))
    ax2.set_xticklabels(avg_results['feature_group'], rotation=45)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='No improvement')
    
    # Add value labels on bars
    for i, bar in enumerate(bars2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + avg_results.iloc[i]['mi_improvement_std'],
                f'{height:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    comparison_file = FIGURE_DIR / "04_conditional_importance_comparison.png"
    plt.savefig(comparison_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Conditional importance comparison saved: {comparison_file}")
    return comparison_file

def create_effort_lift_curves(effort_results):
    """Create effort-lift curves showing detection efficiency"""
    print("7. CREATING EFFORT-LIFT CURVES")
    print("-" * 35)
    
    if not effort_results:
        print("⚠️ No effort results to plot")
        return None
    
    fig, axes = plt.subplots(1, len(effort_results), figsize=(5*len(effort_results), 6))
    if len(effort_results) == 1:
        axes = [axes]
    
    for i, (target, target_data) in enumerate(effort_results.items()):
        ax = axes[i] if len(effort_results) > 1 else axes
        
        for group_name, group_data in target_data.items():
            efforts = [d['effort_level'] for d in group_data]
            capture_rates = [d['capture_rate'] for d in group_data]
            
            ax.plot(efforts, capture_rates, 'o-', linewidth=2, markersize=6, label=group_name)
        
        # Add diagonal line for random selection
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random')
        
        ax.set_title(f'{target.replace("_", " ").title()}\nDetection Efficiency', fontweight='bold')
        ax.set_xlabel('Monitoring Effort (Fraction)')
        ax.set_ylabel('Biological Activity Captured (Fraction)')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 0.5)
        ax.set_ylim(0, 1)
    
    plt.suptitle('Effort-Lift Analysis: Detection Efficiency by Feature Category', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    lift_file = FIGURE_DIR / "04_effort_lift_curves.png"
    plt.savefig(lift_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Effort-lift curves saved: {lift_file}")
    return lift_file

def create_cross_station_consistency_plot(results_df, df_analysis):
    """Create plot showing consistency of importance rankings across stations"""
    print("8. CREATING CROSS-STATION CONSISTENCY PLOT")
    print("-" * 50)
    
    if results_df.empty:
        print("⚠️ No results to plot")
        return None
    
    # For now, create a simplified consistency analysis
    # This would be expanded with actual cross-station analysis
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Feature group performance by target
    pivot_data = results_df.pivot(index='feature_group', columns='target', values='conditional_mi')
    
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax1,
                cbar_kws={'label': 'Conditional Mutual Information'})
    ax1.set_title('Conditional MI by Feature Group and Target\n(Consistency Across Community Metrics)', 
                 fontweight='bold')
    ax1.set_xlabel('Community Metric Target')
    ax1.set_ylabel('Feature Category')
    
    # Plot 2: Sample sizes and data availability
    sample_sizes = results_df.groupby('feature_group')['n_samples'].mean()
    bars = ax2.bar(range(len(sample_sizes)), sample_sizes.values, 
                   color='lightblue', alpha=0.7)
    
    ax2.set_title('Data Availability by Feature Category\n(Average Sample Sizes)', fontweight='bold')
    ax2.set_xlabel('Feature Category')
    ax2.set_ylabel('Average Sample Size')
    ax2.set_xticks(range(len(sample_sizes)))
    ax2.set_xticklabels(sample_sizes.index, rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, sample_sizes.values):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 50,
                f'{int(value)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    consistency_file = FIGURE_DIR / "04_cross_station_consistency.png"
    plt.savefig(consistency_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Cross-station consistency plot saved: {consistency_file}")
    return consistency_file

def save_analysis_results(results_df, effort_results, feature_categories):
    """Save all analysis results to files"""
    print("9. SAVING ANALYSIS RESULTS")
    print("-" * 30)
    
    # Save conditional importance results
    if not results_df.empty:
        importance_file = OUTPUT_DIR / "conditional_importance_results.parquet"
        results_df.to_parquet(importance_file, index=False)
        print(f"✓ Conditional importance results saved: {importance_file}")
    
    # Save effort-lift analysis as JSON
    if effort_results:
        effort_file = OUTPUT_DIR / "effort_lift_analysis.json"
        with open(effort_file, 'w') as f:
            # Convert numpy types for JSON serialization
            json_safe_effort = {}
            for target, target_data in effort_results.items():
                json_safe_effort[target] = {}
                for group, group_data in target_data.items():
                    json_safe_effort[target][group] = [
                        {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                         for k, v in item.items()}
                        for item in group_data
                    ]
            json.dump(json_safe_effort, f, indent=2)
        print(f"✓ Effort-lift analysis saved: {effort_file}")
    
    # Save feature categories summary
    categories_file = OUTPUT_DIR / "feature_categories_summary.json"
    with open(categories_file, 'w') as f:
        json.dump({k: v for k, v in feature_categories.items() if k != 'targets'}, f, indent=2)
    print(f"✓ Feature categories summary saved: {categories_file}")
    
    print()

def main():
    """Main execution function"""
    print("Starting feature importance analysis...")
    print()
    
    # Load all required datasets
    df_metrics, df_aligned, df_indices = load_analysis_datasets()
    
    # Identify feature categories
    feature_categories = identify_feature_categories(df_metrics, df_aligned, df_indices)
    
    # Create unified analysis dataset
    df_analysis = create_analysis_dataset(df_metrics, df_aligned, df_indices, feature_categories)
    
    # Calculate conditional mutual information
    results_df = calculate_conditional_mutual_information(df_analysis, feature_categories)
    
    # Calculate effort-lift analysis
    effort_results = calculate_effort_lift_analysis(df_analysis, feature_categories, results_df)
    
    # Create visualizations
    try:
        create_conditional_importance_plot(results_df)
        create_effort_lift_curves(effort_results)
        create_cross_station_consistency_plot(results_df, df_analysis)
    except Exception as e:
        print(f"⚠️ Some visualizations failed: {e}")
    
    # Save all results
    save_analysis_results(results_df, effort_results, feature_categories)
    
    # Summary report
    print()
    print("="*60)
    print("FEATURE IMPORTANCE ANALYSIS COMPLETE")
    print("="*60)
    
    if not results_df.empty:
        print("KEY FINDINGS:")
        
        # Top performing feature groups
        avg_performance = results_df.groupby('feature_group')['conditional_mi'].mean().sort_values(ascending=False)
        print(f"Top feature categories by conditional MI:")
        for i, (group, score) in enumerate(avg_performance.head(3).items(), 1):
            print(f"  {i}. {group}: {score:.4f}")
        
        # Best targets for prediction
        target_performance = results_df.groupby('target')['conditional_mi'].mean().sort_values(ascending=False)
        print(f"\nMost predictable community metrics:")
        for i, (target, score) in enumerate(target_performance.head(3).items(), 1):
            print(f"  {i}. {target}: {score:.4f}")
    
    print()
    print("Key outputs:")
    print(f"- Conditional importance results: {OUTPUT_DIR / 'conditional_importance_results.parquet'}")
    print(f"- Effort-lift analysis: {OUTPUT_DIR / 'effort_lift_analysis.json'}")
    print(f"- Feature categories summary: {OUTPUT_DIR / 'feature_categories_summary.json'}")
    print(f"- Conditional importance comparison: {FIGURE_DIR / '04_conditional_importance_comparison.png'}")
    print(f"- Effort-lift curves: {FIGURE_DIR / '04_effort_lift_curves.png'}")
    print(f"- Cross-station consistency: {FIGURE_DIR / '04_cross_station_consistency.png'}")

if __name__ == "__main__":
    main()