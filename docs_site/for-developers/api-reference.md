# API Reference

Documentation for the data loading API and TypeScript interfaces used in the dashboard.

!!! note "Static Data API"
    This project uses a static data API - all data is pre-processed and served as JSON files from CDN. There are no dynamic API endpoints.

## Data Loading Hooks

### Core Data Hooks

#### `useDetections()`
Loads species detection data from manual annotations.

```typescript
const { data, error, isLoading } = useDetections()

// Returns: DetectionRecord[]
interface DetectionRecord {
  station: string           // "9M", "14M", "37M"
  year: number             // 2018, 2021  
  date: string             // "2021-05-15"
  date_time?: string       // "2021-05-15T10:00:00Z"
  [speciesCode: string]: string | number | undefined  // Species detection counts
}
```

#### `useIndices()`
Loads processed acoustic indices data.

```typescript
const { data, error, isLoading } = useIndices()

// Returns: AcousticIndicesRecord[]
interface AcousticIndicesRecord {
  station: string          // "9M", "14M", "37M"
  year: number            // 2018, 2021
  date: string            // "2021-05-15"
  datetime: string        // "2021-05-15T10:00:00Z"
  window_start: string    // "2021-05-15T10:00:00Z"
  window_end: string      // "2021-05-15T12:00:00Z"
  data_quality: number    // 0.0-1.0 quality score
  missing_data_percent: number  // 0.0-1.0 missing data ratio
  
  // Acoustic indices (56+ indices)
  ZCR?: number            // Zero crossing rate
  MEANt?: number          // Temporal mean
  VARt?: number           // Temporal variance
  ACI?: number            // Acoustic complexity index
  NDSI?: number           // Normalized difference soundscape index
  // ... all other acoustic indices
}
```

#### `useEnvironmental()`
Loads temperature and depth measurements.

```typescript
const { data, error, isLoading } = useEnvironmental()

// Returns: EnvironmentalRecord[]
interface EnvironmentalRecord {
  station: string         // "9M", "14M", "37M"
  year: number           // 2018, 2021
  datetime: string       // "2021-05-15T10:30:00Z"
  temperature?: number   // Celsius
  depth?: number         // Meters
  data_quality: number   // Quality indicator
}
```

#### `useAnalysis()`
Loads PCA and correlation analysis results.

```typescript
const { data, error, isLoading } = useAnalysis()

// Returns: AnalysisResults
interface AnalysisResults {
  pca: {
    loadings: PCALoadings[]
    scores: PCAScores[]
    explained_variance: ExplainedVariance[]
    super_indices: string[]
  }
  correlations: {
    index_species: CorrelationMatrix
    index_environmental: CorrelationMatrix
    component_species: CorrelationMatrix
  }
  summaries: {
    index_rankings: IndexRanking[]
    species_predictions: SpeciesPrediction[]
  }
}
```

#### `useMetadata()`
Loads dataset metadata and summary statistics.

```typescript
const { data, error, isLoading } = useMetadata()

// Returns: DatasetMetadata
interface DatasetMetadata {
  processing_date: string
  pipeline_version: string
  data_sources: DataSource[]
  summary_stats: SummaryStatistics
  quality_report: QualityReport
}
```

### Composite Hooks

#### `useCoreData()`
Loads all primary datasets simultaneously.

```typescript
const { 
  detections, 
  indices, 
  analysis, 
  metadata,
  isLoading,
  hasError 
} = useCoreData()

// Combines all individual hooks for full dataset access
```

#### `useFilteredData(filters: FilterOptions)`
Loads data with applied filters.

```typescript
interface FilterOptions {
  stations?: string[]        // Filter by stations
  species?: string[]         // Filter by species
  dateRange?: [Date, Date]   // Filter by date range
  indices?: string[]         // Filter by acoustic indices
  qualityThreshold?: number  // Minimum data quality
}

const { data, isLoading } = useFilteredData({
  stations: ['9M', '14M'],
  dateRange: [new Date('2021-01-01'), new Date('2021-12-31')],
  qualityThreshold: 0.8
})
```

## TypeScript Interfaces

### Primary Data Types

#### Detection Data
```typescript
interface DetectionRecord {
  // Core identifiers
  station: string
  year: number
  date: string
  date_time?: string
  
  // Species detection columns (dynamic based on data)
  [speciesCode: string]: string | number | undefined
}

interface Species {
  code: string              // "sp", "otbw", "bde"
  name: string             // "Silver perch", "Oyster toadfish boat whistle"
  category: string         // "Fish", "Marine Mammal", "Crustacean"
  detection_count: number  // Total detections across all records
}
```

#### Acoustic Indices Data
```typescript
interface AcousticIndicesRecord {
  // Core metadata
  station: string
  year: number
  date: string
  datetime: string
  window_start: string
  window_end: string
  
  // Data quality indicators
  data_quality: number
  missing_data_percent: number
  interpolated_windows: number
  
  // Temporal domain indices
  ZCR?: number            // Zero crossing rate
  MEANt?: number          // Temporal mean amplitude
  VARt?: number           // Temporal variance  
  SKEWt?: number          // Temporal skewness
  KURTt?: number          // Temporal kurtosis
  LEQt?: number           // Temporal equivalent sound level
  
  // Frequency domain indices
  MEANf?: number          // Frequency mean
  VARf?: number           // Frequency variance
  SKEWf?: number          // Frequency skewness
  KURTf?: number          // Frequency kurtosis
  NBPEAKS?: number        // Number of spectral peaks
  LEQf?: number           // Frequency equivalent sound level
  
  // Complexity indices
  ACI?: number            // Acoustic complexity index
  NDSI?: number           // Normalized difference soundscape index
  ADI?: number            // Acoustic diversity index
  AEI?: number            // Acoustic evenness index
  
  // Diversity indices
  H_Havrda?: number       // Havrda-Charvat entropy
  H_Renyi?: number        // Renyi entropy
  H_pairedShannon?: number // Paired Shannon diversity
  RAOQ?: number           // Rao's Q diversity
  
  // Bioacoustic indices  
  BioEnergy?: number      // Biological energy
  AnthroEnergy?: number   // Anthropogenic energy
  BI?: number             // Bioacoustic index
  rBA?: number            // Relative bioacoustic activity
  
  // Spectral coverage
  LFC?: number            // Low frequency coverage
  MFC?: number            // Mid frequency coverage
  HFC?: number            // High frequency coverage
  
  // Additional indices (extensible)
  [indexName: string]: string | number | undefined
}
```

### Analysis Results Types

#### PCA Results
```typescript
interface PCALoadings {
  index_name: string      // Acoustic index name
  PC1: number            // Loading on first component
  PC2: number            // Loading on second component  
  PC3: number            // Loading on third component
  // ... additional components
}

interface PCAScores {
  station: string
  year: number
  datetime: string
  PC1: number            // Score on first component
  PC2: number            // Score on second component
  PC3: number            // Score on third component
  // ... additional components  
}

interface ExplainedVariance {
  component: string      // "PC1", "PC2", etc.
  variance_explained: number     // Individual variance
  cumulative_variance: number    // Cumulative variance
}
```

#### Correlation Results
```typescript
interface CorrelationMatrix {
  [rowKey: string]: {
    [colKey: string]: number  // Correlation coefficient
  }
}

interface IndexRanking {
  index_name: string
  importance_score: number   // Overall importance (0-1)
  species_correlation: number // Max species correlation
  pca_contribution: number   // Max PCA loading
  category: string          // Index category
}
```

### Metadata Types

#### Station Information
```typescript
interface Station {
  code: string              // "9M", "14M", "37M"
  name: string             // "Station 9M"
  latitude: number         // Decimal degrees
  longitude: number        // Decimal degrees
  depth_mean: number       // Average deployment depth (meters)
  distance_from_mouth: number // Distance from river mouth (km)
  deployment_periods: DeploymentPeriod[]
}

interface DeploymentPeriod {
  start_date: string       // "2021-05-01T00:00:00Z"
  end_date: string         // "2021-08-31T23:59:59Z"
  equipment: string        // Equipment type/model
  sample_rate: number      // Audio sample rate (Hz)
  notes?: string          // Deployment notes
}
```

#### Data Quality
```typescript
interface QualityReport {
  total_records: number
  records_by_station: { [station: string]: number }
  missing_data_summary: {
    detection_data: number    // Percentage missing
    acoustic_indices: number  // Percentage missing  
    environmental_data: number // Percentage missing
  }
  data_coverage: {
    start_date: string
    end_date: string
    gaps: DateGap[]
  }
}

interface DateGap {
  start_date: string
  end_date: string
  affected_stations: string[]
  reason?: string          // Reason for gap if known
}
```

## Utility Functions

### Data Processing Utilities

```typescript
// Filter data by criteria
function filterDetections(
  data: DetectionRecord[], 
  filters: FilterOptions
): DetectionRecord[]

// Join detection and indices data  
function joinDetectionIndices(
  detections: DetectionRecord[],
  indices: AcousticIndicesRecord[]
): CombinedRecord[]

// Calculate species detection rates
function calculateDetectionRates(
  data: DetectionRecord[],
  species: string[]
): { [species: string]: number }

// Get data quality summary
function getQualitySummary(
  data: AcousticIndicesRecord[]
): QualitySummary
```

### Chart Data Transformation

```typescript
// Transform data for Observable Plot
function transformForPlot(
  data: any[],
  config: PlotConfig
): PlotData[]

// Create heatmap data structure
function createHeatmapData(
  data: DetectionRecord[],
  species: string[]
): HeatmapData[]

// Prepare time series data
function prepareTimeSeriesData(
  data: AcousticIndicesRecord[],
  indices: string[]
): TimeSeriesData[]
```

## Error Handling

### Data Loading Errors
```typescript
interface DataError {
  type: 'network' | 'parsing' | 'validation'
  message: string
  details?: any
}

// Error boundaries catch data loading failures
// Fallback to cached data when possible
// Display user-friendly error messages
```

### Data Validation
```typescript
// Validate data structure on load
function validateDetectionData(data: any[]): ValidationResult
function validateIndicesData(data: any[]): ValidationResult
function validateAnalysisData(data: any): ValidationResult

interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
}
```

This API provides type-safe access to all project data with comprehensive error handling and validation.