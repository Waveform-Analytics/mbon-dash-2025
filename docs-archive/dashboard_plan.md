# Marine Biodiversity Dashboard Project Plan

## Executive Summary
This document outlines the development plan for an interactive web dashboard to explore marine acoustic monitoring data from the OSA MBON project. The dashboard will enable researchers and stakeholders to visualize species detections, temporal patterns, and station comparisons through a modern, highly interactive interface. One of the primary goals is to incorporate acoustic indices (computed from hydrophone recordings) to try to learn if there are any relationships between acoustic indices and the detection data.

## Recommended Technology Stack: Next.js Static Data Approach

### Why This Simplified Architecture?

**Key Decision Factors:**
- **Small dataset**: Combined data is only ~5MB (perfect for client-side processing)
- **Static data**: No frequent updates needed once processed
- **Cost-effective**: Single deployment (Vercel only)
- **Simpler development**: No backend complexity, CORS issues, or API debugging

### Technology Benefits:

**Next.js with Static Data:**
- Maximum flexibility for interactive visualizations
- Can integrate multiple chart libraries (Plotly.js, D3.js, Mapbox GL)
- Client-side interactions with zero latency
- All data cached in browser after initial load
- Easy deployment via Vercel (potentially free tier)
- Works offline after initial load

**Future-Proof Design:**
- Can easily migrate to API approach if data grows
- Component architecture supports either data source
- Filter/aggregation logic reusable

## Repository Structure

### Single Repository: mbon-dashboard (Next.js)
```
mbon-dashboard/
├── src/
│   ├── app/                 # Next.js 14 app directory
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Homepage/overview
│   │   ├── species/
│   │   │   └── page.tsx     # Species analysis page
│   │   ├── stations/
│   │   │   └── page.tsx     # Station analysis page
│   │   ├── temporal/
│   │   │   └── page.tsx     # Temporal patterns page
│   │   └── explorer/
│   │       └── page.tsx     # Data explorer page
│   ├── components/
│   │   ├── charts/
│   │   │   ├── TimeSeriesChart.tsx
│   │   │   ├── SpeciesBarChart.tsx
│   │   │   ├── HeatmapChart.tsx
│   │   │   └── InteractiveScatter.tsx
│   │   ├── maps/
│   │   │   ├── StationMap.tsx
│   │   │   └── MarkerCluster.tsx
│   │   ├── filters/
│   │   │   ├── DateRangePicker.tsx
│   │   │   ├── SpeciesSelector.tsx
│   │   │   ├── StationSelector.tsx
│   │   │   └── FilterPanel.tsx
│   │   ├── layout/
│   │   │   ├── Navigation.tsx
│   │   │   ├── Header.tsx
│   │   │   └── MobileMenu.tsx
│   │   ├── export/
│   │   │   ├── DataExporter.tsx
│   │   │   └── PlotExporter.tsx
│   │   └── ui/              # Reusable UI components
│   │       ├── Card.tsx
│   │       ├── Button.tsx
│   │       └── Modal.tsx
│   ├── lib/
│   │   ├── data/
│   │   │   ├── loader.ts    # Load static data files
│   │   │   ├── processor.ts # Client-side data processing
│   │   │   └── aggregator.ts # Data aggregation functions
│   │   ├── hooks/           # Custom React hooks
│   │   │   ├── useData.ts   # Data loading/caching
│   │   │   ├── useFilters.ts
│   │   │   └── useChartInteraction.ts
│   │   └── utils/
│   │       ├── formatters.ts
│   │       ├── constants.ts
│   │       └── export.ts    # Client-side export functions
│   ├── store/               # State management (Zustand)
│   │   ├── filterStore.ts
│   │   ├── dataStore.ts
│   │   └── uiStore.ts
│   └── styles/
│       └── globals.css      # Tailwind CSS
├── public/
│   ├── data/                # Static data files
│   │   ├── detections.json  # Main dataset (~5MB)
│   │   ├── stations.json    # Station metadata
│   │   ├── species.json     # Species lookup
│   │   └── metadata.json    # Column definitions, etc.
│   └── images/
├── scripts/
│   └── processData.js       # Convert Excel to JSON (build-time)
├── tests/
├── next.config.js
├── tailwind.config.js
├── package.json
├── .env.local.example
└── README.md
```

## Core Technologies & Libraries

### Technology Stack:
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better developer experience
- **Tailwind CSS** - Utility-first styling
- **Plotly.js** - Interactive scientific charts (zoom, pan, export)
- **Mapbox GL JS** - Advanced mapping capabilities
- **Zustand** - Client state management (no server state needed)
- **date-fns** - Date manipulation
- **file-saver** - Client-side file downloads
- **Papa Parse** - CSV parsing/generation

### Data Processing (Build-time only):
- **Node.js scripts** - Convert Excel to JSON
- **Pandas** (Python) - Alternative data processing option

### Deployment:
- **Vercel** - Hosting and CI/CD (potentially free tier)
- **GitHub Actions** - Data processing pipeline (optional)

## Core Features

### 1. Overview Dashboard
- Key metrics cards (total detections, species count, active stations)
- Year-over-year comparison summary
- Interactive map of station locations

### 2. Species Analysis Tab
- Species detection rankings
- Temporal patterns by species
- Year comparison charts
- Species co-occurrence analysis

### 3. Station Analysis Tab
- Station activity comparison
- Species diversity by station
- Environmental correlations (temp/depth if available)
- Station-specific temporal patterns

### 4. Temporal Patterns Tab
- Monthly/seasonal trends
- Hour-of-day patterns (if time data available)
- Long-term trends
- Anomaly detection

### 5. Data Explorer Tab
- Filter by date range, species, station
- Download filtered data
- Custom query builder
- Raw data table view

## Implementation Phases

### Phase 1: Foundation & Data Processing (1 week)
- [ ] Set up GitHub repository
- [ ] Create data processing script (Excel → JSON)
- [ ] Set up Next.js with TypeScript and Tailwind
- [ ] Create basic layout and navigation
- [ ] Implement data loading system
- [ ] Deploy to Vercel

### Phase 2: Core Interactive Features (2 weeks)
- [ ] Implement interactive time series charts with zoom/pan
- [ ] Create species comparison visualizations
- [ ] Add station map with Mapbox GL
- [ ] Build filter system with Zustand state management
- [ ] Add loading states and error handling
- [ ] Create responsive mobile layouts

### Phase 3: Advanced Features (2 weeks)
- [ ] Implement client-side data export functionality
- [ ] Create advanced filtering and query builder
- [ ] Add temporal pattern analysis
- [ ] Add data comparison tools
- [ ] Create shareable dashboard states (URL parameters)
- [ ] Add comprehensive chart interactions

### Phase 4: Polish & Future Extensions (1-2 weeks)
- [ ] Performance optimization (data loading, chart rendering)
- [ ] Add comprehensive documentation
- [ ] Design system for acoustic data integration
- [ ] Implement user preferences/saved views
- [ ] SEO optimization
- [ ] Accessibility improvements

## Data Architecture & Processing

### Simplified Data Flow:
```
Excel Files → Build Script → JSON Files → Next.js (Client-side Processing)
```

### Data Processing Strategy:

1. **Build-time Processing**:
   ```javascript
   // scripts/processData.js
   const XLSX = require('xlsx');
   const fs = require('fs');
   
   // Process Excel files into optimized JSON
   const processExcelFiles = () => {
     const detections = [];
     const stations = new Set();
     const species = new Set();
     
     // Combine all Excel files
     excelFiles.forEach(file => {
       const workbook = XLSX.readFile(file);
       const data = XLSX.utils.sheet_to_json(workbook.Sheets[0]);
       detections.push(...data);
       // Extract unique stations/species
     });
     
     // Write optimized JSON files
     fs.writeFileSync('public/data/detections.json', JSON.stringify(detections));
     fs.writeFileSync('public/data/stations.json', JSON.stringify(Array.from(stations)));
     fs.writeFileSync('public/data/species.json', JSON.stringify(Array.from(species)));
   };
   ```

2. **Client-side Data Management**:
   ```typescript
   // lib/data/loader.ts
   export const loadData = async () => {
     const [detections, stations, species] = await Promise.all([
       fetch('/data/detections.json').then(r => r.json()),
       fetch('/data/stations.json').then(r => r.json()),
       fetch('/data/species.json').then(r => r.json())
     ]);
     
     return { detections, stations, species };
   };
   ```

3. **Data Processing Functions**:
   ```typescript
   // lib/data/processor.ts
   export const filterDetections = (data: Detection[], filters: FilterState) => {
     return data.filter(detection => {
       if (filters.dateRange && !isWithinRange(detection.date, filters.dateRange)) return false;
       if (filters.stations.length && !filters.stations.includes(detection.station)) return false;
       if (filters.species.length && !hasSpecies(detection, filters.species)) return false;
       return true;
     });
   };
   
   export const aggregateByMonth = (data: Detection[]) => {
     return data.reduce((acc, detection) => {
       const month = format(detection.date, 'yyyy-MM');
       acc[month] = (acc[month] || 0) + 1;
       return acc;
     }, {});
   };
   ```

4. **Performance Optimizations**:
    - Lazy loading of data on app startup
    - Memoized filter/aggregation functions
    - Virtual scrolling for large tables
    - Debounced filter updates
    - IndexedDB caching for repeat visits

## Deployment Architecture

### Deployment: Vercel Only ✅
- **Cost**: Free for hobby projects, $20/month for Pro (which you may already have!)
- **Benefits**:
    - Zero-config deployment from GitHub
    - Automatic preview deployments for PRs
    - Global CDN with edge functions
    - Excellent analytics and Web Vitals
    - Custom domains easy to set up
    - Built-in optimizations for Next.js

### Simple Deployment Flow:
```bash
# 1. Push to GitHub
git push origin main

# 2. Import to Vercel (one-time setup)
# - Go to vercel.com
# - Import GitHub repository  
# - Auto-detects Next.js configuration
# - Deploys automatically

# 3. Environment variables (if needed)
# Add to Vercel dashboard:
NEXT_PUBLIC_MAPBOX_TOKEN=your_token_here
```

### Build Configuration:
```json
// package.json
{
  "scripts": {
    "build-data": "node scripts/processData.js",
    "build": "npm run build-data && next build",
    "dev": "npm run build-data && next dev"
  }
}
```

### Cost Estimate:
- **Vercel Free**: Perfect for development and small projects
- **Vercel Pro**: $20/month if you need more bandwidth/features
- **Total**: $0-20/month (vs $25-40/month with separate API)

### Benefits of This Approach:
- ✅ Single deployment to manage
- ✅ No backend costs or complexity
- ✅ Faster development iteration
- ✅ Zero latency data access
- ✅ Works offline after initial load
- ✅ Easy to scale when data grows (can migrate to API later)

## Data Export Features

### Client-Side Export Capabilities:

### 1. Plot Export (Built into Charts)
```typescript
// components/charts/ExportableChart.tsx
import { saveAs } from 'file-saver';
import Plotly from 'plotly.js';

export const ExportableChart = ({ data, layout, title }) => {
  const chartRef = useRef();

  const downloadAsImage = async (format: 'png' | 'svg' | 'jpeg') => {
    const imgData = await Plotly.toImage(chartRef.current, {
      format,
      width: 1200,
      height: 800,
      scale: 2
    });
    
    const blob = base64ToBlob(imgData);
    saveAs(blob, `${title}_${Date.now()}.${format}`);
  };
  
  const downloadChartData = () => {
    const csv = convertPlotDataToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    saveAs(blob, `${title}_data_${Date.now()}.csv`);
  };
  
  return (
    <div className="chart-container">
      <Plot data={data} layout={layout} ref={chartRef} />
      <div className="export-toolbar">
        <button onClick={() => downloadAsImage('png')}>📸 PNG</button>
        <button onClick={() => downloadAsImage('svg')}>🎨 SVG</button>
        <button onClick={downloadChartData}>📊 Data (CSV)</button>
      </div>
    </div>
  );
};
```

### 2. Data Export Component
```typescript
// components/export/DataExporter.tsx
import Papa from 'papaparse';
import { saveAs } from 'file-saver';

export const DataExporter = () => {
  const { filteredData } = useDataStore();
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  
  const exportData = () => {
    const timestamp = new Date().toISOString().split('T')[0];
    
    if (format === 'csv') {
      const csv = Papa.unparse(filteredData);
      const blob = new Blob([csv], { type: 'text/csv' });
      saveAs(blob, `mbon_detections_${timestamp}.csv`);
    } else {
      const json = JSON.stringify(filteredData, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      saveAs(blob, `mbon_detections_${timestamp}.json`);
    }
  };
  
  return (
    <Card className="export-card">
      <h3>Export Current Dataset</h3>
      <p>Export {filteredData.length} filtered records</p>
      
      <RadioGroup value={format} onChange={setFormat}>
        <Radio value="csv">CSV (Excel compatible)</Radio>
        <Radio value="json">JSON (programming friendly)</Radio>
      </RadioGroup>
      
      <Button onClick={exportData} className="export-btn">
        Download Data
      </Button>
    </Card>
  );
};
```

### 3. Bulk Export with Multiple Formats
```typescript
// lib/utils/export.ts
export const createBulkExport = async (data: Detection[], filters: FilterState) => {
  const zip = new JSZip();
  const timestamp = new Date().toISOString().split('T')[0];
  
  // Add CSV
  const csv = Papa.unparse(data);
  zip.file(`detections_${timestamp}.csv`, csv);
  
  // Add metadata
  const metadata = {
    exportDate: new Date().toISOString(),
    filters: filters,
    recordCount: data.length,
    columns: Object.keys(data[0] || {})
  };
  zip.file(`metadata_${timestamp}.json`, JSON.stringify(metadata, null, 2));
  
  // Add summary statistics
  const summary = generateSummaryStats(data);
  zip.file(`summary_${timestamp}.json`, JSON.stringify(summary, null, 2));
  
  // Generate and download ZIP
  const blob = await zip.generateAsync({ type: 'blob' });
  saveAs(blob, `mbon_export_${timestamp}.zip`);
};
```

### 4. Export Features:
- ✅ **Chart Images**: PNG, SVG, JPEG downloads
- ✅ **Chart Data**: Extract underlying data as CSV
- ✅ **Filtered Dataset**: Download current filtered view
- ✅ **Multiple Formats**: CSV, JSON, ZIP bundles
- ✅ **Metadata Included**: Filters applied, export date, record counts
- ✅ **No Server Required**: All processing done client-side
- ✅ **Works Offline**: After initial data load

## Interactive Features Implementation

### 1. Zoom/Pan for Time Series
```typescript
const layout = {
  xaxis: {
    rangeslider: { visible: true },
    type: 'date'
  },
  yaxis: {
    fixedrange: false
  },
  dragmode: 'zoom',
  hovermode: 'closest'
};
```

### 2. Cross-Filtering Between Charts
- Click on a species in one chart to filter all other visualizations
- Brush selection on time series updates species counts
- Map selections filter data tables

### 3. Real-Time Filter Updates
- Debounced API calls (300ms delay)
- Optimistic UI updates
- Loading skeletons during data fetch

## Mobile Responsiveness Strategy

### Responsive Design Approach:
```typescript
// Tailwind breakpoints
// sm: 640px, md: 768px, lg: 1024px, xl: 1280px

// Desktop: Full dashboard with side-by-side charts
// Tablet: Stack charts vertically, collapsible filters
// Mobile: Single column, swipeable tabs, bottom sheet filters
```

### Mobile-Specific Features:
- Touch-friendly chart interactions
- Swipe gestures for navigation
- Condensed data tables with horizontal scroll
- Bottom sheet for filters (saves screen space)
- Progressive disclosure for complex features

## API Endpoints Overview

### Core Endpoints:
```
GET  /api/detections
GET  /api/detections/aggregate
GET  /api/species
GET  /api/species/{species_id}/timeline
GET  /api/stations
GET  /api/stations/{station_id}/summary
GET  /api/temporal/patterns
GET  /api/temporal/anomalies
POST /api/export/custom
GET  /api/export/detections
GET  /api/metadata/columns
```

### WebSocket Endpoints (Future):
```
WS   /ws/live-detections
WS   /ws/alerts
```

## Development Timeline

### Week 1-2: Foundation
- Set up repositories
- Basic API with test data
- Next.js scaffolding
- Deploy both to cloud

### Week 3-4: Core Features
- Interactive charts
- Filter system
- Data export
- Mobile layouts

### Week 5-6: Advanced Features
- Statistical analysis
- Map integration
- Performance optimization
- User testing

### Week 7-8: Polish & Launch
- Bug fixes
- Documentation
- Performance tuning
- Production deployment

## Getting Started Commands

### Project Setup:
```bash
# Create Next.js project
npx create-next-app@latest mbon-dashboard \
  --typescript --tailwind --app

cd mbon-dashboard

# Install dependencies
npm install plotly.js react-plotly.js mapbox-gl
npm install zustand date-fns file-saver
npm install papaparse jszip
npm install xlsx  # For data processing script

# Create data processing script
mkdir scripts
# Add your Excel files to a data/raw folder
# Run data processing
npm run build-data

# Run development server
npm run dev
```

### Data Processing Script:
```bash
# scripts/processData.js - Convert your Excel files to JSON
node scripts/processData.js
# This creates public/data/detections.json, stations.json, etc.
```

### Deploy to Vercel:
```bash
# Connect to GitHub first
git init
git add .
git commit -m "Initial dashboard"
git remote add origin https://github.com/yourusername/mbon-dashboard
git push -u origin main

# Then deploy via Vercel dashboard or CLI
npm install -g vercel
vercel
```

## Summary

This simplified architecture provides:
- ✅ Highly interactive visualizations with zoom/pan/filter
- ✅ Data and plot export capabilities (client-side)
- ✅ Mobile-responsive design
- ✅ Zero-latency interactions
- ✅ Single deployment (much simpler)
- ✅ Cost-effective ($0-20/month vs $25-40/month)
- ✅ Future-proof (can migrate to API when data grows)

The client-side approach is perfect for your 5MB dataset and eliminates backend complexity while providing all the interactive features you need. When you add acoustic analysis data later, you can easily migrate to the API approach if needed.