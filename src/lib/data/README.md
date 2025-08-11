# Data Processing & Validation

This directory contains client-side data processing utilities and validation functions.

## Planned Utilities

- **dataValidation.ts**: Client-side validation for loaded JSON data
- **dataTransforms.ts**: Data transformation utilities for chart preparation
- **aggregationUtils.ts**: Data aggregation functions for statistics and summaries
- **cacheUtils.ts**: IndexedDB caching for offline data access
- **exportUtils.ts**: Data export formatting (CSV, JSON, Excel)

## Data Flow

Client-side data processing supplements the Python-based data pipeline:

1. **Load**: Fetch processed JSON from CDN
2. **Validate**: Check data integrity and completeness
3. **Transform**: Convert to chart-ready formats
4. **Cache**: Store in IndexedDB for offline access
5. **Export**: Format for user download

## Usage

Data utilities work with the standardized interfaces from `/src/lib/hooks/useData.ts`:

```typescript
import { validateDetectionData, transformForChart } from '@/lib/data';

const processChartData = (detections: Detection[]) => {
  const errors = validateDetectionData(detections);
  if (errors.length > 0) {
    console.warn('Data validation issues:', errors);
  }
  
  return transformForChart(detections, {
    groupBy: 'station',
    timeInterval: 'month'
  });
};
```