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
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Import from mbon_analysis package
    from mbon_analysis.core import (
        load_processed_data,
        prepare_detection_data,
        get_detection_columns
    )
    return (
        get_detection_columns,
        load_processed_data,
        mo,
        pd,
        prepare_detection_data,
        px,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Load detections data""")
    return


@app.cell
def _(get_detection_columns, load_processed_data, prepare_detection_data):
    df, environmental, detection_meta, stations = load_processed_data()
    df = prepare_detection_data(df)
    detection_cols, biological, anthropogenic = get_detection_columns(df, detection_meta)
    return detection_cols, df


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Temporal aggregations

    In this example, we are preparing a dataframe that would work for generating a Plotly figure.
    """
    )
    return


@app.cell
def _(detection_cols, df, pd):
    # Simple daily totals (all stations combined)
    daily_total = df.groupby(pd.Grouper(key='date', freq='D'))[detection_cols].sum()
    print(f"   Daily totals shape: {daily_total.shape}")
    print(f"   Date range: {daily_total.index[0]} to {daily_total.index[-1]}")

    # Daily by station (MultiIndex)
    daily_by_station = df.groupby([pd.Grouper(key='date', freq='D'), 'station'])[detection_cols].sum()
    print(f"   Daily by station shape: {daily_by_station.shape}")

    # For Plotly: Convert MultiIndex to columns
    daily_for_plotly = daily_by_station.reset_index()
    # add a month column
    daily_for_plotly['month'] = daily_for_plotly['date'].dt.month

    print(f"   Ready for Plotly shape: {daily_for_plotly.shape}")

    return (daily_for_plotly,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Here's an example showing how to generate a plotly visualization.""")
    return


@app.cell
def _(daily_for_plotly, detection_cols, px):
    fig = px.scatter(daily_for_plotly,
            x='date',
            y=daily_for_plotly[detection_cols].sum(axis=1),  # Total all detections
            color='station',
            title='Daily Total Detections by Station',
            labels={'y': 'Total Detections', 'date': 'Date'})
    fig.show()
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
