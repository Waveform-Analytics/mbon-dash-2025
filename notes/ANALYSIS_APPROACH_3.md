# Analysis Approach 3: Automated Multi-Species Acoustic Index Analysis

## Executive Summary

We need to systematically analyze relationships between 50-60 acoustic indices and 7-8 detection types (including fish, dolphins and vessels) to identify which acoustic features best predict different types of biological activity. This document outlines an automated pipeline to efficiently screen ~500 potential combinations and focus detailed analysis on the most promising relationships.

## Data Structure

### Input Data
- **Manual Detections**: Every two hours, annotations were logged for a 2-minute segment of acoustic data. There's presence/intensity data for 7-8 detection types (fish, dolphins, vessels).
  - Fish use the Intensity scale: 0 (absent), 1 (single call), 2 (multiple calls), 3 (chorus)
  - Dolphins use call counts. 
  - Vessels use presence/absence (0/1)
  - Each species has different temporal patterns (seasonal, diel, lunar)
  - **Overall Fish Presence**: Aggregate measure across all species (treat as additional "species")
  
- **Acoustic Indices**: 50-60 indices calculated hourly
  - Many are correlated (redundant information)
  - Different categories: complexity, diversity, frequency, energy, bioacoustic
  - Full temporal coverage for 2021

- **Environmental Data**: Temperature and depth at each station

## Analysis Pipeline

### Phase 1: Data Preparation and Reduction

**Step 1.1: Create Overall Fish Presence Variable**
```python
# Aggregate all species into overall fish presence
fish_presence = {
    'intensity': detections[species_columns].max(axis=1),  # Max intensity across species
    'diversity': detections[species_columns].gt(0).sum(axis=1),  # Number of species present
    'total_activity': detections[species_columns].sum(axis=1)  # Sum of all intensities
}
# Treat this as an additional "species" in all analyses
```

**Step 1.2: Reduce Acoustic Indices**
Three approaches to choose from:

**Option A: Correlation-Based Reduction**
- Group indices with correlation > 0.85
- Select most representative from each group
- Expected output: 10-15 indices from 60

**Option B: Category-Based Selection**
- Pick 2-3 best performing indices from each category
- Categories: Complexity (ACI, ADI), Diversity (H, EAS), Bioacoustic (BI, BGNt), etc.
- Expected output: 12-18 indices

**Option C: PCA with Temporal Features**
- Combine acoustic indices with temporal markers (hour, month)
- Apply PCA to preserve some temporal context
- Use top 10 components

### Phase 2: Automated Screening

**Step 2.1: Quick Performance Metrics**
For each species × index combination, calculate:
1. **Correlation**: Basic Spearman correlation with intensity
2. **Discrimination**: Effect size between quiet (0) and chorus (3)
3. **Detection Rate**: % of high-intensity events with acoustic anomaly
4. **Lead Time**: Hours of advance warning before intensity increases

**Step 2.2: Screening Matrix Generation**
```python
screening_results = pd.DataFrame()
species_list = ['silver_perch', 'spotted_seatrout', ..., 'overall_fish']

for species in species_list:
    for index in reduced_indices:
        screening_results.loc[species, index] = {
            'correlation': calculate_correlation(species, index),
            'discrimination': calculate_effect_size(species, index),
            'detection_rate': calculate_detection_rate(species, index),
            'mean_lead_time': calculate_lead_time(species, index)
        }
```

**Step 2.3: Identify Top Performers**
- Top 3 indices per species
- Top 3 species per index
- Universal performers (good across multiple species)

### Phase 3: Detailed Transition Analysis

Focus only on promising combinations from screening.

**Step 3.1: Transition Event Extraction**
```python
transition_types = {
    'rapid_onset': (0, 3),  # Silence to chorus
    'gradual_buildup': (0, 1, 2, 3),  # Progressive increase
    'cessation': (3, 0),  # Chorus to silence
    'failed_buildup': (0, 1, 2, 1, 0)  # Buildup without chorus
}

for species in top_species:
    transitions = extract_transitions(species, transition_types)
```

**Step 3.2: Acoustic Signatures**
For each transition:
- Extract acoustic patterns 12 hours before/after
- Identify consistent pre-transition changes
- Calculate reliability of detection

**Step 3.3: Temporal Pattern Analysis**
- Hour-of-day effects on index-species relationships
- Seasonal variations in acoustic responses
- Lunar phase influences

### Phase 4: Pattern Discovery and Synthesis

**Step 4.1: Species Grouping**
Group species by acoustic response patterns:
- Continuous callers vs burst callers
- Nocturnal vs diurnal vs crepuscular
- Seasonal vs year-round

**Step 4.2: Index Categorization**
Identify which indices work best for:
- Chorus detection
- Single species detection
- Overall biodiversity
- Transition prediction

**Step 4.3: Predictive Model Building**
For most promising combinations:
- Build simple threshold models
- Test on held-out time periods
- Calculate real-world performance metrics

## Automated Output Generation

### Visualization Suite

1. **Screening Heatmap**: Species × Index performance matrix
2. **Species Profiles**: Individual reports for each species showing:
   - Temporal calling patterns
   - Best performing indices
   - Transition signatures
   - Detection lead times

3. **Index Report Cards**: For each top index showing:
   - Which species it detects well
   - Temporal stability
   - Environmental sensitivity

4. **Transition Gallery**: Before/after acoustic patterns for different transition types

### Summary Statistics Table

| Species | Best Index | Correlation | Lead Time | Detection Rate | Optimal Threshold |
|---------|------------|-------------|-----------|----------------|-------------------|
| Overall Fish | BI | 0.72 | 4h | 78% | BI > 8.5 |
| Silver Perch | BGNt | 0.68 | 6h | 82% | BGNt > -20 |
| Spotted Seatrout | ADI | 0.65 | 3h | 71% | ADI > 2.1 |
| ... | ... | ... | ... | ... | ... |

### Decision Rules

Generate simple, deployable rules:
- "If BI > 8.5 between 6pm-midnight in April-May → Silver perch chorus likely in 4-6 hours"
- "If ADI drops below 1.8 after being >2.5 → Spotted seatrout calling ending"

## Implementation Workflow

### Week 1: Setup and Screening
- Day 1-2: Data preparation, index reduction
- Day 3-4: Run automated screening
- Day 5: Review results, identify top performers

### Week 2: Deep Dive Analysis
- Day 1-2: Transition analysis for top combinations
- Day 3-4: Temporal pattern analysis
- Day 5: Environmental correlation

### Week 3: Synthesis and Reporting
- Day 1-2: Pattern discovery across species
- Day 3-4: Build predictive rules
- Day 5: Generate final visualizations and report

## Code Structure

```
analysis/
├── data_prep/
│   ├── index_reduction.py
│   ├── species_aggregation.py
│   └── transition_extraction.py
├── screening/
│   ├── correlation_analysis.py
│   ├── discrimination_metrics.py
│   └── screening_matrix.py
├── detailed_analysis/
│   ├── transition_signatures.py
│   ├── temporal_patterns.py
│   └── lead_time_optimization.py
├── visualization/
│   ├── species_profiles.py
│   ├── index_report_cards.py
│   └── performance_heatmaps.py
└── main_pipeline.py
```

## Success Metrics

### Minimum Viable Success
- Identify 3-5 indices that reliably detect overall fish presence (>70% detection rate)
- Find species-specific acoustic signatures for at least 50% of species
- Demonstrate 2-6 hour lead time for chorus events

### Ideal Outcome
- Automated monitoring rules for all major species
- 80%+ detection rate for high-intensity calling events
- Clear understanding of which indices work for which biological patterns
- Deployable real-time monitoring system design

## Key Advantages of This Approach

1. **Comprehensive**: Tests all combinations systematically
2. **Efficient**: Screens quickly, focuses effort on promising combinations
3. **Scalable**: Easy to add new species or indices
4. **Practical**: Generates deployable detection rules
5. **Scientific**: Preserves temporal patterns and ecological context

## Next Steps

1. Implement index reduction algorithm
2. Build screening pipeline
3. Run initial screening on 2021 data
4. Review results with domain experts
5. Refine analysis based on biological insights
6. Generate final detection rules and recommendations

## Critical Questions to Address

1. Should we analyze stations separately or combined?
2. How do we handle species that are rare (few detection hours)?
3. What's the minimum chorus duration to count as an "event"?
4. How do we validate findings without independent test data?
5. Should environmental variables be included in screening phase?

This automated approach will efficiently identify the most promising acoustic indicators for each species while preserving the temporal and ecological context necessary for real-world deployment.