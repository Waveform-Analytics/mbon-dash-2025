# Dolphin Reintegration Plan
**Re-integrating dolphins into the marine community analysis pipeline**

## Overview
Dolphins were filtered out early in the analysis (around notebooks 2-3), but they should be part of the complete marine biological community. This plan systematically adds them back through the existing pipeline, culminating in comparative modeling (fish-only vs full marine community) in notebook 6.

## Key Challenge: Metric Incompatibility
**Fish vs Dolphin Measurements:**
- **Fish**: Intensity scale 0-3 (0=absent, 1=one, 2=more than one, 3=chorus)
- **Dolphins**: Raw counts (unbounded integers for echolocation, whistles, burst pulses)

**Solution: Hybrid Approach**
- **Preserve fish intensity scale** (keeps existing analysis intact)
- **Convert dolphin counts to comparable 0-3 intensity scale**
- **Combine all dolphin types** (echolocation + whistles + burst pulses = total dolphin activity)

## Strategy
1. **Work through existing notebooks sequentially** - modify to include dolphins
2. **Keep existing fish-only analysis** - don't break what's working
3. **Add dolphin intensity conversion** - make metrics comparable
4. **Add dolphins to create full marine community metrics** 
5. **Comparative modeling in notebook 6** - fish-only vs marine community
6. **Dashboard updates** - only if comparative results are compelling

## Dolphin Intensity Conversion Methodology
**Objective**: Convert dolphin counts to fish-comparable 0-3 intensity scale using data-driven thresholds

### Step-by-step Conversion:
1. **Combine dolphin types**: `total_dolphin_activity = echolocation_count + whistle_count + burst_pulse_count`
2. **Analyze distribution**: Examine distribution of combined dolphin counts across all data
3. **Set data-driven thresholds**:
   - **0 (Absent)**: `total_dolphin_activity == 0`
   - **1 (Low)**: Lower quartile of non-zero values (e.g., 25th percentile)
   - **2 (Medium)**: Middle range (25th-75th percentile)
   - **3 (High)**: Upper quartile (75th+ percentile)
4. **Validate against fish intensity distribution**: Ensure similar proportions in each category

### Implementation Approach:
```python
def determine_dolphin_thresholds(dolphin_counts):
    """Determine data-driven thresholds for dolphin intensity conversion
    
    Args:
        dolphin_counts: Array of total dolphin activity counts
        
    Returns:
        dict: Threshold values for intensity levels
    """
    non_zero_counts = dolphin_counts[dolphin_counts > 0]
    
    if len(non_zero_counts) == 0:
        return {'low': 1, 'medium': 2, 'high': 3}  # fallback
    
    # Use percentiles of non-zero data
    low_threshold = np.percentile(non_zero_counts, 33)   # 33rd percentile
    high_threshold = np.percentile(non_zero_counts, 67)  # 67th percentile
    
    return {
        'low': int(np.ceil(low_threshold)),
        'high': int(np.ceil(high_threshold))
    }

def create_dolphin_intensity(bde_count, bdbp_count, bdw_count, thresholds):
    """Convert bottlenose dolphin counts to 0-3 intensity scale
    
    Args:
        bde_count: Bottlenose dolphin echolocation count
        bdbp_count: Bottlenose dolphin burst pulses count  
        bdw_count: Bottlenose dolphin whistles count
        thresholds: Dict with 'low' and 'high' threshold values
        
    Returns:
        int: Dolphin intensity (0-3 scale matching fish intensity)
    """
    total_dolphin = bde_count + bdbp_count + bdw_count
    
    if total_dolphin == 0:
        return 0  # Absent
    elif total_dolphin < thresholds['high']:
        if total_dolphin < thresholds['low']:
            return 1  # Low activity
        else:
            return 2  # Medium activity
    else:
        return 3  # High activity
```

**Validation Steps**:
- Compare dolphin vs fish intensity distributions
- Ensure reasonable biological interpretation
- Document threshold values and rationale

---

## Phase 1: Identify Current State & Dolphin Exclusion Point
**Goal**: Understand exactly where and how dolphins were filtered out

### Step 1.1: Audit Existing Notebooks
- [ ] **Actions**:
  - Review notebooks 01-06 to identify dolphin filtering
  - Document exactly where `fish_only` or similar filters were applied
  - Note what the original detection data structure looked like
  - Identify which notebooks need modification
- [ ] **Test**: Review current notebook outputs to establish baseline
- [ ] **Commit**: "Document current state before dolphin reintegration"

---

## Phase 2: Early Pipeline Modifications (Notebooks 2-3)
**Goal**: Add dolphins back to the detection processing and community analysis

### Step 2.1: Modify Detection Data Processing (likely Notebook 2)
- [ ] **Notebook**: `python/scripts/notebooks/02_detection_data_processing.py`
- [ ] **Actions**:
  - Remove or modify fish-only filters
  - Include dolphin detections alongside fish
  - **Combine dolphin types**: Create `total_dolphin_activity = bde + bdbp + bdw`
  - **Analyze dolphin count distribution**: Examine combined dolphin counts across all data
  - **Determine data-driven thresholds**: Use percentiles to set intensity conversion thresholds
  - **Convert to dolphin intensity**: Apply 0-3 scale matching fish intensity approach
  - **Validate conversion**: Compare fish vs dolphin intensity distributions
  - Ensure proper species classification (fish vs dolphin)
- [ ] **Test**: Compare detection counts before/after modification, validate threshold logic
- [ ] **Commit**: "Reintegrate dolphins with data-driven intensity conversion"

### Step 2.2: Update Community Metrics (likely Notebook 3) 
- [ ] **Notebook**: `python/scripts/notebooks/03_community_metrics.py`
- [ ] **Actions**:
  - **Load dolphin intensity data**: Use converted 0-3 scale from Step 2.1
  - **Update community activity**: `total_community_activity = fish_intensity + dolphin_intensity`
  - **Update species diversity**: Include dolphin as additional "species" in diversity calculations
  - **Create marine community metrics**: New variables combining fish + dolphin intensity
  - **Preserve existing fish-only metrics**: Keep original fish analysis intact
  - **Compare distributions**: Fish-only vs marine community activity patterns
- [ ] **Test**: Review updated community metrics distributions, validate combined metrics
- [ ] **Commit**: "Update community metrics to include dolphin intensity"

---

## Phase 3: Temporal and Environmental Analysis (Notebooks 4-5)
**Goal**: Ensure temporal patterns and environmental context include full marine community

### Step 3.1: Update Temporal Pattern Analysis (Notebook 4)
- [ ] **Notebook**: `python/scripts/notebooks/04_temporal_pattern_analysis.py`
- [ ] **Actions**:
  - Include dolphin activity in temporal patterns
  - Analyze daily, seasonal patterns for full marine community
  - Compare fish vs dolphin temporal activity patterns
  - Update visualizations to show complete community
- [ ] **Test**: Review temporal pattern outputs
- [ ] **Commit**: "Include dolphins in temporal pattern analysis"

### Step 3.2: Update Environmental Context (Notebook 5)
- [ ] **Notebook**: `python/scripts/notebooks/05_environmental_context.py`
- [ ] **Actions**:
  - Ensure environmental correlations include full community
  - Analyze environmental drivers for dolphins vs fish
  - Update feature engineering to reflect marine community
- [ ] **Test**: Validate environmental analysis includes dolphins
- [ ] **Commit**: "Update environmental context for full marine community"

---

## Phase 4: Comparative Community Pattern Detection (Notebook 6)
**Goal**: Implement both fish-only and full marine community approaches for comparison

### Step 4.1: Prepare Comparative Framework
- [ ] **Notebook**: `python/scripts/notebooks/06_community_pattern_detection.py`
- [ ] **Actions**:
  - Load enhanced community data (with dolphins)
  - Create two parallel datasets:
    - `fish_only_data`: Original fish-focused metrics
    - `marine_community_data`: Fish + dolphin metrics
  - Ensure identical environmental features for fair comparison
  - Define comparable target variables for both approaches
- [ ] **Test**: Validate both datasets have same structure
- [ ] **Commit**: "Set up comparative analysis framework"

### Step 4.2: Train Fish-Only Models (Baseline)
- [ ] **Notebook**: Continue in `06_community_pattern_detection.py`
- [ ] **Actions**:
  - Train existing fish-only screening models
  - Use original fish community targets
  - Document baseline performance metrics
  - Save fish-only models and results
- [ ] **Test**: Verify fish-only models match previous performance
- [ ] **Commit**: "Train baseline fish-only screening models"

### Step 4.3: Train Marine Community Models
- [ ] **Notebook**: Continue in `06_community_pattern_detection.py`
- [ ] **Actions**:
  - Train equivalent models using full marine community data
  - Use marine community targets (fish + dolphin activity)
  - Apply identical model types and hyperparameters
  - Document marine community model performance
  - Save marine community models and results
- [ ] **Test**: Review marine community model performance
- [ ] **Commit**: "Train marine community screening models"

### Step 4.4: Comparative Analysis
- [ ] **Notebook**: Continue in `06_community_pattern_detection.py`
- [ ] **Actions**:
  - Compare model performance metrics side-by-side
  - Analyze differences in:
    - Precision, Recall, F1-scores
    - Feature importance rankings
    - Temporal pattern detection capability
    - False positive/negative patterns
  - Document key findings and insights
  - Create summary comparison tables
- [ ] **Test**: Review comparative analysis results
- [ ] **Commit**: "Complete comparative model analysis"

---

## Phase 5: Decision Point & Optional Dashboard Updates
**Goal**: Evaluate results and decide on dashboard integration

### Step 5.1: Evaluate Comparative Results
- [ ] **Actions**:
  - Review model performance differences
  - Assess biological/scientific value of including dolphins
  - Determine if comparative results warrant dashboard updates
  - Document decision rationale
- [ ] **Decision**: Proceed with dashboard updates? (Yes/No)

### Step 5.2: Dashboard Updates (Optional - if results are compelling)
- [ ] **Actions** (if proceeding):
  - Generate dashboard data with comparative results
  - Create visualizations showing both approaches
  - Update dashboard to display comparison
  - Test dashboard functionality
- [ ] **Commit**: "Add comparative marine community dashboard" (if applicable)

---

## Key Principles

### 1. Incremental & Reversible
- Work through notebooks sequentially
- Commit after each notebook modification
- Each commit provides a rollback point
- Test thoroughly before proceeding

### 2. Preserve Existing Work
- Don't break current fish-only analysis
- Build on existing structure rather than replacing
- Maintain compatibility with current outputs

### 3. Fair Comparison
- Use identical environmental features
- Apply same modeling approaches
- Ensure comparable evaluation metrics
- Document any methodological differences

### 4. Scientific Rigor
- Include dolphins for biological completeness
- Compare approaches objectively
- Document limitations and assumptions
- Let results guide dashboard decisions

---

## Testing Strategy
- **Notebook-by-notebook**: Run and validate each modified notebook
- **Data continuity**: Ensure data flows properly between notebooks
- **Comparative validation**: Check that both approaches are truly comparable
- **Performance baseline**: Maintain fish-only performance as baseline

## Expected Outcomes
- **Enhanced biological representation**: Full marine community included
- **Comparative insights**: Understanding of dolphins' contribution to patterns
- **Improved screening**: Potentially better detection of marine biodiversity
- **Dashboard flexibility**: Option to show fish-only or full community

---

## File Structure After Implementation
```
python/scripts/notebooks/
├── 01_*.py                    # (unchanged)
├── 02_*.py                    # Modified: dolphins included
├── 03_*.py                    # Modified: marine community metrics
├── 04_*.py                    # Modified: dolphin temporal patterns
├── 05_*.py                    # Modified: full community environmental context
└── 06_*.py                    # Major modification: comparative modeling

data/processed/
├── *_fish_only.json          # Fish-only results (preserved)
├── *_marine_community.json   # Full community results (new)
└── comparative_analysis.json # Model comparison results (new)
```

---

## Next Steps
1. **Start with Step 1.1**: Audit existing notebooks to find dolphin exclusion points
2. **Work sequentially**: Modify notebooks 2→3→4→5→6
3. **Test at each step**: Ensure notebooks run without errors
4. **Document changes**: Clear commit messages describing modifications
5. **Compare results**: Focus on comparative analysis in notebook 6

Ready to begin the audit! 🐬🐟