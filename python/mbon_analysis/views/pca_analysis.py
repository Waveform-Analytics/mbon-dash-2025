"""PCA analysis view generator."""

from typing import Dict, Any
import json
import logging

from .base import BaseViewGenerator
from ..analysis.pca_analysis import PCAAnalyzer

logger = logging.getLogger(__name__)


class PCAAnalysisViewGenerator(BaseViewGenerator):
    """Generate pca_analysis.json view with principal component analysis results."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate PCA analysis view data.
        
        Returns:
            Dictionary with PCA analysis data optimized for dashboard
        """
        
        # Default to even hours data for alignment with detection data
        data_file = self.data_root / "processed" / "compiled_indices_even_hours.json"
        
        if not data_file.exists():
            # Fallback to regular compiled data
            data_file = self.data_root / "processed" / "compiled_indices.json"
            
        if not data_file.exists():
            raise FileNotFoundError(f"No compiled indices data found. Expected at {data_file}")
        
        # Configuration
        bandwidth = 'FullBW'  # Use full bandwidth for PCA analysis
        n_components = 20     # Analyze top 20 components (more than needed for viz)
        
        logger.info(f"Generating PCA analysis from {data_file}")
        
        # Create analyzer and load data
        analyzer = PCAAnalyzer(str(data_file))
        analyzer.load_data()
        
        # Extract data with bandwidth filtering  
        df = analyzer.extract_indices_dataframe(
            station=None,  # Use all stations
            year=None,     # Use all years
            bandwidth=bandwidth
        )
        
        # Fit PCA model
        analyzer.fit_pca(df, n_components=n_components)
        
        # Compute PCA results
        analyzer.compute_pca_results(df)
        
        # Generate view data
        view_data = analyzer.generate_view_data()
        
        logger.info(f"Generated PCA analysis: {view_data['summary']['total_indices']} indices → "
                   f"{view_data['summary']['components_for_80_percent']} components (80% variance)")
        
        return view_data