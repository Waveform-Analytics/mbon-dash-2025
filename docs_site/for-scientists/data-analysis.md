# Data Analysis Workflow

Step-by-step guide for analyzing acoustic indices and species detection data.

!!! info "Work in Progress"
    This workflow is being refined as we develop the acoustic indices analysis methods. The documentation will be updated as approaches are tested and validated.

## Overview

The analysis workflow follows these major phases:

1. **Data Integration** - Combine acoustic indices with species detection and environmental data
2. **Quality Assessment** - Validate data completeness and identify issues
3. **Dimensionality Reduction** - Use PCA to identify key index patterns  
4. **Correlation Analysis** - Relate indices to species detection patterns
5. **Result Interpretation** - Extract actionable insights

## Phase 1: Data Integration

### Run the Processing Pipeline

=== "Python Approach"
    ```bash
    uv run scripts/pipeline/run_full_pipeline.py
    ```

=== "Unified Commands"
    ```bash
    npm run build-data
    ```

This combines:
- **Acoustic indices** (hourly measurements → 2-hour windows)
- **Species detections** (manual annotations, 2-hour windows)
- **Environmental data** (temperature, depth)

### Verify Integration Success

```bash
npm run validate-data
```

Expected output shows successful data joining across all three data types.

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

## Phase 3: Dimensionality Reduction

### Run PCA Analysis

=== "Python Approach"
    ```bash
    uv run scripts/analysis/pca_analysis.py
    ```

=== "Unified Commands"  
    ```bash
    npm run build-analysis
    ```

This generates:
- Principal component loadings
- Explained variance by component
- Index contribution rankings
- Component interpretation

### Interpret PCA Results

Key questions to address:
- How many components explain >70% of variance?
- Which indices contribute most to top components?
- Do components have clear biological interpretation?
- Are there natural index groupings?

## Phase 4: Correlation Analysis

### Index-Species Correlations

The correlation analysis examines relationships between:
- Individual acoustic indices and species detection rates
- PCA component scores and biodiversity metrics
- Environmental factors and both indices and species

### Environmental Context

Assess how temperature and depth cycles affect:
- Acoustic index patterns
- Species detection patterns
- Index-species relationships

## Phase 5: Result Interpretation

### Key Outputs

1. **Reduced Index Set** - Top performing indices for biodiversity assessment
2. **Prediction Models** - How well indices predict species presence
3. **Environmental Corrections** - Accounting for temperature/depth effects
4. **Cost-Benefit Analysis** - Effort savings vs information loss

### Validation

Cross-validate results using:
- Different time periods
- Different stations
- Different species groups
- Statistical resampling methods

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

### Working with Results in Python

All analysis results are saved as JSON files that can be loaded into pandas:

```python
import pandas as pd
import json

# Load PCA results
with open('analysis/pca/pca_loadings.json', 'r') as f:
    loadings = json.load(f)

# Convert to DataFrame for analysis
loadings_df = pd.DataFrame(loadings)

# Your custom analysis here
```

### Extending the Analysis

The modular structure allows you to:
- Add custom analysis scripts to `scripts/analysis/`
- Modify processing steps in `scripts/pipeline/steps/`
- Create custom visualizations
- Export results in different formats

## Next Steps

Once you've completed the basic workflow:

1. **[Review research questions](research-questions.md)** to ensure analysis addresses key objectives
2. **[Understand acoustic indices](acoustic-indices.md)** to interpret biological meaning
3. **[Explore PCA workflow details](../analysis/pca-workflow.md)** for advanced PCA options

!!! note "Iterative Process"
    This workflow is designed to be iterative. As you discover patterns and refine questions, you can re-run analysis steps with different parameters or additional data.