# Interactive Notebooks

Welcome to the MBON interactive notebook collection! These notebooks demonstrate key workflows and analysis patterns using the `mbon_analysis` package.

!!! info "About These Notebooks"
    These are [marimo](https://marimo.io) notebooks hosted on marimo's static platform. They provide interactive Python code with preserved outputs and can be viewed directly in your browser.

!!! tip "Working with Notebooks"
    - **View online**: Click any notebook below to explore interactively
    - **Run locally**: Install marimo (`pip install marimo`) and run the source files
    - **Create your own**: Upload to [static.marimo.app](https://static.marimo.app) and add to the registry

## Available Notebooks (2)

1. **[Data Loading Example](#data-loading-example)** - Basic data loading patterns with mbon_analysis
2. **[Basic Analysis Example](#basic-analysis-example)** - A few examples of doing basic aggregation and analysis on the detections data

---


### Data Loading Example

Basic data loading patterns with mbon_analysis

<div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 20px 0;">
  <div style="background: #f5f5f5; padding: 10px; font-weight: bold;">
    📓 Data Loading Example
  </div>
  <iframe src="https://static.marimo.app/static/data-loading-w4nz" 
          width="100%" height="700px" frameborder="0" 
          style="display: block;"
          loading="lazy">
    <p>Your browser does not support iframes. <a href="https://static.marimo.app/static/data-loading-w4nz" target="_blank">View notebook directly</a></p>
  </iframe>
  <div style="padding: 10px; text-align: center; background: #fafafa; font-size: 0.9em;">
    <a href="https://static.marimo.app/static/data-loading-w4nz" target="_blank">View full notebook →</a> | <a href="https://github.com/Waveform-Analytics/mbon-dash-2025/blob/main/scripts/notebooks/0.0_loading_data.py" target="_blank">Source code →</a>
  </div>
</div>

---

### Basic Analysis Example

A few examples of doing basic aggregation and analysis on the detections data

<div style="border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 20px 0;">
  <div style="background: #f5f5f5; padding: 10px; font-weight: bold;">
    📓 Basic Analysis Example
  </div>
  <iframe src="https://static.marimo.app/static/analysis-8wis" 
          width="100%" height="700px" frameborder="0" 
          style="display: block;"
          loading="lazy">
    <p>Your browser does not support iframes. <a href="https://static.marimo.app/static/analysis-8wis" target="_blank">View notebook directly</a></p>
  </iframe>
  <div style="padding: 10px; text-align: center; background: #fafafa; font-size: 0.9em;">
    <a href="https://static.marimo.app/static/analysis-8wis" target="_blank">View full notebook →</a> | <a href="https://github.com/Waveform-Analytics/mbon-dash-2025/blob/main/scripts/notebooks/1.0_analysis_workflow_example.py" target="_blank">Source code →</a>
  </div>
</div>

---

## Creating New Notebooks

To add a new notebook to this collection:

1. **Create locally**: `marimo new scripts/notebooks/your_notebook.py`
2. **Develop**: `marimo edit scripts/notebooks/your_notebook.py`
3. **Upload**: Go to [static.marimo.app](https://static.marimo.app) and upload your notebook
4. **Register**: Add the static URL to `docs_site/marimo_notebooks.txt`
5. **Build**: Run `uv run scripts/build_notebook_docs.py` to update this page

### Local Development

To work with these notebooks locally:

```bash
# Install marimo
pip install marimo

# Run a notebook interactively
marimo run scripts/notebooks/0.0_loading_data.py

# Edit a notebook
marimo edit scripts/notebooks/0.0_loading_data.py
```
