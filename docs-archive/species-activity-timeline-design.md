# Species Activity Timeline Design Options

## Overview

The Species Activity Timeline on the main dashboard should provide a compelling, high-level overview that immediately communicates the scope and nature of the marine biodiversity monitoring project. It should be informative for visitors who want to understand what they're exploring.

## Design Option 1: **Multi-Station Detection Activity Heatmap** (RECOMMENDED)

### Concept
A timeline heatmap showing species detection activity across all 3 stations over the 2018-2021 period.

### Visual Design
- **X-axis**: Time (months/quarters from 2018-2021)
- **Y-axis**: Species (top 8-12 most detected species)  
- **Station separation**: 3 horizontal sections or color coding
- **Activity intensity**: Color/opacity showing detection frequency
- **Deployment periods**: Subtle background indicators showing when stations were active

### Why This Works
- **Immediate insight**: Shows temporal patterns and species diversity at a glance
- **Station comparison**: Reveals differences between 9M, 14M, 37M locations
- **Data gaps visible**: Shows deployment periods and data coverage
- **Scales well**: Will accommodate future acoustic indices as additional layers
- **Interactive potential**: Hover shows specific detection counts, click to filter

### Implementation
```javascript
// Data structure for timeline
const timelineData = [
  {
    month: '2018-01',
    station: '9M', 
    species: 'Silver perch',
    detections: 45,
    deploymentActive: true
  },
  // ... more records
]

// Visual encoding
- Color intensity = detection frequency
- Gaps = no deployment data
- Hover = specific metrics
```

---

## Design Option 2: **Deployment Activity Overview**

### Concept
Timeline showing when each station was actively collecting data, with overlay of total daily/weekly detections.

### Visual Design
- **X-axis**: Time (2018-2021)
- **Y-axis**: 3 stations (9M, 14M, 37M)
- **Deployment bars**: Solid bars showing active recording periods
- **Detection overlay**: Line graph or dots showing detection intensity
- **Environmental context**: Subtle background showing seasonal temperature patterns

### Why This Works
- **Clear data context**: Immediately shows what data is available when
- **Deployment story**: Explains gaps and coverage
- **Detection activity**: Shows overall biological activity patterns
- **Future-ready**: Easy to add acoustic indices as additional overlays

---

## Design Option 3: **Species Discovery Timeline**

### Concept
Cumulative timeline showing when different species were first detected and how detection patterns evolved.

### Visual Design
- **X-axis**: Time (2018-2021)
- **Y-axis**: Cumulative species count or individual species lanes
- **New species**: Highlighted moments when species first appear
- **Activity streams**: River-style flow showing detection intensity per species
- **Station indicators**: Color coding or symbols for which station detected what

### Why This Works
- **Discovery narrative**: Tells a story of marine biodiversity exploration
- **Species focus**: Highlights the primary research interest
- **Temporal evolution**: Shows how understanding grew over time
- **Engaging**: More story-driven than pure data visualization

---

## Design Option 4: **Environmental Context Timeline** (Future-Ready)

### Concept
Multi-layer timeline showing deployments, environmental conditions, and species activity in context.

### Visual Design
- **Top layer**: Deployment periods and data availability
- **Middle layer**: Temperature/depth trends (environmental context)
- **Bottom layer**: Species detection activity (current) + acoustic indices (future)
- **Seasonal markers**: Background indicators for seasonal patterns
- **Event highlights**: Notable periods or phenomena

### Why This Works
- **Holistic view**: Shows biological activity in environmental context
- **Research-focused**: Emphasizes the correlation questions you want to explore
- **Expandable**: Perfect for adding 60 acoustic indices later
- **Scientific storytelling**: Shows the complete monitoring picture

---

## Implementation Recommendations

### Phase 1: Start with Option 1 (Detection Heatmap) ✅ COMPLETED
**Implementation**: Observable Plot heatmap
- Most immediately informative for visitors
- Showcases the primary dataset (manual detections)
- Lightweight and fast rendering
- Clean, scientific visualization aesthetic

### Phase 2: Add Environmental Context
- Overlay temperature/depth trends on the timeline
- Show seasonal patterns that might correlate with species activity
- Prepare framework for acoustic indices integration

### Phase 3: Acoustic Indices Integration
When the 60 acoustic indices become available:
- **New layer**: Add acoustic patterns below species detections
- **Correlation highlighting**: Visual indicators where acoustic and species patterns align
- **Index selection**: Allow users to toggle between different acoustic indices
- **5-minute resolution**: Show high-temporal-resolution acoustic data with daily/weekly species aggregations

## Technical Implementation Approach

### Data Processing
```javascript
// Aggregate detection data for timeline
const processTimelineData = (detections) => {
  // Group by time periods (weekly/monthly)
  // Calculate detection frequencies per species per station
  // Identify deployment periods from metadata
  // Create timeline-friendly data structure
}
```

### Visualization Libraries
- **Observable Plot**: Primary choice for clean, efficient heatmaps and time series
- **D3.js**: For advanced interactive timeline visualizations and utilities
- **Plotly.js**: Alternative for complex interactive dashboards (if needed)

### Responsive Design
- **Desktop**: Full timeline with all species and stations
- **Mobile**: Simplified view focusing on top species and overall activity
- **Interaction**: Touch-friendly hover states and zoom capabilities

## Future Acoustic Indices Integration

When the 60 acoustic indices (5-minute intervals) become available:

### Enhanced Timeline Features
1. **Multi-resolution display**: Species (daily/weekly) + Acoustic (5-minute/hourly)
2. **Index selection**: Dropdown to choose which acoustic indices to display
3. **Correlation highlighting**: Visual emphasis when species detections align with acoustic patterns
4. **Comparative views**: Side-by-side species vs acoustic index patterns
5. **Ecological significance**: Color coding or annotations for ecologically meaningful indices

### New Research Questions to Visualize
- Which acoustic indices correlate with specific species detections?
- How do acoustic patterns change seasonally vs. species activity?
- Are there acoustic "signatures" that predict species presence?
- Do different stations show different acoustic-species relationships?

## Implementation Status ✅

1. **✅ Completed**: Detection Heatmap implemented with Observable Plot
2. **✅ Completed**: Data processing utilities for timeline aggregation
3. **✅ Completed**: React component with interactive controls
4. **✅ Completed**: Integration with main dashboard page
5. **📋 Next**: Gather user feedback and iterate on visualization

This timeline will serve as both an engaging introduction to the project and a functional overview that grows more sophisticated as new data types are integrated.