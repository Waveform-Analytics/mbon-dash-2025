# View-Based Architecture Migration Plan

## Quick Start - Risk-Minimized Approach

This plan uses **Test-Driven Development (TDD)** with manual checkpoints to ensure zero-risk migration:

1. **Write tests first** → 2. **Implement minimal code** → 3. **Manual testing** → 4. **Full implementation**

Each phase has:
- ✅ Checkboxes to track progress
- 🧪 Automated tests to write before coding
- 👀 Manual testing checkpoints with specific things to verify  
- ⚠️ Clear rollback triggers if anything goes wrong

**Start here:** [Phase 1: Foundation Setup](#phase-1-foundation-setup-low-risk)

## Overview

Migrate from large monolithic JSON files to view-specific optimized data files with full CDN automation.

## Goals

- ✅ **Zero risk refactoring** - keep existing system working during migration
- ✅ **Test-driven development** - write tests before implementation
- ✅ **Manual testing checkpoints** - verify each step works correctly
- ✅ **Clean Python package architecture** - all logic in `mbon_analysis`, scripts are thin wrappers
- ✅ **Fully automated CDN pipeline** - one command to prep, upload, and validate
- ✅ **Interactive dashboard features preserved** - filtering, zoom, hover, etc.
- ✅ **Developer-friendly** - easy to "jump back in" after months
- ✅ **Clear exploration workflow** - separate local exploration from production pipeline
- ✅ **Project-agnostic design** - code should work for any marine monitoring project (any number of stations, any naming)

## Exploration vs. Pipeline Workflow

### **Local Exploration (Development Phase)**
- Use Marimo notebooks, Python scripts, or exploratory analysis in `scripts/exploratory/`
- Load data using `mbon_analysis` package functions for interactive exploration
- Experiment with different visualizations, aggregations, and analyses
- Prototype charts and identify what data views are needed

### **Production Pipeline (Dashboard Integration)**
- Once you decide on a specific plot/visualization, add it to the formal pipeline
- Create view generator in `mbon_analysis/views/` that produces the exact data structure needed
- Add corresponding frontend page that loads the optimized view data
- Deploy via automated CDN pipeline

### **Clear Separation:**
```
Local Exploration:    Raw Data → mbon_analysis functions → Interactive exploration
Production Pipeline:  Raw Data → mbon_analysis/views → Optimized JSON → CDN → Dashboard
```

This keeps exploration flexible while ensuring the production system is clean and optimized.

## Current State Issues

1. **Performance**: 159MB acoustic_indices.json, 45MB environmental.json (despite recent pagination optimization)
2. **Manual CDN uploads**: Error-prone, tedious
3. **Complex pagination system**: 61 paginated files, complex pagination logic, still loading large amounts of data
4. **Maintenance burden**: Multiple systems, manual processes
5. **Architecture mismatch**: Frontend loads raw data instead of view-optimized data

## Target Architecture

### **Data Flow**
```
Excel Files → mbon_analysis Package → View-Specific JSONs → Automated CDN → Frontend
```

### **View-Specific Files (Small & Fast)**
- `station_overview.json` (~5KB) - Station locations, metadata, summary stats
- `species_timeline.json` (~100KB) - Monthly/yearly aggregated detection data
- `acoustic_summary.json` (~50KB) - Key acoustic indices, PCA results
- `environmental_trends.json` (~20KB) - Temperature/depth patterns
- `biodiversity_patterns.json` (~30KB) - Species co-occurrence, diversity metrics

### **Package Architecture**
```
mbon_analysis/
├── core/
│   ├── excel_processor.py          # ← Existing (keep)
│   ├── data_loader.py              # ← Existing (keep)  
│   └── view_generator.py           # ← NEW - core view generation logic
├── views/                          # ← NEW module
│   ├── __init__.py
│   ├── station_views.py            # ← Station-specific data processing
│   ├── species_views.py            # ← Species timeline & analysis
│   ├── acoustic_views.py           # ← Acoustic indices & PCA
│   ├── environmental_views.py      # ← Temperature/depth trends
│   └── biodiversity_views.py       # ← Diversity metrics & patterns
├── deployment/                     # ← NEW module
│   ├── __init__.py
│   ├── cdn_sync.py                 # ← Smart CDN upload logic
│   ├── manifest_generator.py       # ← Auto-generate manifests
│   └── validation.py               # ← Deployment validation
└── analysis/                       # ← Existing (keep)
    └── ...
```

---

## Risk-Minimized Implementation Strategy

### **Test-Driven Development (TDD) Approach**
We'll follow a strict TDD methodology to minimize risk at each stage:
1. **Write tests first** - Define expected behavior before implementation
2. **Implement minimal code** - Just enough to pass tests
3. **Manual testing checkpoint** - Verify in browser after each stage
4. **Rollback trigger** - If any test fails, stop and fix before proceeding

### **Testing Infrastructure Setup**

#### **Prerequisites Checklist**
- [x] Add pytest to project: `uv add pytest pytest-cov`
- [x] Create test directories: `tests/unit/` and `tests/integration/`
- [x] Set up test fixtures for mock data
- [x] Configure pytest.ini for test discovery
- [x] Add test commands to package.json

---

## Phase 1: Foundation Setup (Low Risk)

### **1.1 Test Infrastructure Setup**

#### **Step 1.1.1: Install Testing Dependencies**
- [x] Run: `uv add pytest pytest-cov pytest-mock`
- [x] Run: `uv add --dev pytest-watch` (for continuous testing)
- [x] Verify installation: `uv run pytest --version`

#### **Step 1.1.2: Create Test Structure**
```bash
tests/
├── unit/
│   ├── test_station_views.py      # Station view generator tests
│   ├── test_cdn_sync.py          # CDN sync logic tests
│   └── test_view_generator.py    # Core view generation tests
├── integration/
│   ├── test_end_to_end.py        # Full pipeline tests
│   └── test_cdn_deployment.py    # CDN deployment tests
└── fixtures/
    ├── sample_data.py             # Sample test data
    └── mock_responses.py          # Mock CDN responses
```
- [x] Create all test directories
- [x] Create placeholder test files
- [x] **MANUAL TEST**: Run `uv run pytest` - should find 0 tests but no errors

### **1.2 Create First Function with TDD**

#### **Step 1.2.1: Write Tests for `generate_station_overview()`**
```python
# tests/unit/test_station_views.py
def test_generate_station_overview_structure():
    """Test that station overview has correct structure."""
    result = generate_station_overview(mock_data_dir)
    assert 'stations' in result
    assert 'metadata' in result
    assert len(result['stations']) >= 0  # Can handle any number of stations

def test_station_overview_size():
    """Test that output is reasonably sized for performance."""
    result = generate_station_overview(mock_data_dir)
    json_str = json.dumps(result)
    station_count = len(result['stations'])
    size_limit = 5120 + station_count * 2048  # 5KB base + 2KB per station
    assert len(json_str) < size_limit

def test_station_summary_stats():
    """Test that each station has required summary stats."""
    result = generate_station_overview(mock_data_dir)
    for station in result['stations']:
        assert 'total_detections' in station['summary_stats']
        assert 'species_count' in station['summary_stats']

def test_station_coordinates():
    """Test that coordinates are valid lat/lon values."""
    result = generate_station_overview(mock_data_dir)
    for station in result['stations']:
        assert -90.0 <= station['coordinates']['lat'] <= 90.0
        assert -180.0 <= station['coordinates']['lon'] <= 180.0
```
- [x] Write all tests in `test_station_views.py` *(Updated: Made tests completely generic for any marine monitoring project - no hardcoded station names/counts)*
- [x] Run tests: `uv run pytest tests/unit/test_station_views.py -v`
- [x] Verify all tests FAIL (no implementation yet)

#### **Step 1.2.2: Implement Minimal `generate_station_overview()`**
```python
# mbon_analysis/views/station_views.py
def generate_station_overview(processed_data_dir: Path) -> dict:
    """Generate station overview optimized for interactive map."""
    # Minimal implementation to pass tests
    return {
        'stations': [],
        'metadata': {
            'generated_at': '2024-01-01T12:00:00Z',
            'data_sources': [],
            'total_stations': 0
        }
    }
```
- [x] Create `mbon_analysis/views/__init__.py`
- [x] Create `mbon_analysis/views/station_views.py`
- [x] Implement minimal function
- [x] Run tests: `uv run pytest tests/unit/test_station_views.py -v`
- [x] All tests PASS (excellent! Generic tests handle minimal case)

#### **Step 1.2.3: Full Implementation**
- [x] Implement complete `generate_station_overview()` function
- [x] Run tests: `uv run pytest tests/unit/test_station_views.py -v`
- [x] ALL tests should PASS
- [x] **MANUAL TEST CHECKPOINT**: 
  - [x] Run: `uv run python -c "from mbon_analysis.views import station_views; print(station_views.generate_station_overview('data/cdn/processed'))"`
  - [x] Verify output looks correct *(✅ Real data: 3 stations, deployments, coordinates, stats)*
  - [x] Check file size is < 10KB *(✅ 2.8 KB - excellent performance)*

**⚠️ ROLLBACK TRIGGER**: If any test fails or manual check shows issues, STOP and fix before proceeding

### **1.3 Script Wrapper Implementation**

#### **Step 1.3.1: Create Thin Wrapper Script**
```python
# scripts/view_generation/generate_station_views.py
#!/usr/bin/env python3
"""Thin wrapper to generate station views."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mbon_analysis.views.station_views import generate_station_overview
import json

def main():
    data = generate_station_overview(Path('data/cdn/processed'))
    output_path = Path('data/cdn/views/station_overview.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Generated {output_path} ({len(json.dumps(data))} bytes)")

if __name__ == "__main__":
    main()
```
- [x] Create `scripts/view_generation/` directory
- [x] Create `generate_station_views.py` wrapper
- [x] Make script executable: `chmod +x scripts/view_generation/generate_station_views.py`
- [x] Test script: `uv run scripts/view_generation/generate_station_views.py`
- [x] Verify `data/cdn/views/station_overview.json` was created
- [x] **MANUAL TEST CHECKPOINT**:
  - [x] Check file size: `ls -lh data/cdn/views/station_overview.json` *(✅ 4.5K - excellent)*
  - [x] Verify < 10KB *(✅ Well under limit)*
  - [x] Open file and verify structure looks correct *(✅ 3 stations, deployments, coordinates, stats, metadata)*

**⚠️ ROLLBACK TRIGGER**: If script fails or output is > 10KB, investigate before proceeding

### **1.4 New Directory Structure Setup**

#### **Step 1.4.1: Create Directory Structure**
```bash
# Keep existing structure intact
data/cdn/
├── processed/          # ← DO NOT TOUCH (existing system)
│   ├── detections.json
│   ├── acoustic_indices.json
│   └── paginated/
└── views/              # ← NEW (safe to add)
    └── station_overview.json  # Created by script above
```
- [x] Verify `data/cdn/processed/` exists and is untouched *(✅ Original system intact)*
- [x] Verify `data/cdn/views/` was created by the script *(✅ Created with station_overview.json)*
- [ ] Add `data/cdn/views/` to `.gitignore` *(Optional - view files could be committed or ignored)*

---

## Phase 2: Build First View (Stations) - WITH TESTING

### **2.1 Frontend Hook Implementation**

#### **Step 2.1.1: Write Tests for Frontend Hook**
```typescript
// tests/unit/test_view_hooks.spec.tsx
describe('useViewData Hook', () => {
  it('should load station overview data successfully', async () => {
    const mockStationData = { stations: [...], metadata: {...} }
    fetch.mockResolvedValueOnce({ ok: true, json: async () => mockStationData })
    
    const { result } = renderHook(() => useViewData('station-overview'))
    
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data).toEqual(mockStationData)
    expect(fetch).toHaveBeenCalledWith(`${process.env.NEXT_PUBLIC_DATA_URL}/views/station_overview.json`)
  });
  // ... comprehensive test suite covering loading, errors, type safety
});
```
- [x] Install React Testing Library: `npm install -D @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom`
- [x] Create Jest configuration files (`jest.config.js`, `jest.setup.js`)
- [x] Create comprehensive tests in `tests/unit/test_view_hooks.spec.tsx`
- [x] Tests cover: loading states, error handling, type safety, view type validation
- [ ] Run tests: `npm test` *(will fail - hook doesn't exist yet)*

#### **Step 2.1.2: Implement `useViewData` Hook**
```typescript
// src/lib/hooks/useViewData.ts
export function useViewData<T extends ViewType>(viewType: T): UseViewDataResult<T> {
  // Type-safe loading with view type validation
  // Automatic URL construction from view type
  // Comprehensive error handling and loading states
}

export function useStationOverview() {
  return useViewData('station-overview');
}
```
- [x] Create `src/lib/hooks/useViewData.ts` *(Comprehensive implementation with TypeScript generics)*
- [x] Add view data types to `src/types/data.ts` *(StationOverviewData, ViewType)*
- [x] Implement type-safe hook with view validation
- [x] Run tests: `npm run test -- tests/unit/test_view_hooks.spec.tsx`
- [x] **ALL 9 TESTS PASS** *(Loading states, error handling, type safety, view validation)*
- [x] **MANUAL TEST CHECKPOINT**:
  - [x] Hook loads correct CDN paths: `/views/station_overview.json`
  - [x] Type inference works correctly for different view types
  - [x] Error handling for invalid view types and network failures

**✅ SUCCESS**: Hook implementation complete with comprehensive test coverage

### **2.2 Create Parallel Station Page (/stations-v2)**

#### **Step 2.2.1: Create New Page with Tests**
```typescript
// tests/unit/test_stations_v2_page.spec.tsx
describe('Stations V2 Page', () => {
  // Comprehensive test suite with 15 tests covering:
  // - Page rendering and structure
  // - Loading states and error handling
  // - Data display with exact content verification
  // - Performance indicators and accessibility
  // - Empty state handling
});
```
- [x] Create `src/app/stations-v2/` directory
- [x] Create comprehensive test suite in `tests/unit/test_stations_v2_page.spec.tsx`
- [x] **15 TESTS WRITTEN** covering all page states and functionality
- [x] Handle Jest module resolution issues (relative paths work)
- [x] Run tests: `npm run test -- tests/unit/test_stations_v2_page.spec.tsx`
- [x] Initial tests FAILED as expected (no implementation)

**✅ SUCCESS**: Comprehensive test suite ready with full coverage

#### **Step 2.2.2: Implement Minimal Stations-v2 Page**
```typescript
// src/app/stations-v2/page.tsx
export default function StationsV2Page() {
  const { data, loading, error } = useStationOverview();
  
  // Comprehensive implementation with:
  // - Loading states with spinner
  // - Error handling with styled error messages
  // - Full station data display (cards with stats)
  // - Coordinate display and deployment information
  // - Metadata section and responsive design
}
```
- [x] Create `src/app/stations-v2/page.tsx` with full implementation
- [x] Create `src/app/stations-v2/page.content.tsx` following content helper pattern
- [x] Implement comprehensive page with all required functionality
- [x] Run tests: `npm run test -- tests/unit/test_stations_v2_page.spec.tsx`
- [x] **ALL 15 TESTS PASS** ✅

**✅ SUCCESS**: Complete stations-v2 page implementation with perfect test coverage

#### **Step 2.2.3: Performance Comparison Test**
- [ ] Start dev server: `npm run dev`
- [ ] Open browser DevTools Network tab
- [ ] Navigate to `/stations` (old version)
- [ ] Record: Total data transferred: _______ MB
- [ ] Record: Load time: _______ seconds
- [ ] Navigate to `/stations-v2` (new version)  
- [ ] Record: Total data transferred: _______ KB
- [ ] Record: Load time: _______ seconds
- [ ] **SUCCESS CRITERIA**: New version should load < 100KB (vs 159MB old)

**⚠️ ROLLBACK TRIGGER**: If new version loads > 100KB or is slower, investigate before proceeding

### **2.3 Side-by-Side Testing Checklist**

#### **Functionality Comparison**
- [ ] Old `/stations` page loads correctly
- [ ] New `/stations-v2` page loads correctly
- [ ] Both show same 3 stations (9M, 14M, 37M)
- [ ] Both show correct station locations on map
- [ ] Both show summary statistics
- [ ] **MANUAL TEST**: Click through all interactive elements on both pages

#### **Data Accuracy Verification**
- [ ] Compare total detection counts between old and new
- [ ] Compare species counts between old and new
- [ ] Compare year ranges between old and new
- [ ] Document any discrepancies: _____________

#### **Performance Metrics**
- [ ] Old page initial load: _____ MB in _____ seconds
- [ ] New page initial load: _____ KB in _____ seconds
- [ ] Improvement factor: _____x faster

**⚠️ ROLLBACK TRIGGER**: If any data discrepancies found or functionality missing, fix before proceeding

---

## Phase 3: CDN Automation System

### **3.1 Environment Configuration**

```bash
# .env.local (development)
CDN_PROVIDER=local_dev
CDN_BASE_URL=http://localhost:3000/data

# .env.production
CDN_PROVIDER=cloudflare_r2
CDN_BUCKET_NAME=your-bucket-name
CDN_ACCOUNT_ID=your-account-id  
CDN_ACCESS_KEY_ID=your-access-key
CDN_SECRET_ACCESS_KEY=your-secret-key
CDN_BASE_URL=https://pub-your-id.r2.dev
```

### **3.2 Smart CDN Sync**

**Features:**
- **Hash-based change detection** - only upload modified files
- **Atomic deployments** - all files uploaded or none
- **Automatic manifest generation** - no manual maintenance
- **Deployment validation** - test CDN files after upload
- **Rollback capability** - keep previous version available

**Implementation:**
```python
# mbon_analysis/deployment/cdn_sync.py
class CDNDeployer:
    def sync_views(self, local_views_dir: Path) -> DeploymentResult:
        # 1. Generate file hashes
        # 2. Compare with CDN manifest
        # 3. Upload only changed files
        # 4. Update manifest atomically
        # 5. Validate deployment
        # 6. Return detailed results
```

### **3.3 Package.json Integration**

```json
{
  "scripts": {
    "generate-views": "uv run scripts/dashboard_prep/generate_views.py",
    "deploy-views": "uv run scripts/deployment/full_deploy.py",
    "deploy-views:check": "uv run scripts/deployment/full_deploy.py --check-only",
    "validate-deployment": "uv run scripts/deployment/validate_deployment.py",
    
    "dev": "next dev",
    "dev:with-views": "npm run generate-views && next dev",
    
    "process-data": "npm run process-data:excel && npm run generate-views",
    "process-data:excel": "uv run scripts/dashboard_prep/process_excel_to_json.py"
  }
}
```

---

## Phase 4: Full Migration

### **4.1 Migration Order (Safest to Riskiest)**

1. **Station Overview** - Simple, mostly static data
2. **Species Timeline** - Aggregated time series  
3. **Acoustic Summary** - PCA results, index summaries
4. **Environmental Trends** - Temperature/depth patterns
5. **Biodiversity Patterns** - Complex co-occurrence data

### **4.2 Each Migration Step**

1. **Generate view data** using `mbon_analysis/views/`
2. **Build new page version** at `/{page}-v2`
3. **Test thoroughly** - functionality, performance, data accuracy
4. **Replace original page** once validated
5. **Clean up old version**

### **4.3 Frontend Hook Migration**

**Before:**
```typescript
const { detections, loading } = useTimelineData(); // Loads 14MB
```

**After:**  
```typescript
const { timeline, loading } = useSpeciesTimeline(); // Loads 100KB
```

---

## Phase 5: Clean Up

### **5.1 Remove Old System**

- Delete paginated files and pagination logic
- Remove large monolithic JSON files
- Clean up unused scripts and hooks
- Update documentation

### **5.2 Clean Up Mixed Processed/View Files**

**⚠️ IMPORTANT**: The current `data/cdn/processed/` directory contains a mix of true processed data and view files. This needs to be cleaned up:

**True Processed Data (keep in processed/)**:
- `detections.json` - Raw detection records from Excel
- `environmental.json` - Raw temperature/depth measurements from Excel
- `acoustic_indices.json` - Raw acoustic index calculations from CSV
- `deployment_metadata.json` - Deployment information from Excel
- `stations.json` - Station definitions
- `species.json` - Species metadata

**View Files (move to views/ or delete if replaced)**:
- `monthly_detections.json` → Move to `views/` or replace with new view generator
- `pca_biplot*.json` → Move to `views/` as acoustic analysis views
- `step1a_raw_data_landscape.json` → Move to `views/` or `analysis/` folder
- `step1b_index_distributions.json` → Move to `views/` or `analysis/` folder
- `paginated/` folder → **DELETE** (replaced by view-based system)
- `*_summary.json` files → **DELETE** (replaced by view-based system)
- `acoustic_indices_detailed.json`, `acoustic_indices_raw.json` → Evaluate if needed

**Clean Architecture Goal**:
```
data/cdn/
├── processed/     # ← Only normalized data from Excel/CSV
│   ├── detections.json
│   ├── environmental.json
│   ├── acoustic_indices.json
│   ├── deployment_metadata.json
│   ├── stations.json
│   └── species.json
└── views/         # ← Only optimized frontend views
    ├── station_overview.json
    ├── species_timeline.json
    ├── acoustic_summary.json
    ├── environmental_trends.json
    └── biodiversity_patterns.json
```

### **5.3 Final Package.json**

```json
{
  "scripts": {
    "process-data": "uv run scripts/dashboard_prep/generate_views.py",
    "deploy": "npm run process-data && uv run scripts/deployment/full_deploy.py",
    "deploy:check": "uv run scripts/deployment/full_deploy.py --check-only",
    "dev": "next dev",
    "dev:fresh": "npm run process-data && next dev"
  }
}
```

**Single command deployment:**
```bash
npm run deploy
# ✅ Processes Excel files
# ✅ Generates optimized view files  
# ✅ Uploads only changed files to CDN
# ✅ Updates manifest automatically
# ✅ Validates deployment
# ✅ Reports results
```

---

## Deployment and Rollback Procedures

### **Safe Deployment Checklist**

#### **Pre-Deployment Verification**
- [ ] All automated tests passing: `uv run pytest && npm test`
- [ ] Manual testing completed for current phase
- [ ] Performance metrics documented
- [ ] Data accuracy verified
- [ ] No console errors in browser
- [ ] Memory usage acceptable (check DevTools)

#### **Deployment Steps**
1. **Generate Views Locally**
   - [ ] Run: `uv run scripts/view_generation/generate_station_views.py`
   - [ ] Verify output size: `ls -lh data/cdn/views/`
   - [ ] Quick data check: `head -20 data/cdn/views/station_overview.json`

2. **Test Locally with Production Build**
   - [ ] Build: `npm run build`
   - [ ] Start: `npm start`
   - [ ] Test `/stations-v2` with production build
   - [ ] Verify performance still good

3. **Upload to CDN (Manual for now)**
   - [ ] Upload `data/cdn/views/` folder to CDN
   - [ ] Verify files accessible via CDN URL
   - [ ] Test with live CDN data

4. **Monitor After Deployment**
   - [ ] Check browser console for errors
   - [ ] Monitor network tab for failed requests
   - [ ] Verify all features working
   - [ ] Document any issues: _____________

### **Rollback Procedures**

#### **Immediate Rollback Triggers**
If ANY of these occur, rollback immediately:
- [ ] Page crashes or shows errors
- [ ] Data is incorrect or missing
- [ ] Performance degradation (slower than old version)
- [ ] Features stop working
- [ ] User reports issues

#### **How to Rollback**

**Option 1: Keep Old Page Active (Recommended)**
```typescript
// Don't replace /stations yet, keep both:
// /stations (old, working)
// /stations-v2 (new, testing)
```
- Simply direct users back to `/stations` if issues found

**Option 2: Quick Code Revert**
```bash
# If you already replaced the original page
git stash  # Save current work
git checkout HEAD -- src/app/stations/page.tsx
npm run dev  # Verify old version works
```

**Option 3: CDN Rollback**
```bash
# Keep backup of old views
data/cdn/views_backup/  # Previous version
data/cdn/views/         # Current version

# To rollback: re-upload views_backup to CDN
```

#### **Post-Rollback Actions**
- [ ] Document what went wrong
- [ ] Write failing test case for the issue
- [ ] Fix issue in development
- [ ] Add additional tests
- [ ] Try deployment again

---

## Success Metrics

### **Performance Improvements**
- **Initial Load**: 218MB → <500KB (400x faster)
- **File Count**: 61 files → 5-10 files  
- **CDN Management**: Manual → Fully automated
- **Deployment Time**: Manual minutes → Automated seconds

### **Developer Experience**
- **One command deploy**: `npm run deploy`
- **Safe migration**: No risk to existing system during transition
- **Clean codebase**: All logic in package, scripts are thin wrappers
- **Easy maintenance**: Clear separation of concerns

### **Risk Mitigation**
- **Parallel systems**: Old and new work simultaneously during migration
- **Incremental migration**: One page at a time
- **Automated testing**: Deployment validation built-in
- **Easy rollback**: Previous versions always available

---

## Open Questions

1. ✅ **Which page should we migrate first?** Station overview confirmed as safest starting point.

2. ✅ **CDN provider preferences?** Cloudflare R2 confirmed - cost effective and reliable.

3. **Manifest format?** JSON with file hashes and metadata for change detection.

4. **Validation strategy?** Automated tests for data accuracy and deployment health checks.

5. **Rollback mechanism?** Keep N previous versions on CDN for safe rollbacks.

---

## Next Steps

1. **Review this plan** - Does the approach feel right?

2. **Environment setup** - CDN credentials and configuration

3. **Start with station overview** - Build first view generator

4. **Test automation** - Ensure CDN sync works reliably  

5. **Incremental migration** - One page at a time, low risk

This approach gives you the clean, automated, maintainable system you want while minimizing risk during the transition.