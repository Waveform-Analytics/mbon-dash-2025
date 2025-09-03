"""
Principal Component Analysis for acoustic indices dimensionality reduction.
Reduces 56+ acoustic indices to interpretable principal components.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

class PCAAnalyzer:
    """Perform PCA on acoustic indices for dimensionality reduction."""
    
    def __init__(self, data_path: str):
        """Initialize with path to compiled indices data."""
        self.data_path = Path(data_path)
        self.data = None
        self.pca = None
        self.scaler = None
        self.pipeline = None
        self.indices = None
        self.pca_results = None
        
    def load_data(self):
        """Load compiled indices data."""
        logger.info(f"Loading data from {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            self.data = json.load(f)
        
        logger.info("Data loaded successfully")
        return self
    
    def extract_indices_dataframe(self, 
                                station: Optional[str] = None, 
                                year: Optional[str] = None, 
                                bandwidth: Optional[str] = None) -> pd.DataFrame:
        """Extract acoustic indices as DataFrame for analysis.
        
        Args:
            station: Specific station ('9M', '14M', '37M') or None for all
            year: Specific year ('2021') or None for all  
            bandwidth: Specific bandwidth ('FullBW', '8kHz') or None for all
            
        Returns:
            DataFrame with indices as columns, timestamps as index
        """
        if self.data is None:
            self.load_data()
            
        all_records = []
        
        # Iterate through stations
        stations = [station] if station else self.data['stations'].keys()
        
        for station_id in stations:
            if station_id not in self.data['stations']:
                continue
                
            years = [year] if year else self.data['stations'][station_id].keys()
            
            for year_id in years:
                if year_id not in self.data['stations'][station_id]:
                    continue
                    
                bandwidths = [bandwidth] if bandwidth else self.data['stations'][station_id][year_id].keys()
                
                for bandwidth_id in bandwidths:
                    if bandwidth_id not in self.data['stations'][station_id][year_id]:
                        continue
                        
                    records = self.data['stations'][station_id][year_id][bandwidth_id]['data']
                    
                    for record in records:
                        # Add metadata columns
                        record_with_meta = record.copy()
                        record_with_meta['station'] = station_id
                        record_with_meta['year'] = year_id  
                        record_with_meta['bandwidth'] = bandwidth_id
                        all_records.append(record_with_meta)
        
        if not all_records:
            raise ValueError("No data found for specified parameters")
            
        df = pd.DataFrame(all_records)
        
        # Convert Date to datetime and set as index
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Identify numeric index columns (exclude metadata)
        exclude_cols = ['Date', 'Filename', 'station', 'year', 'bandwidth']
        index_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Convert to numeric, handling any string values
        for col in index_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Drop columns with all NaN values
        df = df.dropna(axis=1, how='all')
        
        # Update index columns after dropping NaN columns
        index_cols = [col for col in df.columns if col not in exclude_cols]
        
        self.indices = index_cols
        logger.info(f"Extracted {len(index_cols)} indices from {len(df)} records")
        
        return df
    
    def fit_pca(self, df: pd.DataFrame, n_components: Optional[int] = None):
        """Fit PCA model on acoustic indices.
        
        Args:
            df: DataFrame with acoustic indices
            n_components: Number of components to keep (default: all)
        """
        # Get index columns only
        index_data = df[self.indices].copy()
        
        # Remove rows with any NaN values
        index_data = index_data.dropna()
        
        logger.info(f"Fitting PCA on {len(index_data)} samples with {len(self.indices)} features")
        
        # Create pipeline with scaling and PCA
        steps = [
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=n_components))
        ]
        
        self.pipeline = Pipeline(steps)
        
        # Fit the pipeline
        self.pipeline.fit(index_data)
        
        # Store individual components for easier access
        self.scaler = self.pipeline.named_steps['scaler']
        self.pca = self.pipeline.named_steps['pca']
        
        logger.info(f"PCA fitted with {self.pca.n_components_} components")
        
        return self
    
    def compute_pca_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute comprehensive PCA results.
        
        Args:
            df: DataFrame with acoustic indices
            
        Returns:
            Dictionary with PCA analysis results
        """
        if self.pipeline is None:
            raise ValueError("Must fit PCA model first using fit_pca()")
            
        # Get index data
        index_data = df[self.indices].copy()
        original_data = index_data.dropna()
        
        # Transform data
        transformed_data = self.pipeline.transform(original_data)
        
        # Calculate explained variance
        explained_variance_ratio = self.pca.explained_variance_ratio_
        cumulative_variance_ratio = np.cumsum(explained_variance_ratio)
        
        # Find number of components for 80% variance
        components_80 = np.argmax(cumulative_variance_ratio >= 0.8) + 1
        components_90 = np.argmax(cumulative_variance_ratio >= 0.9) + 1
        
        # Get component loadings
        loadings = pd.DataFrame(
            self.pca.components_.T,
            index=self.indices,
            columns=[f'PC{i+1}' for i in range(self.pca.n_components_)]
        )
        
        # Identify top contributors for each component
        top_loadings = {}
        for i in range(min(5, self.pca.n_components_)):  # Top 5 components
            pc_name = f'PC{i+1}'
            # Get absolute loadings and sort
            abs_loadings = loadings[pc_name].abs().sort_values(ascending=False)
            top_loadings[pc_name] = {
                'positive': loadings[pc_name].nlargest(5).to_dict(),
                'negative': loadings[pc_name].nsmallest(5).to_dict(),
                'top_contributors': abs_loadings.head(10).index.tolist()
            }
        
        self.pca_results = {
            'n_components': self.pca.n_components_,
            'n_features': len(self.indices),
            'n_samples': len(original_data),
            'explained_variance_ratio': explained_variance_ratio.tolist(),
            'cumulative_variance_ratio': cumulative_variance_ratio.tolist(),
            'components_for_80_percent': int(components_80),
            'components_for_90_percent': int(components_90),
            'loadings': loadings.round(4).to_dict(),
            'top_loadings': top_loadings,
            'feature_names': self.indices
        }
        
        logger.info(f"PCA analysis complete: {components_80} components explain 80% of variance")
        
        return self.pca_results
    
    def generate_scree_plot_data(self) -> List[Dict[str, Any]]:
        """Generate data for scree plot visualization.
        
        Returns:
            List of data points for scree plot
        """
        if self.pca_results is None:
            raise ValueError("Must compute PCA results first")
        
        scree_data = []
        for i, (explained_var, cumulative_var) in enumerate(
            zip(self.pca_results['explained_variance_ratio'], 
                self.pca_results['cumulative_variance_ratio'])
        ):
            scree_data.append({
                'component': f'PC{i+1}',
                'component_number': i + 1,
                'explained_variance': round(explained_var * 100, 2),  # Convert to percentage
                'cumulative_variance': round(cumulative_var * 100, 2)  # Convert to percentage
            })
        
        return scree_data
    
    def generate_loadings_heatmap_data(self, top_components: int = 5) -> Dict[str, Any]:
        """Generate data for loadings heatmap visualization.
        
        Args:
            top_components: Number of top components to include
            
        Returns:
            Dictionary with heatmap data and metadata
        """
        if self.pca_results is None:
            raise ValueError("Must compute PCA results first")
        
        loadings_df = pd.DataFrame(self.pca_results['loadings'])
        
        # Select top components
        top_components = min(top_components, len(loadings_df.columns))
        selected_components = [f'PC{i+1}' for i in range(top_components)]
        
        # Get top contributing indices across all selected components
        all_abs_loadings = loadings_df[selected_components].abs()
        top_indices = all_abs_loadings.max(axis=1).nlargest(20).index.tolist()
        
        # Create heatmap data
        heatmap_data = []
        for index_name in top_indices:
            for component in selected_components:
                loading_value = loadings_df.loc[index_name, component]
                heatmap_data.append({
                    'index': index_name,
                    'component': component,
                    'loading': round(loading_value, 4),
                    'abs_loading': round(abs(loading_value), 4)
                })
        
        return {
            'data': heatmap_data,
            'indices': top_indices,
            'components': selected_components,
            'metadata': {
                'top_components': top_components,
                'top_indices_count': len(top_indices),
                'explained_variance': [
                    round(self.pca_results['explained_variance_ratio'][i] * 100, 2) 
                    for i in range(top_components)
                ]
            }
        }
    
    def generate_view_data(self) -> Dict[str, Any]:
        """Generate complete PCA view data for dashboard.
        
        Returns:
            Dictionary with all PCA analysis results for visualization
        """
        if self.pca_results is None:
            raise ValueError("Must compute PCA results first")
        
        return {
            'summary': {
                'total_indices': self.pca_results['n_features'],
                'total_samples': self.pca_results['n_samples'],
                'components_analyzed': self.pca_results['n_components'],
                'components_for_80_percent': self.pca_results['components_for_80_percent'],
                'components_for_90_percent': self.pca_results['components_for_90_percent'],
                'variance_explained_top_5': sum(self.pca_results['explained_variance_ratio'][:5]) * 100
            },
            'scree_plot': self.generate_scree_plot_data(),
            'loadings_heatmap': self.generate_loadings_heatmap_data(),
            'component_interpretation': {
                f'PC{i+1}': {
                    'explained_variance_percent': round(self.pca_results['explained_variance_ratio'][i] * 100, 2),
                    'top_positive_loadings': list(self.pca_results['top_loadings'][f'PC{i+1}']['positive'].keys())[:3],
                    'top_negative_loadings': list(self.pca_results['top_loadings'][f'PC{i+1}']['negative'].keys())[:3],
                    'interpretation': self._interpret_component(i)
                }
                for i in range(min(5, self.pca_results['n_components']))
            },
            'metadata': {
                'analysis_date': pd.Timestamp.now().isoformat(),
                'method': 'sklearn.decomposition.PCA',
                'preprocessing': 'StandardScaler',
                'feature_selection': 'None (used all valid indices)'
            }
        }
    
    def _interpret_component(self, component_idx: int) -> str:
        """Generate interpretation for a principal component.
        
        Args:
            component_idx: Index of the component (0-based)
            
        Returns:
            String interpretation of the component
        """
        if component_idx >= len(self.pca_results['top_loadings']):
            return "Component interpretation not available"
            
        pc_name = f'PC{component_idx + 1}'
        top_positive = list(self.pca_results['top_loadings'][pc_name]['positive'].keys())[:3]
        top_negative = list(self.pca_results['top_loadings'][pc_name]['negative'].keys())[:3]
        
        # Basic interpretation based on common acoustic indices
        interpretations = {
            0: "Likely represents overall acoustic activity and complexity",
            1: "May capture temporal vs. spectral characteristics",
            2: "Could represent anthropogenic vs. biological sounds",
            3: "Might distinguish frequency-specific acoustic features",
            4: "May represent seasonal or diel acoustic patterns"
        }
        
        base_interpretation = interpretations.get(component_idx, "Additional acoustic variation component")
        
        return f"{base_interpretation}. Strongly loaded by: {', '.join(top_positive[:2])}"