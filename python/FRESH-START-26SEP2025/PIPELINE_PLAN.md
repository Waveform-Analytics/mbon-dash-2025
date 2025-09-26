# Fresh Start Analysis Pipeline: Acoustic Indices vs Environmental Data
## 26 September 2025

## 🎯 Core Research Questions

**Primary**: Do acoustic indices provide community biological information beyond what environmental data and SPL can already tell us? (particularly focused on species diversity / richness, rather than specific species detection)

**Secondary**: Can we develop a systematic workflow to determine which acoustic index combinations reflect biological patterns in marine ecosystems?

**Target Audience**: Environmental managers and passive acoustic monitoring community

## 📋 Pipeline Overview

This pipeline implements a focused, systematic approach to answer our key question while avoiding rabbit holes. Each script has a single clear purpose and builds directly toward answering our core research questions.

### Design Principles
- **Question-focused**: Every analysis directly addresses the core research questions
- **Systematic comparison**: Environmental-only vs Environmental+SPL vs Environmental+SPL+Indices vs Indices-only
- **Community metrics**: Focus on total fish intensity, species richness, activity levels (not individual species)
- **Cross-validation**: Station-based validation ensures transferability
- **Feature reduction**: Remove redundant indices, focus on distinct signal types
- **Reproducible**: Clear data flows, standardized outputs, minimal dependencies

---

## 🔄 Pipeline Scripts Structure

### Script 1: `01_data_preparation.py`
**Purpose**: Load, align, and clean all data streams
**Key Question**: What data do we have and is it analysis-ready?

**Tasks**:
- Load all data sources (acoustic indices, manual detections, environmental, SPL)
- Temporal alignment to 2-hour intervals (matching manual detection frequency)
- Quality assessment and outlier detection
- Standardize column names and data types
- Generate basic data coverage statistics
- note that I have adjust the metadata file, det_column_names.csv (located in data/raw/metadat folder) to indicate that we want to "keep" a few more species/detection types than what we had included before (since we are now more focused on the community/biodiversity rather than individual species). 

**Outputs**:
- `data/processed/aligned_dataset_2021.parquet` - Complete aligned dataset
- `data/processed/data_quality_report.json` - Data coverage and quality metrics
- `figures/01_data_coverage_summary.png` - Temporal coverage visualization
- `figures/01_missing_data_heatmap.png` - Missing data patterns

**Reference Sources**: 
- `python/scripts/notebooks/01_data_prep.py` - Data loading patterns
- `python/scripts/notebooks/02_temporal_aggregation.py` - Temporal alignment approach

---

### Script 2: `02_feature_reduction.py`
**Purpose**: Reduce acoustic indices to non-redundant set focused on biological signal
**Key Question**: Which indices provide unique information vs redundant signal?

**Tasks**:
- Correlation analysis of all ~60 acoustic indices
- Hierarchical clustering to identify functional groups
- Remove highly correlated indices (>0.85 correlation threshold)
- Prioritize indices with low vessel noise impact
- Select representatives from each functional cluster
- Validate reduction preserves biological signal coverage

**Outputs**:
- `data/processed/reduced_acoustic_indices.parquet` - Final index set (~15-20 indices)
- `data/processed/index_reduction_report.json` - Selection rationale and statistics
- `figures/02_index_correlation_matrix.png` - Before/after reduction
- `figures/02_index_clustering_dendrogram.png` - Functional groupings
- `figures/02_vessel_impact_assessment.png` - Index robustness to vessel noise
- * ensure that we have an easy-to-read (for humans) summary of # of clusters, and which indices were included in each cluster, and which was selected as the representative.

**Reference Sources**:
- `python/scripts/notebooks/03_acoustic_index_reduction.py` - Index reduction methods
- `python/acoustic_vs_environmental/01_data_loading.py` - Correlation analysis patterns

---

### Script 3: `03_community_metrics.py`
**Purpose**: Define and compute community-level biological targets
**Key Question**: What biological patterns do we want to predict?

**Tasks**:
- Calculate total fish calling intensity (sum across species: only fish for now, but later we may try to generate a similar scale for dolphins)
- Compute species richness (number of unique species calling) - note that I included "vessel" and "unknown anthropogenic" in my manual detection types to "keep". I am not quite certain whether to keep those include or not, and probably at some point want to actually remove known vessel/anthro types and compare results with those removed to determine whether they are very detrimental to the modeling outcomes. oops - perhaps that's covered by the last bullet point in this section. 
- Generate activity level percentiles (any activity, 75th, 90th percentiles)
- Create binary activity indicators for different thresholds (e.g., any activity > 0, activity > 75th percentile, activity > 90th percentile)
- Assess temporal patterns in community metrics
- Document vessel impact on community metrics

**Outputs**:
- `data/processed/community_metrics.parquet` - All target variables
- `data/processed/community_patterns_summary.json` - Temporal pattern statistics
- `figures/03_community_temporal_patterns.png` - Seasonal/diel patterns
- `figures/03_community_metrics_distributions.png` - Target variable distributions
- `figures/03_vessel_impact_on_biology.png` - Community metrics with/without vessels

**Reference Sources**:
- `python/scripts/notebooks/04_fish_and_indices_patterns.py` - Community pattern analysis
- `python/scripts/notebooks/06_community_pattern_detection.py` - Target variable definitions

---

### Script 4: `04_feature_importance_analysis.py`
**Purpose**: Assess feature importance using methods appropriate for seasonal data
**Key Question**: Which feature categories matter most beyond the seasonal/diel baseline?

**Tasks**:
- **Conditional mutual information**: I(feature; biology | season, hour, station) - the key metric for your team's bar chart
- Compare ENV vs ENV+SPL vs ENV+SPL+IDX vs IDX-only using conditional MI
- **Effort-lift analysis**: How much does adding each feature category improve detection efficiency at 20% effort?
- Cross-station validation of conditional importance rankings
- Identify consistently important vs site-specific features
- Document which indices provide information beyond environmental + seasonal patterns

**Rationale**: Traditional MI/Boruta conflate seasonal patterns with "importance." Conditional MI asks: given we know it's May at 6am, how much does temperature/SPL/acoustic indices reduce uncertainty about fish activity?

**Outputs**:
- `data/processed/conditional_importance_results.parquet` - Conditional MI rankings by feature category
- `data/processed/effort_lift_analysis.json` - Detection efficiency improvements by feature type
- `figures/04_conditional_importance_comparison.png` - **The bar chart your team wants** - conditional MI by feature category
- `figures/04_effort_lift_curves.png` - Detection efficiency curves showing improvement from adding features
- `figures/04_cross_station_consistency.png` - Stability of conditional importance across stations

**Reference Sources**:
- `python/scripts/notebooks/06_02_standardized_feature_selection.py` - Feature selection methods
- `python/acoustic_vs_environmental/02_baseline_comparison.py` - Feature importance patterns

**Future Extensions**: For GAM implementation (Script 7), this conditional approach sets up:
- Partial deviance analysis (ΔAIC when adding features to seasonal GAM baseline)
- Smooth term significance testing while controlling for season/diel patterns
- Residual heatmaps showing before/after seasonal pattern removal

---

### Script 5: `05_2d_probability_surfaces.py`
**Purpose**: Implement and validate 2D probability surface approach
**Key Question**: Can we create actionable guidance for when biological activity is likely?

**Tasks**:
- Generate 2D KDE surfaces (day-of-year × hour-of-day) from manual detections
- Implement simple enhancement using local detection rates
- Cross-station validation of probability surfaces
- Test guidance system performance (detection efficiency at 20% effort)
- Compare surface quality with/without acoustic index enhancement
- Assess transferability across stations and seasons

**Outputs**:
- `data/processed/probability_surfaces/` - 2D surfaces for each community metric
- `data/processed/guidance_system_performance.json` - Detection efficiency metrics
- `figures/05_2d_probability_surfaces.png` - Visualization of key surfaces
- `figures/05_guidance_system_validation.png` - Efficiency vs effort curves
- `figures/05_cross_station_transferability.png` - Surface performance across stations

**Reference Sources**:
- `python/acoustic_vs_environmental/09_detection_guidance.py` - 2D surface implementation
- `python/acoustic_vs_environmental/06_temporal_correlation_analysis.py` - Pattern detection methods

---

### Script 6: `06_gam_enhancement_prototype.py` (Optional/Future)
**Purpose**: Prototype GAM-based enhancement of probability surfaces
**Key Question**: Can statistical modeling improve guidance system performance?

**Tasks**:
- Implement GAM enhancement framework from notes/GAM-ENHANCEMENT-MODELING-PLAN.md
- Train GAM models for each feature scenario
- Replace simple enhancement factors with GAM-derived adjustments
- Compare GAM-enhanced vs simple KDE approaches
- Test incorporation of test-site environmental conditions

**Outputs**:
- `data/processed/gam_enhanced_surfaces/` - GAM-enhanced probability surfaces
- `data/processed/gam_performance_comparison.json` - GAM vs simple enhancement
- `figures/06_gam_enhancement_validation.png` - Performance improvement assessment
- `figures/06_gam_feature_effects.png` - Statistical model interpretation

**Reference Sources**:
- `notes/GAM-ENHANCEMENT-MODELING-PLAN.md` - Complete GAM implementation plan
- GAM modeling literature and R/Python implementations

---

### Script 7: `07_synthesis_and_reporting.py`
**Purpose**: Generate final analysis report and key figures for paper
**Key Question**: What is the clear answer to our research questions?

**Tasks**:
- Synthesize results across all previous analyses
- Generate publication-ready figures
- Create summary statistics and effect size calculations
- Document methodology for reproducibility
- Generate executive summary for stakeholders
- Create interactive visualizations for dashboard

**Outputs**:
- `reports/final_analysis_report.html` - Comprehensive analysis report
- `figures/publication/` - High-quality figures for paper
- `data/processed/synthesis_results.json` - Key findings summary
- `dashboard/public/views/` - Interactive visualizations
- `reports/methodology_documentation.md` - Reproducibility guide

---

## 📊 Key Analysis Priorities

### Immediate Focus (Scripts 1-5)
1. **Data preparation and quality assessment** - Ensure solid foundation
2. **Feature reduction** - Focus on non-redundant acoustic indices
3. **Community metrics** - Define clear biological targets
4. **Systematic feature comparison** - Answer Neil's core question directly
5. **Probability surfaces** - Practical guidance system validation

### Future Enhancement (Script 6)
- GAM-based statistical modeling for enhanced predictive power

### Final Synthesis (Script 7)
- Clear answers to research questions with supporting evidence

---

## 🔧 Technical Implementation

### Dependencies
```python
# Core analysis
pandas, numpy, scipy, scikit-learn
matplotlib, seaborn, plotly

# Advanced modeling
statsmodels  # for GAM implementation if needed - MW: should we consider pyGAM?
uv  # for dependency management (user preference)

# Optional for GAM enhancement
rpy2, R packages: mgcv, ggplot2
```

### Data Flow
```
Raw Data → Script 1 → Aligned Dataset
         ↓
Aligned Dataset → Script 2 → Reduced Feature Set
                ↓
Feature Set + Targets → Scripts 3-6 → Analysis Results
                                    ↓
All Results → Script 8 → Final Report + Dashboard
```

### Output Structure
```
python/FRESH-START-26SEP2025/
├── data/
│   ├── processed/          # Analysis-ready datasets
│   └── results/           # Analysis outputs
├── figures/               # All generated plots
├── reports/               # Analysis reports
└── scripts/              # Pipeline scripts
```

### Standards
- **Path resolution**: Use DATA_ROOT pattern from existing marimo standards
- **File naming**: Descriptive names with script number prefix
- **Documentation**: Each script includes purpose, inputs, outputs, key findings
- **Version control**: Clear commit messages linking to specific research questions
- **Reproducibility**: All random seeds set, all parameters documented

---

## 🚀 Execution Plan

### Phase 1: Foundation (Scripts 1-3)
- Establish solid data foundation
- Define clear community targets
- Reduce acoustic indices to manageable set

### Phase 2: Core Analysis (Scripts 4-5)
- Answer the primary research question systematically
- Validate practical guidance system approach
- Document cross-station transferability

### Phase 3: Enhancement & Synthesis (Scripts 6-7)
- Explore advanced statistical approaches (GAM)
- Generate final report and publication materials
- Create dashboard visualizations

### Quality Gates
- After Script 3: Data quality assessment and community metrics validation
- After Script 5: Core research questions answered with evidence
- After Script 7: Publication-ready results and reproducible methodology

---

## 🎯 Success Criteria

### Primary Research Question Answer
Clear quantitative evidence for whether acoustic indices provide biological information beyond environmental data + SPL

### Practical Outcomes
1. **If indices add value**: Standardized workflow for marine index selection and application
2. **If indices don't add value**: Clear evidence to focus resources on environmental monitoring
3. **Either way**: Guidance for marine acoustic monitoring community

### Deliverables
- Peer-reviewed paper with clear methodology and results
- Interactive dashboard for community use
- Reproducible analysis pipeline for other datasets
- Clear recommendations for environmental managers

---

*This pipeline is designed to provide definitive answers to our core research questions while avoiding analytical rabbit holes. Each script builds systematically toward the final goal of determining whether acoustic indices provide valuable biological information beyond traditional environmental monitoring approaches.*
