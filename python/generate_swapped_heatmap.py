#!/usr/bin/env python3

import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

from scripts.exploratory.explore_05_diel_patterns import DielPatternAnalyzer

def main():
    # Initialize analyzer
    analyzer = DielPatternAnalyzer(repo_root / "data")
    
    # Load data
    print("Loading data...")
    if not analyzer.load_data(station='14M', year=2021):
        print("Failed to load data")
        return
    
    # Create output directory
    output_dir = Path.cwd() / "analysis_results" / "diel_patterns"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate weekly heatmaps with swapped axes
    print("Creating weekly heatmaps with swapped axes...")
    species_list = ['Spotted seatrout', 'Silver perch', 'Oyster toadfish boat whistle']
    index_list = ['Hf', 'ACI', 'BI']
    
    # Filter to available species and indices
    species_list = [sp for sp in species_list if sp in analyzer.detections.columns]
    index_list = [idx for idx in index_list if idx in analyzer.acoustic_indices.columns]
    
    heatmap_path = output_dir / "weekly_hourly_heatmaps_swapped.png"
    fig = analyzer.plot_weekly_heatmaps(species_list, index_list, save_path=str(heatmap_path))
    plt.close(fig)
    
    print(f"Saved: {heatmap_path}")

if __name__ == "__main__":
    main()