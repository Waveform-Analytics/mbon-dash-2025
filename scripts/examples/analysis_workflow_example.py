#!/usr/bin/env python3
"""
Example showing how to use the mbon_analysis package for comprehensive analysis.

This demonstrates how the exploratory analysis can be simplified by using
the reusable functions from the mbon_analysis package.
"""

import json
from pathlib import Path

# Import analysis functions from mbon_analysis package
from mbon_analysis.core import (
    load_processed_data,
    prepare_detection_data, 
    get_detection_columns,
    create_dashboard_aggregations
)
from mbon_analysis.analysis import (
    get_monthly_patterns,
    find_temporal_peaks,
    compare_stations,
    calculate_co_occurrence,
    analyze_bio_anthro_patterns,
    get_diversity_metrics
)


def comprehensive_analysis_workflow():
    """
    Comprehensive analysis workflow using mbon_analysis package functions.
    """
    
    print("MBON Comprehensive Analysis Workflow")
    print("=" * 60)
    
    # ========================================================================
    # 1. DATA LOADING AND PREPARATION
    # ========================================================================
    print("\n📊 Loading and preparing data...")
    
    # Load raw data
    detections, environmental, detection_meta, stations = load_processed_data()
    
    # Prepare detection data (adds temporal columns, cleans mixed types)
    detections = prepare_detection_data(detections)
    
    # Get detection columns and classify by type
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    
    print(f"  ✓ Loaded {len(detections):,} detection records")
    print(f"  ✓ Found {len(detection_cols)} detection types:")
    print(f"    - {len(biological)} biological species")
    print(f"    - {len(anthropogenic)} anthropogenic sounds")
    
    # ========================================================================
    # 2. TEMPORAL ANALYSIS
    # ========================================================================
    print("\n⏰ Analyzing temporal patterns...")
    
    # Get monthly patterns
    monthly_patterns = get_monthly_patterns(detections, detection_cols)
    
    # Find temporal peaks
    monthly_peaks = find_temporal_peaks(detections, detection_cols, time_grouping='month', top_n=5)
    seasonal_peaks = find_temporal_peaks(detections, detection_cols, time_grouping='season')
    
    print(f"  ✓ Monthly patterns: {monthly_patterns.shape}")
    print(f"  ✓ Peak month: {monthly_peaks['peaks'][0]['period']} ({monthly_peaks['peaks'][0]['total_detections']:,} detections)")
    print(f"  ✓ Peak season: {seasonal_peaks['peaks'][0]['period']} ({seasonal_peaks['peaks'][0]['total_detections']:,} detections)")
    
    # ========================================================================
    # 3. SPATIAL ANALYSIS
    # ========================================================================
    print("\n🗺️  Analyzing spatial patterns...")
    
    # Compare stations
    station_comparison = compare_stations(detections, detection_cols)
    
    # Get diversity metrics by station
    station_diversity = get_diversity_metrics(detections, detection_cols, by_column='station')
    
    print(f"  ✓ Compared {len(station_comparison)} stations")
    print(f"  ✓ Station diversity metrics calculated")
    
    # Find most active station
    most_active_station = max(station_comparison.items(), key=lambda x: x[1]['total_detections'])
    print(f"  ✓ Most active station: {most_active_station[0]} ({most_active_station[1]['total_detections']:,} detections)")
    
    # ========================================================================
    # 4. BIODIVERSITY ANALYSIS
    # ========================================================================
    print("\n🐟 Analyzing biodiversity patterns...")
    
    # Calculate co-occurrence matrix
    co_occurrence = calculate_co_occurrence(detections, detection_cols)
    
    # Analyze biological vs anthropogenic patterns
    bio_anthro_patterns = analyze_bio_anthro_patterns(detections, biological, anthropogenic, detection_cols)
    
    print(f"  ✓ Co-occurrence matrix: {co_occurrence.shape}")
    print(f"  ✓ Biological detections: {bio_anthro_patterns['biological']['total_detections']:,}")
    print(f"  ✓ Anthropogenic detections: {bio_anthro_patterns['anthropogenic']['total_detections']:,}")
    print(f"  ✓ Bio/Anthro ratio: {bio_anthro_patterns['ratio']['bio_percentage']:.1f}% biological")
    
    # ========================================================================
    # 5. CREATE DASHBOARD VIEWS
    # ========================================================================
    print("\n📈 Creating dashboard aggregations...")
    
    # Create pre-aggregated views for dashboard
    dashboard_views = create_dashboard_aggregations(detections, detection_cols)
    
    print(f"  ✓ Created {len(dashboard_views)} dashboard views")
    print(f"    - Daily aggregations: {len(dashboard_views['daily_by_station'])} records")
    print(f"    - Monthly aggregations: {len(dashboard_views['monthly_by_station'])} records") 
    print(f"    - Detection rankings: {len(dashboard_views['detection_rankings'])} items")
    print(f"    - Station summaries: {len(dashboard_views['station_summaries'])} stations")
    
    # ========================================================================
    # 6. SAVE RESULTS
    # ========================================================================
    print("\n💾 Saving analysis results...")
    
    # Combine all results
    analysis_results = {
        'temporal_analysis': {
            'monthly_peaks': monthly_peaks,
            'seasonal_peaks': seasonal_peaks
        },
        'spatial_analysis': {
            'station_comparison': station_comparison,
            'station_diversity': station_diversity.to_dict('records')
        },
        'biodiversity_analysis': {
            'bio_anthro_patterns': bio_anthro_patterns,
            'co_occurrence_shape': co_occurrence.shape
        },
        'dashboard_views': dashboard_views,
        'summary': {
            'total_detections': int(detections[detection_cols].sum().sum()),
            'date_range': {
                'start': detections['date'].min().isoformat(),
                'end': detections['date'].max().isoformat()
            },
            'stations': sorted(detections['station'].unique()),
            'years': sorted(detections['year'].unique())
        }
    }
    
    # Save to output directory
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    output_dir = project_root / "data" / "intermediate_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "comprehensive_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"  ✓ Results saved to: {output_file}")
    
    # ========================================================================
    # 7. SUMMARY
    # ========================================================================
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"📊 Total detections analyzed: {analysis_results['summary']['total_detections']:,}")
    print(f"📅 Date range: {analysis_results['summary']['date_range']['start']} to {analysis_results['summary']['date_range']['end']}")
    print(f"🗺️  Stations: {', '.join(analysis_results['summary']['stations'])}")
    print(f"📈 Years: {', '.join(map(str, analysis_results['summary']['years']))}")
    print(f"🐟 Species types: {len(biological)} biological, {len(anthropogenic)} anthropogenic")
    
    return analysis_results


if __name__ == "__main__":
    results = comprehensive_analysis_workflow()
    print("\n✅ Comprehensive analysis workflow completed!")
    print(f"Results available in 'results' variable and saved to file.")