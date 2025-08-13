# Data Explorer Page Planning

## Purpose & Goals

The Data Explorer page serves as the **data discovery and understanding hub** for researchers and collaborators. It should provide:

1. **Visual Overview** - What data exists, when, and where
2. **Interactive Exploration** - Filter, zoom, subset the data
3. **Download Capability** - Export filtered datasets for further analysis
4. **Foundation Understanding** - Prepare users for deeper dives in specialized pages

## User Stories

**As a researcher, I want to:**
- See what species were detected at which stations and when
- Understand the temporal coverage and gaps in the data
- Download specific subsets (e.g., "all 2018 data for station 9M")
- Get a sense of seasonal patterns and station differences
- Know what environmental conditions coincided with detections

**As a collaborator, I want to:**
- Quickly understand the scope of available data
- See basic statistics (record counts, date ranges, etc.)
- Identify interesting patterns worth investigating
- Export data for my own analysis tools

## Data Currently Available

### 1. Species Detections (26,280 records)
- 28 species across 3 stations
- 2-hour detection windows
- 2018 and 2021 data

### 2. Environmental Data (237,334 records)
- Temperature and depth measurements
- Higher temporal resolution than detections
- Same stations and years

### 3. Deployment Metadata (25 records)
- Station information
- Deployment periods
- Equipment details

### 4. Future: Acoustic Indices (planned)
- 56 indices when available
- Hourly measurements
- Will need temporal alignment

## Page Layout Concept

```
┌─────────────────────────────────────────────────────────┐
│ Data Explorer                                          │
│ Explore and download marine biodiversity datasets      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Dataset Overview                                 │   │
│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐           │   │
│ │ │Species  │ │Environ. │ │Acoustic │           │   │
│ │ │26,280   │ │237,334  │ │Coming   │           │   │
│ │ │records  │ │records  │ │Soon     │           │   │
│ │ └─────────┘ └─────────┘ └─────────┘           │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Filters                                          │   │
│ │ Station: [9M] [14M] [37M]                       │   │
│ │ Year: [2018] [2021]                             │   │
│ │ Species: [Select multiple...]                    │   │
│ │ Date Range: [___] to [___]                      │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Data Visualizations (Tabbed)                     │   │
│ │ [Timeline] [Station Comparison] [Species Matrix] │   │
│ │                                                   │   │
│ │ [Interactive chart based on selected tab]        │   │
│ │                                                   │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Data Table Preview                               │   │
│ │ Showing 1-10 of X filtered records               │   │
│ │ [Paginated table with current filters applied]   │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ [Download Filtered Data ↓]                             │
└─────────────────────────────────────────────────────────┘
```

## Visualization Components

### 1. Timeline View
- **Purpose**: Show temporal patterns and data availability
- **Chart Type**: Area chart or timeline with multiple series
- **Features**:
  - X-axis: Time (monthly aggregation)
  - Y-axis: Detection counts or records
  - Series: Different species or stations
  - Gaps clearly visible
  - Zoom/pan capability

### 2. Station Comparison
- **Purpose**: Compare activity across stations
- **Chart Type**: Grouped bar chart or small multiples
- **Features**:
  - Compare species composition
  - Environmental conditions
  - Total activity levels
  - Side-by-side or overlaid

### 3. Species Matrix
- **Purpose**: Show species co-occurrence and patterns
- **Chart Type**: Heatmap or correlation matrix
- **Features**:
  - Species x Time matrix
  - Species x Station matrix
  - Color intensity = detection frequency
  - Interactive tooltips

### 4. Environmental Context
- **Purpose**: Show environmental conditions
- **Chart Type**: Line charts with dual axes
- **Features**:
  - Temperature and depth over time
  - Overlay with detection events
  - Statistical summaries

## Filter System Design

### Implementation Strategy
1. **Global State**: Use Zustand store for filter state
2. **URL Sync**: Filters reflected in URL for shareable views
3. **Performance**: Debounced filtering (300ms)
4. **Clear Feedback**: Show record count with current filters

### Filter Options
```typescript
interface DataFilters {
  stations: string[];      // Multi-select
  years: number[];         // Multi-select
  species: string[];       // Multi-select with search
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  dataTypes: {
    detections: boolean;
    environmental: boolean;
    acoustic: boolean;    // Future
  };
}
```

## Download Functionality

### Export Options
1. **Filtered Dataset**
   - Current filters applied
   - CSV or JSON format
   - Include metadata

2. **Summary Statistics**
   - Aggregated by station/species/time
   - CSV format
   - Ready for Excel analysis

3. **Raw Data Subsets**
   - Original format preservation
   - Station or year-specific
   - Bulk download option

### Implementation
```typescript
// Download configuration
interface DownloadOptions {
  format: 'csv' | 'json';
  includeMetadata: boolean;
  aggregationLevel: 'raw' | 'hourly' | 'daily' | 'monthly';
  datasets: ('detections' | 'environmental' | 'acoustic')[];
}
```

## Python Preprocessing Requirements

### 1. Create Aggregated Views
```python
# scripts/exploratory/prepare_explorer_data.py

# Daily summaries for timeline
daily_detections = detections.groupby(['date', 'station']).sum()

# Species occurrence matrix
species_matrix = detections.pivot_table(
    index='date', 
    columns='species', 
    values='count',
    aggfunc='sum'
)

# Station summaries
station_stats = {
    'total_detections': by_station.sum(),
    'active_days': by_station.count(),
    'top_species': by_station.nlargest(5)
}

# Save preprocessed views
save_to_json('data/cdn/processed/explorer_views.json')
```

### 2. Create Download Packages
```python
# Prepare downloadable subsets
def create_download_package(filters):
    filtered_data = apply_filters(data, filters)
    
    # Create CSV with metadata header
    metadata = f"# MBON Data Export\n# Filters: {filters}\n# Date: {today}\n"
    
    return metadata + filtered_data.to_csv()
```

### 3. Calculate Statistics
```python
# Generate summary statistics for display
stats = {
    'temporal_coverage': get_date_ranges(),
    'species_rankings': get_top_species(),
    'station_activity': get_station_summaries(),
    'data_quality': get_completeness_metrics()
}
```

## Component Architecture

```
explorer/
├── page.tsx                    # Main page component
├── page.content.tsx           # Text content
├── components/
│   ├── DatasetOverview.tsx   # Cards showing record counts
│   ├── FilterPanel.tsx        # Reusable filter component
│   ├── ExplorerCharts.tsx    # Tabbed visualization container
│   │   ├── TimelineChart.tsx
│   │   ├── StationComparison.tsx
│   │   └── SpeciesMatrix.tsx
│   ├── DataTable.tsx          # Paginated preview table
│   └── DownloadModal.tsx      # Download options dialog
└── hooks/
    ├── useFilteredData.ts     # Filter logic
    └── useExportData.ts       # Download functionality
```

## Observable Plot Charts

### Timeline Implementation
```javascript
Plot.plot({
  marks: [
    Plot.areaY(data, {
      x: "date",
      y: "detections",
      fill: "station",
      curve: "step"
    }),
    Plot.ruleY([0])
  ],
  x: { type: "time" },
  y: { label: "Detection Count" },
  color: { legend: true }
})
```

### Species Matrix
```javascript
Plot.plot({
  marks: [
    Plot.cell(data, {
      x: "date",
      y: "species",
      fill: "count",
      tip: true
    })
  ],
  color: {
    scheme: "YlOrRd",
    label: "Detections"
  }
})
```

## Development Phases

### Phase 1: Foundation (Current Focus)
1. Create Python script for data preprocessing
2. Generate aggregated views and statistics
3. Upload to CDN as `explorer_views.json`

### Phase 2: Basic Display
1. Dataset overview cards
2. Simple timeline chart
3. Basic filter panel (stations, years)
4. Data table with pagination

### Phase 3: Enhanced Interactivity
1. Additional chart types (station, species matrix)
2. Advanced filters (species, date range)
3. Download functionality
4. URL state management

### Phase 4: Polish
1. Loading states and error handling
2. Responsive design optimization
3. Export format options
4. Performance optimization

## Success Metrics

**Functionality**:
- ✓ Users can see all available data at a glance
- ✓ Filtering reduces dataset as expected
- ✓ Downloads include only filtered data
- ✓ Charts update smoothly with filter changes

**Understanding**:
- ✓ Users understand temporal coverage
- ✓ Station differences are clear
- ✓ Data gaps are visible
- ✓ Basic patterns emerge

**Performance**:
- ✓ Page loads in <2 seconds
- ✓ Filter updates in <300ms
- ✓ Downloads start immediately
- ✓ Charts render smoothly

## Notes & Considerations

1. **Data Size**: Environmental data is large (237K records) - need aggregation
2. **Missing Data**: Clearly show gaps, don't interpolate in explorer
3. **Mobile View**: Prioritize timeline and overview cards
4. **Accessibility**: Ensure keyboard navigation and screen reader support
5. **Future Acoustic**: Design with space for acoustic indices integration

## Next Steps

1. **Create preprocessing script** in `scripts/exploratory/`
2. **Generate aggregated views** for efficient loading
3. **Design filter state management** in Zustand
4. **Implement basic timeline** with Observable Plot
5. **Add download functionality** with format options

---

*This planning document is temporary and will be replaced by proper documentation once implementation is complete.*