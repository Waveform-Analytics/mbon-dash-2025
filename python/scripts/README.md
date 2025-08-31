# MBON Data Processing Scripts

This directory contains simple entry point scripts that call the `mbon_analysis` package CLI. The core functionality has been moved into the package for better organization and reusability.

## 🏗️ **Architecture Overview**

### **Package-Based Design**
- **Core functionality**: `mbon_analysis/` package
- **CLI interface**: `mbon_analysis.cli` module
- **Entry points**: Simple scripts in this directory
- **Root orchestration**: `package.json` npm scripts

### **Package.json vs Makefile**
- **`package.json`**: Root-level orchestration (recommended)
- **`Makefile`**: Python-specific convenience (optional)
- **No conflict**: They serve different purposes

## 📦 **Available Scripts**

### **Entry Point Scripts**
These are simple wrappers that call the package CLI:

- **`generate_views.py`**: Generate dashboard view files
- **`compile_indices.py`**: Compile all indices into single JSON
- **`convert_indices_to_json.py`**: Convert raw indices CSV files to combined JSON (alias for compile_indices)
- **`compile_detections.py`**: Compile all detections/annotations data into single JSON
- **`detections_utils.py`**: Work with compiled detections JSON file
- **`migrate_data.py`**: Migrate data to top-level directory
- **`test_dashboard.py`**: Test dashboard data access

### **Usage**
```bash
# Direct script execution
cd python/scripts
python generate_views.py
python compile_indices.py
python convert_indices_to_json.py
python migrate_data.py
python test_dashboard.py

# Via uv run
cd python
uv run scripts/generate_views.py
uv run scripts/compile_indices.py
uv run scripts/convert_indices_to_json.py
uv run scripts/migrate_data.py
uv run scripts/test_dashboard.py
```

## 🚀 **Recommended Usage Patterns**

### **1. Package.json (Root Level)**
```bash
# From project root
npm run data:views        # Generate all views
npm run data:compile      # Compile indices
npm run data:migrate      # Migrate data
npm run test:data         # Test dashboard access
```

### **2. Direct CLI (Python Level)**
```bash
# From python directory
uv run mbon-analysis generate-views
uv run mbon-analysis compile-indices
uv run mbon-analysis migrate-data
uv run mbon-analysis test-dashboard
```

### **3. Makefile (Optional Convenience)**
```bash
# From python directory
make views               # Generate views
make indices            # Compile indices
make migrate            # Migrate data
make test-data          # Test data access
```

## 📊 **CLI Commands Reference**

### **Main CLI Interface**
```bash
uv run mbon-analysis --help
```

### **Available Commands**
```bash
# Generate views
uv run mbon-analysis generate-views [--view stations] [--verbose]

# Compile indices (Year-aware structure)
uv run mbon-analysis compile-indices [--output path] [--verbose]

# Migrate data
uv run mbon-analysis migrate-data [--force] [--verbose]

# Test dashboard
uv run mbon-analysis test-dashboard [--check-api] [--verbose]

# Work with compiled indices
uv run mbon-analysis indices-utils file.json [--action summary|stations|export]
```

### **Compile Indices Command Details**
The `compile-indices` command creates a year-aware JSON structure:

```bash
# Basic compilation
uv run mbon-analysis compile-indices

# Verbose output with progress details
uv run mbon-analysis compile-indices --verbose

# Custom output location
uv run mbon-analysis compile-indices --output custom/path/indices.json

# Help
uv run mbon-analysis compile-indices --help
```

**Output Structure:**
- **Hierarchical**: `stations → year → bandwidth → data`
- **Year Extraction**: Automatically parsed from filenames
- **Metadata**: Generation timestamp, file counts, record counts
- **Summary**: Statistics by station, year, and bandwidth

## 🔧 **Package Structure**

```
mbon_analysis/
├── cli.py                    # Main CLI interface
├── utils/
│   ├── compiled_indices.py   # Indices compilation utilities
│   ├── data_migration.py     # Data migration utilities
│   └── dashboard_testing.py  # Dashboard testing utilities
├── views/                    # View generators
├── data/                     # Data loaders
└── ...
```

## 📊 **Compiled Indices System**

### **Overview**
The compiled indices system converts raw acoustic indices CSV files into a single, structured JSON file for efficient dashboard access and analysis.

### **Features**
- **Year-aware structure**: Automatically extracts and organizes data by year from filenames
- **Hierarchical organization**: `stations → year → bandwidth → data`
- **Comprehensive metadata**: File information, summary statistics, and data validation
- **Performance optimized**: Single JSON file instead of multiple CSV files
- **Analysis ready**: Direct pandas DataFrame conversion and filtering capabilities

### **JSON Structure**
```json
{
  "metadata": {
    "generated_at": "2025-08-30T21:42:50.909948",
    "description": "Compiled acoustic indices data from all available CSV files",
    "version": "1.0.0",
    "total_files_processed": 6,
    "total_records": 52160
  },
  "stations": {
    "14M": {
      "2021": {                    // ← Year level
        "FullBW": {
          "data": [...],           // ← Actual indices data
          "columns": [...],        // ← Column names
          "shape": [8735, 64],     // ← Data dimensions
          "file_info": {
            "filename": "Acoustic_Indices_14M_2021_FullBW_v2_Final.csv",
            "records_count": 8735,
            "columns_count": 64
          }
        },
        "8kHz": { ... }
      }
    }
  },
  "summary": {
    "stations": {
      "14M": {
        "total_records": 17469,
        "years": {
          "2021": {
            "total_records": 17469,
            "bandwidths": {
              "FullBW": 8735,
              "8kHz": 8734
            }
          }
        }
      }
    },
    "years": { "2021": 52160 },    // ← Global year summary
    "bandwidths": {
      "FullBW": 26078,
      "8kHz": 26082
    },
    "total_files": 6,
    "total_records": 52160
  }
}
```

### **Usage Examples**

#### **Command Line**
```bash
# Compile all indices with verbose output
uv run python -m mbon_analysis.cli compile-indices --verbose

# Use the dedicated script
uv run python scripts/convert_indices_to_json.py --verbose

# Specify custom output location
uv run python -m mbon_analysis.cli compile-indices --output custom/path/indices.json
```

#### **Programmatic Usage**
```python
from mbon_analysis.utils.compiled_indices import CompiledIndicesManager

# Initialize manager
manager = CompiledIndicesManager("data/processed/compiled_indices.json")

# Get overview
summary = manager.get_summary()
print(f"Total records: {summary['total_records']:,}")
print(f"Available years: {list(summary['years'].keys())}")
print(f"Available stations: {manager.get_stations()}")

# Get specific data
df = manager.get_station_dataframe("14M", "FullBW")
print(f"14M FullBW data: {df.shape}")

# Filter by date range
filtered_df = manager.filter_by_date_range(
    "14M", "FullBW", 
    "2021-01-01", "2021-06-30"
)

# Export to CSV
manager.export_station_to_csv("14M", "FullBW", "output.csv")
```

### **Data Sources**
The system automatically processes files matching this pattern:
```
data/raw/indices/Acoustic_Indices_{STATION}_{YEAR}_{BANDWIDTH}_v2_Final.csv
```

**Examples:**
- `Acoustic_Indices_14M_2021_FullBW_v2_Final.csv`
- `Acoustic_Indices_37M_2021_8kHz_v2_Final.csv`
- `Acoustic_Indices_9M_2021_FullBW_v2_Final.csv`

### **Benefits**
- **Performance**: Single JSON file (272MB) vs multiple CSV files
- **Organization**: Clear hierarchical structure by station/year/bandwidth
- **Analysis**: Direct pandas DataFrame access with filtering
- **Dashboard**: Optimized for dashboard queries and visualizations
- **Future-proof**: Automatically handles new years and stations
- **Validation**: Comprehensive error handling and data validation

### **Key Improvements (Latest Version)**
- **Year Awareness**: Automatically extracts and organizes data by year from filenames
- **Enhanced Structure**: `stations → year → bandwidth → data` hierarchy
- **Comprehensive Summaries**: Year breakdowns at both station and global levels
- **File Information**: Each dataset includes original filename with year
- **Error Handling**: Graceful handling of missing files and data validation
- **Metadata Tracking**: Generation timestamp, version, and processing statistics

## 🎯 **Best Practices**

### **For Development**
1. **Use package.json scripts** for root-level orchestration
2. **Use direct CLI** for Python-specific tasks
3. **Use Makefile** for convenience shortcuts (optional)

### **For CI/CD**
```yaml
# GitHub Actions example
- name: Generate Views
  run: |
    cd python
    uv run mbon-analysis generate-views

- name: Test Dashboard
  run: |
    cd python
    uv run mbon-analysis test-dashboard --check-api
```

### **For Documentation**
- **Package.json**: Project-level workflow
- **CLI**: Python-specific functionality
- **Makefile**: Developer convenience

## 🔄 **Migration from Old Scripts**

### **Old Way**
```bash
cd python/scripts
python generate_all_views.py
python generate_compiled_indices.py
python migrate_data_to_top_level.py
```

### **New Way**
```bash
# Option 1: Package.json (recommended)
npm run data:views
npm run data:compile
npm run data:migrate

# Option 2: Direct CLI
cd python
uv run mbon-analysis generate-views
uv run mbon-analysis compile-indices
uv run mbon-analysis migrate-data

# Option 3: Entry point scripts
cd python/scripts
python generate_views.py
python compile_indices.py
python migrate_data.py
```

## 📚 **Benefits of New Architecture**

### ✅ **Better Organization**
- Core functionality in package
- Reusable modules
- Clear separation of concerns

### ✅ **Professional CLI**
- Consistent interface
- Help documentation
- Error handling

### ✅ **Flexible Usage**
- Multiple entry points
- Root-level orchestration
- Developer convenience

### ✅ **Maintainability**
- Single source of truth
- Easy to test
- Easy to extend

## 🎉 **Summary**

The new architecture provides:
- **Professional CLI interface** via `mbon_analysis` package
- **Root-level orchestration** via `package.json`
- **Developer convenience** via `Makefile` (optional)
- **Simple entry points** via scripts in this directory

Choose the approach that best fits your workflow! 🚀
