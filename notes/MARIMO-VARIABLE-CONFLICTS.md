# Marimo Variable Conflicts - Problem & Solution

## The Problem

Marimo notebooks use **reactive programming** with **globally scoped variables**. This creates a fundamental challenge:

- All variables defined in any cell are available in ALL other cells
- If you define the same variable name in multiple cells, they conflict
- Variable conflicts can cause unexpected behavior, bugs, and broken reactive execution

### Common Conflict Patterns

**Plotting Variables:**
```python
# Cell 1
ax = plt.subplots()[1]
ax.plot(data1)

# Cell 2 - CONFLICT!
ax = plt.gca()  
ax.hist(data2)
```

**DataFrame Variables:**
```python
# Cell 1  
df = pd.read_csv('file1.csv')

# Cell 2 - CONFLICT!
df = pd.read_csv('file2.csv')
```

**Temporary Variables:**
```python
# Cell 1
temp = process_data(raw_data)

# Cell 2 - CONFLICT!
temp = "processing status"
```

## The Solution: Automated Variable Conflict Fixer

We've created a comprehensive script that automatically detects and fixes all variable conflicts in marimo notebooks.

### Script Location
```
python/scripts/fix_marimo_variables.py
```

### Key Features

1. **Comprehensive Detection** - Uses AST parsing to find ALL variable assignments
2. **Smart Renaming** - Uses semantic suffixes before falling back to numbers
3. **Safety Features** - Backup, dry-run, and report-only modes
4. **General Purpose** - Works with any variable names, not just common ones

### Usage

**Check for conflicts:**
```bash
python scripts/fix_marimo_variables.py notebook.py --report-only
```

**Preview fixes:**
```bash
python scripts/fix_marimo_variables.py notebook.py --dry-run
```

**Fix with backup:**
```bash
python scripts/fix_marimo_variables.py notebook.py --backup
```

**Batch check all notebooks:**
```bash
find scripts/notebooks -name "*.py" -exec python scripts/fix_marimo_variables.py {} --report-only \;
```

### How It Works

1. **Parse Cells** - Identifies all `@app.cell` blocks and function definitions
2. **AST Analysis** - Uses Python's AST parser to find variable assignments
3. **Detect Conflicts** - Finds variables assigned in multiple cells
4. **Smart Renaming** - Generates meaningful unique names
5. **Safe Replacement** - Uses whole-word replacement to avoid partial matches

### Naming Strategy

**Semantic Suffixes (Preferred):**
- `ax` → `ax_plot`, `ax_chart`, `ax_graph`, `ax_viz`
- `fig` → `fig_plot`, `fig_chart`, `fig_diagram`
- `df` → `df_data`, `df_temp`, `df_proc`, `df_clean`
- `result` → `result_output`, `result_final`, `result_temp`

**Numeric Fallback:**
- `variable` → `variable_1`, `variable_2`, etc.

**Cell-based (Last Resort):**
- `variable` → `variable_cell_1`, `variable_cell_2`

## Real-World Example

We used this approach to fix conflicts in `04_fish_and_indices_patterns.py`:

**Before:**
```python
# Multiple cells all using 'ax'
ax = axes_diel[i]
ax = axes_conc[0, i] 
ax = axes_temp[i]
ax = axes_station[0, 0]
```

**After (Manual Fix):**
```python
# Each ax has a semantic name
ax_diel = axes_diel[i]
ax_conc_idx = axes_conc[0, i]
ax_temp = axes_temp[i] 
ax_station_means = axes_station[0, 0]
```

The automated script would have detected and fixed these conflicts automatically.

## Integration into Workflow

### Pre-commit Check
Add to your development routine:
```bash
# Check all notebooks before committing
python scripts/fix_marimo_variables.py scripts/notebooks/*.py --report-only
```

### Automated Fix
When conflicts are found:
```bash
# Fix all conflicts with backups
python scripts/fix_marimo_variables.py scripts/notebooks/problem_notebook.py --backup
```

### CI/CD Integration
Could be integrated into automated workflows to catch conflicts early.

## Benefits

1. **Prevents Bugs** - Eliminates variable conflicts that break marimo's reactivity
2. **Saves Time** - No more manual renaming of conflicting variables
3. **Consistent Naming** - Uses semantic patterns for better code readability
4. **Safe Operation** - Multiple safety modes to prevent accidental changes
5. **Comprehensive** - Catches ALL variable conflicts, not just obvious ones

## Documentation

- **Full README**: `python/scripts/README_marimo_fixer.md`
- **Script**: `python/scripts/fix_marimo_variables.py`

This tool addresses a fundamental challenge in marimo development and makes working with reactive notebooks much more reliable and efficient.