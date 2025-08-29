"""Datasets summary view generator."""

from typing import Dict, Any
import pandas as pd
from .base import BaseViewGenerator
from ..data.loaders import create_loader


class DatasetsSummaryViewGenerator(BaseViewGenerator):
    """Generate datasets_summary.json with overview statistics."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate datasets summary view data.
        
        Returns:
            Dictionary with dataset statistics and overview
        """
        loader = create_loader(self.data_root)
        
        # Get available stations and years
        stations = loader.get_available_stations()
        years = loader.get_available_years()
        
        # Initialize summary data
        datasets = []
        total_records = 0
        
        # Process detection data
        detection_records = 0
        detection_species = set()
        species_mapping = loader.load_species_mapping()
        
        for station in stations:
            for year in years:
                try:
                    df = loader.load_detection_data(station, year)
                    detection_records += len(df)
                    # Count unique species columns (excluding date/time)
                    for col in df.columns:
                        if col not in ['Date', 'Time', 'DateTime', 'date', 'time']:
                            detection_species.add(col)
                except:
                    pass
        
        datasets.append({
            "id": "detections",
            "name": "Species Detections",
            "description": "Manual species annotations from hydrophone recordings",
            "record_count": detection_records,
            "stations": stations,
            "years": years,
            "temporal_resolution": "2-hour windows",
            "unique_species": len(detection_species),
            "data_type": "presence/absence"
        })
        total_records += detection_records
        
        # Process environmental data
        env_records = 0
        for station in stations:
            for year in years:
                for data_type in ['Temp', 'Depth']:
                    try:
                        df = loader.load_environmental_data(station, year, data_type)
                        env_records += len(df)
                    except:
                        pass
        
        datasets.append({
            "id": "environmental",
            "name": "Environmental Data",
            "description": "Temperature and depth measurements at hydrophone locations",
            "record_count": env_records,
            "stations": stations,
            "years": years,
            "temporal_resolution": "hourly",
            "measurements": ["temperature_celsius", "depth_meters"],
            "data_type": "continuous"
        })
        total_records += env_records
        
        # Process acoustic indices
        indices_records = 0
        indices_count = 0
        indices_stations = []
        
        for station in ['9M', '14M', '37M']:  # Known stations with indices
            try:
                df = loader.load_acoustic_indices(station, 'FullBW')
                indices_records += len(df)
                if indices_count == 0:
                    # Count indices columns (excluding datetime)
                    indices_count = len([col for col in df.columns if col not in ['Date', 'Time', 'DateTime']])
                indices_stations.append(station)
            except:
                pass
        
        datasets.append({
            "id": "acoustic_indices",
            "name": "Acoustic Indices",
            "description": "Computed acoustic metrics from audio analysis",
            "record_count": indices_records,
            "stations": indices_stations,
            "years": [2021],  # Based on available data
            "temporal_resolution": "hourly",
            "index_count": indices_count,
            "bandwidth_types": ["FullBW", "8kHz"],
            "data_type": "computed_metrics"
        })
        total_records += indices_records
        
        # Load deployment metadata for additional context
        deployment_df = loader.load_deployment_metadata()
        deployment_years = deployment_df['Year'].dropna().unique().tolist() if 'Year' in deployment_df.columns else []
        
        # Generate summary statistics
        summary = {
            "total_records": total_records,
            "total_datasets": len(datasets),
            "stations": {
                "count": len(stations),
                "list": stations
            },
            "temporal_coverage": {
                "years": sorted(years),
                "deployment_years": sorted([int(y) for y in deployment_years if pd.notna(y)]),
                "earliest": min(years) if years else None,
                "latest": max(years) if years else None
            },
            "data_types": {
                "biological": ["species_detections"],
                "environmental": ["temperature", "depth"],
                "acoustic": ["acoustic_indices", "sound_levels"]
            }
        }
        
        return {
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "version": "1.0.0",
                "description": "Dataset overview and statistics for MBON dashboard"
            },
            "summary": summary,
            "datasets": datasets
        }