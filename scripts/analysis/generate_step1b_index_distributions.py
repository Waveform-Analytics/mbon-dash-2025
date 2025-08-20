#!/usr/bin/env python3
"""
Generate Step 1B: Index Distribution & Quality Check visualization data.

This script creates comprehensive distribution analysis of all acoustic indices:
- Small multiples histograms for each index
- Quality metrics (skewness, outliers, zero percentages)
- Station-specific distribution differences
- Data quality flags and recommendations

Purpose: Quality control before analysis - identify problematic indices.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy import stats
import sys

# scipy will be imported locally in generate_density_data function if needed

def safe_float(value, default=0.0):
    """Convert value to float, handling NaN and inf values."""
    try:
        result = float(value)
        return result if np.isfinite(result) else default
    except:
        return default

sys.path.append(str(Path(__file__).parent.parent.parent))

def load_all_acoustic_indices():
    """Load all available acoustic indices files."""
    base_dir = Path(__file__).parent.parent.parent / "data" / "cdn" / "raw-data" / "indices"
    
    # All available files
    available_files = [
        'Acoustic_Indices_9M_2021_FullBW_v2_Final.csv',
        'Acoustic_Indices_14M_2021_FullBW_v2_Final.csv',
        'Acoustic_Indices_9M_2021_8kHz_v2_Final.csv',
        'Acoustic_Indices_14M_2021_8kHz_v2_Final.csv'
    ]
    
    datasets = {}
    all_indices = set()
    
    for filename in available_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"  Loading {filename}")
            df = pd.read_csv(filepath)
            
            # Parse metadata from filename
            parts = filename.split('_')
            station = parts[2]  # e.g., "9M"
            bandwidth = parts[4]  # e.g., "FullBW" or "8kHz"
            
            # Get numeric columns (acoustic indices)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            exclude_cols = ['Date', 'datetime', 'year', 'month', 'day', 'hour']
            indices = [col for col in numeric_cols if col not in exclude_cols]
            
            all_indices.update(indices)
            
            key = f"{station}_{bandwidth}"
            datasets[key] = {
                'data': df,
                'station': station,
                'bandwidth': bandwidth,
                'filename': filename,
                'indices': indices,
                'n_records': len(df)
            }
            
            print(f"    • {len(indices)} indices, {len(df):,} records")
        else:
            print(f"  Warning: {filename} not found")
    
    print(f"\nTotal unique indices across all datasets: {len(all_indices)}")
    return datasets, sorted(list(all_indices))

def calculate_distribution_stats(values):
    """Calculate comprehensive distribution statistics."""
    values_clean = values.dropna()
    
    if len(values_clean) == 0:
        return {
            'count': 0,
            'mean': 0,
            'std': 0,
            'min': 0,
            'max': 0,
            'skewness': 0,
            'kurtosis': 0,
            'zero_pct': 100,
            'missing_pct': 100,
            'outlier_pct': 0,
            'distribution_type': 'empty'
        }
    
    # Basic stats (using safe_float helper)
    mean_val = safe_float(values_clean.mean())
    std_val = safe_float(values_clean.std()) 
    min_val = safe_float(values_clean.min())
    max_val = safe_float(values_clean.max())
    
    # Shape statistics (using safe_float helper)
    skewness = safe_float(stats.skew(values_clean))
    kurt = safe_float(stats.kurtosis(values_clean))
    
    # Quality metrics (using safe_float helper)
    zero_pct = safe_float((values_clean == 0).sum() / len(values_clean) * 100)
    missing_pct = safe_float(values.isna().sum() / len(values) * 100)
    
    # Outlier detection (IQR method)
    Q1 = safe_float(values_clean.quantile(0.25))
    Q3 = safe_float(values_clean.quantile(0.75))
    IQR = Q3 - Q1
    if IQR > 0:
        outlier_mask = (values_clean < (Q1 - 1.5 * IQR)) | (values_clean > (Q3 + 1.5 * IQR))
        outlier_pct = safe_float(outlier_mask.sum() / len(values_clean) * 100)
    else:
        outlier_pct = 0.0
    
    # Distribution classification
    if abs(skewness) > 2:
        if skewness > 0:
            dist_type = 'highly_right_skewed'
        else:
            dist_type = 'highly_left_skewed'
    elif abs(skewness) > 1:
        if skewness > 0:
            dist_type = 'right_skewed'
        else:
            dist_type = 'left_skewed'
    elif zero_pct > 50:
        dist_type = 'zero_inflated'
    elif outlier_pct > 10:
        dist_type = 'outlier_heavy'
    else:
        dist_type = 'normal'
    
    return {
        'count': int(len(values_clean)),
        'mean': mean_val,
        'std': std_val,
        'min': min_val,
        'max': max_val,
        'skewness': skewness,
        'kurtosis': kurt,
        'zero_pct': zero_pct,
        'missing_pct': missing_pct,
        'outlier_pct': outlier_pct,
        'distribution_type': dist_type
    }

def generate_histogram_data(values, n_bins=30):
    """Generate histogram data for visualization."""
    values_clean = values.dropna()
    
    if len(values_clean) == 0:
        return {'bins': [], 'counts': [], 'bin_edges': []}
    
    try:
        counts, bin_edges = np.histogram(values_clean, bins=n_bins)
        
        # Convert to list of bin centers and counts
        bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(counts))]
        
        return {
            'bins': [float(x) for x in bin_centers],
            'counts': [int(x) for x in counts],
            'bin_edges': [float(x) for x in bin_edges]
        }
    except:
        return {'bins': [], 'counts': [], 'bin_edges': []}

def load_index_categories():
    """Load index category mappings from the updated categories file."""
    categories_file = Path(__file__).parent.parent.parent / "data" / "cdn" / "raw-data" / "Updated_Index_Categories_v2.csv"
    
    if not categories_file.exists():
        print(f"Warning: Categories file not found at {categories_file}")
        return {}
    
    try:
        categories_df = pd.read_csv(categories_file)
        print(f"Loaded {len(categories_df)} index categories from CSV")
        
        # Create mapping dictionary using Prefix -> Category
        category_mapping = {}
        for _, row in categories_df.iterrows():
            if 'Prefix' in row and 'Category' in row:
                # Use the Prefix as the key (this matches our index names)
                prefix = str(row['Prefix']).strip()
                category = str(row['Category']).strip()
                category_mapping[prefix] = category
        
        print(f"Created mapping for {len(category_mapping)} index prefixes")
        return category_mapping
    except Exception as e:
        print(f"Error loading categories: {e}")
        return {}

def categorize_index(index_name, category_mapping=None):
    """Categorize acoustic index using CSV mapping with fallback."""
    if category_mapping and index_name in category_mapping:
        return category_mapping[index_name]
    
    # Fallback categorization (should rarely be needed)
    fallback_categories = {
        'Diversity Indices': ['H_', 'RAOQ', 'Shannon', 'Renyi', 'ADI', 'AEI'],
        'Complexity Indices': ['ACI', 'NDSI'], 
        'Amplitude Indices': ['Bio', 'BI', 'rBA', 'Energy', 'Anthro'],
        'Temporal Indices': ['MEAN_t', 'VAR_t', 'SKEW_t', 'KURT_t', 'ZCR', 'LEQ', 'MEANt', 'VARt', 'SKEWt', 'KURTt', 'ACTt'],
        'Spectral Indices': ['MEAN_f', 'VAR_f', 'SKEW_f', 'KURT_f', 'LFC', 'MFC', 'HFC', 'NBPEAKS', 'MEANf', 'VARf', 'SKEWf', 'KURTf']
    }
    
    for cat_name, patterns in fallback_categories.items():
        if any(pattern in index_name for pattern in patterns):
            return cat_name
    return 'Other Indices'

def generate_density_data(values, n_points=100):
    """Generate probability density function data for visualization."""
    values_clean = values.dropna()
    
    if len(values_clean) < 3:
        return {'x': [], 'density': [], 'x_original': []}
    
    try:
        from scipy.stats import gaussian_kde
        
        # Create density estimate
        kde = gaussian_kde(values_clean)
        
        # Create normalized x-axis (0 to 1)
        min_val = values_clean.min()
        max_val = values_clean.max()
        
        if min_val == max_val:
            # Handle constant values
            return {
                'x': [0.5],  # Middle of normalized range
                'density': [1.0],  # Full probability at one point
                'x_original': [min_val]
            }
        
        # Original data range for density calculation
        x_original = np.linspace(min_val, max_val, n_points)
        density = kde(x_original)
        
        # Normalized x-axis (0-1)
        x_normalized = (x_original - min_val) / (max_val - min_val)
        
        return {
            'x': x_normalized.tolist(),
            'density': density.tolist(),
            'x_original': x_original.tolist()
        }
    except Exception as e:
        print(f"  Warning: Could not generate density for {values.name if hasattr(values, 'name') else 'values'}: {e}")
        # Fallback to histogram
        histogram_data = generate_histogram_data(values, n_bins=20)
        if histogram_data['bins']:
            min_val = min(histogram_data['bins'])
            max_val = max(histogram_data['bins'])
            if min_val != max_val:
                x_normalized = [(x - min_val) / (max_val - min_val) for x in histogram_data['bins']]
            else:
                x_normalized = [0.5] * len(histogram_data['bins'])
            return {
                'x': x_normalized,
                'density': histogram_data['counts'],
                'x_original': histogram_data['bins']
            }
        else:
            return {'x': [], 'density': [], 'x_original': []}

def analyze_index_distributions_by_bandwidth(datasets, all_indices):
    """Analyze distribution patterns for indices, separated by bandwidth."""
    
    print(f"\n🔍 Analyzing distributions for {len(all_indices)} indices by bandwidth...")
    
    # Load category mappings
    category_mapping = load_index_categories()
    
    # Group datasets by bandwidth
    bandwidth_groups = {}
    for dataset_key, dataset_info in datasets.items():
        bandwidth = dataset_info['bandwidth']
        if bandwidth not in bandwidth_groups:
            bandwidth_groups[bandwidth] = {}
        bandwidth_groups[bandwidth][dataset_key] = dataset_info
    
    print(f"  Found bandwidths: {list(bandwidth_groups.keys())}")
    
    # Process each bandwidth separately
    bandwidth_analyses = {}
    
    for bandwidth, bandwidth_datasets in bandwidth_groups.items():
        print(f"\n  Processing {bandwidth} bandwidth ({len(bandwidth_datasets)} datasets)...")
        
        index_analyses = []
        
        for i, index_name in enumerate(all_indices):
            if (i + 1) % 15 == 0:
                print(f"    {bandwidth}: {i + 1}/{len(all_indices)} indices processed")
            
            index_analysis = {
                'index': index_name,
                'category': categorize_index(index_name, category_mapping),
                'bandwidth': bandwidth,
                'datasets': {},
                'combined_stats': None,
                'quality_metrics': {}
            }
            
            # Collect data from datasets in this bandwidth
            all_values = []
            dataset_stats = {}
            
            for dataset_key, dataset_info in bandwidth_datasets.items():
                df = dataset_info['data']
                
                if index_name in df.columns:
                    values = df[index_name]
                    stats_dict = calculate_distribution_stats(values)
                    density_data = generate_density_data(values, n_points=50)
                    
                    dataset_stats[dataset_key] = {
                        'station': dataset_info['station'],
                        'bandwidth': dataset_info['bandwidth'],
                        'available': True,
                        'stats': stats_dict,
                        'density': density_data
                    }
                    
                    all_values.extend(values.dropna().tolist())
                else:
                    dataset_stats[dataset_key] = {
                        'station': dataset_info['station'],
                        'bandwidth': dataset_info['bandwidth'],
                        'available': False
                    }
            
            index_analysis['datasets'] = dataset_stats
            
            # Combined statistics across datasets in this bandwidth
            if all_values:
                combined_series = pd.Series(all_values)
                index_analysis['combined_stats'] = calculate_distribution_stats(combined_series)
                index_analysis['combined_density'] = generate_density_data(combined_series, n_points=100)
            
            # Quality metrics (raw values, no arbitrary thresholds)
            if index_analysis['combined_stats']:
                stats = index_analysis['combined_stats']
                index_analysis['quality_metrics'] = {
                    'missing_pct': stats['missing_pct'],
                    'zero_pct': stats['zero_pct'], 
                    'skewness_abs': abs(stats['skewness']),
                    'outlier_pct': stats['outlier_pct'],
                    'std': stats['std'],
                    'distribution_type': stats['distribution_type']
                }
            
            index_analyses.append(index_analysis)
        
        bandwidth_analyses[bandwidth] = index_analyses
        print(f"  ✅ {bandwidth} analysis complete: {len(index_analyses)} indices")
    
    print(f"✅ All bandwidth analyses complete")
    return bandwidth_analyses

def generate_summary_statistics_by_bandwidth(bandwidth_analyses):
    """Generate summary statistics about index distributions, by bandwidth."""
    
    summary_by_bandwidth = {}
    
    for bandwidth, index_analyses in bandwidth_analyses.items():
        total_indices = len(index_analyses)
        
        distribution_type_counts = {}
        category_counts = {}
        
        # Collect raw metrics for analysis
        skewness_values = []
        zero_pct_values = []
        missing_pct_values = []
        
        for analysis in index_analyses:
            # Category counts
            category = analysis['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Distribution types
            if analysis['combined_stats']:
                dist_type = analysis['combined_stats']['distribution_type']
                distribution_type_counts[dist_type] = distribution_type_counts.get(dist_type, 0) + 1
                
                # Collect raw metrics for summary
                skewness_values.append(abs(analysis['combined_stats']['skewness']))
                zero_pct_values.append(analysis['combined_stats']['zero_pct'])
                missing_pct_values.append(analysis['combined_stats']['missing_pct'])
        
        summary_by_bandwidth[bandwidth] = {
            'total_indices': total_indices,
            'distribution_type_counts': distribution_type_counts,
            'category_counts': category_counts,
            'raw_metrics_summary': {
                'skewness_median': np.median(skewness_values) if skewness_values else 0,
                'zero_pct_median': np.median(zero_pct_values) if zero_pct_values else 0,
                'missing_pct_median': np.median(missing_pct_values) if missing_pct_values else 0,
                'highly_skewed_count': sum(1 for s in skewness_values if s > 2),
                'zero_heavy_count': sum(1 for z in zero_pct_values if z > 25),
                'missing_heavy_count': sum(1 for m in missing_pct_values if m > 5)
            }
        }
    
    return summary_by_bandwidth

def main():
    """Generate Index Distribution & Quality Check visualization data."""
    
    print("🔍 Generating Index Distribution & Quality Check Analysis")
    print("=" * 60)
    
    print("\n📊 Loading acoustic indices datasets...")
    datasets, all_indices = load_all_acoustic_indices()
    
    print("\n📈 Analyzing index distributions by bandwidth...")
    bandwidth_analyses = analyze_index_distributions_by_bandwidth(datasets, all_indices)
    
    print("\n📋 Generating summary statistics by bandwidth...")
    summary_stats_by_bandwidth = generate_summary_statistics_by_bandwidth(bandwidth_analyses)
    
    # Prepare output data with bandwidth separation
    output_data = {
        'index_distributions_by_bandwidth': bandwidth_analyses,
        'summary_stats_by_bandwidth': summary_stats_by_bandwidth,
        'available_bandwidths': list(bandwidth_analyses.keys()),
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'description': 'Distribution analysis and quality assessment of acoustic indices, separated by bandwidth',
            'purpose': 'Quality control before analysis - identify skewed distributions, visualize with normalized PDFs',
            'total_indices_analyzed': len(all_indices),
            'datasets_included': len(datasets),
            'bandwidths_analyzed': list(bandwidth_analyses.keys()),
            'visualization_type': 'probability_density_functions',
            'normalization': 'min_max_0_1_scaling'
        },
        'generated_at': datetime.now().isoformat()
    }
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / "data" / "cdn" / "processed"
    output_file = output_dir / "step1b_index_distributions.json"
    
    print(f"\n💾 Saving Index Distribution analysis to {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Index Distribution analysis complete!")
    
    for bandwidth in bandwidth_analyses.keys():
        summary = summary_stats_by_bandwidth[bandwidth]
        print(f"\n   📊 {bandwidth} Bandwidth:")
        print(f"      • Indices analyzed: {summary['total_indices']}")
        print(f"      • Categories: {', '.join(summary['category_counts'].keys())}")
        print(f"      • Highly skewed (>2): {summary['raw_metrics_summary']['highly_skewed_count']}")
        print(f"      • Zero-heavy (>25%): {summary['raw_metrics_summary']['zero_heavy_count']}")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Upload to CDN: npm run upload-cdn")
    print(f"   2. View visualization: Navigate to /explore/indices page")
    print(f"   3. File will be served from: NEXT_PUBLIC_DATA_URL/processed/{output_file.name}")
    print(f"   4. Visualization will show PDF curves with 0-1 normalized x-axis")

if __name__ == "__main__":
    main()