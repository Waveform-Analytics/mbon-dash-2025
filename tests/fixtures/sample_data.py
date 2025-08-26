"""Sample test data for MBON Dashboard tests."""

from pathlib import Path
import tempfile
import json
import pytest


@pytest.fixture
def mock_data_dir():
    """Create a temporary directory with mock data files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        
        # Create mock detections.json
        detections_data = {
            "data": [
                {
                    "station": "9M",
                    "datetime": "2021-01-01T00:00:00",
                    "species": "sp",
                    "detection": 1
                },
                {
                    "station": "14M", 
                    "datetime": "2021-01-01T02:00:00",
                    "species": "otbw",
                    "detection": 1
                }
            ]
        }
        
        with open(data_dir / "detections.json", "w") as f:
            json.dump(detections_data, f)
        
        # Create mock stations.json (include required stations, but can have more)
        stations_data = {
            "stations": [
                {"id": "9M", "name": "Station 9M", "lat": 32.1, "lon": -80.8},
                {"id": "14M", "name": "Station 14M", "lat": 32.2, "lon": -80.7},
                {"id": "37M", "name": "Station 37M", "lat": 32.3, "lon": -80.6}
                # Future stations can be added here without breaking tests
            ]
        }
        
        with open(data_dir / "stations.json", "w") as f:
            json.dump(stations_data, f)
        
        yield data_dir


@pytest.fixture
def sample_station_data():
    """Sample station overview data for testing."""
    return {
        'stations': [
            {
                'id': '9M', 
                'name': 'Station 9M',
                'coordinates': {'lat': 32.1, 'lon': -80.8},
                'deployments': [{'start': '2021-01-01', 'end': '2021-12-31'}],
                'summary_stats': {
                    'total_detections': 100,
                    'species_count': 5,
                    'recording_hours': 8760,
                    'years_active': [2021]
                }
            },
            {
                'id': '14M',
                'name': 'Station 14M', 
                'coordinates': {'lat': 32.2, 'lon': -80.7},
                'deployments': [{'start': '2021-01-01', 'end': '2021-12-31'}],
                'summary_stats': {
                    'total_detections': 80,
                    'species_count': 4,
                    'recording_hours': 8760,
                    'years_active': [2021]
                }
            },
            {
                'id': '37M',
                'name': 'Station 37M',
                'coordinates': {'lat': 32.3, 'lon': -80.6}, 
                'deployments': [{'start': '2021-01-01', 'end': '2021-12-31'}],
                'summary_stats': {
                    'total_detections': 120,
                    'species_count': 6,
                    'recording_hours': 8760,
                    'years_active': [2021]
                }
            }
        ],
        'metadata': {
            'generated_at': '2024-01-01T12:00:00Z',
            'data_sources': ['detections.json', 'stations.json'],
            'total_stations': 3
        }
    }