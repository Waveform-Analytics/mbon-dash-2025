import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Data Loading Example""")
    return


@app.cell
def _():
    import marimo as mo
    from mbon_analysis.core import (
        load_processed_data,
        load_acoustic_indices, 
        load_metadata
    )
    return load_acoustic_indices, load_metadata, load_processed_data, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Loading core data

    Here we show example code for loading data. We begin by loading the core datasets - which are datasets in json fomrat.
    """
    )
    return


@app.cell
def _(load_processed_data):
    detections, environmental, species_meta, stations = load_processed_data()
    return detections, environmental


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Loading with acoustic indices

    In this case the core_data are all in a list, and the acoustic indices are stored as well.
    """
    )
    return


@app.cell
def _(load_processed_data):
    *core_data, acoustic_indices = load_processed_data(include_acoustic_indices=True)
    detections_core = core_data[0]
    environmental_core = core_data[1]
    species_meta_core = core_data[2]
    stations_core = core_data[3]
    return (acoustic_indices,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Loading acoustic indices ONLY

    Sometimes you may want to only load acoustic indices. In that case you can use the following function.
    """
    )
    return


@app.cell
def _(load_acoustic_indices):
    indices_only = load_acoustic_indices()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Loading processing metadata

    The metadata loads as a python dictionary object with stats and tallies of the data loaded. 
    """
    )
    return


@app.cell
def _(load_metadata):
    metadata = load_metadata()
    summary = metadata['data_summary']

    summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Extracting information from the metadata:""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Data tables

    A listing of the core data tables that were loaded
    """
    )
    return


@app.cell
def _(detections):
    detections
    return


@app.cell
def _(environmental):
    environmental
    return


@app.cell
def _(acoustic_indices):
    acoustic_indices
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
