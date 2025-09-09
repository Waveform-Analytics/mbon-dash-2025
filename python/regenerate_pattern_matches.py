#!/usr/bin/env python3

import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
repo_root = project_root.parent

# Execute the main script to get the analyzer class
exec(open('scripts/exploratory/explore-06-pattern-similarity.py').read(), globals())

def main():
    # Initialize analyzer
    analyzer = PatternSimilarityAnalyzer(repo_root / "data")
    
    # Load data
    print("Loading data...")
    analyzer.load_data(station='14M', year=2021)
    
    # Analyze similarities
    print("Calculating pattern similarities...")
    analyzer.analyze_all_similarities()
    
    # Create output directory
    output_dir = Path.cwd() / "analysis_results" / "pattern_similarity"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Regenerate top matches with fixed hour axis
    print("Creating corrected top pattern matches visualization...")
    matches_path = output_dir / "top_pattern_matches_fixed.png"
    fig = analyzer.plot_top_matches(n_top=8, save_path=str(matches_path))
    plt.close(fig)
    
    print(f"Saved: {matches_path}")

if __name__ == "__main__":
    main()