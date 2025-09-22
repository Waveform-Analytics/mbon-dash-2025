# Acoustic vs Environmental Predictors: Exploratory Analysis Plan

## Objective
**Core Question**: Do acoustic indices provide meaningful predictive value for biological activity beyond what environmental variables already capture?

## Context & Motivation
- Current pipeline shows environmental features dominating predictions (temp lags MI ~0.17 vs acoustic indices MI ~0.09)
- But comparison is unfair: environmental features have rich temporal structure (18 lag/mean/change features) while acoustic indices are mostly "raw"
- Need systematic, methodologically sound comparison before investing in notebook pipeline refinements

## Key Methodological Issues Identified
1. **Temporal Feature Asymmetry**: Environmental data has lags/means, acoustic indices mostly don't
2. **Feature Selection Timing**: Currently using clustering-based reduction (60→18) before knowing which indices predict biology
3. **Data Processing Errors**: Keep hitting datetime/alignment issues that were already solved in notebook 2

## Analysis Strategy: Progressive Complexity

### Phase 1: Clean Baseline (Use Notebook 1 Outputs)
**Goal**: Fair baseline comparison without temporal complications
**Data**: Use cleaned `01_*_2021.parquet` files (post-cleaning, pre-temporal alignment)
**Approach**: 
- Load raw cleaned data from notebook 1 outputs
- Simple 2-hour aggregation matching detection intervals
- Compare raw acoustic indices vs raw environmental variables
- **No temporal features initially** - just current conditions

### Phase 2: Activity-Informed Index Selection  
**Goal**: Replace clustering-based reduction with biology-driven selection
**Approach**:
- Screen all ~60 acoustic indices against biological activity using mutual information
- Select top N (8-12) most predictive indices
- Compare this to notebook 3's clustering-based selection
- Document which approach selects better predictors

### Phase 3: Fair Temporal Feature Engineering
**Goal**: Create equivalent temporal complexity for both feature types
**Approach**:
- For top acoustic indices: create 1-3h lags, 6-12h means, 2-4h changes (matching env features)
- Ensure both acoustic and environmental have similar temporal feature counts (~15-20)
- Test raw vs temporal for both feature types

### Phase 4: Systematic Comparison
**Goal**: Definitive answer to acoustic vs environmental question
**Models**: Logistic Regression + Random Forest
**Scenarios**:
- Acoustic (raw) only
- Environmental (raw) only
- Acoustic + temporal only
- Environmental + temporal only  
- Combined (fair comparison)
**Validation**: Both standard CV and temporal CV (TimeSeriesSplit)

## Implementation Plan

### Scripts Organization
```
python/acoustic_vs_environmental/
├── 01_data_loading.py          # Clean data loading from notebook 1 outputs
├── 02_baseline_comparison.py    # Phase 1: Raw features comparison
├── 03_index_selection.py       # Phase 2: Biology-informed selection
├── 04_temporal_features.py     # Phase 3: Fair temporal engineering  
├── 05_final_comparison.py      # Phase 4: Systematic evaluation
└── utils/
    ├── data_utils.py           # Reusable data loading/cleaning functions
    ├── feature_utils.py        # Feature engineering utilities
    └── eval_utils.py           # Model evaluation utilities
```

### Success Metrics
- **Clear answer**: Do acoustic indices add >2% F1 improvement over environmental?
- **Feature counts**: Comparable temporal complexity (±20% feature count difference)
- **Validation consistency**: <5% difference between standard and temporal CV
- **Reproducibility**: Scripts run cleanly without datetime/alignment errors

### Expected Outcomes
1. **If acoustic indices add value**: Justify temporal feature engineering in notebooks
2. **If environmental dominates**: Focus notebook pipeline on environmental prediction + acoustic interpretation
3. **If comparable**: Develop combined modeling approach

### Integration Back to Notebooks
- **Best practices** from clean data loading → improve notebook 2
- **Feature selection insights** → revise notebook 3 reduction strategy  
- **Temporal modeling results** → refine notebook 6 approaches
- **Final recommendations** → update project documentation

## Timeline
- **Day 1**: Scripts 01-02 (data loading + baseline)
- **Day 2**: Scripts 03-04 (selection + temporal features)  
- **Day 3**: Script 05 + analysis (final comparison)
- **Day 4**: Integration planning for notebooks

## Key Advantages of This Approach
1. **Speed**: Python scripts run faster than notebooks for exploration
2. **Clean slate**: Avoid accumulated technical debt from notebook pipeline
3. **Methodological rigor**: Systematic progression from simple to complex
4. **Reusability**: Utils can be imported into notebooks later
5. **Focus**: Answer the specific acoustic vs environmental question first