# MBON Acoustic Monitoring Dashboard - Site Structure

## Overview
A web dashboard presenting marine acoustic monitoring research, focusing on whether acoustic indices can predict biological activity in marine environments.

---

## 🏠 Homepage (`/`)

### Hero Section
- **Title**: "Marine Biodiversity Acoustic Monitoring"
- **Subtitle**: "Can acoustic indices predict marine life activity patterns?"
- **Key Metrics Cards**:
  - 3,026 biological events detected
  - 7 species monitored
  - 3 monitoring stations
  - 2 years of data (2018, 2021)

### Project Overview Section
- **Research Question**: Brief explanation of the core question
- **Methodology**: 3-4 bullet points on approach
- **Interactive Station Map**: Mapbox showing 9M, 14M, 37M stations with depth/location info

### Quick Navigation Cards
- Link to each main section with icon and description
- Recent findings highlight box

---

## 📊 1. Data Overview (`/data`)

### 1.1 Detection Data (`/data/detections`)
- **Summary Statistics Table**:
  - Total observations: 26,280
  - Species detected: List with counts
  - Temporal coverage: Timeline visualization
  
- **Interactive Heatmap**: Species × Time matrix showing detection intensity
- **Download Options**: CSV exports

### 1.2 Acoustic Indices (`/data/acoustic-indices`)
- **Index Reference Table** (filterable):
  - 61 indices with descriptions
  - Categories: Temporal, Frequency, Complexity, Diversity
  - Correlation groups (showing which indices are redundant)
  
- **Index Explorer Tool**:
  - Select index → see time series plot
  - Statistical distributions by station
  - Download selected data

### 1.3 Environmental Data (`/data/environmental`)
- **Temperature Time Series**: Interactive plot by station
- **Tidal/Depth Patterns**: Visualization of depth changes
- **Environmental Summary Stats**: Tables with ranges, means, anomalies

---

## 🐟 2. Species Profiles (`/species`)

### Species Selection Page (`/species`)
- Grid of species cards with:
  - Species name and image/icon
  - Total events detected
  - Primary calling time (e.g., "Night caller")
  - Link to detailed profile

### Individual Species Pages (`/species/[species-name]`)

#### Example: Spotted Seatrout (`/species/spotted-seatrout`)

**Page Sections**:

1. **Species Overview**
   - Scientific name, common names
   - Total events: 1,076
   - Chorus rate: 79.5%
   - Peak calling months: May-June

2. **Calling Patterns**
   - **Diel Pattern Chart**: 24-hour activity distribution
   - **Seasonal Pattern**: Monthly event counts
   - **Event Duration Distribution**: Histogram of event lengths

3. **Event Characteristics**
   - Average event duration: 7.3 hours
   - Typical onset type: Rapid (< 2 hours)
   - Environmental preferences: Temperature range, tidal state

4. **Acoustic Signatures**
   - Top 3 predictive indices with correlation values
   - Time series showing index behavior before/during/after events
   - Detection rules: "If ACI > X at night → 70% chance of chorus in 4 hours"

5. **Station Comparison**
   - Activity levels at each station
   - Site-specific patterns

---

## 📈 3. Biological Events (`/events`)

### 3.1 Event Explorer (`/events/explorer`)
- **Interactive Timeline**:
  - Gantt chart showing all 3,026 events
  - Filter by: Species, Station, Year, Event type, Intensity
  - Color coding: Intensity levels (1-3)
  - Hover for details: Duration, peak time, environmental conditions

### 3.2 Event Analysis (`/events/analysis`)
- **Event Type Breakdown**:
  - Pie chart: Brief (55%), Rapid onset (39%), Gradual (2.4%), Sustained (1.4%)
  
- **Temporal Patterns**:
  - Diel distribution: Night (53%), Dusk (21%), Day (16%), Dawn (9%)
  - Day-of-week patterns
  - Lunar phase analysis (if available)

- **Event Transitions**:
  - Visualization of typical event progression
  - Buildup → Peak → Decay patterns
  - Species-specific transition signatures

### 3.3 Chorus Events (`/events/chorus`)
- **Chorus Statistics**:
  - 1,153 chorus events (38% of all events)
  - Mean duration: 11.2 hours
  - Species ranking by chorus frequency

- **Chorus Predictors**:
  - Environmental triggers (temperature thresholds)
  - Acoustic index patterns preceding chorus
  - Multi-species coordination patterns

---

## 🔍 4. Acoustic Analysis (`/analysis`)

### 4.1 Index Performance (`/analysis/indices`)
- **Performance Matrix**: Species × Index correlation heatmap
- **Top Performers Table**:
  ```
  | Index | Best For | Correlation | Lead Time | Detection Rate |
  |-------|----------|-------------|-----------|----------------|
  | LFC   | Overall fish | 0.55 | 4h | 72% |
  | VARf  | Overall fish | 0.54 | 6h | 68% |
  | ACI   | Spotted seatrout | 0.48 | 3h | 65% |
  ```

### 4.2 Predictive Models (`/analysis/models`)
- **Model Comparison**:
  - Simple threshold models
  - Time-aware models (accounting for temporal correlation)
  - Performance metrics: Precision, Recall, F1

- **Real-time Predictions** (if implemented):
  - Current acoustic state vs baseline
  - Probability of event in next 6/12/24 hours
  - Confidence intervals

### 4.3 Environmental Correlations (`/analysis/environmental`)
- **Temperature Effects**:
  - Scatter plots: Temperature vs calling activity
  - Species-specific temperature preferences
  - Seasonal temperature patterns

- **Tidal Influences**:
  - Calling activity by tidal state
  - High/low tide preferences by species

---

## 🎯 5. Detection Rules (`/detection`)

### 5.1 Rule Dashboard (`/detection/rules`)
- **Deployable Detection Rules**:
  ```
  IF acoustic_index > threshold 
  AND time_of_day IN preferred_hours 
  AND temp > min_temp 
  THEN probability of event = X%
  ```

- **Rule Performance Table**:
  - Success rate, False positive rate, Lead time
  - Sortable by metric

### 5.2 Rule Testing (`/detection/test`)
- **Interactive Rule Tester**:
  - Input: Index values, time, temperature
  - Output: Predicted species activity
  - Historical validation results

---

## 📚 6. Methods & Documentation (`/methods`)

### 6.1 Data Collection (`/methods/data-collection`)
- Hydrophone deployment details
- Recording schedules
- Manual annotation process
- Data quality control

### 6.2 Acoustic Indices (`/methods/acoustic-indices`)
- Index calculation methods
- Software and parameters used
- Validation approaches

### 6.3 Analysis Approaches (`/methods/analysis`)
- Evolution of analysis strategy
- Why event-based analysis works better
- Statistical methods used
- Code repository links

### 6.4 Publications (`/methods/publications`)
- Related papers
- Presentations
- Dataset DOIs

---

## 🔬 7. Research Insights (`/insights`)

### 7.1 Key Findings (`/insights/findings`)
- **Major Discoveries**:
  1. Night/dusk dominate calling (74% of events)
  2. Species-specific acoustic signatures exist
  3. Environmental triggers are predictable
  4. 4-6 hour prediction windows achievable

### 7.2 Implications (`/insights/implications`)
- Real-time monitoring possibilities
- Cost-effective biodiversity assessment
- Early warning system potential
- Complementary to AI species detection

### 7.3 Future Work (`/insights/future`)
- Longer time series needs
- Multi-station coordination
- Real-time deployment plans
- Integration with other monitoring

---

## 📥 8. Data Access (`/downloads`)

### Download Center
- **Processed Datasets**:
  - Biological events (CSV, 3,026 records)
  - Event statistics by species
  - Acoustic index time series
  - Environmental data

- **Visualizations**:
  - PNG exports of all charts
  - Interactive notebook examples

- **Code & Methods**:
  - Python analysis scripts
  - R visualization code
  - API documentation (if applicable)

---

## 🎛️ 9. Interactive Tools (`/tools`)

### 9.1 Event Predictor (`/tools/predictor`)
- Input current conditions
- Get probability estimates
- See similar historical events

### 9.2 Pattern Explorer (`/tools/explorer`)
- Select time range and species
- Visualize acoustic patterns
- Compare with environmental data

### 9.3 Custom Analysis (`/tools/custom`)
- Upload your own acoustic data
- Apply detection rules
- Generate reports

---

## 💡 Technical Implementation Notes

### Navigation Structure
```
Main Nav:
- Home
- Data ▼
  - Detection Data
  - Acoustic Indices  
  - Environmental
- Species ▼
  - [List of 7 species]
- Events ▼
  - Explorer
  - Analysis
  - Chorus Events
- Analysis ▼
  - Index Performance
  - Models
  - Environmental
- Detection Rules
- Methods
- Insights
- Downloads
```

### Key Interactive Components
1. **Filterable Tables**: Use DataTables or AG-Grid
2. **Time Series Plots**: Plotly or Nivo for interactivity
3. **Heatmaps**: D3.js or Plotly
4. **Map**: Mapbox GL JS
5. **Event Timeline**: Gantt chart library or custom D3

### Data Loading Strategy
- **Static Pages**: Pre-rendered with Next.js SSG
- **Small Data** (< 50KB): Direct CDN loading
- **Large Data** (> 50KB): Progressive loading with API endpoints
- **Real-time Updates**: WebSocket for live predictions (future)

### Mobile Considerations
- Responsive tables that stack on mobile
- Touch-friendly time series navigation
- Simplified visualizations for small screens
- Progressive disclosure of complex information

### Performance Priorities
1. Sub-second page loads
2. Instant filtering/sorting on small datasets
3. Progressive loading indicators for large data
4. Export functionality for offline analysis

---

## 🚀 MVP Pages (Phase 1)

Start with these essential pages:

1. **Homepage** - Overview and navigation
2. **Data Overview** - Basic statistics and summaries  
3. **Species Profiles** - One page per species with patterns
4. **Event Explorer** - Interactive timeline of all events
5. **Key Findings** - Main research insights
6. **Methods** - How the analysis was done

Then expand to include predictive models, detection rules, and interactive tools in Phase 2.