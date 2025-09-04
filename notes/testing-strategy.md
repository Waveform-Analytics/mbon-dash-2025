# MBON Dashboard Testing Strategy

## Overview

This document outlines a comprehensive testing strategy to catch issues early and ensure data consistency across the MBON dashboard pipeline. The strategy addresses three critical areas: Python data processing, Next.js dashboard functionality, and CDN data consistency.

## Python Data Processing Tests

### 1. Data Loader Tests (`python/tests/test_data_loaders.py`)

**Purpose**: Validate raw data loading and integrity

**Critical Tests:**
- **File existence validation**: Test that missing files raise appropriate `FileNotFoundError`
- **Data integrity**: Verify Excel/CSV files load with expected columns and data types
- **Station/year combinations**: Test all valid station/year combinations exist
- **Species mapping validation**: Ensure species codes map correctly to long names
- **Date parsing**: Test various date formats are handled correctly
- **Data consistency**: Cross-validate related files (e.g., detection files have corresponding environmental files)

**Key Test Cases:**
```python
def test_load_deployment_metadata_file_not_found():
    # Test FileNotFoundError for missing metadata file
    
def test_load_detection_data_valid_columns():
    # Test detection files have required columns
    
def test_species_mapping_completeness():
    # Test all species codes have mappings
    
def test_station_year_combinations():
    # Test all expected station/year combinations exist
```

### 2. View Generation Tests (`python/tests/test_view_generation.py`)

**Purpose**: Ensure view files are correctly generated and optimized

**Critical Tests:**
- **File size limits**: Ensure all view files stay under 50KB 
- **JSON structure validation**: Test output JSON matches expected schema
- **Data transformation accuracy**: Verify statistical calculations are correct
- **Completeness**: Ensure no data is lost during view generation
- **Performance**: Test view generation completes within reasonable time limits
- **Data traceability**: Verify view data can be traced back to raw source files
- **No simulation data**: Ensure views contain only real data from raw files

**Key Test Cases:**
```python
def test_view_file_size_limits():
    # Ensure all view files < 50KB
    
def test_stations_json_schema():
    # Validate stations.json structure
    
def test_heatmap_data_completeness():
    # Verify no data loss in aggregation
    
def test_view_generation_performance():
    # Ensure generation completes in reasonable time
    
def test_view_data_matches_raw_sources():
    # Sample values from views and verify against raw data
    
def test_no_simulated_data_in_views():
    # Check for patterns indicating simulated/fake data
```

### 2.1 View Data Integrity Tests (`python/tests/test_view_integrity.py`)

**Purpose**: Verify that generated view files contain real data from raw sources, not simulated or corrupted data

**Critical Tests:**
- **Raw data traceability**: Sample random records from views and trace back to raw Excel/CSV files
- **Statistical consistency**: Verify aggregations match manual calculations from raw data
- **Cross-file consistency**: Ensure related views have consistent data
- **Checksum validation**: Generate checksums of critical data fields for comparison
- **Pattern detection**: Look for suspicious patterns (too uniform, perfect sequences, etc.)

**Key Test Cases:**
```python
def test_station_coordinates_match_metadata():
    # Load stations.json and verify coordinates against raw metadata Excel
    
def test_detection_counts_match_raw():
    # Compare species detection counts in views vs raw detection files
    
def test_acoustic_index_values_traceable():
    # Sample acoustic index values and verify against raw CSV files
    
def test_no_placeholder_data():
    # Check for common placeholder values (0.0, 999, -999, "test", etc.)
    
def test_date_ranges_match_raw_data():
    # Verify date ranges in views match actual data availability
    
def test_aggregation_calculations():
    # Manually calculate means/sums from raw data and compare to views
    
def test_no_duplicate_synthetic_patterns():
    # Look for repeating patterns that indicate synthetic data
```

### 3. CDN Upload Tests (`python/tests/test_cdn_operations.py`)

**Purpose**: Validate CDN upload functionality and configuration

**Critical Tests:**
- **Environment validation**: Test required environment variables are present
- **Upload verification**: Mock S3 calls and verify correct upload parameters
- **File path mapping**: Ensure files go to correct CDN paths (`views/` vs `processed/`)
- **Error handling**: Test behavior with network failures and invalid credentials
- **Content type detection**: Verify correct MIME types are set

**Key Test Cases:**
```python
def test_missing_environment_variables():
    # Test behavior with missing env vars
    
def test_upload_file_path_mapping():
    # Test files go to correct CDN directories
    
def test_upload_content_type_detection():
    # Verify correct MIME types
    
def test_upload_error_handling():
    # Test network failure scenarios
```

## Next.js Dashboard Tests

### 1. API Route Tests (`dashboard/src/app/api/__tests__/`)

**Purpose**: Validate API endpoints and data processing

**Critical Tests:**
- **Parameter validation**: Test missing/invalid parameters return 400 errors
- **CDN data loading**: Mock CDN responses and test data processing
- **Cache behavior**: Verify in-memory caching works correctly
- **Error handling**: Test network failures and malformed data responses
- **Performance**: Ensure API responses complete within acceptable time limits

**Key Test Files:**
```typescript
// dashboard/src/app/api/__tests__/indices-heatmap.test.ts
describe('Indices Heatmap API', () => {
  test('returns 400 for missing parameters', async () => {
    // Test parameter validation
  });
  
  test('processes CDN data correctly', async () => {
    // Mock CDN response and test processing
  });
  
  test('caches results appropriately', async () => {
    // Test caching behavior
  });
});
```

### 2. Data Hook Tests (`dashboard/src/lib/data/__tests__/`)

**Purpose**: Validate custom hooks for data fetching

**Critical Tests:**
- **Data fetching**: Mock API calls and test data loading
- **Loading states**: Verify loading indicators work correctly
- **Error states**: Test error handling and user feedback
- **Data transformation**: Ensure hooks return data in expected format
- **Caching**: Test that duplicate requests are handled efficiently

**Key Test Files:**
```typescript
// dashboard/src/lib/data/__tests__/useIndicesHeatmap.test.ts
describe('useIndicesHeatmap Hook', () => {
  test('handles loading states correctly', () => {
    // Test loading indicators
  });
  
  test('processes API responses correctly', () => {
    // Test data transformation
  });
  
  test('handles API errors gracefully', () => {
    // Test error handling
  });
});
```

### 3. Component Integration Tests (`dashboard/src/components/__tests__/`)

**Purpose**: Validate component behavior with real data

**Critical Tests:**
- **Chart rendering**: Test charts render with valid data
- **Empty state handling**: Verify behavior when no data is available
- **User interactions**: Test filtering, selection, and export features
- **Responsive design**: Ensure components work on different screen sizes

**Key Test Files:**
```typescript
// dashboard/src/components/__tests__/AcousticIndicesHeatmap.test.tsx
describe('Acoustic Indices Heatmap', () => {
  test('renders chart with valid data', () => {
    // Test chart rendering
  });
  
  test('handles empty data gracefully', () => {
    // Test empty state
  });
  
  test('responds to user interactions', () => {
    // Test filtering and selection
  });
});
```

## CDN Data Consistency Tests

### 1. Data Pipeline Integration Tests (`python/tests/test_pipeline_integration.py`)

**Purpose**: Validate end-to-end data pipeline

**Critical Tests:**
- **End-to-end pipeline**: Test complete pipeline from raw data to CDN
- **Data consistency**: Verify CDN data matches local view files
- **File synchronization**: Ensure all required files are uploaded
- **Version consistency**: Test that related files have compatible data
- **Rollback capability**: Verify ability to revert to previous data versions

**Key Test Cases:**
```python
def test_end_to_end_pipeline():
    # Test complete pipeline execution
    
def test_cdn_local_data_consistency():
    # Compare CDN files with local versions
    
def test_file_synchronization():
    # Ensure all required files uploaded
    
def test_data_version_consistency():
    # Test related files have compatible data
```

### 2. CDN Health Checks (`python/scripts/test_cdn_health.py`)

**Purpose**: Monitor CDN health and data availability

**Critical Tests:**
- **File availability**: Check all required files are accessible
- **File integrity**: Verify file sizes and checksums match expectations
- **Response times**: Ensure CDN responses are fast enough for dashboard
- **CORS configuration**: Test cross-origin requests work correctly
- **Cache behavior**: Verify CDN caching headers are set correctly

**Key Health Checks:**
```python
def check_file_availability():
    # Test all required files accessible
    
def check_file_integrity():
    # Verify file sizes and checksums
    
def check_response_times():
    # Ensure fast CDN responses
    
def check_cors_configuration():
    # Test cross-origin requests
```

## Detecting Simulated/Fake Data

### Common Signs of Simulated Data

1. **Too Perfect Patterns**
   - Exact regular intervals (e.g., values incrementing by exactly 0.1)
   - Perfectly round numbers appearing too frequently
   - Suspiciously uniform distributions

2. **Placeholder Values**
   - Common test values: 0.0, 1.0, 999, -999, -1
   - Test strings: "test", "sample", "demo", "example"
   - Sequential IDs that are too clean (1, 2, 3, 4...)

3. **Unrealistic Data Characteristics**
   - Temperature values outside realistic ranges
   - Coordinates that don't match station locations
   - Dates that don't match deployment periods
   - Species detected outside their known ranges

4. **Missing Natural Variation**
   - No noise in measurements that should have natural variation
   - Identical repeated sequences
   - Lack of missing data (real data always has gaps)

### Validation Strategy

```python
class ViewDataIntegrityValidator:
    """Validates that view data comes from real sources."""
    
    def validate_against_raw(self, view_file, raw_data_loader):
        # 1. Sample random records from view
        # 2. Load corresponding raw data
        # 3. Verify values match within acceptable tolerance
        # 4. Check for data patterns
        pass
    
    def detect_synthetic_patterns(self, data):
        # Check for:
        # - Too many round numbers
        # - Perfect sequences
        # - Repeating patterns
        # - Unrealistic value ranges
        pass
    
    def verify_checksum(self, view_data, expected_checksum):
        # Generate checksum of critical fields
        # Compare with expected checksum from raw data
        pass
```

## Implementation Roadmap

### Phase 1: Foundation Tests (Week 1)

**Goals:**
- Set up pytest configuration with coverage reporting
- Create test data fixtures for consistent testing
- Implement critical data loader tests
- Add basic CDN upload validation tests

**Deliverables:**
- `python/tests/conftest.py` - pytest configuration and fixtures
- `python/tests/test_data_loaders.py` - basic data loading tests
- `python/tests/test_cdn_operations.py` - CDN upload validation
- Test data fixtures in `python/tests/fixtures/`

**Commands:**
```bash
cd python/
uv add --dev pytest pytest-cov pytest-mock
uv run pytest tests/ --cov=mbon_analysis --cov-report=html
```

### Phase 2: Pipeline Tests (Week 2)

**Goals:**
- Add view generation tests with size/performance checks
- Implement API route tests with mocking
- Create data consistency validation tests
- Add integration tests for critical user paths

**Deliverables:**
- `python/tests/test_view_generation.py` - view generation validation
- `dashboard/src/app/api/__tests__/` - API route tests
- `python/tests/test_pipeline_integration.py` - end-to-end tests

**Commands:**
```bash
cd dashboard/
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm run test -- --coverage
```

### Phase 3: Monitoring & CI (Week 3)

**Goals:**
- Set up automated test running on data changes
- Implement CDN health monitoring scripts
- Add performance benchmarking tests
- Create test reporting and failure alerts

**Deliverables:**
- `python/scripts/validate_pipeline.py` - pipeline health check
- `python/scripts/check_cdn_sync.py` - CDN synchronization check
- `.github/workflows/tests.yml` - CI configuration
- Performance benchmarking suite

**Commands:**
```bash
cd python/
uv run scripts/validate_pipeline.py
uv run scripts/check_cdn_sync.py
```

### Phase 4: Advanced Testing (Week 4)

**Goals:**
- Add end-to-end browser tests for critical features
- Implement load testing for API endpoints
- Create data quality monitoring dashboards
- Add automated regression testing

**Deliverables:**
- Playwright or Cypress end-to-end tests
- Load testing with Artillery or similar
- Data quality monitoring dashboard
- Regression test suite

## Key Test Scripts to Create

### Immediate Priority Tests

1. **`python/tests/test_data_integrity.py`**
   - Test that raw data files haven't been corrupted
   - Validate data relationships and constraints

2. **`python/scripts/validate_pipeline.py`**
   - Quick script to check entire pipeline health
   - Run all critical validations in one command

3. **`dashboard/src/__tests__/api-health.test.ts`**
   - Test all API endpoints return valid responses
   - Validate API response schemas

4. **`python/scripts/check_cdn_sync.py`**
   - Verify CDN has latest data versions
   - Check file timestamps and sizes

### Sample Test Commands

```bash
# Python tests
cd python/
uv run pytest tests/ --cov=mbon_analysis --cov-report=html

# NextJS tests  
cd dashboard/
npm run test -- --coverage

# CDN health check
cd python/
uv run scripts/check_cdn_sync.py

# Full pipeline validation
cd python/
uv run scripts/validate_pipeline.py

# Run all tests
make test  # (if you create a Makefile)
```

## Test Configuration Files

### Python Test Configuration (`python/pyproject.toml`)

Already configured in your existing `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=mbon_analysis",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Next.js Test Configuration (`dashboard/jest.config.js`)

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
```

## Benefits of This Testing Strategy

This comprehensive testing approach will help you:

1. **Catch issues early** by validating data integrity at every pipeline stage
2. **Ensure consistency** between local and CDN data
3. **Test error conditions** before they cause user-facing issues
4. **Monitor performance** to catch degradation early
5. **Provide clear failure diagnostics** when issues occur
6. **Maintain confidence** when making changes to the pipeline
7. **Document expected behavior** through executable specifications

## Maintenance and Updates

- **Update tests** when adding new data sources or API endpoints
- **Review test coverage** monthly to ensure all critical paths are tested
- **Monitor test execution time** and optimize slow tests
- **Update fixtures** when data formats change
- **Document test failures** and their resolution for future reference

## Getting Started

To implement this testing strategy:

1. **Start with Phase 1** foundation tests
2. **Choose the most critical area** causing current issues
3. **Create test fixtures** using a subset of your real data
4. **Write failing tests first**, then make them pass
5. **Run tests frequently** during development
6. **Integrate tests** into your development workflow

This testing strategy provides a solid foundation for maintaining data quality and catching issues before they impact users of your marine biodiversity dashboard.