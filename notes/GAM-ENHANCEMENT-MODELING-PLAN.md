# GAM Enhancement Modeling Plan for 2D Probability Surfaces

## Background & Motivation

Current 2D probability surface approach uses:
1. **Kernel Density Estimation (KDE)** for baseline seasonal/daily patterns
2. **Simple enhancement factors** based on local detection rates
3. **Cross-station validation** for transferability testing

**Gap identified**: Current enhancement step doesn't fully leverage available environmental/acoustic features at test sites during deployment.

## Proposed Enhancement: GAM-Based Feature Integration

### Core Concept
Replace simple enhancement factors with **statistically robust feature-based adjustments** that can incorporate test-site conditions during real deployment.

### Model Framework

#### Baseline + Enhancement Structure:
```
P_final(day, hour) = P_baseline(day, hour) × f_enhancement(features)
```

Where:
- `P_baseline`: Current KDE-based 2D probability surface 
- `f_enhancement`: GAM-derived adjustment factor using available features

#### GAM Enhancement Model:
```r
# Train on training stations
enhancement_gam <- gam(
  local_rate_ratio ~ s(temperature) + s(spl) + s(acoustic_indices) + 
                     s(day_of_year, k=20) + s(hour_of_day, k=12),
  family = Gamma(link = "log"),  # multiplicative effects
  data = training_data
)

# Apply to test station
enhancement_factor <- predict(enhancement_gam, newdata = test_site_conditions)
final_prob <- baseline_surface * enhancement_factor
```

## Four-Way Feature Comparison Integration

Test all four feature scenarios within the GAM framework:

1. **ENV**: `gam(ratio ~ s(temp) + s(depth) + temporal_terms)`
2. **ENV+SPL**: `gam(ratio ~ s(temp) + s(depth) + s(spl) + temporal_terms)`  
3. **ENV+SPL+IDX**: `gam(ratio ~ s(temp) + s(depth) + s(spl) + s(acoustic_indices) + temporal_terms)`
4. **IDX**: `gam(ratio ~ s(acoustic_indices) + temporal_terms)`

## Why GAMs for This Application

### Advantages Over Current Approach:
- **Uses test-site features**: Can incorporate contemporaneous environmental/acoustic conditions
- **Smooth relationships**: Captures non-linear feature effects
- **Uncertainty quantification**: Provides confidence intervals for enhancement factors
- **Interpretable**: Can visualize how each feature modifies baseline probabilities
- **Statistically principled**: Standard ecological modeling approach

### Addresses Current Limitations:
- Current enhancement uses only local detection density from training data
- No principled way to incorporate test-site environmental conditions
- Limited ability to quantify uncertainty in enhancement factors

## Implementation Strategy

### Phase 1: Enhanced Feature Integration
1. Fit GAM enhancement models on training station combinations
2. Generate enhancement factors for test stations using their actual feature values
3. Compare performance against current simple enhancement approach

### Phase 2: Four-Way Systematic Comparison
1. Train GAM enhancement models for each feature scenario (ENV, ENV+SPL, etc.)
2. Test cross-station performance for all scenarios
3. Quantify improvement from acoustic indices using statistically robust framework

### Phase 3: Validation & Comparison
1. Compare GAM-enhanced approach vs current KDE approach
2. Test transferability across all station combinations
3. Evaluate practical performance (detection efficiency at 20% effort)

## Expected Outcomes

### If GAMs Improve Performance:
- Validates that incorporating test-site features adds value
- Provides statistically robust framework for four-way comparison
- Enables uncertainty quantification for guidance system

### If GAMs Don't Improve Performance:
- Validates that simple KDE approach captures most available signal
- Demonstrates that complex feature relationships don't add practical value
- Supports current approach as optimal given available data

## Technical Considerations

### Temporal Structure:
- Include `s(day_of_year, hour_of_day)` interaction terms if needed
- Consider temporal autocorrelation with `correlation = corAR1()` if appropriate

### Cross-Station Framework:
- Maintains current spatial validation approach
- Tests whether feature relationships transfer across locations

### Feature Selection:
- Use existing Phase 2 mutual information results for acoustic index selection
- Compare different smoothing approaches for environmental variables

## Integration with Current Pipeline

This enhancement preserves the core 2D probability surface insight while:
- Adding statistical rigor to feature integration
- Enabling test-site feature utilization during deployment  
- Providing systematic framework for acoustic vs environmental comparison
- Maintaining interpretability and practical applicability

## Next Steps for Implementation

1. **Design GAM enhancement models** for each feature scenario
2. **Implement training/testing pipeline** maintaining cross-station validation
3. **Compare performance** against current KDE-only approach
4. **Evaluate practical impact** on detection efficiency and effort reduction
5. **Document methodology** for publication-ready analysis

---

*This plan builds on the successful 2D probability surface discovery while addressing the limitation of not using available test-site features during deployment. The GAM framework provides a principled way to incorporate contemporaneous environmental/acoustic conditions while maintaining the guidance-focused approach that makes this method practically valuable.*