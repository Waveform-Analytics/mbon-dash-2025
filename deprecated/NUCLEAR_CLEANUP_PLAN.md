# Nuclear Cleanup Plan: Simplifying MBON Dashboard

## Problem Statement

The project has become bloated with:
- 50+ JSON files when we need ~10
- 29 pagination files nobody asked for
- Overly complex Python package with unclear boundaries
- Multiple competing data processing approaches
- Test files before we have working basics
- Deprecated migration pages still cluttering the dashboard

## User Experience Preservation

**CRITICAL**: The user must see **identical functionality** after cleanup:

### Current Working Dashboard Pages:
1. **Overview** (`/`) - Homepage with project intro
2. **Analysis:**
   - Acoustic Indices (`/acoustic-biodiversity`) - Uses `usePCABiplot`, `useRawDataLandscape`, `useIndexDistributions`
   - Environmental Factors (`/environmental-factors`) - Basic environmental analysis
3. **Resources:**
   - Index Guide (`/acoustic-glossary`) - Educational content about acoustic indices  
   - Station Profiles (`/stations`) - Uses `useStations`, `useDeploymentMetadata`
4. **Explore:**
   - Species Annotations (`/explore/annotations`) - Uses `useTimelineData`, `useMonthlyDetections`
   - Acoustic Indices (`/explore/indices`) - Uses acoustic indices data

### Data Dependencies Analysis:

**Core Data Files (KEEP):**
- `metadata.json` - Used by multiple hooks
- `stations.json` - Used by `useStations()`
- `species.json` - Used by `useSpecies()`
- `detections.json` - Used by `useTimelineData()` 
- `environmental.json` - Used for temp/depth data
- `deployment_metadata.json` - Used by `useDeploymentMetadata()`

**View Files (KEEP & IMPROVE):**
- `views/station_overview.json` - Used by `useStationOverview()` (7KB vs 9KB original)
- `views/species_timeline.json` - Used by `useSpeciesTimeline()` (1.6KB vs MB+)
- `views/acoustic_summary.json` - Used by `useAcousticSummary()` (19.6KB vs 166MB!)
- `views/raw_data_landscape.json` - Used by `useRawDataLandscape()` (32KB vs 100KB+)
- `views/index_distributions.json` - Used by `useIndexDistributions()` (119KB vs 2.8MB)

**Bloat to DELETE:**
- `data/cdn/processed/paginated/` - 29+ pagination files (pagination system removed)
- `acoustic_indices.json` (166MB) - replaced by `acoustic_summary.json` (19.6KB)
- `acoustic_indices_detailed.json`, `acoustic_indices_raw.json` - duplicates
- `pca_biplot.json`, `pca_biplot_8khz.json`, `pca_biplot_fullbw.json` - can regenerate from views
- `step1a_raw_data_landscape.json` - replaced by view
- `step1b_index_distributions.json` - replaced by view

## Cleanup Strategy

### Phase 1: Delete Bloated Pages & Routes

**Pages to DELETE:**
```bash
src/app/acoustic-v2/           # Migration leftover
src/app/species-v2/            # Migration leftover  
src/app/stations-v2/           # Migration leftover
src/app/pagination-demo/       # Testing leftover
src/app/explorer/              # Duplicate of explore/?
src/app/temporal/              # Unclear purpose
src/app/api/cdn/processed/     # Complex proxy routes
```

### Phase 2: Streamline Backend Processing

**Simplified Architecture:**
```
scripts/
├── 1_process_excel_to_json.py    # Excel → Core JSON (reuse existing logic)
├── 2_generate_all_views.py       # JSON → Views (consolidate view generators)  
├── 3_upload_to_cdn.py             # Upload to Cloudflare R2
└── utils/
    └── cdn_upload.py              # Simple upload helper
```

**Python Package Simplification:**
```
mbon_analysis/
├── __init__.py                    # Main exports
├── processing/
│   ├── __init__.py
│   ├── excel_to_json.py           # Excel processing (keep what works)
│   └── json_to_views.py           # View generation (consolidate existing)
└── utils/
    ├── __init__.py  
    └── cdn_sync.py                # Simple CDN operations
```

**Directories to DELETE:**
```bash
mbon_analysis/analysis/            # Research logic (separate from dashboard)
mbon_analysis/deployment/          # Over-engineered deployment
mbon_analysis/views/               # Replace with single module
mbon_analysis/visualization/       # Unused
scripts/analysis/                  # Research scripts
scripts/examples/                  # Examples before basics work
scripts/exploratory/              # Research scripts  
scripts/notebooks/                 # Research scripts
scripts/utils/paginate*.py         # Pagination complexity
tests/                             # Testing before basics work
notes/                             # Planning docs
htmlcov/                           # Coverage reports
```

### Phase 3: Preserve Working Data Logic

**Keep & Reuse:**
1. **Excel Processing Logic** - `scripts/dashboard_prep/process_excel_to_json.py` has proven logic
2. **View Generation Logic** - Individual view generators in `scripts/view_generation/` work well
3. **CDN Upload Logic** - `scripts/data_management/upload_to_cdn.py` works
4. **Data Loading Hooks** - `src/lib/hooks/useData.ts` and `useViewData.ts` work perfectly

**Data Pipeline:**
```
Raw Excel (data/cdn/raw-data/)
    ↓ [1_process_excel_to_json.py] 
Core JSON (data/cdn/processed/) - 6 essential files only
    ↓ [2_generate_all_views.py]
View JSON (data/cdn/views/) - 5 optimized files  
    ↓ [3_upload_to_cdn.py]
Cloudflare R2 CDN ← Dashboard consumes views
```

## Additional Root Directory Bloat Identified

**Major Bloat Found:**
- `mkdocs.yml` + `docs_site/` + `site/` - **Complete mkdocs system** (will rebuild cleaner version)
- `htmlcov/` - **Coverage reports directory** (20+ HTML files)
- `tests/` - **Entire test suite** (20+ test files before basics work)
- `mbon_dash_2025.egg-info/` - **Python package metadata** (auto-generated)
- `coverage.json` - Coverage data file
- `dashboard_data_processing.log` - Processing log file
- `pytest.ini` + `jest.config.js` + `jest.setup.js` - **Testing config files**
- `test_runner.py` - Custom test runner
- `tsconfig.tsbuildinfo` - **Massive TypeScript build cache** (95,390 tokens!)
- `data/intermediate_results/` - **Intermediate processing files**
- `src/content/` - **Empty content directory**
- `src/lib/data/README.md` - **Orphaned README**

**Package.json Script Bloat:**
- 26 scripts when we need ~5
- Complex testing, validation, pagination scripts
- Multiple deployment variations
- Notebook documentation builders

**Frontend Component Bloat:**
- `src/components/ui/PaginationControls.tsx` - For removed pagination
- `src/lib/hooks/usePaginatedData.ts` - Pagination hook
- `src/lib/hooks/useAcousticIndicesCSV.ts` - Direct CSV loading (bypasses views)

## Flexibility & Extensibility Requirements

**Future-Proofing Considerations:**
1. **Easy View Addition** - New plots should require minimal code changes
2. **Station Scalability** - Support for additional stations (beyond 9M, 14M, 37M)
3. **Expandable Data Pipeline** - New data types (environmental sensors, new indices)
4. **Research Integration** - Ability to add research scripts without cluttering dashboard

**Design Principles:**
- **View generators should be pluggable** - Add new view without touching core pipeline
- **Station-agnostic processing** - Automatically detect and process new stations
- **Extensible view system** - Frontend hooks can load any view type
- **Separation of concerns** - Research scripts separate from dashboard pipeline

## Implementation Plan

### Step 1: Create Clean Scripts
```bash
# Keep working logic, remove complexity
scripts/1_process_excel_to_json.py    # Based on existing dashboard_prep script
scripts/2_generate_all_views.py       # Consolidates all view generators (extensible)
scripts/3_upload_to_cdn.py            # Based on existing upload script
```

**Extensibility**: `2_generate_all_views.py` will auto-discover view generators, making it easy to add new views.

### Step 2: Simplified Python Package  
```bash
# Minimal package focused on dashboard data processing
mbon_analysis/
├── processing/excel_to_json.py       # Core Excel processing (station-agnostic)
├── processing/json_to_views.py       # View generation framework (pluggable)
└── views/                            # Individual view generators (extensible)
    ├── __init__.py
    ├── station_views.py              # Keep existing
    ├── species_views.py              # Keep existing  
    ├── acoustic_views.py             # Keep existing
    └── [future_views.py]             # Easy to add new views
```

**Extensibility**: New view types just require adding a new file to `views/` directory.

### Step 3: Delete Major Bloat
```bash
# Remove entire directory systems
rm -rf mkdocs.yml docs_site/ site/           # Complete mkdocs system
rm -rf htmlcov/ coverage.json                # Coverage reports  
rm -rf tests/ pytest.ini test_runner.py      # Entire test suite
rm -rf mbon_dash_2025.egg-info/              # Auto-generated package metadata

# Remove bloated scripts and Python modules  
rm -rf scripts/{analysis,examples,exploratory,notebooks,utils,deployment}
rm -rf mbon_analysis/{analysis,deployment,visualization}
rm -rf data/{intermediate_results,cdn/processed/paginated}

# Remove testing and build artifacts
rm -rf jest.config.js jest.setup.js tsconfig.tsbuildinfo
rm -rf dashboard_data_processing.log

# Remove unused frontend components
rm -rf src/content/ src/lib/data/
rm -rf src/components/ui/PaginationControls.tsx
rm -rf src/lib/hooks/{usePaginatedData.ts,useAcousticIndicesCSV.ts}
```

### Step 4: Simplified Package.json
```bash
# Reduce from 26 scripts to ~8 essential scripts:
"scripts": {
  "process-data": "uv run scripts/1_process_excel_to_json.py",
  "generate-views": "uv run scripts/2_generate_all_views.py", 
  "upload-cdn": "uv run scripts/3_upload_to_cdn.py",
  "pipeline": "npm run process-data && npm run generate-views && npm run upload-cdn",
  "dev": "next dev",
  "build": "next build", 
  "lint": "next lint",
  "type-check": "tsc --noEmit"
}
```

### Step 5: Clean Frontend Routes
```bash
# Remove migration/testing pages
rm -rf src/app/{acoustic-v2,species-v2,stations-v2,pagination-demo,explorer,temporal}
rm -rf src/app/api/cdn/
rm -rf src/app/stations/page.backup.tsx
```

## Extensibility Architecture

### Adding New Views (Future)
```python
# 1. Create new view generator in mbon_analysis/views/
# mbon_analysis/views/new_analysis_views.py
def generate_my_new_view(processed_data_dir):
    return {"my_data": [...], "metadata": {...}}

# 2. Add to frontend types
# src/types/data.ts  
export interface MyNewViewData { ... }
type ViewDataMap = {
  'my-new-view': MyNewViewData;
  ...
}

# 3. Add hook (auto-generated pattern)
# src/lib/hooks/useViewData.ts
export function useMyNewView() {
  return useViewData('my-new-view');
}

# 4. Use in component
const { data } = useMyNewView();
```

### Adding New Stations (Future)
```python
# Processing automatically detects new stations from Excel filenames:
# Master_Manual_42M_2h_2024.xlsx → station: "42M", year: 2024
# No code changes needed in processing pipeline
```

### Research vs Dashboard Separation
```bash
# Future structure allows research work separate from dashboard:
research_scripts/           # New directory for research (not dashboard)
├── exploratory_analysis/
├── statistical_models/  
└── paper_figures/

scripts/                   # Clean dashboard-only pipeline
├── 1_process_excel_to_json.py
├── 2_generate_all_views.py
└── 3_upload_to_cdn.py
```

## File Size Wins We Keep

The view-based approach has proven massive performance gains:
- **Acoustic Summary**: 166MB → 19.6KB (8,686x improvement) ✅
- **Species Timeline**: MB+ → 1.6KB (1000x+ improvement) ✅  
- **Index Distributions**: 2.8MB → 119KB (23x improvement) ✅
- **Raw Data Landscape**: 100KB+ → 32KB (3x improvement) ✅
- **Station Overview**: 9KB → 7KB (modest but cleaner) ✅

## Expected Results

**Before Cleanup:**
- 200+ files across multiple directories
- 26 confusing npm scripts
- 50+ JSON files in processed/
- Complex Python package with unclear boundaries
- Migration pages cluttering navigation
- Entire mkdocs system (50+ files)
- Complete test suite before basics work

**After Cleanup:**  
- 3 clear processing scripts + 8 npm scripts
- Simple Python package focused on dashboard needs  
- 11 total JSON files (6 core + 5 views)
- Clean dashboard with identical user experience
- All performance improvements preserved
- Extensible architecture for future views/stations

## Risk Mitigation

1. **Git Safety Net** - All changes are reversible
2. **Preserve Working Logic** - Reuse proven processing code
3. **Test Core Functionality** - Verify each dashboard page works after cleanup  
4. **Incremental Approach** - Clean in phases, test after each phase
5. **User Experience Priority** - Dashboard must work identically before/after

## Success Criteria

✅ **Identical User Experience** - All dashboard pages work exactly as before
✅ **Simplified Backend** - 3 processing scripts instead of 20+  
✅ **Clean File Structure** - <50 total files instead of 200+
✅ **Preserved Performance** - All view-based optimizations kept
✅ **CDN Integration** - Direct upload/download still works
✅ **Clear Documentation** - Simple README with 3-step process

---

**Next Steps:**
1. Review this plan with user
2. Create deprecated/ folder for old planning docs  
3. Implement Phase 1 (delete bloated pages/routes)
4. Implement Phase 2 (streamline backend)
5. Implement Phase 3 (preserve working logic)
6. Test dashboard functionality matches original

*Target: Transform complex, bloated codebase into clean, maintainable system while preserving all user-facing functionality.*