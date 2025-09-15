import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""# Notebook 5: Anthropogenic Impact Assessment""")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
