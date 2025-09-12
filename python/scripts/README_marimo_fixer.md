# Marimo Variable Conflict Fixer

This script automatically detects and fixes variable naming conflicts in marimo notebooks.

## Why This is Needed

Marimo notebooks use **reactive programming** where all variables are **globally scoped** across the entire notebook. This means:

- Any variable defined in one cell is available in all other cells
- If you define the same variable name in multiple cells, they will conflict
- Variable conflicts can cause unexpected behavior and bugs

Common conflict patterns:
- `ax` variables in plotting cells
- `fig` variables for matplotlib figures  
- `df` variables for DataFrames
- `data`, `temp`, `result` variables

## Usage

### Check for conflicts (report only)
```bash
python scripts/fix_marimo_variables.py notebook.py --report-only
```

### Preview changes (dry run)
```bash
python scripts/fix_marimo_variables.py notebook.py --dry-run
```

### Fix conflicts automatically
```bash
python scripts/fix_marimo_variables.py notebook.py
```

### Fix with backup
```bash
python scripts/fix_marimo_variables.py notebook.py --backup
```

## How It Works

1. **Parse Cells**: Identifies all `@app.cell` blocks and their function definitions
2. **Analyze Variables**: Uses AST parsing to find variable assignments in each cell
3. **Detect Conflicts**: Finds variables that are assigned in multiple cells
4. **Generate Unique Names**: Creates semantic or numeric suffixes for conflicting variables
5. **Apply Fixes**: Replaces variable names throughout each conflicting cell

## Naming Strategy

The script uses intelligent renaming:

1. **Semantic suffixes** (preferred):
   - `ax` → `ax_plot`, `ax_chart`, `ax_graph`, `ax_viz`
   - `fig` → `fig_plot`, `fig_chart`, `fig_diagram`  
   - `df` → `df_data`, `df_temp`, `df_proc`, `df_clean`

2. **Numeric suffixes** (fallback):
   - `variable` → `variable_1`, `variable_2`, etc.

3. **Cell-based** (last resort):
   - `variable` → `variable_cell_1`, `variable_cell_2`, etc.

## Example

**Before (with conflicts):**
```python
@app.cell
def _():
    ax = plt.subplots()[1]
    ax.plot([1, 2, 3])
    return ax

@app.cell  
def _():
    ax = plt.gca()  # Conflict!
    ax.hist([1, 2, 3])
    return ax
```

**After (conflicts resolved):**
```python
@app.cell
def _():
    ax = plt.subplots()[1]
    ax.plot([1, 2, 3])
    return ax

@app.cell
def _():
    ax_plot = plt.gca()  # Fixed!
    ax_plot.hist([1, 2, 3])
    return ax_plot
```

## Safety Features

- **Backup creation** with `--backup` flag
- **Dry run mode** to preview changes
- **Report-only mode** for analysis without changes
- **AST-based parsing** for accurate variable detection
- **Whole-word replacement** to avoid partial matches

## Limitations

- Only detects variable assignments, not dynamic variable creation
- Cannot resolve conflicts in complex cases (eval, exec, etc.)
- Assumes standard marimo cell structure (`@app.cell` + `def _():`)

## Integration

You can run this script as part of your development workflow:

```bash
# Check all notebooks for conflicts
find scripts/notebooks -name "*.py" -exec python scripts/fix_marimo_variables.py {} --report-only \;

# Fix all conflicts with backups  
find scripts/notebooks -name "*.py" -exec python scripts/fix_marimo_variables.py {} --backup \;
```