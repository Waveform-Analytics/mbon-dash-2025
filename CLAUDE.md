# Marine Biodiversity Dashboard (MBON-USC-2025)

## Project Overview
Interactive web dashboard exploring whether acoustic indices can predict marine soundscape biodiversity and serve as cost-effective proxies for complex biodiversity monitoring. The core research question: "Can computed acoustic indices help us understand and predict marine biodiversity patterns as an alternative to expensive, labor-intensive manual species detection methods?"

**Research Focus**: Analyzing relationships between 56+ acoustic indices and species presence across 3 stations in May River, South Carolina, with emphasis on identifying the most informative indices for biodiversity assessment and understanding environmental confounding factors.

**Key Goals**:
- Identify which acoustic indices best predict species detection patterns
- Use PCA to reduce 56 indices to a smaller set of "super indices" 
- Develop cost-effective alternatives to manual species annotation
- Understand spatial (between stations) and temporal patterns in acoustic environments

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
- **Legacy Acoustic Data**: RMS Sound Pressure Level (rmsSPL) measurements  
  - **Files**: Master_rmsSPL_[STATION]_1h_[YEAR].xlsx (sheet 1)
  - **Note**: Being replaced by comprehensive acoustic indices (see below)
- **Deployment Metadata**: Filtered to relevant deployments only (2018, 2021, 9M/14M/37M)

### **NEW: Comprehensive Acoustic Indices (Primary Analysis Focus)**
- **Source**: Collaborator-provided CSV files with 56 acoustic indices
- **Temporal Resolution**: Hourly (aggregated to 2-hour windows to match detections)
- **Expected Files**: 
  - `AcousticIndices_[STATION]_FullBW_v1.csv` (Full bandwidth)
  - `AcousticIndices_[STATION]_[OTHER_BW]_v1.csv` (Additional bandwidth - TBD)
- **Stations**: 9M (received), 14M & 37M (expected)
- **Years**: 2021 (received), 2018 (expected)
- **Index Categories**:
  - Temporal domain: ZCR, MEANt, VARt, SKEWt, KURTt, LEQt, etc.
  - Frequency domain: MEANf, VARf, SKEWf, KURTf, NBPEAKS, etc.
  - Acoustic complexity: ACI, NDSI, ADI, AEI
  - Diversity indices: H_Havrda, H_Renyi, H_pairedShannon, RAOQ, etc.
  - Bioacoustic: BioEnergy, AnthroEnergy, BI, rBA
  - Spectral coverage: LFC, MFC, HFC

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

### UPDATED: Data Structure (Post-Acoustic Indices Integration)

```
mbon-dash-2025/
├── data/                           # Raw data (committed to git)
│   ├── indices/
│   │   └── raw/                   # Raw acoustic indices from collaborator
│   │       ├── AcousticIndices_9M_FullBW_v1.csv      # ✅ Received
│   │       ├── AcousticIndices_14M_FullBW_v1.csv     # 🔄 Expected
│   │       ├── AcousticIndices_37M_FullBW_v1.csv     # 🔄 Expected  
│   │       ├── AcousticIndices_9M_[OTHER_BW]_v1.csv  # 🔄 Expected
│   │       └── ... (additional stations/years/bandwidths)
│   ├── 1_Montie Lab_metadata_deployments_2017 to 2022.xlsx
│   ├── 2018/                      # Legacy detection/environmental data
│   │   ├── Master_Manual_[STATION]_2h_2018.xlsx
│   │   ├── Master_[STATION]_Temp_2018.xlsx
│   │   ├── Master_[STATION]_Depth_2018.xlsx
│   │   └── Master_rmsSPL_[STATION]_1h_2018.xlsx  # Legacy - keep for comparison
│   └── 2021/                      # [similar structure]
│
├── processed/                      # Intermediate processing (gitignored)
│   ├── indices/                   # Cleaned index data
│   │   ├── indices_9M_2021.json
│   │   ├── indices_14M_2021.json  
│   │   └── indices_combined.json   # All stations/years/bandwidths
│   ├── detections/               # Processed detection data
│   ├── environmental/            # Processed environmental data  
│   └── combined/                 # Temporally aligned datasets
│       ├── full_dataset.json     # All data types joined
│       └── analysis_ready.json   # Filtered for PCA
│
├── analysis/                      # Analysis results (gitignored) 
│   ├── pca/                      # PCA results, loadings, component scores
│   │   ├── pca_loadings.json
│   │   ├── pca_scores.json
│   │   └── explained_variance.json
│   ├── correlations/             # Index-species correlation matrices
│   ├── summaries/               # Statistical summaries
│   └── model_results/           # Predictive model outputs
│
├── cdn/                          # CDN-ready data (gitignored)
│   ├── dashboard-data.json      # Lightweight dashboard data
│   ├── pca-results.json        # Pre-computed PCA for visualization
│   ├── index-summaries.json    # Key metrics and trends
│   └── station-profiles.json   # Station-specific acoustic profiles
│
└── public/                      # Static assets only (no data files)
    ├── images/
    └── icons/
```

### UPDATED: Processing Pipeline Architecture

The data processing has been redesigned as a modular pipeline to handle the integration of comprehensive acoustic indices with existing detection and environmental data.

#### **Pipeline Overview**
```bash
# Complete pipeline (run when new data arrives)
uv run scripts/pipeline/run_full_pipeline.py

# Individual processing steps (for development/debugging)
uv run scripts/pipeline/steps/1_process_raw_data.py
uv run scripts/pipeline/steps/2_align_temporal_windows.py  
uv run scripts/pipeline/steps/3_join_datasets.py
uv run scripts/pipeline/steps/4_handle_missing_data.py
uv run scripts/pipeline/steps/5_run_pca_analysis.py
uv run scripts/pipeline/steps/6_prepare_dashboard_data.py

# Analysis scripts (heavy computational work)
uv run scripts/analysis/pca_analysis.py
uv run scripts/analysis/correlation_analysis.py
uv run scripts/analysis/biodiversity_models.py
```

#### **Step-by-Step Processing**

**Step 1: Process Raw Data**
- **Detection Files**: Master_Manual_[STATION]_2h_[YEAR].xlsx (6 files)
- **Environmental Files**: Temperature/Depth files (12 files) 
- **Acoustic Indices**: AcousticIndices_[STATION]_[BANDWIDTH]_v1.csv (flexible count)
- **Deployment Metadata**: Filter to relevant deployments
- **Output**: `processed/` directory with cleaned JSON files

**Step 2: Temporal Alignment** 
- **Challenge**: Indices are hourly, detections are 2-hourly
- **Solution**: Aggregate indices to 2-hour windows using configurable methods (mean, max, etc.)
- **Missing Data**: Flag gaps, apply interpolation rules
- **Output**: `processed/combined/aligned_windows.json`

**Step 3: Dataset Joining**
- **Join Criteria**: Station + datetime windows
- **Data Prioritization**: Detection data drives temporal scope
- **Quality Control**: Flag mismatched windows, missing periods
- **Output**: `processed/combined/full_dataset.json`

**Step 4: Missing Data Handling**
- **Short gaps (≤2 hours)**: Linear interpolation with QC flags
- **Medium gaps (2-6 hours)**: Mark as "interpolated" 
- **Long gaps (>6 hours)**: Exclude from analysis
- **Output**: `processed/combined/analysis_ready.json`

**Step 5: PCA Analysis** (Heavy Computation)
- **Index Filtering**: Remove low-variance, highly-correlated indices
- **PCA Computation**: Principal components, loadings, explained variance
- **Component Analysis**: Identify key indices for each component
- **Output**: `analysis/pca/` directory with multiple JSON files

**Step 6: Dashboard Data Preparation**
- **Data Reduction**: Extract key metrics, trends, PCA results  
- **Visualization Prep**: Format for Observable Plot consumption
- **CDN Optimization**: Compress, split by usage patterns
- **Output**: `cdn/` directory ready for upload

#### **Flexible File Handling**

The pipeline automatically detects and processes available acoustic index files:

```python
# File pattern matching (flexible for new datasets)
ACOUSTIC_INDEX_PATTERNS = [
    "AcousticIndices_{station}_{bandwidth}_v*.csv",
    "Acoustic_Indices_{station}_{bandwidth}_v*.csv"  # Handle naming variations
]

# Supported configurations
EXPECTED_STATIONS = ["9M", "14M", "37M"]
EXPECTED_YEARS = [2018, 2021] 
BANDWIDTH_TYPES = ["FullBW", "LowBW", "HighBW"]  # Flexible list

# Processing behavior:
# - Process all found files matching patterns
# - Log missing expected files  
# - Handle naming variations gracefully
# - Support future bandwidth types automatically
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
# UPDATED: Pipeline processing (recommended for full workflow)
uv run scripts/pipeline/run_full_pipeline.py    # Complete data processing pipeline
uv run scripts/pipeline/run_partial_pipeline.py --steps 1,2,3  # Run specific steps

# Individual pipeline steps (for development)
uv run scripts/pipeline/steps/1_process_raw_data.py
uv run scripts/pipeline/steps/2_align_temporal_windows.py
uv run scripts/pipeline/steps/3_join_datasets.py
uv run scripts/pipeline/steps/4_handle_missing_data.py
uv run scripts/pipeline/steps/5_run_pca_analysis.py
uv run scripts/pipeline/steps/6_prepare_dashboard_data.py

# Analysis scripts (computationally intensive)
uv run scripts/analysis/pca_analysis.py         # Principal component analysis
uv run scripts/analysis/correlation_analysis.py  # Index-species correlations
uv run scripts/analysis/biodiversity_models.py  # Predictive models

# Legacy/utility scripts (maintained for compatibility)
uv run scripts/legacy/process_data.py           # Original processing script
uv run scripts/legacy/validate_data.py          # Data integrity checks
uv run scripts/legacy/data_stats.py             # Generate data summaries

# Or via npm scripts (calls uv under the hood)
npm run build-data                   # Runs full pipeline
npm run validate-data               # Runs validation
npm run data-stats                  # Runs statistics
npm run build-analysis             # Runs PCA and correlation analysis
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

6. **Cost-Effectiveness Assessment**
   - Can a reduced index set provide equivalent biodiversity information to manual annotation?
   - What is the processing time/computational cost trade-off for different index sets?
   - ROI analysis: effort savings vs information loss

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
- Demonstrate cost-effectiveness of acoustic monitoring for biodiversity assessment
- Provide actionable recommendations for marine monitoring programs

## Implementation Timeline & Milestones

### **Phase 1: Data Integration & Basic Analysis (Weeks 1-2)**

**Week 1: Infrastructure Setup**
- ✅ Restructure data folders (`data/`, `processed/`, `analysis/`, `cdn/`)
- ✅ Create flexible acoustic indices processing pipeline
- ✅ Implement temporal alignment (hourly → 2-hour windows)
- ✅ Basic PCA analysis with 9M 2021 data

**Week 2: Multi-Dataset Integration**  
- ⏳ Extend pipeline for multiple stations/bandwidths (when available)
- ⏳ Missing data handling implementation
- ⏳ Dashboard integration: Index Explorer page
- ⏳ **Milestone 1 Presentation**: "Here's what the acoustic indices look like"

### **Phase 2: PCA Analysis & Insights (Weeks 3-4)**

**Week 3: Advanced Analysis**
- ⏳ Index filtering and dimensionality reduction
- ⏳ Full PCA analysis with component interpretation
- ⏳ Index-species correlation analysis
- ⏳ Environmental confounder assessment

**Week 4: Visualization & Results**
- ⏳ Interactive PCA dashboard components  
- ⏳ Top indices identification and ranking
- ⏳ Station comparison analysis
- ⏳ **Milestone 2 Presentation**: "Here's what we're learning from the indices"

### **Phase 3: Predictive Models & Recommendations (Weeks 5-6)**

**Week 5: Model Development**
- ⏳ Biodiversity prediction models using reduced index sets
- ⏳ Cost-effectiveness analysis
- ⏳ Cross-validation and model performance assessment
- ⏳ Environmental correction experiments

**Week 6: Final Integration**
- ⏳ Dashboard completion with all analysis results
- ⏳ Index recommendation system
- ⏳ Documentation and methodology writeup
- ⏳ **Final Presentation**: "Here's what managers should use"

### **Flexible Timeline Notes**
- Timeline adjusts based on data availability from collaborators
- Each milestone can be presented independently
- Pipeline designed to incorporate new datasets as they arrive
- Dashboard iterates based on analysis discoveries

### **Success Metrics**
- **Technical**: Pipeline processes new acoustic index files automatically
- **Scientific**: Identify <10 key indices that explain >70% of biodiversity variation
- **Practical**: Demonstrate computational cost savings vs manual annotation
- **Communication**: Clear visualizations showing index-biodiversity relationships

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

### 🎯 **Current Priority: Site Restructuring**
1. ✅ **Foundation Complete** - Data processing, Observable Plot integration, working dashboard
2. ✅ **Research focus refined** - Soundscape biodiversity and acoustic indices as proxies
3. **NEXT: Implement restructured pages** following `docs/site-restructuring-plan.md`:
   - `/acoustic-biodiversity` - Primary analysis (PCA, correlations, rankings)
   - `/environmental-factors` - Temperature/depth confounders
   - `/acoustic-glossary` - Index education and science communication
   - Enhanced `/stations` - Spatial context and deployment details
4. **Phase 1 Goal**: Answer core question "Which acoustic indices best predict soundscape biodiversity?"

---

*Last updated: $(date)*
*Data processing based on existing examples.py workflow*