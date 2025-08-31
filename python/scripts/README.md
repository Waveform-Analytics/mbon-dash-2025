# MBON Data Processing Scripts

This directory contains scripts for processing and organizing MBON acoustic indices data.

## Scripts Overview

### 1. `migrate_data_to_top_level.py`
**Purpose**: Migrate data from `python/data` to top-level `data/` directory for better organization.

**Why migrate?**
- Better separation of concerns
- Shared access between Python backend and Next.js frontend
- Standard project structure
- Easier CDN synchronization

**Usage**:
```bash
cd python/scripts
python migrate_data_to_top_level.py
```

**What it does**:
- Moves all data from `python/data/` to `data/` (top-level)
- Creates a backup of original data
- Updates data loader paths automatically
- Creates a reference file for backward compatibility

### 2. `generate_compiled_indices.py`
**Purpose**: Compile all acoustic indices CSV files into a single large JSON file for intermediate processing.

**Usage**:
```bash
cd python/scripts
python generate_compiled_indices.py
```

**What it does**:
- Reads all acoustic indices CSV files (6 files total)
- Compiles them into a single JSON structure
- Organizes data by station and bandwidth
- Includes metadata and summary statistics
- Saves to `data/processed/compiled_indices.json`

**Output Structure**:
```json
{
  "metadata": {
    "generated_at": "2024-01-01T12:00:00",
    "description": "Compiled acoustic indices data",
    "version": "1.0.0",
    "total_files_processed": 6,
    "total_records": 123456
  },
  "stations": {
    "9M": {
      "FullBW": {
        "data": [...],
        "columns": [...],
        "shape": [rows, cols],
        "file_info": {...}
      },
      "8kHz": {
        "data": [...],
        "columns": [...],
        "shape": [rows, cols],
        "file_info": {...}
      }
    },
    "14M": {...},
    "37M": {...}
  },
  "summary": {
    "stations": {...},
    "bandwidths": {...},
    "total_files": 6,
    "total_records": 123456
  }
}
```

### 3. `compiled_indices_utils.py`
**Purpose**: Utility functions for working with the compiled indices JSON file.

**Usage**:
```bash
# Get summary of compiled data
python compiled_indices_utils.py data/processed/compiled_indices.json --action summary

# List available stations
python compiled_indices_utils.py data/processed/compiled_indices.json --action stations

# Export specific station data to CSV
python compiled_indices_utils.py data/processed/compiled_indices.json \
  --action export \
  --station 9M \
  --bandwidth FullBW \
  --output exported_9M_FullBW.csv
```

### 4. `test_dashboard_data_access.py`
**Purpose**: Test script to verify dashboard data access after migration.

**Usage**:
```bash
# Test data access (run after migration)
python test_dashboard_data_access.py

# Test with dashboard running
npm run dev:dashboard  # In another terminal
python test_dashboard_data_access.py
```

**What it tests**:
- View file accessibility in both old and new locations
- Dashboard API endpoint functionality
- JSON file readability and data integrity
- Provides recommendations for next steps

**Python API**:
```python
from compiled_indices_utils import CompiledIndicesManager

# Initialize manager
manager = CompiledIndicesManager("data/processed/compiled_indices.json")

# Get summary
summary = manager.get_summary()
print(f"Total records: {summary['total_records']:,}")

# Get specific station data
df = manager.get_station_dataframe("9M", "FullBW")
print(f"9M FullBW data shape: {df.shape}")

# Filter by date range
filtered_df = manager.filter_by_date_range("9M", "FullBW", "2021-01-01", "2021-06-30")

# Get indices summary statistics
stats = manager.get_indices_summary("9M", "FullBW")
```

## Recommended Data Organization

### Before Migration:
```
mbon-dash-2025/
├── python/
│   └── data/           # Data mixed with Python code
│       ├── raw/
│       ├── processed/
│       └── views/
├── dashboard/          # Next.js frontend
└── ...
```

### After Migration:
```
mbon-dash-2025/
├── data/               # Top-level data directory
│   ├── raw/           # Original data files
│   │   ├── indices/   # CSV indices files
│   │   ├── metadata/  # Reference files
│   │   └── [year]/    # Year-specific data
│   ├── processed/     # Intermediate processed files
│   │   └── compiled_indices.json  # Large compiled JSON
│   └── views/         # Final view files for dashboard
├── python/            # Python backend code
├── dashboard/         # Next.js frontend
└── ...
```

## Benefits of New Structure

1. **Shared Access**: Both Python and Next.js can access the same data
2. **Clear Separation**: Data is separate from application code
3. **Standard Practice**: Follows common project organization patterns
4. **CDN Sync**: Easier to sync with CDN when data is centralized
5. **Scalability**: Better structure for growing datasets

## File Sizes and Performance

### Compiled Indices JSON
- **Expected size**: ~200-300 MB (depending on data)
- **Loading time**: ~5-10 seconds on first load
- **Memory usage**: ~500-800 MB when loaded
- **Use case**: Intermediate processing, not for direct dashboard serving

### Performance Tips
1. **Lazy loading**: Use `CompiledIndicesManager` for on-demand loading
2. **Caching**: Cache frequently accessed data in memory
3. **Streaming**: For very large files, consider streaming JSON parsing
4. **Compression**: Consider gzipping the JSON file for storage

## Next Steps

1. **Run migration**: Execute `migrate_data_to_top_level.py`
2. **Generate compiled indices**: Run `generate_compiled_indices.py`
3. **Test data access**: Run `test_dashboard_data_access.py` to verify everything works
4. **Update .gitignore**: Add `data/processed/` to ignore large files
5. **Test integration**: Verify Python scripts still work
6. **Update dashboard**: Modify frontend to use new data paths (if needed)
7. **CDN sync**: Update CDN synchronization process

## Troubleshooting

### Common Issues

1. **File not found errors**: Ensure data migration completed successfully
2. **Memory errors**: The compiled JSON is large - ensure sufficient RAM
3. **Path issues**: Check that data loader paths were updated correctly

### Logs
- Migration logs: `data_migration.log`
- Compilation logs: `compiled_indices_generation.log`
- Check these files for detailed error information
