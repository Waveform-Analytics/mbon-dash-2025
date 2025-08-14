# For Scientists

## Analysis Workflow

### 1. Setup Environment
```bash
# Install Python environment
uv sync

# Process raw data
npm run process-data
```

### 2. Run Exploratory Analysis
```bash
# Interactive exploration
uv run scripts/exploratory/step01_explore_data_for_dashboard.py

# View generated plots
ls scripts/exploratory/figures/
```

### 3. Dashboard Exploration
```bash
npm run dev   # http://localhost:3000
```

## Research Methods

### Acoustic Indices Analysis
The project analyzes 56 acoustic indices across 6 categories:

- **Temporal**: ZCR, MEANt, VARt, SKEWt, KURTt, LEQt
- **Frequency**: MEANf, VARf, SKEWf, KURTf, NBPEAKS
- **Complexity**: ACI, NDSI, ADI, AEI
- **Diversity**: H_Havrda, H_Renyi, H_pairedShannon, RAOQ
- **Bioacoustic**: BioEnergy, AnthroEnergy, BI, rBA
- **Spectral**: LFC, MFC, HFC

### PCA Dimensionality Reduction
Goal: Reduce 56 indices to 3-5 "super indices" that capture most variation.

```python
from mbon_analysis.analysis import pca_analysis
# Load data and run PCA
results = pca_analysis.run_pca(data)
```

### Species Detection Correlation
Identify which indices best predict species presence/absence.

## Content Editing

Dashboard text can be edited without coding knowledge:

1. Find the page's `.content.tsx` file
2. Edit text between quotes
3. Save and refresh browser

Example location: `src/app/page.content.tsx`

## Key Research Questions

1. **Index Reduction**: Can 56 indices → 3-5 super indices?
2. **Biodiversity Prediction**: Which indices predict species best?
3. **Environmental Effects**: How do temperature/depth affect indices?
4. **Spatial Patterns**: How do stations differ acoustically?

## Data Access

### Processed Data
```python
import pandas as pd
import json

# Load detection data
with open('data/cdn/processed/detections.json') as f:
    detections = pd.DataFrame(json.load(f))

# Load environmental data
with open('data/cdn/processed/environmental.json') as f:
    environmental = pd.DataFrame(json.load(f))
```

### Station Information
- **9M**: Shallow station, highest activity
- **14M**: Mid-depth station
- **37M**: Deep station, different species composition

## Support
For questions about analysis methods or data interpretation, check the research questions in CLAUDE.md or contact the project team.