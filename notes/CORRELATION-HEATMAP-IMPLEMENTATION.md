# Correlation Heatmap with Dendrogram Implementation Guide

## Overview
Interactive visualization showing the 61x61 correlation matrix of acoustic indices with hierarchical clustering dendrogram. This explains how acoustic indices were clustered for dimensionality reduction.

## Layout Design

```
┌─────────┬─────────────────────────┬──────────┐
│[corner1]│   Column Labels (sticky)│[corner2] │
├─────────┼─────────────────────────┼──────────┤
│Row      │  Scrollable Heatmap     │Dendrogram│
│Labels   │      Matrix             │ (sticky) │
│(sticky) │                         │          │
└─────────┴─────────────────────────┴──────────┘
```

## Technical Requirements

### Data Preparation
1. **Correlation Matrix**: Need 61x61 correlation matrix between all acoustic indices
2. **Clustering Results**: Hierarchical clustering dendrogram data
3. **Index Metadata**: Names, cluster assignments, selection status

### Layout Specifications
- **Fixed card width**: 1000-1200px total
- **Row labels**: ~100px width, sticky left
- **Column labels**: ~30px height, sticky top
- **Dendrogram**: ~150px width, always visible right
- **Matrix cells**: ~8-10px each for readability
- **Corners**: Match label dimensions

### Sticky Positioning Strategy
1. **Corner 1** (top-left): Always fixed
2. **Corner 2** (top-right): Always fixed
3. **Column labels**: Sticky top, scroll horizontally with matrix
4. **Row labels**: Sticky left, scroll vertically with matrix
5. **Dendrogram**: Always visible, matches matrix height
6. **Matrix**: Scrollable both directions

### Visual Design
- **Cluster grouping**: Sort/group indices by cluster_id so similar ones are adjacent
- **Color coding**:
  - Correlation strength: Blue (negative) → White (zero) → Red (positive)
  - Cluster borders: Subtle borders around cluster groups in labels
  - Representative indices: Highlighted in labels (red text or background)
- **Labels**:
  - Rotated column labels (-45° or -90°)
  - Abbreviated index names if too long
  - Cluster color coding in label backgrounds

## Implementation Components

### 1. Data Generation (Python/Notebook)
```python
# Generate correlation matrix
correlation_matrix = indices_df.corr()

# Perform hierarchical clustering
from scipy.cluster.hierarchy import linkage, dendrogram
linkage_matrix = linkage(correlation_matrix, method='ward')
dendrogram_data = dendrogram(linkage_matrix, no_plot=True)

# Export for frontend
{
  "correlation_matrix": correlation_matrix.to_dict(),
  "dendrogram": dendrogram_data,
  "index_metadata": cluster_metadata,
  "index_order": ordered_index_names
}
```

### 2. React Component Structure
```tsx
<div className="correlation-heatmap-container">
  <div className="heatmap-grid">
    <div className="corner-1">Corner</div>
    <div className="column-labels sticky-top">
      {/* Scrolls horizontally with matrix */}
    </div>
    <div className="corner-2">Corner</div>

    <div className="row-labels sticky-left">
      {/* Scrolls vertically with matrix */}
    </div>
    <div className="matrix-container">
      {/* Main scrollable correlation matrix */}
    </div>
    <div className="dendrogram-container">
      {/* Always visible dendrogram */}
    </div>
  </div>
</div>
```

### 3. D3.js Implementation
- **Matrix rendering**: SVG rect elements for correlation cells
- **Dendrogram**: SVG path elements for tree structure
- **Synchronized scrolling**: Event listeners to sync label scrolling
- **Tooltips**: Show correlation values and index names on hover
- **Color scales**: d3.scaleSequential for correlation colors

## CSS Grid Layout
```css
.heatmap-grid {
  display: grid;
  grid-template-columns: 100px 1fr 150px;
  grid-template-rows: 30px 1fr;
  width: 1200px;
  height: 800px;
}

.matrix-container {
  overflow: auto;
  position: relative;
}

.sticky-top, .sticky-left {
  position: sticky;
  background: white;
  z-index: 10;
}
```

## Interaction Features
1. **Tooltips**: Hover to see correlation value and index names
2. **Cluster highlighting**: Click cluster in dendrogram to highlight matrix block
3. **Representative highlighting**: Visual emphasis on selected representative indices
4. **Zoom**: Optional zoom controls for matrix cells

## File Locations
- **Component**: `dashboard/components/CorrelationHeatmap.tsx`
- **Data generation**: Add to `python/scripts/notebooks/10_view_generation.py`
- **Data output**: `data/views/correlation_heatmap.json`
- **Page integration**: `dashboard/app/explore/index-reduction/page.tsx`

## Implementation Steps
1. Generate correlation matrix and dendrogram data in Python
2. Create basic React component structure with CSS Grid
3. Implement D3.js matrix visualization
4. Add dendrogram visualization
5. Implement sticky positioning for labels
6. Add interactive features (tooltips, highlighting)
7. Style and polish visual design
8. Test scrolling behavior and responsiveness

## Notes
- Consider performance with 61x61 = 3,721 matrix cells
- May need virtualization if rendering becomes slow
- Ensure dendrogram aligns perfectly with matrix rows/columns
- Test sticky positioning across different browsers