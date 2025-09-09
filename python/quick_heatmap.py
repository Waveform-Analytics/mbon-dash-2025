import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

from mbon_analysis.data.loaders import create_loader

def calculate_weekly_hourly_patterns(data, column):
    """Calculate hourly patterns for each week."""
    data[column] = pd.to_numeric(data[column], errors='coerce').fillna(0)
    
    # Pivot to create week x hour matrix
    weekly_hourly = data.pivot_table(
        values=column,
        index='week',
        columns='hour',
        aggfunc='mean',
        fill_value=0
    )
    
    return weekly_hourly

def main():
    # Load data
    loader = create_loader(repo_root / "data")
    
    # Load detection data
    detections = loader.load_detection_data('14M', 2021)
    detections['datetime'] = pd.to_datetime(detections['Date'])
    detections['hour'] = detections['datetime'].dt.hour
    detections['week'] = detections['datetime'].dt.isocalendar().week
    
    # Load acoustic indices
    acoustic_indices = loader.load_acoustic_indices('14M', 'FullBW')
    acoustic_indices['datetime'] = pd.to_datetime(acoustic_indices['Date'])
    acoustic_indices['hour'] = acoustic_indices['datetime'].dt.hour
    acoustic_indices['week'] = acoustic_indices['datetime'].dt.isocalendar().week
    
    # Create figure
    species_list = ['Spotted seatrout', 'Silver perch', 'Oyster toadfish boat whistle']
    index_list = ['Hf', 'ACI', 'BI']
    
    # Filter to available
    species_list = [sp for sp in species_list if sp in detections.columns]
    index_list = [idx for idx in index_list if idx in acoustic_indices.columns]
    
    fig, axes = plt.subplots(len(species_list) + len(index_list), 1, 
                            figsize=(20, 4 * (len(species_list) + len(index_list))))
    
    plot_idx = 0
    
    # Plot species heatmaps  
    for species in species_list:
        ax = axes[plot_idx]
        
        weekly_hourly = calculate_weekly_hourly_patterns(detections, species)
        weekly_hourly_T = weekly_hourly.T  # Transpose so weeks on x-axis
        
        sns.heatmap(weekly_hourly_T, 
                   cmap='YlOrRd',
                   ax=ax,
                   cbar_kws={'label': 'Detection Intensity'},
                   xticklabels=True,
                   yticklabels=True)
        
        ax.set_xlabel('Week of Year', fontsize=11)
        ax.set_ylabel('Hour of Day', fontsize=11)
        ax.set_title(f'{species} - Weekly Diel Patterns', fontsize=12)
        
        # Add horizontal lines for day/night transitions
        ax.axhline(y=6, color='yellow', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=18, color='navy', linestyle='--', alpha=0.7, linewidth=1)
        
        # Invert y-axis so 0 hour is at top
        ax.invert_yaxis()
        
        plot_idx += 1
    
    # Plot index heatmaps
    for index in index_list:
        ax = axes[plot_idx]
        
        weekly_hourly = calculate_weekly_hourly_patterns(acoustic_indices, index)
        weekly_hourly_T = weekly_hourly.T  # Transpose so weeks on x-axis
        
        sns.heatmap(weekly_hourly_T,
                   cmap='viridis',
                   ax=ax,
                   cbar_kws={'label': f'{index} Value'},
                   xticklabels=True,
                   yticklabels=True)
        
        ax.set_xlabel('Week of Year', fontsize=11)
        ax.set_ylabel('Hour of Day', fontsize=11)
        ax.set_title(f'{index} Index - Weekly Diel Patterns', fontsize=12)
        
        # Add horizontal lines for day/night transitions
        ax.axhline(y=6, color='yellow', linestyle='--', alpha=0.7, linewidth=1)
        ax.axhline(y=18, color='navy', linestyle='--', alpha=0.7, linewidth=1)
        
        # Invert y-axis so 0 hour is at top
        ax.invert_yaxis()
        
        plot_idx += 1
    
    plt.suptitle('Weekly Evolution of Daily Activity Patterns (Swapped Axes)', 
                 fontsize=14, y=0.995)
    plt.tight_layout()
    
    # Save
    output_dir = Path.cwd() / "analysis_results" / "diel_patterns"
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / "weekly_hourly_heatmaps_swapped.png"
    
    fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {save_path}")
    plt.close(fig)

if __name__ == "__main__":
    main()