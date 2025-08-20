# Exploratory Plotting Suggestions for MBON Dashboard
*Generated August 19, 2025 | Updated with Implementation Status*

## 📊 **Current Implementation Status**

### ✅ **Completed**
- **Step 1A: Raw Data Landscape** - Live on `/explore/indices` page
  - Shows all 61 acoustic indices with availability heatmap
  - Category-based color coding and data coverage statistics

### 🚧 **In Progress**
- **Step 1B: Index Distribution & Quality Check** - Recently fixed
  - **Fixed Issues**: Now uses PDF curves, bandwidth separation, proper 0-1 normalization, clear index labels
  - **Implementation**: Probability density functions with FullBW/8kHz user selection
  - **Status**: Ready for CDN upload and testing

### ⏸️ **Paused**
- **Step 1I: PCA Biplot** - Removed until foundation steps complete

### 📋 **Planned Next**
- Steps 1C-1H: Progressive analysis pipeline
- Environmental and temporal analysis sections

---

## 🎯 Primary Research Focus Plots

When implementing this, remind me to upload data to the cdn as needed (ie if we use python to do analysis and want to make the results (json) available via CDN.

### 1. **Acoustic Indices → Biodiversity Prediction: A Step-by-Step Journey**

#### **Step 1A: The Raw Data Landscape** ✅ **COMPLETED**
- **All Indices Overview**: Heatmap or table showing all 60+ available indices
  - Color by index category (diversity, complexity, bioacoustic, temporal, frequency)
  - Show data availability per station/time period
  - Highlight missing data patterns
  - *Purpose: Show the starting complexity we need to reduce*
  - **Status: Implemented and live on /explore/indices page**

#### **Step 1B: Index Distribution & Quality Check** ✅ **COMPLETED**
- **Index Distribution Plots**: Small multiples PDF/density plots of all indices
  - **Probability Density Functions**: Smooth curves showing distribution shape
  - **Bandwidth Separation**: User can select FullBW or 8kHz (not combined)
  - **Proper Data Scaling**: Continuous 0-1 normalization for comparison
  - **Clear Index Labels**: Prominent text overlay showing specific index names (ACI, LEQt, etc.)
  - Identify skewed/bimodal distributions
  - Show raw quality metrics (no arbitrary quality flags)
  - *Purpose: Quality control before analysis*
  - **Status: Implementation complete, ready for CDN upload**

#### **Step 1C: Station Data Balance Analysis** 📋 **PLANNED**
- **Data Availability Matrix**: Station × Time × Index availability
  - Bar chart showing observation counts per station
  - Timeline showing data gaps
  - Station comparison of temporal coverage
  - *Purpose: Explain why 9M dominates (more data?)*

#### **Step 1D: Variance-Based Index Ranking** 📋 **PLANNED**
- **Index Variance Ranking**: Bar chart of indices ranked by variance
  - Color bars by index category
  - Show threshold line for "high variance" selection
  - Highlight the top 25-30 indices selected
  - *Purpose: Show which indices carry the most information*

#### **Step 1E: Index Correlation Network** 📋 **PLANNED**
- **Correlation Network Plot**: Network showing index relationships
  - Nodes = indices (sized by variance, colored by category)
  - Edges = high correlations (>0.8 or 0.9)  
  - Clusters show highly correlated groups
  - *Purpose: Visualize redundancy before removal*

#### **Step 1F: Progressive Index Selection** 📋 **PLANNED**
- **Selection Timeline**: Multi-panel showing the filtering process
  - Panel 1: All 60+ indices
  - Panel 2: After variance filtering (top 50)
  - Panel 3: After correlation filtering (final 25)
  - Show which indices were dropped at each step and why
  - *Purpose: Make the selection process transparent*

#### **Step 1G: PCA Scree Plot & Variance Selection** 📋 **PLANNED**
- **Scree Plot**: Eigenvalues for all components
  - Cumulative variance explained curve
  - "Elbow" identification for optimal components
  - Threshold line at 80% variance
  - *Purpose: Show why we chose X components*

#### **Step 1H: Component Interpretation** 📋 **PLANNED**
- **Loading Matrix Heatmap**: PC1-PC5 vs selected indices
  - Color intensity = loading strength
  - Cluster indices by similar loading patterns
  - Annotate with index categories
  - *Purpose: Show what each component represents*

#### **Step 1I: The Final PCA Biplot** ⏸️ **PAUSED** 
- **Enhanced PCA Biplot**: Now with full context from previous steps
  - Better legend explaining the selection process
  - Annotation showing what PC1 & PC2 represent
  - Clear station balance explanation
  - Improved arrow visibility and labeling
  - *Purpose: The culmination of the methodical process*
  - **Status: Removed from /acoustic-biodiversity page until prep work complete**

#### **Step 1J: Biodiversity Relationships** 📋 **PLANNED**
- **PCA-Species Correlation**: PC scores vs species richness
  - Scatter plots for PC1, PC2, PC3 vs biodiversity
  - Station-specific trends
  - Temporal patterns in PC scores
  - *Purpose: Validate that PCA captures biological signal*

### 2. **Index Dimensionality Reduction**
- **Variance Explained Plot**: PCA eigenvalues (scree plot) showing optimal number of components
- **Component Loading Heatmap**: Which indices contribute most to PC1, PC2, PC3
- **Index Category Contribution**: Boxplots showing how different index types (temporal, frequency, complexity) load onto components

## 🌊 Environmental Confounders

### 3. **Environment vs Indices**
- **Environmental Correlation Matrix**: Temperature/depth vs acoustic indices
  - Identify which indices are environmentally driven vs biologically driven
- **Diurnal Patterns**: Hourly averages of key indices overlaid with temperature cycles
  - Multi-panel plot showing different stations
- **Seasonal Trends**: Monthly patterns in indices vs environmental variables (2018 vs 2021)

### 4. **Environmental Correction Analysis**
- **Before/After Correction Scatter**: Raw indices vs environmentally-corrected indices
- **Residual Analysis**: Species detection patterns after removing environmental effects

## 🗺️ Spatial Patterns

### 5. **Station Comparison**
- **Station Profile Radar Charts**: Average index values for each station (normalized 0-1)
- **Between-Station Distance Matrix**: Acoustic environment similarity using index profiles
- **Geographic Gradient Analysis**: Index values vs station position (if stations form a spatial gradient)

## ⏰ Temporal Patterns

### 6. **Time Series Analysis**
- **Multi-Index Time Series**: Key indices over time with species detection events overlaid
- **Seasonal Decomposition**: Trend, seasonal, and residual components for top indices
- **Cross-Correlation Analysis**: Lag relationships between indices and species detections

## 🔊 Index Performance Evaluation

### 7. **Index Ranking and Selection**
- **Predictive Power Ranking**: Bar chart of indices ranked by ability to predict species richness
- **Redundancy Analysis**: Network plot showing highly correlated indices (>0.8)
- **Index Stability**: Coefficient of variation across time periods for each index

### 8. **Bandwidth Comparison**
- **FullBW vs 8kHz Comparison**: Side-by-side correlation with species detections
- **Frequency Range Sensitivity**: Which species/sounds are better captured in different bandwidths

## 🐠 Species-Specific Analysis

### 9. **Species Activity Patterns**
- **Species Co-occurrence Network**: Which species are detected together
- **Species-Index Affinity**: Which indices best predict specific species (silver perch, toadfish, etc.)
- **Bio vs Anthropogenic Separation**: Can indices distinguish biological from anthropogenic sounds?

### 10. **Detection Probability Modeling**
- **ROC Curves**: Index-based models for predicting species presence/absence
- **Threshold Analysis**: Optimal index cutoff values for species detection

## 📊 Method Validation

### 11. **Manual vs Automated Comparison**
- **Index Proxy Performance**: How well do index combinations replicate manual annotation patterns
- **Processing Time vs Information Trade-off**: Computational cost vs biological insight
- **Sensitivity Analysis**: How robust are index-based predictions to parameter changes

## 🎨 Dashboard Implementation Suggestions

### Interactive Plot Types (Observable Plot)
1. **Linked Brushing**: Select time period in one chart, update all others
2. **Faceted Small Multiples**: Compare patterns across stations/years
3. **Animated Transitions**: Show temporal evolution of index relationships
4. **Hover Details**: Species names, exact index values, environmental context
5. **Responsive Design**: Simplified mobile versions focusing on key insights

### Color Schemes
- **Stations**: Ocean blues (light to dark: 9M→14M→37M)
- **Index Categories**: Categorical palette (viridis or ColorBrewer)
- **Correlation Strength**: Diverging red-white-blue
- **Time**: Sequential yellow-orange-red for temporal progression

### Key Metrics to Highlight
- Top 5 predictive indices
- Variance explained by first 3 PCs
- Station-specific acoustic signatures
- Environmental vs biological drivers

## 🔧 Detailed Implementation Workflow

### Plot Implementation Pattern
**Python Analysis** → **JSON Export** → **CDN Upload** → **Dashboard Visualization**

---

## 📊 Plot-by-Plot Implementation Details

### **Plot 1: PCA Biplot** 
*Priority: High - Addresses core research question*

**Python Module (`mbon_analysis/analysis/dimensionality.py`)**:
```python
def compute_pca_analysis():
    # Load acoustic indices data
    # Standardize 56+ indices 
    # Perform PCA (keep components explaining 80% variance)
    # Calculate loadings for top contributing indices
    # Return: components, loadings, variance_explained, point_data
```

**JSON Structure**:
```json
{
  "pca_biplot": {
    "points": [
      {"pc1": 0.23, "pc2": -0.45, "station": "9M", "datetime": "2021-05-01T10:00:00", "species_count": 3},
      ...
    ],
    "loadings": [
      {"index": "ACI", "pc1": 0.67, "pc2": 0.12, "category": "complexity"},
      ...
    ],
    "variance_explained": [45.2, 23.1, 12.8],
    "metadata": {"total_variance": 81.1, "n_components": 3}
  }
}
```

**Dashboard Component (`components/charts/PCABiplot.tsx`)**:
- Observable Plot scatter plot with PC1 vs PC2
- Color points by station, size by species_count
- Add loading vectors as arrows
- Interactive hover for point details

---

### **Plot 2: Index-Species Correlation Heatmap**
*Priority: High - Key for index selection*

**Python Module (`mbon_analysis/analysis/correlations.py`)**:
```python
def compute_index_species_correlations():
    # Aggregate detections to 2-hour windows
    # Calculate species richness per window
    # Compute Pearson correlations: indices vs species metrics
    # Hierarchical clustering for ordering
    # Return: correlation_matrix, cluster_order, significance
```

**JSON Structure**:
```json
{
  "correlation_heatmap": {
    "correlations": [
      {"index": "ACI", "species": "species_richness", "correlation": 0.34, "p_value": 0.001},
      {"index": "ACI", "species": "bio_detections", "correlation": 0.28, "p_value": 0.012},
      ...
    ],
    "index_order": ["ACI", "NDSI", "H_Shannon", ...],
    "species_metrics": ["species_richness", "bio_detections", "anthro_detections"],
    "clustering": {"linkage": "ward", "distance": "euclidean"}
  }
}
```

**Dashboard Component (`components/charts/CorrelationHeatmap.tsx`)**:
- Observable Plot cell plot for heatmap
- Hierarchical clustering order for rows/columns
- Color scale: red-white-blue diverging
- Click to highlight specific index-species relationships

---

### **Plot 3: Environmental Correlation Matrix**
*Priority: Medium - Understanding confounders*

**Python Module (`mbon_analysis/analysis/environmental.py`)**:
```python
def compute_environmental_correlations():
    # Merge indices with temp/depth data by datetime
    # Calculate correlations: indices vs environmental variables
    # Identify environmentally-driven vs biologically-driven indices
    # Return: env_correlations, index_categories
```

**JSON Structure**:
```json
{
  "environmental_correlations": {
    "correlations": [
      {"index": "ACI", "env_var": "temperature", "correlation": -0.12, "category": "weak"},
      {"index": "BioEnergy", "env_var": "depth", "correlation": 0.67, "category": "strong"},
      ...
    ],
    "index_classification": {
      "environmentally_driven": ["RMS", "LFC"],
      "biologically_driven": ["ACI", "NDSI", "BioEnergy"],
      "mixed": ["H_Shannon", "ADI"]
    }
  }
}
```

---

### **Plot 4: Station Profile Radar Charts**
*Priority: Medium - Spatial comparison*

**Python Module (`mbon_analysis/analysis/spatial.py`)**:
```python
def compute_station_profiles():
    # Calculate mean index values per station
    # Normalize to 0-1 scale for comparison
    # Include confidence intervals
    # Return: station_profiles, index_ranges
```

**JSON Structure**:
```json
{
  "station_profiles": {
    "profiles": [
      {
        "station": "9M",
        "indices": [
          {"name": "ACI", "value": 0.67, "ci_lower": 0.62, "ci_upper": 0.72},
          ...
        ]
      },
      ...
    ],
    "index_categories": {
      "diversity": ["H_Shannon", "H_Renyi"],
      "complexity": ["ACI", "NDSI"],
      "bioacoustic": ["BioEnergy", "BI"]
    }
  }
}
```

---

### **Plot 5: Temporal Patterns Time Series**
*Priority: Medium - Understanding dynamics*

**Python Module (`mbon_analysis/analysis/temporal.py`)**:
```python
def compute_temporal_patterns():
    # Calculate hourly/daily/monthly patterns
    # Overlay species detection events
    # Identify peak activity periods
    # Return: time_series, detection_events, patterns
```

**JSON Structure**:
```json
{
  "temporal_patterns": {
    "time_series": [
      {
        "datetime": "2021-05-01T10:00:00",
        "station": "9M",
        "ACI": 0.45,
        "NDSI": 0.23,
        "species_detections": 2,
        "bio_detections": 1,
        "anthro_detections": 1
      },
      ...
    ],
    "peak_periods": {
      "daily": {"start_hour": 6, "end_hour": 10},
      "seasonal": {"peak_months": [5, 6, 7]}
    }
  }
}
```

---

## 🛠️ Implementation Steps for Each Plot

### **Step-by-Step Workflow**:

1. **Python Analysis**:
   ```bash
   # Create analysis function in mbon_analysis package
   uv run scripts/analysis/generate_[plot_name]_data.py
   ```

2. **JSON Export**:
   ```python
   # Export results to data/cdn/processed/[plot_name].json
   # Follow consistent JSON schema
   ```

3. **CDN Upload**:
   ```bash
   # Upload to Cloudflare R2
   # Update data manifest
   npm run sync-data:upload
   ```

4. **Dashboard Component**:
   ```typescript
   // Create React component with Observable Plot
   // Load JSON data via useData hook
   // Implement interactive features
   ```

5. **Integration**:
   ```typescript
   // Add to appropriate dashboard page
   // Test responsive design
   // Add export functionality
   ```

---

## 📅 Suggested Implementation Order

### **Week 1: Foundation**
1. **PCA Biplot** - Core dimensionality reduction analysis
2. **Index-Species Correlation Heatmap** - Key relationships

### **Week 2: Context**  
3. **Environmental Correlation Matrix** - Understanding confounders
4. **Station Profile Radar Charts** - Spatial patterns

### **Week 3: Dynamics**
5. **Temporal Patterns Time Series** - Time-based insights
6. **Index Performance Ranking** - Method evaluation

### **Week 4: Advanced**
7. **Species Co-occurrence Network** - Biological insights
8. **Predictive Performance Scatter** - Model validation

---

## 🔄 Reusable Components

**Create Once, Use Everywhere**:
- `useAnalysisData(plotType)` - Data loading hook
- `ExportButton` - Download plot data/images  
- `StationFilter` - Filter by station
- `TimeRangeFilter` - Filter by date range
- `IndexSelector` - Choose which indices to display

**JSON Schema Consistency**:
- Always include metadata (timestamps, data sources)
- Standardize station/datetime formats
- Include confidence intervals where applicable
- Add data quality flags