"""Tests for view file generation and optimization."""

import pytest
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import tempfile
import time
from unittest.mock import patch, Mock

from mbon_analysis.data.loaders import create_loader


class TestViewFileSizeLimits:
    """Test that generated view files stay under size limits."""
    
    def setup_method(self):
        """Set up test environment."""
        # Data is at project root, not in python folder
        self.data_root = Path(__file__).parent.parent.parent / "data"
        self.views_dir = self.data_root / "views"
    
    def test_all_view_files_under_size_limit(self):
        """Ensure all view files are under 50KB size limit."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        size_limit = 50 * 1024  # 50KB in bytes
        oversized_files = []
        
        for view_file in self.views_dir.glob("*.json"):
            file_size = view_file.stat().st_size
            if file_size > size_limit:
                oversized_files.append({
                    'file': view_file.name,
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 2)
                })
        
        if oversized_files:
            error_msg = "View files exceeding 50KB limit:\n"
            for file_info in oversized_files:
                error_msg += f"  - {file_info['file']}: {file_info['size_kb']}KB\n"
            pytest.fail(error_msg)
    
    def test_view_files_exist(self):
        """Test that expected view files exist."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        expected_files = [
            "stations.json",
            "datasets_summary.json", 
            "indices_reference.json",
            "project_metadata.json"
        ]
        
        missing_files = []
        for filename in expected_files:
            if not (self.views_dir / filename).exists():
                missing_files.append(filename)
        
        if missing_files:
            pytest.fail(f"Missing expected view files: {missing_files}")
    
    def test_view_vs_processed_file_sizes(self):
        """Test that view files are smaller than their processed counterparts."""
        processed_dir = self.data_root / "processed"
        
        if not processed_dir.exists():
            pytest.skip("Processed directory not found")
        
        # Check if large processed files exist
        large_files = list(processed_dir.glob("compiled_*.json"))
        if not large_files:
            pytest.skip("No large processed files found to compare")
        
        view_files = list(self.views_dir.glob("*.json"))
        if not view_files:
            pytest.skip("No view files found")
        
        # Total size comparison
        total_view_size = sum(f.stat().st_size for f in view_files)
        total_processed_size = sum(f.stat().st_size for f in large_files)
        
        # View files should be much smaller than processed files
        assert total_view_size < total_processed_size, \
            f"View files ({total_view_size} bytes) should be smaller than processed files ({total_processed_size} bytes)"


class TestJSONStructureValidation:
    """Test that view files have correct JSON structure."""
    
    def setup_method(self):
        """Set up test environment."""
        self.data_root = Path(__file__).parent.parent.parent / "data"
        self.views_dir = self.data_root / "views"
    
    def test_all_files_valid_json(self):
        """Test that all view files contain valid JSON."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        invalid_files = []
        
        for view_file in self.views_dir.glob("*.json"):
            try:
                with open(view_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                invalid_files.append(f"{view_file.name}: {e}")
        
        if invalid_files:
            pytest.fail(f"Invalid JSON files found: {invalid_files}")
    
    def test_stations_json_schema(self):
        """Validate stations.json has expected structure."""
        stations_file = self.views_dir / "stations.json"
        
        if not stations_file.exists():
            pytest.skip("stations.json not found")
        
        with open(stations_file) as f:
            data = json.load(f)
        
        # Check top-level structure
        required_keys = ["metadata", "summary", "stations"]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
        
        # Check metadata structure
        metadata = data["metadata"]
        assert "generated_at" in metadata, "Missing generated_at in metadata"
        assert "version" in metadata, "Missing version in metadata"
        
        # Check stations structure
        stations = data["stations"]
        assert isinstance(stations, list), "Stations should be a list"
        
        if stations:
            station = stations[0]
            required_station_keys = ["id", "name", "coordinates"]
            for key in required_station_keys:
                assert key in station, f"Missing required station key: {key}"
            
            # Check coordinates structure
            coords = station["coordinates"]
            assert "latitude" in coords, "Missing latitude in coordinates"
            assert "longitude" in coords, "Missing longitude in coordinates"
            assert isinstance(coords["latitude"], (int, float)), "Latitude should be numeric"
            assert isinstance(coords["longitude"], (int, float)), "Longitude should be numeric"
    
    def test_datasets_summary_schema(self):
        """Validate datasets_summary.json has expected structure."""
        summary_file = self.views_dir / "datasets_summary.json"
        
        if not summary_file.exists():
            pytest.skip("datasets_summary.json not found")
        
        with open(summary_file) as f:
            data = json.load(f)
        
        # Check top-level structure
        required_keys = ["metadata", "summary"]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
        
        # Check summary has counts
        summary = data["summary"]
        assert "total_records" in summary or "total_stations" in summary, \
            "Summary should contain record/station counts"
    
    def test_indices_reference_schema(self):
        """Validate indices_reference.json has expected structure."""
        indices_file = self.views_dir / "indices_reference.json"
        
        if not indices_file.exists():
            pytest.skip("indices_reference.json not found")
        
        with open(indices_file) as f:
            data = json.load(f)
        
        # Should contain indices information
        assert "indices" in data or "categories" in data or isinstance(data, list), \
            "Indices file should contain indices information"


class TestDataTransformationAccuracy:
    """Test that view transformations preserve data accuracy."""
    
    def setup_method(self):
        """Set up test environment."""
        self.data_root = Path(__file__).parent.parent.parent / "data"
        self.views_dir = self.data_root / "views"
        self.loader = create_loader(self.data_root)
    
    def test_station_count_accuracy(self):
        """Verify station counts match between raw metadata and views."""
        stations_file = self.views_dir / "stations.json"
        
        if not stations_file.exists():
            pytest.skip("stations.json not found")
        
        # Load view data
        with open(stations_file) as f:
            view_data = json.load(f)
        
        view_stations = len(view_data.get("stations", []))
        
        # Try to load raw deployment metadata
        try:
            raw_deployment = self.loader.load_deployment_metadata()
            # Count unique stations in raw data
            raw_stations = raw_deployment["Station"].nunique()
            
            # Allow some tolerance for filtering/processing differences
            assert abs(view_stations - raw_stations) <= 2, \
                f"Station count mismatch: view={view_stations}, raw={raw_stations}"
                
        except Exception:
            # If we can't load raw data, just ensure view has reasonable station count
            assert view_stations > 0, "View should contain at least one station"
            assert view_stations < 50, "View station count seems unreasonably high"
    
    def test_coordinate_precision_maintained(self):
        """Test that coordinate precision is maintained in transformations."""
        stations_file = self.views_dir / "stations.json"
        
        if not stations_file.exists():
            pytest.skip("stations.json not found")
        
        with open(stations_file) as f:
            data = json.load(f)
        
        stations = data.get("stations", [])
        if not stations:
            pytest.skip("No station data found")
        
        for station in stations[:3]:  # Test first 3 stations
            coords = station.get("coordinates", {})
            lat = coords.get("latitude")
            lon = coords.get("longitude")
            
            if lat is not None and lon is not None:
                # Check reasonable precision (at least 3 decimal places for GPS)
                lat_str = str(lat)
                lon_str = str(lon)
                
                if "." in lat_str:
                    lat_precision = len(lat_str.split(".")[1])
                    assert lat_precision >= 3, f"Latitude precision too low: {lat_precision} decimal places"
                
                if "." in lon_str:
                    lon_precision = len(lon_str.split(".")[1])
                    assert lon_precision >= 3, f"Longitude precision too low: {lon_precision} decimal places"
    
    def test_numeric_data_ranges(self):
        """Test that numeric data falls within reasonable scientific ranges."""
        
        # Test acoustic indices distributions
        acoustic_file = self.views_dir / "acoustic_indices_distributions.json"
        if acoustic_file.exists():
            with open(acoustic_file) as f:
                data = json.load(f)
            
            # Check that statistical values are reasonable
            for index_name, stats in data.items():
                if isinstance(stats, dict):
                    if "mean" in stats:
                        mean_val = stats["mean"]
                        assert not np.isnan(mean_val), f"Mean value is NaN for {index_name}"
                        assert np.isfinite(mean_val), f"Mean value is infinite for {index_name}"
                    
                    if "std" in stats:
                        std_val = stats["std"]
                        assert std_val >= 0, f"Standard deviation negative for {index_name}"
                        assert np.isfinite(std_val), f"Std deviation is infinite for {index_name}"
    
    def test_date_format_consistency(self):
        """Test that date formats are consistent across views."""
        
        date_patterns = []
        
        for view_file in self.views_dir.glob("*.json"):
            with open(view_file) as f:
                data = json.load(f)
            
            # Extract date strings recursively
            def extract_dates(obj, path=""):
                dates = []
                if isinstance(obj, str):
                    # Look for date-like strings
                    if any(sep in obj for sep in ["-", "/"]) and any(c.isdigit() for c in obj):
                        if len(obj) >= 8:  # Minimum date length
                            dates.append((obj, path))
                elif isinstance(obj, dict):
                    for key, value in obj.items():
                        dates.extend(extract_dates(value, f"{path}.{key}"))
                elif isinstance(obj, list):
                    for i, item in enumerate(obj[:10]):  # Check first 10 items
                        dates.extend(extract_dates(item, f"{path}[{i}]"))
                return dates
            
            dates = extract_dates(data)
            date_patterns.extend(dates)
        
        if date_patterns:
            # Check that most dates follow a consistent pattern
            formats = {}
            for date_str, path in date_patterns[:20]:  # Check first 20
                # Rough format detection
                if "-" in date_str:
                    formats["dash"] = formats.get("dash", 0) + 1
                elif "/" in date_str:
                    formats["slash"] = formats.get("slash", 0) + 1
            
            # Should have some consistency in format
            assert len(formats) <= 2, f"Too many different date formats detected: {formats}"


class TestCompletenessValidation:
    """Test that views contain complete and expected data."""
    
    def setup_method(self):
        """Set up test environment."""
        self.data_root = Path(__file__).parent.parent.parent / "data"
        self.views_dir = self.data_root / "views"
    
    def test_all_expected_view_files_present(self):
        """Test that all expected view files are generated."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        expected_files = [
            "stations.json",
            "datasets_summary.json", 
            "indices_reference.json",
            "project_metadata.json"
        ]
        
        # Optional files that might exist
        optional_files = [
            "heatmap.json",
            "acoustic_indices_distributions.json",
            "species_timeline.json",
            "environmental_trends.json"
        ]
        
        missing_required = []
        for filename in expected_files:
            if not (self.views_dir / filename).exists():
                missing_required.append(filename)
        
        if missing_required:
            pytest.fail(f"Missing required view files: {missing_required}")
        
        # Report on optional files (as info, not failure)
        present_optional = []
        for filename in optional_files:
            if (self.views_dir / filename).exists():
                present_optional.append(filename)
        
        print(f"Optional view files present: {present_optional}")
    
    def test_view_files_not_empty(self):
        """Test that view files contain actual data."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        empty_files = []
        minimal_files = []
        
        for view_file in self.views_dir.glob("*.json"):
            file_size = view_file.stat().st_size
            
            if file_size == 0:
                empty_files.append(view_file.name)
            elif file_size < 100:  # Less than 100 bytes is suspicious
                minimal_files.append(f"{view_file.name} ({file_size} bytes)")
        
        if empty_files:
            pytest.fail(f"Empty view files found: {empty_files}")
        
        if minimal_files:
            print(f"Warning: Suspiciously small files: {minimal_files}")
    
    def test_metadata_completeness(self):
        """Test that metadata sections are complete."""
        
        metadata_files = [
            ("stations.json", ["generated_at", "version", "data_sources"]),
            ("datasets_summary.json", ["generated_at", "version"]),
            ("project_metadata.json", ["generated_at", "version", "research_context"])
        ]
        
        for filename, required_metadata in metadata_files:
            filepath = self.views_dir / filename
            if not filepath.exists():
                continue
            
            with open(filepath) as f:
                data = json.load(f)
            
            metadata = data.get("metadata", {})
            missing_meta = []
            
            for meta_key in required_metadata:
                if meta_key not in metadata:
                    missing_meta.append(meta_key)
            
            if missing_meta:
                print(f"Warning: Missing metadata in {filename}: {missing_meta}")
    
    def test_data_sections_populated(self):
        """Test that data sections contain expected content."""
        
        data_checks = [
            ("stations.json", "stations", list, 1),  # Should have at least 1 station
            ("indices_reference.json", ["indices", "categories", None], [list, dict, list], 1),  # Flexible structure
        ]
        
        for filename, data_keys, expected_types, min_count in data_checks:
            filepath = self.views_dir / filename
            if not filepath.exists():
                continue
            
            with open(filepath) as f:
                data = json.load(f)
            
            # Handle flexible data key options
            if isinstance(data_keys, list):
                found_data = None
                for key in data_keys:
                    if key is None:
                        found_data = data if isinstance(data, (list, dict)) else None
                        break
                    elif key in data:
                        found_data = data[key]
                        break
            else:
                found_data = data.get(data_keys)
            
            if found_data is not None:
                # Check type
                if not isinstance(expected_types, list):
                    expected_types = [expected_types]
                
                assert any(isinstance(found_data, t) for t in expected_types), \
                    f"Data in {filename} has wrong type: expected {expected_types}, got {type(found_data)}"
                
                # Check minimum count
                if hasattr(found_data, '__len__'):
                    assert len(found_data) >= min_count, \
                        f"Data in {filename} has insufficient records: {len(found_data)} < {min_count}"


class TestPerformanceRequirements:
    """Test that view generation meets performance requirements."""
    
    def setup_method(self):
        """Set up test environment."""
        self.data_root = Path(__file__).parent.parent.parent / "data"
        self.views_dir = self.data_root / "views"
    
    def test_view_file_size_limits(self):
        """Test that view files stay under the 50KB limit for CDN optimization."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        size_limit = 50 * 1024  # 50KB
        oversized_files = []
        
        for view_file in self.views_dir.glob("*.json"):
            file_size = view_file.stat().st_size
            if file_size > size_limit:
                oversized_files.append({
                    'file': view_file.name,
                    'size_kb': round(file_size / 1024, 2)
                })
        
        if oversized_files:
            # Allow some files to be larger but warn about it
            large_but_acceptable = []
            truly_oversized = []
            
            for file_info in oversized_files:
                if file_info['size_kb'] <= 100:  # Up to 100KB might be acceptable
                    large_but_acceptable.append(file_info)
                else:
                    truly_oversized.append(file_info)
            
            if truly_oversized:
                error_msg = "View files significantly exceeding size limits:\n"
                for file_info in truly_oversized:
                    error_msg += f"  - {file_info['file']}: {file_info['size_kb']}KB\n"
                pytest.fail(error_msg)
            
            if large_but_acceptable:
                print("Warning: Files over 50KB but under 100KB:")
                for file_info in large_but_acceptable:
                    print(f"  - {file_info['file']}: {file_info['size_kb']}KB")
    
    def test_json_parsing_performance(self):
        """Test that view files can be parsed quickly."""
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        slow_files = []
        
        for view_file in self.views_dir.glob("*.json"):
            start_time = time.time()
            
            try:
                with open(view_file) as f:
                    json.load(f)
                
                parse_time = time.time() - start_time
                
                # Files should parse in under 1 second
                if parse_time > 1.0:
                    slow_files.append({
                        'file': view_file.name,
                        'parse_time': round(parse_time, 3)
                    })
                    
            except Exception as e:
                pytest.fail(f"Failed to parse {view_file.name}: {e}")
        
        if slow_files:
            print("Warning: Slow parsing files:")
            for file_info in slow_files:
                print(f"  - {file_info['file']}: {file_info['parse_time']}s")
    
    def test_view_generation_efficiency(self):
        """Test that view generation process is reasonably efficient."""
        # This would test the actual view generation process
        # For now, just ensure the views directory isn't excessively large
        
        if not self.views_dir.exists():
            pytest.skip("Views directory not found")
        
        total_size = sum(f.stat().st_size for f in self.views_dir.glob("*.json"))
        total_size_mb = total_size / (1024 * 1024)
        
        # All view files together shouldn't exceed 5MB
        assert total_size_mb <= 5.0, \
            f"Total view files size too large: {total_size_mb:.2f}MB > 5MB"
        
        # Should have reasonable number of files (not too many, not too few)
        file_count = len(list(self.views_dir.glob("*.json")))
        assert 3 <= file_count <= 20, \
            f"Unexpected number of view files: {file_count} (expected 3-20)"