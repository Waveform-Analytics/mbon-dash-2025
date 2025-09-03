#!/usr/bin/env python3
"""
Generate correlation matrix view for the dashboard.
"""

import json
import logging
from pathlib import Path

from mbon_analysis.views.correlation_matrix import generate_correlation_matrix_view

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Generate correlation matrix view."""
    
    # Paths
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data"
    views_path = data_path / "views"
    
    logger.info("=" * 60)
    logger.info("MBON Correlation Matrix View Generation")
    logger.info("=" * 60)
    
    try:
        # Generate correlation matrix view
        view_data = generate_correlation_matrix_view(
            base_path=data_path,
            output_path=views_path,
            threshold=0.95,
            bandwidth='FullBW'  # Use full bandwidth for correlation analysis
        )
        
        if view_data:
            stats = view_data['statistics']
            logger.info("Generated correlation matrix view:")
            logger.info(f"  - Total indices: {stats['total_indices']}")
            logger.info(f"  - High correlation pairs (|r| >= 0.95): {stats['high_correlation_pairs']}")
            logger.info(f"  - Suggested indices to remove: {stats['suggested_removals']}")
            logger.info(f"  - Mean |correlation|: {stats['mean_abs_correlation']:.3f}")
            logger.info(f"  - Max off-diagonal |correlation|: {stats['max_off_diagonal_correlation']:.3f}")
        
        logger.info("=" * 60)
        logger.info("Correlation matrix view generation completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error generating correlation matrix view: {e}")
        raise

if __name__ == "__main__":
    main()