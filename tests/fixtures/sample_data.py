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
        
        # Create mock detections.json (array of detection records)
        detections_data = [
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
            },
            {
                "station": "9M",
                "datetime": "2021-01-01T04:00:00",
                "species": "bde",
                "detection": 1
            }
        ]
        
        with open(data_dir / "detections.json", "w") as f:
            json.dump(detections_data, f)
        
        # Create mock stations.json (match real data structure: array directly)
        stations_data = [
            {
                "id": "9M", 
                "name": "Station 9M", 
                "coordinates": {"lat": 32.1, "lon": -80.8},
                "years": ["2021"],
                "data_types": ["detections", "environmental"]
            },
            {
                "id": "14M", 
                "name": "Station 14M", 
                "coordinates": {"lat": 32.2, "lon": -80.7},
                "years": ["2021"],
                "data_types": ["detections", "environmental"]
            },
            {
                "id": "37M", 
                "name": "Station 37M", 
                "coordinates": {"lat": 32.3, "lon": -80.6},
                "years": ["2021"],
                "data_types": ["detections", "environmental"]
            }
            # Future stations can be added here without breaking tests
        ]
        
        with open(data_dir / "stations.json", "w") as f:
            json.dump(stations_data, f)
        
        # Create mock deployment_metadata.json
        deployment_data = [
            {
                "station": "9M",
                "deployment_id": "9M_test_2021",
                "start_date": "2021-01-01",
                "end_date": "2021-12-31"
            },
            {
                "station": "14M",
                "deployment_id": "14M_test_2021", 
                "start_date": "2021-01-01",
                "end_date": "2021-12-31"
            }
        ]
        
        with open(data_dir / "deployment_metadata.json", "w") as f:
            json.dump(deployment_data, f)
        
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