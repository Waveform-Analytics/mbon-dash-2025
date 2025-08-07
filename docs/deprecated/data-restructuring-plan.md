# Data Restructuring Plan

## Current Problems Identified

### 1. **Scope Issues**
- ❌ Processing years 2017-2022 instead of just **2018, 2021**
- ❌ Including all stations instead of just **9M, 14M, 37M**
- ❌ Too much deployment metadata (183 records vs ~6-12 needed)

### 2. **Data Processing Issues**
- ❌ Wrong sheet selection for environmental/acoustic files (using sheet 0 instead of sheet 1)
- ❌ Manual (detection) files not treated as primary data source
- ❌ Date parsing issues (showing "1900-01-01" as start date)

### 3. **Data Priority Issues**
- ❌ All data types treated equally instead of:
  - **Primary**: Manual detection files (species/sound identification)
  - **Secondary**: Environmental (temp, depth) and acoustic (rmsSPL) for correlations

## Corrected Data Requirements

### **Scope**
- **Years**: 2018, 2021 ONLY
- **Stations**: 9M, 14M, 37M ONLY
- **File Types**: Manual (primary), Temp, Depth, rmsSPL (secondary)

### **Raw Data Files to Process**
```
data/2018/
├── Master_Manual_9M_2h_2018.xlsx      ← PRIMARY
├── Master_Manual_14M_2h_2018.xlsx     ← PRIMARY
├── Master_Manual_37M_2h_2018.xlsx     ← PRIMARY
├── Master_9M_Temp_2018.xlsx           ← SECONDARY (sheet 1)
├── Master_14M_Temp_2018.xlsx          ← SECONDARY (sheet 1)
├── Master_37M_Temp_2018.xlsx          ← SECONDARY (sheet 1)
├── Master_9M_Depth_2018.xlsx          ← SECONDARY (sheet 1)
├── Master_14M_Depth_2018.xlsx         ← SECONDARY (sheet 1)
├── Master_37M_Depth_2018.xlsx         ← SECONDARY (sheet 1)
├── Master_rmsSPL_9M_1h_2018.xlsx      ← SECONDARY (sheet 1)
├── Master_rmsSPL_14M_1h_2018.xlsx     ← SECONDARY (sheet 1)
└── Master_rmsSPL_37M_1h_2018.xlsx     ← SECONDARY (sheet 1)

data/2021/
├── Master_Manual_9M_2h_2021.xlsx      ← PRIMARY
├── Master_Manual_14M_2h_2021.xlsx     ← PRIMARY
├── Master_Manual_37M_2h_2021.xlsx     ← PRIMARY
├── Master_9M_Temp_2021.xlsx           ← SECONDARY (sheet 1)
├── Master_14M_Temp_2021.xlsx          ← SECONDARY (sheet 1)
├── Master_37M_Temp_2021.xlsx          ← SECONDARY (sheet 1)
├── Master_9M_Depth_2021.xlsx          ← SECONDARY (sheet 1)
├── Master_14M_Depth_2021.xlsx         ← SECONDARY (sheet 1)
├── Master_37M_Depth_2021.xlsx         ← SECONDARY (sheet 1)
├── Master_rmsSPL_9M_1h_2021.xlsx      ← SECONDARY (sheet 1)
├── Master_rmsSPL_14M_1h_2021.xlsx     ← SECONDARY (sheet 1)
└── Master_rmsSPL_37M_1h_2021.xlsx     ← SECONDARY (sheet 1)
```

## Implementation Plan

### Phase 1: Update Data Processing Script
**Priority: CRITICAL**

#### Changes needed in `scripts/process_data.py`:

1. **Filter Years**:
   ```python
   # Change line 60, 111, 160 from:
   for year in ["2017", "2018", "2019", "2020", "2021", "2022"]:
   # To:
   for year in ["2018", "2021"]:
   ```

2. **Filter Stations**:
   ```python
   # Add station filtering after file processing
   STATIONS_OF_INTEREST = ["9M", "14M", "37M"]
   
   # Filter dataframes to only include stations of interest
   def filter_to_stations_of_interest(df):
       if 'station' in df.columns:
           return df[df['station'].isin(STATIONS_OF_INTEREST)]
       return df
   ```

3. **Fix Sheet Selection**:
   ```python
   # In process_environmental_files() and process_acoustic_files()
   # Change from sheet_name=0 to sheet_name=1
   df = pd.read_excel(file, sheet_name=1)  # Not sheet_name=0
   ```

4. **Filter Deployment Metadata**:
   ```python
   # In process_deployment_metadata()
   # Filter to only 2018, 2021 and 9M, 14M, 37M
   metadata_df = metadata_df[
       (metadata_df['year'].isin([2018, 2021])) & 
       (metadata_df['station'].isin(["9M", "14M", "37M"]))
   ]
   ```

5. **Data Prioritization**:
   ```python
   # Add validation to ensure Manual files are successfully processed
   # Add warnings if secondary data is missing but continue processing
   ```

### Phase 2: Update Documentation
**Priority: HIGH**

1. **Update CLAUDE.md**:
   - Correct data scope (2018, 2021, 9M/14M/37M only)
   - Clarify Manual files as primary data source
   - Update workflow instructions
   - Fix sheet selection documentation

2. **Update guides**:
   - Fix adding-stations-to-map-guide.md with correct data expectations
   - Update any other references to data structure

### Phase 3: Update Frontend Data Expectations
**Priority: MEDIUM**

1. **Update TypeScript interfaces**:
   - Ensure station filtering works correctly
   - Update expected data shapes
   - Handle filtered datasets appropriately

2. **Update components**:
   - Station map should only show 9M, 14M, 37M
   - Dashboard metrics should reflect correct scope
   - Error handling for missing data

### Phase 4: Validation & Testing
**Priority: HIGH**

1. **Data Validation**:
   - Verify only 6 stations total (3 stations × 2 years)
   - Check date ranges are reasonable
   - Confirm Manual detection data is primary
   - Validate environmental/acoustic data as supplementary

2. **Dashboard Testing**:
   - Ensure map shows correct 3 stations
   - Verify data loads without errors
   - Check metrics reflect correct scope

## Expected Outcomes After Changes

### **JSON Files Should Contain**:
- **detections.json**: Manual detection data from 6 files (3 stations × 2 years)
- **environmental.json**: Temperature + depth data from 12 files (6 temp + 6 depth)
- **acoustic.json**: rmsSPL data from 6 files (3 stations × 2 years)
- **deployment_metadata.json**: ~6-12 records (filtered to relevant deployments only)
- **stations.json**: 3 stations (9M, 14M, 37M)
- **metadata.json**: Corrected summary statistics

### **Dashboard Should Show**:
- 3 stations on map (not 10)
- Date range covering 2018-2021 (not 1900-2021)
- Focused species detection data as primary content
- Environmental/acoustic data available for correlation analysis

## Immediate Action Items

### 1. **Update Data Processing Script** (CRITICAL)
```bash
# Edit scripts/process_data.py with the changes above
# Then regenerate data:
uv run scripts/process_data.py
```

### 2. **Update CLAUDE.md** (HIGH PRIORITY)
- Fix data structure documentation
- Update workflow instructions
- Clarify primary vs secondary data sources

### 3. **Test Dashboard** (HIGH PRIORITY)
```bash
# After data regeneration:
npm run dev
# Verify 3 stations show on map
# Check date ranges are correct
# Confirm detection data loads properly
```

### 4. **Update Documentation** (MEDIUM PRIORITY)
- Fix guides and other documentation
- Update any hardcoded assumptions about data structure

## Future Considerations

### **Analysis Focus**:
1. **Primary Analysis**: Species detection patterns in Manual files
2. **Correlation Analysis**: How environmental factors (temp, depth, SPL) relate to detections
3. **Temporal Patterns**: Changes between 2018 and 2021
4. **Station Comparison**: Differences between 9M, 14M, 37M locations

### **Dashboard Features Priority**:
1. **Detection visualization** (primary)
2. **Environmental correlation tools** (secondary)
3. **Temporal comparison tools** (secondary)
4. **Station-by-station analysis** (secondary)

---

**Status**: Ready to implement
**Next Step**: Update `scripts/process_data.py` with the changes outlined above
**Timeline**: Should be completed before working on additional dashboard pages