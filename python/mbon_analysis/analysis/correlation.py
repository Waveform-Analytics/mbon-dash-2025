"""
Correlation analysis for acoustic indices.
Identifies redundant indices through correlation matrix analysis.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CorrelationAnalyzer:
    """Analyze correlations between acoustic indices for redundancy detection."""
    
    def __init__(self, data_path: str):
        """Initialize with path to compiled indices data."""
        self.data_path = Path(data_path)
        self.data = None
        self.correlation_matrix = None
        self.indices = None
        
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
            
        self.indices = index_cols
        logger.info(f"Extracted {len(index_cols)} indices from {len(df)} records")
        
        return df
    
    def compute_correlation_matrix(self, 
                                  df: Optional[pd.DataFrame] = None,
                                  method: str = 'pearson',
                                  min_periods: int = 100) -> pd.DataFrame:
        """Compute correlation matrix for acoustic indices.
        
        Args:
            df: DataFrame with indices, or None to use default extraction
            method: Correlation method ('pearson', 'spearman', 'kendall')
            min_periods: Minimum number of observations for correlation
            
        Returns:
            Correlation matrix DataFrame
        """
        if df is None:
            df = self.extract_indices_dataframe()
            
        # Get only numeric index columns
        exclude_cols = ['Date', 'Filename', 'station', 'year', 'bandwidth']
        index_cols = [col for col in df.columns if col not in exclude_cols and pd.api.types.is_numeric_dtype(df[col])]
        
        indices_df = df[index_cols].copy()
        
        # Remove columns with too many NaN values
        indices_df = indices_df.dropna(axis=1, thresh=min_periods)
        
        logger.info(f"Computing {method} correlation matrix for {len(indices_df.columns)} indices")
        
        self.correlation_matrix = indices_df.corr(method=method, min_periods=min_periods)
        self.indices = list(self.correlation_matrix.columns)
        
        return self.correlation_matrix
    
    def find_high_correlations(self, threshold: float = 0.95) -> List[Tuple[str, str, float]]:
        """Find pairs of indices with high correlation.
        
        Args:
            threshold: Correlation threshold (absolute value)
            
        Returns:
            List of (index1, index2, correlation) tuples
        """
        if self.correlation_matrix is None:
            self.compute_correlation_matrix()
            
        high_corrs = []
        
        # Get upper triangle (avoid duplicates and self-correlations)
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i + 1, len(self.correlation_matrix.columns)):
                idx1 = self.correlation_matrix.columns[i]
                idx2 = self.correlation_matrix.columns[j]
                corr = self.correlation_matrix.iloc[i, j]
                
                if not pd.isna(corr) and abs(corr) >= threshold:
                    high_corrs.append((idx1, idx2, corr))
        
        # Sort by absolute correlation descending
        high_corrs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        logger.info(f"Found {len(high_corrs)} pairs with |correlation| >= {threshold}")
        
        return high_corrs
    
    def suggest_indices_to_remove(self, threshold: float = 0.95) -> List[str]:
        """Suggest indices to remove based on high correlations.
        
        Uses a greedy approach: for each highly correlated pair,
        remove the index that appears in more high-correlation pairs.
        
        Args:
            threshold: Correlation threshold
            
        Returns:
            List of index names to consider removing
        """
        high_corrs = self.find_high_correlations(threshold)
        
        if not high_corrs:
            return []
        
        # Count how many high correlations each index participates in
        index_counts = {}
        for idx1, idx2, _ in high_corrs:
            index_counts[idx1] = index_counts.get(idx1, 0) + 1
            index_counts[idx2] = index_counts.get(idx2, 0) + 1
        
        # For each high correlation pair, suggest removing the one with more connections
        to_remove = set()
        processed_pairs = set()
        
        for idx1, idx2, corr in high_corrs:
            pair = tuple(sorted([idx1, idx2]))
            if pair in processed_pairs:
                continue
                
            processed_pairs.add(pair)
            
            # Remove the index with more high correlations
            if index_counts[idx1] > index_counts[idx2]:
                to_remove.add(idx1)
            elif index_counts[idx2] > index_counts[idx1]:
                to_remove.add(idx2)
            else:
                # If tied, remove the second one (arbitrary choice)
                to_remove.add(idx2)
        
        result = list(to_remove)
        logger.info(f"Suggesting to remove {len(result)} indices: {result[:5]}{'...' if len(result) > 5 else ''}")
        
        return result
    
    def generate_view_data(self, threshold: float = 0.95) -> Dict:
        """Generate view data for dashboard correlation matrix visualization.
        
        Args:
            threshold: Correlation threshold for highlighting
            
        Returns:
            Dictionary with correlation data for visualization
        """
        if self.correlation_matrix is None:
            self.compute_correlation_matrix()
            
        # Convert correlation matrix to list format for visualization
        indices = list(self.correlation_matrix.columns)
        
        # Create matrix data
        matrix_data = []
        for i, idx1 in enumerate(indices):
            for j, idx2 in enumerate(indices):
                corr = self.correlation_matrix.iloc[i, j]
                if not pd.isna(corr):
                    matrix_data.append({
                        'x': idx1,
                        'y': idx2,
                        'value': float(corr),
                        'x_index': i,
                        'y_index': j,
                        'is_high_corr': bool(abs(corr) >= threshold and i != j),
                        'is_diagonal': bool(i == j)
                    })
        
        # Get high correlation pairs
        high_corrs = self.find_high_correlations(threshold)
        high_corr_pairs = [
            {
                'index1': pair[0],
                'index2': pair[1], 
                'correlation': float(pair[2]),
                'abs_correlation': float(abs(pair[2]))
            }
            for pair in high_corrs
        ]
        
        # Get removal suggestions
        suggested_removals = self.suggest_indices_to_remove(threshold)
        
        # Basic statistics
        corr_values = self.correlation_matrix.values
        corr_values = corr_values[~np.isnan(corr_values)]
        off_diagonal = corr_values[np.abs(corr_values) < 0.999]  # Exclude perfect self-correlations
        
        stats = {
            'total_indices': len(indices),
            'total_pairs': len(indices) * (len(indices) - 1) // 2,
            'high_correlation_pairs': len(high_corrs),
            'suggested_removals': len(suggested_removals),
            'mean_abs_correlation': float(np.mean(np.abs(off_diagonal))),
            'max_off_diagonal_correlation': float(np.max(np.abs(off_diagonal))) if len(off_diagonal) > 0 else 0,
            'correlation_distribution': {
                'bins': np.histogram(off_diagonal, bins=20)[1].tolist(),
                'counts': np.histogram(off_diagonal, bins=20)[0].tolist()
            }
        }
        
        view_data = {
            'metadata': {
                'generated_at': pd.Timestamp.now().isoformat(),
                'description': 'Acoustic indices correlation matrix analysis',
                'threshold': threshold,
                'method': 'pearson',
                'data_source': str(self.data_path)
            },
            'indices': indices,
            'matrix_data': matrix_data,
            'high_correlations': high_corr_pairs,
            'suggested_removals': suggested_removals,
            'statistics': stats
        }
        
        logger.info(f"Generated view data: {stats['total_indices']} indices, {stats['high_correlation_pairs']} high correlations")
        
        return view_data


def create_correlation_view(data_path: str, 
                          output_path: str,
                          threshold: float = 0.95,
                          station: Optional[str] = None,
                          year: Optional[str] = None, 
                          bandwidth: Optional[str] = None):
    """Create correlation matrix view file.
    
    Args:
        data_path: Path to compiled indices JSON
        output_path: Path for output view file
        threshold: Correlation threshold for analysis
        station: Optional station filter
        year: Optional year filter  
        bandwidth: Optional bandwidth filter
    """
    analyzer = CorrelationAnalyzer(data_path)
    analyzer.load_data()
    
    # Extract data with optional filtering
    df = analyzer.extract_indices_dataframe(station, year, bandwidth)
    
    # Compute correlation matrix
    analyzer.compute_correlation_matrix(df, method='pearson')
    
    # Generate view data
    view_data = analyzer.generate_view_data(threshold)
    
    # Save view file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(view_data, f, indent=2)
        
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Saved correlation view to {output_path} ({file_size_mb:.1f} MB)")
    
    return view_data