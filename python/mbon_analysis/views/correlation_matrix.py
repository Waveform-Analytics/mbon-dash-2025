"""Correlation matrix view generator."""

from typing import Dict, Any
import json
import logging

from .base import BaseViewGenerator
from ..analysis.correlation import CorrelationAnalyzer

logger = logging.getLogger(__name__)


class CorrelationMatrixViewGenerator(BaseViewGenerator):
    """Generate correlation_matrix.json view with acoustic indices correlation analysis."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate correlation matrix view data.
        
        Returns:
            Dictionary with correlation matrix data optimized for dashboard
        """
        
        # Default to even hours data for alignment with detection data
        data_file = self.data_root / "processed" / "compiled_indices_even_hours.json"
        
        if not data_file.exists():
            # Fallback to regular compiled data
            data_file = self.data_root / "processed" / "compiled_indices.json"
            
        if not data_file.exists():
            raise FileNotFoundError(f"No compiled indices data found. Expected at {data_file}")
        
        # Configuration
        threshold = 0.95
        bandwidth = 'FullBW'  # Use full bandwidth for correlation analysis
        
        logger.info(f"Generating correlation matrix from {data_file}")
        
        # Create analyzer and load data
        analyzer = CorrelationAnalyzer(str(data_file))
        analyzer.load_data()
        
        # Extract data with bandwidth filtering  
        df = analyzer.extract_indices_dataframe(
            station=None,  # Use all stations
            year=None,     # Use all years
            bandwidth=bandwidth
        )
        
        # Compute correlation matrix
        analyzer.compute_correlation_matrix(df, method='pearson')
        
        # Generate view data
        view_data = analyzer.generate_view_data(threshold)
        
        logger.info(f"Generated correlation matrix: {view_data['statistics']['total_indices']} indices, "
                   f"{view_data['statistics']['high_correlation_pairs']} high correlations")
        
        return view_data