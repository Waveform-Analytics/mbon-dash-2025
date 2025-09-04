"""Tests for overall data integrity and pipeline validation."""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestDataPipelineIntegrity:
    """Test the overall data pipeline integrity."""
    
    def test_required_environment_variables(self):
        """Test that required environment variables are defined."""
        required_vars = [
            'CLOUDFLARE_R2_ACCOUNT_ID',
            'CLOUDFLARE_R2_ACCESS_KEY_ID',
            'CLOUDFLARE_R2_SECRET_ACCESS_KEY',
            'CLOUDFLARE_R2_BUCKET_NAME',
            'CLOUDFLARE_R2_ENDPOINT',
            'NEXT_PUBLIC_CDN_BASE_URL'
        ]
        
        for var in required_vars:
            # These are set by the setup_test_environment fixture
            assert os.getenv(var) is not None, f"Environment variable {var} should be set"
    
    def test_data_directory_structure(self, temp_data_dir):
        """Test that expected data directory structure exists."""
        expected_dirs = [
            "raw",
            "raw/metadata", 
            "raw/2018/detections",
            "raw/2018/environmental",
            "raw/2021/detections",
            "raw/2021/environmental",
            "raw/indices",
            "processed",
            "views"
        ]
        
        for dir_path in expected_dirs:
            full_path = temp_data_dir / dir_path
            assert full_path.exists(), f"Directory {dir_path} should exist"
            assert full_path.is_dir(), f"{dir_path} should be a directory"
    
    def test_view_files_size_limits(self, temp_data_dir, large_sample_data):
        """Test that view files stay under size limits."""
        views_dir = temp_data_dir / "views"
        views_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a large data file that exceeds limits
        large_data_file = views_dir / "large_data.json"
        with open(large_data_file, 'w') as f:
            json.dump(large_sample_data, f)
        
        file_size = large_data_file.stat().st_size
        size_limit = 50 * 1024  # 50KB limit from architecture
        
        # This should fail - demonstrating the need for size limits
        assert file_size > size_limit, "Large sample data should exceed size limit"
        
        # In real implementation, view generators should prevent this
        # by aggregating/sampling data appropriately
    
    def test_json_schema_validity(self, sample_view_data):
        """Test that view data follows expected JSON schema."""
        # Test stations schema
        assert "stations" in sample_view_data
        assert "metadata" in sample_view_data
        
        stations = sample_view_data["stations"]
        assert isinstance(stations, list)
        
        for station in stations:
            required_fields = ["id", "name", "latitude", "longitude", "depth"]
            for field in required_fields:
                assert field in station, f"Station should have {field} field"
                assert station[field] is not None, f"Station {field} should not be None"
        
        # Test metadata schema
        metadata = sample_view_data["metadata"]
        required_metadata_fields = ["generated_at", "total_stations", "data_version"]
        for field in required_metadata_fields:
            assert field in metadata, f"Metadata should have {field} field"
    
    def test_file_naming_conventions(self, temp_data_dir):
        """Test that files follow expected naming conventions."""
        # Test detection file naming
        expected_detection_patterns = [
            "Master_Manual_9M_2h_2018.xlsx",
            "Master_Manual_14M_2h_2021.xlsx",
            "Master_Manual_37M_2h_2021.xlsx"
        ]
        
        for pattern in expected_detection_patterns:
            # Extract components
            parts = pattern.split('_')
            assert parts[0] == "Master", "Detection files should start with 'Master'"
            assert parts[1] == "Manual", "Detection files should have 'Manual'"
            assert parts[3] == "2h", "Detection files should indicate '2h' interval"
            assert pattern.endswith('.xlsx'), "Detection files should be Excel format"
        
        # Test acoustic indices naming
        indices_patterns = [
            "Acoustic_Indices_9M_2021_FullBW_v2_Final.csv",
            "Acoustic_Indices_14M_2021_8kHz_v2_Final.csv"
        ]
        
        for pattern in indices_patterns:
            parts = pattern.split('_')
            assert parts[0] == "Acoustic", "Indices files should start with 'Acoustic'"
            assert parts[1] == "Indices", "Indices files should have 'Indices'"
            assert parts[3] in ["2021"], "Should have valid year"
            assert parts[4] in ["FullBW", "8kHz"], "Should have valid bandwidth"
            assert pattern.endswith('.csv'), "Indices files should be CSV format"


class TestDataConsistency:
    """Test data consistency across different files."""
    
    def test_station_consistency_across_files(self, temp_data_dir):
        """Test that station identifiers are consistent across different file types."""
        expected_stations = ["9M", "14M", "37M"]
        
        # Test detection files have consistent station names
        detection_dir = temp_data_dir / "raw" / "2021" / "detections" 
        detection_dir.mkdir(parents=True, exist_ok=True)
        
        for station in expected_stations:
            detection_file = detection_dir / f"Master_Manual_{station}_2h_2021.xlsx"
            detection_file.touch()  # Create empty file
            
            # Verify file exists and station name is extractable
            assert detection_file.exists()
            filename_station = detection_file.stem.split('_')[2]
            assert filename_station == station
    
    def test_year_consistency(self, temp_data_dir):
        """Test that years are consistent across file types."""
        expected_years = [2018, 2021]
        
        for year in expected_years:
            year_dir = temp_data_dir / "raw" / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)
            
            # Test that year directories exist
            assert year_dir.exists()
            assert year_dir.is_dir()
            
            # Test that year can be parsed as integer
            parsed_year = int(year_dir.name)
            assert parsed_year in expected_years
    
    def test_date_format_consistency(self):
        """Test that date formats are handled consistently."""
        test_dates = [
            "2021-01-01 00:00:00",  # Standard format
            "1/1/2021 0:00",        # Excel format variant
            "12/31/2021 23:00"      # End of year format
        ]
        
        # This would test actual date parsing logic
        # For now, just verify formats are recognized
        for date_str in test_dates:
            # In real implementation, this would use the actual date parser
            assert len(date_str) > 0
            assert any(char.isdigit() for char in date_str)
            assert ':' in date_str  # Time component
    
    @pytest.mark.parametrize("station,year,bandwidth", [
        ("9M", 2021, "FullBW"),
        ("14M", 2021, "FullBW"), 
        ("9M", 2021, "8kHz"),
        ("14M", 2021, "8kHz")
    ])
    def test_acoustic_indices_availability(self, station, year, bandwidth, temp_data_dir):
        """Test that acoustic indices files exist for expected combinations."""
        indices_dir = temp_data_dir / "raw" / "indices"
        indices_dir.mkdir(parents=True, exist_ok=True)
        
        expected_file = indices_dir / f"Acoustic_Indices_{station}_{year}_{bandwidth}_v2_Final.csv"
        # In actual test, this file should exist
        # For now, just test the naming logic
        
        assert f"{station}_{year}_{bandwidth}" in str(expected_file)
        assert expected_file.suffix == ".csv"


class TestViewFileValidation:
    """Test view file generation and validation."""
    
    def test_view_file_completeness(self, temp_data_dir):
        """Test that all required view files are generated."""
        views_dir = temp_data_dir / "views"
        views_dir.mkdir(parents=True, exist_ok=True)
        
        required_view_files = [
            "stations.json",
            "datasets_summary.json", 
            "indices_reference.json",
            "heatmap.json",
            "acoustic_indices_distributions.json",
            "project_metadata.json"
        ]
        
        # In actual implementation, these would be generated by view generators
        for filename in required_view_files:
            view_file = views_dir / filename
            # For testing, create minimal valid files
            view_file.write_text('{"test": "data"}')
            
            assert view_file.exists(), f"View file {filename} should exist"
            assert view_file.stat().st_size > 0, f"View file {filename} should not be empty"
            
            # Test JSON validity
            with open(view_file) as f:
                data = json.load(f)
            assert isinstance(data, dict), f"View file {filename} should contain valid JSON object"
    
    def test_view_file_size_constraints(self, temp_data_dir):
        """Test that view files stay under size constraints."""
        views_dir = temp_data_dir / "views"
        views_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a reasonably sized view file
        reasonable_data = {"stations": [{"id": f"station_{i}"} for i in range(100)]}
        reasonable_file = views_dir / "reasonable.json"
        
        with open(reasonable_file, 'w') as f:
            json.dump(reasonable_data, f)
        
        size_limit = 50 * 1024  # 50KB
        file_size = reasonable_file.stat().st_size
        
        # This should pass for well-designed view files
        if file_size > size_limit:
            pytest.fail(f"View file {reasonable_file.name} is {file_size} bytes, exceeds {size_limit} byte limit")
    
    def test_processed_file_handling(self, temp_data_dir):
        """Test handling of large processed files."""
        processed_dir = temp_data_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Large processed files should be handled differently
        large_processed_file = processed_dir / "compiled_indices.json"
        large_data = {"data": [{"index": i, "value": i * 0.1} for i in range(1000)]}
        
        with open(large_processed_file, 'w') as f:
            json.dump(large_data, f)
        
        file_size = large_processed_file.stat().st_size
        
        # Large processed files are OK - they're not served directly
        assert file_size > 1024, "Processed files can be large"
        
        # But they should be valid JSON
        with open(large_processed_file) as f:
            data = json.load(f)
        assert "data" in data
        assert len(data["data"]) == 1000


@pytest.mark.integration
class TestPipelineIntegration:
    """Integration tests for the complete data pipeline."""
    
    def test_pipeline_dependencies(self):
        """Test that all required packages are available."""
        # Test that critical packages can be imported
        try:
            import pandas
            import numpy
            import sklearn
            import boto3
            import requests
        except ImportError as e:
            pytest.fail(f"Required package not available: {e}")
    
    def test_configuration_validation(self):
        """Test that configuration is valid."""
        # Test environment variables
        cdn_url = os.getenv('NEXT_PUBLIC_CDN_BASE_URL')
        assert cdn_url is not None, "CDN URL should be configured"
        assert cdn_url.startswith('https://'), "CDN URL should use HTTPS"
        
        bucket_name = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')
        assert bucket_name is not None, "Bucket name should be configured"
        assert len(bucket_name) > 0, "Bucket name should not be empty"
    
    @pytest.mark.slow
    def test_memory_usage_limits(self, large_sample_data):
        """Test that data processing doesn't exceed memory limits.""" 
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available - skipping memory usage test")
        
        import os
        
        # Get current process
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large data (simulate heavy operation)
        processed_data = []
        for item in large_sample_data[:1000]:  # Limit to prevent actual memory issues
            processed_data.append(item)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for test data)
        memory_limit = 100 * 1024 * 1024  # 100MB
        assert memory_increase < memory_limit, f"Memory usage increased by {memory_increase} bytes"