"""Unit tests for station views module."""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import fixtures
from tests.fixtures.sample_data import mock_data_dir, sample_station_data

# Import the function we're testing (will fail initially - that's expected in TDD)
from mbon_analysis.views.station_views import generate_station_overview


@pytest.mark.tdd
class TestStationOverviewGeneration:
    """Test-driven development tests for station overview generation."""

    def test_generate_station_overview_structure(self, mock_data_dir):
        """Test that station overview has correct structure."""
        result = generate_station_overview(mock_data_dir)
        assert 'stations' in result
        assert 'metadata' in result
        assert isinstance(result['stations'], list)
        assert len(result['stations']) >= 0  # Can handle any number of stations

    def test_station_overview_size(self, mock_data_dir):
        """Test that output is reasonably sized for performance."""
        result = generate_station_overview(mock_data_dir)
        json_str = json.dumps(result)
        station_count = len(result['stations'])
        
        # Reasonable size limit: 5KB base + 2KB per station
        # Ensures good performance regardless of project size
        size_limit = 5120 + station_count * 2048
        assert len(json_str) < size_limit, f"Output size {len(json_str)} bytes exceeds limit {size_limit} bytes for {station_count} stations"

    def test_station_summary_stats(self, mock_data_dir):
        """Test that each station has required summary stats."""
        result = generate_station_overview(mock_data_dir)
        for station in result['stations']:
            assert 'summary_stats' in station
            assert 'total_detections' in station['summary_stats']
            assert 'species_count' in station['summary_stats']
            assert 'recording_hours' in station['summary_stats']
            assert 'years_active' in station['summary_stats']

    def test_station_coordinates(self, mock_data_dir):
        """Test that each station has coordinates."""
        result = generate_station_overview(mock_data_dir)
        for station in result['stations']:
            assert 'coordinates' in station
            assert 'lat' in station['coordinates']
            assert 'lon' in station['coordinates']
            
            # Coordinates should be valid latitude/longitude values
            assert -90.0 <= station['coordinates']['lat'] <= 90.0, f"Station {station['id']} latitude {station['coordinates']['lat']} out of valid range"
            assert -180.0 <= station['coordinates']['lon'] <= 180.0, f"Station {station['id']} longitude {station['coordinates']['lon']} out of valid range"

    def test_station_basic_info(self, mock_data_dir):
        """Test that each station has basic identifying information."""
        result = generate_station_overview(mock_data_dir)
        
        for station in result['stations']:
            assert 'id' in station
            assert 'name' in station
            
            # ID should be a non-empty string
            assert isinstance(station['id'], str)
            assert len(station['id']) > 0
            
            # Name should be a non-empty string
            assert isinstance(station['name'], str)
            assert len(station['name']) > 0

    def test_metadata_structure(self, mock_data_dir):
        """Test that metadata has required fields."""
        result = generate_station_overview(mock_data_dir)
        metadata = result['metadata']
        
        assert 'generated_at' in metadata
        assert 'data_sources' in metadata
        assert 'total_stations' in metadata
        
        # Total stations should match actual number of stations returned
        assert metadata['total_stations'] == len(result['stations'])
        assert isinstance(metadata['total_stations'], int)
        assert metadata['total_stations'] >= 0

    def test_deployments_structure(self, mock_data_dir):
        """Test that deployments information is included."""
        result = generate_station_overview(mock_data_dir)
        for station in result['stations']:
            assert 'deployments' in station
            assert isinstance(station['deployments'], list)
            # Each deployment should have basic info
            for deployment in station['deployments']:
                assert 'start' in deployment or 'end' in deployment

    def test_summary_stats_data_types(self, mock_data_dir):
        """Test that summary stats have correct data types."""
        result = generate_station_overview(mock_data_dir)
        for station in result['stations']:
            stats = station['summary_stats']
            
            # Should be integers
            assert isinstance(stats['total_detections'], int)
            assert isinstance(stats['species_count'], int) 
            assert isinstance(stats['recording_hours'], (int, float))
            
            # Should be reasonable values
            assert stats['total_detections'] >= 0
            assert stats['species_count'] >= 0
            assert stats['recording_hours'] >= 0
            
            # Years should be a list of integers
            assert isinstance(stats['years_active'], list)
            for year in stats['years_active']:
                assert isinstance(year, int)
                assert 1990 <= year <= 2030  # Reasonable year range for any marine monitoring project

    def test_json_serializable(self, mock_data_dir):
        """Test that the result is JSON serializable."""
        result = generate_station_overview(mock_data_dir)
        try:
            json_str = json.dumps(result)
            # Should also be deserializable
            deserialized = json.loads(json_str)
            assert deserialized == result
        except (TypeError, ValueError) as e:
            pytest.fail(f"Result is not JSON serializable: {e}")

    def test_empty_directory_handling(self):
        """Test handling of empty or non-existent data directory."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_dir = Path(tmpdir)
            # Should handle gracefully, not crash
            result = generate_station_overview(empty_dir)
            assert isinstance(result, dict)
            assert 'stations' in result
            assert 'metadata' in result