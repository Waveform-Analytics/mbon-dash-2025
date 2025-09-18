# Experimental Analysis: Beyond Correlation

## Overview

This document outlines experimental approaches to analyze acoustic data that go beyond the correlation-based methods in the MVP plan. The goal is to detect subtle patterns and complex interactions that traditional statistical approaches might miss, particularly focusing on image processing techniques applied to acoustic heatmaps and time-frequency analysis methods.

## Background & Motivation

Current findings from MVP analysis:
- Spotted sea trout shows strong visual patterns (nighttime "squiggles" in summer) that are obvious in heatmaps but may not show up well in simple correlations
- Other species show weak correlations with indices, potentially due to:
  - Temporally localized patterns (not consistent across entire time series)
  - Non-linear relationships
  - Complex interactions with environmental variables
  - Patterns that exist at different time-frequency scales

Visual inspection of heatmaps reveals patterns that correlation analysis misses, suggesting image processing and advanced time-series techniques could be valuable.

---

## Phase 1: Image Processing & Pattern Detection

### Approach 1: Texture Analysis
**Goal**: Quantify textural changes in acoustic heatmaps that correlate with biological events

**Methods**:
- Convert acoustic index and detection heatmaps to grayscale images
- Extract texture features using sliding windows:
  - **Gray-Level Co-occurrence Matrix (GLCM)**: Measures texture properties (contrast, homogeneity, energy, correlation)
  - **Local Binary Patterns (LBP)**: Captures local texture patterns and transitions
  - **Gabor filters**: Detect oriented patterns and textures
- Correlate texture metrics with:
  - Species presence/absence timing
  - Seasonal transitions
  - Environmental variable changes

**Questions to Answer**:
- Do texture changes precede species onset?
- Are there subtle textural signatures for each species?
- Can texture analysis detect ecological state transitions?

### Approach 2: Visual Pattern Matching
**Goal**: Find similar patterns across different species, indices, or time periods

**Methods**:
- **Template matching**: Use spotted sea trout "squiggle" pattern as template to search other heatmaps
- **Normalized cross-correlation**: Find similar 2D patterns even if scaled or shifted
- **Ridge/edge detection**: Identify boundaries where acoustic patterns change
- **2D Fourier analysis**: Detect periodic structures in time-hour space

**Applications**:
- Search for spotted sea trout-like patterns in other species
- Identify recurring patterns across seasons or years
- Detect transitions between acoustic regimes

---

## Phase 2: Wavelet Analysis

### Background: Why Wavelets?
Traditional spectral analysis (FFT) shows "what frequencies are present" but loses temporal information. Wavelets preserve both:
- **Time information**: When events occur
- **Frequency information**: What frequency components are present
- **Multi-scale analysis**: Patterns at different temporal scales simultaneously

### Approach 3: Time-Frequency Decomposition
**Goal**: Identify patterns that exist at specific time-frequency combinations

**Methods**:
- **Continuous Wavelet Transform (CWT)** on acoustic indices and fish detection time series
- Use Morlet wavelets for optimal time-frequency resolution
- Create scalograms showing how frequency content evolves over time
- Compare scalogram patterns between indices and manual detections

**Questions**:
- Do spawning seasons show characteristic frequency signatures?
- Are there frequency bands where biological signals dominate?
- Do environmental cycles create predictable wavelet patterns?

### Approach 4: Cross-Wavelet Coherence
**Goal**: Find time-frequency regions where indices and fish detections co-vary

**Methods**:
- Calculate wavelet coherence between each acoustic index and fish detections
- Identify significant coherence regions using statistical testing
- Map coherence patterns across species and seasons
- Compare coherence with/without vessel periods

**Applications**:
- Detect temporary correlations that traditional methods miss
- Identify optimal frequency bands for biological monitoring
- Understand how vessel noise affects different frequency ranges

---

## Phase 3: Advanced Statistical Modeling

### Approach 5: Complex GAMs
**Goal**: Model non-linear interactions between indices, environment, and biology

**Methods**:
- **Tensor product smooths**: s(day_of_year, hour_of_day) to capture seasonal changes in diel patterns
- **Cyclic smooths**: Properly handle periodic variables (hour, day-of-year)
- **Station-specific effects**: Different smooth functions by monitoring location
- **Interaction terms**: Temperature × season, depth × tidal_cycle
- **Threshold models**: Non-linear responses to environmental variables

**Features to Include**:
- Day-of-year (seasonal patterns)
- Hour-of-day (diel patterns)
- Temperature and its lags
- Depth/tidal variables
- Image texture features (from Phase 1)
- Wavelet coefficients (from Phase 2)

### Approach 6: State-Space Models
**Goal**: Model system as switching between ecological states

**Methods**:
- **Hidden Markov Models**: Identify latent acoustic states (quiet, fish chorus, vessel-dominated)
- **Dynamic Factor Models**: Extract common biological signals from multiple indices
- **Regime-switching models**: Detect transitions between different acoustic regimes
- **Change-point detection**: Identify when acoustic patterns fundamentally shift

---

## Phase 4: Integration & Validation

### Approach 7: Multi-Modal Feature Fusion
**Goal**: Combine insights from image processing, wavelets, and traditional features

**Methods**:
- Create feature matrix combining:
  - Raw acoustic indices
  - Image texture features (GLCM, LBP)
  - Wavelet coefficients and coherence measures
  - Environmental variables
  - Temporal features
- **Dimensionality reduction**: UMAP or t-SNE to visualize acoustic-biological space
- **Clustering analysis**: Identify natural groupings in feature space
- **Supervised learning**: Random Forest or XGBoost to predict biological activity

### Approach 8: Pattern Discovery & Mining
**Goal**: Find recurring patterns without prior assumptions

**Methods**:
- **Matrix Profile analysis**: Discover motifs and anomalies in time series
- **Dynamic Time Warping (DTW)**: Find similar patterns even if time-shifted
- **Symbolic Aggregate Approximation (SAX)**: Convert time series to symbols for pattern matching
- **Frequent pattern mining**: Identify commonly occurring sequences

---

## Experimental Notebook Structure

### Notebook A: Image-Based Pattern Detection
- Convert heatmaps to images
- Extract and validate texture features
- Correlate with biological events
- Test pattern matching approaches

### Notebook B: Wavelet Analysis
- Implement CWT and cross-wavelet coherence
- Identify significant time-frequency patterns
- Compare wavelet features with traditional correlations
- Validate biological relevance

### Notebook C: Advanced Modeling
- Build complex GAMs with interaction terms
- Implement state-space models
- Test threshold and regime-switching approaches
- Compare predictive performance

### Notebook D: Integrated Pattern Mining
- Combine all feature types
- Apply unsupervised pattern discovery
- Validate discovered patterns against ground truth
- Develop operational recommendations

---

## Implementation Strategy

### Phase 1 Priority: Spotted sea trout as Proof-of-Concept
- Start with clearest signal (spotted sea trout nighttime patterns)
- Validate that image processing can detect known patterns
- Establish baseline performance before exploring subtler patterns

### Modular Development
- Create reusable functions for each technique
- Document computational requirements
- Build pipeline for applying methods across species/indices
- Maintain compatibility with existing MVP analysis

### Validation Approach
- Use 2021 data with established ground truth
- Cross-validate temporal patterns
- Test generalization across stations
- Compare with manual detection patterns

### Success Metrics
- Detection of known patterns (spotted sea trout validation)
- Discovery of previously unknown patterns
- Improved prediction of biological activity
- Reduced false positive/negative rates
- Practical implementation feasibility

---

## Expected Outcomes

### Primary Goals
1. **Pattern Discovery**: Find subtle biological patterns missed by correlation analysis
2. **Method Validation**: Establish which advanced techniques work best for acoustic-biological data
3. **Operational Tools**: Develop practical methods for improved biological monitoring
4. **Mechanistic Insight**: Better understand how acoustic indices relate to biological processes

### Potential Applications
- **Real-time monitoring**: Image-based anomaly detection for continuous systems
- **Targeted sampling**: Use pattern recognition to guide manual detection efforts
- **Cross-site comparison**: Standardized texture/pattern metrics for comparing locations
- **Climate studies**: Long-term pattern analysis for ecosystem change detection

### Research Questions Addressed
- Can image processing reveal biological patterns invisible to traditional statistics?
- What time-frequency scales are most informative for biological monitoring?
- How do complex environmental interactions affect acoustic-biological relationships?
- Which combination of techniques provides optimal biological pattern detection?

---

## Technical Considerations

### Computational Requirements
- Image processing: Moderate (sliding window operations)
- Wavelet analysis: High (CWT across long time series)
- Advanced modeling: Variable (GAMs moderate, state-space high)
- Integration phase: High (large feature matrices)

### Software Dependencies
- **Image processing**: scikit-image, opencv-python
- **Wavelets**: pywt, scipy
- **Advanced stats**: mgcv (R) or pyGAM (Python), statsmodels
- **Machine learning**: scikit-learn, xgboost
- **Visualization**: matplotlib, plotly, seaborn

### Data Management
- Standardized file naming for experimental outputs
- Efficient storage of large feature matrices
- Version control for experimental parameters
- Documentation of computational choices and performance