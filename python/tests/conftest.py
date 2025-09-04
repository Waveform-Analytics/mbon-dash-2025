"""Pytest configuration and shared fixtures for MBON analysis tests."""

import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import Mock
import tempfile
import shutil
from typing import Dict, Any

# Test data root - we'll create sample data here
TEST_DATA_ROOT = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def test_data_root():
    """Provide path to test data fixtures."""
    return TEST_DATA_ROOT


@pytest.fixture(scope="session")
def sample_deployment_metadata():
    """Sample deployment metadata DataFrame."""
    return pd.DataFrame([
        {
            'Station': '9M',
            'Latitude': 32.8234,
            'Longitude': -79.2345,
            'Deployment_Start': '2021-01-01',
            'Deployment_End': '2021-12-31',
            'Depth_m': 15.5,
            'Platform_Type': 'Mooring'
        },
        {
            'Station': '14M',
            'Latitude': 32.7123,
            'Longitude': -79.1234,
            'Deployment_Start': '2021-01-01', 
            'Deployment_End': '2021-12-31',
            'Depth_m': 20.2,
            'Platform_Type': 'Mooring'
        }
    ])


@pytest.fixture(scope="session")
def sample_species_mapping():
    """Sample species mapping DataFrame."""
    return pd.DataFrame([
        {
            'short_name': 'sp',
            'long_name': 'Silver perch',
            'category': 'biological'
        },
        {
            'short_name': 'otbw',
            'long_name': 'Oyster toadfish boat whistle',
            'category': 'biological'
        },
        {
            'short_name': 'bde',
            'long_name': 'Bottlenose dolphin echolocation',
            'category': 'biological'
        },
        {
            'short_name': 'anth',
            'long_name': 'Anthropogenic sounds',
            'category': 'anthropogenic'
        }
    ])


@pytest.fixture(scope="session")
def sample_detection_data():
    """Sample detection data DataFrame."""
    return pd.DataFrame([
        {
            'Date': '2021-01-01 00:00:00',
            'sp': 1,
            'otbw': 0,
            'bde': 1,
            'anth': 0
        },
        {
            'Date': '2021-01-01 02:00:00',
            'sp': 0,
            'otbw': 1,
            'bde': 0,
            'anth': 0
        },
        {
            'Date': '2021-01-01 04:00:00',
            'sp': 1,
            'otbw': 1,
            'bde': 1,
            'anth': 1
        }
    ])


@pytest.fixture(scope="session")
def sample_environmental_data():
    """Sample environmental data DataFrame."""
    return pd.DataFrame([
        {
            'Date': '2021-01-01 00:00:00',
            'Temperature_C': 18.5,
            'Depth_m': 15.2
        },
        {
            'Date': '2021-01-01 01:00:00', 
            'Temperature_C': 18.3,
            'Depth_m': 15.4
        },
        {
            'Date': '2021-01-01 02:00:00',
            'Temperature_C': 18.1,
            'Depth_m': 15.6
        }
    ])


@pytest.fixture(scope="session")
def sample_acoustic_indices():
    """Sample acoustic indices DataFrame."""
    return pd.DataFrame([
        {
            'Date': '2021-01-01 00:00:00',
            'Filename': 'audio_20210101_000000.wav',
            'ACI': 0.123,
            'NDSI': 0.456,
            'ADI': 0.789,
            'AEI': 0.234,
            'H_Havrda': 0.567,
            'MEANt': 0.890
        },
        {
            'Date': '2021-01-01 01:00:00',
            'Filename': 'audio_20210101_010000.wav', 
            'ACI': 0.234,
            'NDSI': 0.567,
            'ADI': 0.890,
            'AEI': 0.345,
            'H_Havrda': 0.678,
            'MEANt': 0.901
        }
    ])


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary directory with sample data structure."""
    # Create directory structure
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed" 
    views_dir = tmp_path / "views"
    
    # Metadata directory
    metadata_dir = raw_dir / "metadata"
    metadata_dir.mkdir(parents=True)
    
    # Year directories
    year_2018 = raw_dir / "2018"
    year_2021 = raw_dir / "2021"
    for year_dir in [year_2018, year_2021]:
        (year_dir / "detections").mkdir(parents=True)
        (year_dir / "environmental").mkdir(parents=True)
    
    # Indices directory
    indices_dir = raw_dir / "indices"
    indices_dir.mkdir(parents=True)
    
    # Create processed and views directories
    processed_dir.mkdir(parents=True)
    views_dir.mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def mock_r2_client():
    """Mock Cloudflare R2 client for testing CDN operations."""
    mock_client = Mock()
    mock_client.upload_fileobj = Mock(return_value=None)
    mock_client.head_object = Mock(return_value={'ContentLength': 1024})
    mock_client.download_file = Mock(return_value=None)
    return mock_client


@pytest.fixture
def sample_view_data():
    """Sample view data for testing."""
    return {
        "stations": [
            {
                "id": "9M",
                "name": "Station 9M", 
                "latitude": 32.8234,
                "longitude": -79.2345,
                "depth": 15.5
            },
            {
                "id": "14M",
                "name": "Station 14M",
                "latitude": 32.7123, 
                "longitude": -79.1234,
                "depth": 20.2
            }
        ],
        "metadata": {
            "generated_at": "2024-01-01T00:00:00Z",
            "total_stations": 2,
            "data_version": "1.0.0"
        }
    }


@pytest.fixture
def large_sample_data():
    """Generate sample data that would exceed size limits."""
    # Create a dataset that would be too large for a view file
    large_data = []
    for i in range(10000):
        large_data.append({
            "id": i,
            "timestamp": f"2021-01-01T{i%24:02d}:00:00Z",
            "value": i * 0.001,
            "metadata": f"This is sample metadata for record {i} " * 10  # Make it verbose
        })
    return large_data


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    # Mock environment variables for testing
    test_env_vars = {
        'CLOUDFLARE_R2_ACCOUNT_ID': 'test_account_id',
        'CLOUDFLARE_R2_ACCESS_KEY_ID': 'test_access_key',
        'CLOUDFLARE_R2_SECRET_ACCESS_KEY': 'test_secret_key',
        'CLOUDFLARE_R2_BUCKET_NAME': 'test-bucket',
        'CLOUDFLARE_R2_ENDPOINT': 'https://test.r2.cloudflarestorage.com',
        'NEXT_PUBLIC_CDN_BASE_URL': 'https://test.waveformdata.work'
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)


# Test markers for categorizing tests
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"  
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "cdn: mark test as requiring CDN access"
    )