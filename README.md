# MBON Marine Biodiversity Dashboard 2025

** this readme is somewhat provisional for now - it's a catchall for notes and developments. I'll clean it up and use it as a basis for doumentation eventually. 

Exploring acoustic indices as biodiversity predictors through interactive visualizations and data analysis.

## 🏗️ Project Structure

This is a **monorepo** with the following structure:

```
mbon-dash-2025/
├── package.json              # 🎯 ROOT: Orchestration scripts & workspace management
├── dashboard/                # 🌐 Frontend: Next.js React application
│   ├── package.json         # 📦 Dashboard-specific dependencies
│   └── src/                 # React components & pages
├── python/                  # 🐍 Backend: Data processing & analysis
│   ├── pyproject.toml       # Python dependencies
│   └── mbon_analysis/       # Analysis modules
└── data/                    # 📊 Data files (raw & processed)
```

## 🚀 Quick Start

**From the root directory, run:**

```bash
# Install everything
npm run setup

# Start development (both frontend & data processing)
npm run dev

# Process data only
npm run data:process

# Build for production
npm run build
```

## 📦 Package.json Files Explained

### Root `package.json` (🎯 Orchestrator)
- **Purpose**: Workspace management and orchestration
- **Contains**: Scripts to run both frontend and backend
- **Key commands**: `npm run dev`, `npm run data:process`, `npm run build`

### Dashboard `package.json` (🌐 Frontend)
- **Purpose**: Next.js application dependencies
- **Contains**: React, Next.js, and visualization libraries
- **Key commands**: `npm run dev`, `npm run build` (run from dashboard/ directory)

## 🔧 Development Workflow

1. **Always start from the root directory**
2. **Use root scripts for orchestration**: `npm run dev`, `npm run data:process`
3. **Use dashboard scripts for frontend-only tasks**: `cd dashboard && npm run lint`

## Architecture Overview

This project uses a **view-first architecture** that separates data processing from visualization:

```
Raw Data (Excel/CSV) � Python Processing � Optimized Views (<50KB) � Dashboard
     (50+ files)         (Heavy compute)      (JSON files)        (Fast UI)
```

- **Python Layer**: Heavy computation, data processing, view generation
- **Web Layer**: Visualization, interaction, presentation only  
- **CDN Layer**: Static file serving, global distribution

## Quick Start

### Prerequisites

- Python 3.12+ with `uv` package manager
- Node.js 18+ with `npm`
- Mapbox token (for maps) - set as `NEXT_PUBLIC_MAPBOX_TOKEN`
- Cloudflare R2 credentials for CDN (optional for local development)

### Environment Configuration

**Important:** The `.env.local` file must be placed at the **project root** (not inside the dashboard/ directory). This allows both Python scripts and the Next.js application to access the same environment variables.

```bash
# Create .env.local at project root
touch .env.local
```

Add the following environment variables:

```bash
# Cloudflare R2 Configuration (used by Python scripts for CDN uploads)
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

The Next.js configuration (`dashboard/next.config.ts`) is set up to automatically load environment variables from the root-level `.env.local` file using:
```javascript
dotenv.config({ path: path.resolve(__dirname, '../.env.local') });
```

### Setup

```bash
# Clone and enter project
git clone <repository>
cd mbon-dash-2025

# Set up Python environment (using UV)
cd python/
uv sync --dev                         # Install dependencies with dev tools
uv run pre-commit install             # Install pre-commit hooks

# Set up Dashboard
cd ../dashboard/
npm install                           # Install dependencies
```

### Development

```bash
# Generate initial views (run once or when data changes)
cd python/
uv run mbon-generate-views           # Generate all views
# OR use the Makefile:
make views

# Start dashboard development server
cd ../dashboard/
npm run dev                          # http://localhost:3000
```

## Available Views and Visualizations

The dashboard currently includes the following data views and interactive visualizations:

### Acoustic Indices Distributions

**Location**: `/explore` page  
**View File**: `acoustic_indices_distributions.json` (~600KB)  
**Component**: `AcousticIndicesSmallMultiples`

Interactive small multiples visualization showing probability density distributions (KDE) of 60+ acoustic indices across three monitoring stations (9M, 14M, 37M).

**Features**:
- Small multiples grid layout with individual KDE plots for each acoustic index
- Station filtering with color-coded distributions (9M: Blue, 14M: Red, 37M: Green)
- Bandwidth filtering (FullBW vs 8kHz)
- Category filtering by acoustic index type
- Search functionality to find specific indices
- Real-time record counts for each station

**Data Source**: 
- Acoustic indices CSV files from 2021 dataset
- Computed using Kernel Density Estimation with 50 evaluation points
- Covers all available stations and bandwidth combinations

**Usage**: Navigate to the Explorer page to interact with acoustic indices distributions. Use the filter controls to focus on specific stations, bandwidths, or index categories.

### Other Available Views

- **Station Map**: Interactive map showing hydrophone deployment locations
- **Dataset Summary**: Overview cards with record counts and temporal coverage
- **Indices Reference**: Filterable table of all acoustic indices with descriptions
- **Project Metadata**: Research context, methodology, and citations

## Two-Tier Data Architecture

This project uses a **two-tier data architecture** optimized for different use cases:

### Tier 1: Small View Files (< 50KB) - Direct CDN Access
For small datasets that can be pre-processed and served directly:

```json
views/
├── stations.json                      # Station metadata (8KB)
├── datasets_summary.json              # Dataset overview (12KB)  
├── indices_reference.json             # Acoustic indices reference (25KB)
├── heatmap.json                       # Species detection heatmap (42KB)
└── acoustic_indices_distributions.json # Index distributions (35KB)
```

**Usage Pattern:**
```typescript
const { data, loading, error } = useViewData<StationData>('stations.json');
```

### Tier 2: Large Datasets (> 50MB) - Progressive Loading
For large datasets requiring server-side filtering:

```json
processed/
└── compiled_indices.json              # Full acoustic indices (279MB)
```

**Usage Pattern:**
```typescript
const { data, loading, error, metadata } = useIndicesHeatmap({
  index: 'ACI',
  station: '14M',
  year: 2021,
  bandwidth: 'FullBW'
});
```

**How Progressive Loading Works:**
1. API route (`/api/indices-heatmap`) fetches large file from CDN once and caches in memory
2. Server-side filtering returns only requested subset (e.g., 8,735 records from 50,000+)
3. Multiple cache layers prevent redundant processing
4. Performance: ~16 second initial load, then sub-second responses

### Decision Matrix: Which Approach to Use?

| Data Size | Processing Needs | User Interaction | Recommended Approach |
|-----------|------------------|------------------|----------------------|
| < 50KB | Pre-processed | Static display | **Tier 1**: Small view file |
| < 50KB | Pre-processed | Simple filtering | **Tier 1**: Small view file |
| > 50MB | Dynamic filtering | Complex user selections | **Tier 2**: Progressive loading |
| > 50MB | Real-time analysis | Parameter-based queries | **Tier 2**: Progressive loading |

## Creating New Views and Visualizations

### Tier 1: Small View Files (< 50KB)

#### 1. Create a New View (Python)

Views are small, optimized JSON files (<50KB) that contain pre-processed data for the dashboard.

#### Step 1: Create View Generator

Create a new file in `python/mbon_analysis/views/`:

```python
# python/mbon_analysis/views/my_new_view.py
"""My new view generator."""

from typing import Dict, Any
import pandas as pd
from .base import BaseViewGenerator
from ..data.loaders import create_loader

class MyNewViewGenerator(BaseViewGenerator):
    """Generate my_new_view.json with specific analysis data."""
    
    def generate_view(self) -> Dict[str, Any]:
        """Generate view data for my analysis.
        
        Returns:
            Dictionary with analysis data optimized for dashboard
        """
        loader = create_loader(self.data_root)
        
        # Load your required data
        # detections_df = loader.load_detection_data()
        # indices_df = loader.load_acoustic_indices()
        # env_df = loader.load_environmental_data()
        
        # Process and analyze your data here
        # analysis_results = self._perform_analysis(detections_df, indices_df)
        
        return {
            "metadata": {
                "generated_at": pd.Timestamp.now().isoformat(),
                "version": "1.0.0",
                "description": "Description of this view"
            },
            "summary": {
                # High-level summary stats
            },
            "data": {
                # Your processed data for charts
            }
        }
    
    def _perform_analysis(self, data1, data2):
        """Helper method for analysis logic."""
        # Your analysis code here
        pass
```

#### Step 2: Create Generation Script

Create a script to generate your view:

```python
# python/scripts/generate_my_view.py
#!/usr/bin/env python3
"""Generate my_new_view.json for dashboard."""

from pathlib import Path
from mbon_analysis.views.my_new_view import MyNewViewGenerator

def main():
    """Generate the view."""
    # Path to data directory
    data_root = Path(__file__).parent.parent / "data"
    
    # Generate view
    generator = MyNewViewGenerator(data_root)
    result = generator.create_view("my_new_view.json")
    
    print(f" Generated {result['filename']}")
    print(f"   Size: {result['size_kb']} KB")
    print(f"   Path: {result['path']}")

if __name__ == "__main__":
    main()
```

#### Step 3: Run the Generator

```bash
cd python/
uv run scripts/generate_my_view.py
```

This creates `python/data/views/my_new_view.json`.

### 2. Create Data Types (TypeScript)

Add TypeScript interfaces in `dashboard/src/types/data.ts`:

```typescript
// Add to existing data.ts file
export interface MyViewData {
  metadata: {
    generated_at: string;
    version: string;
    description: string;
  };
  summary: {
    total_items: number;
    // other summary fields
  };
  data: {
    // your chart data structure
  };
}
```

### 3. Create Data Hook

Create a data loading hook in `dashboard/src/lib/data/`:

```typescript
// dashboard/src/lib/data/useMyView.ts
import { useViewData } from './useViewData';
import { MyViewData } from '@/types/data';

export function useMyView() {
  const { data, loading, error } = useViewData<MyViewData>('my_new_view.json');
  
  return {
    myViewData: data,
    loading,
    error
  };
}
```

### 4. Create Visualization Component

Create a chart component in `dashboard/src/components/charts/`:

```tsx
// dashboard/src/components/charts/MyChart.tsx
'use client';

import { ResponsiveBar } from '@nivo/bar'; // or other Nivo chart
import { MyViewData } from '@/types/data';

interface MyChartProps {
  data: MyViewData['data'];
  height?: number;
  className?: string;
}

export default function MyChart({ data, height = 400, className = '' }: MyChartProps) {
  // Transform data for Nivo format
  const chartData = Object.entries(data).map(([key, value]) => ({
    id: key,
    value: value,
    // other chart properties
  }));

  return (
    <div className={`${className}`} style={{ height }}>
      <ResponsiveBar
        data={chartData}
        keys={['value']}
        indexBy="id"
        margin={{ top: 50, right: 130, bottom: 50, left: 60 }}
        padding={0.3}
        valueScale={{ type: 'linear' }}
        colors={{ scheme: 'nivo' }}
        borderColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'X Axis Label',
          legendPosition: 'middle',
          legendOffset: 32
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Y Axis Label',
          legendPosition: 'middle',
          legendOffset: -40
        }}
        labelSkipWidth={12}
        labelSkipHeight={12}
        labelTextColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
        animate={true}
        motionStiffness={90}
        motionDamping={15}
      />
    </div>
  );
}
```

### 5. Create Page or Add to Existing Page

Option A: Create new page in `dashboard/src/app/my-page/page.tsx`:

```tsx
'use client';

import { useMyView } from '@/lib/data/useMyView';
import MyChart from '@/components/charts/MyChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function MyPage() {
  const { myViewData, loading, error } = useMyView();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading data: {error.message}</p>
      </div>
    );
  }

  if (!myViewData) return null;

  return (
    <div className="container mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">My Analysis</h1>
        <p className="text-muted-foreground mt-2">Description of the analysis</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>My Chart</CardTitle>
        </CardHeader>
        <CardContent>
          <MyChart data={myViewData.data} />
        </CardContent>
      </Card>
    </div>
  );
}
```

Option B: Add to existing page like `explore/page.tsx`.

### Tier 2: Progressive Loading (> 50MB)

For large datasets that require server-side filtering and progressive loading:

#### 1. Create Large Dataset (Python)
First, create a script to compile your large dataset:

```python
# python/scripts/generate_large_dataset.py
import json
from pathlib import Path

def create_large_dataset():
    """Create a large compiled dataset for progressive loading."""
    
    # Load and combine your data sources
    # compiled_data = process_large_datasets()
    
    compiled_data = {
        "metadata": {
            "generated_at": "2025-01-01T00:00:00",
            "total_records": 50000,
            "stations": ["14M", "37M", "9M"],
            "years": [2018, 2021]
        },
        "stations": {
            "14M": {
                "2021": {
                    "data": [
                        # Large array of records
                    ]
                }
            }
        }
    }
    
    # Save to processed directory
    output_path = Path("data/processed/my_large_dataset.json")
    with open(output_path, 'w') as f:
        json.dump(compiled_data, f)
    
    print(f"Created {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")

if __name__ == "__main__":
    create_large_dataset()
```

#### 2. Create API Route
Create an API endpoint for server-side filtering:

```typescript
// dashboard/src/app/api/my-large-data/route.ts
import { NextRequest, NextResponse } from 'next/server';

interface CompiledData {
  metadata?: {
    total_records?: number;
    stations?: string[];
    years?: number[];
  };
  stations?: {
    [station: string]: {
      [year: string]: {
        data: RawDataPoint[];
      };
    };
  };
}

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';
let compiledData: CompiledData | null = null;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function loadCompiledData() {
  if (compiledData) return compiledData;
  
  try {
    const dataUrl = `${CDN_BASE_URL}/processed/my_large_dataset.json`;
    const response = await fetch(dataUrl);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    compiledData = await response.json();
    return compiledData;
  } catch (error) {
    console.error('Error loading compiled data from CDN:', error);
    throw new Error('Failed to load compiled data from CDN');
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const station = searchParams.get('station');
  const year = searchParams.get('year');
  
  if (!station || !year) {
    return NextResponse.json(
      { error: 'Missing required parameters: station, year' },
      { status: 400 }
    );
  }
  
  try {
    const compiledDataset = await loadCompiledData();
    
    // Handle nested data structure
    const stationData = compiledDataset?.stations?.[station];
    if (!stationData) {
      return NextResponse.json(
        { error: `Station '${station}' not found` },
        { status: 404 }
      );
    }
    
    const yearData = stationData[year];
    if (!yearData) {
      return NextResponse.json(
        { error: `Year '${year}' not found` },
        { status: 404 }
      );
    }
    
    const rawData = yearData.data || [];
    
    return NextResponse.json({
      metadata: {
        stations: Object.keys(compiledDataset?.stations || {}),
        years: compiledDataset?.metadata?.years || [],
        filtered_records: rawData.length,
      },
      data: rawData
    });
    
  } catch (error) {
    console.error('Error in API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

#### 3. Create Progressive Loading Hook
Create a data hook that handles metadata fetching and progressive loading:

```typescript
// dashboard/src/lib/data/useMyLargeData.ts
import { useState, useEffect, useCallback } from 'react';

interface MyLargeDataParams {
  station?: string;
  year?: number;
}

export function useMyLargeData(params: MyLargeDataParams) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metadata, setMetadata] = useState(null);
  
  // Fetch metadata first (using default params to get available options)
  useEffect(() => {
    if (!params.station || !params.year) {
      // Fetch metadata to get available stations/years
      fetchMetadata();
      return;
    }
    
    // Fetch actual data
    fetchData();
  }, [params]);
  
  const fetchMetadata = useCallback(async () => {
    try {
      setLoading(true);
      // Use default params to get metadata
      const response = await fetch(`/api/my-large-data?station=14M&year=2021`);
      const result = await response.json();
      setMetadata(result.metadata);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, []);
  
  const fetchData = useCallback(async () => {
    if (!params.station || !params.year) return;
    
    try {
      setLoading(true);
      const response = await fetch(
        `/api/my-large-data?station=${params.station}&year=${params.year}`
      );
      const result = await response.json();
      setData(result);
      setMetadata(result.metadata);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [params]);
  
  return { data, loading, error, metadata };
}
```

#### 4. Upload to CDN
Upload your large dataset to CDN:

```bash
cd python/
uv run scripts/generate_large_dataset.py    # Create the large file
uv run scripts/upload_to_cdn.py            # Upload to CDN (includes processed/ files)
```

#### 5. Use in Component
Use the progressive loading hook in your component:

```tsx
function MyLargeDataChart() {
  const [selectedStation, setSelectedStation] = useState('');
  const [selectedYear, setSelectedYear] = useState(0);
  
  const { data, loading, error, metadata } = useMyLargeData({
    station: selectedStation,
    year: selectedYear
  });
  
  // Set defaults when metadata loads
  useEffect(() => {
    if (!metadata) return;
    
    if (metadata.stations.length > 0 && !selectedStation) {
      setSelectedStation(metadata.stations[0]);
    }
    if (metadata.years.length > 0 && !selectedYear) {
      setSelectedYear(metadata.years[0]);
    }
  }, [metadata]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!data) return null;
  
  return (
    <div>
      {/* Controls */}
      <select value={selectedStation} onChange={(e) => setSelectedStation(e.target.value)}>
        {metadata?.stations?.map(station => (
          <option key={station} value={station}>{station}</option>
        ))}
      </select>
      
      {/* Chart */}
      <MyChart data={data.data} />
    </div>
  );
}
```

### 6. Add Navigation (Optional)

Update navigation in `dashboard/src/components/layout/Navigation.tsx`:

```tsx
// Add to navigation items array
{
  name: 'My Analysis',
  href: '/my-page',
  description: 'Custom analysis page'
}
```

## Available Chart Types

The project uses **Nivo.rocks** for charts. Available components:

```typescript
import { ResponsiveBar } from '@nivo/bar';          // Bar charts
import { ResponsiveLine } from '@nivo/line';        // Line charts  
import { ResponsiveScatterPlot } from '@nivo/scatterplot'; // Scatter plots
import { ResponsiveHeatMap } from '@nivo/heatmap';   // Heat maps
// See @nivo/* packages in package.json for full list
```

## File Structure Reference

```
mbon-dash-2025/
   python/                              # Data processing
      mbon_analysis/views/             # � Add view generators here
      scripts/                         # � Add generation scripts here  
      data/views/                      # � Generated JSON files
   dashboard/
      src/
          components/charts/           # � Add chart components here
          lib/data/                    # � Add data hooks here
          types/data.ts                # � Add data types here
          app/                         # � Add pages here
```

## Development Commands

### Python (Data Processing)
```bash
cd python/

# Quick setup
make dev-setup                        # Install deps + pre-commit hooks
make help                            # Show all available commands

# Install/update dependencies
uv sync --dev                        # Install with dev dependencies
make update                          # Update all dependencies

# Generate views and process data
make views                           # Generate all view files
make indices                         # Generate compiled indices
make migrate                         # Migrate data to top-level
make test-data                       # Test data access

# Development workflow
make dev-cycle                       # Format + lint + test
make ci                              # Full CI checks

# Code quality
make lint                            # Run all linting checks
make format                          # Format code
make typecheck                       # Type checking
make test-cov                        # Tests with coverage

# Individual commands
uv run mbon-generate-views           # Generate views via CLI
uv run scripts/generate_compiled_indices.py
uv run pytest                        # Run tests
uv run ruff check .                  # Lint with ruff
uv run black .                       # Format with black
```

### Dashboard (Frontend)
```bash
cd dashboard/

# Development server
npm run dev

# Build for production  
npm run build

# Type checking
npm run typecheck

# Lint code
npm run lint
```

## Data Loading Patterns

### View Data Hook Pattern
All data loading uses the same pattern:

```typescript
const { data, loading, error } = useViewData<DataType>('filename.json');
```

### Error Handling Template
```tsx
if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return null;
```

### Chart Wrapper Pattern
```tsx
<Card>
  <CardHeader>
    <CardTitle>Chart Title</CardTitle>
  </CardHeader>
  <CardContent>
    <MyChart data={data.chartData} height={400} />
  </CardContent>
</Card>
```

## Performance Guidelines

### View Files
- Keep views under 50KB each
- Pre-aggregate data in Python, not in React
- Use efficient data structures (arrays for charts, not nested objects)

### Components
- Use `'use client'` for interactive components
- Implement proper loading states
- Add error boundaries
- Optimize re-renders with useMemo/useCallback if needed

## Testing

### Python Testing
```bash
cd python/
uv run pytest tests/test_views.py          # Test view generation
uv run pytest tests/test_loaders.py        # Test data loading
```

### Frontend Testing
```bash
cd dashboard/
npm run test                               # Run tests (when configured)
npm run typecheck                          # Type checking
```

## CDN Upload and Management

### Automatic CDN Upload
The CDN upload script handles both small and large files automatically:

```bash
cd python/
uv run scripts/upload_to_cdn.py
```

**What gets uploaded:**
- **Small view files** (< 50KB): From `data/views/` → CDN `views/` folder  
- **Large processed files** (> 50MB): From `data/processed/` → CDN `processed/` folder

**Example output:**
```
✅ Uploaded: views/stations.json
✅ Uploaded: views/datasets_summary.json  
✅ Uploaded: processed/compiled_indices.json (279MB, 19 seconds)
📊 Upload Summary: ✅ 11 files uploaded successfully
```

### CORS Configuration
If you add new domains or encounter CORS issues:

```bash
cd python/
uv run scripts/configure_r2_cors.py
```

This updates the CORS policy to allow requests from:
- Local development: `http://localhost:3000-3004`
- Vercel deployments: `https://mbon-dash-2025.vercel.app`, `https://mbon-dash-2025-*.vercel.app`

## Deployment

### Development Workflow
```bash
# 1. Generate/update data views
cd python/
uv run scripts/generate_all_views.py

# 2. Upload to CDN (optional for local dev)
uv run scripts/upload_to_cdn.py

# 3. Start dashboard
cd dashboard/
npm run dev                          # http://localhost:3000
```

### Production Deployment
```bash
# 1. Generate and upload data
cd python/
uv run scripts/generate_all_views.py    # Generate all views
uv run scripts/upload_to_cdn.py         # Upload to CDN

# 2. Build and deploy dashboard  
cd dashboard/
npm run build                           # Test build locally
git add . && git commit -m "feat: update data"
git push                               # Automatic Vercel deployment
```

### Environment Variables for Vercel
When deploying to Vercel, add these environment variables to the Vercel project settings:

**Required Variables:**
```bash
NEXT_PUBLIC_CDN_BASE_URL=https://waveformdata.work
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token
```

**Optional (for Python script access in Vercel Functions, if needed):**
```bash
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=mbon-usc-2025
CLOUDFLARE_R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
```

**How to add in Vercel:**
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables  
3. Add each environment variable
4. Redeploy the project

## Common Issues

### "View not found" errors
- Make sure view JSON file exists in `python/data/views/`
- Check filename matches exactly in hook
- Regenerate views with generation script

### Chart not rendering
- Check data structure matches Nivo requirements
- Verify data types in TypeScript interfaces
- Use browser dev tools to inspect data

### Build errors
- Run `npm run typecheck` to find type issues
- Ensure all imports are correct
- Check for missing dependencies

## Getting Help

- Check existing view generators in `python/mbon_analysis/views/`
- Look at existing chart components in `dashboard/src/components/charts/`
- Review CLAUDE.md for architectural details
- Use browser dev tools to debug data flow

## Next Steps

1. Create your view generator class
2. Generate the JSON view file  
3. Create TypeScript types
4. Build the chart component
5. Create or update the page
6. Test and iterate

The architecture is designed to be modular - each view and chart is independent, making it easy to add new analyses incrementally.