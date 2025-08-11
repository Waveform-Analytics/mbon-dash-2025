# Command Reference

Complete reference for all available commands in the MBON project.

!!! tip "Two Command Interfaces"
    All commands can be run either directly with Python (`uv run`) or through npm (`npm run`). Both use the same Python environment and produce identical results.

## Quick Reference

| Task | npm Command | Python Command |
|------|-------------|----------------|
| **Download raw data** | `npm run download-data` | `uv run scripts/download_raw_data.py` |
| **Full pipeline** | `npm run build-data` | `uv run scripts/pipeline/run_full_pipeline.py` |
| **PCA analysis** | `npm run build-analysis` | `uv run scripts/analysis/pca_analysis.py` |
| **Data validation** | `npm run validate-data` | `uv run scripts/legacy/validate_data.py` |
| **Data statistics** | `npm run data-stats` | `uv run scripts/legacy/data_stats.py` |
| **Start dashboard** | `npm run dev` | N/A |

## Data Processing Commands

### Download Raw Data

=== "npm"
    ```bash
    npm run download-data
    ```

=== "Python"
    ```bash
    uv run scripts/download_raw_data.py
    ```

Downloads raw data files from CDN to local `data/` directory. Required before running any processing commands.

**Why CDN storage**: Raw data files total 114MB+, too large for GitHub repository.

**Files downloaded**:
- Detection data (Excel files): ~6 files for 3 stations × 2 years
- Environmental data (temperature/depth): ~12 files  
- Acoustic indices: ~7 files (CSV and Excel)
- Deployment metadata: 1 Excel file

**Prerequisites**: Internet connection, CDN configured with raw data files.

### Full Pipeline

=== "npm"
    ```bash
    npm run build-data
    ```

=== "Python"
    ```bash
    uv run scripts/pipeline/run_full_pipeline.py
    ```

Runs the complete data processing pipeline:
1. Process raw Excel/CSV files  
2. Align temporal windows (hourly → 2-hour)
3. Join detection + environmental + acoustic data
4. Handle missing data with interpolation
5. Run PCA analysis
6. Prepare data for dashboard

**Output**: Creates files in `processed/`, `analysis/`, and `cdn/` directories.

### Individual Pipeline Steps

Process data step-by-step for development and debugging:

=== "npm"
    ```bash
    npm run pipeline:step1    # Process raw data
    npm run pipeline:step2    # Temporal alignment  
    npm run pipeline:step3    # Join datasets
    npm run pipeline:step4    # Handle missing data
    npm run pipeline:step5    # Run PCA analysis
    npm run pipeline:step6    # Prepare dashboard data
    ```

=== "Python"
    ```bash
    uv run scripts/pipeline/steps/1_process_raw_data.py
    uv run scripts/pipeline/steps/2_align_temporal_windows.py
    uv run scripts/pipeline/steps/3_join_datasets.py
    uv run scripts/pipeline/steps/4_handle_missing_data.py
    uv run scripts/pipeline/steps/5_run_pca_analysis.py
    uv run scripts/pipeline/steps/6_prepare_dashboard_data.py
    ```

**Use cases**:
- Debugging processing issues
- Running partial updates
- Testing new processing logic

## Analysis Commands

### PCA and Correlation Analysis

=== "npm"
    ```bash
    npm run build-analysis
    ```

=== "Python"
    ```bash
    uv run scripts/analysis/pca_analysis.py
    uv run scripts/analysis/correlation_analysis.py
    ```

Runs statistical analysis:
- Principal component analysis on acoustic indices
- Index-species correlation matrices
- Component interpretation and index ranking

**Output**: Results saved to `analysis/pca/` and `analysis/correlations/`

### Individual Analysis Scripts

=== "Python"
    ```bash
    uv run scripts/analysis/pca_analysis.py           # PCA only
    uv run scripts/analysis/correlation_analysis.py   # Correlations only
    uv run scripts/analysis/biodiversity_models.py    # Predictive models
    ```

## Data Quality Commands

### Validation

=== "npm"
    ```bash
    npm run validate-data
    ```

=== "Python"
    ```bash
    uv run scripts/legacy/validate_data.py
    ```

Checks data integrity:
- File existence and readability
- Expected data structures
- Missing data patterns
- Cross-file consistency

**Example output**:
```
✓ Detections: 26,280 records from 3 stations
✓ Environmental: 237,334 records
✓ Stations: 3 stations configured
✓ Species: 28 species identified
```

### Statistics

=== "npm"
    ```bash
    npm run data-stats
    ```

=== "Python"
    ```bash
    uv run scripts/legacy/data_stats.py
    ```

Generates comprehensive data summaries:
- Record counts by station and year
- Species detection frequencies
- File sizes and completeness
- Top species by detection count

## Dashboard Commands

### Development Server

```bash
npm run dev
```

Starts the interactive dashboard at `http://localhost:3000`.

**Prerequisites**:
- Processed data available in `cdn/` directory
- Environment configured in `.env.local`

### Production Build

```bash
npm run build
npm run start
```

Builds optimized dashboard for production deployment.

## Legacy Commands

Original processing scripts maintained for backward compatibility:

=== "npm"
    ```bash
    npm run build-data-legacy    # Original Excel → JSON processing
    ```

=== "Python"
    ```bash
    uv run scripts/legacy/process_data.py
    uv run scripts/legacy/check_data_freshness.py
    ```

**Use cases**:
- Comparing with new pipeline results
- Processing data without acoustic indices
- Troubleshooting pipeline issues

## Environment Commands

### Python Environment

```bash
# Install/update Python dependencies
uv sync

# Add new Python package
uv add package-name

# Check Python environment
uv run python --version
```

### Node.js Environment

```bash
# Install/update Node.js dependencies  
npm install

# Add new Node.js package
npm install package-name

# Check versions
npm run type-check    # TypeScript checking
npm run lint          # Code linting
```

## Development Commands

### Code Quality

```bash
npm run lint          # ESLint checking
npm run type-check    # TypeScript validation
```

### Documentation

```bash
# Build documentation site (this site!)
uv run mkdocs serve

# Deploy documentation
uv run mkdocs build
```

## Troubleshooting Commands

### Check Installation

```bash
# Verify Python environment
uv run python -c "import pandas, numpy, sklearn; print('Python OK')"

# Verify Node.js environment
npm run --version

# Check data availability  
ls -la data/indices/raw/
```

### Debug Data Issues

```bash
# Detailed validation with debug info
uv run scripts/legacy/validate_data.py --verbose

# Check specific file
uv run python -c "import pandas as pd; print(pd.read_csv('data/indices/raw/Acoustic_Indices_9M_FullBW_v1.csv').info())"
```

### Reset Environment

```bash
# Clean generated files
rm -rf processed/ analysis/ cdn/

# Reinstall dependencies
uv sync --reinstall
npm install --force

# Rebuild from scratch
npm run build-data
```

## Command Options

Some commands accept optional parameters:

### Pipeline Options
```bash
# Run specific pipeline steps
uv run scripts/pipeline/run_partial_pipeline.py --steps 1,2,3

# Skip certain validations
uv run scripts/pipeline/run_full_pipeline.py --skip-validation
```

### Analysis Options
```bash
# PCA with specific number of components
uv run scripts/analysis/pca_analysis.py --n-components 5

# Correlation analysis with specific method
uv run scripts/analysis/correlation_analysis.py --method spearman
```

!!! note "Parameter Documentation"
    Detailed parameter documentation for each script can be viewed with:
    ```bash
    uv run scripts/script_name.py --help
    ```