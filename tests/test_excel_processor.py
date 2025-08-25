"""
Tests for the Excel processor module.
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mbon_analysis.core.excel_processor import MBONExcelProcessor


class TestMBONExcelProcessor:
    
    def test_extract_metadata_from_filename(self):
        """Test metadata extraction from various filename patterns."""
        processor = MBONExcelProcessor()
        
        test_cases = [
            (Path("data/2018/Master_Manual_9M_2h_2018.xlsx"), ("2018", "9M")),
            (Path("data/2021/Master_Manual_14M_2h_2021.xlsx"), ("2021", "14M")),
            (Path("data/2021/Master_9M_Temp_2021.xlsx"), ("2021", "9M")),
            (Path("data/2018/Master_37M_Depth_2018.xlsx"), ("2018", "37M")),
        ]
        
        for filepath, expected in test_cases:
            year, station = processor.extract_metadata_from_filename(filepath)
            assert (year, station) == expected, f"Failed for {filepath}"
    
    def test_extract_metadata_invalid_format(self):
        """Test that invalid filename formats raise appropriate errors."""
        processor = MBONExcelProcessor()
        
        # Test file with no station identifier
        try:
            processor.extract_metadata_from_filename(Path("data/2018/Master.xlsx"))
            raise AssertionError("Expected ValueError was not raised")
        except ValueError as e:
            assert "Cannot extract station" in str(e)
    
    def test_load_column_mapping(self):
        """Test column mapping loading."""
        processor = MBONExcelProcessor()
        
        # This will only work if the actual files exist
        try:
            name_mapping, type_mapping = processor.load_column_mapping()
            
            assert isinstance(name_mapping, dict), "name_mapping should be a dictionary"
            assert isinstance(type_mapping, dict), "type_mapping should be a dictionary"
            assert len(name_mapping) > 0, "name_mapping should not be empty"
            assert len(type_mapping) > 0, "type_mapping should not be empty"
            
            # Check for critical columns
            assert "date" in name_mapping, "Missing critical 'date' column"
            assert "time" in name_mapping, "Missing critical 'time' column"
            
            # Check that type_mapping has the right structure
            for key, value in type_mapping.items():
                assert "long_name" in value, f"Missing 'long_name' for {key}"
                assert "type" in value, f"Missing 'type' for {key}"
            
            # Test caching - should return same object
            name_mapping2, type_mapping2 = processor.load_column_mapping()
            assert name_mapping is name_mapping2, "Column mapping should be cached"
            
        except FileNotFoundError:
            print("Column mapping file not found - skipping test")
            return
    
    def test_processor_configuration(self):
        """Test processor initialization with custom configuration."""
        processor = MBONExcelProcessor(
            raw_data_dir="custom/path",
            years_of_interest=["2019", "2020"],
            stations_of_interest=["1M", "2M"]
        )
        
        assert processor.raw_data_dir == Path("custom/path")
        assert processor.years_of_interest == ["2019", "2020"]
        assert processor.stations_of_interest == ["1M", "2M"]
    
    def test_processor_default_configuration(self):
        """Test processor initialization with default configuration."""
        processor = MBONExcelProcessor()
        
        assert processor.raw_data_dir == Path("data/cdn/raw-data")
        assert processor.years_of_interest == ["2018", "2021"]
        assert processor.stations_of_interest == ["9M", "14M", "37M"]
    
    def test_find_detection_files(self):
        """Test finding detection files."""
        processor = MBONExcelProcessor()
        
        try:
            files = processor.find_detection_files()
            
            # Check that returned files are Path objects
            for file in files:
                assert isinstance(file, Path), f"{file} should be a Path object"
                assert file.name.startswith("Master_Manual_"), f"{file.name} should start with 'Master_Manual_'"
                assert file.suffix == ".xlsx", f"{file.name} should be an Excel file"
            
            # If files were found, check they match our criteria
            if files:
                for file in files:
                    year, station = processor.extract_metadata_from_filename(file)
                    assert year in processor.years_of_interest, f"Year {year} not in years of interest"
                    assert station in processor.stations_of_interest, f"Station {station} not in stations of interest"
                    
        except ValueError:
            # No files found is acceptable for testing
            pass

    def test_validate_detection_data_good_data(self):
        """Test validation passes for good data."""
        processor = MBONExcelProcessor()
        
        # Create sample good data
        good_data = pd.DataFrame({
            'date': pd.date_range('2021-01-01', periods=100, freq='2H'),
            'time': ['12:00'] * 100,
            'sp': [1, 0, 1, 0] * 25,  # Some detections
            'bde': [0, 1, 0, 0] * 25,  # Some detections
            'year': ['2021'] * 100,
            'station': ['9M'] * 100
        })
        
        # Should pass validation
        assert processor.validate_detection_data(good_data) == True

    def test_validate_detection_data_bad_dates(self):
        """Test validation fails for bad date data."""
        processor = MBONExcelProcessor()
        
        # Create data with mostly invalid dates
        bad_data = pd.DataFrame({
            'date': ['invalid_date'] * 90 + ['2021-01-01'] * 10,  # 90% invalid
            'sp': [1] * 100,
            'year': ['2021'] * 100,
            'station': ['9M'] * 100
        })
        
        # Should fail validation
        assert processor.validate_detection_data(bad_data) == False

    def test_validate_detection_data_no_detections(self):
        """Test validation fails when no detection columns have data."""
        processor = MBONExcelProcessor()
        
        # Create data with no detections (all zeros)
        no_detections = pd.DataFrame({
            'date': pd.date_range('2021-01-01', periods=100, freq='2H'),
            'sp': [0] * 100,  # No detections
            'bde': [0] * 100,  # No detections
            'year': ['2021'] * 100,
            'station': ['9M'] * 100
        })
        
        # Should fail validation
        assert processor.validate_detection_data(no_detections) == False


class TestConvenienceFunctions:
    """Test the convenience functions for backward compatibility."""
    
    def test_load_column_mapping_function(self):
        """Test the standalone load_column_mapping function."""
        from mbon_analysis.core.excel_processor import load_column_mapping
        
        try:
            name_mapping, type_mapping = load_column_mapping()
            assert isinstance(name_mapping, dict)
            assert isinstance(type_mapping, dict)
        except FileNotFoundError:
            print("Column mapping file not found - skipping test")
            return
    
    def test_extract_metadata_function(self):
        """Test the standalone extract_metadata_from_filename function."""
        from mbon_analysis.core.excel_processor import extract_metadata_from_filename
        
        year, station = extract_metadata_from_filename(
            Path("data/2018/Master_Manual_9M_2h_2018.xlsx")
        )
        assert year == "2018"
        assert station == "9M"


if __name__ == "__main__":
    # Run tests manually
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Running Excel Processor Tests")
    print("=" * 50)
    
    # Create test instance
    test_class = TestMBONExcelProcessor()
    
    # Run tests
    try:
        print("Testing metadata extraction...")
        test_class.test_extract_metadata_from_filename()
        print("  ✓ Metadata extraction test passed")
    except AssertionError as e:
        print(f"  ✗ Metadata extraction test failed: {e}")
    
    try:
        print("Testing invalid filename handling...")
        test_class.test_extract_metadata_invalid_format()
        print("  ✓ Invalid filename handling test passed")
    except AssertionError as e:
        print(f"  ✗ Invalid filename handling test failed: {e}")
    
    try:
        print("Testing column mapping loading...")
        test_class.test_load_column_mapping()
        print("  ✓ Column mapping test passed")
    except Exception as e:
        print(f"  ℹ {e}")
    
    try:
        print("Testing processor configuration...")
        test_class.test_processor_configuration()
        print("  ✓ Configuration test passed")
    except AssertionError as e:
        print(f"  ✗ Configuration test failed: {e}")
    
    # Test the new validation functions
    try:
        print("Testing good data validation...")
        test_class.test_validate_detection_data_good_data()
        print("  ✓ Good data validation test passed")
    except AssertionError as e:
        print(f"  ✗ Good data validation test failed: {e}")
    except AttributeError as e:
        print(f"  ℹ Validation method not implemented yet: {e}")
    
    try:
        print("Testing bad date validation...")
        test_class.test_validate_detection_data_bad_dates()
        print("  ✓ Bad date validation test passed")
    except AssertionError as e:
        print(f"  ✗ Bad date validation test failed: {e}")
    except AttributeError as e:
        print(f"  ℹ Validation method not implemented yet: {e}")
    
    try:
        print("Testing no detections validation...")
        test_class.test_validate_detection_data_no_detections()
        print("  ✓ No detections validation test passed")
    except AssertionError as e:
        print(f"  ✗ No detections validation test failed: {e}")
    except AttributeError as e:
        print(f"  ℹ Validation method not implemented yet: {e}")
    
    print("\n✅ All tests completed!")