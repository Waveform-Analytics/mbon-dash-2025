# Research Questions

This project addresses fundamental questions about using acoustic indices as proxies for marine biodiversity monitoring.

## Primary Research Questions

### 1. Index Dimensionality Reduction *(Future Work)*
- Can we reduce 56+ acoustic indices to 3-5 "super indices" that capture most soundscape variation?
- Which indices contribute most to principal components?
- What percentage of variance do the top components explain?

### 2. Biodiversity Prediction Capability *(Future Work)*
- Which acoustic indices best predict species detection patterns?
- How do index-based predictions compare to environmental predictors (temperature/depth)?
- Can we develop cost-effective alternatives to manual species annotation?

### 3. Index Category Performance
- Do certain index categories (diversity, complexity, bioacoustic) outperform others?
- Which temporal vs frequency domain indices are most informative?
- Are there redundant index categories we can eliminate?

## Secondary Research Questions

### 4. Spatial and Temporal Patterns
- How do acoustic environments differ between stations (9M, 14M, 37M)?
- Are there consistent temporal patterns (hourly, seasonal) in key indices?
- Multi-year stability: Do index patterns remain consistent (2018 vs 2021)?

### 5. Environmental Interactions
- Do temperature and depth cycles drive index variation independent of biology?
- Should indices be environmentally corrected for better biodiversity assessment?
- Which indices are most/least affected by environmental confounders?

### 6. Cost-Effectiveness Assessment
- Can a reduced index set provide equivalent biodiversity information to manual annotation?
- What is the processing time/computational cost trade-off for different index sets?
- ROI analysis: effort savings vs information loss

## Analysis Approach

### Phase 1: Foundation Data Analysis *(Current)*
1. **Data Processing**: Transform Excel files into analysis-ready format
2. **Species Patterns**: Analyze detection patterns across stations and time
3. **Environmental Context**: Understand temperature/depth relationships

### Phase 2: Acoustic Integration *(Planned)*
1. **Index Integration**: Combine acoustic indices with existing datasets
2. **Temporal Alignment**: Match acoustic measurements with species detections
3. **Quality Assessment**: Evaluate data completeness and processing needs

### Phase 3: Predictive Analysis *(Future)*
1. **Dimensionality Reduction**: PCA analysis of acoustic indices
2. **Correlation Analysis**: Index-species relationships
3. **Predictive Modeling**: Develop biodiversity prediction tools

## Success Metrics

### Technical Success
- ✅ Robust data processing pipeline for Excel files and manual annotations
- ✅ Handle naming variations and missing data patterns
- 🔄 Integrate acoustic indices when available
- 🔄 Scale to additional datasets and time periods

### Scientific Success
- **Target**: Identify <10 key indices explaining >70% of biodiversity variation
- Demonstrate statistically significant index-species relationships
- Quantify cost-effectiveness vs manual annotation approaches

### Practical Applications
- Provide actionable recommendations for marine monitoring programs
- Create automated index selection tools for new environments
- Develop cost-effective alternatives to labor-intensive manual methods

## Data Scope

### Current Dataset
- **Stations**: 9M, 14M, 37M (May River, South Carolina)
- **Years**: 2018, 2021
- **Detection Data**: 26,280 records (2-hour windows)
- **Environmental Data**: 237,334 temperature/depth measurements
- **Species**: 28 tracked species from manual annotations
- **Acoustic Indices**: In development (56 planned indices)

### Index Categories
- **Temporal Domain**: ZCR, MEANt, VARt, SKEWt, KURTt, LEQt
- **Frequency Domain**: MEANf, VARf, SKEWf, KURTf, NBPEAKS, LEQf
- **Acoustic Complexity**: ACI, NDSI, ADI, AEI
- **Diversity Indices**: H_Havrda, H_Renyi, H_pairedShannon, RAOQ
- **Bioacoustic**: BioEnergy, AnthroEnergy, BI, rBA
- **Spectral Coverage**: LFC, MFC, HFC

## Methodological Considerations

### Missing Data Strategy
- **Short gaps (≤2 hours)**: Linear interpolation with quality flags
- **Medium gaps (2-6 hours)**: Mark as "interpolated", include with warnings  
- **Long gaps (>6 hours)**: Exclude from analysis, document impact
- **Seasonal gaps**: Analyze available periods separately

### Statistical Approach
- Use standardized indices for PCA to handle different scales
- Apply appropriate correlation methods for non-normal distributions
- Account for temporal autocorrelation in time series analysis
- Validate results using cross-validation approaches

### Reproducibility
- All processing steps documented and scripted
- Random seeds set for reproducible results
- Version control for all analysis code
- Clear provenance tracking from raw data to results

## Expected Outcomes

This research will provide:

1. **Methodological Framework**: Reproducible approach for acoustic index analysis
2. **Index Recommendations**: Reduced set of most informative indices  
3. **Cost-Benefit Analysis**: Quantified trade-offs between manual and automated approaches
4. **Implementation Guidelines**: Practical recommendations for marine monitoring programs

The results will inform broader questions about scaling acoustic monitoring approaches to other marine environments and species assemblages.