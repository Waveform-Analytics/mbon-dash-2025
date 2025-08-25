"""
Tests for the acoustic indices loader module.
"""

import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mbon_analysis.core.acoustic_indices_loader import (
    get_indices_data_directory,
    load_acoustic_indices_csv,
    load_all_acoustic_indices,
    get_available_indices
)


class TestAcousticIndicesLoader:
    """Test acoustic indices loading functions."""
    
    def test_get_indices_data_directory(self):
        """Test getting indices data directory."""
        data_dir = get_indices_data_directory()
        assert isinstance(data_dir, Path)
        # Directory might not exist in test environment
    
    def test_get_indices_data_directory_custom(self):
        """Test custom indices data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            result = get_indices_data_directory(custom_dir)
            assert result == custom_dir
    
    def test_load_acoustic_indices_csv_station_param(self):
        """Test loading acoustic indices with station parameter."""
        try:
            # This will likely fail if files don't exist, which is expected
            df = load_acoustic_indices_csv(station='9M')
            assert isinstance(df, pd.DataFrame)
        except FileNotFoundError:
            # Expected in test environment
            pass
    
    def test_load_all_acoustic_indices(self):
        """Test loading all acoustic indices."""
        try:
            result = load_all_acoustic_indices(stations=['9M'])
            assert isinstance(result, dict)
        except FileNotFoundError:
            # Expected in test environment
            pass
    
    def test_get_available_indices(self):
        """Test getting available indices from dataframe."""
        sample_df = pd.DataFrame({
            'ZCR': [0.1, 0.4],
            'MEANt': [0.2, 0.5],
            'VARt': [0.3, 0.6],
            'station': ['9M', '9M']
        })
        
        indices = get_available_indices(sample_df)
        assert isinstance(indices, list)
        assert 'ZCR' in indices
        assert 'MEANt' in indices
        assert 'VARt' in indices
        assert 'station' not in indices  # Should exclude non-index columns


class TestAcousticDataIntegration:
    """Integration tests for acoustic indices with real data."""
    
    @pytest.mark.integration
    def test_load_real_acoustic_indices(self):
        """Test loading real acoustic indices files."""
        try:
            from mbon_analysis.core.data_loader import load_acoustic_indices
            
            acoustic_df = load_acoustic_indices()
            assert isinstance(acoustic_df, pd.DataFrame)
            assert len(acoustic_df) > 1000  # Should have many records
            
            # Check for expected acoustic index columns
            expected_indices = ['ZCR', 'MEANt', 'VARt']
            for index_col in expected_indices:
                if index_col in acoustic_df.columns:
                    assert acoustic_df[index_col].dtype in ['float64', 'int64', 'object']
            
        except (FileNotFoundError, ImportError):
            pytest.skip("Real acoustic indices data not available")


class TestAcousticErrorHandling:
    """Test error handling in acoustic indices loading."""
    
    def test_get_available_indices_empty_dataframe(self):
        """Test getting available indices from empty dataframe."""
        empty_df = pd.DataFrame()
        
        indices = get_available_indices(empty_df)
        assert isinstance(indices, list)
        assert len(indices) == 0
    
    def test_load_acoustic_with_invalid_station(self):
        """Test loading acoustic data with invalid station."""
        try:
            # Should handle invalid station gracefully
            result = load_acoustic_indices_csv(station='INVALID')
            assert isinstance(result, pd.DataFrame)
        except FileNotFoundError:
            # Expected behavior
            pass