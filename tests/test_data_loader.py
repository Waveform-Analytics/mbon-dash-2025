"""
Tests for the data loader module.
"""

import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mbon_analysis.core.data_loader import (
    get_data_directory,
    load_processed_data,
    load_acoustic_indices,
    load_metadata
)


class TestDataDirectory:
    """Test data directory utilities."""
    
    def test_get_data_directory_default(self):
        """Test getting default data directory."""
        data_dir = get_data_directory()
        assert isinstance(data_dir, Path)
        assert data_dir.exists()
        assert "processed" in str(data_dir)
    
    def test_get_data_directory_custom_existing(self):
        """Test custom data directory that exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            result = get_data_directory(custom_dir)
            assert result == custom_dir
    
    def test_get_data_directory_custom_nonexistent(self):
        """Test custom data directory that doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Data directory not found"):
            get_data_directory("/nonexistent/path")


class TestDataLoading:
    """Test data loading functions."""
    
    @pytest.fixture
    def sample_data_dir(self):
        """Create temporary data directory with sample files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            
            # Create sample detection data
            detections = [
                {"id": 1, "date": "2021-01-01T10:00:00", "sp": 1, "station": "9M"},
                {"id": 2, "date": "2021-01-01T12:00:00", "bde": 1, "station": "14M"}
            ]
            with open(data_dir / "detections.json", 'w') as f:
                json.dump(detections, f)
            
            # Create sample environmental data  
            environmental = [
                {"datetime": "2021-01-01T10:00:00", "Water temp (°C)": 15.2, "station": "9M"},
                {"datetime": "2021-01-01T12:00:00", "Water temp (°C)": 15.8, "station": "14M"}
            ]
            with open(data_dir / "environmental.json", 'w') as f:
                json.dump(environmental, f)
            
            # Create sample species metadata
            species = [
                {"short_name": "sp", "long_name": "Silver perch", "category": "bio"},
                {"short_name": "bde", "long_name": "Bottlenose dolphin echolocation", "category": "bio"}
            ]
            with open(data_dir / "species.json", 'w') as f:
                json.dump(species, f)
            
            # Create sample stations metadata
            stations = [
                {"id": "9M", "name": "Station 9M", "coordinates": {"lat": 32.28, "lon": -80.88}},
                {"id": "14M", "name": "Station 14M", "coordinates": {"lat": 32.27, "lon": -80.90}}
            ]
            with open(data_dir / "stations.json", 'w') as f:
                json.dump(stations, f)
            
            yield data_dir
    
    def test_load_metadata(self, sample_data_dir):
        """Test loading metadata."""
        try:
            metadata = load_metadata(sample_data_dir)
            assert isinstance(metadata, dict)
        except FileNotFoundError:
            # Metadata file might not exist in test setup
            pytest.skip("Metadata file not available in test directory")
    
    def test_load_processed_data_core(self, sample_data_dir):
        """Test loading all core processed data."""
        detections, environmental, species, stations = load_processed_data(
            data_dir=sample_data_dir, 
            include_acoustic_indices=False
        )
        
        assert isinstance(detections, pd.DataFrame)
        assert isinstance(environmental, pd.DataFrame)
        assert isinstance(species, list)
        assert isinstance(stations, list)
        
        assert len(detections) == 2
        assert len(environmental) == 2
        assert len(species) == 2
        assert len(stations) == 2
    
    def test_load_processed_data_missing_files(self, sample_data_dir):
        """Test loading processed data when files are missing."""
        (sample_data_dir / "detections.json").unlink()
        
        with pytest.raises(FileNotFoundError):
            load_processed_data(data_dir=sample_data_dir)


class TestDataIntegration:
    """Integration tests with real data files."""
    
    @pytest.mark.integration
    def test_load_real_data(self):
        """Test loading actual processed data files."""
        try:
            detections, environmental, species, stations = load_processed_data(
                include_acoustic_indices=False
            )
            
            # Check data structure
            assert isinstance(detections, pd.DataFrame)
            assert isinstance(environmental, pd.DataFrame)
            assert isinstance(species, list)
            assert isinstance(stations, list)
            
            # Check we have reasonable amounts of data
            assert len(detections) > 1000  # Should have many detection records
            assert len(environmental) > 1000  # Should have many environmental records
            assert len(species) > 10  # Should have multiple species
            assert len(stations) >= 3  # Should have our 3 stations
            
        except FileNotFoundError:
            pytest.skip("Real data files not available - skipping integration test")
    
    @pytest.mark.integration 
    def test_load_with_acoustic_indices(self):
        """Test loading data including acoustic indices."""
        try:
            result = load_processed_data(include_acoustic_indices=True)
            assert len(result) == 5  # Should return 5 items when including acoustic indices
            
            detections, environmental, species, stations, acoustic_indices = result
            assert isinstance(acoustic_indices, pd.DataFrame)
            assert len(acoustic_indices) > 1000  # Should have many acoustic index records
            
        except FileNotFoundError:
            pytest.skip("Real data files not available - skipping integration test")