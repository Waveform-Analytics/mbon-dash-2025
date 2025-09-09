# Statistical Metrics Explained for Acoustic Analysis

## Overview
This document explains the screening metrics used in the acoustic index analysis in plain, non-jargon terms. These metrics help us understand which acoustic indices best predict marine species activity.

## The Four Screening Metrics

### 1. Correlation (Spearman) - "Do they move together?"

**What it measures**: When the acoustic index goes up, does species activity also tend to go up?

**Spearman vs Pearson - The Key Difference**:
- **Pearson**: Measures if they move together in a *straight line* relationship
  - Example: "For every 1 unit increase in temperature, ice cream sales increase by $10"
  - Assumes the relationship is linear and data is normally distributed
  
- **Spearman**: Measures if they move together in *the same direction*, but not necessarily in a straight line
  - Example: "When temperature ranks higher, ice cream sales also rank higher"
  - Works with rankings instead of actual values
  - Better for real-world messy data that isn't perfectly linear

**Why we use Spearman for marine acoustics**: 
- Fish don't respond linearly to sound (a twice-as-loud sound doesn't mean twice as many fish)
- Species detection data is often skewed (lots of zeros, occasional high values)
- We care more about "does higher index = more fish?" than the exact mathematical relationship

**Reading the correlation values**:
- `1.0` = Perfect positive relationship (index up → species up, always)
- `0.0` = No relationship (random)
- `-1.0` = Perfect negative relationship (index up → species down, always)
- `0.3-0.5` = Moderate relationship (useful for prediction)
- `>0.5` = Strong relationship (very useful)

### 2. Discrimination (Cohen's d) - "Can it tell quiet from loud times?"

**What it measures**: How different are the acoustic index values between quiet times (no fish) and chorus times (lots of fish)?

**In everyday terms**: Imagine you're trying to tell if a party is happening by listening from outside:
- High discrimination = Party noise is VERY different from quiet time (easy to tell)
- Low discrimination = Party noise is only slightly louder (hard to tell)

**The math in plain English**:
1. Calculate average index value during quiet times
2. Calculate average index value during fish choruses  
3. Find the difference between these averages
4. Divide by the "typical variation" (pooled standard deviation)

**Code implementation**:
```python
# Cohen's d effect size
discrimination = abs(chorus_values.mean() - quiet_values.mean()) / pooled_std
```

**Reading the discrimination values**:
- `0.2` = Small effect (barely noticeable difference)
- `0.5` = Medium effect (noticeable difference)
- `0.8` = Large effect (obvious difference)
- `>1.0` = Very large effect (quiet and chorus are clearly distinct)

### 3. Detection Rate - "How often does it catch the action?"

**What it measures**: When fish are actually active, what percentage of the time does the acoustic index show something unusual?

**In everyday terms**: Like a motion detector for sound:
- If fish are singing 100 times
- And the acoustic index shows "something's happening!" 70 times
- Detection rate = 70%

**How it works**:
1. Find all times when fish activity is high (intensity ≥ 2)
2. Define "acoustic anomaly" as index values in the top 25% (75th percentile)
3. Count how many high-activity times also have high index values
4. Calculate the percentage

**Code implementation**:
```python
detection_rate = (high_intensity_mask & anomaly_mask).sum() / high_intensity_mask.sum()
```

**Reading the detection rate values**:
- `0.7` (70%) = Good detector (catches most events)
- `0.5` (50%) = Okay detector (50/50 chance)
- `0.3` (30%) = Poor detector (misses most events)

### 4. Lead Time - "Can it predict what's coming?"

**What it would measure**: How many hours before a fish chorus does the acoustic index start changing?

**In everyday terms**: Like weather prediction:
- Barometric pressure drops → Storm coming in 6 hours
- Acoustic index rises → Fish chorus starting in 2 hours

**Implementation note**: This requires sophisticated time-series analysis to implement properly and is currently marked as future work in the code.

## Why These Metrics Matter Together

Think of it like evaluating a smoke detector:
- **Correlation**: Does smoke level relate to fire intensity? (relationship strength)
- **Discrimination**: Can it tell the difference between no fire and big fire? (separation ability)  
- **Detection Rate**: When there IS a fire, does it alarm? (reliability)
- **Lead Time**: How early does it warn you? (predictive power)

A good acoustic index for predicting fish activity would have:
- High correlation (>0.5) - strongly related to fish presence
- High discrimination (>0.8) - clearly different between quiet/active
- High detection rate (>70%) - reliably detects when fish are present
- Positive lead time - gives advance warning

## Practical Application

This screening process helps identify which of the 50+ acoustic indices are actually useful for predicting each species' activity patterns. By running all combinations through these metrics, we can:

1. **Reduce complexity**: Focus on the 3-5 indices that work best
2. **Species-specific insights**: Different indices may work better for different species
3. **Station variations**: Account for different acoustic environments at each monitoring station
4. **Build better models**: Use only the most predictive indices in machine learning models

## Key Takeaways

- **Spearman correlation** is more robust for ecological data than Pearson
- **Multiple metrics** give a fuller picture than any single measure
- **High values in all metrics** indicate a truly useful acoustic index
- **Context matters**: An index that works for one species may not work for another