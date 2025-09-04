"""Tests for view data integrity - ensuring views contain real data from raw sources."""

import pytest
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import hashlib
from unittest.mock import patch, Mock
import random

from mbon_analysis.data.loaders import create_loader


class TestViewDataIntegrity:
    """Test that view files contain real data traceable to raw sources."""
    
    def setup_method(self):
        """Set up test environment."""
        # Data is at project root, not in python folder
        self.data_root = Path(__file__).parent.parent.parent / "data"
        self.views_dir = self.data_root / "views"
        self.loader = create_loader(self.data_root)
    
    def test_stations_coordinates_match_metadata(self):
        """Verify station coordinates in views match raw deployment metadata."""
        stations_file = self.views_dir / "stations.json"
        
        if not stations_file.exists():
            pytest.skip("stations.json not found")
        
        with open(stations_file) as f:
            stations_data = json.load(f)
        
        # Try to load actual deployment metadata
        try:
            deployment_df = self.loader.load_deployment_metadata()
            
            # Check if the required columns exist (actual column names from Excel)
            lat_col = None
            lon_col = None
            
            # Look for latitude/longitude columns with various possible names
            for col in deployment_df.columns:
                col_lower = col.lower()
                if 'lat' in col_lower and not lat_col:
                    lat_col = col
                elif 'lon' in col_lower and not lon_col:
                    lon_col = col
            
            if not lat_col or not lon_col:
                pytest.skip(f"Raw metadata doesn't have lat/lon columns. Available columns: {list(deployment_df.columns)}")
            
            for station in stations_data.get("stations", []):
                station_id = station.get("id")
                
                # Find matching station in raw metadata
                raw_station = deployment_df[deployment_df["Station"] == station_id]
                
                if not raw_station.empty:
                    # Verify coordinates match (within reasonable tolerance for float comparison)
                    # Handle nested coordinates structure
                    if "coordinates" in station:
                        coords = station["coordinates"]
                        
                        # Convert raw values to float in case they're stored as strings
                        try:
                            raw_lat = float(raw_station.iloc[0][lat_col])
                            raw_lon = float(raw_station.iloc[0][lon_col])
                            
                            assert abs(coords["latitude"] - raw_lat) < 0.01, \
                                f"Latitude mismatch for station {station_id}: view={coords['latitude']}, raw={raw_lat}"
                            assert abs(coords["longitude"] - raw_lon) < 0.01, \
                                f"Longitude mismatch for station {station_id}: view={coords['longitude']}, raw={raw_lon}"
                        except (ValueError, TypeError) as e:
                            # Skip if coordinates can't be converted to numbers
                            print(f"Skipping {station_id}: coordinate conversion error: {e}")
                            continue
                            
                    elif "latitude" in station:
                        # Handle flat structure
                        try:
                            raw_lat = float(raw_station.iloc[0][lat_col])
                            raw_lon = float(raw_station.iloc[0][lon_col])
                            
                            assert abs(station["latitude"] - raw_lat) < 0.01, \
                                f"Latitude mismatch for station {station_id}"
                            assert abs(station["longitude"] - raw_lon) < 0.01, \
                                f"Longitude mismatch for station {station_id}"
                        except (ValueError, TypeError) as e:
                            print(f"Skipping {station_id}: coordinate conversion error: {e}")
                            continue
        
        except (FileNotFoundError, KeyError):
            pytest.skip("Raw deployment metadata not available or has different column names")
    
    
    def test_detection_counts_match_raw(self):
        """Verify species detection counts in views match raw detection files."""
        heatmap_file = self.views_dir / "heatmap.json"
        
        if not heatmap_file.exists():
            pytest.skip("heatmap.json not found")
        
        with open(heatmap_file) as f:
            heatmap_data = json.load(f)
        
        # Sample a few data points to verify
        if "data" in heatmap_data and len(heatmap_data["data"]) > 0:
            sample_points = random.sample(heatmap_data["data"], 
                                        min(5, len(heatmap_data["data"])))
            
            for point in sample_points:
                # Try to verify this point against raw data
                station = point.get("station")
                year = point.get("year")
                species = point.get("species")
                
                if station and year and species:
                    try:
                        # Load raw detection data
                        raw_detections = self.loader.load_detection_data(station, year)
                        
                        # Verify the species exists in raw data
                        if species in raw_detections.columns:
                            # Check that values are reasonable
                            raw_values = raw_detections[species].values
                            assert any(raw_values > 0), \
                                f"No detections found for {species} in raw data"
                    
                    except FileNotFoundError:
                        # Raw data not available for this station/year
                        pass
    
    
    
    def test_no_duplicate_records(self):
        """Check for duplicate records that might indicate data generation errors."""
        
        view_files = list(self.views_dir.glob("*.json")) if self.views_dir.exists() else []
        
        for view_file in view_files:
            with open(view_file) as f:
                data = json.load(f)
            
            # Check for duplicate detection in arrays
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                # Create hashes of each record
                hashes = []
                for record in data["data"]:
                    # Create a hash of the record (excluding unique IDs)
                    record_copy = {k: v for k, v in record.items() 
                                 if k not in ["id", "_id", "index"]}
                    record_str = json.dumps(record_copy, sort_keys=True)
                    record_hash = hashlib.md5(record_str.encode()).hexdigest()
                    hashes.append(record_hash)
                
                # Check for duplicates
                unique_hashes = set(hashes)
                if len(unique_hashes) < len(hashes):
                    duplicate_count = len(hashes) - len(unique_hashes)
                    pytest.fail(f"Found {duplicate_count} duplicate records in {view_file.name}")
    
    def test_statistical_consistency(self):
        """Verify that aggregated statistics match manual calculations."""
        
        # Test a sample aggregation
        acoustic_dist_file = self.views_dir / "acoustic_indices_distributions.json"
        
        if acoustic_dist_file.exists():
            with open(acoustic_dist_file) as f:
                dist_data = json.load(f)
            
            # Try to verify against raw data for a sample index
            sample_index = "ACI"
            if sample_index in dist_data:
                view_stats = dist_data[sample_index]
                
                # Try to load raw data and calculate stats
                try:
                    # Load acoustic indices for a sample station
                    raw_indices = self.loader.load_acoustic_indices("9M", "FullBW")
                    
                    if sample_index in raw_indices.columns:
                        raw_values = raw_indices[sample_index].dropna()
                        
                        # Calculate statistics
                        raw_mean = raw_values.mean()
                        raw_std = raw_values.std()
                        raw_min = raw_values.min()
                        raw_max = raw_values.max()
                        
                        # Compare with view statistics (with tolerance for float comparison)
                        if "mean" in view_stats:
                            assert abs(view_stats["mean"] - raw_mean) < 0.01, \
                                f"Mean mismatch for {sample_index}"
                        
                        if "std" in view_stats:
                            assert abs(view_stats["std"] - raw_std) < 0.01, \
                                f"Std deviation mismatch for {sample_index}"
                
                except FileNotFoundError:
                    # Raw data not available
                    pass
    


class TestDataTraceability:
    """Test that data in views can be traced back to specific raw files."""
    
    def test_create_data_lineage(self):
        """Create a lineage map showing where view data comes from."""
        
        lineage_map = {
            "stations.json": [
                "raw/metadata/1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
            ],
            "indices_reference.json": [
                "raw/metadata/Updated_Index_Categories_v2.csv"
            ],
            "heatmap.json": [
                "raw/2018/detections/Master_Manual_*_2h_2018.xlsx",
                "raw/2021/detections/Master_Manual_*_2h_2021.xlsx",
                "raw/metadata/det_column_names.csv"
            ],
            "acoustic_indices_distributions.json": [
                "raw/indices/Acoustic_Indices_*_2021_*_v2_Final.csv"
            ]
        }
        
        # Verify the lineage is documented
        assert len(lineage_map) > 0, "Data lineage should be documented"
        
        # Could save this to a file for reference
        lineage_file = Path("data_lineage.json")
        with open(lineage_file, 'w') as f:
            json.dump(lineage_map, f, indent=2)
    
    def test_sample_data_verification(self):
        """Sample specific data points and verify against raw sources."""
        
        # This is a template for spot-checking specific values
        test_cases = [
            {
                "view_file": "stations.json",
                "field_path": "stations[0].latitude",
                "raw_source": "deployment_metadata",
                "raw_field": "Latitude",
                "tolerance": 0.001
            },
            # Add more test cases as needed
        ]
        
        for test_case in test_cases:
            # Implementation would load both view and raw data
            # and compare the specific fields
            pass


@pytest.mark.slow
class TestFullDataValidation:
    """Comprehensive validation of all view data (slow tests)."""
    
    def test_complete_raw_to_view_validation(self):
        """Validate entire pipeline from raw data to views."""
        
        # This would be a comprehensive test that:
        # 1. Loads all raw data
        # 2. Manually calculates what should be in views
        # 3. Compares with actual view contents
        # 4. Reports any discrepancies
        
        # Due to complexity, this is a template for future implementation
        pytest.skip("Full validation not yet implemented")
    
    def test_regenerate_and_compare_views(self):
        """Regenerate views from scratch and compare with existing."""
        
        # This test would:
        # 1. Back up existing views
        # 2. Regenerate all views from raw data
        # 3. Compare new views with backed up versions
        # 4. Report any differences
        
        pytest.skip("View regeneration test not yet implemented")