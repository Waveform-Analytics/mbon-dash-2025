#!/usr/bin/env python3
"""Generate PCA analysis view for the dashboard."""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from mbon_analysis.views.pca_analysis import PCAAnalysisViewGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data():
    """Create minimal test data for PCA analysis if compiled data doesn't exist."""
    
    data_root = Path("data")
    processed_dir = data_root / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = processed_dir / "compiled_indices.json"
    
    if test_file.exists():
        logger.info("Compiled indices data already exists, skipping test data generation")
        return
    
    logger.info("Creating test acoustic indices data for PCA analysis")
    
    # Create synthetic acoustic indices data
    np.random.seed(42)  # For reproducibility
    
    # Common acoustic indices
    indices = [
        'ACI', 'ADI', 'AEI', 'BioEnergy', 'BI', 'NDSI', 'H_Havrda', 'H_Renyi',
        'MEANf', 'VARf', 'SKEWf', 'KURTf', 'MEANt', 'VARt', 'SKEWt', 'KURTt',
        'LFC', 'MFC', 'HFC', 'ACItf', 'ZCR', 'LEQt', 'NBPEAKS', 'AnthroEnergy',
        'rBA', 'SH', 'TH', 'ENR', 'BGN', 'SNR', 'ACIf1', 'ACIf2', 'ACIf3',
        'Hf', 'Ht', 'H', 'R', 'ROI_cover', 'C', 'Dvar', 'Dtf', 'Dff',
        'ROI_s', 'ROI_t', 'ROI_f', 'RAOQ', 'H_pairedShannon', 'SpectralCentroid',
        'SpectralVariance', 'SpectralSkewness', 'SpectralKurtosis', 'SpectralRolloff',
        'SpectralFlatness', 'ZeroCrossingRate', 'MFCC1', 'MFCC2', 'MFCC3', 'MFCC4', 'MFCC5'
    ]
    
    # Generate data for stations and time periods
    stations = ['9M', '14M']  # Use stations that typically have data
    years = ['2021']
    bandwidths = ['FullBW']
    
    # Create date range (simulate hourly data for a few months)
    date_range = pd.date_range('2021-01-01', '2021-03-31', freq='H')
    
    compiled_data = {
        'metadata': {
            'generated': pd.Timestamp.now().isoformat(),
            'description': 'Synthetic acoustic indices data for PCA analysis testing',
            'indices_count': len(indices),
            'stations': stations,
            'years': years,
            'bandwidths': bandwidths
        },
        'stations': {}
    }
    
    for station in stations:
        compiled_data['stations'][station] = {}
        
        for year in years:
            compiled_data['stations'][station][year] = {}
            
            for bandwidth in bandwidths:
                # Create realistic correlations between indices
                n_samples = len(date_range)
                n_indices = len(indices)
                
                # Create base patterns
                base_pattern = np.random.normal(0, 1, n_samples)
                seasonal_pattern = np.sin(2 * np.pi * np.arange(n_samples) / (24 * 30))  # Monthly cycle
                daily_pattern = np.sin(2 * np.pi * np.arange(n_samples) / 24)  # Daily cycle
                
                # Generate correlated indices with different patterns
                data_matrix = np.zeros((n_samples, n_indices))
                
                for i, idx_name in enumerate(indices):
                    # Different index families with different correlation patterns
                    if 'ACI' in idx_name or 'ADI' in idx_name:
                        # Acoustic complexity indices - correlated
                        data_matrix[:, i] = 0.7 * base_pattern + 0.3 * seasonal_pattern + np.random.normal(0, 0.3, n_samples)
                    elif 'MEAN' in idx_name or 'VAR' in idx_name:
                        # Spectral moment indices - correlated
                        data_matrix[:, i] = 0.6 * base_pattern - 0.4 * daily_pattern + np.random.normal(0, 0.4, n_samples)
                    elif 'Bio' in idx_name or 'Anthro' in idx_name:
                        # Energy indices
                        data_matrix[:, i] = 0.5 * seasonal_pattern + 0.5 * daily_pattern + np.random.normal(0, 0.5, n_samples)
                    elif 'H_' in idx_name or 'RAOQ' in idx_name:
                        # Diversity indices
                        data_matrix[:, i] = -0.4 * base_pattern + 0.6 * seasonal_pattern + np.random.normal(0, 0.4, n_samples)
                    else:
                        # Other indices
                        data_matrix[:, i] = np.random.normal(0, 1, n_samples)
                
                # Convert to positive values where appropriate
                for i, idx_name in enumerate(indices):
                    if idx_name in ['ACI', 'ADI', 'AEI', 'BioEnergy', 'AnthroEnergy', 'LEQt']:
                        data_matrix[:, i] = np.abs(data_matrix[:, i])
                    elif 'H_' in idx_name:
                        data_matrix[:, i] = np.clip(data_matrix[:, i], 0, None)
                
                # Create records
                records = []
                for j, timestamp in enumerate(date_range):
                    record = {
                        'Date': timestamp.isoformat(),
                        'Filename': f"synthetic_{timestamp.strftime('%Y%m%d_%H%M%S')}.wav"
                    }
                    
                    # Add index values
                    for i, idx_name in enumerate(indices):
                        record[idx_name] = round(float(data_matrix[j, i]), 4)
                    
                    records.append(record)
                
                compiled_data['stations'][station][year][bandwidth] = {
                    'metadata': {
                        'station': station,
                        'year': year,
                        'bandwidth': bandwidth,
                        'indices': indices,
                        'record_count': len(records)
                    },
                    'data': records
                }
    
    # Save test data
    with open(test_file, 'w') as f:
        json.dump(compiled_data, f, indent=2)
    
    logger.info(f"Created test data: {len(date_range)} samples × {len(indices)} indices × {len(stations)} stations")
    logger.info(f"Saved to: {test_file}")

def main():
    """Generate PCA analysis view."""
    
    # Create test data if needed
    create_test_data()
    
    # Generate PCA analysis view
    data_root = Path("data")
    generator = PCAAnalysisViewGenerator(data_root)
    
    try:
        result = generator.create_view("pca_analysis.json")
        logger.info(f"✅ Generated PCA analysis view: {result['filename']}")
        logger.info(f"   📁 Size: {result['size_kb']} KB")
        logger.info(f"   📊 Path: {result['path']}")
        
    except Exception as e:
        logger.error(f"❌ Failed to generate PCA analysis view: {e}")
        raise

if __name__ == "__main__":
    main()