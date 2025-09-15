# MVP Roadmap: Acoustic Indices as Proxies for Manual Fish Detection

## Project Overview

This MVP validates whether acoustic indices can serve as reliable proxies for species presence/absence without requiring extensive manual detection efforts. Using 2021 May River data with manual detections as ground truth, we test if acoustic indices alone can provide actionable biological information for future deployments where manual detection is impractical. The analysis builds upon insights from Transue et al. (2023) Charleston Harbor study, where biological patterns were masked by anthropogenic noise in traditional SPL approaches, by testing acoustic indices in a less urbanized estuary.

**Core Research Question**: Can acoustic indices serve as effective biological screening tools and detect community-level fish patterns at scales impossible with manual detection?

**Scope**: Fish community analysis demonstrating acoustic indices as screening tools for targeted manual effort and continuous pattern detection
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

## Notebook 5: Anthropogenic Impact Assessment

**Purpose**: Document vessel impacts on acoustic indices and demonstrate indices work despite anthropogenic noise  
**Key Outputs**: Evidence that indices maintain biological signal even during vessel periods

### Core Analysis
- Basic vessel presence/absence analysis using existing manual vessel data
- Cohen's d effect sizes for vessel impacts on reduced index set
- Before/during/after vessel comparisons for biological indices
- Station-specific vessel impact patterns

### Robustness Assessment  
- Do fish-calling patterns persist during vessel periods?
- Which indices are most/least affected by vessel presence?
- Environmental vs anthropogenic drivers of index variation
- Seasonal differences in vessel impact severity

### Key Validation Questions
- Can indices detect biological patterns even with vessel noise?
- Are community-level fish patterns robust to anthropogenic interference?
- Which temporal scales minimize vessel impacts?

### Static Plots to Generate
- Before/during/after vessel box plots for key indices
- Fish calling patterns: vessel vs non-vessel periods
- Index robustness rankings (vessel sensitivity analysis)
- Seasonal variation in anthropogenic impacts
- Station comparison of vessel effects

**Output**: Documentation that indices provide biological signal despite anthropogenic noise

---

## Notebook 6: Community Pattern Detection and Biological Screening

**Purpose**: Demonstrate that acoustic indices can detect community-level fish patterns and identify periods of biological interest  
**Key Outputs**: Evidence that indices serve as effective biological screening tools for continuous monitoring

### Community-Level Analysis
- **Total fish activity prediction** (sum across all species rather than individual species)
- **Binary presence/absence modeling** (active vs inactive periods) rather than 0-3 intensity scale
- **Seasonal pattern detection** using indices alone (spawning periods, activity peaks)
- **Periods of biological interest classification** for targeted manual analysis

### Model Architecture (Simplified)
- Focus on aggregate fish community activity rather than species-specific prediction
- Binary classification: high vs low biological activity periods
- Use reduced acoustic index set from Notebook 3
- Include environmental variables and temporal features as available

### Pattern Detection Analysis
- **Diel rhythm concordance**: Do indices capture same 24-hour patterns as manual detections?
- **Seasonal phenology**: Can indices identify spawning seasons and activity peaks?
- **Cross-station consistency**: Do patterns hold across different monitoring locations?
- **Temporal scales**: At what time scales do indices best capture biological patterns?

### Screening Tool Validation
- **Efficiency assessment**: How much manual effort could be saved by using indices to identify high-activity periods?
- **False positive/negative rates**: When do indices miss biological activity or suggest activity when none exists?
- **Threshold optimization**: What index values correspond to meaningful biological activity?

### Static Plots to Generate
- Community fish activity: predicted vs actual time series
- Seasonal pattern comparison (indices vs manual detections)
- Diel rhythm concordance analysis
- Screening efficiency assessment (effort reduction quantification)
- Cross-station pattern consistency
- Threshold sensitivity analysis for biological activity detection

**Output**: Evidence that indices effectively detect community patterns and serve as biological screening tools

---

## Notebook 7: Continuous Monitoring Validation

**Purpose**: Validate that acoustic indices enable effective continuous biological monitoring at ecosystem scales  
**Key Outputs**: Quantified evidence that indices provide continuous biological insights impossible with manual detection alone

### Key Validation Questions
- **Seasonal pattern detection**: Can indices identify spawning seasons and biological phenology?
- **Diel pattern preservation**: Do indices capture 24-hour biological rhythms?
- **Continuous vs snapshot monitoring**: What biological information is gained through continuous index monitoring vs 2-hour manual snapshots?
- **Minimum viable index set**: What is the smallest set of indices needed for reliable community pattern detection?

### Monitoring Efficiency Analysis
- **Temporal coverage comparison**: Continuous indices vs sparse manual detection
- **Pattern detection capability**: Biological events detected by indices but missed by manual sampling
- **Cross-station transferability**: Do index-based patterns generalize across monitoring locations?
- **Cost-benefit assessment**: Manual effort saved vs biological information retained

### Ecological Pattern Validation
- **Compare seasonal patterns**: Index-detected vs manually-detected biological activity peaks
- **Environmental relationship consistency**: Do temperature-activity relationships match between methods?
- **Community vs species patterns**: Where do indices excel (community) vs struggle (species-specific)?
- **Temporal scale optimization**: At what time scales are indices most informative?

### Static Plots to Generate
- Seasonal phenology: indices vs manual detection comparison
- Continuous monitoring advantages visualization
- Cross-station pattern transferability assessment
- Environmental-biological relationship concordance
- Monitoring effort efficiency analysis
- Minimum viable index set performance

**Output**: Validation that indices enable effective continuous biological monitoring with quantified advantages over manual-only approaches

---

## Notebook 8: Practical Implementation as Biological Screening Tools

**Purpose**: Synthesize evidence that acoustic indices serve as effective biological screening tools and continuous monitoring systems  
**Key Outputs**: Clear recommendations for integrating indices into marine monitoring programs

### Core Findings
- **"Can acoustic indices replace manual detection?"** - Quantified answer: "Not replace, but complement and guide"
- **Community-level accuracy**: Performance levels achievable for aggregate biological activity detection
- **Screening efficiency**: Manual effort reduction possible through index-guided targeted sampling  
- **Optimal temporal scales**: Time scales at which indices are most/least informative for biological patterns
- **Minimum viable index set**: The smallest set of indices (from 18 reduced set) needed for effective screening

### Method Comparison & Integration Strategy
- **Acoustic indices vs traditional SPL approaches**: Advantages for biological pattern detection
- **Hybrid monitoring frameworks**: Combining continuous index monitoring with targeted manual detection
- **Cost-benefit analysis**: Long-term monitoring efficiency gains
- **Implementation practicality**: Computational requirements, deployment considerations

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

This MVP will definitively answer: **"Can acoustic indices serve as effective biological screening tools and enable continuous community-level monitoring?"**

Specific deliverables:

1. **Community Pattern Detection**: Quantified ability to detect aggregate fish community activity and seasonal patterns using indices
2. **Biological Screening Performance**: Efficiency of indices in identifying periods of high biological activity for targeted manual analysis
3. **Minimum Viable Index Set**: The smallest subset (from 18 reduced indices) providing maximum community-level biological information
4. **Continuous Monitoring Validation**: Evidence that indices capture biological patterns at temporal scales impossible with manual detection
5. **Practical Integration Framework**: Guidelines for hybrid monitoring combining continuous indices with strategic manual detection

Key advantages over manual-only detection:
- **Continuous biological pattern detection** (not just 2-hour snapshots)
- **Ecosystem-scale monitoring** with minimal ongoing human effort
- **Intelligent manual effort allocation** guided by index-detected high-activity periods
- **Robust to anthropogenic noise** while maintaining biological signal
- **Cost-effective for long-term community monitoring**

This validation establishes acoustic indices as **biological screening tools** that dramatically improve monitoring efficiency while preserving ecological insights, directly addressing the scalability limitations of manual-only approaches identified by Transue et al. (2023).