# Analysis Approach 2: Real-Time Acoustic Monitoring System

## Executive Summary

We're pivoting from trying to replicate manual species detection (62% accuracy) to building an early warning system that flags unusual acoustic events for further investigation. This approach better aligns with real-world monitoring needs and leverages the strengths of acoustic indices. (Run this by Liz to start - does this still align with the goals of the project? I think this is an interesting and doable direction but does Neil agree?)

## The Problem We're Actually Solving

**Original approach**: Can we predict fish presence from acoustic indices?
- Result: 62% accuracy using Random Forest
- Issue: Treated time series data as independent points
- Missing: Temporal patterns, station differences, environmental context

**Refined goal**: Can we detect unusual acoustic events that indicate something biologically interesting is happening?
- Use acoustic indices as anomaly detectors
- Provide early warning for marine events
- Flag events for manual investigation
- Work alongside (not replace) emerging AI species detection

## Why Our Current Approach Falls Short

I mean, it's not that dramatic - we only worked on the current predictive model for about 2 days. But it's still a gap.

Our current models ignore critical dependencies:
- **Temporal**: Hour-to-hour correlation, diel patterns, lunar cycles, seasonal patterns
- **Spatial**: Each station has different species, depths, and acoustic environments  
- **Environmental**: Temperature and depth changes drive biological activity
- **Biological**: Spawning events last days/weeks, not isolated hours

Treating each hour as independent is like analyzing a movie by looking at random frames.

## The Opportunity: Acoustic Anomaly Detection

Instead of asking "are fish present?" we should ask "is something unusual happening?"

Acoustic indices are perfect for this because they capture overall soundscape properties without requiring species identification. They can detect:
- Changes in acoustic energy distribution
- Shifts in frequency patterns
- Unusual temporal patterns
- Deviations from expected conditions

## Proof of Concept Approach

### Goal
Demonstrate that acoustic indices can provide early warning for biological events using one year of existing data.

### Method: Known Event Validation

**Step 1: Identify Ground Truth Events**
Use manual detection data to identify major biological events (spawning aggregations, unusual activity periods).

**Step 2: Extract Acoustic Patterns**
For each known event, analyze acoustic indices:
- 48 hours before the event
- During the event
- 24 hours after the event

**Step 3: Characterize Anomalies**
Calculate how much acoustic indices deviated from expected values based on:
- Time of day (night vs day)
- Month (seasonal expectations)
- Station (local baseline)
- Temperature (environmental conditions)

**Step 4: Evaluate Detection Performance**
Determine what percentage of known biological events showed detectable acoustic anomalies before or during the event.

### Success Metrics

A successful proof of concept would show:
- Acoustic anomalies preceded or accompanied 70% of major biological events
- Anomalies appeared 6-24 hours before peak biological activity
- False positive rate is manageable (less than 30%)

### Implementation Plan

**Phase 1: Baseline Analysis (Week 1)**
- Calculate typical acoustic patterns for each station by hour and month
- Identify the top 20 biological events from manual detection data
- Extract acoustic index values around these events

**Phase 2: Pattern Discovery (Week 2)**
- Compare event periods to baselines
- Identify consistent anomaly patterns
- Test different deviation thresholds

**Phase 3: Validation (Week 3)**
- Apply anomaly detection to full dataset
- Compare detected anomalies to known events
- Calculate performance metrics

## Data Requirements

We have:
- 1 year of acoustic indices (2021)
- Manual detection data (ground truth)
- Temperature and depth data
- 3 stations with different characteristics

We need to calculate:
- Hourly baseline expectations (station × hour × month)
- Deviation scores from multiple baselines
- Temporal patterns around known events

## Questions for Subject Matter Experts

### About Biological Events

1. **What are the most important biological events you want to detect?**
   Examples: spawning aggregations, migration pulses, predation events

2. **How long do these events typically last?**
   This helps us set appropriate time windows for analysis.

3. **Are there known triggers for these events?**
   Temperature thresholds, lunar phases, seasonal timing?

4. **What's the minimum lead time that would be useful for detection?**
   Is 6 hours enough? 24 hours? Different for different events?

### About Acoustic Patterns

5. **Have you noticed acoustic patterns that precede biological events?**
   Gradual buildups, sudden changes, specific frequency bands?

6. **What types of false positives are acceptable vs problematic?**
   Is it worse to miss events or have too many false alarms?

7. **Are there known non-biological acoustic events we should filter?**
   Boat traffic patterns, weather events, equipment noise?

### About Station Differences

8. **What makes each station acoustically unique?**
   Different depths, substrates, proximity to shore, typical species?

9. **Should we expect the same events at all stations?**
   Or are some events station-specific?

10. **How do environmental conditions vary between stations?**
    Different temperature ranges, stratification, currents?

### About Practical Deployment

11. **How would this tool be used in practice?**
    Daily checks? Automated alerts? Integrated with other monitoring?

12. **What information would be most useful in an alert?**
    Just "something unusual" or specific context about the anomaly?

13. **How quickly do you need to know about events?**
    Real-time, daily summaries, weekly reports?

## Technical Considerations

### Simple Implementation First
Start with statistical deviation detection before moving to complex models:
- Z-scores from expected values
- Simple threshold-based alerting
- Rule-based pattern matching

### Future Enhancements
Once proof of concept succeeds:
- Machine learning anomaly detection (Isolation Forest, LSTM autoencoders)
- Multi-scale temporal analysis
- Cross-station pattern recognition
- Integration with AI species detection

## Expected Outcomes

### Minimum Viable Product
A system that can flag when acoustic conditions deviate significantly from expected patterns, with context about why the deviation is unusual.

### Best Case Scenario
Early warning system that detects 80% of biological events with 6-24 hour lead time and provides interpretable context about the type of anomaly detected.

### Research Contribution
Demonstration that acoustic indices provide valuable monitoring information complementary to species detection, especially for real-time applications.

## Next Steps

1. Get feedback from subject matter experts using the questions above
2. Implement baseline calculation for proof of concept
3. Analyze acoustic patterns around known biological events
4. Build simple anomaly detection prototype
5. Validate against ground truth data
6. Iterate based on results

## Why This Approach Will Succeed

- **Achievable**: Anomaly detection is easier than perfect classification
- **Valuable**: Early warning has immediate practical applications
- **Scalable**: Can start simple and add complexity over time
- **Complementary**: Works alongside species detection, not in competition
- **Robust**: Multiple validation approaches with existing ground truth data

The key insight: We don't need to identify exactly what's happening, just that something unusual is occurring that warrants closer investigation.