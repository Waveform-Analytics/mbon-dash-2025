# Analysis Approach 4: Event-Based Acoustic Monitoring with Temporal Context

## Executive Summary

We need to stop treating acoustic data as independent time points and start analyzing it as continuous events with temporal structure. This approach focuses on detecting and characterizing **biological events** (chorus onset, peak calling, cessation) using acoustic indices while accounting for temporal autocorrelation, station differences, and environmental drivers.

## The Core Insight We've Been Missing

Fish choruses aren't random occurrences - they're **extended events** with:
- **Build-up phases**: Gradual increase in calling activity
- **Sustained periods**: Hours of continuous calling
- **Decay phases**: Gradual cessation
- **Environmental triggers**: Temperature thresholds, tidal states, time of day

By focusing on event detection rather than point prediction, we can leverage the temporal structure that makes these patterns predictable.

## What We Keep From Previous Approaches

### From explore-01.py:
- ✅ Data alignment and decimation methods
- ✅ Species grouping (fish, dolphins, vessels)
- ✅ Index reduction via correlation
- ✅ Station-specific analysis
- ✅ Overall fish presence metrics

### From Approach 2 (Anomaly Detection):
- ✅ Focus on deviations from baseline
- ✅ Early warning system concept
- ✅ Known event validation

### From Approach 3 (Systematic Screening):
- ✅ Automated testing of combinations
- ✅ Performance metrics framework
- ✅ Transition type definitions

## The New Framework: Event Windows Analysis

### Core Concept
Instead of asking "are fish present at time T?", we ask:
- "Is a calling event starting/ongoing/ending?"
- "What acoustic patterns precede event onset?"
- "How do environmental conditions influence event timing?"

### Event Definition
A **biological event** is a continuous period where:
1. Species intensity ≥ 2 for at least 3 consecutive observations
2. Peak intensity reaches 3 (chorus) at some point
3. Clear onset and offset transitions

### Analysis Unit
**Event Windows** spanning:
- 12 hours before onset (pre-event baseline)
- Event duration (variable length)
- 6 hours after cessation (post-event recovery)

## Implementation Pipeline

### Phase 1: Event Extraction and Characterization (Day 1-2)

```python
def extract_biological_events(detections_df, species, min_duration=3):
    """Extract continuous calling events from detection data."""
    events = []
    
    # Find runs of high intensity (≥2)
    high_intensity = detections_df[species] >= 2
    
    # Group consecutive high-intensity periods
    event_groups = (high_intensity != high_intensity.shift()).cumsum()
    
    for event_id in event_groups[high_intensity].unique():
        event_data = detections_df[event_groups == event_id]
        
        if len(event_data) >= min_duration and event_data[species].max() == 3:
            events.append({
                'species': species,
                'station': event_data['station'].iloc[0],
                'start_time': event_data['Date'].min(),
                'end_time': event_data['Date'].max(),
                'duration_hours': len(event_data) * 2,  # 2-hour intervals
                'peak_intensity': event_data[species].max(),
                'mean_intensity': event_data[species].mean()
            })
    
    return pd.DataFrame(events)
```

### Phase 2: Acoustic Signature Analysis (Day 2-3)

For each event, extract acoustic index patterns:

```python
def analyze_event_acoustics(event, indices_df, hours_before=12, hours_after=6):
    """Extract acoustic patterns around biological events."""
    
    # Define analysis window
    window_start = event['start_time'] - pd.Timedelta(hours=hours_before)
    window_end = event['end_time'] + pd.Timedelta(hours=hours_after)
    
    # Extract indices for this window
    event_indices = indices_df[
        (indices_df['Date'] >= window_start) & 
        (indices_df['Date'] <= window_end)
    ].copy()
    
    # Mark event phases
    event_indices['phase'] = 'baseline'
    event_indices.loc[
        event_indices['Date'] >= event['start_time'], 'phase'
    ] = 'event'
    event_indices.loc[
        event_indices['Date'] > event['end_time'], 'phase'
    ] = 'recovery'
    
    # Calculate phase statistics for each index
    phase_stats = event_indices.groupby('phase')[reduced_indices].agg(['mean', 'std', 'max'])
    
    # Calculate change metrics
    baseline_mean = phase_stats.loc['baseline', :]['mean']
    event_mean = phase_stats.loc['event', :]['mean']
    
    return {
        'relative_change': (event_mean - baseline_mean) / baseline_mean,
        'effect_size': (event_mean - baseline_mean) / phase_stats.loc['baseline', :]['std'],
        'max_deviation': phase_stats.loc['event', :]['max'] - baseline_mean
    }
```

### Phase 3: Environmental Context Integration (Day 3-4)

```python
def add_environmental_context(events_df, env_data):
    """Add environmental conditions at event onset."""
    
    for idx, event in events_df.iterrows():
        # Get environmental conditions at event start
        env_at_start = env_data[
            (env_data['Date'] == event['start_time']) &
            (env_data['station'] == event['station'])
        ]
        
        # Get environmental conditions 24h before
        env_before = env_data[
            (env_data['Date'] >= event['start_time'] - pd.Timedelta(hours=24)) &
            (env_data['Date'] < event['start_time']) &
            (env_data['station'] == event['station'])
        ]
        
        events_df.loc[idx, 'temp_at_onset'] = env_at_start['temperature'].mean()
        events_df.loc[idx, 'depth_at_onset'] = env_at_start['depth'].mean()
        events_df.loc[idx, 'temp_change_24h'] = (
            env_at_start['temperature'].mean() - env_before['temperature'].mean()
        )
        events_df.loc[idx, 'tidal_state'] = classify_tidal_state(env_at_start['depth'])
    
    return events_df
```

### Phase 4: Pattern Discovery (Day 4-5)

```python
def discover_event_patterns(events_with_acoustics):
    """Identify consistent patterns across events."""
    
    # Group events by characteristics
    event_clusters = {
        'rapid_onset': events_with_acoustics[events_with_acoustics['onset_hours'] <= 2],
        'gradual_buildup': events_with_acoustics[events_with_acoustics['onset_hours'] > 2],
        'dawn_chorus': events_with_acoustics[events_with_acoustics['start_hour'].between(4, 8)],
        'dusk_chorus': events_with_acoustics[events_with_acoustics['start_hour'].between(16, 20)],
        'nocturnal': events_with_acoustics[events_with_acoustics['start_hour'].between(20, 4)]
    }
    
    # Find indices that consistently change before events
    reliable_indicators = {}
    for cluster_name, cluster_events in event_clusters.items():
        if len(cluster_events) < 5:
            continue
            
        # Which indices show consistent pre-event changes?
        pre_event_changes = cluster_events['pre_event_change'].mean()
        reliable_indicators[cluster_name] = pre_event_changes[
            pre_event_changes.abs() > 0.5  # >50% change from baseline
        ].sort_values(ascending=False)
    
    return reliable_indicators
```

### Phase 5: Detection Rule Generation (Day 5)

```python
def generate_detection_rules(pattern_analysis):
    """Create simple, deployable detection rules."""
    
    rules = []
    
    for event_type, indicators in pattern_analysis.items():
        for index, change_magnitude in indicators.items():
            rule = {
                'event_type': event_type,
                'index': index,
                'threshold': calculate_optimal_threshold(index, event_type),
                'expected_lead_time': calculate_lead_time(index, event_type),
                'confidence': calculate_rule_confidence(index, event_type),
                'rule_text': f"If {index} increases by >{change_magnitude:.1%} from 6h baseline → {event_type} likely in {lead_time}h"
            }
            rules.append(rule)
    
    return pd.DataFrame(rules)
```

## Quick Wins for Demonstration

### Week 1 Deliverables

1. **Event Timeline Visualization**
   - Timeline showing all detected biological events
   - Color-coded by species and intensity
   - Aligned with environmental data

2. **Top 3 Event Predictors**
   - Identify 3 acoustic indices that best predict event onset
   - Show lead time and reliability for each
   - Station-specific performance metrics

3. **Environmental Trigger Analysis**
   - Temperature thresholds for different species
   - Tidal state preferences
   - Time-of-day patterns

4. **Simple Detection Dashboard**
   - Current acoustic state vs. baseline
   - Probability of event in next 6 hours
   - Environmental conditions assessment

## Key Advantages of This Approach

1. **Respects Temporal Structure**: Analyzes continuous events, not isolated points
2. **Incorporates Context**: Uses environmental and temporal information
3. **Station-Specific**: Accounts for local baselines and patterns
4. **Actionable Output**: Generates clear detection rules with confidence levels
5. **Scientifically Valid**: Based on actual event structure, not artificial independence

## Critical Implementation Details

### Handling Sparse Events
- Combine similar species for rare events
- Use overall fish presence for initial analysis
- Bootstrap confidence intervals for small sample sizes

### Baseline Calculation
- Use same hour-of-day from previous 7 days
- Exclude known event periods from baseline
- Account for seasonal trends

### Multi-Station Analysis
- Normalize indices by station-specific ranges
- Test if rules transfer between stations
- Identify station-specific vs. universal patterns

## Environmental Integration Strategy

### Temperature Analysis
- Rolling 24h temperature change
- Degree-days above threshold
- Temperature anomalies from seasonal norm

### Tidal Analysis
- Classify as: low, rising, high, falling
- Time since last high/low tide
- Spring vs. neap tide periods

### Combined Environmental Score
```python
environmental_favorability = (
    temp_score * 0.4 +
    tidal_score * 0.3 +
    time_of_day_score * 0.3
)
```

## Validation Approach

### Leave-One-Out by Event
- Train on all events except one
- Test detection on held-out event
- Ensures temporal independence

### Performance Metrics
- Detection rate (% of events detected)
- Lead time (hours of advance warning)
- False positive rate (alerts without events)
- Precision-Recall curves for different thresholds

## Expected Results

### Minimum Success
- Detect 60% of major calling events
- 2-4 hour average lead time
- Clear patterns for 2-3 species

### Likely Outcome
- 70-80% detection of chorus events
- 4-6 hour lead time for gradual buildups
- Environmental triggers identified
- Station-specific detection rules

### Best Case
- 85%+ detection rate for major events
- 6-12 hour predictive capability
- Multi-species coordination patterns discovered
- Deployable real-time monitoring system

## Next Immediate Steps

1. **Extract all biological events** from 2021 detection data
2. **Calculate event-based acoustic signatures** for top 10 events
3. **Test environmental correlations** with event timing
4. **Generate initial detection rules** for overall fish presence
5. **Validate on independent time periods**

## Why This Will Work

- **Events are rare but extended**: Even with limited events, each provides hours of data
- **Temporal structure is information**: The buildup pattern itself is predictive
- **Environmental coupling is strong**: Temperature and tidal triggers are well-documented
- **Acoustic indices capture energy changes**: Even if not species-specific, energy redistribution is detectable

The key insight: **We don't need to predict every hour - we need to detect when conditions are building toward an event.**