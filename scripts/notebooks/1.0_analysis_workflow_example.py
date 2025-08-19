import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Analysis workflow example""")
    return


@app.cell
def _():
    import marimo as mo
    import json
    from pathlib import Path
    import pandas as pd

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
    return (
        analyze_bio_anthro_patterns,
        calculate_co_occurrence,
        compare_stations,
        create_dashboard_aggregations,
        find_temporal_peaks,
        get_detection_columns,
        get_diversity_metrics,
        get_monthly_patterns,
        load_processed_data,
        mo,
        prepare_detection_data,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Data Loading and Prep""")
    return


@app.cell
def _(get_detection_columns, load_processed_data, prepare_detection_data):
    # Load raw data
    detections, environmental, detection_meta, stations = load_processed_data()

    # Prepare detection data (adds temporal columns, cleans mixed types)
    detections = prepare_detection_data(detections)

    # Get detection columns and classify by type
    detection_cols, biological, anthropogenic = get_detection_columns(detections, detection_meta)
    return anthropogenic, biological, detection_cols, detections


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Temporal Analysis""")
    return


@app.cell
def _(detection_cols, detections, find_temporal_peaks, get_monthly_patterns):
    # Get monthly patterns - this returns a dataframe with detection counts for each month/year of deployement at each station
    monthly_patterns = get_monthly_patterns(detections, detection_cols)

    # Find temporal peaks (dict format)
    monthly_peaks = find_temporal_peaks(detections, detection_cols, time_grouping='month', top_n=5)
    seasonal_peaks = find_temporal_peaks(detections, detection_cols, time_grouping='season')

    print(f"  ✓ Monthly patterns: {monthly_patterns.shape}")
    print(f"  ✓ Peak month: {monthly_peaks['peaks'][0]['period']} ({monthly_peaks['peaks'][0]['total_detections']:,} detections)")
    print(f"  ✓ Peak season: {seasonal_peaks['peaks'][0]['period']} ({seasonal_peaks['peaks'][0]['total_detections']:,} detections)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Spatial Analysis""")
    return


@app.cell
def _(compare_stations, detection_cols, detections, get_diversity_metrics):
    # Compare stations - provides a dict with a variety of stations per month
    station_comparison = compare_stations(detections, detection_cols)

    # Get diversity metrics by station, returns a dataframe
    station_diversity = get_diversity_metrics(detections, detection_cols, by_column='station')
    print(f"  ✓ Compared {len(station_comparison)} stations")
    print(f"  ✓ Station diversity metrics calculated")

    # Find most active station
    most_active_station = max(station_comparison.items(), key=lambda x: x[1]['total_detections'])
    print(f"  ✓ Most active station: {most_active_station[0]} ({most_active_station[1]['total_detections']:,} detections)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Biodiversity Analysis""")
    return


@app.cell
def _(
    analyze_bio_anthro_patterns,
    anthropogenic,
    biological,
    calculate_co_occurrence,
    detection_cols,
    detections,
):
    # Calculate co-occurrence matrix
    co_occurrence = calculate_co_occurrence(detections, detection_cols)

    # Analyze biological vs anthropogenic patterns
    bio_anthro_patterns = analyze_bio_anthro_patterns(detections, biological, anthropogenic, detection_cols)

    print(f"  ✓ Co-occurrence matrix: {co_occurrence.shape}")
    print(f"  ✓ Biological detections: {bio_anthro_patterns['biological']['total_detections']:,}")
    print(f"  ✓ Anthropogenic detections: {bio_anthro_patterns['anthropogenic']['total_detections']:,}")
    print(f"  ✓ Bio/Anthro ratio: {bio_anthro_patterns['ratio']['bio_percentage']:.1f}% biological")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Dashboard data prep

    This function uses the detections dataframe computed earlier to generate various data aggregations to make it easier to generate visualizations for the dashboard.
    """
    )
    return


@app.cell
def _(create_dashboard_aggregations, detection_cols, detections):
    # Create pre-aggregated views for the dashboard
    dashboard_views = create_dashboard_aggregations(detections, detection_cols)

    print(f"  ✓ Created {len(dashboard_views)} dashboard views")
    print(f"    - Daily aggregations: {len(dashboard_views['daily_by_station'])} records")
    print(f"    - Monthly aggregations: {len(dashboard_views['monthly_by_station'])} records") 
    print(f"    - Detection rankings: {len(dashboard_views['detection_rankings'])} items")
    print(f"    - Station summaries: {len(dashboard_views['station_summaries'])} stations")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
