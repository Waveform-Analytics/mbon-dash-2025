# First-Pass Predictive Modeling Implementation Plan

## Summary
A streamlined approach to quickly assess whether acoustic indices can predict marine biodiversity, focusing on interpretable models and actionable insights that will guide deeper analysis.

## Timeline: 2-3 Weeks Total

### Week 1: Data Prep & Simple Models 
### Week 2: Model Refinement & Validation 
### Week 3: Interpretation & Dashboard Integration 

---

## Phase 1: Data Preparation 

### 1.1 Feature Engineering Pipeline ✅ DONE
```python
# Completed preprocessing steps:
def prepare_modeling_data():
    # ✅ 1. Temporal alignment: Decimated indices to 2-hour windows (matching detections)
    
    # ✅ 2. Feature reduction: Removed correlated indices → 7 principal components
    
    # ✅ 3. Target variables created:
    #   - Vessels: Binary present/absent
    #   - Fish: Sum of intensity scores across all fish species  
    #   - Mammals: Sum of call counts
    #   - Species richness: Combine fish + mammal + vessel activity
    
    # 4. Train/test split: 70/30 random split within 2021 (single year available)
```

### 1.2 Quick Exploratory Analysis
```python
# Essential data understanding:
- Detection frequency per category (fish/mammals/vessels)
- Temporal coverage gaps (missing data patterns) 
- Correlation heatmap (7 PC components vs aggregated detections)
- Class balance: Fish intensity sums, mammal call counts, vessel presence/absence
```

---

## Phase 2: Core Modeling 

### 2.1 Model Selection

#### **Logistic Regression** (Primary - interpretability)
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Binary classification for each major species
models = {}
for species in ['fish', 'marine_mammals', 'vessels']:
    X_scaled = StandardScaler().fit_transform(X_train)
    model = LogisticRegression(penalty='l1', solver='liblinear', C=1.0)
    model.fit(X_scaled, y_train[species])
    models[species] = model
    
    # Get coefficients for interpretation
    coef_df = pd.DataFrame({
        'index': feature_names,
        'coefficient': model.coef_[0]
    }).sort_values('coefficient', key=abs)
```

#### **Random Forest** (Secondary - performance)
```python
from sklearn.ensemble import RandomForestClassifier

# Single model with built-in feature importance
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,  # Keep shallow for interpretability
    min_samples_split=20,  # Prevent overfitting
    random_state=42
)
rf.fit(X_train, y_train)

# Feature importance
importance_df = pd.DataFrame({
    'index': feature_names,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)
```


### 2.2 Model Variations to Test
```python
# Automated testing across different configurations:
variations = {
    'target_types': [
        'fish_intensity',      # Sum of fish intensity scores
        'mammal_calls',        # Sum of mammal call counts  
        'vessel_presence',     # Binary vessel detection
        'total_biodiversity'   # Combined biological activity
    ],
    'feature_sets': [
        'all_7_components',    # All 7 PCA components
        'top_3_components',    # Most important components only
        'pc1_pc2_only'         # First two components
    ],
    'model_types': [
        'logistic_regression', # Interpretable coefficients
        'random_forest'        # Feature importance
    ]
}
```

---

## Phase 3: Validation Strategy 

### 3.1 Cross-Validation Strategy (Single Year Data)

#### **Primary: Stratified Random Split**
```python
# 70/30 split within 2021 data, preserve class distributions
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Evaluate performance
metrics = {
    'f1': f1_score(y_test, predictions),
    'precision': precision_score(y_test, predictions), 
    'recall': recall_score(y_test, predictions)
}
```

#### **Secondary: Station-Based Cross-Val**
```python
# Leave-one-station-out to test spatial generalization
for test_station in ['9M', '14M', '37M']:
    train_data = data[data.station != test_station]
    test_data = data[data.station == test_station]
    # Tests if patterns transfer between locations
```

### 3.2 Performance Metrics (Focus on these)
```python
# For classification
- Precision/Recall (handle class imbalance)
- F1 Score (balanced metric)
- ROC-AUC (if classes are balanced enough)
- Confusion Matrix (understand error types)

# For regression (richness/abundance)
- R² Score (variance explained)
- Mean Absolute Error (interpretable units)
- Spearman Correlation (monotonic relationships)
```

---

## Phase 4: Interpretation & Insights (2-3 days)

### 4.1 Feature Importance Analysis

#### **Method 1: Coefficient Interpretation** (for Logistic Regression)
```python
# Top positive predictors (presence indicators)
top_positive = coef_df.nlargest(5, 'coefficient')

# Top negative predictors (absence indicators)  
top_negative = coef_df.nsmallest(5, 'coefficient')

# Create interpretable summary
summary = f"""
Indices that predict {species} presence:
• {top_positive.iloc[0]['index']}: When high, {species} likely present
• {top_positive.iloc[1]['index']}: Strong positive correlation
...
"""
```

#### **Method 2: SHAP Values** (for Random Forest)
```python
import shap

# Create explainer
explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_test)

# Summary plot (which features matter most?)
shap.summary_plot(shap_values, X_test, feature_names=feature_names)

# Dependence plots (how do features affect predictions?)
for top_feature in importance_df.head(5)['index']:
    shap.dependence_plot(top_feature, shap_values, X_test)
```

### 4.2 Key Questions to Answer

#### **Q1: Which indices best predict species presence?**
```python
# Deliverable: Ranked list of indices by predictive power
results = pd.DataFrame({
    'index': feature_names,
    'fish_importance': fish_model.feature_importances_,
    'mammal_importance': mammal_model.feature_importances_,
    'overall_importance': overall_model.feature_importances_
})
results.to_csv('index_importance_rankings.csv')

# Visualization: Bar chart of top 10 indices
```

#### **Q2: Can we predict biodiversity metrics?**
```python
# Simple regression for species richness
from sklearn.linear_model import LinearRegression

richness_model = LinearRegression()
richness_model.fit(X_train, richness_train)
r2 = richness_model.score(X_test, richness_test)

# Deliverable: "Acoustic indices explain {r2:.1%} of richness variation"
```

#### **Q3: Do patterns hold across stations?**
```python
# Station-based validation matrix (single year)
validation_results = pd.DataFrame({
    'train_stations': ['9M+14M', '9M+37M', '14M+37M'], 
    'test_station': ['37M', '14M', '9M'],
    'f1_score': [0.68, 0.71, 0.65]
})

# Key insight: "Models transfer across stations with X% performance drop"
```

---

## Phase 5: Dashboard Integration 

### 5.1 Essential Visualizations

```typescript
// 1. Model Performance Overview
<ModelPerformanceCard>
  - Bar chart: F1 scores by species
  - Confusion matrices (2x2 grids)
  - ROC curves (if applicable)
</ModelPerformanceCard>

// 2. Feature Importance Display
<FeatureImportanceChart>
  - Horizontal bar chart of top 15 indices
  - Color-coded by index category
  - Hover for index descriptions
</FeatureImportanceChart>

// 3. Prediction Timeline
<PredictionTimeline>
  - Actual vs predicted detections over time
  - Confidence bands
  - Highlight misclassifications
</PredictionTimeline>

// 4. Cross-Validation Results
<ValidationMatrix>
  - Heatmap of performance across years/stations
  - Clear indication of generalization ability
</ValidationMatrix>
```

### 5.2 Interactive Elements

```typescript
// Simple parameter selection
<ModelExplorer>
  <Select options={['fish', 'mammals', 'vessels', 'biodiversity']} />
  <Select options={['logistic', 'random_forest']} />
  <Select options={['9M', '14M', '37M', 'all']} />
  
  // Updates visualizations based on selection
</ModelExplorer>
```

---

## Deliverables Checklist

### Week 1 Deliverables
- [ ] Aligned dataset with 2-hour detection windows
- [ ] Feature correlation matrix and selection of 20-30 indices
- [ ] Basic logistic regression for top 3 species
- [ ] Initial performance metrics (accuracy, F1)

### Week 2 Deliverables  
- [ ] Random Forest model with feature importance
- [ ] Station-based cross-validation results  
- [ ] SHAP value analysis for top model
- [ ] Biodiversity metric regression models

### Week 3 Deliverables
- [ ] Summary report: "Top 5 Predictive Indices"
- [ ] Dashboard page with model performance
- [ ] Feature importance visualization
- [ ] Recommendations for deeper analysis

---

## Critical Success Factors

### What Success Looks Like
1. **Identify 3-5 indices** that consistently predict species presence (F1 > 0.6)
2. **Demonstrate spatial stability**: Models work across stations (performance drop < 20%)
3. **Clear interpretation**: Can explain WHY certain indices predict biodiversity
4. **Actionable insights**: Recommendations for monitoring protocol

### What Would Trigger Deeper Analysis
1. F1 scores > 0.7 for any species → Optimize that model further
2. Strong station-specific patterns → Investigate environmental factors
3. Temporal indices dominate → Explore time-series models
4. Unexpected index importance → Investigate ecological significance

---

## Python Implementation Structure

```python
# Suggested file organization
python/
├── scripts/
│   ├── 10_prepare_modeling_data.py     # Data alignment and feature engineering
│   ├── 11_train_simple_models.py       # Logistic regression and RF
│   ├── 12_validate_models.py           # Cross-validation and metrics
│   └── 13_generate_model_views.py      # Export results for dashboard
├── mbon_analysis/
│   ├── modeling/
│   │   ├── __init__.py
│   │   ├── preprocessor.py             # Feature engineering utilities
│   │   ├── simple_models.py            # Model training functions
│   │   ├── validation.py               # Cross-validation utilities
│   │   └── interpretation.py           # SHAP, feature importance
│   └── views/
│       └── model_results.py            # Generate dashboard-ready JSON
└── notebooks/
    └── model_exploration.ipynb         # Interactive exploration

# Dashboard integration
dashboard/src/
├── app/
│   └── models/
│       └── page.tsx                    # Model results page
└── components/
    └── models/
        ├── PerformanceMetrics.tsx
        ├── FeatureImportance.tsx
        └── PredictionTimeline.tsx
```

---

## Next Steps After First Pass

Based on first-pass results, prioritize:

1. **If models show promise** (F1 > 0.6):
   - Add more sophisticated features (rolling windows, interactions)
   - Try ensemble methods
   - Implement real-time prediction capability

2. **If certain indices dominate**:
   - Deep dive into those specific indices
   - Collect more training data for those patterns
   - Design targeted monitoring protocol

3. **If results are mixed**:
   - Try different temporal aggregations
   - Investigate station-specific models
   - Consider external factors (temperature, depth)

4. **If results are poor** (F1 < 0.4):
   - Revisit data quality and alignment
   - Try unsupervised methods first (clustering)
   - Consider that indices may not predict these specific species

---

*This plan prioritizes speed to insight while maintaining scientific rigor. The goal is to have actionable results within 2-3 weeks that guide whether deeper analysis is warranted.*