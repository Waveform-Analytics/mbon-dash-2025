# Python Exploratory Data Analysis Workflow

## Overview
The Python side of the project handles heavy computational analysis, data processing, and statistical modeling. This is separated from the web visualization layer to allow for complex scientific computing without impacting frontend performance.

## Directory Structure

```
scripts/
├── dashboard_prep/              # Core data processing pipeline
│   ├── process_excel_to_json.py  # Main data processing script
│   └── [other processing utilities]
├── exploratory/                 # Interactive analysis scripts
│   ├── figures/                 # Generated plots (gitignored)
│   ├── step01_explore_data_for_dashboard.py  # Current exploration script
│   ├── step02_[future].py       # Additional analysis steps
│   └── [other exploratory scripts]
└── analysis/                    # Advanced statistical analysis
    ├── pca_analysis.py          # Principal component analysis
    ├── correlation_analysis.py  # Index-species correlations
    └── [other analysis scripts]
```

## Exploratory Script Organization

### Naming Convention
- **Pattern**: `stepXX_descriptive_name.py`
- **Purpose**: Links scripts to generated figures and maintains analysis sequence
- **Example**: `step01_explore_data_for_dashboard.py` → generates `step01_*.png` figures

### Figure Management
- **Location**: `scripts/exploratory/figures/`
- **Naming**: `step01_description_of_plot.png`
- **Git Status**: Automatically ignored via `.gitignore` pattern `scripts/**/*.png`
- **Benefits**: 
  - Easy to identify which script generated which plots
  - No overwriting between different analysis runs
  - Clean separation of code and outputs

### Current Exploratory Features (`step01_explore_data_for_dashboard.py`)
1. **Data Type Classification**: Properly separates biological species from anthropogenic sounds
2. **Temporal Pattern Analysis**: Monthly detection patterns across stations
3. **Station Comparison**: Top annotations by station
4. **Co-occurrence Analysis**: Detection correlation matrix
5. **Scientific Terminology**: Uses "detections" and "annotations" instead of "species" when mixing bio/anthro data

## Data Processing Workflow

### Input Data Classification
Based on `det_column_names.csv` with type column:
- **`bio`**: Biological species (fish, marine mammals, etc.)
- **`anthro`**: Anthropogenic sounds (vessels, chains, static, etc.)  
- **`info`**: Metadata columns (date, station, analyzer, etc.)
- **`none`**: Empty/null data columns

### Analysis Pipeline
1. **Load & Clean**: Read processed JSON data, handle mixed data types
2. **Categorize**: Separate bio vs anthro detections using type metadata
3. **Explore**: Generate visualizations for temporal, spatial, and co-occurrence patterns
4. **Export**: Save dashboard-ready aggregated views

### Key Features
- **Proper Scientific Terminology**: Only calls biological detections "species"
- **Non-Interactive Plots**: Uses `matplotlib.use('Agg')` for server-friendly plotting
- **Absolute Paths**: Works correctly in both command line and IDE debuggers
- **Data Validation**: Ensures numeric columns only for analysis

## Running Exploratory Analysis

### Preferred Method (using uv)
```bash
# Run main exploratory script
uv run scripts/exploratory/step01_explore_data_for_dashboard.py

# Future analysis scripts
uv run scripts/exploratory/step02_pca_exploration.py
uv run scripts/exploratory/step03_environmental_correlations.py
```

### Interactive Debugging
- Set breakpoints in PyCharm or VS Code
- Script uses absolute paths, works regardless of working directory
- Debugger-friendly with clear variable names and data inspection points

## Integration with Web Dashboard

### Data Flow
1. **Python Processing**: Heavy analysis, statistical modeling, data aggregation
2. **JSON Export**: Lightweight, pre-computed results for web consumption  
3. **Web Visualization**: Interactive charts, filtering, user exploration

### Separation of Concerns
- **Python**: Statistical analysis, PCA, correlation matrices, data validation
- **Web**: Interactive visualization, user interface, real-time filtering
- **CDN**: Pre-processed data served efficiently to web clients

## Future Exploratory Steps

### Planned Analysis Scripts
- **Step 02**: PCA analysis and dimensionality reduction
- **Step 03**: Environmental correlation analysis
- **Step 04**: Acoustic indices evaluation
- **Step 05**: Predictive modeling for biodiversity assessment

### Best Practices
- Use step naming convention for traceability
- Generate figures with informative names
- Include data validation and quality checks
- Export key results as JSON for dashboard integration
- Use scientific terminology appropriately (species vs detections)