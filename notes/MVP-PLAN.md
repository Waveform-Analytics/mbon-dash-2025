# MVP Roadmap: Fish Acoustic Prediction using Acoustic Indices

## Project Overview

This MVP focuses on developing acoustic index-based models to predict fish calling intensity in marine soundscapes, building upon the Transue et al. (2023) Charleston Harbor framework. The analysis is structured as a series of marimo notebooks, each with specific focus areas, to maintain transparency and reproducibility while establishing a foundation for the full study.

**Scope**: Fish-only analysis with vessel detection as supporting feature
**Data**: 2021 acoustic indices, manual detections, environmental variables, SPL data
**Timeline**: 8 focused marimo notebooks progressing from data preparation to model validation

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
**Key Outputs**: Reduced index set (~15-20 indices) with ecological justification

### Index Analysis
- Correlation matrix and hierarchical clustering of all indices
- Principal Component Analysis with interpretation of components
- Variance Inflation Factor calculation to identify multicollinearity
- Response to vessel presence by index (vessel impact assessment)

### Reduction Strategy
- Apply correlation threshold (0.85) to remove redundant indices
- Hierarchical clustering to identify functional groups
- Select representatives from each cluster based on ecological relevance and vessel noise robustness
- Validate reduction using explained variance and cross-correlation preservation

### Index-Environment Relationships
- Correlation with temperature, seasonality, and station
- Response to known biological patterns (if apparent)
- Noise robustness assessment (index behavior during vessel events)

### Static Plots to Generate
- Correlation heatmap with hierarchical clustering dendrogram
- PCA biplot with index loadings
- VIF bar charts before/after reduction
- Index response to vessel presence (box plots)
- Seasonal patterns for key retained indices
- Station-wise index behavior comparison

**Output**: Reduced acoustic index dataset with selection justification document

---

## Notebook 4: Fish Detection Pattern Analysis

**Purpose**: Characterize fish calling patterns and their environmental relationships  
**Key Outputs**: Understanding of species-specific temporal and environmental patterns

### Species-Level Analysis
- Calling frequency and intensity by species across year
- Temporal patterns (diel, lunar, seasonal) for each species
- Station-specific calling patterns
- Environmental correlates of calling activity

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

## Notebook 6: Fish Calling Prediction Model Development

**Purpose**: Develop models to predict fish calling intensity using acoustic indices  
**Key Outputs**: Species-specific calling prediction models with ecological validation

### Model Architecture
- Individual models per species vs multi-output approach decision
- Handle ordinal nature of 0-3 calling intensity scale
- Address zero-inflation (many periods with no calling)
- Include vessel predictions as features (from Notebook 5)

### Feature Engineering for Fish Models
- Use reduced acoustic index set from Notebook 3
- Include environmental variables and temporal features
- Add vessel probability predictions as feature
- Create species-specific environmental interactions

### Model Training and Validation
- Temporal blocked cross-validation with 2-week blocks
- Species-specific performance metrics (accuracy, weighted kappa)
- Feature importance analysis by species
- Model interpretability assessment

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

## Notebook 7: Model Validation and Ecological Assessment

**Purpose**: Comprehensive validation of models against known ecological patterns  
**Key Outputs**: Model validation report and ecological interpretation

### Ecological Validation
- Do predicted patterns match known fish biology?
- Are seasonal patterns realistic?
- Do environmental relationships make sense?
- How do predictions perform during extreme conditions?

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

## Notebook 8: Results Synthesis and Future Directions

**Purpose**: Synthesize results and establish framework for full study expansion  
**Key Outputs**: Publication-ready results and roadmap for full study

### Results Synthesis
- Key findings summary from MVP analysis
- Model performance comparison across approaches
- Ecological insights gained from acoustic indices
- Limitations and areas for improvement

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

This MVP approach will:

1. **Validate Core Methodology**: Demonstrate that acoustic indices can effectively predict fish calling patterns
2. **Establish Baseline Performance**: Quantify prediction accuracy and compare with traditional SPL approaches
3. **Identify Key Indices**: Determine which acoustic indices are most informative for marine soundscape analysis
4. **Create Reproducible Framework**: Develop modular analysis pipeline for expansion to full study
5. **Generate Ecological Insights**: Document fish calling patterns and environmental relationships using automated methods

The modular structure will make it easy to expand to the full study design (including dolphins and more complex vessel analysis) once the core methodology is validated and refined.