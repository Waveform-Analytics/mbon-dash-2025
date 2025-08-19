import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Exploratory Analysis of Acoustic Indices Data

    In this notebook, we explore how acoustic indices data might inform
    research questions about biodiversity prediction and dimensionality reduction.

    Key Research Questions:

    1. Can we reduce ~60 acoustic indices to 3-5 "super indices", or even a single index to rule them all via PCA?

    2. Which indices best predict species detection patterns?

    3. How do different index categories (diversity, complexity, spectral) perform?

    4. What are the temporal patterns and correlations between indices?
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    from datetime import datetime
    import warnings
    warnings.filterwarnings('ignore')

    # Set up plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    return Path, mo


@app.cell
def _(Path):
    # Load the raw indices files
    data_dir = Path("data/cdn/raw-data/indices")

    # Check what files we have
    indices_files = list(data_dir.glob("*.csv"))
    print(f"Found {len(indices_files)} indices files:")
    for file in indices_files:
        print(f"  - {file.name}")

    return data_dir, indices_files


@app.cell
def _(data_dir, indices_files):
    # Load the main indices file (Full BW version)
    main_file = data_dir / "Acoustic_Indices_9M_2021_FullBW_v2_Final.csv"
    if not main_file.exists():
        main_file = indices_files[0]  # Fallback to first available file

    print(f"📂 Loading primary indices file: {main_file.name}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
