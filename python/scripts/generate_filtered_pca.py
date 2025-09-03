#!/usr/bin/env python
"""
Generate PCA analysis with correlation-based filtering.
This script first removes highly correlated indices before running PCA.
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from mbon_analysis.analysis.pca_analysis import PCAAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def filter_correlated_indices(df: pd.DataFrame, threshold: float = 0.95) -> list:
    """
    Remove highly correlated indices to reduce redundancy.
    
    Args:
        df: DataFrame with indices as columns
        threshold: Correlation threshold for removal
        
    Returns:
        List of indices to keep
    """
    # Calculate correlation matrix
    corr_matrix = df.corr().abs()
    
    # Create a mask for the upper triangle
    upper_tri = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    
    # Find indices to drop
    to_drop = set()
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if corr_matrix.iloc[i, j] >= threshold:
                # Drop the column with more overall correlations
                col_i = corr_matrix.columns[i]
                col_j = corr_matrix.columns[j]
                
                # Count high correlations for each
                high_corr_i = (corr_matrix[col_i] >= threshold).sum()
                high_corr_j = (corr_matrix[col_j] >= threshold).sum()
                
                # Drop the one with more high correlations
                if high_corr_i > high_corr_j:
                    to_drop.add(col_i)
                else:
                    to_drop.add(col_j)
    
    # Return indices to keep
    indices_to_keep = [col for col in df.columns if col not in to_drop]
    
    logger.info(f"Removed {len(to_drop)} highly correlated indices (threshold={threshold})")
    logger.info(f"Keeping {len(indices_to_keep)} indices for PCA")
    
    return indices_to_keep


def main():
    """Run filtered PCA analysis."""
    
    # Paths
    data_root = Path(__file__).parent.parent / "data"
    data_file = data_root / "processed" / "compiled_indices_even_hours.json"
    
    if not data_file.exists():
        data_file = data_root / "processed" / "compiled_indices.json"
    
    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        return
    
    # Configuration
    bandwidth = 'FullBW'
    correlation_threshold = 0.95
    n_components = 20
    
    logger.info("=" * 60)
    logger.info("FILTERED PCA ANALYSIS")
    logger.info("=" * 60)
    
    # Load and prepare data
    logger.info(f"Loading data from {data_file}")
    analyzer = PCAAnalyzer(str(data_file))
    analyzer.load_data()
    
    # Extract dataframe
    df = analyzer.extract_indices_dataframe(
        station=None,  # Use all stations
        year=None,     # Use all years
        bandwidth=bandwidth
    )
    
    # Get numeric columns only (exclude metadata)
    exclude_cols = ['Date', 'Filename', 'station', 'year', 'bandwidth']
    index_cols = [col for col in df.columns if col not in exclude_cols]
    
    logger.info(f"Original indices: {len(index_cols)}")
    
    # Filter highly correlated indices
    indices_df = df[index_cols].dropna()
    filtered_indices = filter_correlated_indices(indices_df, threshold=correlation_threshold)
    
    # Create new dataframe with filtered indices
    filtered_df = df[exclude_cols + filtered_indices].copy()
    
    # Update analyzer's indices list
    analyzer.indices = filtered_indices
    
    # Fit PCA on filtered data
    logger.info("\nFitting PCA on filtered indices...")
    analyzer.fit_pca(filtered_df, n_components=n_components)
    
    # Compute results
    analyzer.compute_pca_results(filtered_df)
    
    # Generate view data
    view_data = analyzer.generate_view_data()
    
    # Print results comparison
    logger.info("\n" + "=" * 60)
    logger.info("RESULTS COMPARISON")
    logger.info("=" * 60)
    
    logger.info("\nOriginal PCA (59 indices):")
    logger.info("- PC1: 11.83% variance")
    logger.info("- Top 5: 22.34% variance")
    logger.info("- Top 20: ~50% variance")
    logger.info("- For 80%: Would need ~40+ components")
    
    logger.info(f"\nFiltered PCA ({len(filtered_indices)} indices):")
    scree_data = view_data['scree_plot']
    if scree_data:
        logger.info(f"- PC1: {scree_data[0]['explained_variance']}% variance")
        if len(scree_data) >= 5:
            top5_variance = sum(s['explained_variance'] for s in scree_data[:5])
            logger.info(f"- Top 5: {top5_variance:.2f}% variance")
        if len(scree_data) >= 10:
            top10_variance = sum(s['explained_variance'] for s in scree_data[:10])
            logger.info(f"- Top 10: {top10_variance:.2f}% variance")
        
    components_80 = view_data['summary']['components_for_80_percent']
    components_90 = view_data['summary']['components_for_90_percent']
    logger.info(f"- For 80%: {components_80} components")
    logger.info(f"- For 90%: {components_90} components")
    
    # Save results
    output_file = data_root / "views" / "pca_analysis_filtered.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(view_data, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")
    
    # Print interpretation
    logger.info("\n" + "=" * 60)
    logger.info("INTERPRETATION")
    logger.info("=" * 60)
    
    if components_80 <= 10:
        logger.info("✓ Good news! With correlation filtering, PCA is much more effective.")
        logger.info("  You can now work with a manageable number of components.")
    else:
        logger.info("⚠ Even with filtering, the data remains highly dimensional.")
        logger.info("  Consider using Random Forest or other ML methods that handle")
        logger.info("  high-dimensional data naturally.")
    
    # Identify key indices from PC1
    if 'component_interpretation' in view_data:
        pc1_info = view_data['component_interpretation'].get('PC1', {})
        if pc1_info:
            logger.info("\nPC1 Top Contributors (most important indices):")
            for idx in pc1_info.get('top_positive_loadings', [])[:3]:
                logger.info(f"  + {idx}")
            for idx in pc1_info.get('top_negative_loadings', [])[:3]:
                logger.info(f"  - {idx}")


if __name__ == "__main__":
    main()