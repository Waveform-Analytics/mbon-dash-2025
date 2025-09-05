#!/usr/bin/env python3
"""
Data integrity test for modeling_analysis.json view.

Tests the structure, content, and validity of the modeling analysis view
to ensure dashboard compatibility and data quality.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime


@pytest.fixture
def modeling_analysis_data():
    """Load the modeling analysis view data."""
    view_file = Path(__file__).parent.parent.parent / "data" / "views" / "modeling_analysis.json"
    
    assert view_file.exists(), f"Modeling analysis view not found at {view_file}"
    
    with open(view_file, 'r') as f:
        data = json.load(f)
    
    return data


def test_metadata_structure(modeling_analysis_data):
    """Test metadata section has required fields."""
    metadata = modeling_analysis_data['metadata']
    
    required_fields = ['generated_at', 'version', 'description', 'data_sources', 'analysis_scope']
    for field in required_fields:
        assert field in metadata, f"Missing metadata field: {field}"
    
    # Test timestamp is valid
    assert datetime.fromisoformat(metadata['generated_at'].replace('Z', '+00:00'))
    
    # Test version format
    assert isinstance(metadata['version'], str)
    assert len(metadata['version'].split('.')) == 3, "Version should be semantic (x.y.z)"


def test_dataset_summary_structure(modeling_analysis_data):
    """Test dataset summary has required information."""
    summary = modeling_analysis_data['dataset_summary']
    
    required_fields = [
        'total_records', 'date_range', 'stations', 
        'temporal_coverage', 'fish_activity_rate'
    ]
    for field in required_fields:
        assert field in summary, f"Missing dataset summary field: {field}"
    
    # Test data types
    assert isinstance(summary['total_records'], int)
    assert summary['total_records'] > 0
    
    assert isinstance(summary['stations'], list)
    assert len(summary['stations']) >= 1
    
    assert isinstance(summary['fish_activity_rate'], float)
    assert 0 <= summary['fish_activity_rate'] <= 1


def test_temporal_patterns_structure(modeling_analysis_data):
    """Test temporal patterns analysis structure."""
    patterns = modeling_analysis_data['temporal_patterns']
    
    # Test monthly patterns
    assert 'monthly_patterns' in patterns
    monthly_data = patterns['monthly_patterns']
    assert isinstance(monthly_data, list)
    assert len(monthly_data) <= 12, "Should not have more than 12 months"
    
    # Test monthly pattern fields
    required_monthly_fields = [
        'month', 'month_name', 'total_records', 
        'fish_presence_rate', 'mean_fish_intensity'
    ]
    for item in monthly_data:
        for field in required_monthly_fields:
            assert field in item, f"Missing monthly field: {field}"
        
        assert 1 <= item['month'] <= 12
        assert isinstance(item['month_name'], str)
        assert 0 <= item['fish_presence_rate'] <= 1
    
    # Test seasonal insights
    assert 'seasonal_insights' in patterns
    seasonal = patterns['seasonal_insights']
    required_seasonal_fields = [
        'peak_activity_month', 'lowest_activity_month',
        'seasonal_variation_coefficient', 'total_year_activity_rate'
    ]
    for field in required_seasonal_fields:
        assert field in seasonal, f"Missing seasonal insight: {field}"


def test_model_performance_structure(modeling_analysis_data):
    """Test model performance analysis structure."""
    performance = modeling_analysis_data['model_performance']
    
    # Test performance comparison
    assert 'performance_comparison' in performance
    comparison = performance['performance_comparison']
    assert isinstance(comparison, list)
    assert len(comparison) > 0
    
    required_performance_fields = [
        'model_type', 'target', 'f1_score', 'precision', 'recall', 'roc_auc'
    ]
    for model in comparison:
        for field in required_performance_fields:
            assert field in model, f"Missing performance field: {field}"
        
        # Test metric ranges
        assert 0 <= model['f1_score'] <= 1
        assert 0 <= model['precision'] <= 1
        assert 0 <= model['recall'] <= 1
        assert 0 <= model['roc_auc'] <= 1
        
        # Test model type values
        assert model['model_type'] in ['logistic_regression', 'random_forest']
    
    # Test feature importance
    assert 'feature_importance' in performance
    importance = performance['feature_importance']
    assert isinstance(importance, list)
    
    for item in importance:
        required_importance_fields = ['model_type', 'target', 'rank', 'feature', 'importance']
        for field in required_importance_fields:
            assert field in item, f"Missing importance field: {field}"
        
        assert item['rank'] >= 1
        assert item['feature'].startswith('PC'), "Features should be PCA components"
        assert item['importance'] >= 0
    
    # Test model insights
    assert 'model_insights' in performance
    insights = performance['model_insights']
    required_insight_fields = [
        'best_performing_model', 'best_f1_score', 'consistent_top_features'
    ]
    for field in required_insight_fields:
        assert field in insights, f"Missing insight field: {field}"
    
    assert isinstance(insights['consistent_top_features'], list)
    assert len(insights['consistent_top_features']) >= 1


def test_temporal_stratification_structure(modeling_analysis_data):
    """Test temporal stratification analysis structure."""
    stratification = modeling_analysis_data['temporal_stratification']
    
    # Test monthly distribution
    assert 'monthly_distribution' in stratification
    distribution = stratification['monthly_distribution']
    assert isinstance(distribution, list)
    
    for item in distribution:
        required_dist_fields = ['month', 'total_records', 'activity_rate']
        for field in required_dist_fields:
            assert field in item, f"Missing distribution field: {field}"
        
        assert 1 <= item['month'] <= 12
        assert item['total_records'] > 0
        assert 0 <= item['activity_rate'] <= 1
    
    # Test stratification benefits
    assert 'stratification_benefits' in stratification
    benefits = stratification['stratification_benefits']
    required_benefit_fields = [
        'overall_activity_rate', 'seasonal_variance_preserved', 'months_with_data'
    ]
    for field in required_benefit_fields:
        assert field in benefits, f"Missing benefit field: {field}"
    
    assert 0 <= benefits['overall_activity_rate'] <= 1
    assert benefits['months_with_data'] >= 1
    
    # Test methodology validation
    assert 'methodology_validation' in stratification
    validation = stratification['methodology_validation']
    required_validation_fields = [
        'split_strategy', 'total_records', 'train_test_ratio', 'temporal_coverage'
    ]
    for field in required_validation_fields:
        assert field in validation, f"Missing validation field: {field}"


def test_scientific_interpretation_structure(modeling_analysis_data):
    """Test scientific interpretation section structure."""
    interpretation = modeling_analysis_data['scientific_interpretation']
    
    # Test ecological insights
    assert 'ecological_insights' in interpretation
    insights = interpretation['ecological_insights']
    assert isinstance(insights, list)
    assert len(insights) >= 1
    
    # Test monitoring implications
    assert 'monitoring_implications' in interpretation
    implications = interpretation['monitoring_implications']
    required_implication_fields = [
        'year_round_deployment_viable', 'seasonal_calibration_needed',
        'key_acoustic_indicators', 'expected_accuracy_range'
    ]
    for field in required_implication_fields:
        assert field in implications, f"Missing implication field: {field}"
    
    assert isinstance(implications['year_round_deployment_viable'], bool)
    assert isinstance(implications['seasonal_calibration_needed'], bool)
    assert isinstance(implications['key_acoustic_indicators'], list)
    
    # Test methodological contributions
    assert 'methodological_contributions' in interpretation
    contributions = interpretation['methodological_contributions']
    assert isinstance(contributions, list)
    assert len(contributions) >= 1


def test_methodology_structure(modeling_analysis_data):
    """Test methodology section structure."""
    methodology = modeling_analysis_data['methodology']
    
    required_method_fields = [
        'stratification_approach', 'model_types', 'feature_engineering',
        'target_variables', 'evaluation_metrics'
    ]
    for field in required_method_fields:
        assert field in methodology, f"Missing methodology field: {field}"
    
    # Test model types
    model_types = methodology['model_types']
    assert isinstance(model_types, list)
    assert 'Logistic Regression' in model_types
    assert 'Random Forest' in model_types
    
    # Test target variables
    target_vars = methodology['target_variables']
    assert isinstance(target_vars, list)
    assert 'fish_presence' in target_vars


def test_data_quality_metrics(modeling_analysis_data):
    """Test overall data quality and consistency."""
    # Test that total records are consistent across sections
    dataset_records = modeling_analysis_data['dataset_summary']['total_records']
    
    # Monthly patterns should sum to roughly the total records
    monthly_records = sum(
        item['total_records'] 
        for item in modeling_analysis_data['temporal_patterns']['monthly_patterns']
    )
    
    # Allow for some variance due to rounding or missing data
    assert abs(monthly_records - dataset_records) / dataset_records < 0.05, \
        f"Monthly records ({monthly_records}) don't match dataset total ({dataset_records})"
    
    # Test that fish activity rates are consistent
    dataset_activity = modeling_analysis_data['dataset_summary']['fish_activity_rate']
    seasonal_activity = modeling_analysis_data['temporal_patterns']['seasonal_insights']['total_year_activity_rate']
    
    # Should be very close
    assert abs(dataset_activity - seasonal_activity) < 0.01, \
        f"Activity rates inconsistent: dataset={dataset_activity}, seasonal={seasonal_activity}"


def test_file_size_reasonable():
    """Test that the view file is a reasonable size for web delivery."""
    view_file = Path(__file__).parent.parent.parent / "data" / "views" / "modeling_analysis.json"
    
    file_size_kb = view_file.stat().st_size / 1024
    
    # Should be larger than 10KB (has substantial content) but smaller than 100KB (web-friendly)
    assert 10 < file_size_kb < 100, f"File size {file_size_kb:.1f}KB may be problematic for web delivery"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])