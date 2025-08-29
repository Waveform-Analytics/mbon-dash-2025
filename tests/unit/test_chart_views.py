"""
Tests for chart view generators.

This module tests view generators that create optimized data files for chart components.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_data_dir():
    """Mock data directory for testing."""
    return Path("data/cdn/processed")


class TestRawDataLandscape:
    """Tests for generate_raw_data_landscape() function."""
    
    def test_generate_raw_data_landscape_structure(self, mock_data_dir):
        """Test that raw data landscape has correct structure."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        
        # Required top-level keys
        assert 'raw_data_landscape' in result
        landscape = result['raw_data_landscape']
        
        assert 'indices_overview' in landscape
        assert 'summary_stats' in landscape  
        assert 'datasets_info' in landscape
        assert 'metadata' in result
        
    def test_generate_raw_data_landscape_size(self, mock_data_dir):
        """Test that output is reasonably sized for performance."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        json_str = json.dumps(result)
        
        # Target < 50KB for chart performance
        assert len(json_str) < 50 * 1024, f"Output size {len(json_str)} bytes exceeds 50KB limit"
        
    def test_index_availability_matrix(self, mock_data_dir):
        """Test availability data for each index/station combination."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        indices_overview = result['raw_data_landscape']['indices_overview']
        
        # Each index should have availability data
        for index in indices_overview:
            assert 'index' in index
            assert 'category' in index
            assert 'availability' in index
            assert isinstance(index['availability'], dict)
            
    def test_datasets_info_structure(self, mock_data_dir):
        """Test datasets_info has station and bandwidth information."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        datasets_info = result['raw_data_landscape']['datasets_info']
        
        # Should have dataset keys with station/bandwidth info
        assert len(datasets_info) > 0
        for dataset_key, info in datasets_info.items():
            assert 'station' in info
            assert 'bandwidth' in info
            
    def test_summary_stats_present(self, mock_data_dir):
        """Test that summary statistics are included."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        summary_stats = result['raw_data_landscape']['summary_stats']
        
        assert 'total_indices' in summary_stats
        assert 'total_datasets' in summary_stats
        assert 'coverage_summary' in summary_stats
        
    def test_metadata_included(self, mock_data_dir):
        """Test that metadata is properly included."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        metadata = result['metadata']
        
        assert 'generated_at' in metadata
        assert 'data_sources' in metadata
        assert 'view_type' in metadata
        assert metadata['view_type'] == 'raw_data_landscape'
        
    def test_index_categories_valid(self, mock_data_dir):
        """Test that index categories are valid."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        indices_overview = result['raw_data_landscape']['indices_overview']
        
        valid_categories = [
            'complexity', 'diversity', 'temporal', 'spectral', 'amplitude', 'other'
        ]
        
        for index in indices_overview:
            assert index['category'] in valid_categories
            
    def test_availability_coverage_percentages(self, mock_data_dir):
        """Test that coverage percentages are reasonable."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        indices_overview = result['raw_data_landscape']['indices_overview']
        
        for index in indices_overview:
            for dataset_key, availability in index['availability'].items():
                if 'coverage_pct' in availability:
                    coverage = availability['coverage_pct']
                    assert 0 <= coverage <= 100, f"Coverage {coverage}% not in valid range"
                    
    def test_n_values_are_positive(self, mock_data_dir):
        """Test that n_values are positive integers when present."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        indices_overview = result['raw_data_landscape']['indices_overview']
        
        for index in indices_overview:
            for dataset_key, availability in index['availability'].items():
                if 'n_values' in availability:
                    n_values = availability['n_values']
                    assert isinstance(n_values, int)
                    assert n_values >= 0
                    
    def test_project_agnostic_design(self, mock_data_dir):
        """Test that function works with any number of stations."""
        from mbon_analysis.views.chart_views import generate_raw_data_landscape
        
        result = generate_raw_data_landscape(mock_data_dir)
        
        # Should work regardless of number of stations
        datasets_info = result['raw_data_landscape']['datasets_info']
        assert len(datasets_info) >= 0  # Could be 0, 3, or any number
        
        # If datasets exist, they should follow expected structure
        if len(datasets_info) > 0:
            for dataset_key, info in datasets_info.items():
                assert isinstance(info['station'], str)
                assert info['bandwidth'] in ['FullBW', '8kHz', 'fullBW']  # Accept variations


# ============================================================================
# Index Distributions View Tests
# ============================================================================

def test_generate_index_distributions_structure(mock_data_dir):
    """Test that index distributions has correct structure."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    assert 'index_distributions_by_bandwidth' in result
    assert 'summary_stats_by_bandwidth' in result
    assert 'available_bandwidths' in result
    assert 'metadata' in result
    assert 'generated_at' in result


def test_generate_index_distributions_size_limit(mock_data_dir):
    """Test that index distributions output is under 150KB (still 20x smaller than source)."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    json_str = json.dumps(result)
    # Target: Under 150KB for index distributions (20x improvement from 2.8MB)
    assert len(json_str) < 150 * 1024


def test_index_distributions_bandwidth_structure(mock_data_dir):
    """Test that each bandwidth has proper structure."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    distributions = result['index_distributions_by_bandwidth']
    
    for bandwidth, analyses in distributions.items():
        assert isinstance(analyses, list)
        
        for analysis in analyses:
            # Required fields for each index analysis
            assert 'index' in analysis
            assert 'category' in analysis
            assert 'bandwidth' in analysis
            assert 'combined_stats' in analysis
            assert 'combined_density' in analysis


def test_index_distributions_combined_stats(mock_data_dir):
    """Test that combined stats contain required statistical measures."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    distributions = result['index_distributions_by_bandwidth']
    
    for bandwidth, analyses in distributions.items():
        for analysis in analyses:
            stats = analysis['combined_stats']
            
            # Statistical measures
            assert 'mean' in stats
            assert 'std' in stats
            assert 'skewness' in stats
            assert 'min' in stats
            assert 'max' in stats
            
            # Data quality measures
            assert 'zero_pct' in stats
            assert 'missing_pct' in stats
            assert 'outlier_pct' in stats
            assert 'distribution_type' in stats


def test_index_distributions_combined_density(mock_data_dir):
    """Test that combined density data is properly structured."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    distributions = result['index_distributions_by_bandwidth']
    
    for bandwidth, analyses in distributions.items():
        for analysis in analyses:
            density = analysis['combined_density']
            
            # Required density fields
            assert 'x' in density
            assert 'density' in density
            assert 'x_original' in density
            
            # Arrays should have same length
            assert len(density['x']) == len(density['density'])
            assert len(density['x']) == len(density['x_original'])


def test_index_distributions_summary_stats(mock_data_dir):
    """Test that summary stats are calculated correctly."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    summary_stats = result['summary_stats_by_bandwidth']
    
    for bandwidth, stats in summary_stats.items():
        assert 'total_indices' in stats
        assert 'categories' in stats
        assert 'quality_metrics' in stats
        
        # Quality metrics
        quality = stats['quality_metrics']
        assert 'zero_heavy_count' in quality
        assert 'missing_heavy_count' in quality


def test_index_distributions_metadata(mock_data_dir):
    """Test that metadata contains required information."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    # Check root level generated_at
    assert 'generated_at' in result
    
    # Check metadata structure
    metadata = result['metadata']
    assert 'analysis_date' in metadata
    assert 'description' in metadata
    assert 'purpose' in metadata
    assert 'total_indices_analyzed' in metadata
    assert 'datasets_included' in metadata
    assert 'bandwidths_analyzed' in metadata
    assert 'visualization_type' in metadata
    assert 'normalization' in metadata
    
    # Should indicate this is index distributions view
    assert metadata['visualization_type'] == 'probability_density_functions'


def test_index_distributions_categories(mock_data_dir):
    """Test that valid index categories are used."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    result = generate_index_distributions(mock_data_dir)
    
    valid_categories = {
        'Complexity Indices', 'Diversity Indices', 'Amplitude Indices',
        'Temporal Indices', 'Spectral Indices', 'Other Indices'
    }
    
    distributions = result['index_distributions_by_bandwidth']
    
    for bandwidth, analyses in distributions.items():
        for analysis in analyses:
            assert analysis['category'] in valid_categories


def test_index_distributions_errors(mock_data_dir):
    """Test index distributions generation with error conditions."""
    from mbon_analysis.views.chart_views import generate_index_distributions
    
    # Test with non-existent directory
    non_existent_dir = Path("/non/existent/directory")
    result = generate_index_distributions(non_existent_dir)
    
    # Should return minimal structure
    assert 'index_distributions_by_bandwidth' in result
    assert len(result['index_distributions_by_bandwidth']) == 0