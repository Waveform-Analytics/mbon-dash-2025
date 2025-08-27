"""Station view generators for dashboard frontend."""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd


def generate_station_overview(processed_data_dir) -> Dict[str, Any]:
    """Generate station overview optimized for interactive map.
    
    Creates a lightweight view containing:
    - Station locations and basic info
    - Summary statistics (detection counts, species counts, recording hours)
    - Deployment information
    - Years active
    
    Args:
        processed_data_dir: Path to directory with processed JSON files (str or Path)
        
    Returns:
        Dictionary with stations and metadata for frontend consumption
    """
    # Convert to Path object if needed
    processed_data_dir = Path(processed_data_dir)
    
    # Load source data files
    stations_data = _load_stations_data(processed_data_dir)
    deployment_data = _load_deployment_data(processed_data_dir)
    summary_stats = _calculate_station_summaries(processed_data_dir, stations_data)
    
    # Build station overview
    stations = []
    for station_info in stations_data:
        station_id = station_info['id']
        
        # Get deployment info for this station
        station_deployments = [
            {
                'start': dep.get('start_date'),
                'end': dep.get('end_date'),
                'deployment_id': dep.get('deployment_id')
            }
            for dep in deployment_data 
            if dep.get('station') == station_id
        ]
        
        # Get summary stats for this station
        stats = summary_stats.get(station_id, {
            'total_detections': 0,
            'species_count': 0,
            'recording_hours': 0,
            'years_active': []
        })
        
        station_overview = {
            'id': station_id,
            'name': station_info['name'],
            'coordinates': station_info['coordinates'],
            'deployments': station_deployments,
            'summary_stats': stats
        }
        
        stations.append(station_overview)
    
    # Generate metadata
    data_sources = []
    if (processed_data_dir / 'stations.json').exists():
        data_sources.append('stations.json')
    if (processed_data_dir / 'deployment_metadata.json').exists():
        data_sources.append('deployment_metadata.json')
    if (processed_data_dir / 'detections.json').exists():
        data_sources.append('detections.json')
    if (processed_data_dir / 'environmental.json').exists():
        data_sources.append('environmental.json')
    
    return {
        'stations': stations,
        'metadata': {
            'generated_at': datetime.now().isoformat() + 'Z',
            'data_sources': data_sources,
            'total_stations': len(stations)
        }
    }


def _load_stations_data(processed_data_dir: Path) -> List[Dict[str, Any]]:
    """Load stations data from JSON file."""
    stations_file = processed_data_dir / 'stations.json'
    if not stations_file.exists():
        return []
    
    with open(stations_file, 'r') as f:
        return json.load(f)


def _load_deployment_data(processed_data_dir: Path) -> List[Dict[str, Any]]:
    """Load deployment metadata from JSON file."""
    deployment_file = processed_data_dir / 'deployment_metadata.json'
    if not deployment_file.exists():
        return []
    
    with open(deployment_file, 'r') as f:
        return json.load(f)


def _calculate_station_summaries(processed_data_dir: Path, stations_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Calculate summary statistics for each station."""
    summaries = {}
    
    # Load metadata for overall stats
    metadata_file = processed_data_dir / 'metadata.json'
    metadata = {}
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    
    # Try to load detections data for per-station stats
    detections_file = processed_data_dir / 'detections.json'
    detections_df = None
    if detections_file.exists():
        try:
            detections_df = pd.read_json(detections_file)
        except:
            pass  # If loading fails, we'll use default values
    
    # Try to load environmental data for recording hours estimate
    environmental_file = processed_data_dir / 'environmental.json'
    environmental_df = None
    if environmental_file.exists():
        try:
            environmental_df = pd.read_json(environmental_file)
        except:
            pass
    
    # Calculate stats for each station
    for station_info in stations_data:
        station_id = station_info['id']
        years_active = []
        
        # Extract years from station info if available
        if 'years' in station_info:
            years_active = [int(year) for year in station_info['years']]
        
        # Calculate detection-based stats if data is available
        total_detections = 0
        species_count = 0
        if detections_df is not None and 'station' in detections_df.columns:
            station_detections = detections_df[detections_df['station'] == station_id]
            total_detections = len(station_detections)
            if 'species' in station_detections.columns:
                # Count unique species (excluding non-biological sounds)
                species_count = station_detections['species'].nunique()
        
        # Estimate recording hours from environmental data or use default
        recording_hours = 0
        if environmental_df is not None and 'station' in environmental_df.columns:
            station_env = environmental_df[environmental_df['station'] == station_id]
            # Rough estimate: assume hourly measurements
            recording_hours = len(station_env)
        else:
            # Default estimate based on years active (assume ~8760 hours per year)
            recording_hours = len(years_active) * 8760
        
        summaries[station_id] = {
            'total_detections': total_detections,
            'species_count': species_count,
            'recording_hours': recording_hours,
            'years_active': years_active
        }
    
    return summaries