# Acoustic Indices as Biodiversity Proxies: Analysis Approach & Dashboard Design

## Executive Summary
This document outlines a comprehensive analytical approach for investigating whether acoustic indices can serve as proxies for marine biodiversity (as measured by manual species detections) and proposes a narrative-driven dashboard structure to guide users through the discovery process.

## Part 1: Analytical Approach

### 1.1 Data Overview & Challenges
- **Acoustic Indices**: ~60 indices, hourly resolution, 3 stations, 2 years (2018, 2021)
- **Manual Detections**: Fish, marine mammals, vessels, 2-hour resolution, same stations/years
- **Key Challenge**: Temporal alignment (1-hour indices vs 2-hour detections)
- **Scientific Question**: Can acoustic indices predict/indicate biodiversity patterns?

### 1.2 Preprocessing & Feature Reduction Strategy

#### Phase 1: Temporal Alignment
```python
# Options for handling temporal mismatch:
1. Aggregate indices to 2-hour windows (mean, max, min, std) -- MW - I want this one, except don't aggregate: just decimate. 
2. Assign detections to nearest hour (with overlap handling)
3. Use sliding windows with overlap
```

#### Phase 2: Index Redundancy Analysis
**Goal**: Identify and remove highly correlated indices before modeling

1. **Correlation Matrix Analysis**
   - Pearson correlation for linear relationships
   - Spearman correlation for monotonic relationships
   - Threshold: Remove indices with |r| > 0.95
   
2. **Variance Inflation Factor (VIF)**
   - Identify multicollinearity
   - Remove indices with VIF > 10
   
3. **Information-Based Metrics**
   - Mutual Information between indices
   - Remove indices providing redundant information

4. **Domain Knowledge Filtering**
   - Group indices by type (temporal, spectral, complexity)
   - Keep best representative from each group

#### Phase 3: Feature Importance Pre-screening
1. **Univariate Analysis**
   - Correlation with detection presence/absence
   - ANOVA F-statistic for each index vs species
   
2. **Random Forest Feature Importance**
   - Quick preliminary ranking
   - Use as guide, not final selection

### 1.3 Progressive Analysis Pipeline

#### Stage 1: Exploratory Data Analysis (Start Here)
1. **Temporal Patterns**
   - Time series of indices vs detections
   - Diel patterns (day/night differences)
   - Seasonal patterns
   
2. **Spatial Patterns**
   - Station-specific characteristics
   - Depth-related variations (9M, 14M, 37M)
   
3. **Basic Correlations**
   - Index-detection correlations
   - Environmental confounders (temperature, depth)

#### Stage 2: Dimensionality Reduction
1. **Principal Component Analysis (PCA)**
   - Reduce indices to 3-5 components
   - Interpret components ecologically
   - Visualize detection patterns in PC space
   
2. **Alternative Methods**
   - Factor Analysis (more interpretable loadings)
   - UMAP/t-SNE (non-linear patterns)
   - Independent Component Analysis (ICA)

#### Stage 3: Predictive Modeling (Simple → Complex)

**Level 1: Linear Models**
```python
# Start simple, interpretable
- Logistic Regression (presence/absence)
- Linear Regression (abundance/richness)
- Regularized models (LASSO for feature selection)
```

**Level 2: Tree-Based Models**
```python
# Good balance of interpretability and performance
- Decision Trees (single, interpretable)
- Random Forests (feature importance)
- Gradient Boosting (XGBoost, but explain with SHAP)
```

**Level 3: Advanced Models (if needed)**
```python
# Only if simpler models insufficient
- Neural Networks (start with shallow)
- Temporal models (LSTM for time series)
- Ensemble methods
```

#### Stage 4: Model Validation & Interpretation
1. **Cross-Validation Strategy**
   - Time-based splits (respect temporal order)
   - Station-based splits (test generalization)
   - Species-specific vs pooled models
   
2. **Interpretability Tools**
   - SHAP values for feature importance
   - Partial dependence plots
   - Local interpretable models (LIME)

### 1.4 Specific Analyses by Research Question

#### Q1: Which indices best predict species presence?
- Binary classification per species
- Multi-label classification for community
- Feature importance ranking

#### Q2: Can indices predict biodiversity metrics?
- Regression for species richness
- Shannon diversity prediction
- Acoustic vs biological diversity correlation

#### Q3: Do indices capture anthropogenic impacts?
- Vessel detection vs noise indices
- Anthropogenic vs biological index separation
- Temporal impact patterns

#### Q4: Are patterns consistent across years/stations?
- Model transfer between 2018↔2021
- Station-specific vs universal models
- Stability of index-detection relationships

## Part 2: Dashboard Design - Narrative Structure

### 2.1 Design Philosophy
**"Progressive Disclosure with Guided Discovery"**
- Start with the story, reveal complexity gradually
- Each page answers a specific question
- Build understanding step-by-step
- Allow both linear narrative and direct navigation

### 2.2 Proposed Site Architecture

```
Home (Landing)
├── The Challenge (Problem Statement)
│   └── Quick visual: Manual detection effort vs need for automation
│
├── Our Approach (Overview)
│   └── Interactive flowchart: Data → Analysis → Insights
│
└── Key Findings (Executive Summary)
    └── 3-4 major discoveries with visual previews

Data Overview (/data)
├── Study Sites (Interactive Map)
│   └── Station profiles with depth, location, characteristics
│
├── The Soundscape (/data/soundscape) - this would be v cool but I'd need to ask for the data
│   ├── Raw acoustic data examples (spectrograms)
│   └── What we're listening for (example sounds)
│
├── Manual Detections (/data/detections)
│   ├── Species catalog with images/sounds
│   ├── Detection effort timeline
│   └── Spatial distribution patterns
│
└── Acoustic Indices (/data/indices)
    ├── Index explorer (what each measures)
    ├── Index families (grouped by type)
    └── Computation examples

Analysis Journey (/analysis)
├── Step 1: Reducing Complexity (/analysis/reduction)
│   ├── The problem: 60+ indices
│   ├── Finding redundancy (correlation matrix)
│   ├── Information content analysis
│   └── Final selection: Key indices
│
├── Step 2: Finding Patterns (/analysis/patterns)
│   ├── Temporal rhythms (diel, seasonal)
│   ├── Spatial signatures (by station)
│   ├── PCA exploration (interactive 3D)
│   └── Clustering soundscapes
│
├── Step 3: Building Predictions (/analysis/models)
│   ├── Simple correlations first
│   ├── Model progression (simple → complex)
│   ├── Performance comparison
│   └── What works and why
│
└── Step 4: Validation (/analysis/validation)
    ├── Cross-year consistency
    ├── Cross-station generalization
    ├── Uncertainty quantification
    └── Limitations & caveats

Insights (/insights)
├── Key Indicators (/insights/indicators)
│   ├── Top 5 indices for biodiversity
│   ├── Species-specific indicators
│   └── Early warning signals
│
├── Practical Applications (/insights/applications)
│   ├── Monitoring protocol recommendations
│   ├── Cost-benefit analysis
│   └── Implementation guide
│
└── Future Directions (/insights/future)
    ├── Open questions
    ├── Data gaps
    └── Research priorities

Interactive Explorer (/explore)
├── Custom Analysis (power users)
├── Data Export
├── API Access
└── Reproducible Code

Methods (/methods)
├── Detailed Methodology
├── Statistical Approaches
├── Code Repository
└── Publications

### 2.3 Navigation Strategy

#### Primary Navigation (Header)
```
[Logo] Home | Data | Analysis | Insights | Explorer | Methods
```

#### Secondary Navigation (Context-aware)
- **Breadcrumbs**: Home > Analysis > Finding Patterns > PCA
- **Progress Indicator**: Step 2 of 4 in Analysis Journey
- **Next/Previous**: Guided flow through narrative

#### Quick Access (Sidebar when needed)
```
Jump to:
□ Executive Summary
□ Key Findings
□ Interactive Plots
□ Download Data
□ Methods
```

### 2.4 Page Design Patterns

#### Pattern A: "Overview → Detail" Pages
```typescript
// Structure for complex topics
<PageLayout>
  <HeroSection>
    <Title>Finding Patterns in the Soundscape</Title>
    <KeyInsight>3-5 acoustic indices explain 80% of biodiversity variation</KeyInsight>
    <PreviewVisualization /> {/* Simple, impactful chart */}
  </HeroSection>
  
  <TabbedContent>
    <Tab label="Quick Look">
      {/* 2-3 key charts with main findings */}
    </Tab>
    <Tab label="Deep Dive">
      {/* Detailed analysis, multiple charts */}
    </Tab>
    <Tab label="Methodology">
      {/* Technical details for researchers */}
    </Tab>
    <Tab label="Try It Yourself">
      {/* Interactive exploration tools */}
    </Tab>
  </TabbedContent>
  
  <NextSteps>
    <PreviousPage>Reducing Complexity</PreviousPage>
    <NextPage>Building Predictions</NextPage>
  </NextSteps>
</PageLayout>
```

#### Pattern B: "Guided Tutorial" Pages
```typescript
// For complex analyses
<TutorialLayout>
  <StepIndicator current={2} total={5} />
  
  <Step1_Context>
    <Explanation>Why we need dimension reduction</Explanation>
    <InteractivePlot>60 indices → confusion</InteractivePlot>
  </Step1_Context>
  
  <Step2_Method>
    <Explanation>How PCA works</Explanation>
    <AnimatedDiagram />
  </Step2_Method>
  
  <Step3_Application>
    <Explanation>PCA on our data</Explanation>
    <InteractivePCAPlot />
  </Step3_Application>
  
  <Step4_Interpretation>
    <Explanation>What the components mean</Explanation>
    <LoadingsTable />
  </Step4_Interpretation>
  
  <Step5_Insights>
    <KeyFindings />
    <ImplicationsForMonitoring />
  </Step5_Insights>
</TutorialLayout>
```

### 2.5 Performance Optimization Strategy

#### Data Loading
```typescript
// Progressive loading based on user journey
const useProgressiveData = (page: string) => {
  // Load only what's needed for current page
  const baseData = useBaseData(); // Lightweight summary
  const [detailData, setDetailData] = useState(null);
  
  // Prefetch next likely page data
  useEffect(() => {
    prefetchNextPageData(page);
  }, [page]);
  
  // Load details on demand
  const loadDetails = () => {
    // Lazy load heavy visualizations
  };
  
  return { baseData, detailData, loadDetails };
};
```

#### Visualization Strategy
1. **Thumbnail previews** → Click for full interactive
2. **Virtual scrolling** for long lists
3. **WebGL** for complex 3D plots (three.js)
4. **Canvas** for heatmaps over 10k points
5. **Progressive enhancement** (static → interactive)

### 2.6 User Personas & Paths

#### Persona 1: Research Scientist
**Path**: Methods → Analysis → Explorer
- Wants: Reproducibility, raw data, statistical details
- Solution: Deep-dive tabs, code snippets, data export

#### Persona 2: Marine Manager
**Path**: Home → Key Findings → Applications
- Wants: Practical recommendations, cost-benefit
- Solution: Executive summaries, decision tools

#### Persona 3: Curious Public
**Path**: Home → Data Overview → Insights
- Wants: Understanding, pretty visualizations
- Solution: Guided narrative, explanations, examples

#### Persona 4: Data Scientist
**Path**: Explorer → Methods → API
- Wants: Raw data, model details, reproducible code
- Solution: Jupyter exports, API access, GitHub links

## Part 3: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up analysis pipeline infrastructure
- [ ] Implement temporal alignment strategies
- [ ] Create correlation/redundancy analysis
- [ ] Build basic navigation structure

### Phase 2: Core Analysis (Week 3-4)
- [ ] Complete PCA implementation
- [ ] Build simple predictive models
- [ ] Create key visualizations
- [ ] Implement data overview pages

### Phase 3: Narrative Development (Week 5-6)
- [ ] Design and implement story flow
- [ ] Create interactive tutorials
- [ ] Build progressive disclosure UI
- [ ] Add context and explanations

### Phase 4: Advanced Features (Week 7-8)
- [ ] Implement complex models (if needed)
- [ ] Add interactive explorer
- [ ] Create export/API functionality
- [ ] Performance optimization

### Phase 5: Polish & Deploy (Week 9-10)
- [ ] User testing with target personas
- [ ] Refine based on feedback
- [ ] Documentation completion
- [ ] Production deployment

## Part 4: Key Design Decisions

### 4.1 Technology Choices
- **Analysis**: Python (scikit-learn, statsmodels, shap)
- **Visualization**: D3.js (custom), Plotly (3D), Nivo (standard charts)
- **Framework**: Next.js with app router
- **State**: Zustand for complex interactions
- **Styling**: Tailwind with custom scientific theme

### 4.2 Visual Design Language
- **Color Palette**: Ocean-inspired (deep blues → teals → warm accents)
- **Typography**: Clean, scientific (Inter for UI, Fira Code for data)
- **Charts**: Consistent, colorblind-friendly, print-safe
- **Interactions**: Smooth, purposeful, informative

### 4.3 Accessibility & Usability
- **Mobile**: Responsive but optimize for desktop (data complexity)
- **A11y**: WCAG AA compliance, keyboard navigation
- **Performance**: <3s initial load, <1s navigation
- **Export**: PNG charts, CSV data, PDF reports

## Part 5: Success Metrics

### Scientific Success
- [ ] Identify 3-5 key indices that predict biodiversity
- [ ] Achieve >70% classification accuracy for major species
- [ ] Demonstrate temporal/spatial consistency
- [ ] Provide actionable monitoring recommendations

### User Experience Success
- [ ] 80% of users can find key insights within 5 minutes
- [ ] Scientists can reproduce all analyses
- [ ] Managers can extract decision-relevant information
- [ ] Public understands the research importance

### Technical Success
- [ ] All pages load in <3 seconds
- [ ] Zero critical accessibility issues
- [ ] 100% reproducible analysis pipeline
- [ ] Complete API documentation

## Next Steps

1. **Immediate**: Start with correlation analysis to reduce indices
2. **This Week**: Implement PCA and basic predictive models
3. **Next Week**: Design navigation structure and first 3 pages
4. **Ongoing**: Iterate based on analysis results and user feedback

---

*This document is a living guide that will evolve as we discover patterns in the data and refine our approach based on user needs.*