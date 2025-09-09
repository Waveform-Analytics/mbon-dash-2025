# Documentation Implementation Notes

## Overview
This document outlines how to implement automated MkDocs documentation for the MBON project using marimo notebooks with auto-exported HTML files.

## Current Setup Status
- ✅ Marimo notebooks configured with `auto_download=["html"]`
- ✅ Auto-exported HTML files generate in `__marimo__/` subdirectories
- ✅ Example: `scripts/notebooks/__marimo__/02_temporal_aggregation.html`

## Architecture Decision
**Chosen Approach**: MkDocs + Static HTML from Marimo Auto-Export
- **Why**: Simplest implementation, leverages existing marimo auto-export
- **Benefits**: No manual conversion, preserves formatting, minimal maintenance
- **Trade-offs**: Less MkDocs integration than pure markdown

## Directory Structure
```
mbon-dash-2025/
├── mkdocs.yml                           # MkDocs configuration
├── docs/                               # Documentation source
│   ├── index.md                        # Main landing page
│   ├── notebooks/                      # Processed notebook pages
│   │   ├── index.md                   # Notebook gallery
│   │   ├── 01-data-prep.html          # From marimo auto-export
│   │   └── 02-temporal-aggregation.html
│   ├── assets/                        # Static assets
│   │   ├── custom.css                 # Custom styling
│   │   └── plots/                     # Generated plot images (if needed)
│   ├── project-plan.md               # Copy from notes/PROJECT-PLAN.md
│   └── data-sources.md               # Copy from notes/RAW-DATA-DESCRIPTION.md
├── python/
│   └── scripts/
│       ├── notebooks/                 # Source notebooks
│       │   ├── __marimo__/           # Auto-exported HTML files
│       │   ├── 01_data_prep.py
│       │   └── 02_temporal_aggregation.py
│       └── build_docs.py             # Build automation script
└── .github/
    └── workflows/
        └── docs.yml                   # GitHub Actions for deployment
```

## Implementation Files

### 1. MkDocs Configuration (`mkdocs.yml`)
```yaml
site_name: MBON Data Analysis
site_description: Marine Biodiversity Observatory Network - Data Analysis
site_url: https://USERNAME.github.io/mbon-dash-2025  # Update USERNAME

theme:
  name: material
  features:
    - navigation.sections
    - search.highlight
    - content.code.copy
  palette:
    - scheme: default
      primary: blue
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: blue
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

nav:
  - Home: index.md
  - Analysis Notebooks:
    - Overview: notebooks/index.md
    - Data Preparation: notebooks/01-data-prep.html
    - Temporal Aggregation: notebooks/02-temporal-aggregation.html
  - Documentation:
    - Project Plan: project-plan.md
    - Data Sources: data-sources.md

plugins:
  - search

extra_css:
  - assets/custom.css
```

### 2. Build Script (`python/scripts/build_docs.py`)
Key functions needed:

#### a) Process Marimo Auto-Exports
```python
def process_marimo_exports():
    """
    Find and process marimo auto-exported HTML files
    - Scan notebooks/__marimo__/ directories
    - Copy HTML files to docs/notebooks/
    - Rename with consistent naming (e.g., 01_data_prep.html → 01-data-prep.html)
    - Extract metadata from original .py files for indexing
    """
```

#### b) Extract Notebook Metadata
```python
def extract_notebook_metadata(notebook_py_path):
    """
    Parse marimo .py file to extract:
    - Title from first mo.md() call with # header
    - Purpose from **Purpose**: pattern
    - Key Outputs from **Key Outputs**: pattern
    
    Example from 01_data_prep.py:
    Title: "Notebook 1: Data Loading and Initial Exploration"
    Purpose: "Load all data streams and perform initial quality assessment"
    Key Outputs: "Raw data summaries, temporal coverage plots, missing data visualization"
    """
```

#### c) Generate Notebook Index
```python
def generate_notebook_index(notebook_metadata):
    """
    Create docs/notebooks/index.md with:
    - Card-style layout for each notebook
    - Title, purpose, key outputs
    - Links to HTML files
    - Instructions for running locally
    """
```

#### d) Copy Documentation Files
```python
def copy_documentation():
    """
    Copy and process:
    - notes/PROJECT-PLAN.md → docs/project-plan.md
    - notes/RAW-DATA-DESCRIPTION.md → docs/data-sources.md
    - Create docs/index.md if doesn't exist
    """
```

### 3. Custom CSS (`docs/assets/custom.css`)
```css
/* Notebook grid layout for index page */
.notebook-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin: 32px 0;
}

/* Notebook cards styling */
.notebook-card {
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 8px;
  padding: 24px;
  background: var(--md-code-bg-color);
  transition: all 0.2s ease-in-out;
}

/* Marimo HTML iframe integration */
.marimo-notebook {
  width: 100%;
  min-height: 800px;
  border: 1px solid var(--md-default-fg-color--lightest);
  border-radius: 4px;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .notebook-grid {
    grid-template-columns: 1fr;
  }
}
```

### 4. GitHub Actions Workflow (`.github/workflows/docs.yml`)
```yaml
name: Deploy Documentation
on:
  push:
    branches: [main]
    paths: 
      - 'python/scripts/notebooks/**'
      - 'docs/**'
      - 'notes/**'
      - 'mkdocs.yml'

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: |
        pip install mkdocs-material beautifulsoup4
        
    - name: Build documentation
      run: |
        cd python/scripts
        python build_docs.py
        cd ../..
        mkdocs build
        
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: './site'
        
    - name: Deploy to GitHub Pages
      uses: actions/deploy-pages@v4
```

## Content Templates

### Main Index Page (`docs/index.md`)
```markdown
# MBON Data Analysis Dashboard

Marine Biodiversity Observatory Network - Data analysis and visualization.

## Quick Navigation

- **[Analysis Notebooks](notebooks/)** - Interactive data processing and visualization
- **[Project Plan](project-plan.md)** - Detailed methodology and approach
- **[Data Sources](data-sources.md)** - Raw data descriptions and formats

## Project Overview

This project analyzes marine biodiversity data from acoustic monitoring stations, focusing on:

- **Acoustic indices analysis** - Temporal patterns and ecological indicators
- **Fish detection patterns** - Manual detection data processing and analysis  
- **Environmental correlations** - Temperature, depth, and SPL relationships
- **Temporal aggregation** - Multi-resolution time series analysis

## Data Processing Pipeline

1. **Data Preparation** - Load and quality-assess all data streams
2. **Temporal Aggregation** - Align data to common time resolution
3. **Analysis & Visualization** - Generate insights and interactive plots

## Technology Stack

- **[Marimo](https://marimo.io/)** - Reactive Python notebooks
- **[Pandas](https://pandas.pydata.org/)** - Data analysis and manipulation  
- **[Matplotlib/Seaborn](https://matplotlib.org/)** - Statistical visualization
- **[MkDocs Material](https://squidfunk.github.io/mkdocs-material/)** - Documentation
```

### Notebook Index Template (`docs/notebooks/index.md`)
```markdown
# Analysis Notebooks

Interactive data analysis notebooks with static outputs. Each notebook processes different aspects of the MBON dataset.

## Available Notebooks

<div class="notebook-grid">

<div class="notebook-card">
  <h3><a href="01-data-prep.html">Data Loading and Initial Exploration</a></h3>
  <p><strong>Purpose:</strong> Load all data streams and perform initial quality assessment</p>
  <p><strong>Key Outputs:</strong> Raw data summaries, temporal coverage plots, missing data visualization</p>
  <p><a href="01-data-prep.html" class="button">View Notebook →</a></p>
</div>

<div class="notebook-card">
  <h3><a href="02-temporal-aggregation.html">Temporal Aggregation</a></h3>
  <p><strong>Purpose:</strong> Align all data streams to common temporal resolution</p>
  <p><strong>Key Outputs:</strong> Synchronized datasets, coverage analysis</p>
  <p><a href="02-temporal-aggregation.html" class="button">View Notebook →</a></p>
</div>

</div>

## Running Notebooks Locally

To run these notebooks interactively with live data:

```bash
cd python/scripts
marimo edit notebooks/01_data_prep.py
```

## Data Requirements

All notebooks expect data to be available in `python/data/raw/` following the structure described in [Data Sources](../data-sources.md).
```

## Implementation Workflow

### Phase 1: Basic Setup
1. Create `mkdocs.yml` in repo root
2. Create `docs/` directory structure
3. Write basic `docs/index.md` 
4. Set up GitHub Pages in repository settings
5. Test with simple GitHub Action

### Phase 2: Automation
1. Create `build_docs.py` script
2. Implement marimo HTML processing
3. Add metadata extraction from notebooks
4. Generate dynamic notebook index
5. Copy documentation files

### Phase 3: Styling & Polish
1. Create custom CSS for notebook cards
2. Improve mobile responsiveness
3. Add search functionality
4. Optimize for performance

### Phase 4: Advanced Features (Optional)
1. Add notebook thumbnails/previews
2. Implement notebook dependencies/workflow
3. Add data download links
4. Create API documentation

## Key Considerations

### Metadata Extraction Strategy
- Parse marimo `.py` files using AST
- Look for first `mo.md()` call with markdown content
- Extract title from `# Header` pattern
- Extract purpose from `**Purpose**: text` pattern
- Extract outputs from `**Key Outputs**: text` pattern

### File Naming Conventions
- Source notebooks: `01_data_prep.py` (underscores)
- Documentation: `01-data-prep.html` (hyphens, web-friendly)
- Consistent numbering for ordered workflows

### Performance Considerations
- Marimo HTML files can be large (include full framework)
- Consider iframe embedding vs direct inclusion
- Optimize for mobile viewing
- Implement lazy loading if needed

### Maintenance
- Build script should be idempotent
- Handle missing files gracefully
- Provide clear error messages
- Log processing steps for debugging

## GitHub Repository Settings

### Enable GitHub Pages
1. Go to Settings > Pages
2. Source: GitHub Actions
3. No custom domain needed
4. Site will be available at: `https://USERNAME.github.io/mbon-dash-2025/`

### Required Permissions
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

## Deployment URL
Once set up, documentation will be available at:
`https://USERNAME.github.io/mbon-dash-2025/`

Replace `USERNAME` with your GitHub username.