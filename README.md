# MBON Dash 2025: Marine Soundscape Analysis Platform

A comprehensive platform for analyzing marine soundscapes using acoustic indices as proxies for biological activity. This project validates whether acoustic indices can serve as effective screening tools for continuous marine ecosystem monitoring, building on methods from Transue et al. (2023).

## 🌊 Project Overview

**Core Research Question**: Can acoustic indices serve as effective biological screening tools and detect community-level fish patterns at scales impossible with manual detection?

**Approach**: Using 2021 May River data with manual detections as ground truth, we test whether acoustic indices alone can provide actionable biological information for future deployments where manual detection is impractical.

### Key Components

- **🐍 Python Analysis Pipeline**: Marimo notebooks for data processing, acoustic index analysis, and biological pattern detection
- **🖥️ Interactive Dashboard**: Next.js web application for visualizing results and patterns
- **📊 Data Management**: Automated processing, CDN integration, and standardized data formats
- **🔧 Development Tools**: Quality assurance, automated checking, and workflow optimization

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with npm/yarn
- **Git** for version control

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd mbon-dash-2025

# Load marimo helper functions (for development)
source marimo-helpers.sh
```

### 2. Python Environment Setup

```bash
# Navigate to python directory
cd python

# Install dependencies with uv
uv install

# Verify installation
uv run python --version
uv run marimo --version
```

### 3. Dashboard Setup

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`.

---

## 📁 Project Structure

```
mbon-dash-2025/
├── 📊 data/                          # Data storage (raw, processed, CDN)
├── 🐍 python/                        # Analysis pipeline
│   ├── scripts/notebooks/            # Main marimo analysis notebooks
│   ├── scripts/                      # Utility scripts and debugging tools
│   ├── pyproject.toml                # Python dependencies
│   └── README.md                     # Python-specific documentation
├── 🖥️ dashboard/                     # Next.js web application
│   ├── app/                          # Next.js app router pages
│   ├── components/                   # React components for visualizations
│   ├── lib/                          # Data loading and utility functions
│   ├── public/                       # Static assets and processed data
│   └── package.json                  # Node.js dependencies
├── 📋 notes/                         # Project planning and documentation
│   ├── PROJECT-PLAN.md               # Comprehensive research plan
│   ├── MVP-PLAN.md                   # Current implementation roadmap
│   ├── DATA-FILE-NAMING.md           # Data conventions and file descriptions
│   └── SITE-IMPLEMENTATION-NOTES.md  # Dashboard implementation details
├── 🔧 Development Tools
│   ├── marimo-helpers.sh             # Shell functions for marimo workflows
│   ├── editor-marimo-check.py        # Editor integration script
│   └── marimo-config.md              # Marimo check configuration guide
└── 📜 scripts/                       # Build and deployment scripts
```

---

## 🔬 Analysis Pipeline (Python/Marimo)

The analysis follows a structured 8-notebook progression from data loading to validation:

### Core Notebooks

1. **[01_data_prep.py](python/scripts/notebooks/01_data_prep.py)** - Data loading and quality assessment
2. **[02_temporal_aggregation.py](python/scripts/notebooks/02_temporal_aggregation.py)** - Temporal alignment and feature engineering
3. **[03_acoustic_index_reduction.py](python/scripts/notebooks/03_acoustic_index_reduction.py)** - Index characterization and dimensionality reduction
4. **[04_fish_and_indices_patterns.py](python/scripts/notebooks/04_fish_and_indices_patterns.py)** - Fish pattern analysis and index concordance
5. **[05_vessel_analysis.py](python/scripts/notebooks/05_vessel_analysis.py)** - Vessel detection and biological signal separation
6. **[06_community_pattern_detection.py](python/scripts/notebooks/06_community_pattern_detection.py)** - Community-level pattern analysis
7. **[07_continuous_monitoring_validation.py](python/scripts/notebooks/07_continuous_monitoring_validation.py)** - Continuous monitoring validation
8. **[10_view_generation.py](python/scripts/notebooks/10_view_generation.py)** - Dashboard data generation

### Working with Notebooks

```bash
# Load helper functions
source marimo-helpers.sh

# List all project notebooks
list_marimo

# Check and fix a specific notebook
check_marimo python/scripts/notebooks/01_data_prep.py

# Check all project notebooks
check_all_marimo

# Open a notebook for editing
ai_marimo python/scripts/notebooks/01_data_prep.py
```

### Marimo Standards

All notebooks follow standardized patterns:
- **Path Resolution**: Robust project root detection
- **Variable Naming**: Unique descriptive names across cells
- **Return Patterns**: Proper cell variable returns
- **Documentation**: Rich markdown explanations

See `notes/MVP-PLAN.md` for detailed notebook specifications.

---

## 🖥️ Dashboard Application

The dashboard provides interactive visualizations of the analysis results using Next.js and modern web technologies.

### Key Features

- **Station Maps**: Interactive maps showing monitoring locations
- **Heatmaps**: Acoustic indices, detections, and environmental patterns
- **Time Series**: Temporal patterns and correlations
- **Correlation Analysis**: Index-environment-biology relationships
- **Community Dashboards**: Aggregate biological activity patterns

### Development

```bash
cd dashboard

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Build notebook data for dashboard
npm run build:notebooks
```

### Key Components

- **`components/`**: Reusable visualization components
- **`lib/data.ts`**: Data loading and processing utilities
- **`lib/utils.ts`**: Helper functions and utilities
- **`app/`**: Next.js app router pages and layouts

---

## 📊 Data Management

### Data Flow

```
Raw Data → Python Processing → Processed Data → Dashboard Visualization
     ↓                ↓                ↓                    ↓
   data/raw/    marimo notebooks    data/processed/    dashboard/public/
```

### Data Naming Conventions

All data files follow standardized naming patterns described in `notes/DATA-FILE-NAMING.md`:

- **Pattern**: `{notebook_number}_{description}_{year}.parquet`
- **Example**: `01_raw_data_2021.parquet`

### CDN Integration

For large datasets, files are automatically uploaded to CDN:

```bash
# Upload processed data to CDN
cd python
uv run python scripts/upload_to_cdn.py

# Use CDN workflow script
bash scripts/cdn-workflow.sh
```

---

## 🔧 Development Workflows

### For AI-Assisted Development

1. **Load marimo helpers**: `source marimo-helpers.sh`
2. **Check notebooks after AI generation**: `check_marimo <notebook.py>`
3. **Watch for changes**: `watch_marimo python/scripts/notebooks/`
4. **Git hooks** automatically check notebooks before commits

### For Dashboard Development

1. **Update data**: Run relevant marimo notebooks → `npm run build:notebooks`
2. **Component development**: Use existing patterns in `components/`
3. **Data integration**: Update `lib/data.ts` for new data sources
4. **Testing**: `npm run dev` for hot reload

### Quality Assurance

The project includes comprehensive quality tools:

- **Marimo Check**: Automated notebook linting and fixing
- **Git Hooks**: Pre-commit notebook validation
- **Editor Integration**: VS Code task for notebook checking
- **Shell Helpers**: Convenient functions for common tasks

---

## 📚 Key Documentation

### Planning Documents
- **[PROJECT-PLAN.md](notes/PROJECT-PLAN.md)** - Comprehensive research methodology and statistical analysis plan
- **[MVP-PLAN.md](notes/MVP-PLAN.md)** - Current implementation roadmap with detailed notebook specifications
- **[RAW-DATA-DESCRIPTION.md](notes/RAW-DATA-DESCRIPTION.MD)** - Complete raw data catalog and formats

### Implementation Guides
- **[SITE-IMPLEMENTATION-NOTES.md](notes/SITE-IMPLEMENTATION-NOTES.md)** - Dashboard architecture and styling
- **[DATA-FILE-NAMING.md](notes/DATA-FILE-NAMING.md)** - File naming conventions and data catalog
- **[marimo-config.md](marimo-config.md)** - Marimo check configuration and usage
- **[CDN_INTEGRATION_GUIDE.md](notes/CDN_INTEGRATION_GUIDE.md)** - CDN setup and workflow

---

## 🎯 Common Tasks

### Starting a New Analysis

```bash
# 1. Load helper functions
source marimo-helpers.sh

# 2. Create/edit a notebook
ai_marimo python/scripts/notebooks/new_analysis.py

# 3. Check and fix the notebook
check_marimo python/scripts/notebooks/new_analysis.py

# 4. Generate dashboard data (if needed)
cd python && uv run python scripts/notebooks/10_view_generation.py
```

### Updating the Dashboard

```bash
# 1. Run relevant python notebooks to update processed data
cd python && uv run marimo run scripts/notebooks/10_view_generation.py

# 2. Build notebook metadata
cd dashboard && npm run build:notebooks

# 3. Start/restart development server
npm run dev
```

### Processing New Data

```bash
# 1. Place raw data in data/raw/
# 2. Update notebook 01 for new data sources
ai_marimo python/scripts/notebooks/01_data_prep.py

# 3. Run the full pipeline
check_all_marimo

# 4. Update dashboard
cd dashboard && npm run build:notebooks
```

### Quality Control

```bash
# Check all notebooks for issues
check_all_marimo

# Check recently modified notebooks
check_recent_marimo 120  # last 2 hours

# Watch for changes and auto-check
watch_marimo python/scripts/notebooks/
```

---

## 🛠️ Troubleshooting

### Common Issues

**Marimo command not found**
```bash
# Use uv run prefix
uv run marimo --version

# Or activate environment
cd python && uv shell
```

**Notebook path issues**
- All notebooks use standardized path resolution
- Always run from project root or use helper functions

**Data loading errors**
- Check file paths in `notes/DATA-FILE-NAMING.md`
- Verify data directory structure
- Use `list_marimo` to see available notebooks

**Dashboard not updating**
- Run `npm run build:notebooks` after data changes
- Check `dashboard/public/analysis/notebooks/` for generated files
- Verify data loading in `lib/data.ts`

### Getting Help

1. Check relevant documentation in `notes/`
2. Use `marimo check --verbose` for detailed error messages
3. Review `marimo-config.md` for configuration guidance
4. Check git commit history for recent changes

---

## 🌟 Contributing

This project uses:
- **Python**: uv for dependency management, marimo for notebooks
- **JavaScript**: npm for dependencies, Next.js for dashboard
- **Code Quality**: Automated marimo check, git hooks, standardized patterns
- **Documentation**: Extensive planning docs, inline comments, README files

When contributing:
1. Follow existing patterns in notebooks and components
2. Use helper functions for common tasks
3. Update documentation for new features
4. Run quality checks before committing

---

## 📄 License

MIT License

Copyright (c) 2025 Michelle Weirathmueller / Waveform Analytics, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 📞 Contact

michelle@waveformanalytics

---

*This project represents a comprehensive approach to marine soundscape analysis, combining rigorous statistical methods with modern data visualization techniques to advance our understanding of acoustic ecology in marine environments.*
