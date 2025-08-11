# Site Restructuring Plan: Soundscape Biodiversity Dashboard

## Core Research Question
**"Can acoustic indices help us predict soundscape biodiversity and serve as proxies for more complex marine biodiversity monitoring?"**

## Research Narrative
This dashboard explores whether computed acoustic indices can replace or supplement expensive, labor-intensive species detection methods for understanding marine soundscape biodiversity. We focus on identifying which indices are most informative for biodiversity assessment and understanding the environmental factors that might influence these relationships.

## Site Structure & Implementation Plan

### **Page 1: `/` - Overview & Introduction**
**Status**: ✅ Completed (current homepage)
**Purpose**: Entry point that establishes the research question and shows data scope
**Content**:
- Hero: "Marine Soundscape Biodiversity Observatory"
- Tagline: "Exploring relationships between computed acoustic indices and species presence using data collected at three stations in May River, South Carolina"
- Current species activity heatmap
- Key metrics: detections, species, stations, timeframe
- Navigation to analysis pages

### **Page 2: `/acoustic-biodiversity` - Primary Analysis Page**
**Status**: 🚧 To implement (replaces current `/species`)
**Purpose**: Core research question - which acoustic indices predict soundscape biodiversity?
**Priority**: **HIGH - Primary deliverable**

**Content Sections**:
1. **Research Question** (science communication)
   - "Can we use acoustic indices to predict marine biodiversity?"
   - Brief explanation of acoustic indices vs manual annotations
   - Why this matters (cost, scalability, automation)

2. **Index Performance Analysis**
   - PCA visualization: which indices cluster with species detections
   - Correlation heatmap: indices vs species presence
   - Ranked list: "Top 10 Most Informative Indices"
   - Interactive: select species to see which indices correlate

3. **Species vs Anthropogenic Signals**
   - Distribution plots by annotation type
   - Can indices differentiate biological vs human-made sounds?
   - Focus on vessel, chain, unknown anthropogenic vs biological species

4. **Biodiversity Prediction Models** (future)
   - Which combination of indices best predicts species richness?
   - Validation across different time periods

**Visualizations Needed**:
- PCA biplot (indices + species loadings)
- Correlation matrix heatmap
- Distribution plots by annotation type
- Performance ranking chart

### **Page 3: `/environmental-factors` - Environmental Influences**
**Status**: 🚧 To implement (replaces current `/temporal`)
**Purpose**: Do environmental factors confound acoustic indices?
**Priority**: **MEDIUM-HIGH - Critical for interpretation**

**Content Sections**:
1. **Environmental Confounders**
   - "Do temperature and depth affect acoustic indices?"
   - Correlation analysis: temp/depth vs each index
   - Need for environmental correction?

2. **Seasonal Patterns**
   - Are indices driven by seasonal biology or seasonal environment?
   - Monthly patterns in indices vs species activity
   - Temperature/depth seasonal cycles

3. **Spatial Factors** (future implementation)
   - Distance from river mouth effects
   - Proximity to marinas/shipping lanes
   - Station-specific environmental profiles

4. **Correction Models**
   - Should indices be adjusted for environmental conditions?
   - Raw vs environmentally-corrected indices performance

**Visualizations Needed**:
- Scatterplots: indices vs temperature/depth
- Seasonal decomposition plots
- Before/after correction comparisons
- Station environmental profiles

### **Page 4: `/acoustic-glossary` - Understanding Acoustic Indices**
**Status**: 🚧 To implement (new page)
**Purpose**: Science communication - explain the 60+ acoustic indices
**Priority**: **MEDIUM - Supporting education**

**Content Sections**:
1. **What Are Acoustic Indices?**
   - Plain language explanation
   - Why use indices instead of raw audio?
   - How they relate to soundscape biodiversity

2. **Index Categories**
   - Organize by what they measure (frequency, amplitude, complexity, etc.)
   - Biological relevance of each category
   - Examples with actual audio/spectrogram samples

3. **Interactive Index Explorer**
   - Select an index → see definition, formula, biological meaning
   - Show examples from actual data
   - "Most useful for biodiversity" highlighting

4. **Current vs Future Data**
   - Current: rmsSPL (with known issues)
   - Future: 60 indices at 5-minute resolution

**Visualizations Needed**:
- Interactive index selector
- Spectrogram examples
- Category organization chart
- Data availability timeline

### **Page 5: `/stations` - Station Profiles & Context**
**Status**: ✅ Basic version exists, needs enhancement
**Purpose**: Spatial context and deployment details
**Priority**: **LOW-MEDIUM - Supporting context**

**Content Sections**:
1. **Station Locations & Characteristics**
   - Enhanced map with river mouth, marina locations
   - Environmental characteristics (depth, temperature ranges)
   - Known anthropogenic sources nearby

2. **Deployment Timeline**
   - When each station was active
   - Data quality notes and known issues
   - Equipment specifications

3. **Comparative Profiles**
   - Species diversity by station
   - Environmental conditions by station
   - Acoustic index patterns by station

**Enhancements Needed**:
- Add river mouth, marina locations to map
- Deployment timeline visualization
- Station comparison charts

### **Page 6: `/explorer` - Data Explorer**
**Status**: ✅ Placeholder exists, keep as-is
**Purpose**: Raw data exploration for researchers
**Priority**: **LOW - Advanced users only**

## Implementation Phases

### **Phase 1: Core Analysis (Weeks 1-2)**
Priority order for immediate implementation:

1. **`/acoustic-biodiversity` page** - The primary research deliverable
   - PCA analysis of indices vs species
   - Correlation matrices
   - Index performance ranking
   - Species vs anthropogenic distributions

2. **Data processing updates** - Add 60 future acoustic indices structure
   - Prepare for when full acoustic index data becomes available
   - Update data loading hooks

### **Phase 2: Environmental Context (Week 3)**
3. **`/environmental-factors` page**
   - Temperature/depth correlation analysis
   - Seasonal pattern decomposition
   - Environmental correction models

### **Phase 3: Education & Context (Week 4)**
4. **`/acoustic-glossary` page**
   - Index definitions and explanations
   - Interactive examples

5. **Enhanced `/stations` page**
   - Spatial context improvements
   - Deployment timeline

## Science Communication Guidelines

### **Jargon Management**
- **Always explain on first use**: "Acoustic indices (computed metrics that summarize audio recordings)"
- **Progressive disclosure**: Simple explanation → technical details → mathematical formulation
- **Visual examples**: Show spectrograms, audio examples where possible
- **Glossary tooltips**: Hover definitions for technical terms

### **Research Narrative Flow**
1. **Problem**: Manual species detection is expensive and time-intensive
2. **Hypothesis**: Acoustic indices can predict soundscape biodiversity
3. **Method**: Compare indices to manual annotations across 3 stations, 2018-2021
4. **Results**: Which indices work best? What affects them?
5. **Implications**: Cost-effective biodiversity monitoring potential

### **Target Audiences**
- **Primary**: Marine biologists, acoustics researchers
- **Secondary**: Conservation practitioners, resource managers
- **Tertiary**: Graduate students, interested public

## Technical Implementation Notes

### **New Page Structure**
Update Next.js app router:
```
src/app/
├── page.tsx                    # Overview (current)
├── acoustic-biodiversity/      # NEW - Primary analysis
├── environmental-factors/      # NEW - Environmental analysis  
├── acoustic-glossary/         # NEW - Index education
├── stations/                  # ENHANCE existing
└── explorer/                  # KEEP existing
```

### **Data Requirements**
- Current detection data (species annotations)
- Current environmental data (temp/depth)
- Current acoustic data (rmsSPL - with known issues)
- Future: 60 acoustic indices at 5-minute resolution
- Spatial data: river mouth, marina locations

### **New Visualizations Needed**
1. **PCA biplot** - Observable Plot + D3 for interactive loadings
2. **Correlation heatmaps** - Observable Plot cell marks
3. **Distribution plots** - Observable Plot histograms/density plots
4. **Scatterplot matrices** - Observable Plot faceted plots
5. **Index performance rankings** - Observable Plot bar charts

### **Navigation Updates**
Update main navigation to reflect research flow:
```
Overview → Acoustic Analysis → Environmental Factors → Index Guide → Station Info → Data Explorer
```

## Success Metrics

### **Research Impact**
- Clear answer to: "Which acoustic indices best predict marine biodiversity?"
- Environmental correction recommendations
- Cost-effectiveness analysis for monitoring programs

### **Science Communication**
- Non-experts can understand the research question and findings
- Researchers can dive deep into technical details
- Visualizations tell compelling story about soundscape biodiversity

### **Technical Performance**
- All pages load quickly with Observable Plot visualizations
- Interactive elements respond smoothly
- Mobile-friendly design maintained

This restructuring transforms the dashboard from a generic data viewer into a focused research communication tool that directly addresses the core question of using acoustic indices for biodiversity monitoring.