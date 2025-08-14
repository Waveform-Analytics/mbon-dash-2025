import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Data Aggregation Examples

    Much of the python code in this project is focused on preparing data for use in a web environment, which means we're using a lot of dictionary objects (since they can be easily converted to json which is the best format for web things). This notebook is intended to provide the Python users with some examples of how to use Pandas to aggregate the data directly. 
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    # Import from mbon_analysis package
    from mbon_analysis.core import (
        load_processed_data,
        prepare_detection_data,
        get_detection_columns
    )
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Temporal aggregations""")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
