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
    return (mo,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
