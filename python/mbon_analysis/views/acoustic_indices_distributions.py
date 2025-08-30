"""Acoustic indices distributions view generator for small multiples visualization."""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List
from .base import BaseViewGenerator
from ..data.loaders import create_loader


class AcousticIndicesDistributionsGenerator(BaseViewGenerator):
    """Generate acoustic_indices_distributions.json with KDE data for small multiples."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate view data for acoustic indices distributions.
        
        Returns:
            Dictionary with KDE distributions for all indices, grouped by station/year/bandwidth
        """
        loader = create_loader(self.data_root)
        
        # Get available stations and load all acoustic indices data
        stations = ['9M', '14M', '37M']  # Known stations with acoustic indices
        bandwidths = ['FullBW', '8kHz']
        year = 2021  # Only year with acoustic indices data
        
        distributions_data = {}
        indices_metadata = {}
        
        # Load indices reference for metadata
        try:
            indices_ref = loader.load_indices_reference()
            # Create lookup for index descriptions and categories
            ref_lookup = {}
            for _, row in indices_ref.iterrows():
                if 'Prefix' in row and 'Category' in row:
                    ref_lookup[row['Prefix']] = {
                        'category': row.get('Category', 'Unknown'),
                        'subcategory': row.get('Subcategory', ''),
                        'description': row.get('Description', ''),
                        'unit': ''  # No unit column in this CSV
                    }
            print(f"Loaded {len(ref_lookup)} index metadata entries")
        except Exception as e:
            print(f"Warning: Could not load indices reference: {e}")
            ref_lookup = {}
        
        # Collect all data first
        all_data = []
        
        for station in stations:
            for bandwidth in bandwidths:
                try:
                    df = loader.load_acoustic_indices(station, bandwidth)
                    
                    # Add metadata columns
                    df['station'] = station
                    df['bandwidth'] = bandwidth
                    df['year'] = year
                    
                    all_data.append(df)
                    print(f"Loaded data for {station} {bandwidth}: {len(df)} records")
                    
                except FileNotFoundError:
                    print(f"No data found for {station} {bandwidth}")
                    continue
                except Exception as e:
                    print(f"Error loading {station} {bandwidth}: {e}")
                    continue
        
        if not all_data:
            return {
                "metadata": {
                    "generated_at": pd.Timestamp.now().isoformat(),
                    "version": "1.0.0",
                    "description": "No acoustic indices data found",
                    "error": "No data files could be loaded"
                },
                "summary": {},
                "distributions": {},
                "filters": {}
            }
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Get numeric columns (exclude metadata and non-numeric columns)
        metadata_cols = ['Date', 'Filename', 'station', 'bandwidth', 'year']
        numeric_cols = []
        
        for col in combined_df.columns:
            if col not in metadata_cols:
                # Check if column is numeric
                try:
                    pd.to_numeric(combined_df[col], errors='coerce')
                    # Only include if it has valid numeric data
                    if combined_df[col].notna().sum() > 10:  # At least 10 valid values
                        numeric_cols.append(col)
                except:
                    continue
        
        print(f"Found {len(numeric_cols)} numeric indices columns")
        
        # Generate KDE distributions for each index
        for index_name in numeric_cols:
            distributions_data[index_name] = {}
            
            # Get metadata for this index
            index_meta = ref_lookup.get(index_name, {
                'category': 'Unknown',
                'description': f'Acoustic index: {index_name}',
                'unit': ''
            })
            indices_metadata[index_name] = index_meta
            
            # Calculate distributions for each station
            station_distributions = {}
            
            for station in stations:
                station_data = combined_df[
                    (combined_df['station'] == station) & 
                    (combined_df[index_name].notna())
                ][index_name]
                
                if len(station_data) < 5:  # Need at least 5 points for KDE
                    continue
                
                try:
                    # Calculate KDE
                    kde = stats.gaussian_kde(station_data)
                    
                    # Create evaluation points
                    data_min, data_max = station_data.min(), station_data.max()
                    data_range = data_max - data_min
                    
                    # Extend range slightly for better visualization
                    eval_min = data_min - 0.1 * data_range
                    eval_max = data_max + 0.1 * data_range
                    
                    # Create evaluation points (50 points for smooth curves)
                    eval_points = np.linspace(eval_min, eval_max, 50)
                    density_values = kde(eval_points)
                    
                    station_distributions[station] = {
                        'x': eval_points.tolist(),
                        'y': density_values.tolist(),
                        'count': len(station_data),
                        'mean': float(station_data.mean()),
                        'std': float(station_data.std()),
                        'min': float(data_min),
                        'max': float(data_max)
                    }
                    
                except Exception as e:
                    print(f"Error calculating KDE for {index_name} at {station}: {e}")
                    continue
            
            distributions_data[index_name] = station_distributions
        
        # Filter options
        filter_options = {
            'stations': stations,
            'bandwidths': bandwidths,
            'years': [year],
            'available_combinations': []
        }
        
        # Find available combinations
        for station in stations:
            for bandwidth in bandwidths:
                combo_data = combined_df[
                    (combined_df['station'] == station) & 
                    (combined_df['bandwidth'] == bandwidth)
                ]
                if len(combo_data) > 0:
                    filter_options['available_combinations'].append({
                        'station': station,
                        'bandwidth': bandwidth,
                        'year': year,
                        'record_count': len(combo_data)
                    })
        
        return {
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "version": "1.0.0",
                "description": "KDE distributions for all acoustic indices by station",
                "total_indices": len(distributions_data),
                "total_records": len(combined_df),
                "kde_points": 50
            },
            "summary": {
                "indices_count": len(distributions_data),
                "stations": stations,
                "bandwidths": bandwidths,
                "year": year,
                "categories": list(set(meta.get('category', 'Unknown') for meta in indices_metadata.values()))
            },
            "distributions": distributions_data,
            "indices_metadata": indices_metadata,
            "filters": filter_options
        }