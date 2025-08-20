#!/usr/bin/env python3
"""
Generate Step 1A: Raw Data Landscape visualization data.

This script creates a comprehensive overview showing all 60+ available acoustic indices
with their categories, data availability per station/time period, and missing data patterns.
The purpose is to show the starting complexity we need to reduce.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

def load_index_categories():
    """Load index category mappings from the updated categories file."""
    categories_file = Path(__file__).parent.parent.parent / "data" / "cdn" / "raw-data" / "Updated_Index_Categories_v2.csv"
    
    if not categories_file.exists():
        print(f"Warning: Categories file not found at {categories_file}")
        return {}
    
    try:
        categories_df = pd.read_csv(categories_file)
        print(f"Loaded {len(categories_df)} index categories")
        
        # Create mapping dictionary
        category_mapping = {}
        for _, row in categories_df.iterrows():
            if 'Index' in row and 'Category' in row:
                category_mapping[row['Index']] = row['Category']
        
        return category_mapping
    except Exception as e:
        print(f"Error loading categories: {e}")
        return {}

def categorize_index_fallback(index_name):
    """Fallback categorization based on index name patterns."""
    categories = {
        'diversity': ['H_', 'RAOQ', 'Shannon', 'Renyi'],
        'complexity': ['ACI', 'NDSI', 'ADI', 'AEI'],
        'bioacoustic': ['Bio', 'BI', 'rBA', 'Energy'],
        'temporal': ['MEAN_t', 'VAR_t', 'SKEW_t', 'KURT_t', 'ZCR', 'LEQ', 'MEANt', 'VARt', 'SKEWt', 'KURTt'],
        'frequency': ['MEAN_f', 'VAR_f', 'SKEW_f', 'KURT_f', 'LFC', 'MFC', 'HFC', 'NBPEAKS', 'MEANf', 'VARf', 'SKEWf', 'KURTf'],
        'anthropogenic': ['Anthro', 'anthropogenic']
    }
    
    for cat_name, patterns in categories.items():
        if any(pattern in index_name for pattern in patterns):
            return cat_name
    return 'other'

def load_all_acoustic_indices():
    """Load all available acoustic indices files to get complete picture."""
    base_dir = Path(__file__).parent.parent.parent / "data" / "cdn" / "raw-data" / "indices"
    
    # All available files
    available_files = [
        'Acoustic_Indices_9M_2021_FullBW_v2_Final.csv',
        'Acoustic_Indices_14M_2021_FullBW_v2_Final.csv',
        'Acoustic_Indices_9M_2021_8kHz_v2_Final.csv',
        'Acoustic_Indices_14M_2021_8kHz_v2_Final.csv'
    ]
    
    datasets = {}
    
    for filename in available_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"  Loading {filename}")
            df = pd.read_csv(filepath)
            
            # Parse metadata from filename
            parts = filename.split('_')
            station = parts[2]  # e.g., "9M"
            bandwidth = parts[4]  # e.g., "FullBW" or "8kHz"
            
            key = f"{station}_{bandwidth}"
            datasets[key] = {
                'data': df,
                'station': station,
                'bandwidth': bandwidth,
                'filename': filename,
                'n_records': len(df),
                'date_range': None  # Will calculate below
            }
            
            # Try to get date range
            if 'Date' in df.columns:
                try:
                    df['Date'] = pd.to_datetime(df['Date'])
                    datasets[key]['date_range'] = {
                        'start': df['Date'].min().isoformat(),
                        'end': df['Date'].max().isoformat(),
                        'days': (df['Date'].max() - df['Date'].min()).days
                    }
                except Exception as e:
                    print(f"    Warning: Could not parse dates in {filename}: {e}")
        else:
            print(f"  Warning: {filename} not found")
    
    print(f"Loaded {len(datasets)} acoustic indices datasets")
    return datasets

def analyze_index_coverage(datasets):
    """Analyze which indices are available in which datasets."""
    
    # Collect all indices across all datasets
    all_indices = set()
    dataset_indices = {}
    
    for key, dataset in datasets.items():
        df = dataset['data']
        
        # Get numeric columns (these are the acoustic indices)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['Date', 'datetime', 'year', 'month', 'day', 'hour']
        indices = [col for col in numeric_cols if col not in exclude_cols]
        
        all_indices.update(indices)
        dataset_indices[key] = indices
        
        print(f"  {key}: {len(indices)} indices")
    
    all_indices = sorted(list(all_indices))
    print(f"\nTotal unique indices found: {len(all_indices)}")
    
    # Load category mappings
    category_mapping = load_index_categories()
    
    # Create coverage matrix
    coverage_matrix = []
    for index in all_indices:
        
        # Determine category
        category = category_mapping.get(index, categorize_index_fallback(index))
        
        index_info = {
            'index': index,
            'category': category,
            'availability': {}
        }
        
        # Check availability in each dataset
        for key, indices in dataset_indices.items():
            station, bandwidth = key.split('_')
            available = index in indices
            
            index_info['availability'][key] = {
                'available': available,
                'station': station,
                'bandwidth': bandwidth
            }
            
            if available:
                # Get basic stats
                df = datasets[key]['data']
                if index in df.columns:
                    values = df[index].dropna()
                    if len(values) > 0:
                        index_info['availability'][key].update({
                            'n_values': int(len(values)),
                            'n_missing': int(df[index].isna().sum()),
                            'coverage_pct': float((len(values) / len(df)) * 100),
                            'mean': float(values.mean()),
                            'std': float(values.std()) if not pd.isna(values.std()) else 0.0,
                            'min': float(values.min()),
                            'max': float(values.max())
                        })
        
        coverage_matrix.append(index_info)
    
    return coverage_matrix, datasets

def calculate_summary_stats(coverage_matrix, datasets):
    """Calculate summary statistics about the data landscape."""
    
    # Category counts
    category_counts = {}
    for index_info in coverage_matrix:
        cat = index_info['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Availability statistics
    total_possible = len(coverage_matrix) * len(datasets)
    total_available = sum(
        1 for index_info in coverage_matrix 
        for key in index_info['availability'] 
        if index_info['availability'][key]['available']
    )
    
    # Station-specific stats
    station_stats = {}
    bandwidth_stats = {}
    
    for key, dataset in datasets.items():
        station, bandwidth = key.split('_')
        
        # Station stats
        if station not in station_stats:
            station_stats[station] = {
                'datasets': 0,
                'total_indices': 0,
                'total_records': 0,
                'bandwidths': set()
            }
        
        station_stats[station]['datasets'] += 1
        station_stats[station]['bandwidths'].add(bandwidth)
        station_stats[station]['total_records'] += dataset['n_records']
        
        # Count available indices for this dataset
        available_count = sum(
            1 for index_info in coverage_matrix 
            if index_info['availability'][key]['available']
        )
        station_stats[station]['total_indices'] += available_count
        
        # Bandwidth stats
        if bandwidth not in bandwidth_stats:
            bandwidth_stats[bandwidth] = {
                'datasets': 0,
                'total_records': 0,
                'stations': set()
            }
        
        bandwidth_stats[bandwidth]['datasets'] += 1
        bandwidth_stats[bandwidth]['total_records'] += dataset['n_records']
        bandwidth_stats[bandwidth]['stations'].add(station)
    
    # Convert sets to lists for JSON serialization
    for station in station_stats:
        station_stats[station]['bandwidths'] = sorted(list(station_stats[station]['bandwidths']))
    
    for bandwidth in bandwidth_stats:
        bandwidth_stats[bandwidth]['stations'] = sorted(list(bandwidth_stats[bandwidth]['stations']))
    
    summary = {
        'total_indices': len(coverage_matrix),
        'total_datasets': len(datasets),
        'category_counts': category_counts,
        'coverage_percentage': (total_available / total_possible) * 100,
        'station_stats': station_stats,
        'bandwidth_stats': bandwidth_stats,
        'missing_patterns': {
            'indices_missing_from_all': [
                index_info['index'] for index_info in coverage_matrix
                if not any(avail['available'] for avail in index_info['availability'].values())
            ],
            'indices_in_all': [
                index_info['index'] for index_info in coverage_matrix
                if all(avail['available'] for avail in index_info['availability'].values())
            ]
        }
    }
    
    return summary

def main():
    """Generate Raw Data Landscape visualization data."""
    
    print("🔍 Generating Step 1A: Raw Data Landscape")
    print("=" * 50)
    
    print("\n📊 Loading all acoustic indices datasets...")
    datasets = load_all_acoustic_indices()
    
    print("\n🔬 Analyzing index coverage and availability...")
    coverage_matrix, dataset_info = analyze_index_coverage(datasets)
    
    print("\n📈 Calculating summary statistics...")
    summary_stats = calculate_summary_stats(coverage_matrix, dataset_info)
    
    # Prepare output data
    output_data = {
        'raw_data_landscape': {
            'indices_overview': coverage_matrix,
            'datasets_info': {
                key: {
                    'station': info['station'],
                    'bandwidth': info['bandwidth'],
                    'filename': info['filename'],
                    'n_records': info['n_records'],
                    'date_range': info['date_range']
                }
                for key, info in dataset_info.items()
            },
            'summary_stats': summary_stats,
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'description': 'Complete overview of all acoustic indices showing data availability and missing patterns',
                'purpose': 'Show the starting complexity before dimensionality reduction'
            }
        },
        'generated_at': datetime.now().isoformat()
    }
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / "data" / "cdn" / "processed"
    output_file = output_dir / "step1a_raw_data_landscape.json"
    
    print(f"\n💾 Saving Raw Data Landscape to {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Raw Data Landscape analysis complete!")
    print(f"   • Total indices analyzed: {summary_stats['total_indices']}")
    print(f"   • Datasets included: {summary_stats['total_datasets']}")
    print(f"   • Overall coverage: {summary_stats['coverage_percentage']:.1f}%")
    print(f"   • Categories: {', '.join(summary_stats['category_counts'].keys())}")
    
    # Show some key insights
    print(f"\n📋 Key Insights:")
    print(f"   • Indices present in all datasets: {len(summary_stats['missing_patterns']['indices_in_all'])}")
    print(f"   • Indices missing from all datasets: {len(summary_stats['missing_patterns']['indices_missing_from_all'])}")
    
    for station, stats in summary_stats['station_stats'].items():
        print(f"   • Station {station}: {stats['total_records']:,} records across {len(stats['bandwidths'])} bandwidths")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Upload to CDN: npm run upload-cdn")
    print(f"   2. View visualization: Navigate to /acoustic-biodiversity page")
    print(f"   3. File will be served from: NEXT_PUBLIC_DATA_URL/processed/{output_file.name}")

if __name__ == "__main__":
    main()