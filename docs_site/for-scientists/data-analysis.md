# Data Analysis Workflow

Step-by-step guide for analyzing acoustic indices and species detection data.

!!! tip "Flexible Approach"
    This workflow provides a foundation you can adapt based on your specific research questions.

## Overview

The analysis workflow follows these major phases:

1. **Data Integration** - Combine acoustic indices with species detection and environmental data
2. **Quality Assessment** - Validate data completeness and identify issues
3. **Dimensionality Reduction** - Use PCA to identify key index patterns  
4. **Correlation Analysis** - Relate indices to species detection patterns
5. **Result Interpretation** - Extract actionable insights

## Phase 1: Data Preparation

### Process Raw Data

```bash
# Transform Excel files → analysis-ready JSON
npm run process-data

# Verify data quality
npm run validate-data
```

This creates standardized datasets from:
- **Species detections** (manual annotations, 2-hour windows)
- **Environmental data** (temperature, depth measurements)
- **Deployment metadata** (station locations, timing)

*Note: Acoustic indices integration is planned for future development.*

## Phase 2: Quality Assessment

### Check Data Statistics

```bash
npm run data-stats
```

Review:
- Record counts by station and year
- Missing data patterns
- Species detection frequencies
- Environmental data ranges

### Identify Data Gaps

Look for:
- Periods with missing acoustic indices
- Stations with incomplete coverage
- Species with very low detection rates
- Environmental measurement gaps

## Phase 3: Exploratory Analysis

### Custom Analysis Scripts

```bash
# Use the exploratory folder for your analysis
cd scripts/exploratory/

# Run your analysis scripts
uv run your_analysis_script.py
```

Develop analysis approaches for:
- Species detection patterns
- Environmental correlations
- Temporal trends
- Spatial variations

### Interpret PCA Results

Key questions to address:
- How many components explain >70% of variance?
- Which indices contribute most to top components?
- Do components have clear biological interpretation?
- Are there natural index groupings?

## Phase 4: Statistical Analysis

### Species-Environment Relationships

Examine correlations between:
- Species detection rates and environmental factors
- Temporal patterns in species activity
- Spatial differences across stations

### Prepare for Acoustic Indices

Once acoustic indices are integrated:
- Correlation analysis between indices and species
- Dimensionality reduction (PCA)
- Predictive modeling

## Phase 5: Results & Visualization

### Dashboard Integration

```bash
# Update dashboard with your findings
npm run process-data  # Include new analysis results
npm run dev          # View in interactive dashboard
```

### Export Results

Save your analysis outputs to `data/intermediate_results/` for:
- Further statistical analysis
- Publication figures
- Sharing with collaborators

## Interactive Exploration

### Dashboard Analysis

Start the dashboard to explore results interactively:

```bash
npm run dev
```

Use the dashboard to:
- Visualize PCA results and component loadings
- Explore index-species correlation matrices
- Compare patterns across stations and time periods
- Export filtered datasets for further analysis

## Custom Analysis

### Working with Data in Python

Load processed data for custom analysis:

```python
import pandas as pd
import json

# Load dashboard data
with open('data/cdn/processed/detections.json', 'r') as f:
    detections = pd.DataFrame(json.load(f))

with open('data/cdn/processed/environmental.json', 'r') as f:
    environmental = pd.DataFrame(json.load(f))

# Your analysis here
```

### Extending the Workflow

- Add scripts to `scripts/exploratory/` for experiments
- Use `scripts/dashboard_prep/` for production data processing
- Save intermediate results to `data/intermediate_results/`

## Next Steps

1. **[Review research questions](research-questions.md)** - Understand the scientific objectives
2. **[Learn about acoustic indices](acoustic-indices.md)** - Prepare for future acoustic analysis
3. **[Edit dashboard content](content-editing.md)** - Update text with your findings

!!! success "Ready to Analyze"
    The data processing foundation is ready - start exploring patterns in the species detection and environmental data!