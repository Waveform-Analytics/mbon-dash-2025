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
- **`migrate_data.py`**: Migrate data to top-level directory
- **`test_dashboard.py`**: Test dashboard data access

### **Usage**
```bash
# Direct script execution
cd python/scripts
python generate_views.py
python compile_indices.py
python migrate_data.py
python test_dashboard.py

# Via uv run
cd python
uv run scripts/generate_views.py
uv run scripts/compile_indices.py
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

# Compile indices
uv run mbon-analysis compile-indices [--output path] [--verbose]

# Migrate data
uv run mbon-analysis migrate-data [--force] [--verbose]

# Test dashboard
uv run mbon-analysis test-dashboard [--check-api] [--verbose]

# Work with compiled indices
uv run mbon-analysis indices-utils file.json [--action summary|stations|export]
```

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
