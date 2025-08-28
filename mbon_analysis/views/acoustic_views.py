"""
Acoustic summary view generation for MBON dashboard.

This module creates optimized acoustic data views for interactive visualization,
focusing on PCA analysis, index categorization, and research-relevant summaries.

Key optimizations:
- PCA dimensionality reduction (56+ indices → 3-5 components)
- Index categorization by research domains
- Temporal aggregation to reduce data size
- Research question alignment (biodiversity prediction focus)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Scientific computing imports for PCA
try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


def generate_acoustic_summary(processed_data_dir) -> dict:
    """
    Generate acoustic summary optimized for interactive visualization.
    
    This function processes large acoustic indices files (159MB) into
    compact summaries (~50KB) suitable for dashboard consumption.
    
    Args:
        processed_data_dir: Path to processed data directory
        
    Returns:
        Dict containing:
        - acoustic_summary: Temporal and station aggregations
        - pca_analysis: PCA components and loadings
        - index_categories: Indices grouped by research domain
        - metadata: Generation info and data sources
    """
    
    # Load acoustic indices data
    processed_data_dir = Path(processed_data_dir)
    acoustic_file = processed_data_dir / "acoustic_indices.json"
    
    if not acoustic_file.exists():
        # Return minimal structure if no data available
        return _create_minimal_structure()
    
    try:
        with open(acoustic_file, 'r') as f:
            acoustic_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return _create_minimal_structure()
    
    # Handle different data structures
    if isinstance(acoustic_data, list):
        # Data is already a list of records
        indices_records = acoustic_data
    elif isinstance(acoustic_data, dict) and 'acoustic_indices' in acoustic_data:
        # Data is wrapped in an object
        indices_records = acoustic_data['acoustic_indices']
    else:
        return _create_minimal_structure()
    if not indices_records:
        return _create_minimal_structure()
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(indices_records)
    
    # Generate each component
    acoustic_summary = _generate_temporal_summary(df)
    pca_analysis = _generate_pca_analysis(df)
    index_categories = _generate_index_categories(df)
    metadata = _generate_metadata(df, processed_data_dir)
    
    return {
        'acoustic_summary': acoustic_summary,
        'pca_analysis': pca_analysis, 
        'index_categories': index_categories,
        'metadata': metadata
    }


def _create_minimal_structure() -> dict:
    """Create minimal structure when no data is available."""
    return {
        'acoustic_summary': [],
        'pca_analysis': {
            'components': [],
            'explained_variance': [],
            'feature_loadings': {}
        },
        'index_categories': {},
        'metadata': {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'data_sources': ['acoustic_indices.json'],
            'total_indices': 0,
            'stations_included': [],
            'total_records_processed': 0,
            'generator': 'mbon_analysis.views.acoustic_views'
        }
    }


def _generate_temporal_summary(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate temporal aggregation summaries."""
    if df.empty:
        return []
    
    # Convert datetime column if it exists
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['year_month'] = df['datetime'].dt.to_period('M').astype(str)
    
    summary_data = []
    
    # Station-level summaries
    if 'station' in df.columns:
        for station in df['station'].unique():
            station_data = df[df['station'] == station]
            
            # Calculate key acoustic metrics
            numeric_cols = station_data.select_dtypes(include=[np.number]).columns
            
            station_summary = {
                'station': station,
                'temporal_stats': {
                    'total_records': len(station_data),
                    'date_range': {
                        'start': station_data['datetime'].min().isoformat() if 'datetime' in df.columns else None,
                        'end': station_data['datetime'].max().isoformat() if 'datetime' in df.columns else None
                    }
                },
                'acoustic_metrics': {}
            }
            
            # Add key acoustic indices averages
            for col in numeric_cols:
                if col not in ['datetime']:
                    station_summary['acoustic_metrics'][col] = {
                        'mean': float(station_data[col].mean()) if not station_data[col].isna().all() else None,
                        'std': float(station_data[col].std()) if not station_data[col].isna().all() else None
                    }
            
            summary_data.append(station_summary)
    
    return summary_data


def _generate_pca_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate PCA analysis for dimensionality reduction."""
    pca_result = {
        'components': [],
        'explained_variance': [],
        'feature_loadings': {}
    }
    
    if not HAS_SKLEARN or df.empty:
        return pca_result
    
    # Get numeric columns (acoustic indices)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in ['datetime']]
    
    if len(numeric_cols) < 2:
        return pca_result
    
    # Prepare data for PCA
    pca_data = df[numeric_cols].dropna()
    
    if len(pca_data) < 2 or len(numeric_cols) < 2:
        return pca_result
    
    try:
        # Standardize the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pca_data)
        
        # Perform PCA (limit to 5 components for visualization)
        n_components = min(5, len(numeric_cols), len(pca_data))
        pca = PCA(n_components=n_components)
        pca.fit(scaled_data)
        
        # Extract results
        pca_result['components'] = [f'PC{i+1}' for i in range(n_components)]
        pca_result['explained_variance'] = pca.explained_variance_ratio_.tolist()
        
        # Feature loadings (which original indices contribute to each component)
        for i, component in enumerate(pca_result['components']):
            pca_result['feature_loadings'][component] = {
                col: float(pca.components_[i][j]) 
                for j, col in enumerate(numeric_cols)
            }
        
    except Exception:
        # Return empty structure if PCA fails
        pass
    
    return pca_result


def _generate_index_categories(df: pd.DataFrame) -> Dict[str, Any]:
    """Categorize acoustic indices by research domain."""
    if df.empty:
        return {}
    
    # Get available acoustic indices from data
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in ['datetime']]
    
    # Define index categories based on research documentation
    categories = {
        'temporal_domain': {
            'description': 'Time-based acoustic features',
            'indices': [col for col in numeric_cols if any(x in col.lower() for x in ['zcr', 'meant', 'vart', 'skewt', 'kurtt', 'leqt'])]
        },
        'frequency_domain': {
            'description': 'Frequency-based acoustic features', 
            'indices': [col for col in numeric_cols if any(x in col.lower() for x in ['meanf', 'varf', 'skewf', 'kurtf', 'nbpeaks'])]
        },
        'acoustic_complexity': {
            'description': 'Measures of acoustic complexity and structure',
            'indices': [col for col in numeric_cols if any(x in col.lower() for x in ['aci', 'ndsi', 'adi', 'aei'])]
        },
        'diversity_indices': {
            'description': 'Acoustic diversity and entropy measures',
            'indices': [col for col in numeric_cols if any(x in col.lower() for x in ['h_', 'havrda', 'renyi', 'shannon', 'raoq'])]
        },
        'bioacoustic': {
            'description': 'Biological vs anthropogenic sound separation',
            'indices': [col for col in numeric_cols if any(x in col.lower() for x in ['bioenergy', 'anthroenergy', 'bi', 'rba'])]
        },
        'spectral_coverage': {
            'description': 'Frequency coverage and bandwidth measures',
            'indices': [col for col in numeric_cols if any(x in col.lower() for x in ['lfc', 'mfc', 'hfc'])]
        }
    }
    
    # Remove empty categories
    categories = {k: v for k, v in categories.items() if v['indices']}
    
    # Add summary statistics for each category
    for category_name, category_data in categories.items():
        category_indices = category_data['indices']
        if category_indices:
            # Calculate category-level statistics
            category_df = df[category_indices]
            category_data['summary_stats'] = {
                'index_count': len(category_indices),
                'avg_correlation': float(category_df.corr().mean().mean()) if len(category_indices) > 1 else None,
                'data_availability': float((~category_df.isna()).mean().mean()) if not category_df.empty else 0.0
            }
    
    return categories


def _generate_metadata(df: pd.DataFrame, processed_data_dir: Path) -> Dict[str, Any]:
    """Generate metadata about the acoustic summary."""
    
    # Get unique stations
    stations = df['station'].unique().tolist() if 'station' in df.columns else []
    
    # Count total indices
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    total_indices = len([col for col in numeric_cols if col not in ['datetime']])
    
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'data_sources': ['acoustic_indices.json'],
        'total_indices': total_indices,
        'stations_included': stations,
        'total_records_processed': len(df),
        'date_range': {
            'start': df['datetime'].min().isoformat() if 'datetime' in df.columns and not df.empty else None,
            'end': df['datetime'].max().isoformat() if 'datetime' in df.columns and not df.empty else None
        },
        'generator': 'mbon_analysis.views.acoustic_views',
        'version': '1.0.0'
    }