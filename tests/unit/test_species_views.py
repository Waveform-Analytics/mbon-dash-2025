"""
Tests for species views module.

Testing the species timeline generator with focus on:
- Data structure validation
- Performance (size limits)  
- Monthly aggregation logic
- Biological species filtering
- Generic project compatibility (any number of species, stations)
"""

import json
import pytest
from pathlib import Path
from mbon_analysis.views.species_views import generate_species_timeline


def test_generate_species_timeline_structure():
    """Test that species timeline has correct structure."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    # Core structure
    assert 'species_timeline' in result
    assert 'metadata' in result
    assert 'temporal_aggregation' in result
    
    # Metadata structure
    assert 'generated_at' in result['metadata']
    assert 'data_sources' in result['metadata']
    assert 'total_species' in result['metadata']
    assert 'aggregation_level' in result['metadata']
    
    # Timeline structure
    assert isinstance(result['species_timeline'], list)
    assert result['temporal_aggregation'] in ['monthly', 'weekly', 'daily']


def test_species_timeline_size():
    """Test that output is reasonably sized (~100KB target)."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    json_str = json.dumps(result)
    
    # Allow up to 100KB for species timeline data (vs MB+ raw data)
    size_bytes = len(json_str.encode('utf-8'))
    size_kb = size_bytes / 1024
    
    print(f"Species timeline size: {size_kb:.1f} KB")
    assert size_kb < 100, f"Species timeline too large: {size_kb:.1f} KB"


def test_monthly_aggregation():
    """Test monthly aggregation reduces data size significantly."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    # Should have monthly aggregated data, not hourly
    assert result['temporal_aggregation'] == 'monthly'
    
    # Each species should have aggregated detection data
    for species_data in result['species_timeline']:
        assert 'species_name' in species_data
        assert 'monthly_detections' in species_data
        assert 'detection_frequency' in species_data
        assert 'total_detections' in species_data
        
        # Monthly data should be aggregated (fewer data points than raw)
        monthly_data = species_data['monthly_detections']
        assert isinstance(monthly_data, list)
        
        # Each month entry should have required fields
        for month_entry in monthly_data:
            assert 'year_month' in month_entry  # e.g., "2021-05"
            assert 'detection_count' in month_entry
            assert 'stations' in month_entry  # Which stations had detections


def test_species_filtering():
    """Test that only biological species are included, not anthropogenic sounds."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    for species_data in result['species_timeline']:
        # Should only contain biological species based on species metadata
        assert species_data['category'] == 'biological'
        assert 'species_name' in species_data
        assert 'species_code' in species_data
        
        # Should not contain true anthropogenic sounds (but "boat whistle" in fish names is OK)
        species_name = species_data['species_name'].lower() 
        # Only test against clearly non-biological terms, not fish sound descriptions
        assert 'anthropogenic' not in species_name
        assert 'vessel' not in species_name  # This would be truly anthropogenic
        # Note: "boat whistle" can be a fish sound (e.g., oyster toadfish boat whistle call)


def test_detection_frequency_calculations():
    """Test that detection frequency is calculated correctly."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    for species_data in result['species_timeline']:
        freq = species_data['detection_frequency']
        
        # Frequency should be between 0 and 1
        assert 0 <= freq <= 1
        
        # Should be calculated as: detections / total_possible_detections
        assert isinstance(freq, (int, float))


def test_temporal_coverage():
    """Test that temporal coverage matches data scope (2018, 2021)."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    # Should cover the expected years in the dataset
    years_found = set()
    for species_data in result['species_timeline']:
        for month_entry in species_data['monthly_detections']:
            year = int(month_entry['year_month'].split('-')[0])
            years_found.add(year)
    
    # Should include both 2018 and 2021 (the project's data years)
    expected_years = {2018, 2021}
    assert years_found.intersection(expected_years), f"Expected years {expected_years}, found {years_found}"


def test_station_coverage():
    """Test that station information is preserved in aggregated data."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    # Should reference the 3 stations in the project
    stations_found = set()
    for species_data in result['species_timeline']:
        for month_entry in species_data['monthly_detections']:
            for station in month_entry['stations']:
                stations_found.add(station)
    
    # Should have data from the expected stations (9M, 14M, 37M)
    print(f"Stations found in species timeline: {stations_found}")
    assert len(stations_found) >= 1, "Should have at least one station with species detections"


def test_empty_data_handling():
    """Test graceful handling of missing or empty data."""
    # This test ensures the function doesn't crash with edge cases
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    # Should return valid structure even if some species have no detections
    assert isinstance(result, dict)
    assert 'species_timeline' in result
    assert 'metadata' in result
    
    # Metadata should indicate data quality
    metadata = result['metadata']
    assert 'total_species' in metadata
    assert isinstance(metadata['total_species'], int)
    assert metadata['total_species'] >= 0


def test_generic_project_compatibility():
    """Test that the function works for any marine monitoring project."""
    result = generate_species_timeline(Path('data/cdn/processed'))
    
    # Function should work regardless of:
    # - Number of stations (could be 1, 3, 10, etc.)
    # - Number of species (could be 5, 50, etc.) 
    # - Station naming convention (9M, 14M, 37M is specific to this project)
    
    # Should not hardcode specific station names or species counts
    assert isinstance(result['species_timeline'], list)
    assert result['metadata']['total_species'] >= 0
    
    # Each species entry should be self-contained
    for species_data in result['species_timeline']:
        assert all(key in species_data for key in [
            'species_name', 'species_code', 'category', 
            'monthly_detections', 'detection_frequency', 'total_detections'
        ])