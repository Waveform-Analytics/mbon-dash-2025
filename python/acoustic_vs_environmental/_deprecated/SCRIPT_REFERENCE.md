# Acoustic vs Environmental Analysis - Script Reference

## Overview
This pipeline analyzes the predictive value of acoustic indices versus environmental features for marine species detection, with a focus on temporal relationships that traditional ML approaches may miss.

## Scripts Summary

### Core Pipeline Scripts

#### **01_data_loading.py**
**Purpose**: Foundation data preparation
- Loads acoustic indices, species detections, and environmental data
- Aggregates all data to 2-hour intervals to match detection timing
- Creates biological target variables (any_activity, high_activity, etc.)
- Merges datasets and handles data quality issues
- **Output**: `data_01_aligned_2021.csv` - clean aligned dataset for all analysis

#### **02_baseline_comparison.py**
**Purpose**: Initial feature selection and baseline performance
- Performs mutual information analysis to rank acoustic vs environmental features
- Selects top 10 acoustic indices based on biological prediction power
- Tests baseline model performance (acoustic vs environmental features)
- **Output**: `selected_acoustic_indices.csv`, mutual information rankings

#### **03_temporal_features.py**
**Purpose**: Advanced temporal feature engineering
- Creates rolling window statistics (4h, 12h, 24h periods)
- Generates lag features (historical values)
- Builds trend features (slopes, changes over time)
- Adds temporal context (hour, day, month patterns)
- **Output**: `output/temporal_features_dataset.csv` - enhanced dataset with 300+ features

#### **04_advanced_modeling.py**
**Purpose**: Complex machine learning models
- Tests advanced algorithms (Random Forest, XGBoost, Neural Networks)
- Uses the temporally-enhanced dataset from Phase 3
- Cross-validation with multiple model types
- **Output**: Advanced model performance metrics

#### **05_species_specific_analysis.py** ⭐
**Purpose**: Species-specific modeling (CORRECTED - no data leakage)
- **CRITICAL**: Removes biological context features that caused data leakage
- Tests acoustic vs environmental value for individual species
- Species-specific model performance comparison
- **Output**: `output/phase5_species_comparison.csv` - corrected species-specific results
- **Status**: This is the MAIN analysis referenced in `FINAL_CORRECTED_ANALYSIS.md`

### Discovery & Analysis Scripts

#### **06_simple_correlation_check.py** 🔍
**Purpose**: Validates visual pattern observations
- **KEY DISCOVERY**: Confirms strong temporal correlations (r=0.5-0.7) between acoustic indices and species
- Tests ADI vs Spotted seatrout correlation specifically
- Explains why ML analysis missed visual patterns
- **Output**: `visual_pattern_correlation_check.csv`
- **Finding**: Traditional ML shuffles temporal structure, masking synchrony patterns

#### **07_temporal_synchrony_analysis.py** 🎯
**Purpose**: Comprehensive temporal pattern analysis with dimension reduction
- Multi-species correlation matrix analysis
- PCA and clustering of acoustic indices
- Identifies "acoustic signatures" for each species
- Compares signature patterns between species
- **Output**: Correlation matrices and acoustic signatures by station
- **Goal**: Bridge from temporal synchrony to predictive modeling

#### **08_temporal_aware_models.py** ⚠️
**Purpose**: Attempted temporal-aware ML models (LESSONS LEARNED)
- Creates chronological train/test splits (no random shuffling)
- Builds lag features and cross-correlation features
- Comprehensive data leakage protection
- **Results**: Mixed - worked for vessels (+14% F1) but failed for fish (-93% to -100%)
- **Critical insight**: Training on peak seasons (spring/summer) and testing on winter silence is biologically unrealistic
- **Lesson**: Cross-seasonal prediction doesn't work; need season-aware approaches
- **Status**: Kept for reference, but approach was flawed for the biological question

#### **09_detection_guidance.py** ⭐⭐⭐
**Purpose**: Manual Detection Guidance System (MAJOR SUCCESS)
- **Use Case 2**: Guide manual detection efforts within appropriate seasons
- Builds 2D probability surfaces using kernel density estimation (day-of-year × time-of-day)
- Cross-station validation shows strong generalization across sites
- **Results**: 60-87% detection efficiency while reducing manual effort by 80%
- **Best performers**: Silver perch (86.6% efficiency), Oyster toadfish (AUC=0.944)
- **Innovation**: Works WITH seasonal patterns rather than against them
- **Output**: Comprehensive Quarto report with visualizations and implementation guidance

### Utility Scripts

#### **utils/data_utils.py**
**Purpose**: Data loading utilities
- `CleanDataLoader` class for consistent data loading
- Handles acoustic indices, detections, and environmental data
- Used by all main pipeline scripts

## Key Findings Summary

### **Traditional ML Results** (Phase 5)
- Environmental features sufficient for 80% of species (51-86% F1 scores)
- Only Atlantic croaker and vessels benefit meaningfully from acoustic indices
- Water temperature is the dominant predictor

### **Temporal Synchrony Discovery** (Phase 6)
- **Strong temporal correlations found**: 20+ acoustic indices with |r| > 0.5 for spotted seatrout
- **ADI correlation with spotted seatrout**: r = -0.586 (highly significant)
- **ML vs Visual discrepancy explained**: Cross-validation destroys temporal structure

### **Scientific Implications**
1. Acoustic indices ARE biologically meaningful (strong temporal synchrony)
2. Traditional ML approaches mask temporal relationships
3. Visual pattern analysis captures ecosystem-level coordination
4. Need temporal-aware ML approaches for acoustic ecology

## Usage Guide

### **For Initial Analysis**
```bash
# Complete pipeline from scratch
uv run 01_data_loading.py
uv run 02_baseline_comparison.py  
uv run 03_temporal_features.py
uv run 05_species_specific_analysis.py  # Main corrected results
```

### **For Visual Pattern Investigation**
```bash
# Quick correlation check
uv run 06_simple_correlation_check.py

# Comprehensive temporal analysis
uv run 07_temporal_synchrony_analysis.py
```

### **For Results Review**
- **Main Results**: `FINAL_CORRECTED_ANALYSIS.md`
- **Species Performance**: `output/phase5_species_comparison.csv`
- **Temporal Correlations**: `visual_pattern_correlation_check.csv`
- **🎆 Phase 9 SUCCESS**: `Phase9_Detection_Guidance_Report.html` (comprehensive report)

### **For Practical Implementation**
```bash
# Run the successful detection guidance system
uv run 09_detection_guidance.py

# View comprehensive results report
open Phase9_Detection_Guidance_Report.html
```

## File Dependencies

```
01_data_loading.py → data_01_aligned_2021.csv
                  ↓
02_baseline_comparison.py → selected_acoustic_indices.csv
                         ↓
03_temporal_features.py → output/temporal_features_dataset.csv
                       ↓
05_species_specific_analysis.py → FINAL_CORRECTED_ANALYSIS.md

06_simple_correlation_check.py ← data_01_aligned_2021.csv (independent)
07_temporal_synchrony_analysis.py ← data_01_aligned_2021.csv (independent)
```

## Next Steps

### **Lessons from Phase 8**
Phase 8 revealed that cross-seasonal prediction (summer → winter) is biologically unrealistic for fish species. The approach needs to be refocused from "predictive modeling" to "detection guidance within appropriate seasons."

### **🎆 COMPLETED: Use Case 2 - Manual Detection Guidance (Phase 9)**
**MAJOR SUCCESS!** Built season-aware detection guidance system with impressive results:

✅ **2D probability surfaces**: KDE-based day-of-year × time-of-day modeling  
✅ **Cross-station validation**: Strong generalization across monitoring sites  
✅ **80% time savings**: Reduce manual effort while maintaining detection sensitivity  
✅ **Species-specific performance**: 60-87% detection efficiency for most species  
✅ **Practical implementation**: Ready for operational deployment

### **Future Applications**
- **Use Case 1**: Semi-real-time monitoring during active seasons
- **Use Case 3**: Annual soundscape comparison and trend detection
- **Biological context integration**: Use known spawning seasons as features, not obstacles

## Notes

- **Phase 4** outputs contain data leakage - use Phase 5 results instead
- **Phase 6** discovered the key insight about temporal relationships
- **Phase 7** provides the framework for temporal-aware predictive modeling
- Visual pattern analysis was scientifically validated - trust your observations!