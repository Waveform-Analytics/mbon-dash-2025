# MBON Marine Biodiversity Dashboard

Interactive web dashboard exploring whether acoustic indices can predict marine soundscape biodiversity and serve as proxies for complex biodiversity monitoring.

**Core Question**: "Can computed acoustic indices help us understand or even predict marine biodiversity patterns as an alternative to labor-intensive manual species detection methods?"

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

### Setup

```bash
# Clone and enter project
git clone <repository>
cd mbon-dash-2025

# Set up Python environment
cd python/
uv sync                                # Install dependencies
uv pip install -e .                   # Install mbon_analysis package

# Set up Dashboard
cd ../dashboard/
npm install                           # Install dependencies
```

### Development

```bash
# Generate initial views (run once or when data changes)
cd python/
uv run scripts/generate_all_views.py

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

## Creating New Views and Plots

This section explains how to add new data views and visualizations to the dashboard.

### 1. Create a New View (Python)

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
    
    print(f" Generated {result['filename']}")
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

# Install/update dependencies
uv sync

# Generate all views
uv run scripts/generate_all_views.py

# Generate specific view
uv run scripts/generate_my_view.py

# Run tests
uv run pytest

# Lint code
uv run ruff check
uv run ruff format
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

## Deployment

### Development
```bash
# Generate views
cd python/ && uv run scripts/generate_all_views.py

# Start dashboard
cd dashboard/ && npm run dev
```

### Production
```bash
# Build dashboard
cd dashboard/ && npm run build

# Deploy to Vercel
vercel deploy --prod
```

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