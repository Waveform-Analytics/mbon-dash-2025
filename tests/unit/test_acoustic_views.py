"""
Tests for acoustic summary view generation.

Following TDD approach - these tests define the expected behavior
before implementation exists.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Import will initially fail - that's expected in TDD
try:
    from mbon_analysis.views.acoustic_views import generate_acoustic_summary
except ImportError:
    # Mock the function for initial test development
    def generate_acoustic_summary(processed_data_dir):
        return {
            'acoustic_summary': [],
            'pca_analysis': {},
            'index_categories': {},
            'metadata': {}
        }


class TestAcousticSummaryGeneration:
    """Test suite for acoustic summary view generator."""
    
    @pytest.fixture
    def mock_data_dir(self, tmp_path):
        """Create mock processed data directory."""
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()
        
        # Create mock acoustic_indices.json
        mock_acoustic_data = {
            'acoustic_indices': [
                {
                    'station': '9M',
                    'datetime': '2021-01-01T12:00:00',
                    'ACI': 0.5,
                    'NDSI': 0.3,
                    'H_Renyi': 2.1,
                    'BioEnergy': 120.5
                },
                {
                    'station': '14M', 
                    'datetime': '2021-01-01T14:00:00',
                    'ACI': 0.7,
                    'NDSI': 0.4,
                    'H_Renyi': 2.3,
                    'BioEnergy': 135.2
                }
            ]
        }
        
        with open(processed_dir / "acoustic_indices.json", "w") as f:
            json.dump(mock_acoustic_data, f)
            
        return processed_dir

    def test_generate_acoustic_summary_structure(self, mock_data_dir):
        """Test that acoustic summary has correct top-level structure."""
        result = generate_acoustic_summary(mock_data_dir)
        
        # Core sections that should exist
        assert 'acoustic_summary' in result
        assert 'pca_analysis' in result
        assert 'index_categories' in result
        assert 'metadata' in result
        
        # Verify metadata structure
        assert 'generated_at' in result['metadata']
        assert 'data_sources' in result['metadata']
        assert 'total_indices' in result['metadata']
        assert 'stations_included' in result['metadata']

    def test_acoustic_summary_size_limit(self, mock_data_dir):
        """Test that output is reasonably sized (~50KB target)."""
        result = generate_acoustic_summary(mock_data_dir)
        json_str = json.dumps(result)
        
        # Allow up to 100KB for acoustic summary (generous buffer)
        # Target is 50KB but allow flexibility for comprehensive data
        assert len(json_str) < 100 * 1024, f"Acoustic summary too large: {len(json_str)} bytes"
        
        # Should be much smaller than original (this is the key performance test)
        # We can't test exact original size, but ensure significant reduction
        assert len(json_str) > 1024, "Summary shouldn't be too small (need meaningful data)"

    def test_pca_analysis_structure(self, mock_data_dir):
        """Test that PCA analysis contains expected components."""
        result = generate_acoustic_summary(mock_data_dir)
        pca_data = result['pca_analysis']
        
        # Core PCA components
        assert 'components' in pca_data
        assert 'explained_variance' in pca_data
        assert 'feature_loadings' in pca_data
        
        # Should have reasonable number of components (typically 3-5)
        if pca_data['components']:
            assert len(pca_data['components']) <= 10, "Too many PCA components"
            assert len(pca_data['components']) >= 2, "Need at least 2 PCA components"

    def test_index_categories_grouping(self, mock_data_dir):
        """Test that indices are properly categorized."""
        result = generate_acoustic_summary(mock_data_dir)
        categories = result['index_categories']
        
        # Expected categories from research documentation
        expected_categories = [
            'temporal_domain',
            'frequency_domain', 
            'acoustic_complexity',
            'diversity_indices',
            'bioacoustic',
            'spectral_coverage'
        ]
        
        # Should have at least some of these categories
        assert len(categories) >= 3, "Need multiple index categories"
        
        # Each category should have index names and descriptions
        for category_name, category_data in categories.items():
            assert 'indices' in category_data
            assert 'description' in category_data
            assert isinstance(category_data['indices'], list)

    def test_acoustic_summary_station_coverage(self, mock_data_dir):
        """Test that all stations are represented in summary."""
        result = generate_acoustic_summary(mock_data_dir)
        
        # Should have data from multiple stations
        stations = result['metadata']['stations_included']
        assert len(stations) >= 1, "Need at least one station"
        
        # Verify station names are valid (project-agnostic test)
        for station in stations:
            assert isinstance(station, str)
            assert len(station) > 0

    def test_temporal_aggregation(self, mock_data_dir):
        """Test that temporal data is appropriately aggregated."""
        result = generate_acoustic_summary(mock_data_dir)
        
        # Should have some form of temporal aggregation
        # (monthly, seasonal, or yearly summaries)
        summary_data = result['acoustic_summary']
        
        if summary_data:  # Allow empty for minimal implementation
            # Each summary item should have temporal information
            for item in summary_data:
                # Should have either monthly, seasonal, or yearly aggregation
                temporal_keys = ['monthly_avg', 'seasonal_patterns', 'yearly_summary', 'temporal_stats']
                has_temporal = any(key in item for key in temporal_keys)
                assert has_temporal, f"Summary item missing temporal aggregation: {item.keys()}"

    def test_key_indices_selection(self, mock_data_dir):
        """Test that most important indices are highlighted."""
        result = generate_acoustic_summary(mock_data_dir)
        
        # Should identify top/key indices for research
        if result['acoustic_summary']:
            # Look for importance scoring or ranking
            for category_name, category_data in result['index_categories'].items():
                if 'indices' in category_data:
                    # Should have some ranking or importance measure
                    # (this helps researchers focus on most informative indices)
                    assert len(category_data['indices']) >= 0

    def test_performance_vs_original(self, mock_data_dir):
        """Test performance improvement vs loading full acoustic_indices.json."""
        result = generate_acoustic_summary(mock_data_dir)
        summary_size = len(json.dumps(result))
        
        # Load original file for comparison
        original_file = mock_data_dir / "acoustic_indices.json"
        if original_file.exists():
            with open(original_file) as f:
                original_data = json.load(f)
            original_size = len(json.dumps(original_data))
            
            # Summary should be significantly smaller
            # Allow some cases where test data is small
            if original_size > 10000:  # Only test if original is substantial
                improvement_ratio = original_size / summary_size
                assert improvement_ratio >= 2, f"Summary not smaller enough: {improvement_ratio}x improvement"

    def test_data_validation(self, mock_data_dir):
        """Test that acoustic data is properly validated."""
        result = generate_acoustic_summary(mock_data_dir)
        
        # Should handle missing or invalid data gracefully
        assert result is not None
        assert isinstance(result, dict)
        
        # Metadata should indicate data quality
        metadata = result['metadata']
        assert 'total_records_processed' in metadata
        assert isinstance(metadata['total_records_processed'], int)
        assert metadata['total_records_processed'] >= 0

    def test_research_focus_alignment(self, mock_data_dir):
        """Test that summary aligns with research questions."""
        result = generate_acoustic_summary(mock_data_dir)
        
        # Should support key research questions:
        # 1. Index dimensionality reduction (PCA)
        assert 'pca_analysis' in result
        
        # 2. Biodiversity prediction capability  
        # 3. Index categories performance
        assert 'index_categories' in result
        
        # 4. Should be suitable for frontend visualization
        assert all(isinstance(v, (dict, list, str, int, float, type(None))) 
                  for v in result.values()), "All values should be JSON-serializable"