#!/usr/bin/env python3
"""
Phase 2: Baseline Comparison - Raw Acoustic vs Environmental Features

This phase performs activity-informed selection of acoustic indices and establishes
a fair baseline comparison with environmental features (no temporal complexity yet).

Key outputs:
- Top acoustic indices ranked by biological prediction power
- Baseline model performance comparison
- Mutual information analysis
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


def load_aligned_data():
    """Load the Phase 1 aligned dataset."""
    data_path = Path("data_01_aligned_2021.csv")
    if not data_path.exists():
        raise FileNotFoundError(f"Phase 1 data not found: {data_path}")
    
    df = pd.read_csv(data_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    print(f"✓ Loaded aligned dataset: {df.shape}")
    print(f"   Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    print(f"   Stations: {sorted(df['station'].unique())}")
    
    return df


def identify_feature_groups(df):
    """Identify and categorize feature groups."""
    
    # Acoustic indices (from notebook 1, 60+ indices)
    acoustic_indices = [col for col in df.columns if col not in [
        'datetime', 'station', 'Red drum', 'Oyster toadfish grunt', 'Atlantic croaker', 
        'Vessel', 'Black drum', 'Bottlenose dolphin burst pulses', 'Bottlenose dolphin whistles',
        'Oyster toadfish boat whistle', 'Spotted seatrout', 'Silver perch',
        'Bottlenose dolphin echolocation', 'total_fish_activity', 'any_activity', 
        'num_active_species', 'high_activity', 'Water temp (°C)', 'Water depth (m)',
        'Broadband (1-40000 Hz)', 'Low (50-1200 Hz)', 'High (7000-40000 Hz)'
    ]]
    
    # Environmental features
    environmental_features = [
        'Water temp (°C)', 'Water depth (m)', 'Broadband (1-40000 Hz)', 
        'Low (50-1200 Hz)', 'High (7000-40000 Hz)'
    ]
    environmental_features = [col for col in environmental_features if col in df.columns]
    
    # Target variables
    target_variables = ['any_activity', 'high_activity', 'total_fish_activity', 'num_active_species']
    
    # Species detection variables
    species_variables = [
        'Red drum', 'Oyster toadfish grunt', 'Atlantic croaker', 'Vessel', 'Black drum',
        'Bottlenose dolphin burst pulses', 'Bottlenose dolphin whistles',
        'Oyster toadfish boat whistle', 'Spotted seatrout', 'Silver perch'
    ]
    species_variables = [col for col in species_variables if col in df.columns]
    
    print(f"📊 Feature group identification:")
    print(f"   Acoustic indices: {len(acoustic_indices)}")
    print(f"   Environmental: {len(environmental_features)}")
    print(f"   Species variables: {len(species_variables)}")
    print(f"   Target variables: {len(target_variables)}")
    
    return {
        'acoustic': acoustic_indices,
        'environmental': environmental_features,
        'species': species_variables,
        'targets': target_variables
    }


def mutual_information_analysis(df, feature_groups, target='any_activity'):
    """
    Perform comprehensive mutual information analysis to rank features
    by their biological prediction power.
    """
    
    print(f"\n🔍 MUTUAL INFORMATION ANALYSIS")
    print("="*50)
    print(f"Target variable: {target}")
    print(f"Target distribution: {dict(df[target].value_counts(normalize=True).round(3))}")
    
    all_features = feature_groups['acoustic'] + feature_groups['environmental']
    X = df[all_features]
    y = df[target]
    
    # Handle any remaining missing values
    X = X.fillna(X.mean())
    
    # Calculate mutual information
    mi_scores = mutual_info_classif(X, y, random_state=42)
    
    # Create results dataframe
    mi_results = pd.DataFrame({
        'feature': all_features,
        'mi_score': mi_scores,
        'feature_type': ['acoustic'] * len(feature_groups['acoustic']) + 
                       ['environmental'] * len(feature_groups['environmental'])
    }).sort_values('mi_score', ascending=False)
    
    print(f"\n🏆 TOP 20 MOST PREDICTIVE FEATURES:")
    print("-" * 60)
    for i, (_, row) in enumerate(mi_results.head(20).iterrows(), 1):
        feature_emoji = '🎵' if row['feature_type'] == 'acoustic' else '🌡️'
        print(f"{i:2d}. {feature_emoji} {row['feature_type']:13} | {row['feature'][:35]:35} | MI: {row['mi_score']:.3f}")
    
    # Group-level analysis
    print(f"\n📊 FEATURE TYPE COMPARISON:")
    print("-" * 40)
    
    group_stats = mi_results.groupby('feature_type')['mi_score'].agg(['count', 'mean', 'max', 'std']).round(3)
    
    for feature_type, stats in group_stats.iterrows():
        feature_emoji = '🎵' if feature_type == 'acoustic' else '🌡️'
        top5_mean = mi_results[mi_results['feature_type'] == feature_type].head(5)['mi_score'].mean()
        print(f"{feature_emoji} {feature_type:13} | Features: {int(stats['count']):2d} | Mean: {stats['mean']:.3f} | Max: {stats['max']:.3f} | Top5: {top5_mean:.3f}")
    
    # Statistical comparison
    acoustic_scores = mi_results[mi_results['feature_type'] == 'acoustic']['mi_score']
    env_scores = mi_results[mi_results['feature_type'] == 'environmental']['mi_score']
    
    print(f"\n🎯 STATISTICAL COMPARISON:")
    print(f"   Best acoustic feature: {acoustic_scores.max():.3f}")
    print(f"   Best environmental feature: {env_scores.max():.3f}")
    print(f"   Acoustic mean: {acoustic_scores.mean():.3f}")
    print(f"   Environmental mean: {env_scores.mean():.3f}")
    
    if env_scores.max() > acoustic_scores.max():
        advantage = env_scores.max() - acoustic_scores.max()
        print(f"   🌡️ Environmental features dominate (advantage: +{advantage:.3f})")
    else:
        advantage = acoustic_scores.max() - env_scores.max()
        print(f"   🎵 Acoustic features dominate (advantage: +{advantage:.3f})")
    
    return mi_results


def select_top_acoustic_indices(mi_results, n_indices=10):
    """Select top acoustic indices based on mutual information scores."""
    
    acoustic_results = mi_results[mi_results['feature_type'] == 'acoustic'].copy()
    top_indices = acoustic_results.head(n_indices)
    
    print(f"\n🎯 SELECTED TOP {n_indices} ACOUSTIC INDICES:")
    print("-" * 50)
    print("Rank | Feature                          | MI Score")
    print("-" * 50)
    
    for i, (_, row) in enumerate(top_indices.iterrows(), 1):
        print(f"{i:2d}   | {row['feature'][:30]:30} | {row['mi_score']:.3f}")
    
    selected_indices = top_indices['feature'].tolist()
    
    # Compare with all acoustic indices
    print(f"\n📈 SELECTION QUALITY:")
    all_acoustic_mi = acoustic_results['mi_score']
    selected_mi = top_indices['mi_score']
    
    print(f"   Top {n_indices} mean MI: {selected_mi.mean():.3f}")
    print(f"   All acoustic mean MI: {all_acoustic_mi.mean():.3f}")
    print(f"   Selection advantage: +{selected_mi.mean() - all_acoustic_mi.mean():.3f}")
    print(f"   Coverage of top variance: {selected_mi.sum() / all_acoustic_mi.sum():.1%}")
    
    return selected_indices, top_indices


def baseline_model_comparison(df, feature_groups, selected_acoustic_indices):
    """
    Compare model performance using different feature sets:
    1. Top acoustic indices only
    2. All environmental features only  
    3. Combined (top acoustic + environmental)
    """
    
    print(f"\n🤖 BASELINE MODEL COMPARISON")
    print("="*50)
    print("Testing raw feature performance (no temporal features)")
    
    # Define feature sets for comparison
    feature_sets = {
        'acoustic_selected': {
            'features': selected_acoustic_indices,
            'description': f'Top {len(selected_acoustic_indices)} Acoustic Indices'
        },
        'environmental_only': {
            'features': feature_groups['environmental'],
            'description': 'Environmental Features Only'
        },
        'combined_raw': {
            'features': selected_acoustic_indices + feature_groups['environmental'],
            'description': 'Top Acoustic + Environmental'
        }
    }
    
    # Models to test
    models = {
        'Logistic': LogisticRegression(random_state=42, max_iter=1000),
        'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    }
    
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    target = 'any_activity'
    results = {}
    
    print(f"\nTarget: {target}")
    print(f"Dataset: {df.shape[0]} observations")
    print(f"Target distribution: {dict(df[target].value_counts(normalize=True).round(3))}")
    
    for model_name, model in models.items():
        print(f"\n📈 {model_name.upper()} RESULTS:")
        print("-" * 35)
        
        model_results = {}
        
        for set_name, set_config in feature_sets.items():
            available_features = [f for f in set_config['features'] if f in df.columns]
            
            if len(available_features) == 0:
                print(f"  ⚠️ No features available for {set_name}")
                continue
            
            X = df[available_features].fillna(df[available_features].mean())
            y = df[target]
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='f1')
            
            model_results[set_name] = {
                'mean_f1': cv_scores.mean(),
                'std_f1': cv_scores.std(),
                'scores': cv_scores,
                'n_features': len(available_features)
            }
            
            print(f"  {set_config['description']:25} | F1: {cv_scores.mean():.3f}±{cv_scores.std():.3f} | n={len(available_features)}")
        
        results[model_name] = model_results
    
    return results


def generate_phase2_insights(mi_results, baseline_results, selected_indices):
    """Generate key insights from Phase 2 analysis."""
    
    print(f"\n🎯 PHASE 2 INSIGHTS & CONCLUSIONS")
    print("="*60)
    
    # Mutual information insights
    acoustic_mi = mi_results[mi_results['feature_type'] == 'acoustic']['mi_score']
    env_mi = mi_results[mi_results['feature_type'] == 'environmental']['mi_score']
    
    print(f"\n📊 Feature Importance Analysis:")
    print(f"   🎵 Best acoustic feature MI: {acoustic_mi.max():.3f}")
    print(f"   🌡️ Best environmental feature MI: {env_mi.max():.3f}")
    print(f"   📈 Environmental advantage: {env_mi.max() - acoustic_mi.max():+.3f}")
    
    if env_mi.max() > acoustic_mi.max():
        print(f"   🏆 Environmental features are more predictive individually")
    else:
        print(f"   🏆 Acoustic features are more predictive individually")
    
    # Model performance insights
    print(f"\n🤖 Baseline Model Performance:")
    for model_name, model_results in baseline_results.items():
        if all(key in model_results for key in ['acoustic_selected', 'environmental_only', 'combined_raw']):
            acoustic_f1 = model_results['acoustic_selected']['mean_f1']
            env_f1 = model_results['environmental_only']['mean_f1']
            combined_f1 = model_results['combined_raw']['mean_f1']
            
            print(f"   {model_name}:")
            print(f"     Top acoustic indices: F1 = {acoustic_f1:.3f}")
            print(f"     Environmental only:   F1 = {env_f1:.3f}")
            print(f"     Combined:            F1 = {combined_f1:.3f}")
            
            # Calculate improvements
            env_advantage = env_f1 - acoustic_f1
            synergy = combined_f1 - max(acoustic_f1, env_f1)
            
            if env_advantage > 0.02:
                print(f"     🌡️ Environmental dominates (+{env_advantage:.3f})")
            elif env_advantage < -0.02:
                print(f"     🎵 Acoustic dominates ({env_advantage:+.3f})")
            else:
                print(f"     🤝 Comparable performance")
                
            if synergy > 0.01:
                print(f"     ✨ Positive synergy (+{synergy:.3f})")
            else:
                print(f"     ❌ Limited synergy ({synergy:+.3f})")
    
    # Selection quality
    print(f"\n🔍 Index Selection Results:")
    print(f"   Selected {len(selected_indices)} of {len(acoustic_mi)} acoustic indices")
    selected_mi_mean = mi_results[mi_results['feature'].isin(selected_indices)]['mi_score'].mean()
    print(f"   Selected indices mean MI: {selected_mi_mean:.3f}")
    print(f"   All acoustic indices mean MI: {acoustic_mi.mean():.3f}")
    print(f"   Selection improvement: +{selected_mi_mean - acoustic_mi.mean():.3f}")
    
    # Recommendations for Phase 3
    print(f"\n💡 RECOMMENDATIONS FOR PHASE 3:")
    if env_mi.max() > acoustic_mi.max() + 0.05:
        print(f"   🌡️ Environmental features strongly dominate")
        print(f"   ➤ Focus temporal engineering on environmental features")
        print(f"   ➤ Use acoustic indices primarily for interpretation/context")
    elif combined_f1 > max(acoustic_f1, env_f1) + 0.02:
        print(f"   🤝 Strong synergy detected")
        print(f"   ➤ Create temporal features for both acoustic and environmental")
        print(f"   ➤ Equal complexity recommended")
    else:
        print(f"   ⚖️ Mixed evidence")
        print(f"   ➤ Create limited temporal features for both types")
        print(f"   ➤ Focus on top-performing features from each group")
        
    return {
        'selected_acoustic_indices': selected_indices,
        'mi_results': mi_results,
        'baseline_results': baseline_results,
        'environmental_dominates': env_mi.max() > acoustic_mi.max() + 0.05
    }


def save_phase2_results(insights):
    """Save Phase 2 results for Phase 3."""
    
    # Save selected indices
    selected_indices_df = pd.DataFrame({
        'acoustic_index': insights['selected_acoustic_indices'],
        'selection_method': 'mutual_information',
        'phase': 'phase2'
    })
    
    selected_indices_df.to_csv('selected_acoustic_indices.csv', index=False)
    print(f"\n💾 Saved selected indices to: selected_acoustic_indices.csv")
    
    # Save MI results
    insights['mi_results'].to_csv('phase2_mutual_information_results.csv', index=False)
    print(f"💾 Saved MI results to: phase2_mutual_information_results.csv")
    
    # Save summary
    summary = {
        'n_selected_indices': len(insights['selected_acoustic_indices']),
        'environmental_dominates': bool(insights['environmental_dominates']),
        'selected_indices': insights['selected_acoustic_indices'],
        'best_acoustic_mi': float(insights['mi_results'][insights['mi_results']['feature_type'] == 'acoustic']['mi_score'].max()),
        'best_environmental_mi': float(insights['mi_results'][insights['mi_results']['feature_type'] == 'environmental']['mi_score'].max())
    }
    
    import json
    with open('phase2_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"💾 Saved summary to: phase2_summary.json")


def create_figure_6_feature_importance(mi_results):
    """
    FIGURE 6: Create horizontal bar chart showing mutual information scores 
    comparing acoustic vs environmental features.
    """
    print(f"\n🎨 CREATING FIGURE 6: Feature Importance Comparison")
    print("=" * 50)
    
    # Get top features from each type
    acoustic_features = mi_results[mi_results['feature_type'] == 'acoustic'].nlargest(10, 'mi_score')
    env_features = mi_results[mi_results['feature_type'] == 'environmental'].nlargest(10, 'mi_score')
    
    # Combine for plotting
    plot_data = pd.concat([env_features, acoustic_features]).sort_values('mi_score', ascending=True)
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Color by feature type
    colors = ['#ff7f0e' if ft == 'acoustic' else '#1f77b4' for ft in plot_data['feature_type']]
    
    # Create horizontal bar plot
    bars = ax.barh(range(len(plot_data)), plot_data['mi_score'], color=colors)
    
    # Customize the plot
    ax.set_yticks(range(len(plot_data)))
    ax.set_yticklabels([f[:30] + '...' if len(f) > 33 else f for f in plot_data['feature']], fontsize=10)
    ax.set_xlabel('Mutual Information Score', fontsize=12)
    ax.set_title('Feature Importance: Mutual Information with Fish Activity\n(Orange = Acoustic, Blue = Environmental)', 
                fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, plot_data['mi_score'])):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2, 
               f'{score:.3f}', va='center', fontsize=9)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#1f77b4', label='Environmental Features'),
                      Patch(facecolor='#ff7f0e', label='Acoustic Indices')]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path("output/phase2_baseline/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig_path = output_dir / "feature_importance_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Figure 6: {fig_path}")
    plt.close()
    
    return fig_path

def create_figure_2_model_performance(baseline_results):
    """
    FIGURE 2: Create bar chart comparing model performance across different approaches.
    """
    print(f"\n🎨 CREATING FIGURE 2: Model Performance Comparison")
    print("=" * 50)
    
    # Prepare data for plotting
    models = []
    feature_sets = []
    f1_scores = []
    std_scores = []
    
    feature_set_labels = {
        'acoustic_selected': 'Top Acoustic Indices',
        'environmental_only': 'Environmental Only', 
        'combined_raw': 'Combined Features'
    }
    
    for model_name, model_results in baseline_results.items():
        for set_name, results in model_results.items():
            if set_name in feature_set_labels:
                models.append(model_name)
                feature_sets.append(feature_set_labels[set_name])
                f1_scores.append(results['mean_f1'])
                std_scores.append(results['std_f1'])
    
    # Create DataFrame for easier plotting
    plot_df = pd.DataFrame({
        'Model': models,
        'Feature_Set': feature_sets,
        'F1_Score': f1_scores,
        'F1_Std': std_scores
    })
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    # Group by feature set for side-by-side bars
    unique_sets = plot_df['Feature_Set'].unique()
    unique_models = plot_df['Model'].unique()
    
    x = np.arange(len(unique_sets))
    width = 0.35
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for i, model in enumerate(unique_models):
        model_data = plot_df[plot_df['Model'] == model]
        # Reorder to match unique_sets order
        ordered_data = []
        ordered_std = []
        for fs in unique_sets:
            matching = model_data[model_data['Feature_Set'] == fs]
            if len(matching) > 0:
                ordered_data.append(matching['F1_Score'].iloc[0])
                ordered_std.append(matching['F1_Std'].iloc[0])
            else:
                ordered_data.append(0)
                ordered_std.append(0)
        
        bars = ax.bar(x + i*width, ordered_data, width, yerr=ordered_std, 
                     label=model, color=colors[i], alpha=0.8, capsize=5)
        
        # Add value labels on bars
        for bar, score, std in zip(bars, ordered_data, ordered_std):
            if score > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + std + 0.01,
                       f'{score:.3f}', ha='center', va='bottom', fontsize=10)
    
    # Customize the plot
    ax.set_xlabel('Feature Set', fontsize=12)
    ax.set_ylabel('F1 Score', fontsize=12)
    ax.set_title('Model Performance Comparison\n(Error bars show standard deviation)', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x + width/2)
    ax.set_xticklabels(unique_sets)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, max(f1_scores) + max(std_scores) + 0.1)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path("output/phase2_baseline/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    fig_path = output_dir / "model_performance_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Figure 2: {fig_path}")
    plt.close()
    
    return fig_path

def main():
    """Execute Phase 2: Baseline comparison and index selection."""
    
    print("🔄 PHASE 2: BASELINE COMPARISON & INDEX SELECTION")
    print("="*70)
    print("Goal: Select top acoustic indices based on biological prediction power")
    print("Compare raw feature performance before temporal engineering")
    
    # Load data
    df = load_aligned_data()
    
    # Identify feature groups
    feature_groups = identify_feature_groups(df)
    
    # Mutual information analysis
    mi_results = mutual_information_analysis(df, feature_groups)
    
    # Select top acoustic indices
    selected_indices, top_indices_df = select_top_acoustic_indices(mi_results, n_indices=10)
    
    # Baseline model comparison
    baseline_results = baseline_model_comparison(df, feature_groups, selected_indices)
    
    # Generate insights
    insights = generate_phase2_insights(mi_results, baseline_results, selected_indices)
    
    # Generate figures for the report
    print(f"\n📊 GENERATING FIGURES FOR REPORT")
    print("=" * 40)
    
    # Figure 6: Feature Importance Comparison
    create_figure_6_feature_importance(mi_results)
    
    # Figure 2: Model Performance Comparison
    create_figure_2_model_performance(baseline_results)
    
    # Save results
    save_phase2_results(insights)
    
    print(f"\n🎉 PHASE 2 COMPLETE!")
    print("="*40)
    print("✅ Selected top 10 acoustic indices based on biological prediction")
    print("✅ Established baseline performance comparison")  
    print("✅ Identified environmental vs acoustic strengths")
    print("✅ Ready for Phase 3: Temporal feature engineering")
    
    return insights


if __name__ == "__main__":
    insights = main()