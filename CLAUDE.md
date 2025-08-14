# Marine Biodiversity Dashboard (MBON-USC-2025)

## Project Overview
Interactive web dashboard exploring whether acoustic indices can predict marine soundscape biodiversity and serve as proxies for complex biodiversity monitoring. The core research question: "Can computed acoustic indices help us understand and predict marine biodiversity patterns as an alternative to labor-intensive manual species detection methods?"

**Research Focus**: Analyzing relationships between 56+ acoustic indices and species presence across 3 stations in May River, South Carolina, with emphasis on identifying the most informative indices for biodiversity assessment and understanding environmental confounding factors.

**Key Goals**:
- Identify which acoustic indices best predict species detection patterns
- Use PCA to reduce 56 indices to a smaller set of "super indices" 
- Develop automated alternatives to manual species annotation
- Understand spatial (between stations) and temporal patterns in acoustic environments

## Data Structure

### **Detection Data**
- Manual species annotations from hydrophone recordings
- **Years**: 2018, 2021 (3 stations, 2 years scope)
- **Stations**: 9M, 14M, 37M 
- **Files**: Master_Manual_[STATION]_2h_[YEAR].xlsx (sheet 1)
- **Categories**: Biological species, anthropogenic sounds, environmental sounds

### **Environmental Data**
- Temperature and depth measurements from hydrophone locations
- **Files**: Master_[STATION]_Temp_[YEAR].xlsx, Master_[STATION]_Depth_[YEAR].xlsx (sheet 1)
- **Resolution**: Hourly measurements

### **Acoustic Indices** (Core Analysis Focus)
- **Source**: Collaborator-provided CSV files with 56+ acoustic indices
- **Temporal Resolution**: Hourly (aggregated to 2-hour windows to match detections)
- **Current Files**: `Acoustic_Indices_9M_2021_FullBW_v2_Final.csv`, `Acoustic_Indices_9M_2021_8kHz_v2_Final.csv`
- **Index Categories**:
  - Temporal domain: ZCR, MEANt, VARt, SKEWt, KURTt, LEQt
  - Frequency domain: MEANf, VARf, SKEWf, KURTf, NBPEAKS
  - Acoustic complexity: ACI, NDSI, ADI, AEI
  - Diversity indices: H_Havrda, H_Renyi, H_pairedShannon, RAOQ
  - Bioacoustic: BioEnergy, AnthroEnergy, BI, rBA
  - Spectral coverage: LFC, MFC, HFC

### **Legacy & Metadata**
- **Legacy Acoustic**: RMS Sound Pressure Level measurements (being replaced by indices)
- **Deployment Metadata**: Station locations, equipment specs, deployment periods

## Technology Stack
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS
- **Visualization**: Observable Plot (primary), Mapbox GL JS, D3.js utilities
- **State Management**: Zustand
- **Data Processing**: Python with uv (preferred package manager)
- **Python Package**: Integrated acoustic analysis utilities (`mbon_analysis/` subpackage)
- **Data Storage**: Cloudflare R2 CDN
- **Deployment**: Vercel (frontend only)

**Architecture**: Split into three tightly integrated components:
- **Python Package (`mbon_analysis/`)**: Reusable core utilities for acoustic analysis (subpackage of main project)
- **Python Scripts (`scripts/`)**: Application-specific processing and exploratory analysis
- **Web Visualization (`src/`)**: Interactive dashboard, user interface, real-time filtering

## Principles and Best Practices
- Always use best practices and aim for tidiness and good documentation

## Development Guidelines
- Don't write commit messages for me, or commit or push.
- **Content Helper Pattern**: All pages must use the content helper pattern for text management:
  - Create a `page.content.tsx` file alongside each `page.tsx`
  - Export a const object with all text content
  - Include clear comments for non-programmer editors
  - Keep text simple (no HTML formatting)
  - Maintain all styling in the main page component

## Quick Start

### 1. Project Setup
```bash
# Create Next.js project
npx create-next-app@latest mbon-dashboard --typescript --tailwind --app
cd mbon-dashboard

# Initialize Python environment with uv
uv init

# Install Python dependencies for data processing
uv add pandas openpyxl numpy

# Install Node.js dependencies for web app
npm install @observablehq/plot d3 mapbox-gl zustand date-fns
npm install file-saver papaparse jszip
npm install -D @types/d3 @types/file-saver @types/papaparse
```

### 2. Data Processing
```bash
# Process raw Excel files to JSON (run after any data updates)
uv run scripts/process_data.py
# OR via npm script:
npm run build-data

# Development options:
npm run dev          # Start dev server (uses existing data)
npm run dev:fresh    # Process data first, then start dev server

# Check if data processing is needed
uv run scripts/check_data_freshness.py

# Production build (Next.js only, no data processing)
npm run build
```

### 3. Environment Variables
Create `.env.local`:
```
NEXT_PUBLIC_DATA_URL=https://pub-71436b8d94864ba1ace2ef29fa28f0f1.r2.dev
NEXT_PUBLIC_MAPBOX_TOKEN=mapbox_token_here
```

## Data Processing Workflow

### Current Data Structure

```
mbon-dash-2025/
├── data/                           # Raw data (committed to git)
│   ├── cdn/
│   │   └── raw-data/              # Column mappings and metadata
│   │       └── det_column_names.csv  # Species/sound classifications
│   ├── 2018/                      # Detection and environmental data
│   │   ├── Master_Manual_[STATION]_2h_2018.xlsx
│   │   ├── Master_[STATION]_Temp_2018.xlsx
│   │   └── Master_[STATION]_Depth_2018.xlsx
│   ├── 2021/                      # [similar structure]
│   ├── indices/                   # Acoustic indices from collaborator
│   │   ├── Acoustic_Indices_9M_2021_FullBW_v2_Final.csv
│   │   └── Acoustic_Indices_9M_2021_8kHz_v2_Final.csv
│   └── 1_Montie Lab_metadata_deployments_2017 to 2022.xlsx
│
├── data/cdn/processed/            # Dashboard-ready JSON (gitignored)
│   ├── detections.json           # All detection data
│   ├── environmental.json        # Temperature/depth data
│   ├── acoustic_indices.json     # Acoustic indices data
│   ├── species.json              # Species metadata with bio/anthro types
│   ├── stations.json             # Station information
│   └── metadata.json             # Data summary and column mappings
│
├── mbon_analysis/                # Integrated Python analysis subpackage
│   ├── __init__.py
│   ├── core/                     # Core data processing utilities
│   │   ├── __init__.py
│   │   ├── data_loader.py        # Basic data loading functions
│   │   ├── data_sync.py          # CDN synchronization
│   │   ├── auto_loader.py        # Auto-sync data loading
│   │   └── data_prep.py          # Data preparation and cleaning
│   ├── analysis/                 # Analysis modules
│   │   ├── __init__.py
│   │   ├── temporal.py           # Temporal pattern analysis
│   │   ├── spatial.py            # Spatial/station comparison analysis
│   │   └── biodiversity.py       # Detection patterns and diversity
│   ├── visualization/            # Plotting and visualization utilities
│   │   └── __init__.py
│   └── utils/                    # General utility functions
│       └── __init__.py
│
├── scripts/
│   ├── dashboard_prep/           # Core data processing
│   │   └── process_excel_to_json.py
│   ├── examples/                 # Usage examples for mbon_analysis package
│   │   ├── data_loading_example.py
│   │   ├── data_sync_example.py
│   │   └── analysis_workflow_example.py
│   └── exploratory/             # Interactive analysis
│       ├── figures/             # Generated plots (gitignored)
│       └── step01_explore_data_for_dashboard.py
│
├── notes/                        # Documentation
│   └── python-exploratory-workflow.md
│
└── src/                         # Next.js web application
    └── [web dashboard code]
```

### Current Processing Workflow

**Core Processing**: `scripts/dashboard_prep/process_excel_to_json.py`
- Reads Excel files from `data/2018/` and `data/2021/` directories
- Processes detection, environmental (temp/depth), acoustic indices, and metadata
- Handles mixed data types and timestamp precision
- Outputs JSON files to `data/cdn/processed/` for web dashboard

**Exploratory Analysis**: `scripts/exploratory/step01_explore_data_for_dashboard.py`
- Loads processed JSON data for interactive exploration
- Generates temporal, spatial, and co-occurrence analysis
- Creates visualizations saved to `scripts/exploratory/figures/`
- Supports scientific categorization (biological vs anthropogenic sounds)

**Key Features**:
- **Data Type Classification**: Uses `det_column_names.csv` with bio/anthro/info/none types
- **Timestamp Handling**: Rounds timestamps to seconds for proper merging
- **Scientific Terminology**: Only calls biological detections "species"
- **Visualization-Ready**: Exports dashboard-compatible JSON formats

### Deployment Metadata File
The `1_Montie Lab_metadata_deployments_2017 to 2022.xlsx` file contains important metadata about the hydrophone deployments across multiple years (2017-2022). This includes:

- Deployment dates and durations
- Station locations and characteristics
- Equipment specifications and configurations
- Environmental conditions during deployments
- Data collection parameters

This metadata provides crucial context for interpreting the detection, environmental, and acoustic data. It can be used to:
- Validate station information
- Cross-reference deployment periods with detection data
- Understand equipment changes between deployments
- Account for environmental factors in data analysis

## Development Commands

### Data Sync (CDN-based)
```bash
# Smart sync with CDN (only downloads changes)
npm run sync-data              # Sync all files that are outdated
npm run sync-data:check        # Check what needs updating (no downloads)  
npm run sync-data:indices      # Sync only indices files
npm run sync-data:force        # Force download everything
npm run generate-manifest      # Generate manifest from local files
```

### Data Processing (Python with uv)
```bash
# Current processing script (proven working)
uv run scripts/dashboard_prep/process_excel_to_json.py

# Exploratory analysis scripts
uv run scripts/exploratory/step01_explore_data_for_dashboard.py

# Or via npm scripts
npm run process-data                # Process raw data to JSON
npm run validate-data               # Data integrity checks
npm run data-stats                  # Generate summaries
```

### Smart Data Processing Workflow
- **First time setup**: Run `uv sync` to install dependencies, then `uv pip install -e .` to install the package, then `npm run sync-data` to get latest data
- **Daily development**: Just use `npm run dev` (skips data processing)
- **After CDN updates**: Run `npm run sync-data` then `npm run process-data` then `npm run dev`
- **Check what needs updating**: Run `npm run sync-data:check`

### Python Package Setup and Usage

**Initial Setup** (run once after cloning):
```bash
# Install the mbon_analysis package in editable mode (after uv sync)
uv pip install -e .
```

The `mbon_analysis` package provides reusable utilities for acoustic analysis with clean imports:

```python
# Basic data loading (from local files)
from mbon_analysis.core import load_processed_data, load_acoustic_indices

# Load all core datasets
detections, environmental, species_meta, stations = load_processed_data()

# Load with acoustic indices included
*core_data, acoustic_indices = load_processed_data(include_acoustic_indices=True)

# Auto-sync loading (ensures fresh data from CDN)
from mbon_analysis.core import load_with_auto_sync, smart_load

# Automatically check for updates and sync before loading
detections, environmental, species, stations = load_with_auto_sync()

# Smart loading - load only what you need
data = smart_load(["detections", "acoustic_indices"])
detections_df = data["detections"]
indices_df = data["acoustic_indices"]

# CDN sync utilities
from mbon_analysis.core import check_data_freshness, ensure_data_available

# Check what needs updating
status = check_data_freshness("indices")

# Ensure data is available (download if needed)
ensure_data_available("all")

# Analysis modules (now available!)
from mbon_analysis.analysis import (
    # Temporal analysis
    get_monthly_patterns, find_temporal_peaks, analyze_temporal_trends,
    
    # Spatial analysis  
    compare_stations, calculate_station_similarity, get_station_profiles,
    
    # Biodiversity analysis
    calculate_co_occurrence, analyze_bio_anthro_patterns, get_diversity_metrics
)

# Data preparation utilities
from mbon_analysis.core import prepare_detection_data, get_detection_columns, create_dashboard_aggregations
```

**Package Structure**: The `mbon_analysis` package is now a full-featured analysis toolkit with data loading, preparation, and analysis capabilities.

### Package Examples
```bash
# Run usage examples to learn the analysis workflows
uv run scripts/examples/data_loading_example.py        # Basic data loading
uv run scripts/examples/data_sync_example.py           # CDN sync features
uv run scripts/examples/analysis_workflow_example.py   # Comprehensive analysis workflow

# Test individual analysis modules
uv run mbon_analysis/analysis/biodiversity.py          # Biodiversity analysis examples
uv run mbon_analysis/analysis/temporal.py              # Temporal analysis examples
uv run mbon_analysis/analysis/spatial.py               # Spatial analysis examples
```

### Development
```bash
npm run dev                 # Start dev server (uses existing data)
npm run dev:fresh          # Process data + start dev server
npm run build              # Production build (no data processing)
npm run start              # Start production server  
npm run lint               # ESLint check
npm run type-check         # TypeScript check
```

### Testing
```bash
npm run test               # Run unit tests
npm run test:e2e          # End-to-end tests
npm run test:coverage     # Test coverage report
```

## Content Helper Pattern

**IMPORTANT**: All pages MUST use this pattern for text content. See the MkDocs documentation at `docs_site/for-scientists/content-editing.md` and `docs_site/for-developers/content-helper-pattern.md` for full implementation details.

**Purpose**: Separate text content from technical code to enable non-programmer collaboration.

**Structure**: Each page has two files:
- `page.tsx` - Technical dashboard code (components, logic, styling)
- `page.content.tsx` - Text content only (safe for non-programmers to edit)

**Key Rules**:
- Never put user-facing text directly in `.tsx` files
- Always create a corresponding `.content.tsx` file
- Include clear editing instructions in content file comments
- Keep content structure simple (strings only, no HTML/JSX)
- Maintain all styling in the main component file

**Example Content Helper** (`page.content.tsx`):
```typescript
/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 */

export const PageContent = {
  header: {
    title: "Page Title",
    subtitle: "Description of the page"
  },
  sections: {
    main: "Main content text here"
  }
}
```

**Usage in Page** (`page.tsx`):
```typescript
import { PageContent } from './page.content';

export default function Page() {
  return (
    <h1>{PageContent.header.title}</h1>
    <p>{PageContent.header.subtitle}</p>
  );
}
```

## Project Structure
```
mbon-dashboard/
├── src/
│   ├── app/                    # Next.js 14 app directory
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Homepage/overview
│   │   ├── page.content.tsx    # Homepage text content
│   │   ├── species/
│   │   │   ├── page.tsx        # Species analysis
│   │   │   └── page.content.tsx # Species text content
│   │   ├── stations/
│   │   │   ├── page.tsx        # Station comparison
│   │   │   └── page.content.tsx # Station text content
│   │   └── explorer/page.tsx   # Data explorer
│   ├── components/
│   │   ├── charts/             # Observable Plot visualizations
│   │   ├── maps/               # Mapbox components
│   │   ├── filters/            # Filter controls
│   │   ├── export/             # Data export tools
│   │   └── ui/                 # Reusable components
│   ├── lib/
│   │   ├── hooks/              # Custom React hooks (includes useData.ts)
│   │   └── utils/              # Utility functions
│   └── store/                  # Zustand state management
├── public/
│   └── data/                   # Processed JSON files (uploaded to R2)
├── scripts/
│   └── process_data.py         # Python data processing script
└── data/                       # Raw Excel files (not in build)
```

## Key Features Implementation

### 1. Interactive Time Series
- Zoom/pan on temporal data
- Species detection frequency over time
- Environmental correlations
- Acoustic index overlays

### 2. Station Analysis
- Geographic distribution map
- Species diversity comparison
- Environmental gradients
- Acoustic environment characterization

### 3. Species Analysis
- Detection frequency rankings
- Temporal activity patterns
- Co-occurrence analysis
- Acoustic signature correlation

### 4. Data Export
- Filtered dataset download (CSV/JSON)
- Chart image export (PNG/SVG)
- Bulk data packages with metadata
- Custom query results

## Data Architecture

### Data Loading (Frontend)
All data loading is consolidated in `/src/lib/hooks/useData.ts`:
- `useMetadata()` - Loads metadata.json with data summary
- `useStations()` - Loads stations.json with station information
- `useSpecies()` - Loads species.json with species list
- `useAcousticIndices()` - Loads acoustic_indices.json with indices data
- `useCoreData()` - Loads all core data simultaneously

Data is fetched from Cloudflare R2 CDN using the `NEXT_PUBLIC_DATA_URL` environment variable.

### Column Mapping
Uses `data/det_column_names.csv` for short/long name conversion:
- `sp` → Silver perch
- `otbw` → Oyster toadfish boat whistle
- `bde` → Bottlenose dolphin echolocation
- etc.

### File Processing Pattern
Following the `examples.py` approach:
1. Read Excel files (sheet_name=1)
2. Apply column name mapping
3. Extract year/station from filename
4. Combine with environmental and acoustic data
5. Export as optimized JSON for CDN upload

### Data Validation
- Date/time consistency checks
- Species detection validation
- Environmental data quality
- Missing data handling

## Deployment

### Production Deployment Workflow

**Important**: Data processing happens locally, not during deployment.

1. **Process Data Locally**:
   ```bash
   npm run sync-data        # Get latest raw data from CDN
   npm run process-data     # Generate JSON files
   ```

2. **Upload Data to Cloudflare R2**:
   - Upload all files from `public/data/` to R2 bucket
   - Files should be accessible at `https://bucket-name.r2.dev/filename.json`

3. **Configure Environment**:
   ```bash
   # Set in Vercel dashboard or .env.local
   NEXT_PUBLIC_DATA_URL=https://pub-your-id.r2.dev
   ```

4. **Deploy to Vercel**:
   ```bash
   # Connect to GitHub
   git init
   git add .
   git commit -m "Initial MBON dashboard"
   git remote add origin https://github.com/username/mbon-dashboard
   git push -u origin main

   # Deploy via Vercel CLI or dashboard
   npm install -g vercel
   vercel --prod
   ```

**Note**: The Vercel build process does NOT run Python data processing. All data is served from Cloudflare R2 CDN.

### Build Configuration

**`package.json`** (Node.js dependencies and scripts):
```json
{
  "scripts": {
    "sync-data": "uv run scripts/data_management/sync_raw_data.py",
    "sync-data:check": "uv run scripts/data_management/sync_raw_data.py --check-only",
    "sync-data:indices": "uv run scripts/data_management/sync_raw_data.py --indices-only",
    "sync-data:force": "uv run scripts/data_management/sync_raw_data.py --force",
    "generate-manifest": "uv run scripts/data_management/generate_manifest.py",
    "process-data": "uv run scripts/dashboard_prep/process_excel_to_json.py",
    "validate-data": "uv run scripts/utils/validate_data.py",
    "data-stats": "uv run scripts/utils/data_statistics.py",
    "build": "next build",
    "dev": "next dev",
    "dev:fresh": "npm run process-data && next dev",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "dashboard:all": "npm run sync-data && npm run process-data"
  }
}
```

**`pyproject.toml`** (Python dependencies via uv):
```toml
[project]
name = "mbon-dash-2025"
version = "0.1.0"
dependencies = [
    "pandas>=2.3.1",
    "openpyxl>=3.1.5", 
    "numpy>=2.3.2",
    "matplotlib>=3.10.5",
    "seaborn>=0.13.2",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["mbon_analysis*", "scripts*"]
```

## Responsive Dashboard Design Best Practices

### Multi-Screen Strategy
Professional dashboards follow an established approach for handling different screen sizes and devices:

#### **Desktop-First Philosophy**
- **Complex data visualization** assumes desktop/laptop usage for detailed analysis
- **Full feature set** available with large screens and mouse interaction
- **Multiple panels** and detailed charts work well on wide screens

#### **Mobile-Responsive but Simplified**  
- **Key metrics prominently displayed** - show overview statistics and high-level insights
- **Simplified charts** - reduce complexity, aggregate data (e.g., yearly vs monthly)
- **Progressive disclosure** - "View full analysis" links to desktop experience
- **Touch-friendly controls** - larger buttons, simplified interactions

#### **Responsive Breakpoints**
- **< 600px (Mobile)**: Single column, simplified charts, key metrics only
- **600-1024px (Tablet)**: Two columns, medium complexity charts
- **> 1024px (Desktop)**: Full layout, complex visualizations, multiple panels

#### **Chart-Specific Responsive Strategies**
1. **Data Aggregation**: Monthly data → Yearly data (fewer columns)
2. **Fixed Font Sizes**: Prevent tiny text on small screens
3. **Horizontal Scrolling**: Acceptable for tables/timelines on mobile
4. **Simplified Color Schemes**: Avoid overly complex legends on small screens
5. **Tooltip Over Labels**: Hover/touch for details instead of cramped text

#### **Industry Examples**
- **Tableau/PowerBI**: Desktop-focused with mobile companion apps
- **Google Analytics**: Simplified mobile dashboard, full desktop experience
- **Financial Dashboards**: Key metrics on mobile, detailed charts on desktop

### Implementation Guidelines
- Use responsive margins and font sizes based on screen width
- Implement ResizeObserver for dynamic chart reflow
- Test at multiple breakpoints during development
- Consider touch interactions for mobile users

## Performance Considerations

### Data Loading Strategy
- Lazy load large datasets on demand
- Implement virtual scrolling for tables
- Cache processed data in IndexedDB
- Debounce filter updates (300ms)

### Optimization Techniques
- Memoize expensive calculations
- Use React.memo for chart components
- Implement chart data sampling for large datasets
- Progressive data loading by date range

## Future Enhancements

### Acoustic Analysis Integration
- Spectral analysis visualization
- Acoustic index correlation matrix
- Sound event clustering
- Machine learning species classification

### Advanced Features
- Real-time data updates
- Collaborative annotations
- Statistical trend analysis
- Environmental impact modeling

## Troubleshooting

### Common Issues
- **Excel reading errors**: Check file format and sheet names
- **Date parsing issues**: Verify date column format consistency
- **Memory issues**: Implement data chunking for large files
- **Chart rendering**: Check data structure and missing values

### Data Quality Checks
```bash
npm run validate-data      # Run data validation
npm run data-stats        # View data summary statistics
```

## Contributing
1. Update raw data files in `data/` directory
2. Run `npm run build-data` to regenerate JSON files
3. Test changes with `npm run dev`
4. Commit processed JSON files along with raw data

## Research Questions to Address

### **🎯 Primary Research Questions (Phase 1) - UPDATED**
1. **Index Dimensionality Reduction**
   - Can we reduce 56+ acoustic indices to 3-5 "super indices" that capture most environmental variation?
   - Which indices contribute most to the first 3 principal components?
   - What percentage of variance do the top components explain?

2. **Biodiversity Prediction Capability**
   - Which acoustic indices (or index combinations) best predict species detection patterns?
   - Can PCA-derived components predict biodiversity better than individual indices?
   - How do index-based predictions compare to environmental predictors (temp/depth)?

3. **Index Categories Performance**
   - Do certain index categories (diversity, complexity, bioacoustic) outperform others?
   - Which temporal vs frequency domain indices are most informative?
   - Are there redundant index categories we can eliminate?

### **🔍 Secondary Research Questions (Phase 2)**
4. **Spatial and Temporal Patterns**
   - How do acoustic environments differ between stations (9M, 14M, 37M)?
   - Are there consistent temporal patterns (hourly, seasonal) in key indices?
   - Multi-year stability: Do index patterns remain consistent (2018 vs 2021)?

5. **Environmental Interactions**
   - Do temperature and depth cycles drive index variation independent of biology?
   - Should indices be environmentally corrected for better biodiversity assessment?
   - Which indices are most/least affected by environmental confounders?

6. **Method Effectiveness Assessment**
   - Can a reduced index set provide equivalent biodiversity information to manual annotation?
   - What is the processing time/computational trade-off for different index sets?
   - Analysis of information retention vs simplification

### **🔮 Future Research Questions (Phase 3)**
7. **Practical Implementation**
   - Can real-time index calculation support adaptive monitoring strategies?
   - How do results scale to other estuarine environments?
   - Integration with existing marine monitoring programs

8. **Advanced Modeling**
   - Machine learning models using top-performing indices for species prediction
   - Bandwidth comparison: Does analysis of different frequency ranges improve predictions?
   - Automated index selection algorithms for new environments

### **🎓 Science Communication Goals**
- Make acoustic indices accessible to non-acoustics researchers
- Demonstrate effectiveness of acoustic monitoring for biodiversity assessment
- Provide actionable recommendations for marine monitoring programs

## Project Workflow

### **Python Analysis (Heavy Computation)**
- **Core Subpackage (`mbon_analysis/`)**: Reusable utilities for acoustic analysis, PCA, correlation matrices (integrated within project)
- **Application Scripts (`scripts/`)**: Project-specific processing and exploratory workflows  
- **Analysis Workflow**: Step-based exploratory scripts that import and use subpackage functions
- **Research Focus**: Acoustic indices evaluation, dimensionality reduction, biodiversity prediction

### **Web Dashboard (Interactive Visualization)**
- Real-time filtering and exploration of processed results
- Interactive charts with Observable Plot and Mapbox
- User-friendly interface for scientists and managers
- Pre-computed visualizations served from CDN

### **Success Metrics**
- Identify key acoustic indices that predict species detection patterns
- Reduce 56+ indices to manageable set of "super indices" via PCA
- Demonstrate automated analysis capabilities vs manual annotation
- Clear visualizations showing index-biodiversity relationships

## Development Notes
- Don't run `npm run dev` - the user will do that in a separate terminal window. Just tell them when they're ready to run.
- Don't write commit messages or commit/push code - the user handles version control.
- CLAUDE.md should not use conversational language like "you" or "your".

## Current Implementation Status

### ✅ **Completed**
- Next.js 14 with TypeScript and Tailwind CSS setup
- Modern ocean-themed design with Google Fonts
- Navigation system across all pages
- Vercel deployment configuration (frontend only)
- Interactive station map with Mapbox GL JS
- Data loading hooks in `useData.ts`
- Cloudflare R2 CDN integration for data storage

### ✅ **Recently Completed (Data Foundation & Visualization)**
- **Acoustic indices processing** - new CSV files integrated with full processing pipeline (17,231 records)
- **CDN sync system** - manifest-based file discovery and smart downloading with change detection
- **Data filtered to 2018, 2021, 9M/14M/37M only** - 3 stations, 2 years as intended
- **Sheet selection corrected** - environmental/acoustic files now use sheet 1
- **Primary data prioritized** - Manual detection files properly emphasized
- **Species Activity Timeline Heatmap** - implemented with Observable Plot
- **Observable Plot integration** - replaced Plotly.js for better performance

### 🚧 **In Progress (MVP Focus)**
- Station map (✅ working with correct 3 stations)
- Dashboard metrics (✅ showing correct scope and data)
- Species activity timeline (✅ completed with Observable Plot heatmap)
- Species analysis page (placeholder)
- Temporal patterns page (placeholder)
- Data explorer page (placeholder)

### 🔮 **Planned (After Data Fixed)**
- Interactive charts and visualizations
- Data filtering and export functionality
- Species detection analysis tools
- Environmental correlation features

### 🎯 **Current Priority: Site Restructuring**
1. ✅ **Foundation Complete** - Data processing, Observable Plot integration, working dashboard
2. ✅ **Research focus refined** - Soundscape biodiversity and acoustic indices as proxies
3. ✅ **Python package structure** - Integrated `mbon_analysis` subpackage for reusable utilities
4. **NEXT: Implement restructured pages** following `docs/site-restructuring-plan.md`:
   - `/acoustic-biodiversity` - Primary analysis (PCA, correlations, rankings)
   - `/environmental-factors` - Temperature/depth confounders
   - `/acoustic-glossary` - Index education and science communication
   - Enhanced `/stations` - Spatial context and deployment details
5. **Phase 1 Goal**: Answer core question "Which acoustic indices best predict soundscape biodiversity?"

### 📝 **TODO: Documentation Updates**
- Update Python workflow documentation to reflect tightly coupled subpackage approach
- Document migration pattern for moving utilities from scripts to `mbon_analysis` subpackage
- Create examples showing how to use subpackage functions in exploratory scripts
- Add testing guidelines for subpackage utilities

---

### Extra notes
- don't launch the site using npm run dev unless I ask you to, normally I will want to do that myself.
- don't edit code or make changes to the site unless I ask you to.
- always attempt to follow best practices and standards for coding and design.
- Keep CLAUDE.md up to date as we go. If our plan changes I want to make sure that is captured.

---

*Last updated: August 2025*
*Current focus: Acoustic indices integration and PCA analysis*