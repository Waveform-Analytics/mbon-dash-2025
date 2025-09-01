# Acoustic Indices Heatmap Implementation Plan

## Overview

This document outlines the implementation plan for creating a progressive loading acoustic indices heatmap that can handle large datasets (279MB+) efficiently by loading only the data needed for the current user selection.

## Architecture

### Current Problem
- `compiled_indices.json` is 279MB
- Loading entire file in browser causes performance issues
- Need to show hour-of-day vs date heatmap (same structure as detections)

### Solution: Progressive Loading
```
User Selection → API Filtering → Small Data Response → Fast Visualization
```

### Data Flow
1. User selects: "ACI index, Station 14M, 2021, 8kHz"
2. Browser requests filtered data from API
3. Vercel server loads 279MB file, filters for specific parameters
4. Server returns ~2MB of filtered data
5. Browser renders heatmap quickly

## Implementation Phases

### Phase 1: Build Progressive Loading System (Local Development)

#### Step 1: Create API Endpoint
**File**: `dashboard/src/app/api/indices-heatmap/route.ts`
**Purpose**: Server-side data filtering
**Functionality**:
- Accept filter parameters (index, station, year, bandwidth)
- Load 279MB file from local path
- Filter data for specific selection
- Return ~2MB of filtered data
- Implement error handling and memory management
- Add performance monitoring and caching

#### Step 2: Create Custom Hook
**File**: `dashboard/src/lib/data/useIndicesHeatmap.ts`
**Purpose**: Manage data fetching and state
**Functionality**:
- Watch for user selections
- Make API requests
- Handle loading/error states
- Return data to component
- Implement request deduplication

#### Step 3: Create React Component
**File**: `dashboard/src/components/charts/AcousticIndicesHeatmap.tsx`
**Purpose**: User interface and visualization
**Functionality**:
- Show dropdown controls (index, station, year, bandwidth)
- Render D3 heatmap (hour-of-day vs date)
- Handle user interactions
- Match structure of AcousticDetectionHeatmap
- Add error boundaries and loading states

#### Step 4: Integrate into Explore Page
**File**: `dashboard/src/app/explore/page.tsx`
**Purpose**: Add new component to page
**Functionality**:
- Import new heatmap component
- Add to page layout
- Provide context and styling

### Phase 2: Test and Deploy

#### Step 5: Local Testing
- Test API endpoint with different parameters
- Verify data filtering works correctly
- Test component with various selections
- Ensure heatmap renders properly
- Test on mobile devices
- Validate error handling scenarios
- Test memory usage and performance

#### Step 6: Deploy to Vercel
- Deploy Next.js app to Vercel
- Test API endpoint on Vercel
- Verify everything works in production environment
- Test with local data file
- Monitor performance and memory usage

### Phase 3: CDN Integration (When Ready)

#### Step 7: Set Up CDN
- Choose CDN provider (AWS S3, Cloudflare, etc.)
- Upload `compiled_indices.json` to CDN
- Get CDN URL for file access
- Implement CDN health checks

#### Step 8: Update API Endpoint
- Modify API route to fetch from CDN
- Add environment variables for CDN URL
- Test CDN data loading
- Implement fallback to local if needed
- Add CDN performance monitoring

## File Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── indices-heatmap/
│   │   │       └── route.ts          ← NEW
│   │   └── explore/
│   │       └── page.tsx              ← MODIFY
│   ├── components/
│   │   └── charts/
│   │       └── AcousticIndicesHeatmap.tsx  ← NEW
│   ├── lib/
│   │   └── data/
│   │       └── useIndicesHeatmap.ts        ← NEW
│   └── types/
│       └── indices.ts                       ← NEW
└── data/
    └── processed/
        └── compiled_indices.json           ← EXISTING
```

## Technical Details

### API Endpoint Design
- **Route**: `/api/indices-heatmap`
- **Parameters**: `index`, `station`, `year`, `bandwidth`
- **Response**: Filtered JSON data with metadata
- **Data Source**: Local file (dev) → CDN (prod)
- **Memory Management**: Streaming/chunked processing
- **Caching**: Redis or in-memory cache for repeated requests
- **Error Handling**: Comprehensive error responses

### Component Design
- **Controls**: Dropdown selectors for all parameters
- **Visualization**: D3 heatmap matching detections structure
- **Responsive**: Works on mobile and desktop
- **Performance**: Only loads data when selections change
- **Error Boundaries**: Graceful error handling
- **Loading States**: Clear user feedback

### Data Transformation
- **Input**: Raw indices data with multiple columns
- **Output**: Heatmap format with date, hour, value structure
- **Filtering**: Only include non-null values for selected index
- **Aggregation**: None - preserve individual data points
- **Validation**: Type checking and data integrity validation

## Risk Mitigation Strategy

### Memory Management
- **Problem**: 279MB file may exceed Vercel serverless memory limits
- **Solution**: Implement streaming/chunked processing
- **Fallback**: Reduce data granularity or implement pagination
- **Monitoring**: Track memory usage and optimize as needed

### Error Handling
- **File Loading Errors**: Graceful degradation with user feedback
- **Network Issues**: Retry logic with exponential backoff
- **Invalid Parameters**: Input validation and helpful error messages
- **Server Limits**: Handle 413 Payload Too Large responses
- **CDN Failures**: Fallback to local data source

### Performance Optimization
- **Caching Strategy**: Cache filtered results to avoid reprocessing
- **Request Deduplication**: Prevent duplicate API calls
- **Data Compression**: Compress responses when beneficial
- **Lazy Loading**: Load data only when needed
- **Monitoring**: Track response times and optimize bottlenecks

## Data Validation Strategy

### Type Definitions
```typescript
// types/indices.ts
interface IndicesDataPoint {
  date: string;
  hour: number;
  index_name: string;
  value: number;
  station: string;
  year: number;
  bandwidth: string;
}

interface IndicesHeatmapData {
  metadata: {
    available_indices: string[];
    stations: string[];
    years: number[];
    bandwidths: string[];
    value_ranges: Record<string, [number, number]>;
  };
  data: IndicesDataPoint[];
}

interface FilterParams {
  index: string;
  station: string;
  year: number;
  bandwidth: string;
}
```

### Validation Rules
- Validate all filter parameters before processing
- Ensure data structure matches expected format
- Check for required fields in each data point
- Validate date formats and ranges
- Handle missing or null values gracefully

## Caching Implementation

### Cache Strategy
```typescript
// Cache key format: indices-{index}-{station}-{year}-{bandwidth}
const cacheKey = `indices-${index}-${station}-${year}-${bandwidth}`;

// Check cache first
const cached = await cache.get(cacheKey);
if (cached) {
  return NextResponse.json(JSON.parse(cached));
}

// Process and cache result
const filteredData = await processData(params);
await cache.set(cacheKey, JSON.stringify(filteredData), '1h');
```

### Cache Configuration
- **TTL**: 1 hour for filtered results
- **Storage**: Redis (production) or in-memory (development)
- **Invalidation**: Manual cache clearing when data updates
- **Size Limits**: Monitor cache size and implement LRU eviction

## Performance Monitoring

### Metrics to Track
- API response times (target: < 2 seconds)
- Memory usage during processing
- Cache hit rates
- Error rates by type
- Data filtering efficiency
- User interaction patterns

### Implementation
```typescript
// Performance tracking in API route
const startTime = Date.now();
const startMemory = process.memoryUsage();

// ... processing ...

const duration = Date.now() - startTime;
const memoryUsed = process.memoryUsage().heapUsed - startMemory.heapUsed;

console.log(`Indices heatmap: ${duration}ms, ${memoryUsed} bytes, ${filteredData.length} records`);
```

## Success Criteria

- [ ] Heatmap loads in < 2 seconds
- [ ] User can change selections and see new data quickly
- [ ] Works on mobile devices without crashes
- [ ] No memory issues or browser slowdowns
- [ ] Same temporal structure as detections heatmap
- [ ] Handles all 60+ acoustic indices
- [ ] Supports all 3 stations and 2 years
- [ ] Works with both bandwidth options
- [ ] Graceful error handling for all failure scenarios
- [ ] Cache hit rate > 80% for repeated requests
- [ ] Memory usage stays within Vercel limits
- [ ] Comprehensive logging and monitoring

## Timeline

- **Phase 1**: 2-3 days (build the system with error handling)
- **Phase 2**: 1-2 days (test and deploy with monitoring)
- **Phase 3**: 1 day (CDN integration, when ready)

## Development Workflow

### Local Development
1. Ensure `compiled_indices.json` is in correct location
2. Create API endpoint with local file support and error handling
3. Build and test components locally with comprehensive testing
4. Verify data filtering, validation, and visualization
5. Test error scenarios and edge cases

### Production Deployment
1. Deploy Next.js app to Vercel
2. Test API endpoints on Vercel with monitoring
3. Verify performance and functionality under load
4. Monitor for memory issues and optimize as needed
5. Set up alerting for performance degradation

### CDN Integration (Future)
1. Upload data to CDN with proper caching headers
2. Update environment variables and health checks
3. Test CDN data loading with fallback mechanisms
4. Monitor CDN performance and costs
5. Remove local file dependencies

## Environment Configuration

### Development
```env
DATA_SOURCE=local
LOCAL_DATA_PATH=../data/processed/compiled_indices.json
CACHE_ENABLED=false
LOG_LEVEL=debug
```

### Production
```env
DATA_SOURCE=cdn
CDN_URL=https://your-cdn-bucket.com
CACHE_ENABLED=true
REDIS_URL=your-redis-url
LOG_LEVEL=info
```

## Testing Strategy

### API Testing
```bash
# Test local API endpoint
curl "http://localhost:3000/api/indices-heatmap?index=ACI&station=14M&year=2021&bandwidth=8kHz"

# Test error scenarios
curl "http://localhost:3000/api/indices-heatmap?index=INVALID&station=14M&year=2021&bandwidth=8kHz"

# Test performance
time curl "http://localhost:3000/api/indices-heatmap?index=ACI&station=14M&year=2021&bandwidth=8kHz"
```

### Component Testing
- Test with different index selections
- Test with different stations/years/bandwidths
- Test on different screen sizes
- Test loading and error states
- Test cache behavior and performance
- Test error boundary scenarios

### Performance Testing
- Measure initial load time
- Measure data switching time
- Test memory usage under load
- Verify no browser crashes
- Test concurrent user scenarios
- Monitor cache effectiveness

## Dependencies

- **Next.js**: API routes and React framework
- **D3.js**: Heatmap visualization
- **React Hooks**: State management
- **TypeScript**: Type safety
- **Redis**: Caching (production)
- **Zod**: Data validation
- **Winston**: Logging and monitoring

## Notes

- This approach works with existing CDN setup
- No FastAPI needed - uses Next.js API routes
- Vercel handles the heavy lifting of processing large files
- Browser only receives filtered, manageable data
- System scales to handle larger datasets in the future
- Comprehensive error handling ensures reliability
- Caching strategy improves performance for repeated requests
- Monitoring provides visibility into system health

## Next Steps

1. Start with Step 1: Create the API endpoint with error handling
2. Test locally with your data and edge cases
3. Build incrementally: hook → component → integration
4. Deploy early to catch any Vercel-specific issues
5. Add CDN integration when ready
6. Monitor and optimize based on real usage patterns

---

**Last Updated**: [Current Date]
**Status**: Planning Phase
**Priority**: High
