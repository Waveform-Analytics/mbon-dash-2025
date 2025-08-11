# Acoustic Indices Integration Plan
*Marine Biodiversity Dashboard - MBON USC 2025*

## Executive Summary

This plan outlines the integration of comprehensive acoustic indices data (56 indices) with existing species detection and environmental data to answer the core research question: **"Can computed acoustic indices help us understand and predict marine biodiversity patterns as an alternative to expensive, labor-intensive manual species detection methods?"**

## Data Integration Strategy

### Current Status
- ✅ **Received**: `AcousticIndices_9M_FullBW_v1.csv` (2021, hourly data, 56 indices)
- 🔄 **Expected**: Additional files for stations 14M, 37M, years 2018, and alternative bandwidths

### Flexible File Architecture
```
data/indices/raw/
├── AcousticIndices_9M_FullBW_v1.csv      ✅ Available
├── AcousticIndices_14M_FullBW_v1.csv     🔄 Expected
├── AcousticIndices_37M_FullBW_v1.csv     🔄 Expected
├── AcousticIndices_9M_2018_FullBW_v1.csv 🔄 Expected (if naming changes)
└── AcousticIndices_*_[OTHER_BW]_*.csv    🔄 Expected (additional bandwidth)
```

**Design Principles**:
- **Flexible naming**: Support variations in file naming conventions
- **Scalable**: Handle new stations, years, and bandwidth types automatically
- **Version tracking**: Support versioned files (v1, v2, etc.)
- **Quality flags**: Track data completeness and processing issues

## Processing Pipeline Architecture

### Modular Pipeline Design
```
scripts/
├── pipeline/
│   ├── config.py                    # Processing parameters & file patterns
│   ├── run_full_pipeline.py         # Orchestrates complete workflow
│   ├── run_partial_pipeline.py      # Run specific steps (development)
│   └── steps/
│       ├── 1_process_raw_data.py     # Clean all raw data sources
│       ├── 2_align_temporal_windows.py # Hourly → 2-hour aggregation
│       ├── 3_join_datasets.py        # Combine all data types
│       ├── 4_handle_missing_data.py  # Missing data strategies
│       ├── 5_run_pca_analysis.py     # Dimensionality reduction
│       └── 6_prepare_dashboard_data.py # CDN-ready exports
├── analysis/
│   ├── pca_analysis.py              # Principal component analysis
│   ├── correlation_analysis.py     # Index-species correlations
│   └── biodiversity_models.py      # Predictive modeling
└── utils/
    ├── temporal_alignment.py       # Time window utilities
    ├── missing_data.py            # Interpolation strategies
    └── export_cdn.py              # Data export utilities
```

### Key Processing Challenges & Solutions

#### 1. Temporal Alignment
**Challenge**: Acoustic indices are hourly, detection data is 2-hourly
**Solution**: Configurable aggregation methods
```python
AGGREGATION_METHODS = {
    'mean': np.mean,      # Default for most indices
    'max': np.max,        # For peak detection indices  
    'min': np.min,        # For minimum thresholds
    'sum': np.sum,        # For count-based indices
    'median': np.median   # For robust central tendency
}
```

#### 2. Missing Data Strategy
**Hierarchical approach**:
- **≤2 hours**: Linear interpolation with quality flags
- **2-6 hours**: Mark as "interpolated", include with warnings
- **>6 hours**: Exclude from analysis, note in reports
- **Seasonal gaps**: Analyze available periods separately

#### 3. Index Selection & Filtering
**Multi-stage filtering**:
```python
# Stage 1: Technical filtering
- Remove indices with >20% missing data
- Remove zero-variance indices
- Remove perfectly correlated pairs (r > 0.95)

# Stage 2: Ecological relevance  
- Group by categories (temporal, frequency, diversity, etc.)
- Literature-based prioritization
- Expert knowledge integration

# Stage 3: PCA-informed selection
- Initial PCA on filtered set (~20-25 indices)
- Select high-loading indices for top 3-4 components
- Final analytical set: ~12-15 indices
```

## Analysis Framework

### Primary Analysis: Principal Component Analysis

#### Objectives
1. **Dimensionality Reduction**: Reduce 56 indices to 3-5 interpretable components
2. **Index Ranking**: Identify most informative indices for biodiversity assessment
3. **Pattern Discovery**: Understand natural groupings and relationships

#### PCA Implementation Strategy
```python
# PCA Analysis Pipeline
1. Data preprocessing (standardization, missing data)
2. Initial PCA (all indices)
3. Component interpretation (loadings analysis)
4. Scree plot analysis (explained variance)
5. Index contribution rankings
6. Component score calculation
7. Biological interpretation
```

#### Expected Outputs
- **Component loadings**: Which indices contribute to each PC
- **Explained variance**: How much variation each PC captures  
- **Index rankings**: Top contributing indices across components
- **Interpretable components**: Biological/ecological meaning of PCs

### Secondary Analysis: Biodiversity Prediction

#### Correlation Analysis
- **Index-species correlations**: Which indices predict species presence
- **Environmental interactions**: Temperature/depth effects on indices
- **Temporal stability**: Consistency across seasons/years

#### Predictive Modeling
- **Linear models**: Index combinations → species detection rates
- **Component models**: PC scores → biodiversity metrics
- **Environmental corrections**: Account for temp/depth confounders

## Dashboard Integration Strategy

### New Dashboard Pages

#### 1. Index Explorer
**Purpose**: Interactive exploration of acoustic indices
**Features**:
- Time series plots for individual indices
- Correlation matrix heatmaps  
- Index category comparisons
- Environmental overlay options

#### 2. PCA Analysis Dashboard
**Purpose**: Visualize dimensionality reduction results
**Features**:
- Interactive biplot (loadings + scores)
- Scree plot with explained variance
- Component interpretation tables
- Top indices identification

#### 3. Biodiversity Prediction
**Purpose**: Show index-species relationships
**Features**:
- Correlation matrices (indices vs species)
- Prediction model results
- Cost-effectiveness comparisons
- Recommendation engine

### Presentation Strategy

#### Milestone 1 (Week 2): "Here's what the acoustic indices look like"
- Basic index time series
- Correlation patterns between indices
- Station comparison plots
- Data availability summaries

#### Milestone 2 (Week 4): "Here's what we're learning"  
- PCA results and component interpretation
- Top-performing indices identification
- Index-species correlation findings
- Environmental confounder analysis

#### Milestone 3 (Final): "Here's what managers should use"
- Reduced index set recommendations
- Cost-benefit analysis results
- Practical implementation guidelines
- Monitoring protocol suggestions

## Technical Implementation

### Data Storage Architecture
```
mbon-dash-2025/
├── data/                    # Raw data (version controlled)
├── processed/              # Intermediate files (gitignored)
├── analysis/               # Analysis results (gitignored)
├── cdn/                    # Dashboard data (gitignored)
└── public/                 # Static assets only
```

### Flexible File Detection
```python
# Automatic file discovery
ACOUSTIC_INDEX_PATTERNS = [
    "AcousticIndices_{station}_{bandwidth}_v*.csv",
    "Acoustic_Indices_{station}_{bandwidth}_v*.csv",
    "{station}_AcousticIndices_{bandwidth}_v*.csv"
]

def discover_acoustic_files(data_dir):
    """Automatically find and categorize acoustic index files"""
    # Implementation handles naming variations
    # Returns structured metadata about available files
    # Logs missing expected files for user awareness
```

### Quality Control & Validation
```python
# Automated validation checks
- File format validation (expected columns)
- Data range checks (reasonable index values)
- Temporal continuity assessment
- Cross-file consistency verification
- Missing data pattern analysis
```

## Risk Mitigation

### Data Availability Risks
**Risk**: New acoustic index files may have different formats/naming
**Mitigation**: Flexible parsing with extensive error handling and logging

**Risk**: Missing expected files (other stations/years)
**Mitigation**: Pipeline works with available data, clearly documents gaps

### Analysis Risks  
**Risk**: PCA may not reveal interpretable patterns
**Mitigation**: Multiple analysis approaches (hierarchical clustering, factor analysis)

**Risk**: Indices may not predict biodiversity well
**Mitigation**: Focus on understanding relationships rather than just prediction

### Timeline Risks
**Risk**: Analysis takes longer than expected
**Mitigation**: Iterative presentation approach, each milestone stands alone

## Success Criteria

### Technical Success
- ✅ Pipeline processes new acoustic index files automatically
- ✅ Flexible handling of naming variations and missing data
- ✅ Scalable architecture for additional datasets

### Scientific Success  
- 🎯 Identify <10 key indices explaining >70% of biodiversity variation
- 🎯 Demonstrate clear index-species relationships
- 🎯 Quantify cost savings vs manual annotation

### Communication Success
- 🎯 Clear visualizations showing acoustic-biodiversity connections
- 🎯 Actionable recommendations for monitoring programs  
- 🎯 Accessible presentation for non-acoustics researchers

## Next Steps (Week 1)

### Immediate Actions
1. **Restructure data folders** according to new architecture
2. **Create pipeline configuration** with flexible file patterns
3. **Implement basic acoustic index processing** for 9M data
4. **Temporal alignment prototype** (hourly → 2-hour windows)
5. **Initial PCA analysis** to validate approach

### Development Focus
- Prioritize flexibility over optimization
- Build with assumption that more data will arrive
- Document all processing decisions for reproducibility
- Create clear logging for troubleshooting

This plan provides a roadmap for systematic integration of acoustic indices while maintaining flexibility for unknown future datasets and discoveries.