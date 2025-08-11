# Getting Started

This guide will get you up and running with the MBON dashboard for acoustic indices analysis.

## Prerequisites

- Python 3.9+ 
- Node.js 18+ (for the web dashboard)
- Git

!!! tip "Environment Management"
    This project uses `uv` for Python dependency management - it's like `conda` but faster and more reliable for this type of project. Don't worry if you haven't used it before, it works similarly to other Python package managers.

## Installation

### 1. Clone the Repository

```bash
git clone [repository-url]
cd mbon-dash-2025
```

### 2. Install Python Dependencies

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync
```

This installs:
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `openpyxl` - Excel file reading
- `scikit-learn` - PCA and statistical analysis
- `mkdocs-material` - Documentation (this site!)

### 3. Install Dashboard Dependencies

```bash
npm install
```

This is only needed if you want to use the interactive dashboard. You can do all the analysis work with just Python.

## Download Raw Data

Raw data files are stored on CDN due to size constraints (114MB+ total). Download them first:

=== "Python Approach"
    ```bash
    # Download raw data from CDN
    uv run scripts/download_raw_data.py
    ```

=== "Unified Commands"
    ```bash
    # Download raw data from CDN
    npm run download-data
    ```

## First Analysis Run

Let's verify everything works by running a basic data validation:

=== "Python Approach"

    ```bash
    # Check data quality
    uv run scripts/legacy/validate_data.py
    
    # Generate data statistics
    uv run scripts/legacy/data_stats.py
    ```

=== "Unified Commands"

    ```bash
    # Check data quality
    npm run validate-data
    
    # Generate data statistics
    npm run data-stats
    ```

You should see output showing:
- ~26,000 detection records
- 3 monitoring stations (9M, 14M, 37M)
- Data from 2018 and 2021
- List of detected species

!!! success "Expected Output"
    ```
    ✓ Detections: 26,280 records from 3 stations
    ✓ Environmental: 237,334 records  
    ✓ Stations: 3 stations configured
    ✓ Species: 28 species identified
    ```

## Understanding the Data Structure

Your data is organized as:

```
data/                           # Raw data (committed to git)
├── indices/raw/               # Acoustic indices from collaborator
│   └── Acoustic_Indices_9m_FullBW_v1.csv
├── 2018/, 2021/              # Detection and environmental data
processed/                     # Generated during analysis (ignored by git)
├── indices/                  # Processed acoustic data
├── combined/                 # Joined datasets
analysis/                     # Analysis results (ignored by git) 
├── pca/                     # PCA results
├── correlations/            # Correlation matrices
```

## Next Steps

Now that everything is set up:

1. **[Explore the data workflow](data-analysis.md)** - Learn the analysis pipeline
2. **[Understand research questions](research-questions.md)** - See what we're investigating  
3. **[Run PCA analysis](../analysis/pca-workflow.md)** - Start with dimensionality reduction

## Common Issues

### Python Environment Problems

If you get import errors:

```bash
# Check if uv environment is active
uv run python --version

# Reinstall dependencies
uv sync --reinstall
```

### Missing Data Files

If you get "file not found" errors:

```bash
# Download raw data from CDN first
npm run download-data

# Then run validation
npm run validate-data
```

The raw data files (114MB+) are stored on CDN due to GitHub size limits. 

### Permission Errors

If you get permission errors when running scripts:

```bash
# Make scripts executable
chmod +x scripts/**/*.py
```

## Working Without the Dashboard

You can do all the analysis work using just Python - the dashboard is only for interactive visualization of results. If you prefer to work entirely in Python:

1. Run analysis scripts directly with `uv run`
2. Export results to CSV/JSON for use in your preferred analysis environment
3. Use the validation scripts to check data quality

The hybrid approach means you can work however feels most comfortable while still benefiting from the organized pipeline structure.