# MBON Marine Biodiversity Dashboard

Interactive web dashboard for exploring marine acoustic monitoring data from the OSA MBON project (2018-2021).

**Research Focus**: Can acoustic indices predict marine biodiversity patterns as an alternative to labor-intensive manual species detection?

## Quick Start

1. **Install dependencies**
   ```bash
   uv sync          # Python dependencies for data processing
   npm install      # Node.js dependencies for web dashboard
   ```

2. **Process data** (first time only)
   ```bash
   npm run build-data
   ```

3. **Configure Cloudflare R2** (see [docs/CLOUDFLARE_R2_SETUP.md](docs/CLOUDFLARE_R2_SETUP.md))
   ```bash
   cp .env.example .env.local
   # Edit with your R2 URL and Mapbox token
   ```

4. **Start development**
   ```bash
   npm run dev      # Opens dashboard at http://localhost:3000
   ```

## For Scientists: Python + Web Dashboard Hybrid Approach

This project uses a **hybrid architecture** designed for researchers:

### 🐍 **Python for Data Analysis**
All the heavy computational work happens in Python using scientific libraries:
- **Data processing**: pandas, numpy, openpyxl
- **Statistical analysis**: PCA, correlations, predictive models  
- **File formats**: CSV, Excel, JSON exports

### 🌐 **Web Dashboard for Visualization** (Interactive Results)
The processed results are displayed in an interactive web dashboard for:
- **Exploration**: Filter, zoom, compare across stations/time
- **Presentation**: Share findings with colleagues and stakeholders
- **Export**: Download charts, filtered datasets, analysis results

### 🔄 **Two Ways to Run the Same Commands**

You can work in the way that's most comfortable for you:

#### Option 1: Python-First Approach
```bash
# Use Python directly with uv (virtual environment manager)
uv run scripts/analysis/pca_analysis.py           # Run PCA analysis
uv run scripts/pipeline/steps/1_process_raw_data.py  # Process raw data
uv run scripts/legacy/validate_data.py            # Check data quality
```

#### Option 2: Unified Command Interface (Convenient)
```bash  
# Same scripts, run through npm for convenience
npm run build-analysis    # Runs PCA + correlation analysis
npm run pipeline:step1     # Process raw data  
npm run validate-data      # Check data quality
```

**Both approaches use exactly the same Python environment and dependencies!** The `npm run` commands just provide a single interface for the whole team.

### 📁 **Data Organization**
```
project/
├── data/                  # Raw data (Excel, CSV) - committed to git
├── processed/            # Cleaned data (JSON) - ignored by git  
├── analysis/             # Analysis results (PCA, correlations) - ignored by git
├── scripts/              # Python analysis scripts
└── dashboard/            # Web visualization (you can ignore this)
```

## Data Processing Commands (Choose Your Style)

### 🚀 **Full Pipeline** (Recommended for New Data)
```bash
npm run build-data              # Complete processing pipeline
# OR in pure Python:
uv run scripts/pipeline/run_full_pipeline.py
```

### 🔍 **Individual Steps** (For Development/Debugging)  
```bash
npm run pipeline:step1          # Process raw Excel/CSV files
npm run pipeline:step2          # Align temporal windows (hourly → 2-hour)
npm run pipeline:step3          # Join detection + environmental + acoustic data
npm run pipeline:step4          # Handle missing data
npm run pipeline:step5          # Run PCA analysis  
npm run pipeline:step6          # Prepare data for dashboard
```

### 📊 **Analysis Commands**
```bash
npm run build-analysis          # PCA + correlation analysis
npm run validate-data           # Check data quality
npm run data-stats              # Generate data summaries
```

### 🔧 **Legacy Commands** (Original Processing)
```bash
npm run build-data-legacy       # Original Excel → JSON processing
```

## Documentation

### For Scientists & Researchers  
- **[ACOUSTIC_INDICES_INTEGRATION_PLAN.md](docs/ACOUSTIC_INDICES_INTEGRATION_PLAN.md)** - Complete analysis strategy
- **[CLAUDE.md](CLAUDE.md)** - Detailed development documentation with research questions
- **[IMPLEMENTATION_CHECKLIST.md](docs/IMPLEMENTATION_CHECKLIST.md)** - Week-by-week implementation plan

### For Developers
- [Dashboard Plan](docs/dashboard_plan.md) - Original project specification
- [Cloudflare R2 Setup](docs/CLOUDFLARE_R2_SETUP.md) - CDN configuration guide

## Tech Stack

### Data Analysis (Python)
- **Processing**: pandas, numpy, openpyxl
- **Analysis**: scikit-learn (PCA), scipy (correlations)
- **Environment**: uv (Python package manager)

### Web Dashboard (JavaScript/TypeScript)
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Visualization**: Observable Plot, Mapbox GL JS, D3.js
- **State Management**: Zustand
- **Deployment**: Vercel + Cloudflare R2 CDN

## Current Dataset

- **26,280** detection records (Manual species annotations)
- **237,334** environmental records (Temperature, depth)  
- **3** monitoring stations (9M, 14M, 37M in May River, SC)
- **56** acoustic indices (NEW - from collaborator)
- **2** years of data (2018, 2021)
- **28** species tracked

## Research Goals

1. **Index Reduction**: Can we reduce 56 acoustic indices to 3-5 "super indices"?
2. **Biodiversity Prediction**: Which indices best predict species detection patterns?  
3. **Cost-Effectiveness**: Can acoustic indices replace expensive manual annotation?
4. **Environmental Context**: How do temperature/depth affect acoustic patterns?

## Getting Help

- **Python Issues**: Check `scripts/legacy/validate_data.py` output for data problems
- **Dashboard Issues**: Check browser console, ensure `.env.local` is configured  
- **Analysis Questions**: See research questions in [CLAUDE.md](CLAUDE.md)

---

*This project bridges marine biology and data science to make acoustic monitoring more accessible and cost-effective for biodiversity assessment.*