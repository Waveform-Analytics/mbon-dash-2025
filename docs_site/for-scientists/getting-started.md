# Getting Started

Quick setup guide for analyzing marine acoustic data and exploring biodiversity patterns.

## Prerequisites

- Python 3.9+
- Node.js 18+ (optional - for interactive dashboard)
- Git

!!! tip "Simple Setup"
    This project uses `uv` for Python dependencies - it handles everything automatically. No need for conda or complex environment setup.

## Installation

### 1. Clone and Setup

```bash
git clone [repository-url]
cd mbon-dash-2025

# Install uv (Python dependency manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python dependencies
uv sync
```

### 2. Dashboard (Optional)

```bash
# Only if you want the interactive web dashboard
npm install
```

The Python environment includes everything needed for analysis: pandas, numpy, scikit-learn, and data processing tools.

## Get Data

All raw data is stored on CDN (cloud storage) to keep the repository lightweight.

```bash
# Download raw data (Excel files, acoustic indices)
npm run download-data
```

## Process Data

Transform raw Excel files into analysis-ready format:

```bash
# Process Excel files → dashboard JSON format
npm run process-data

# Check data quality
npm run validate-data

# View data summary
npm run data-stats
```

**Expected results:**
- 26,280 species detection records
- 3 monitoring stations (9M, 14M, 37M)
- 2018 and 2021 data
- 28 species tracked

## Data Organization

```
data/                          # 🚫 Git-ignored (CDN-based)
├── cdn/                      # Mirror of cloud storage
│   ├── raw-data/            # Excel files, acoustic indices
│   └── processed/           # Dashboard-ready JSON files
└── intermediate_results/     # Your analysis workspace

scripts/                      # ✅ Version controlled
├── dashboard_prep/          # Generate dashboard data
├── exploratory/             # Your analysis sandbox  
├── utils/                   # Data validation tools
└── data_management/         # CDN sync tools
```

## Start Analyzing

1. **[Research Questions](research-questions.md)** - What we're investigating
2. **[Data Analysis Workflow](data-analysis.md)** - Step-by-step analysis guide
3. **[Content Editing](content-editing.md)** - Update dashboard text

**Ready to explore?** Run `npm run dev` to start the interactive dashboard!

## Troubleshooting

**Missing data files?**
```bash
npm run download-data
npm run validate-data
```

**Python environment issues?**
```bash
uv sync --reinstall
```

**Want Python-only workflow?**
All scripts can be run directly with `uv run scripts/[folder]/[script].py` - the dashboard is optional for visualization.

**Need help?** Check the other guides in this section or review the command reference.