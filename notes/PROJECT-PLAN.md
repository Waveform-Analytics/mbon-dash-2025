# Statistical analysis plan for marine soundscape prediction using acoustic indices

## Executive Summary

This comprehensive statistical analysis plan presents a methodologically rigorous approach for predicting fish calling intensity, dolphin vocalizations, and vessel presence using 50-60 acoustic indices as predictors. Building strategically upon Transue et al. (2023)'s Charleston Harbor random forest framework, which achieved 85-99% accuracy for fish calling but required extensive manual review, this plan advances soundscape ecology methods through automated acoustic indices while maintaining ecological interpretability. The core innovation lies in replacing labor-intensive manual detection with noise-robust acoustic indices, implementing multi-output LightGBM models that handle diverse response distributions, and employing temporal blocked cross-validation to prevent overfitting in autocorrelated ecological data.

## Background and Strategic Foundation

The Transue et al. (2023) Charleston Harbor study established a robust baseline using SPL-based random forest models but identified critical limitations: biological patterns emerged only after removing anthropogenic noise files, manual review of 70,493 files proved unsustainable, and SPL patterns failed to capture fine-scale temporal dynamics in urbanized estuaries. Our approach directly addresses these limitations by implementing acoustic indices that maintain signal detection despite vessel noise, automating biological pattern recognition, and capturing multi-scale temporal dynamics from hourly to seasonal cycles.

## Data Structure and Response Variables

### Response Variable Configuration
The multi-response prediction framework targets three distinct variable types requiring specialized modeling approaches. **Fish calling intensity** uses a 0-3 ordinal scale for six species (black drum, oyster toadfish, silver perch, spotted seatrout, red drum, weakfish), treated as ordinal regression within the gradient boosting framework. **Bottlenose dolphin vocalizations** represent count data (whistles, echolocation clicks, burst pulses), modeled using Poisson or negative binomial distributions depending on overdispersion assessment. **Vessel presence** forms a binary classification problem with expected class imbalance requiring weighted loss functions.

### Temporal Resolution Alignment
The hourly acoustic indices align with bimanual detections through temporal aggregation. For acoustic indices calculated every hour, direct matching occurs with the 2-hour manual detection intervals. Temperature data collected every 20 minutes undergoes averaging to hourly resolution. This alignment preserves the temporal granularity needed for circadian pattern detection while maintaining consistency across data streams.

## Acoustic Index Selection and Configuration

### Primary Index Suite
Based on marine soundscape research synthesis, our core index set prioritizes proven performers while maintaining ecological interpretability. **Low-frequency SPL (50-1000 Hz)** remains as the most robust single metric for fish community assessment, showing consistent correlations with spawning activity. **Acoustic Complexity Index (ACI)** with 31.2 Hz frequency resolution captures increased biological activity, particularly effective for detecting marine mammal vocalizations when snapping shrimp don't dominate. **Normalized Difference Soundscape Index (NDSI)** configured with anthrophony band 10 Hz-1 kHz and biophony band 1-32 kHz provides critical vessel noise discrimination.

**Total Entropy (H)** offers complementary information about acoustic diversity but requires careful interpretation as it decreases with both vessel noise and single-species dominance. **Bioacoustic Index (BI)** shows inverse relationships with marine mammal echolocation, providing species-specific response patterns. Additional indices include temporal entropy, acoustic evenness, spectral entropy across multiple frequency bands, and the number of acoustic events per unit time.

### Frequency Band Optimization
Species-specific frequency bands enhance detection accuracy. Fish vocalizations concentrate in 50-2500 Hz, with sciaenids optimally detected at 50-800 Hz and batrachoidids at 80-400 Hz. Bottlenose dolphin whistles span 4-24 kHz while echolocation extends to 150 kHz. Snapping shrimp dominate 2-15 kHz bands, requiring careful interpretation of indices in these frequencies. Vessel noise primarily affects frequencies below 1 kHz, informing noise-robust index design.

### Preprocessing Requirements
Standardization ensures comparable scales across indices while preserving ecological relationships. High-pass filtering above 10 Hz removes low-frequency vessel-induced noise. Five-minute analysis windows provide stable index calculations while maintaining temporal resolution. Automated vessel noise detection flags anthropogenic interference periods without removing data, allowing models to learn noise-robust patterns.

## Dimensional Reduction Strategy

### Three-Stage Hybrid Approach
The optimal reduction from 60 to 20 indices follows a carefully validated pipeline. **Stage 1** applies correlation filtering, removing indices with pairwise correlations exceeding 0.85 while calculating Variance Inflation Factors to eliminate those above 8. This typically reduces the set from 60 to 40 indices. **Stage 2** implements hierarchical clustering to identify 5-6 functional groups representing spectral diversity, temporal complexity, amplitude measures, frequency-specific patterns, and anthropogenic indicators. Selection of 3-4 representatives per cluster based on marine performance metrics yields approximately 25 indices. **Stage 3** employs Recursive Feature Elimination with cross-validation (RFECV) using LightGBM as the estimator, determining the optimal subset of 15-20 indices while maintaining 75-85% of original predictive power.

### Interpretability Preservation
Each reduction stage maintains ecological meaning through explicit constraints. Clusters must contain at least one index representing biophony, geophony, and anthropophony. Feature importance rankings guide selection within clusters. The final index set undergoes validation against known ecological patterns to ensure biological relevance. This approach balances computational efficiency with ecological interpretability, critical for management applications.

## Machine Learning Architecture

### Multi-Output LightGBM Framework
The primary modeling approach employs LightGBM's multi-output capabilities with response-specific configurations. The gradient boosting framework offers 25-30% lower inference latency than XGBoost while maintaining accuracy, crucial for operational deployment. Native categorical support handles station locations and temporal factors without extensive encoding. The leaf-wise tree growth strategy captures complex non-linear acoustic-ecological relationships.

### Response-Specific Model Configuration
**Ordinal fish calling models** use custom ordinal objectives preserving the 0-3 intensity scale's ordered nature. Hyperparameters include learning rate 0.05-0.1, maximum depth 5-8, minimum child samples 20-50, and L1/L2 regularization 0.1-1.0. **Dolphin count models** employ Poisson or Tweedie distributions depending on variance-to-mean ratios. Zero-inflation handling uses two-stage models when zero counts exceed 30%. **Vessel detection models** implement focal loss for extreme class imbalance with class weights inversely proportional to frequency.

### Ensemble Strategy
While LightGBM serves as the primary engine, an ensemble approach provides uncertainty quantification and improved robustness. Random Forest models offer baseline predictions and feature importance validation. The ensemble weights optimize through cross-validation, typically favoring LightGBM 70-80% with Random Forest providing stability. Prediction intervals derive from the ensemble variance, crucial for management decisions.

## Temporal Variable Integration

### Hierarchical Temporal Structure
The model incorporates multiple temporal scales as interacting predictors. **Circadian patterns** enter as both continuous hour (0-23) and categorical day/night/crepuscular periods, with sine/cosine transformations capturing cyclical nature. **Lunar cycles** use continuous lunar illumination percentage (0-100%) rather than discrete phases, with interaction terms between lunar and diel periods. **Seasonal patterns** employ month as both categorical and continuous sinusoidal functions, with water temperature serving as a mechanistic seasonal proxy. **Tidal cycles** integrate as categorical phases (high/low/rising/falling) with continuous height measurements where available.

### Critical Temporal Interactions
Research demonstrates significant interactions requiring explicit modeling. Lunar-diel interactions capture how moon phase modulates daily calling patterns. Temperature-season interactions distinguish direct thermal effects from photoperiod influences. Tidal-station interactions reflect site-specific hydrodynamic effects. Weekend-seasonal patterns account for anthropogenic activity variations. These interactions substantially improve prediction accuracy, particularly for species with complex temporal behaviors.

## Validation Framework

### Temporal Blocked Cross-Validation
The primary validation strategy prevents temporal leakage through ecological blocking. Block size spans 14 days, exceeding the 7-day autocorrelation range identified in marine soundscapes. A minimum 7-day gap separates training and test blocks. Five-fold blocked CV provides robust performance estimates while maintaining sufficient training data. This approach yields conservative but realistic accuracy assessments.

### Multi-Scale Performance Assessment
Validation occurs across multiple temporal scales to ensure consistent model performance. **Hourly predictions** assess diel pattern capture using mean absolute error and phase correlation. **Daily aggregations** evaluate 24-hour activity budgets through RMSE and bias metrics. **Monthly summaries** validate seasonal phenology using correlation with known patterns. **Annual trends** confirm long-term stability through year-over-year comparisons.

### Species-Specific Validation
Each response variable requires tailored validation metrics. **Fish calling models** use ordinal accuracy, weighted kappa, and confusion matrices by intensity level. **Dolphin count models** employ mean absolute error, Poisson deviance, and zero-inflation tests. **Vessel detection models** utilize precision-recall curves, F1 scores, and temporal false positive rates. Cross-species validation ensures the multi-output framework maintains performance across all targets.

## Implementation Protocol

### Data Pipeline Architecture
The analysis pipeline follows a modular design enabling component updates without system-wide changes. **Raw acoustic data** flows through automated index calculation using standardized parameters. **Quality control** flags anomalous recordings through outlier detection and metadata validation. **Feature engineering** generates temporal variables and environmental interactions. **Model training** occurs on clustered computing resources with parallel processing. **Prediction serving** provides real-time or batch inference depending on operational needs.

### Computational Considerations
Processing 50-60 acoustic indices across multiple stations generates substantial computational load. Index calculation parallelizes across recordings using 5-minute windows. Feature reduction occurs monthly to adapt to changing conditions. Model retraining happens quarterly or when performance degrades below thresholds. GPU acceleration enhances LightGBM training for large datasets. Edge deployment uses optimized models for real-time monitoring applications.

### Operational Deployment
The system design supports both research and management applications. **Automated reporting** generates daily/weekly summaries of biological activity patterns. **Alert systems** trigger when unusual patterns exceed statistical thresholds. **Adaptive management interfaces** provide decision-support tools for marine spatial planning. **Data archiving** maintains full acoustic indices for retrospective analyses. **Performance monitoring** tracks model accuracy with automated retraining triggers.

## Comparative Assessment Framework

### Acoustic Indices vs. SPL Baseline
Direct comparison with Transue et al.'s SPL approach validates the acoustic index advantages. Using identical training/test splits enables fair comparison. Performance metrics include prediction accuracy, computational efficiency, and noise robustness. We expect 10-20% accuracy improvements in noise-contaminated periods. Interpretability assessments compare ecological insights from indices versus SPL patterns. Cost-benefit analysis weighs computational overhead against manual review elimination.

### Ablation Studies
Systematic evaluation identifies critical components through selective removal. **Index importance** derives from sequential exclusion with performance tracking. **Temporal variable necessity** tests models without specific temporal predictors. **Environmental variable contribution** assesses pure acoustic versus integrated models. **Ensemble component value** compares single versus multiple model architectures. These studies guide model simplification for resource-constrained deployments.

## Quality Assurance and Ecological Validation

### Ground-Truthing Requirements
Model validation extends beyond statistical metrics to ecological verification. **Species occurrence data** from visual surveys validates acoustic predictions. **Reproductive success metrics** confirm calling intensity relationships with spawning. **Behavioral observations** verify predicted activity patterns. **Environmental correlation** ensures indices respond appropriately to conditions. **Expert review** of edge cases identifies systematic biases requiring correction.

### Uncertainty Quantification
Prediction uncertainty propagates through the modeling pipeline. **Aleatoric uncertainty** from natural variability enters through probabilistic predictions. **Epistemic uncertainty** from model limitations manifests in ensemble disagreement. **Data uncertainty** from measurement errors propagates through sensitivity analysis. **Temporal uncertainty** from autocorrelation affects through blocked validation. Uncertainty estimates accompany all predictions for risk-aware decision making.

## Expected Outcomes and Advancement

This comprehensive approach advances marine soundscape ecology through several innovations. **Automation** eliminates the 70,493 manual file reviews while maintaining accuracy. **Noise robustness** enables biological pattern detection despite vessel interference. **Multi-scale integration** captures temporal dynamics from hours to seasons. **Interpretable predictions** maintain ecological meaning through careful index selection. **Operational readiness** supports real-time monitoring and adaptive management.

Performance targets based on research synthesis suggest 85-95% accuracy for fish calling intensity, 70-80% variance explained for dolphin vocalizations, and 90%+ accuracy for vessel detection. The dimensional reduction to 20 indices maintains 80% of full-suite predictive power while improving computational efficiency 3-fold. Temporal validation ensures stable performance across years, critical for long-term monitoring programs.

## Conclusion

This statistical analysis plan provides a methodologically rigorous framework for advancing marine soundscape ecology beyond traditional SPL approaches. By strategically building upon Transue et al.'s random forest foundation while addressing identified limitations through acoustic indices, multi-output gradient boosting, and temporal blocking validation, the approach enables automated, noise-robust biological monitoring in complex coastal environments. The careful balance of dimensional reduction with ecological interpretability, combined with hierarchical temporal modeling and comprehensive validation, establishes a new standard for soundscape-based ecosystem assessment. Implementation of this framework will substantially enhance our capability to monitor and understand marine acoustic communities in an era of increasing anthropogenic pressure and climate change.