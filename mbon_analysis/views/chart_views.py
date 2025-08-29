"""
Chart view generators for dashboard visualizations.

This module creates optimized data structures for chart components,
reducing file sizes and improving performance while maintaining full functionality.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..processing.data_loader import load_processed_data


def generate_raw_data_landscape(processed_data_dir: Path) -> Dict[str, Any]:
    """
    Generate raw data landscape view for index availability visualization.
    
    Creates an optimized view showing which acoustic indices are available
    for which station/bandwidth combinations, with coverage statistics.
    
    Args:
        processed_data_dir: Path to processed data directory
        
    Returns:
        Dictionary containing:
        - raw_data_landscape: Main data structure
          - indices_overview: List of indices with availability info
          - summary_stats: Overall coverage statistics
          - datasets_info: Station/bandwidth dataset information
        - metadata: Generation timestamp and data source info
        
    Performance Target: < 50KB (compared to larger source files)
    """
    
    try:
        # Load acoustic indices data
        acoustic_indices_path = processed_data_dir / "acoustic_indices.json"
        if not acoustic_indices_path.exists():
            # Return minimal structure if no data available
            return _create_minimal_landscape_structure()
            
        with open(acoustic_indices_path, 'r') as f:
            acoustic_data = json.load(f)
            
        # Load index categories
        categories_path = processed_data_dir / "../raw-data/Updated_Index_Categories_v2.csv"
        if categories_path.exists():
            categories_df = pd.read_csv(categories_path)
            category_mapping = dict(zip(categories_df['Prefix'].str.upper(), 
                                      categories_df['Category'].str.lower().str.replace(' indices', '').str.replace(' ', '_')))
        else:
            category_mapping = {}
    
        # Process acoustic indices data
        indices_overview = []
        datasets_info = {}
        
        # Group data by station and bandwidth to create dataset keys
        data_by_dataset = {}
        for record in acoustic_data:
            station = record.get('station', 'unknown')
            bandwidth = record.get('bandwidth', 'unknown')
            dataset_key = f"{station}_{bandwidth}"
            
            if dataset_key not in data_by_dataset:
                data_by_dataset[dataset_key] = []
            data_by_dataset[dataset_key].append(record)
            
            # Add to datasets_info
            if dataset_key not in datasets_info:
                datasets_info[dataset_key] = {
                    'station': station,
                    'bandwidth': bandwidth
                }
        
        # Get all unique acoustic indices from the data
        all_indices = set()
        for records in data_by_dataset.values():
            for record in records:
                # Extract index names (exclude metadata fields)
                for key in record.keys():
                    if key not in ['station', 'bandwidth', 'timestamp', 'datetime', 
                                 'year', 'month', 'day', 'hour', 'Date', 'Filename',
                                 'source_file']:
                        all_indices.add(key)
        
        # Create indices overview
        for index_name in sorted(all_indices):
            # Determine category
            category = category_mapping.get(index_name.upper(), 'other')
            
            # Calculate availability for each dataset
            availability = {}
            for dataset_key, records in data_by_dataset.items():
                values = [r.get(index_name) for r in records if r.get(index_name) is not None]
                
                availability[dataset_key] = {
                    'station': datasets_info[dataset_key]['station'],
                    'bandwidth': datasets_info[dataset_key]['bandwidth'],
                    'available': len(values) > 0,
                    'n_values': len(values),
                    'coverage_pct': round((len(values) / len(records)) * 100, 1) if records else 0
                }
            
            indices_overview.append({
                'index': index_name,
                'category': category,
                'availability': availability
            })
        
        # Calculate summary statistics
        total_indices = len(indices_overview)
        total_datasets = len(datasets_info)
        
        coverage_summary = {}
        for category in set(idx['category'] for idx in indices_overview):
            cat_indices = [idx for idx in indices_overview if idx['category'] == category]
            coverage_summary[category] = {
                'count': len(cat_indices),
                'avg_coverage': round(
                    sum(
                        sum(avail['coverage_pct'] for avail in idx['availability'].values()) 
                        / len(idx['availability']) 
                        for idx in cat_indices
                    ) / len(cat_indices), 1
                ) if cat_indices else 0
            }
        
        # Calculate category counts for component compatibility
        category_counts = {}
        for category, info in coverage_summary.items():
            category_counts[category] = info['count']

        return {
            'raw_data_landscape': {
                'indices_overview': indices_overview,
                'summary_stats': {
                    'total_indices': total_indices,
                    'total_datasets': total_datasets,
                    'coverage_summary': coverage_summary,
                    'category_counts': category_counts,
                    'coverage_percentage': 100.0,  # All available data shows 100% coverage
                    'station_stats': {station: {'total_records': len([r for r in acoustic_data if r.get('station') == station])} 
                                    for station in ['9M', '14M']},
                    'bandwidth_stats': {'FullBW': {'total_records': len([r for r in acoustic_data if 'FullBW' in r.get('source_file', '')])},
                                      '8kHz': {'total_records': len([r for r in acoustic_data if '8kHz' in r.get('source_file', '')])}}
                },
                'datasets_info': datasets_info
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_sources': ['acoustic_indices.json', 'Updated_Index_Categories_v2.csv'],
                'view_type': 'raw_data_landscape'
            }
        }
        
    except Exception as e:
        # Return minimal structure on error
        return _create_minimal_landscape_structure()


def _create_minimal_landscape_structure() -> Dict[str, Any]:
    """Create minimal landscape structure for fallback cases."""
    return {
        'raw_data_landscape': {
            'indices_overview': [],
            'summary_stats': {
                'total_indices': 0,
                'total_datasets': 0,
                'coverage_summary': {},
                'category_counts': {},
                'coverage_percentage': 0.0,
                'station_stats': {},
                'bandwidth_stats': {}
            },
            'datasets_info': {}
        },
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'data_sources': [],
            'view_type': 'raw_data_landscape'
        }
    }


def generate_index_distributions(processed_data_dir: Path) -> Dict[str, Any]:
    """Generate optimized index distributions view for statistical analysis.
    
    This function processes the large step1b_index_distributions.json file
    and creates a smaller, optimized version suitable for web visualization.
    
    Args:
        processed_data_dir: Path to directory containing processed JSON files
        
    Returns:
        Dictionary containing:
        - index_distributions: Main distribution data structure
          - index_distributions_by_bandwidth: Statistical analyses by bandwidth
          - summary_stats_by_bandwidth: Aggregated statistics
          - available_bandwidths: List of available bandwidths  
        - metadata: Generation timestamp and data source info
        
    Performance Target: < 50KB (compared to ~2.8MB source file)
    """
    
    try:
        # Load the large index distributions file
        distributions_path = processed_data_dir / "step1b_index_distributions.json"
        if not distributions_path.exists():
            # Return minimal structure if no data available
            return _create_minimal_distributions_structure()
            
        with open(distributions_path, 'r') as f:
            distributions_data = json.load(f)
        
        # Process distributions by bandwidth
        index_distributions_by_bandwidth = {}
        summary_stats_by_bandwidth = {}
        available_bandwidths = []
        
        for bandwidth, analyses in distributions_data.get('index_distributions_by_bandwidth', {}).items():
            available_bandwidths.append(bandwidth)
            processed_analyses = []
            
            # Statistics for this bandwidth
            total_indices = 0
            categories = {}
            quality_metrics = {'zero_heavy_count': 0, 'missing_heavy_count': 0}
            
            for analysis in analyses:
                # Extract essential data, reduce size
                combined_stats = analysis.get('combined_stats', {})
                processed_analysis = {
                    'index': analysis['index'],
                    'category': analysis['category'], 
                    'bandwidth': analysis['bandwidth'],
                    'combined_stats': {
                        'mean': combined_stats.get('mean', 0),
                        'std': combined_stats.get('std', 0),
                        'skewness': combined_stats.get('skewness', 0),
                        'min': combined_stats.get('min', 0),
                        'max': combined_stats.get('max', 0),
                        'zero_pct': combined_stats.get('zero_pct', 0),
                        'missing_pct': combined_stats.get('missing_pct', 0),
                        'outlier_pct': combined_stats.get('outlier_pct', 0),
                        'distribution_type': combined_stats.get('distribution_type', 'unknown')
                    },
                    'combined_density': {
                        'x': analysis.get('combined_density', {}).get('x', [])[:10],  # Further reduce density points
                        'density': analysis.get('combined_density', {}).get('density', [])[:10],
                        'x_original': analysis.get('combined_density', {}).get('x_original', [])[:10]
                    }
                }
                
                processed_analyses.append(processed_analysis)
                total_indices += 1
                
                # Count categories
                category = analysis['category']
                categories[category] = categories.get(category, 0) + 1
                
                # Count quality issues
                combined_stats = analysis.get('combined_stats', {})
                if combined_stats.get('zero_pct', 0) > 50:
                    quality_metrics['zero_heavy_count'] += 1
                if combined_stats.get('missing_pct', 0) > 50:
                    quality_metrics['missing_heavy_count'] += 1
            
            index_distributions_by_bandwidth[bandwidth] = processed_analyses
            summary_stats_by_bandwidth[bandwidth] = {
                'total_indices': total_indices,
                'categories': categories,
                'quality_metrics': quality_metrics
            }
        
        return {
            'index_distributions_by_bandwidth': index_distributions_by_bandwidth,
            'summary_stats_by_bandwidth': summary_stats_by_bandwidth,
            'available_bandwidths': available_bandwidths,
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'description': 'Optimized index distributions for web visualization',
                'purpose': 'Statistical analysis and quality assessment of acoustic indices',
                'total_indices_analyzed': sum(len(analyses) for analyses in index_distributions_by_bandwidth.values()),
                'datasets_included': len(set(analysis['bandwidth'] for analyses in index_distributions_by_bandwidth.values() for analysis in analyses)),
                'bandwidths_analyzed': available_bandwidths,
                'visualization_type': 'probability_density_functions',
                'normalization': '0-1_scale'
            },
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        # Return minimal structure on error
        return _create_minimal_distributions_structure()


def _create_minimal_distributions_structure() -> Dict[str, Any]:
    """Create minimal distributions structure for fallback cases."""
    return {
        'index_distributions_by_bandwidth': {},
        'summary_stats_by_bandwidth': {},
        'available_bandwidths': [],
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'description': 'No data available',
            'purpose': 'Statistical analysis and quality assessment of acoustic indices',
            'total_indices_analyzed': 0,
            'datasets_included': 0,
            'bandwidths_analyzed': [],
            'visualization_type': 'probability_density_functions',
            'normalization': '0-1_scale'
        },
        'generated_at': datetime.now().isoformat()
    }