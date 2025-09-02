# MBON Marine Biodiversity Dashboard - Complete Rebuild Plan

## Project Vision

Interactive web dashboard exploring whether acoustic indices can predict marine soundscape biodiversity and serve as proxies for complex biodiversity monitoring. **Core Question**: "Can computed acoustic indices help us understand or even predict marine biodiversity patterns as an alternative to labor-intensive manual species detection methods?"

## Architecture Principles

### 1. **View-First Architecture**
- All data processing generates optimized view files (< 50KB each)
- Dashboard loads only the specific views needed per page
- Raw data stays in Python processing layer, never reaches frontend

### 2. **Clean Separation of Concerns**
- **Python Layer**: Heavy computation, data processing, view generation
- **Web Layer**: Visualization, interaction, presentation only
- **CDN Layer**: Static file serving, global distribution

### 3. **Performance by Design**
- Sub-second page loads for all visualizations
- Progressive data loading based on user interaction
- Intelligent caching and view optimization

## Technology Stack

### Backend (Python)
- **Package Manager**: `uv` for fast, reliable dependency management
- **Processing**: `pandas`, `numpy`, `scikit-learn` for data analysis
- **Visualization Data**: Pre-computed aggregations, PCA results, statistical summaries
- **Testing**: `pytest` with coverage reporting

### Frontend (TypeScript/React)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Nivo.rocks (primary), d3js (secondary)
- **State**: Zustand for client state management
- **Maps**: Mapbox GL JS for geographic visualizations

### Infrastructure
- **Data Storage**: Cloudflare R2 CDN for global distribution (already have it set up at waveformdata.work - bucket name mbon-usc-2025)
- **Deployment**: Vercel (frontend), Python processing runs locally
- **Environment**: Docker optional, uv-based Python environment
- **Environment Variables**: Stored in `.env.local` at the project root level (not in dashboard/), making them accessible to both Python scripts and Next.js application through dotenv configuration

## Project Structure

```
mbon-biodiversity-dashboard/
├── README.md                          # Quick start and overview
├── REBUILD_PLAN.md                    # This document
├── 
├── python/                            # Python processing layer
│   ├── pyproject.toml                 # Python dependencies
│   ├── mbon_analysis/                 # Core analysis package
│   │   ├── __init__.py
│   │   ├── data/                      # Data loading and validation
│   │   │   ├── __init__.py
│   │   │   ├── loaders.py             # Excel/CSV loading utilities
│   │   │   ├── validators.py          # Data quality checks
│   │   │   └── models.py              # Data structure definitions
│   │   ├── analysis/                  # Scientific analysis modules
│   │   │   ├── __init__.py
│   │   │   ├── acoustic.py            # Acoustic indices analysis
│   │   │   ├── biodiversity.py        # Species detection patterns
│   │   │   ├── environmental.py       # Temperature/depth effects
│   │   │   └── spatial.py             # Station comparisons
│   │   ├── views/                     # View generation (dashboard data)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base view generator class
│   │   │   ├── acoustic_summary.py    # Acoustic indices dashboard view
│   │   │   ├── species_timeline.py    # Species detection timeline
│   │   │   ├── station_profiles.py    # Station comparison view
│   │   │   ├── environmental_trends.py # Environmental patterns view
│   │   │   └── biodiversity_metrics.py # Biodiversity analysis view
│   │   └── utils/                     # Shared utilities
│   │       ├── __init__.py
│   │       ├── stats.py               # Statistical helpers
│   │       └── viz_prep.py            # Visualization data prep
│   ├── scripts/                       # Data processing pipeline
│   │   ├── 01_process_raw_data.py     # Excel → Core JSON
│   │   ├── 02_generate_views.py       # Core JSON → View files
│   │   ├── 03_upload_cdn.py           # Upload to Cloudflare R2
│   │   └── dev_tools/                 # Development utilities
│   │       ├── validate_data.py       # Data quality checks
│   │       ├── generate_test_data.py  # Sample data for development
│   │       └── benchmark_views.py     # Performance testing
│   ├── tests/                         # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest configuration
│   │   ├── test_data/                 # Sample data for testing
│   │   ├── test_loaders.py            # Data loading tests
│   │   ├── test_views.py              # View generation tests
│   │   └── test_analysis.py           # Analysis module tests
│   └── data/                          # Data storage
│       ├── raw/                       # Original Excel/CSV files
│       │   ├── 2018/                  # First study year
│       │   ├── 2021/                  # Second study year
│       │   └── indices/               # Acoustic indices CSVs
│       ├── processed/                 # Intermediate JSON files
│       └── views/                     # Optimized dashboard views
│
├── dashboard/                         # Next.js web application
│   ├── package.json                   # Node.js dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── src/
│   │   ├── app/                       # App Router pages
│   │   │   ├── layout.tsx             # Root layout with navigation
│   │   │   ├── page.tsx               # Landing page (project overview, map, dataset summary)
│   │   │   ├── page.content.tsx       # Landing page content
│   │   │   ├── explore/               # Data exploration page
│   │   │   │   ├── page.tsx
│   │   │   │   └── page.content.tsx
│   │   │   └── indices/               # Acoustic indices reference
│   │   │       ├── page.tsx
│   │   │       └── page.content.tsx
│   │   ├── components/
│   │   │   ├── maps/                  # Mapbox components
│   │   │   │   └── StationMap.tsx     # Interactive station map
│   │   │   ├── data/                  # Data summary components
│   │   │   │   ├── DatasetSummary.tsx # Dataset overview cards
│   │   │   │   └── IndicesTable.tsx   # Filterable indices reference
│   │   │   ├── ui/                    # Reusable UI components
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   ├── DataTable.tsx
│   │   │   │   └── ExportButton.tsx
│   │   │   └── layout/                # Layout components
│   │   │       ├── Navigation.tsx
│   │   │       ├── Footer.tsx
│   │   │       └── PageHeader.tsx
│   │   ├── lib/
│   │   │   ├── data/                  # Data loading hooks
│   │   │   │   ├── useStations.ts     # Station data and metadata
│   │   │   │   ├── useIndices.ts      # Acoustic indices reference data
│   │   │   │   └── useDatasets.ts     # Dataset summary information
│   │   │   ├── utils/                 # Utility functions
│   │   │   │   ├── formatting.ts      # Data formatting helpers
│   │   │   │   ├── colors.ts          # Color schemes for charts
│   │   │   │   └── export.ts          # Data export utilities
│   │   │   └── constants.ts           # App constants
│   │   ├── styles/
│   │   │   ├── globals.css            # Global styles and Tailwind
│   │   │   └── charts.css             # Chart-specific styles
│   │   └── types/
│   │       ├── data.ts                # Data type definitions
│   │       ├── views.ts               # View data interfaces
│   │       └── charts.ts              # Chart configuration types
│   ├── public/
│   │   ├── icons/                     # App icons and favicons
│   │   └── images/                    # Static images
│   └── docs/                          # Development documentation
│       ├── components.md              # Component documentation
│       ├── data-flow.md               # Data loading documentation
│       └── deployment.md              # Deployment guide
│
├── docs/                              # Project documentation
│   ├── ARCHITECTURE.md                # Architecture decisions
│   ├── DATA_PROCESSING.md             # Data pipeline documentation
│   ├── API_REFERENCE.md               # Python API documentation
│   └── RESEARCH_CONTEXT.md            # Scientific background
│
└── deployment/                        # Deployment configuration
    ├── docker-compose.yml             # Local development stack
    ├── Dockerfile.python              # Python processing container
    ├── vercel.json                    # Vercel deployment config
    └── cdn_config.md                  # Cloudflare R2 setup guide
```

## Data Pipeline Architecture

### Phase 1: Data Processing (Python)
```bash
# One-time setup
cd python/
uv sync                                # Install dependencies
uv pip install -e .                   # Install mbon_analysis package

# Data processing pipeline
uv run scripts/01_process_raw_data.py  # Excel → Core JSON
uv run scripts/02_generate_views.py    # Core JSON → Optimized views
uv run scripts/03_upload_cdn.py        # Upload views to CDN

# All-in-one command
make process-data                      # Runs all 3 steps
```

### Phase 2: Dashboard Development
```bash
# Dashboard development
cd dashboard/
npm install                           # Install dependencies
npm run dev                          # Start development server

# Production build
npm run build                        # Build for production
npm run start                        # Start production server
```

### Data Flow
```
Raw Excel/CSV → Core JSON → View Files → CDN → Dashboard
   (50+ files)    (6 files)   (8 files)   (Global) (Sub-second)
```

## Raw Data Structure

All raw data files are stored in `python/data/raw/` following the current project structure:

### Data File Organization
```
python/data/raw/
├── metadata/                          # Reference and classification files
│   ├── det_column_names.csv           # Species/sound type classifications
│   ├── Updated_Index_Categories_v2.csv # Acoustic indices categories
│   └── 1_Montie Lab_metadata_deployments_2017 to 2022.xlsx # Deployment metadata
├── 2018/                              # First study year
│   ├── detections/                    # Manual species annotations (primary data)
│   │   ├── Master_Manual_9M_2h_2018.xlsx    # Station 9M detections
│   │   ├── Master_Manual_14M_2h_2018.xlsx   # Station 14M detections  
│   │   └── Master_Manual_37M_2h_2018.xlsx   # Station 37M detections
│   ├── environmental/                 # Environmental measurements
│   │   ├── Master_9M_Temp_2018.xlsx         # Temperature data
│   │   ├── Master_14M_Temp_2018.xlsx
│   │   ├── Master_37M_Temp_2018.xlsx
│   │   ├── Master_9M_Depth_2018.xlsx        # Depth measurements
│   │   ├── Master_14M_Depth_2018.xlsx
│   │   └── Master_37M_Depth_2018.xlsx
│   └── legacy_acoustic/               # Legacy RMS sound pressure levels
│       ├── Master_rmsSPL_9M_1h_2018.xlsx    # Will be replaced by indices
│       ├── Master_rmsSPL_14M_1h_2018.xlsx
│       └── Master_rmsSPL_37M_1h_2018.xlsx
├── 2021/                              # Second study year (same structure as 2018)
│   ├── detections/
│   ├── environmental/
│   └── legacy_acoustic/
└── indices/                           # Modern acoustic indices (replacement for rmsSPL)
    ├── Acoustic_Indices_9M_2021_FullBW_v2_Final.csv    # Full bandwidth indices
    ├── Acoustic_Indices_9M_2021_8kHz_v2_Final.csv      # 8kHz bandwidth indices
    ├── Acoustic_Indices_14M_2021_FullBW_v2_Final.csv
    ├── Acoustic_Indices_14M_2021_8kHz_v2_Final.csv
    ├── Acoustic_Indices_37M_2021_FullBW_v2_Final.csv
    └── Acoustic_Indices_37M_2021_8kHz_v2_Final.csv
```

### File Type Descriptions

#### **1. Detection Files (Primary Data)**
`Master_Manual_[STATION]_2h_[YEAR].xlsx`
- **Purpose**: Manual species annotations from hydrophone recordings
- **Content**: Species detection events with timestamps (2-hour windows)
- **Key Data**: Date/time, species codes (sp, otbw, bde, etc.), detection presence/absence
- **Scientific Value**: Ground truth data for biodiversity analysis
- **Processing**: Converted to `detections.json` with species name mapping

#### **2. Environmental Files**
`Master_[STATION]_Temp_[YEAR].xlsx` & `Master_[STATION]_Depth_[YEAR].xlsx`
- **Purpose**: Environmental conditions at hydrophone locations
- **Content**: Hourly temperature and depth measurements
- **Key Data**: Timestamps, temperature (°C), depth (meters)
- **Scientific Value**: Environmental confounders and habitat characterization
- **Processing**: Combined into `environmental.json` for correlation analysis

#### **3. Acoustic Indices Files (Core Analysis Data)**
`Acoustic_Indices_[STATION]_2021_[BANDWIDTH]_v2_Final.csv`
- **Purpose**: 56+ computed acoustic indices from audio analysis
- **Bandwidth Types**:
    - `FullBW`: Full bandwidth acoustic analysis
    - `8kHz`: Limited to 8kHz frequency range
- **Key Indices Categories**:
    - **Temporal Domain**: ZCR, MEANt, VARt, SKEWt, KURTt, LEQt
    - **Frequency Domain**: MEANf, VARf, SKEWf, KURTf, NBPEAKS
    - **Acoustic Complexity**: ACI, NDSI, ADI, AEI
    - **Diversity Indices**: H_Havrda, H_Renyi, H_pairedShannon, RAOQ
    - **Bioacoustic**: BioEnergy, AnthroEnergy, BI, rBA
    - **Spectral Coverage**: LFC, MFC, HFC
- **Scientific Value**: Core data for PCA analysis and biodiversity prediction
- **Processing**: Converted to `acoustic_indices.json` (~147MB) → optimized views

#### **4. Reference Files**

##### `det_column_names.csv`
- **Purpose**: Species and sound classification mapping
- **Content**: Long names, short codes, biological/anthropogenic categories
- **Key Data**:
    - `sp` → "Silver perch" (biological)
    - `otbw` → "Oyster toadfish boat whistle" (biological)
    - `bde` → "Bottlenose dolphin echolocation" (biological)
    - `anth` → "Anthropogenic sounds" (anthropogenic)
- **Processing**: Used for species name resolution and scientific categorization

##### `Updated_Index_Categories_v2.csv`
- **Purpose**: Acoustic indices categorization and descriptions
- **Content**: Index definitions, scientific categories, computational methods
- **Scientific Value**: Educational content for indices reference page
- **Processing**: Converted to `indices_reference.json` for filterable table

##### `1_Montie Lab_metadata_deployments_2017 to 2022.xlsx`
- **Purpose**: Complete deployment history and equipment specifications
- **Content**: Station coordinates, deployment dates, equipment details, environmental conditions
- **Key Data**: GPS coordinates, deployment periods, platform types, salinity, temperature
- **Scientific Value**: Spatial context and deployment validation
- **Processing**: Converted to `deployment_metadata.json` and `stations.json`

### Data Quality and Coverage

#### **Station Coverage**
- **Station 9M**: Complete data for both years (2018, 2021)
- **Station 14M**: Complete data for both years (2018, 2021)
- **Station 37M**: Detection and environmental data only (no acoustic indices yet)

#### **Temporal Coverage**
- **Detection Data**: 2018, 2021 (2-hour resolution)
- **Environmental Data**: 2018, 2021 (hourly resolution)
- **Acoustic Indices**: 2021 only (hourly resolution, stations 9M, 14M, 37M)

#### **Data Processing Priority**
1. **Detection Files**: Primary scientific data - highest priority
2. **Acoustic Indices**: Core analysis data - second priority
3. **Environmental Files**: Supporting data - third priority
4. **Legacy RMS Files**: Will be deprecated in favor of indices

## View-Based Data Architecture

### Core Principle
Each dashboard page loads only the data it needs through optimized view files.

### Initial View Files (< 50KB each)
```json
views/
├── stations.json                      # Station metadata, coordinates, deployment info (8KB)
├── datasets_summary.json              # Dataset overview, record counts, date ranges (12KB)
├── indices_reference.json             # All acoustic indices with descriptions, categories (25KB)
└── project_metadata.json              # Project info, research context, methods (6KB)
```

### Future View Files (to be added incrementally)
```json
future_views/
├── acoustic_summary.json              # PCA, index rankings, correlations (planned)
├── species_timeline.json              # Detection patterns over time (planned)
├── environmental_trends.json          # Temperature/depth patterns (planned)
└── biodiversity_metrics.json          # Diversity indices, richness (planned)
```

### Data Loading Pattern
```typescript
// Landing page loads stations and dataset summary
function LandingPage() {
  const { stations, loading: stationsLoading } = useStations();
  const { datasets, loading: datasetsLoading } = useDatasets();
  
  if (stationsLoading || datasetsLoading) return <LoadingSpinner />;
  
  return (
    <div>
      <ProjectOverview />
      <StationMap stations={stations} />
      <DatasetSummary datasets={datasets} />
    </div>
  );
}

// Indices page loads reference data
function IndicesPage() {
  const { indices, loading, error } = useIndices();
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return <IndicesTable indices={indices} filterable />;
}
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
```bash
# Setup project structure
mkdir mbon-biodiversity-dashboard
cd mbon-biodiversity-dashboard

# Python environment
mkdir python && cd python
uv init
# Add dependencies to pyproject.toml
uv sync

# Dashboard setup  
mkdir dashboard && cd dashboard
npx create-next-app@latest . --typescript --tailwind --app
npm install @nivo/core @nivo/line @nivo/bar @nivo/scatterplot @nivo/heatmap d3 mapbox-gl zustand
```

**Deliverables**:
- ✅ Project structure created
- ✅ Python package scaffolding
- ✅ Next.js dashboard initialized
- ✅ Basic data loading utilities
- ✅ Test suite foundation

### Phase 2: Data Processing Pipeline (Week 2-3)
```python
# Core processing modules
mbon_analysis/data/loaders.py         # Excel/CSV loading
mbon_analysis/analysis/acoustic.py    # Acoustic indices analysis
mbon_analysis/views/base.py           # Base view generator

# Pipeline scripts
scripts/01_process_raw_data.py        # Excel → JSON conversion
scripts/02_generate_views.py          # JSON → optimized views
scripts/03_upload_cdn.py              # CDN deployment
```

**Deliverables**:
- ✅ Raw data processing (Excel → JSON)
- ✅ Acoustic indices analysis pipeline
- ✅ View generation system
- ✅ CDN upload automation
- ✅ Data validation and quality checks

### Phase 3: Simple Dashboard (Week 3-4)
```typescript
// Core pages and components
app/page.tsx                          # Landing page with overview, map, datasets
app/explore/page.tsx                  # Simple data exploration page
app/indices/page.tsx                  # Acoustic indices reference
components/maps/StationMap.tsx        # Interactive station map
components/data/DatasetSummary.tsx    # Dataset overview cards
components/data/IndicesTable.tsx      # Filterable indices table
```

**Deliverables**:
- ✅ Landing page with project overview and station map
- ✅ Dataset summary with basic statistics
- ✅ Acoustic indices reference page with filtering
- ✅ Simple exploration page (structure for future expansion)
- ✅ Responsive design system
- ✅ Error handling and loading states

### Phase 4: Incremental Enhancement (Week 4+)
```typescript
// Add visualizations one by one as needed
components/charts/[NewChart].tsx      # Add charts incrementally
views/[new_view].json                 # Add optimized views as needed
app/[new_page]/page.tsx              # Add analysis pages as they're developed
```

**Future Deliverables** (to be added incrementally):
- 📋 Species detection timeline visualizations
- 📋 Acoustic indices correlation analysis
- 📋 Environmental factors analysis
- 📋 Advanced filtering and data exploration
- 📋 Chart PNG export functionality (download button per chart)
- 📋 Data export functionality (CSV/JSON downloads)

### Phase 5: Polish & Deploy (Week 5-6)
```bash
# Production deployment
cd dashboard/
npm run build
vercel deploy --prod

# Documentation and testing
pytest python/tests/                   # Full test suite
npm run test                          # Frontend tests
make docs                             # Generate documentation
```

**Deliverables**:
- ✅ Production deployment
- ✅ Comprehensive documentation
- ✅ Performance optimization
- ✅ User acceptance testing
- ✅ Scientific validation

## Development Workflow

### Daily Development
```bash
# Start development
make dev                              # Starts both Python and Node.js services

# Process new data (only when data changes)
make process-data                     # Full pipeline
make views                           # Generate views only
make upload                          # Upload to CDN only

# Testing
make test                            # Full test suite
make test-python                     # Python tests only
make test-dashboard                  # Dashboard tests only
```

### Data Update Workflow
```bash
# When new Excel files are added to python/data/raw/
make validate-data                   # Check data quality
make process-data                    # Run full pipeline
git add python/data/views/           # Commit new views
git commit -m "Update views with new data"
```

### Deployment Workflow
```bash
# Deploy new views to CDN
cd python/
uv run scripts/03_upload_cdn.py

# Deploy dashboard updates
cd dashboard/
vercel deploy --prod
```


## Quality Assurance

### Testing Strategy
```python
# Python tests
pytest python/tests/test_loaders.py        # Data loading
pytest python/tests/test_views.py          # View generation
pytest python/tests/test_analysis.py       # Analysis modules

# JavaScript/TypeScript tests
npm run test                               # Component tests
npm run test:e2e                          # End-to-end tests
npm run test:performance                   # Performance benchmarks
```

### Code Quality
- **Python**: `ruff` for linting and formatting
- **TypeScript**: ESLint + Prettier, strict TypeScript config
- **Pre-commit hooks**: Automated quality checks
- **Documentation**: Comprehensive API docs and examples

### Data Quality
- **Validation Pipeline**: Automated data quality checks
- **Schema Enforcement**: Strict data type validation
- **Missing Data Handling**: Graceful degradation for incomplete data
- **Version Control**: Track data changes and processing versions

## Scientific Validation

### Research Objectives
1. **Index Reduction**: Reduce 56+ acoustic indices to 3-5 "super indices" via PCA
2. **Biodiversity Prediction**: Identify indices that best predict species detection
3. **Environmental Effects**: Quantify temperature/depth influence on acoustic patterns
4. **Spatial Analysis**: Compare acoustic environments between stations
5. **Temporal Stability**: Assess multi-year pattern consistency

### Analysis Validation
- **Statistical Methods**: Peer-reviewed analysis techniques
- **Reproducible Research**: All analysis code versioned and documented
- **Validation Data**: Hold-out datasets for method validation
- **Expert Review**: Scientific collaborator validation of results

### Dashboard Validation
- **User Testing**: Scientist feedback on interface usability
- **Accuracy Verification**: Cross-check visualizations against analysis code
- **Performance Benchmarks**: Ensure sub-second response times
- **Accessibility**: WCAG compliance for broad accessibility

## Deployment & Maintenance

### Production Infrastructure
- **Frontend**: Vercel with global CDN
- **Data Storage**: Cloudflare R2 with global distribution
- **Processing**: Local Python environment (no server required)
- **Monitoring**: Vercel analytics + custom performance tracking

### Maintenance Workflow
```bash
# Monthly data updates (when new data available)
make update-data                      # Process new raw data
make deploy-views                     # Update CDN with new views
make deploy-dashboard                 # Deploy any dashboard updates

# Quarterly reviews
make performance-audit               # Check loading times
make data-quality-report            # Validate data processing
make documentation-review           # Update docs as needed
```

### Backup & Recovery
- **Data**: Raw data backed up in version control
- **Views**: Versioned views stored in CDN with rollback capability
- **Code**: Full version control with tagged releases
- **Deployment**: Automated rollback for failed deployments

## Success Metrics

### Technical Metrics
- **Mobile Performance**: All features work on tablets

### Scientific Metrics
- **Research Questions Answered**: Clear visualizations for all 5 core questions
- **Data Accessibility**: Scientists can easily explore and export data
- **Reproducibility**: All analysis steps documented and repeatable
- **Collaboration**: Multiple researchers can contribute data and analysis

### User Experience Metrics
- **Scientists**: Can find insights within 5 minutes of first visit
- **Managers**: Can understand high-level findings from homepage
- **Technical Users**: Can export data views as json and images as png and reproduce analysis
- **Public**: Can understand research context and importance

## Environment Configuration

### Important: Root-Level Environment Variables
The `.env.local` file is located at the **project root** (not inside the dashboard/ directory). This strategic placement allows:
- **Python scripts** to access environment variables for CDN uploads and data processing
- **Next.js application** to access the same variables through the custom dotenv configuration in `next.config.ts`
- **Single source of truth** for all configuration across the entire project

### Required Environment Variables
```bash
# Cloudflare R2 Configuration (used by Python scripts)
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=mbon-usc-2025
CLOUDFLARE_R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
CLOUDFLARE_R2_PUBLIC_URL=https://waveformdata.work

# Dashboard Configuration (used by Next.js)
NEXT_PUBLIC_CDN_BASE_URL=https://waveformdata.work
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token
```

### How It Works
1. **Next.js Configuration**: The `dashboard/next.config.ts` file uses `dotenv.config({ path: '../.env.local' })` to load the root-level environment file
2. **Python Scripts**: Python scripts use `python-dotenv` to load the same `.env.local` file from the project root
3. **Vercel Deployment**: When deploying to Vercel, add these environment variables to the Vercel project settings

---

This rebuild plan provides a solid foundation for creating a high-performance, scientifically rigorous marine biodiversity dashboard that addresses the identified issues while maintaining the project's research focus and technical requirements.


---

Make sure to follow modern code development best practices and keep the code clean and maintainable. 
