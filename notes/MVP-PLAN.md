# MVP Roadmap: Acoustic Indices as Proxies for Manual Fish Detection

## Project Overview

This MVP validates whether acoustic indices can serve as reliable proxies for species presence/absence without requiring extensive manual detection efforts. Using 2021 May River data with manual detections as ground truth, we test if acoustic indices alone can provide actionable biological information for future deployments where manual detection is impractical. The analysis builds upon insights from Transue et al. (2023) Charleston Harbor study, where biological patterns were masked by anthropogenic noise in traditional SPL approaches, by testing acoustic indices in a less urbanized estuary.

**Core Research Question**: Can acoustic indices provide reliable information about fish populations WITHOUT manual detection efforts?

**Scope**: Fish-only analysis demonstrating acoustic indices as scalable monitoring solution
**Data**: 2021 acoustic indices with manual detections as validation ground truth, environmental variables, SPL data
**Timeline**: 8 focused marimo notebooks progressing from data preparation to validation of indices as standalone indicators


---

We will use marimo notebooks. The first markdown cell in each notebook should contain:
- the main title, like "Notebook 1: Data Loading and Initial Exploration"
- the purpose (e.g., "Load all data streams and perform initial quality assessment")
- the key outputs (e.g., "Clean datasets saved as parquet files with standardized column names and timestamps")

This specific format is important because it will be used to identify the embedded notebooks in the dashboard site. 

---

## Notebook 1: Data Loading and Initial Exploration

**Purpose**: Load all data streams and perform initial quality assessment  
**Key Outputs**: Raw data summaries, temporal coverage plots, missing data visualization

### Core Tasks
- Load acoustic indices (50-60 indices for 2021)
- Load manual fish detection data (every 2 hours, 0-3 intensity scale for each species)
- Load environmental data (temperature every 20 min, depth/pressure hourly)
- Load SPL data (broadband, low freq 50-1200 Hz, high freq 7000-40000 Hz)
- Load vessel detection data (presence/absence every 2 hours)

### Quality Assessment
- Temporal coverage plots showing data availability across year by station
- Missing data heatmaps by variable and time period
- Basic statistics and distributions for all variables
- Outlier detection plots (box plots, scatter plots vs time)

### Static Plots to Generate
- Timeline plots showing data coverage by source
- Distribution histograms for each acoustic index
- Correlation heatmap of acoustic indices (initial overview)
- Time series plots of temperature, depth, and SPL by station

**Output**: Clean datasets saved as parquet files with standardized column names and timestamps

---

## Notebook 2: Temporal Alignment and Aggregation

**Purpose**: Align all data to consistent 2-hour temporal resolution matching manual detections  
**Key Outputs**: Temporally aligned dataset ready for analysis

### Core Tasks
- Aggregate acoustic indices from hourly to 2-hour means (to match manual detection intervals)
- Aggregate temperature from 20-min to 2-hour means
- Keep depth/pressure at original hourly resolution, then aggregate to 2-hour
- Align SPL data to 2-hour intervals
- Create temporal variables (hour, day of year, month, season, weekday)

### Feature Engineering
- Create lag variables for environmental data (temperature t-1, t-2)
- Calculate running means for acoustic indices (6-hour, 12-hour windows)
- Generate interaction terms between key environmental variables
- Create categorical time periods (dawn, day, dusk, night based on solar times)

### Static Plots to Generate
- Before/after aggregation comparison plots
- Time series of key variables showing 2-hour resolution
- Seasonal decomposition plots for major environmental variables
- Cross-correlation plots between acoustic indices and environmental variables

**Output**: Analysis-ready dataset with all variables at 2-hour resolution

---

## Notebook 3: Acoustic Index Characterization and Reduction

**Purpose**: Understand index behavior and reduce to manageable set while preserving ecological information  
**Key Outputs**: Reduced index set (~15-20 indices) with ecological justification and temporal dependence characterization

### Index Analysis
- Correlation matrix and hierarchical clustering of all indices
- Principal Component Analysis with interpretation of components
- Variance Inflation Factor calculation to identify multicollinearity
- Response to vessel presence by index (vessel impact assessment)

### Temporal Dependence Analysis
- Autocorrelation analysis of acoustic indices (how long do patterns persist?)
- Temporal decorrelation distance (at what lag do indices become independent?)
- Document autocorrelation range to justify 2-week blocked CV approach
- Assess which indices show strongest temporal persistence (biological signal stability)

### Reduction Strategy
- Apply correlation threshold (0.85) to remove redundant indices
- Hierarchical clustering to identify functional groups
- Select representatives from each cluster based on ecological relevance and vessel noise robustness
- Prioritize indices that correlate with manual detection patterns
- Validate reduction using explained variance and cross-correlation preservation

### Index-Environment Relationships
- Correlation with temperature, seasonality, and station
- Response to known biological patterns (if apparent)
- Noise robustness assessment (index behavior during vessel events)
- Direct correlation with manual fish detections (which indices are most predictive?)

### Static Plots to Generate
- Correlation heatmap with hierarchical clustering dendrogram
- PCA biplot with index loadings
- VIF bar charts before/after reduction
- Index response to vessel presence (box plots)
- Seasonal patterns for key retained indices
- Station-wise index behavior comparison

**Output**: Reduced acoustic index dataset 

---

## Notebook 4: Fish Detection Pattern Analysis & Index-Manual Concordance

**Purpose**: Characterize fish calling patterns and validate that acoustic indices capture the same biological patterns as manual detections  
**Key Outputs**: Evidence that indices alone would tell the same ecological story as manual detections

### Species-Level Analysis
- Calling frequency and intensity by species across year
- Temporal patterns (diel, lunar, seasonal) for each species
- Station-specific calling patterns
- Environmental correlates of calling activity

### Pattern Concordance Analysis
- Compare temporal patterns: Do indices show same peaks/troughs as manual detections?
- Aggregate trend validation: Can indices alone identify spawning seasons?
- Species discrimination: Which index combinations distinguish between species?
- "What if we had no manual detections?" retrospective analysis

### Cross-Species Analysis
- Species co-occurrence patterns
- Total fish activity metrics (sum across species)
- Community-level temporal patterns
- Relationship between fish calling and vessel presence

### Environmental Relationships
- Temperature thresholds and optimal ranges by species
- Depth/tidal relationships with calling
- Seasonal phenology documentation

### Static Plots to Generate
- Species-specific calling calendars (heatmaps by day of year)
- Diel activity patterns by species (polar plots or line plots by hour)
- Temperature-calling relationships (scatter plots with trend lines)
- Station comparison of species composition
- Fish calling vs vessel presence analysis
- Lunar phase effects on calling (if lunar data available)

**Output**: Fish pattern summary statistics and documented ecological relationships

---

## Notebook 5: Vessel Detection Model Development

**Purpose**: Develop robust vessel detection using acoustic indices  
**Key Outputs**: Trained vessel detection model with performance assessment

### Model Development
- Feature selection specifically for vessel detection
- Handle class imbalance (likely more non-vessel than vessel periods)
- Train multiple algorithms (Random Forest, LightGBM, Logistic Regression)
- Hyperparameter optimization using time-series cross-validation

### Performance Assessment
- Temporal blocked cross-validation (avoid data leakage)
- Precision-recall curves and F1 scores
- Confusion matrices and classification reports
- Feature importance analysis

### Model Validation
- Performance by station and season
- Error analysis (when does the model fail?)
- Comparison with manual detection patterns

### Static Plots to Generate
- ROC curves and precision-recall curves
- Feature importance plots for best model
- Confusion matrix heatmaps
- Prediction vs actual time series plots
- Model performance by station and season
- Residual analysis plots

**Output**: Trained vessel detection model and performance metrics

---

## Notebook 6: Acoustic Indices as Standalone Predictors

**Purpose**: Validate that acoustic indices alone can predict fish presence/patterns without manual detection  
**Key Outputs**: Quantified ability of indices to serve as proxies for manual detection effort

### Model Architecture
- Test both species-specific and aggregate fish activity models
- Handle ordinal nature of 0-3 calling intensity scale
- Address zero-inflation (many periods with no calling)
- Compare indices-only vs indices+environmental variables

### Feature Engineering for Fish Models
- Use reduced acoustic index set from Notebook 3
- Include environmental variables and temporal features
- Add vessel probability predictions as feature
- Create species-specific environmental interactions

### Temporal Validation Strategy
- Temporal blocked cross-validation with 2-week blocks (prevents temporal leakage)
- Document explicitly: 7-day gap between train/test exceeds autocorrelation range
- Compare: Random CV (overly optimistic) vs Blocked CV (realistic) to show importance
- Lag analysis: How well do indices at time t predict detections at t+1, t+2?
- Temporal transfer: Train on spring, predict fall (tests robustness)

### Model Performance Metrics
- Species-specific accuracy and weighted kappa
- Aggregate fish activity prediction accuracy
- Feature importance analysis (which indices matter most?)
- Temporal persistence of predictions (do patterns hold over time?)

### Static Plots to Generate
- Model performance comparison by species
- Feature importance rankings by species
- Predicted vs actual calling intensity scatter plots
- Time series of predictions vs observations
- Confusion matrices for each species
- Residual analysis by environmental conditions
- Model performance across seasons and stations

**Output**: Trained fish calling models with performance documentation

---

## Notebook 7: Validation of Indices as Standalone Monitoring Tool

**Purpose**: Comprehensive validation that acoustic indices alone provide reliable biological information  
**Key Outputs**: Quantified evidence that indices can replace manual detection for broad-scale monitoring

### Key Validation Questions
- Can indices alone identify spawning seasons? (Compare to known biology)
- Do indices capture diel patterns without manual input?
- What biological information is preserved vs lost when using indices only?
- What is the minimum set of indices needed for reliable monitoring?

### Comparative Analysis
- Acoustic indices vs SPL-based predictions (if possible)
- Model performance vs Transue et al. results (different year comparison)
- Cross-station model transferability
- Temporal stability assessment

### Prediction Analysis
- Generate predictions for full year
- Identify periods of high prediction uncertainty
- Assess model performance during vessel-heavy periods
- Evaluate biological pattern preservation

### Static Plots to Generate
- Predicted vs known phenology comparison
- Model performance across environmental gradients
- Prediction uncertainty visualization
- Cross-station prediction transfer assessment
- Year-long prediction time series by species
- Model diagnostic plots (residuals, leverage, etc.)

**Output**: Comprehensive model validation report with ecological assessment

---

## Notebook 8: Practical Implications and Implementation Roadmap

**Purpose**: Synthesize evidence that acoustic indices can serve as proxies for manual detection  
**Key Outputs**: Clear recommendations for when/how to use indices instead of manual detection

### Core Findings
- "Can acoustic indices replace manual detection?" - Quantified answer
- Accuracy levels achievable with indices alone (by species and aggregate)
- Minimum index set required for reliable monitoring
- Temporal scales at which indices are most/least reliable

### Method Comparison
- Acoustic indices vs traditional SPL approaches
- Computational efficiency assessment
- Practical advantages/disadvantages
- Recommended best practices

### Future Directions
- Roadmap for including dolphins and more complex vessel analysis
- Recommendations for additional environmental variables
- Suggestions for real-time implementation
- Ideas for cross-year and cross-site validation

### Static Plots to Generate
- Summary performance comparison plots
- Key ecological findings visualization
- Method comparison charts
- Conceptual framework diagrams for future work

**Output**: Final report with recommendations for full study implementation

---

## Implementation Notes

### Data Management
Each notebook should save intermediate results as parquet files with clear naming conventions (e.g., `01_raw_data.parquet`, `02_aligned_data.parquet`, etc.)

### Function Development
Create utility functions in early notebooks that can be imported into later ones. Consider creating a separate `utils.py` module for commonly used functions.

### Reproducibility
Include random seeds, package versions, and clear documentation of parameter choices in each notebook.

### Performance Tracking
Log computational time and memory usage for each major operation to inform full-scale implementation.

---

## Expected Outcomes

This MVP will definitively answer: **"Can acoustic indices serve as reliable proxies for manual fish detection?"**

Specific deliverables:

1. **Quantified Proxy Performance**: X% accuracy in detecting fish presence/patterns using indices alone
2. **Minimum Viable Index Set**: The 10-15 indices that provide maximum biological information
3. **Temporal Robustness**: Evidence that indices maintain biological signal despite temporal autocorrelation
4. **Practical Guidelines**: Clear recommendations for when indices can replace manual detection
5. **Scalability Demonstration**: Framework for automated monitoring without manual effort

Key advantages over manual detection:
- Continuous monitoring capability (not just 2-hour snapshots)
- No human effort required after initial setup
- Noise-robust compared to traditional SPL approaches
- Cost-effective for long-term deployments

This validation establishes acoustic indices as a practical alternative to manual detection for broad-scale marine monitoring, directly addressing the unsustainable manual effort identified by Transue et al. (2023).