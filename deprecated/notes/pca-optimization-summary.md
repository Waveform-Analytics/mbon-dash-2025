# PCA Optimization Summary

## Performance Improvements Achieved

### **Before Optimization**
- **File size**: 6.5 MB
- **Data points**: 17,231 hourly observations
- **Indices**: 61 acoustic indices
- **Performance**: SLOW rendering, laggy interactions

### **After Optimization**
- **File size**: 417 KB (93% reduction!)
- **Data points**: 1,456 (6-hour aggregation)
- **Indices**: 25 carefully selected indices
- **Performance**: FAST rendering, smooth interactions

## Optimization Strategies Implemented

### 1. **Temporal Aggregation**
- Changed from hourly to 6-hour averages
- Reduces data points by ~92% while maintaining patterns
- Preserves diurnal and seasonal trends

### 2. **Index Selection**
- **Step 1**: Select top 50 indices by variance (most informative)
- **Step 2**: Remove highly correlated indices (>0.95 correlation)
- **Step 3**: Keep top 25 indices that capture most variation
- Result: 59% reduction in dimensionality

### 3. **Pre-computation in Python**
- ALL PCA calculations done in Python
- Web app only renders pre-computed results
- No heavy lifting in the browser

### 4. **Data Structure Optimization**
- Minimal JSON structure
- Only essential fields included
- Loadings limited to top 15 for visualization

## Scientific Validity Maintained

### **Variance Explained**
- Original (61 indices): 82.1% with 8 components
- Optimized (25 indices): 82.7% with 5 components
- **Better performance with fewer indices!**

### **Key Indices Retained**
The optimization automatically selected the most informative indices:
- High variance indices (capture most variation)
- Low correlation between selected indices (minimal redundancy)
- Representative across all index categories

### **Temporal Resolution**
- 6-hour aggregation maintains:
  - Diurnal patterns (4 points per day)
  - Seasonal trends
  - Station differences
  - Reduces noise from hourly fluctuations

## Usage in Dashboard

### **Simple Usage**
```typescript
// Loads the optimized PCA data
const { data, loading, error } = usePCABiplot();
```

## Files Generated

1. **`pca_biplot.json`** (417 KB) - The ONLY PCA data file (optimized)
2. **`generate_pca_biplot_data.py`** - PCA generation script with built-in optimization

## Recommendations for Further Optimization

If still too slow:
1. **Increase aggregation**: Move to daily averages (reduces to ~365 points)
2. **Reduce indices further**: Use top 15 indices only
3. **Implement sampling**: Show every Nth point with drill-down capability
4. **Progressive loading**: Load overview first, details on demand

## Key Insights from Optimization

1. **Many indices are redundant** - High correlation between indices means we can use fewer
2. **Temporal aggregation preserves patterns** - 6-hour windows capture essential variation
3. **Pre-computation is essential** - Browser should only render, not compute
4. **File size matters** - 400KB loads instantly, 6.5MB causes noticeable lag

## Current Status

✅ **COMPLETE** - The PCA implementation now uses ONLY the optimized version:
- Single `pca_biplot.json` file (417 KB)
- All computation done in Python
- Fast, smooth web visualization
- No unnecessary code clutter