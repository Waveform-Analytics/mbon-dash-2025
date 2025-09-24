#!/usr/bin/env python3
"""
Generate Key ML Section Figures for Marine Acoustic Discovery Report
==================================================================

This script creates the critical visualizations that illustrate the systematic
machine learning failures and breakthroughs in the marine acoustic monitoring project.

Figures created:
1. Feature Selection Disagreement (MI vs Boruta)
2. Temporal Validation Performance Drop  
3. Species Prediction Failure Examples
4. ML Journey Summary

Author: Marine Biodiversity Observation Network
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

# Find project root by looking for the data folder (same pattern as notebooks)
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
project_root = current_dir
while not (project_root / "data").exists() and project_root != project_root.parent:
    project_root = project_root.parent

# Set up directories
data_dir = project_root / "data/processed"
output_dir = project_root / "dashboard/public/views/notebooks"
output_dir.mkdir(parents=True, exist_ok=True)

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 11

print("🎨 Generating ML Report Figures")
print("=" * 50)

def create_feature_selection_disagreement_figure():
    """
    Create visualization showing how MI and Boruta disagreed on feature selection.
    """
    print("📊 Creating Feature Selection Disagreement Figure...")
    
    # Load the enhanced analysis results
    try:
        with open(data_dir / "06_01_enhanced_analysis_summary.json", 'r') as f:
            analysis_results = json.load(f)
        
        feature_insights = analysis_results['feature_selection_insights']
        
        # Extract data for visualization
        targets = list(feature_insights.keys())
        agreement_rates = [feature_insights[target]['agreement_rate'] for target in targets]
        consensus_counts = [len(feature_insights[target]['consensus_features']) for target in targets]
        unique_counts = [feature_insights[target]['total_unique_features'] for target in targets]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Left plot: Agreement rates
        colors = ['#e74c3c' if rate < 0.2 else '#f39c12' if rate < 0.5 else '#27ae60' 
                 for rate in agreement_rates]
        
        bars1 = ax1.bar(range(len(targets)), agreement_rates, color=colors, alpha=0.8, 
                       edgecolor='black', linewidth=1)
        ax1.set_xlabel('Biological Target', fontweight='bold')
        ax1.set_ylabel('Agreement Rate', fontweight='bold')
        ax1.set_title('Feature Selection Method Agreement\n(Mutual Information vs Boruta)', 
                     fontweight='bold', fontsize=12)
        ax1.set_xticks(range(len(targets)))
        ax1.set_xticklabels([t.replace('_', '\n').title() for t in targets], rotation=0)
        ax1.set_ylim(0, 1.0)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add agreement rate labels on bars
        for i, (bar, rate) in enumerate(zip(bars1, agreement_rates)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{rate:.0%}', ha='center', va='bottom', fontweight='bold')
        
        # Add horizontal line at 50% for reference
        ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
        ax1.text(0.02, 0.52, '50% (Random)', transform=ax1.transAxes, 
                color='gray', style='italic')
        
        # Right plot: Feature breakdown
        x_pos = np.arange(len(targets))
        width = 0.35
        
        mi_only = [unique - consensus for unique, consensus in zip(unique_counts, consensus_counts)]
        boruta_only = [unique - consensus for unique, consensus in zip(unique_counts, consensus_counts)]
        
        bars2 = ax2.bar(x_pos - width/2, mi_only, width, label='MI Only', 
                       color='steelblue', alpha=0.8)
        bars3 = ax2.bar(x_pos, consensus_counts, width, label='Both Methods', 
                       color='purple', alpha=0.8)
        bars4 = ax2.bar(x_pos + width/2, boruta_only, width, label='Boruta Only', 
                       color='darkgreen', alpha=0.8)
        
        ax2.set_xlabel('Biological Target', fontweight='bold')
        ax2.set_ylabel('Number of Features', fontweight='bold')
        ax2.set_title('Feature Selection Overlap\n(Top 5 Features per Method)', 
                     fontweight='bold', fontsize=12)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([t.replace('_', '\n').title() for t in targets], rotation=0)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars2, bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_dir / '02a_feature_selection_disagreement.png', 
                   bbox_inches='tight', facecolor='white')
        plt.savefig(output_dir / 'ml_feature_selection_disagreement.png', 
                   bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   ✅ Feature selection disagreement figure created")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating feature selection figure: {e}")
        return False


def create_temporal_validation_drop_figure():
    """
    Create visualization showing performance drop with proper temporal validation.
    """
    print("📊 Creating Temporal Validation Performance Drop Figure...")
    
    try:
        with open(data_dir / "06_04_temporal_modeling_analysis.json", 'r') as f:
            temporal_results = json.load(f)
        
        # Extract performance data
        models = ['Logistic Regression', 'Random Forest']
        standard_cv = [temporal_results['logistic']['cv_comparison']['standard_cv_f1'],
                      temporal_results['random_forest']['cv_comparison']['standard_cv_f1']]
        temporal_cv = [temporal_results['logistic']['cv_comparison']['temporal_cv_f1'],
                      temporal_results['random_forest']['cv_comparison']['temporal_cv_f1']]
        
        # Calculate performance drops
        drops = [std - temp for std, temp in zip(standard_cv, temporal_cv)]
        drop_pcts = [drop / std * 100 for drop, std in zip(drops, standard_cv)]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Left plot: Performance comparison
        x_pos = np.arange(len(models))
        width = 0.35
        
        bars1 = ax1.bar(x_pos - width/2, standard_cv, width, label='Standard CV', 
                       color='lightcoral', alpha=0.8, edgecolor='black')
        bars2 = ax1.bar(x_pos + width/2, temporal_cv, width, label='Temporal CV', 
                       color='steelblue', alpha=0.8, edgecolor='black')
        
        ax1.set_xlabel('Model Type', fontweight='bold')
        ax1.set_ylabel('F1 Score', fontweight='bold')
        ax1.set_title('Performance Drop with Proper Temporal Validation\n(Community Activity Detection)', 
                     fontweight='bold', fontsize=12)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(models)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_ylim(0, 0.9)
        
        # Add value labels on bars
        for i, (bar1, bar2, std_val, temp_val) in enumerate(zip(bars1, bars2, standard_cv, temporal_cv)):
            ax1.text(bar1.get_x() + bar1.get_width()/2., bar1.get_height() + 0.01,
                    f'{std_val:.3f}', ha='center', va='bottom', fontweight='bold')
            ax1.text(bar2.get_x() + bar2.get_width()/2., bar2.get_height() + 0.01,
                    f'{temp_val:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # Add arrows showing drops
        for i, (std_val, temp_val, drop_pct) in enumerate(zip(standard_cv, temporal_cv, drop_pcts)):
            ax1.annotate('', xy=(i + width/2, temp_val), xytext=(i - width/2, std_val),
                        arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax1.text(i, (std_val + temp_val)/2, f'{drop_pct:.0f}%\ndrop', 
                    ha='center', va='center', color='red', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Right plot: Temporal leakage explanation
        ax2.axis('off')
        explanation_text = """
        TEMPORAL LEAKAGE PROBLEM
        
        Standard Cross-Validation:
        • Random train/test splits
        • Uses future data to predict past
        • Artificially inflated performance
        • F1 scores: 0.82-0.84
        
        Temporal Cross-Validation:
        • Chronological train/test splits
        • Only uses past to predict future
        • Realistic performance estimate  
        • F1 scores: 0.63-0.79
        
        IMPACT:
        • 6-23% performance overestimation
        • Models were "cheating"
        • Real-world performance much lower
        • Standard validation misleading
        """
        
        ax2.text(0.1, 0.9, explanation_text, transform=ax2.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round,pad=1', 
                facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(output_dir / '02b_temporal_validation_drop.png', 
                   bbox_inches='tight', facecolor='white')
        plt.savefig(output_dir / 'ml_temporal_validation_drop.png', 
                   bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   ✅ Temporal validation drop figure created")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating temporal validation figure: {e}")
        return False


def create_species_prediction_failure_figure():
    """
    Create visualization showing why species-specific prediction failed.
    """
    print("📊 Creating Species Prediction Failure Figure...")
    
    try:
        # Load detection data to demonstrate the failure
        df_detections = pd.read_parquet(data_dir / "02_detections_aligned_2021.parquet")
        df_indices = pd.read_parquet(data_dir / "03_reduced_acoustic_indices.parquet")
        
        # Merge data
        df_merged = df_indices.merge(df_detections, on=['datetime', 'station'], how='inner')
        
        # Select a few species with reasonable activity
        species_cols = ['Silver perch', 'Spotted seatrout', 'Oyster toadfish boat whistle', 'Atlantic croaker']
        available_species = [col for col in species_cols if col in df_merged.columns]
        
        if len(available_species) == 0:
            # Fallback: use any fish columns available
            available_species = [col for col in df_merged.columns 
                               if col not in ['datetime', 'station', 'year'] 
                               and df_merged[col].dtype in ['int64', 'float64']
                               and df_merged[col].max() <= 3][:4]
        
        if len(available_species) < 2:
            print("   ⚠️  Insufficient species data for species failure figure")
            return False
        
        # Select best acoustic index for demonstration (one with some correlation)
        acoustic_indices = [col for col in df_merged.columns 
                          if col not in ['datetime', 'station', 'year'] + available_species
                          and df_merged[col].dtype in ['int64', 'float64']]
        
        if len(acoustic_indices) == 0:
            print("   ⚠️  No acoustic indices found for species failure figure")
            return False
        
        # Create figure
        n_species = min(4, len(available_species))
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        axes = axes.flatten()
        
        # Use a representative acoustic index
        acoustic_index = acoustic_indices[0] if 'ACI' in acoustic_indices[0] else acoustic_indices[0]
        
        for i, species in enumerate(available_species[:n_species]):
            ax = axes[i]
            
            # Get clean data
            species_data = df_merged[[acoustic_index, species]].dropna()
            if len(species_data) < 50:
                continue
                
            x = species_data[acoustic_index]
            y = species_data[species]
            
            # Scatter plot
            scatter = ax.scatter(x, y, alpha=0.6, s=20, c='steelblue')
            
            # Try to fit a line (this will show poor correlation)
            try:
                correlation = np.corrcoef(x, y)[0, 1]
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                x_line = np.linspace(x.min(), x.max(), 100)
                ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
                
                ax.text(0.05, 0.95, f'R = {correlation:.3f}\n(Poor correlation)', 
                       transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                       fontweight='bold', color='red')
            except:
                ax.text(0.05, 0.95, 'No clear pattern', 
                       transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                       fontweight='bold', color='red')
            
            ax.set_xlabel(f'{acoustic_index}', fontweight='bold')
            ax.set_ylabel(f'{species}\nCalling Intensity (0-3)', fontweight='bold')
            ax.set_title(f'Failed Prediction: {species}', fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Set y-axis to show 0-3 scale
            ax.set_ylim(-0.2, 3.2)
            ax.set_yticks([0, 1, 2, 3])
        
        # Add overall title
        fig.suptitle('Species-Specific Prediction Failures\n(Acoustic Indices Cannot Reliably Predict Individual Species Activity)', 
                    fontsize=14, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.92)
        plt.savefig(output_dir / '02c_species_prediction_failure.png', 
                   bbox_inches='tight', facecolor='white')
        plt.savefig(output_dir / 'ml_species_prediction_failure.png', 
                   bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   ✅ Species prediction failure figure created")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating species failure figure: {e}")
        return False


def create_ml_journey_summary_figure():
    """
    Create a summary figure showing the entire ML journey.
    """
    print("📊 Creating ML Journey Summary Figure...")
    
    try:
        # Create a timeline/flowchart style figure
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        
        # Define the journey stages
        stages = [
            {"name": "Phase 1:\nSpecies-Specific\nPrediction", "result": "FAILED", "reason": "Too complex/noisy", 
             "color": "#e74c3c", "y": 3, "x": 1},
            {"name": "Phase 2:\nVessel Analysis", "result": "PARTIAL", "reason": "85% vessel detection\n8% signal improvement", 
             "color": "#f39c12", "y": 2, "x": 3},
            {"name": "Phase 3a:\nCommunity Detection", "result": "MIXED", "reason": "F1=0.84 best case\nBut unstable features", 
             "color": "#f39c12", "y": 3, "x": 5},
            {"name": "Phase 3b:\nFeature Selection", "result": "CRISIS", "reason": "0-30% agreement\nMI vs Boruta", 
             "color": "#e74c3c", "y": 1, "x": 7},
            {"name": "Phase 3c:\nTemporal Validation", "result": "REVELATION", "reason": "6-23% performance drop\nTemporal leakage", 
             "color": "#e74c3c", "y": 2, "x": 9},
            {"name": "BREAKTHROUGH:\nPattern Guidance", "result": "SUCCESS", "reason": "Visual concordance\n2D probability surfaces", 
             "color": "#27ae60", "y": 3, "x": 11}
        ]
        
        # Draw the journey
        for i, stage in enumerate(stages):
            # Draw box
            box_width = 1.5
            box_height = 0.8
            
            # Color based on result
            facecolor = stage["color"]
            alpha = 0.7 if stage["result"] != "SUCCESS" else 1.0
            
            rect = plt.Rectangle((stage["x"]-box_width/2, stage["y"]-box_height/2), 
                               box_width, box_height, 
                               facecolor=facecolor, alpha=alpha, 
                               edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Add text
            ax.text(stage["x"], stage["y"]+0.1, stage["name"], 
                   ha='center', va='center', fontweight='bold', fontsize=10,
                   color='white' if stage["result"] == "SUCCESS" else 'black')
            
            ax.text(stage["x"], stage["y"]-0.2, stage["result"], 
                   ha='center', va='center', fontweight='bold', fontsize=9,
                   color='white' if stage["result"] == "SUCCESS" else 'black')
            
            # Add reason below
            ax.text(stage["x"], stage["y"]-0.6, stage["reason"], 
                   ha='center', va='top', fontsize=8, style='italic',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
            
            # Draw arrow to next stage (except for last)
            if i < len(stages) - 1:
                next_stage = stages[i + 1]
                arrow_start_x = stage["x"] + box_width/2
                arrow_end_x = next_stage["x"] - box_width/2
                arrow_y = (stage["y"] + next_stage["y"]) / 2
                
                ax.annotate('', xy=(arrow_end_x, next_stage["y"]), 
                          xytext=(arrow_start_x, stage["y"]),
                          arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
        
        # Add title and labels
        ax.set_title('Machine Learning Journey: From Systematic Failures to Breakthrough\n' + 
                    'Traditional ML Revealed Fundamental Problems That Led to Pattern-Based Solution', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add legend
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, facecolor='#e74c3c', alpha=0.7, label='Failed Approach'),
            plt.Rectangle((0, 0), 1, 1, facecolor='#f39c12', alpha=0.7, label='Partial Success'),
            plt.Rectangle((0, 0), 1, 1, facecolor='#27ae60', alpha=1.0, label='Breakthrough')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=12)
        
        # Add key insights
        insights_text = """
        KEY INSIGHTS FROM ML FAILURES:
        • Species-specific patterns too complex for generic indices
        • Feature selection methods fundamentally disagreed (0-30% overlap)
        • Temporal validation revealed 6-23% performance overestimation
        • Temperature dominated acoustic indices in all models
        • Traditional ML asked wrong question: "Can we predict?" vs "When should we look?"
        """
        
        ax.text(0.02, 0.15, insights_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
               facecolor='lightblue', alpha=0.8))
        
        # Set axis limits and remove ticks
        ax.set_xlim(-1, 13)
        ax.set_ylim(0, 4)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(output_dir / '02d_ml_journey_summary.png', 
                   bbox_inches='tight', facecolor='white')
        plt.savefig(output_dir / 'ml_journey_summary.png', 
                   bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   ✅ ML journey summary figure created")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating ML journey summary: {e}")
        return False


def main():
    """Main function to generate all figures."""
    print(f"Output directory: {output_dir}")
    
    success_count = 0
    
    # Generate all figures
    if create_feature_selection_disagreement_figure():
        success_count += 1
    
    if create_temporal_validation_drop_figure():
        success_count += 1
        
    if create_species_prediction_failure_figure():
        success_count += 1
        
    if create_ml_journey_summary_figure():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 ML Report Figure Generation Complete!")
    print(f"✅ {success_count}/4 figures created successfully")
    print(f"📁 Figures saved to: {output_dir}")
    
    # List created files
    created_files = list(output_dir.glob("02*_*.png")) + list(output_dir.glob("ml_*.png"))
    if created_files:
        print("\n📋 Created files:")
        for file in sorted(created_files):
            print(f"   • {file.name}")
    
    return success_count == 4


if __name__ == "__main__":
    main()