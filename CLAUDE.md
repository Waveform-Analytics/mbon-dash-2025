# Marine Biodiversity Dashboard (MBON-USC-2025)

## Project Overview
Interactive web dashboard for exploring marine acoustic monitoring data from the OSA MBON project. Visualizes species detections, temporal patterns, station comparisons, and acoustic indices to understand relationships between acoustic environment and species presence.

## Data Structure

### **Primary Data (Core Focus)**
- **Detection Data**: Manual species annotations from hydrophone recordings
  - **Years**: 2018, 2021 ONLY
  - **Stations**: 9M, 14M, 37M ONLY
  - **Files**: Master_Manual_[STATION]_2h_[YEAR].xlsx (sheet 1)
  - **Purpose**: Primary dataset for species detection analysis

### **Secondary Data (For Correlations)**
- **Environmental Data**: Temperature and depth measurements
  - **Temperature**: Master_[STATION]_Temp_[YEAR].xlsx (sheet 1)
  - **Depth**: Master_[STATION]_Depth_[YEAR].xlsx (sheet 1)
- **Acoustic Indices**: RMS Sound Pressure Level (rmsSPL) measurements  
  - **Files**: Master_rmsSPL_[STATION]_1h_[YEAR].xlsx (sheet 1)
- **Deployment Metadata**: Filtered to relevant deployments only (2018, 2021, 9M/14M/37M)

### **Important Notes**
- **Only 3 stations of interest**: 9M, 14M, 37M (ignore B, C, CC4, CR1, D, WB)
- **Only 2 years of interest**: 2018, 2021 (ignore other years)
- **Sheet selection**: Manual files use sheet 1, all others use sheet 1 (NOT sheet 0)
- **Data priority**: Manual detection files are PRIMARY, others are secondary for correlation analysis

## Technology Stack
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS
- **Visualization**: Observable Plot (primary), Mapbox GL JS, D3.js utilities
- **State Management**: Zustand
- **Data Processing**: Python (uv) for local processing, Cloudflare R2 CDN for storage
- **Deployment**: Vercel (frontend only)

## Principles and Best Practices
- Always use best practices and aim for tidiness and good documentation

## Development Guidelines
- Don't write commit messages for me, or commit or push. 

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
data/
├── 1_Montie Lab_metadata_deployments_2017 to 2022.xlsx  # Deployment metadata across years
├── 2018/
│   ├── Master_Manual_[STATION]_2h_2018.xlsx    # Species detections
│   ├── Master_[STATION]_Temp_2018.xlsx         # Temperature data
│   ├── Master_[STATION]_Depth_2018.xlsx        # Depth data
│   └── Master_rmsSPL_[STATION]_1h_2018.xlsx    # Acoustic indices
└── 2021/
    └── [similar structure with more stations]
```

### Data Processing Script (`scripts/process_data.py`)
**Using Python for data processing (RECOMMENDED)** - processes the focused dataset:

1. **Process Detection Files**: Merge Manual detection files (PRIMARY DATA)
   - **Scope**: 2018, 2021 years ONLY + 9M, 14M, 37M stations ONLY
   - **Files**: 6 Manual files (3 stations × 2 years)
   - **Sheet**: Always sheet 1 for Manual files

2. **Process Environmental Data**: Join temperature and depth measurements (SECONDARY)
   - **Files**: 12 environmental files (6 temp + 6 depth)
   - **Sheet**: Always sheet 1 (NOT sheet 0)

3. **Process Acoustic Indices**: Merge rmsSPL data (SECONDARY) 
   - **Files**: 6 rmsSPL files (3 stations × 2 years)
   - **Sheet**: Always sheet 1 (NOT sheet 0)

4. **Filter Deployment Metadata**: Only relevant deployments (2018, 2021, 9M/14M/37M)

5. **Output Filtered JSON Files**: Optimized for focused analysis

```bash
uv run scripts/process_data.py
# Creates filtered datasets:
# - public/data/detections.json (6 detection files, PRIMARY)
# - public/data/environmental.json (12 temp/depth files, SECONDARY)
# - public/data/acoustic.json (6 rmsSPL files, SECONDARY)
# - public/data/deployment_metadata.json (filtered ~6-12 records)
# - public/data/stations.json (3 stations: 9M, 14M, 37M)
# - public/data/species.json (species from detection data)
# - public/data/metadata.json (corrected summary statistics)
```

**UPDATED**: Script has been corrected and data regenerated with proper scope (3 stations, 2018/2021 only).

**Why Python over Node.js for data processing:**
- Superior pandas/numpy ecosystem for scientific data
- Better Excel file handling and data validation
- Existing codebase in `examples.py` can be extended
- Standard practice in research data pipelines

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

### Data Processing (Python with uv)
```bash
# Direct uv commands (recommended)
uv run scripts/process_data.py      # Process Excel files to JSON
uv run scripts/check_data_freshness.py  # Check if data needs reprocessing
uv run scripts/validate_data.py     # Check data integrity  
uv run scripts/data_stats.py        # Generate data summary

# Or via npm scripts (calls uv under the hood)
npm run build-data                   # Runs: uv run scripts/process_data.py
npm run validate-data               # Runs: uv run scripts/validate_data.py
npm run data-stats                  # Runs: uv run scripts/data_stats.py
```

### Smart Data Processing Workflow
- **First time setup**: Run `npm run dev:fresh` to process data and start
- **Daily development**: Just use `npm run dev` (skips data processing)
- **After updating Excel files**: Run `npm run build-data` then `npm run dev`
- **Check if data is stale**: Run `uv run scripts/check_data_freshness.py`

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

## Project Structure
```
mbon-dashboard/
├── src/
│   ├── app/                    # Next.js 14 app directory
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Homepage/overview
│   │   ├── species/page.tsx    # Species analysis
│   │   ├── stations/page.tsx   # Station comparison
│   │   ├── temporal/page.tsx   # Temporal patterns
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
   uv run scripts/process_data.py  # Generate JSON files
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
    "build-data": "uv run scripts/process_data.py",
    "validate-data": "uv run scripts/validate_data.py", 
    "data-stats": "uv run scripts/data_stats.py",
    "build": "next build",
    "dev": "next dev",
    "dev:fresh": "npm run build-data && next dev",
    "lint": "next lint",
    "clean": "rm -rf .next out",
    "clean:data": "rm -rf public/data/*"
  }
}
```

**`pyproject.toml`** (Python dependencies via uv):
```toml
[project]
name = "mbon-dashboard"
version = "0.1.0"
dependencies = [
    "pandas>=2.0.0",
    "openpyxl>=3.1.0", 
    "numpy>=1.24.0"
]
requires-python = ">=3.9"
```

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

### **Primary Analysis (Detection-Focused)**
- Species detection patterns across the 3 stations (9M, 14M, 37M)
- Temporal patterns in species presence between 2018 and 2021
- Station-specific species diversity and detection frequency
- Seasonal and daily patterns in species activity

### **Secondary Analysis (Correlation-Focused)**
- Correlation between acoustic indices (rmsSPL) and species detections
- Environmental drivers of species presence (temperature, depth effects)
- How environmental conditions relate to detection success
- Multi-year changes in ecosystem composition (2018 vs 2021)

### **Methodological Questions**
- Data quality and detection consistency across stations
- Temporal coverage and sampling effectiveness
- Relationships between different data types (manual vs automated)

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
- **Data processing script updated** - now correctly processes focused scope
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

### 🎯 **Current Priority**
1. ✅ **Data processing fixed** - 3 stations, 2018/2021 scope confirmed
2. ✅ **JSON files regenerated** and uploaded to CDN
3. ✅ **Dashboard verified** - showing 3 stations correctly
4. ✅ **Species activity timeline** - Interactive heatmap completed with Observable Plot
5. **Build basic versions of remaining pages** (species, temporal, explorer)
6. **Polish and refinements** (see `docs/future-improvements.md`)

---

*Last updated: $(date)*
*Data processing based on existing examples.py workflow*