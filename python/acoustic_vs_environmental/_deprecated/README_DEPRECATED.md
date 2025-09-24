# Deprecated Files

This folder contains files from previous iterations of the Marine Acoustic Discovery analysis that are no longer part of the active pipeline.

## Current Active Pipeline

The current streamlined pipeline uses only these scripts:
- `01_data_loading.py` - Data loading and verification
- `02_baseline_comparison.py` - Baseline ML analysis showing limitations
- `06_temporal_correlation_analysis.py` - Temporal correlation analysis
- `09_detection_guidance.py` - Detection guidance system
- `run_full_pipeline.py` - Master pipeline runner
- `Marine_Acoustic_Discovery_Report_v2.qmd` - Current report

## Deprecated Analysis Scripts

### Phase 3-8 Scripts (No longer used)
- `03_temporal_features.py` - Temporal feature extraction
- `04_advanced_modeling.py` - Advanced ML models
- `05_species_specific_analysis.py` - Species-specific analysis
- `06_simple_correlation_check.py` - Simple correlation checks
- `07_temporal_synchrony_analysis.py` - Temporal synchrony analysis
- `08_temporal_aware_models.py` - Temporal-aware models

These were part of the extensive ML experimentation phase that ultimately showed the limitations of traditional ML approaches for this problem.

### Old Reports
- `Marine_Acoustic_Discovery_Report.qmd/.html` - Previous version of main report
- `Phase9_Detection_Guidance_Report.qmd/.html/.pdf` - Standalone detection guidance report

### Utility Scripts
- `test_figures.py` - Figure testing
- `create_improved_temperature_figure.py` - Temperature figure generation
- `regenerate_key_figures.py` - Figure regeneration
- `prepare_netlify_deploy.py` - Netlify deployment prep
- `build_and_deploy_report.py` - Netlify build and deployment (replaced by GitHub Pages)

### Documentation
- `FINAL_CORRECTED_ANALYSIS.md` - Previous analysis documentation
- `PROJECT_SUMMARY.md` - Old project summary
- `SCRIPT_REFERENCE.md` - Script reference guide
- `DEPLOYMENT_STATUS.md` - Deployment status
- `TEMPERATURE_ANALYSIS_IMPROVED.md` - Temperature analysis notes

### Data Files
- `phase2_*.csv/.json` - Phase 2 results
- `selected_acoustic_indices.csv` - Selected indices
- `visual_pattern_correlation_check.csv` - Correlation check results

### Deployment Assets
- `netlify_deploy/` - Old Netlify deployment folder

## Why These Files Were Deprecated

The analysis evolved from a complex multi-phase ML approach to a focused, guided approach that emphasizes:
1. Acknowledging ML limitations
2. Providing practical detection guidance
3. Clear temporal correlation analysis
4. Streamlined, reproducible pipeline

These deprecated files represent important research steps but are no longer needed for the current analysis approach.

---
*Files moved to deprecated folder: September 24, 2024*