"""Tests for data loading utilities."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import json

from mbon_analysis.data.loaders import DataLoader, create_loader


class TestDataLoader:
    """Test the DataLoader class."""
    
    def test_init_with_path(self, temp_data_dir):
        """Test DataLoader initialization with explicit path."""
        loader = DataLoader(temp_data_dir)
        assert loader.data_root == temp_data_dir
        assert loader.raw_data_path == temp_data_dir / "raw"
    
    def test_init_with_string_path(self, temp_data_dir):
        """Test DataLoader initialization with string path."""
        loader = DataLoader(str(temp_data_dir))
        assert loader.data_root == Path(temp_data_dir)
    
    def test_load_deployment_metadata_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing metadata file."""
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Metadata file not found"):
            loader.load_deployment_metadata()
    
    def test_load_deployment_metadata_success(self, temp_data_dir, sample_deployment_metadata):
        """Test successful loading of deployment metadata."""
        loader = DataLoader(temp_data_dir)
        
        # Create the metadata file
        metadata_file = temp_data_dir / "raw" / "metadata" / "1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
        
        # Mock pandas read_excel to return our sample data
        with patch('pandas.read_excel', return_value=sample_deployment_metadata) as mock_read:
            # Create the file so it "exists"
            metadata_file.touch()
            
            result = loader.load_deployment_metadata()
            
            # Verify the function was called with correct path
            mock_read.assert_called_once_with(metadata_file)
            
            # Verify the returned data
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'Station' in result.columns
            assert '9M' in result['Station'].values
            assert '14M' in result['Station'].values
    
    def test_load_species_mapping_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing species mapping file.""" 
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Species mapping file not found"):
            loader.load_species_mapping()
    
    def test_load_species_mapping_success(self, temp_data_dir, sample_species_mapping):
        """Test successful loading of species mapping."""
        loader = DataLoader(temp_data_dir)
        
        # Create the mapping file
        mapping_file = temp_data_dir / "raw" / "metadata" / "det_column_names.csv"
        
        # Mock pandas read_csv to return our sample data
        with patch('pandas.read_csv', return_value=sample_species_mapping) as mock_read:
            # Create the file so it "exists"
            mapping_file.touch()
            
            result = loader.load_species_mapping()
            
            # Verify the function was called with correct path
            mock_read.assert_called_once_with(mapping_file)
            
            # Verify the returned data
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 4
            assert 'short_name' in result.columns
            assert 'long_name' in result.columns
            assert 'category' in result.columns
    
    def test_load_indices_reference_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing indices reference file."""
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Indices reference file not found"):
            loader.load_indices_reference()
    
    def test_load_detection_data_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing detection file."""
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Detection file not found"):
            loader.load_detection_data("9M", 2021)
    
    def test_load_detection_data_success(self, temp_data_dir, sample_detection_data):
        """Test successful loading of detection data."""
        loader = DataLoader(temp_data_dir)
        
        # Create the detection file path
        detection_file = temp_data_dir / "raw" / "2021" / "detections" / "Master_Manual_9M_2h_2021.xlsx"
        
        # Mock pandas read_excel
        with patch('pandas.read_excel', return_value=sample_detection_data) as mock_read:
            # Create the file so it "exists"
            detection_file.touch()
            
            result = loader.load_detection_data("9M", 2021)
            
            # Verify the function was called with correct path
            mock_read.assert_called_once_with(detection_file)
            
            # Verify the returned data
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert 'Date' in result.columns
            assert 'sp' in result.columns
            assert 'otbw' in result.columns
    
    def test_load_environmental_data_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing environmental file."""
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Environmental file not found"):
            loader.load_environmental_data("9M", 2021, "Temp")
    
    def test_load_environmental_data_success(self, temp_data_dir, sample_environmental_data):
        """Test successful loading of environmental data."""
        loader = DataLoader(temp_data_dir)
        
        # Create the environmental file path
        env_file = temp_data_dir / "raw" / "2021" / "environmental" / "Master_9M_Temp_2021.xlsx"
        
        # Mock pandas read_excel
        with patch('pandas.read_excel', return_value=sample_environmental_data) as mock_read:
            # Create the file so it "exists" 
            env_file.touch()
            
            result = loader.load_environmental_data("9M", 2021, "Temp")
            
            # Verify the function was called with correct path
            mock_read.assert_called_once_with(env_file)
            
            # Verify the returned data
            assert isinstance(result, pd.DataFrame)
            assert 'Date' in result.columns
            assert 'Temperature_C' in result.columns
    
    def test_load_acoustic_indices_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing acoustic indices file."""
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Acoustic indices file not found"):
            loader.load_acoustic_indices("9M", "FullBW")
    
    def test_load_acoustic_indices_success(self, temp_data_dir, sample_acoustic_indices):
        """Test successful loading of acoustic indices."""
        loader = DataLoader(temp_data_dir)
        
        # Create the indices file path
        indices_file = temp_data_dir / "raw" / "indices" / "Acoustic_Indices_9M_2021_FullBW_v2_Final.csv"
        
        # Mock pandas read_csv
        with patch('pandas.read_csv', return_value=sample_acoustic_indices) as mock_read:
            # Create the file so it "exists"
            indices_file.touch()
            
            result = loader.load_acoustic_indices("9M", "FullBW")
            
            # Verify the function was called with correct path
            mock_read.assert_called_once_with(indices_file)
            
            # Verify the returned data
            assert isinstance(result, pd.DataFrame)
            assert 'Date' in result.columns
            assert 'ACI' in result.columns
            assert 'NDSI' in result.columns
    
    def test_load_acoustic_indices_8khz_bandwidth(self, temp_data_dir, sample_acoustic_indices):
        """Test loading acoustic indices with 8kHz bandwidth."""
        loader = DataLoader(temp_data_dir)
        
        # Create the indices file path for 8kHz
        indices_file = temp_data_dir / "raw" / "indices" / "Acoustic_Indices_9M_2021_8kHz_v2_Final.csv"
        
        # Mock pandas read_csv
        with patch('pandas.read_csv', return_value=sample_acoustic_indices) as mock_read:
            # Create the file so it "exists"
            indices_file.touch()
            
            result = loader.load_acoustic_indices("9M", "8kHz")
            
            # Verify the function was called with correct path
            mock_read.assert_called_once_with(indices_file)
    
    def test_get_available_stations(self, temp_data_dir):
        """Test getting available stations from detection files."""
        loader = DataLoader(temp_data_dir)
        
        # Create some detection files
        detection_files = [
            temp_data_dir / "raw" / "2018" / "detections" / "Master_Manual_9M_2h_2018.xlsx",
            temp_data_dir / "raw" / "2021" / "detections" / "Master_Manual_9M_2h_2021.xlsx", 
            temp_data_dir / "raw" / "2021" / "detections" / "Master_Manual_14M_2h_2021.xlsx",
            temp_data_dir / "raw" / "2021" / "detections" / "Master_Manual_37M_2h_2021.xlsx"
        ]
        
        for file_path in detection_files:
            file_path.touch()
        
        stations = loader.get_available_stations()
        
        # Should find unique stations
        assert isinstance(stations, list)
        assert len(stations) == 3
        assert '9M' in stations
        assert '14M' in stations
        assert '37M' in stations
        assert stations == sorted(stations)  # Should be sorted
    
    def test_get_available_years(self, temp_data_dir):
        """Test getting available years from directory structure.""" 
        loader = DataLoader(temp_data_dir)
        
        # Create additional year directories
        (temp_data_dir / "raw" / "2020").mkdir()
        (temp_data_dir / "raw" / "2022").mkdir()
        
        years = loader.get_available_years()
        
        # Should find all year directories (2018, 2020, 2021, 2022)
        assert isinstance(years, list) 
        assert len(years) == 4
        assert 2018 in years
        assert 2020 in years
        assert 2021 in years
        assert 2022 in years
        assert years == sorted(years)  # Should be sorted
    
    def test_load_compiled_detections_file_not_found(self, temp_data_dir):
        """Test FileNotFoundError for missing compiled detections file."""
        loader = DataLoader(temp_data_dir)
        
        with pytest.raises(FileNotFoundError, match="Compiled detections file not found"):
            loader.load_compiled_detections()
    
    def test_load_compiled_detections_success(self, temp_data_dir):
        """Test successful loading of compiled detections."""
        loader = DataLoader(temp_data_dir)
        
        # Create sample compiled data
        compiled_data = {
            "metadata": {
                "generated_at": "2024-01-01T00:00:00Z",
                "total_records": 100
            },
            "stations": {
                "9M": {
                    "2021": {
                        "detections": [
                            {"date": "2021-01-01", "sp": 1, "otbw": 0}
                        ]
                    }
                }
            }
        }
        
        # Create the compiled file
        compiled_file = temp_data_dir / "processed" / "compiled_detections.json"
        with open(compiled_file, 'w') as f:
            json.dump(compiled_data, f)
        
        result = loader.load_compiled_detections()
        
        # Verify the returned data
        assert isinstance(result, dict)
        assert 'metadata' in result
        assert 'stations' in result
        assert result['metadata']['total_records'] == 100


class TestCreateLoader:
    """Test the create_loader factory function."""
    
    def test_create_loader_with_explicit_path(self, temp_data_dir):
        """Test create_loader with explicit data root path."""
        loader = create_loader(temp_data_dir)
        
        assert isinstance(loader, DataLoader)
        assert loader.data_root == temp_data_dir
    
    def test_create_loader_with_string_path(self, temp_data_dir):
        """Test create_loader with string path."""
        loader = create_loader(str(temp_data_dir))
        
        assert isinstance(loader, DataLoader)
        assert loader.data_root == Path(temp_data_dir)
    
    def test_create_loader_default_path(self):
        """Test create_loader with default path."""
        loader = create_loader()
        
        assert isinstance(loader, DataLoader)
        # Should default to python/data directory relative to the loaders.py file
        assert loader.data_root.name == "data"


class TestDataIntegrity:
    """Test data integrity and consistency checks."""
    
    def test_detection_environmental_consistency(self, temp_data_dir):
        """Test that detection and environmental files exist for same station/year combinations."""
        loader = DataLoader(temp_data_dir)
        
        # Create detection file for 9M 2021
        detection_file = temp_data_dir / "raw" / "2021" / "detections" / "Master_Manual_9M_2h_2021.xlsx"
        detection_file.touch()
        
        # Environmental file should also exist
        temp_file = temp_data_dir / "raw" / "2021" / "environmental" / "Master_9M_Temp_2021.xlsx"
        depth_file = temp_data_dir / "raw" / "2021" / "environmental" / "Master_9M_Depth_2021.xlsx"
        
        # Test that both environmental files are expected to exist
        with pytest.raises(FileNotFoundError):
            loader.load_environmental_data("9M", 2021, "Temp")
        
        with pytest.raises(FileNotFoundError): 
            loader.load_environmental_data("9M", 2021, "Depth")
    
    @pytest.mark.parametrize("station,year", [
        ("9M", 2018),
        ("9M", 2021), 
        ("14M", 2018),
        ("14M", 2021),
        ("37M", 2018),
        ("37M", 2021)
    ])
    def test_expected_station_year_combinations(self, temp_data_dir, station, year):
        """Test that expected station/year combinations are handled correctly."""
        loader = DataLoader(temp_data_dir)
        
        # These should raise FileNotFoundError since files don't exist
        with pytest.raises(FileNotFoundError):
            loader.load_detection_data(station, year)
    
    def test_species_mapping_completeness(self, temp_data_dir, sample_species_mapping, sample_detection_data):
        """Test that all species codes in detection data have mappings."""
        loader = DataLoader(temp_data_dir)
        
        # Mock loading both files
        mapping_file = temp_data_dir / "raw" / "metadata" / "det_column_names.csv"
        detection_file = temp_data_dir / "raw" / "2021" / "detections" / "Master_Manual_9M_2h_2021.xlsx"
        
        mapping_file.touch()
        detection_file.touch()
        
        with patch('pandas.read_csv', return_value=sample_species_mapping), \
             patch('pandas.read_excel', return_value=sample_detection_data):
            
            species_mapping = loader.load_species_mapping()
            detection_data = loader.load_detection_data("9M", 2021)
            
            # Get species codes from detection data (excluding Date column)
            detection_columns = [col for col in detection_data.columns if col != 'Date']
            mapping_codes = species_mapping['short_name'].tolist()
            
            # Check that all detection columns have mappings
            for code in detection_columns:
                assert code in mapping_codes, f"Species code '{code}' not found in mapping"


@pytest.mark.integration 
class TestDataLoaderIntegration:
    """Integration tests that require actual file system operations."""
    
    def test_real_file_operations(self, temp_data_dir, sample_deployment_metadata):
        """Test actual file operations without mocking."""
        loader = DataLoader(temp_data_dir)
        
        # Create a real Excel file using pandas
        metadata_file = temp_data_dir / "raw" / "metadata" / "1_Montie Lab_metadata_deployments_2017 to 2022.xlsx"
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write sample data to actual Excel file
        sample_deployment_metadata.to_excel(metadata_file, index=False)
        
        # Load it back
        result = loader.load_deployment_metadata()
        
        # Verify the data
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'Station' in result.columns
        pd.testing.assert_frame_equal(result, sample_deployment_metadata)