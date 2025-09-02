# MBON Data Inventory

*Last updated: September 2, 2025*

This document tracks all data files in the MBON Marine Biodiversity Dashboard project, organized by processing stage and purpose.

## Overview

| Data Tier | Purpose | File Count | Total Size | Location |
|-----------|---------|------------|------------|----------|
| **Raw Data** | Original source files (Excel/CSV) | 33 files | ~Various | `data/raw/` |
| **Processed Data** | Compiled JSON for analysis | 3 files | ~470 MB | `data/processed/` |
| **View Data** | Optimized dashboard views | 10 files | ~11.7 MB | `data/views/` |

---

## 1. Raw Data Files

**Location**: `data/raw/`  
**Total Files**: 33 files  
**Purpose**: Original source data from field deployments and analysis

### 1.1 Detection Data (Primary Scientific Data)
*Manual species annotations from hydrophone recordings*

**2018 Data:**
- `data/raw/2018/detections/Master_Manual_9M_2h_2018.xlsx` - Station 9M detections  
- `data/raw/2018/detections/Master_Manual_14M_2h_2018.xlsx` - Station 14M detections  
- `data/raw/2018/detections/Master_Manual_37M_2h_2018.xlsx` - Station 37M detections  

**2021 Data:**
- `data/raw/2021/detections/Master_Manual_9M_2h_2021.xlsx` - Station 9M detections  
- `data/raw/2021/detections/Master_Manual_14M_2h_2021.xlsx` - Station 14M detections  
- `data/raw/2021/detections/Master_Manual_37M_2h_2021.xlsx` - Station 37M detections  

**Format**: 2-hour resolution species detection events  
**Key Species**: sp (silver perch), otbw (oyster toadfish), bde (bottlenose dolphin), anth (anthropogenic)

### 1.2 Environmental Data
*Temperature and depth measurements from hydrophone locations*

**2018 Temperature:**
- `2018/environmental/Master_9M_Temp_2018.xlsx`
- `2018/environmental/Master_14M_Temp_2018.xlsx`  
- `2018/environmental/Master_37M_Temp_2018.xlsx`

**2018 Depth:**
- `2018/environmental/Master_9M_Depth_2018.xlsx`
- `2018/environmental/Master_14M_Depth_2018.xlsx`
- `2018/environmental/Master_37M_Depth_2018.xlsx`

**2021 Temperature:**
- `2021/environmental/Master_9M_Temp_2021.xlsx`
- `2021/environmental/Master_14M_Temp_2021.xlsx`
- `2021/environmental/Master_37M_Temp_2021.xlsx`

**2021 Depth:**
- `2021/environmental/Master_9M_Depth_2021.xlsx`
- `2021/environmental/Master_14M_Depth_2021.xlsx`
- `2021/environmental/Master_37M_Depth_2021.xlsx`

**Format**: Hourly measurements  
**Variables**: Temperature (°C), Depth (meters)

### 1.3 Acoustic Indices (Core Analysis Data)
*56+ computed acoustic indices from audio analysis*

**Station 9M:**
- `indices/Acoustic_Indices_9M_2021_FullBW_v2_Final.csv` - Full bandwidth analysis
- `indices/Acoustic_Indices_9M_2021_8kHz_v2_Final.csv` - 8kHz bandwidth analysis

**Station 14M:**
- `indices/Acoustic_Indices_14M_2021_FullBW_v2_Final.csv` - Full bandwidth analysis  
- `indices/Acoustic_Indices_14M_2021_8kHz_v2_Final.csv` - 8kHz bandwidth analysis

**Station 37M:**
- `indices/Acoustic_Indices_37M_2021_FullBW_v2_Final.csv` - Full bandwidth analysis
- `indices/Acoustic_Indices_37M_2021_8kHz_v2_Final.csv` - 8kHz bandwidth analysis

**Format**: Hourly resolution, 2021 data only  
**Index Categories**:
- Temporal Domain: ZCR, MEANt, VARt, SKEWt, KURTt, LEQt
- Frequency Domain: MEANf, VARf, SKEWf, KURTf, NBPEAKS  
- Acoustic Complexity: ACI, NDSI, ADI, AEI
- Diversity Indices: H_Havrda, H_Renyi, H_pairedShannon, RAOQ
- Bioacoustic: BioEnergy, AnthroEnergy, BI, rBA
- Spectral Coverage: LFC, MFC, HFC

### 1.4 Legacy Acoustic Data
*RMS sound pressure levels (will be deprecated)*

**2018:**
- `2018/legacy_acoustic/Master_rmsSPL_9M_1h_2018.xlsx`
- `2018/legacy_acoustic/Master_rmsSPL_14M_1h_2018.xlsx`  
- `2018/legacy_acoustic/Master_rmsSPL_37M_1h_2018.xlsx`

**2021:**
- `2021/legacy_acoustic/Master_rmsSPL_9M_1h_2021.xlsx`
- `2021/legacy_acoustic/Master_rmsSPL_14M_1h_2021.xlsx`
- `2021/legacy_acoustic/Master_rmsSPL_37M_1h_2021.xlsx`

**Status**: Being replaced by acoustic indices data

### 1.5 Metadata and Reference Files

**Species/Sound Classifications:**
- `metadata/det_column_names.csv` - Species codes and biological/anthropogenic categories

**Acoustic Indices Reference:**
- `metadata/Updated_Index_Categories_v2.csv` - Index definitions and scientific categories

**Deployment Information:**
- `metadata/1_Montie Lab_metadata_deployments_2017 to 2022.xlsx` - Station coordinates, deployment history, equipment details

---

## 2. Processed Data Files

**Location**: `./data/processed/`  
**Total Files**: 3 files  
**Total Size**: ~470 MB  
**Purpose**: Compiled, cleaned data ready for analysis

### 2.1 Species Detection Data
- **File**: `compiled_detections.json`
- **Size**: 31.1 MB  
- **Created**: August 30, 2025
- **Records**: All manual species detections from 2018 and 2021
- **Structure**: Nested by station → year → species detection events
- **Resolution**: 2-hour windows
- **Usage**: Species timeline analysis, biodiversity metrics

### 2.2 Full Acoustic Indices (Original)
- **File**: `compiled_indices.json`  
- **Size**: 278.5 MB
- **Created**: August 30, 2025
- **Records**: 52,160 total records
- **Structure**: Nested by station → year → bandwidth → hourly records
- **Resolution**: Hourly (all hours 0-23)
- **Coverage**: 3 stations × 2021 × 2 bandwidths
- **Usage**: Full-resolution acoustic analysis, model training

### 2.3 Decimated Acoustic Indices (Even Hours)  
- **File**: `compiled_indices_even_hours.json`
- **Size**: 139.3 MB  
- **Created**: September 2, 2025
- **Records**: 26,075 total records (50% of original)
- **Structure**: Same as original, but decimated to even hours only
- **Resolution**: 2-hourly (hours 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22)
- **Purpose**: Temporal alignment with detection data (2-hour windows)
- **Usage**: Correlation analysis between indices and species detections

**Decimation Details**:
- Station 14M: 8,735 → 4,368 records (FullBW), 8,734 → 4,368 records (8kHz)
- Station 37M: 8,727 → 4,364 records (FullBW), 8,733 → 4,367 records (8kHz)  
- Station 9M: 8,616 → 4,304 records (FullBW), 8,615 → 4,304 records (8kHz)

---

## 3. View Data Files (Dashboard-Ready)

**Location**: `data/views/`  
**Total Files**: 10 files  
**Total Size**: ~11.7 MB  
**Purpose**: Optimized, pre-processed data for dashboard visualizations

### 3.1 Station Information
- **File**: `stations.json`
- **Size**: 11.8 KB
- **Content**: Station metadata, coordinates, deployment info
- **Usage**: Interactive station map, station selection

### 3.2 Dataset Summary  
- **File**: `datasets_summary.json` / `datasets.json`
- **Size**: 2.2 KB each (duplicate files)
- **Content**: Record counts, date ranges, data availability
- **Usage**: Landing page dataset overview cards

### 3.3 Acoustic Indices Reference
- **File**: `indices_reference.json` / `indices.json`  
- **Size**: 45.2 KB each (duplicate files)
- **Content**: All 56+ acoustic indices with descriptions, categories, formulas
- **Usage**: Filterable indices reference table, educational content

### 3.4 Project Metadata
- **File**: `project_metadata.json` / `metadata.json`
- **Size**: 5.3 KB each (duplicate files)  
- **Content**: Project description, research context, methodology
- **Usage**: Landing page content, about sections

### 3.5 Acoustic Indices Distributions
- **File**: `acoustic_indices_distributions.json` / `acoustic.json`
- **Size**: 601.4 KB each (duplicate files)
- **Content**: Statistical summaries, distributions for all acoustic indices
- **Usage**: Index exploration, statistical visualizations

### 3.6 Species Detection Heatmap
- **File**: `heatmap.json`
- **Size**: 10.8 MB
- **Content**: Pre-processed heatmap data for species detection visualizations
- **Usage**: Interactive heatmap charts, species distribution analysis

---

## 4. Data Processing Pipeline

### 4.1 Current Pipeline Status
```
Raw Excel/CSV → Processed JSON → View Files → CDN
   (33 files)      (3 files)     (5 files)    (Global)
```

### 4.2 Processing Scripts
- `scripts/compile_indices.py` - Creates `compiled_indices.json`  
- `scripts/compile_detections.py` - Creates `compiled_detections.json`
- `scripts/04_decimate_indices_even_hours.py` - Creates `compiled_indices_even_hours.json`
- `scripts/generate_views.py` - Generates dashboard view files
- `scripts/upload_to_cdn.py` - Uploads to Cloudflare R2

### 4.3 Two-Tier Architecture
**Tier 1 - Small View Files (< 50KB)**: Direct CDN access
- `stations.json`, `datasets_summary.json`, `project_metadata.json`, `indices_reference.json`

**Tier 2 - Large Datasets (> 50MB)**: Progressive loading via API  
- `compiled_indices.json`, `compiled_indices_even_hours.json`, `compiled_detections.json`

---

## 5. Data Quality & Coverage

### 5.1 Station Coverage
| Station | 2018 Data | 2021 Data | Acoustic Indices | Notes |
|---------|-----------|-----------|------------------|-------|
| **9M** | ✅ Complete | ✅ Complete | ✅ 2021 only | Full dataset |
| **14M** | ✅ Complete | ✅ Complete | ✅ 2021 only | Full dataset |  
| **37M** | ✅ Complete | ✅ Complete | ✅ 2021 only | Full dataset |

### 5.2 Temporal Coverage
- **Detection Data**: 2018, 2021 (2-hour resolution)
- **Environmental Data**: 2018, 2021 (hourly resolution)
- **Acoustic Indices**: 2021 only (hourly resolution)
- **Legacy RMS**: 2018, 2021 (hourly resolution, being phased out)

### 5.3 Data Integrity
- **Missing Data**: Handled gracefully in processing pipeline
- **Validation**: Automated data quality checks in place
- **Backups**: Raw data backed up in version control
- **Processing Logs**: Metadata tracks processing dates and record counts

---

## 6. Storage & Access

### 6.1 Local Storage
- **Raw Data**: `data/raw/` (active location)
- **Processed Data**: `data/processed/` (active location)
- **View Data**: `data/views/` (active location)

### 6.2 CDN Storage (Cloudflare R2)
- **Bucket**: `mbon-usc-2025`
- **Public URL**: `https://waveformdata.work`
- **Small Views**: Served directly from CDN
- **Large Files**: Fetched by API routes for server-side filtering

### 6.3 Dashboard Access Patterns
- **Landing Page**: Loads `stations.json`, `datasets_summary.json` directly
- **Indices Reference**: Loads `indices_reference.json` directly  
- **Analysis Pages**: Use API routes for progressive loading of large datasets

---

## 7. Future Data Plans

### 7.1 Planned Additions
- [ ] 2018 acoustic indices (when available)
- [ ] Additional station data (if provided)
- [ ] Processed analysis results (PCA, correlation matrices)
- [ ] Model outputs and predictions

### 7.2 Data Pipeline Improvements
- [ ] Automated data validation
- [ ] Incremental processing for new data
- [ ] Data lineage tracking
- [ ] Performance benchmarks

### 7.3 View Generation Needs
- [x] View files are now in active location
- [ ] Clean up duplicate view files (keep one version of each)
- [ ] Create new views for analysis results
- [ ] Optimize large file progressive loading
- [ ] Add data export functionality

---

## 8. Notes & Maintenance

### 8.1 Key Insights
- **Temporal Alignment**: New `compiled_indices_even_hours.json` solves the timing mismatch between hourly indices and 2-hour detections
- **Data Size**: Acoustic indices are the largest dataset (278MB original, 139MB decimated)
- **Coverage Gap**: No acoustic indices for 2018 (only detections and environmental data)

### 8.2 Maintenance Tasks
- [x] View files are now in active location  
- [ ] Clean up duplicate view files (datasets.json/datasets_summary.json, etc.)
- [ ] Set up automated data pipeline
- [ ] Monitor data quality and completeness
- [ ] Update this document when new data is added

### 8.3 Data Dependencies
- **Dashboard**: Depends on view files and processed JSON files
- **Analysis**: Depends on processed JSON files
- **Visualizations**: Mix of direct view files and API-loaded large datasets

---

*This inventory will be updated as new data is processed or existing data is modified.*