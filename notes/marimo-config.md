# Marimo Check Configuration

This document describes how `marimo check` is configured for this project to automatically detect and fix common issues in AI-generated marimo notebooks.

## What marimo check detects

Based on the latest release, `marimo check` can detect:

- **Multiple definitions**: Variables defined in multiple cells (critical for marimo's reactive model)
- **Circular dependencies**: Cells that depend on each other cyclically
- **Syntax errors**: Python syntax issues
- **Empty cells**: Cells that contain only whitespace, comments, or pass statements
- **Formatting issues**: Code style and structure problems
- **Best practice violations**: Issues that violate marimo's reactive programming model

## Available Commands

### Basic Usage
```bash
# Check a single notebook (reports issues)
uv run marimo check notebook.py

# Check and automatically fix issues
uv run marimo check --fix notebook.py

# Check with detailed output
uv run marimo check --verbose notebook.py

# Check with strict mode (warnings cause non-zero exit codes)
uv run marimo check --strict notebook.py

# Enable unsafe fixes (like removing empty cells)
uv run marimo check --fix --unsafe-fixes notebook.py
```

### Helper Functions (source marimo-helpers.sh)
```bash
# Load the helper functions
source marimo-helpers.sh

# Check a single notebook
check_marimo scripts/notebooks/01_data_prep.py

# Check all marimo notebooks in project
check_all_marimo

# Check notebooks modified in last 30 minutes
check_recent_marimo 30

# Watch for changes and auto-check
watch_marimo python/scripts/notebooks/

# AI workflow: check existing notebook and open editor
ai_marimo new_notebook.py
```

## Integration Setups

### 1. Git Pre-commit Hook
- **Location**: `.git/hooks/pre-commit`
- **Purpose**: Automatically checks and fixes marimo notebooks before commits
- **Behavior**: 
  - Runs on all staged `.py` files that appear to be marimo notebooks
  - Auto-fixes issues and re-stages files
  - Reports if issues were found and fixed

### 2. VS Code Task Integration
Add this task to your `.vscode/tasks.json`:

```json
{
    "label": "Check Marimo Notebook",
    "type": "shell",
    "command": "python",
    "args": ["${workspaceFolder}/editor-marimo-check.py", "${file}"],
    "group": "build",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "panel": "new"
    },
    "problemMatcher": []
}
```

Then bind it to a keyboard shortcut in `keybindings.json`:
```json
{
    "key": "cmd+shift+m",
    "command": "workbench.action.tasks.runTask",
    "args": "Check Marimo Notebook",
    "when": "editorFocus && resourceExtname == '.py'"
}
```

### 3. AI Coding Agent Integration

For AI agents like Claude or Cursor, you can configure automatic checking by:

#### Option A: Include in AI prompts
Add this instruction to your AI coding prompts:
```
After generating or modifying marimo notebook code, automatically run:
`uv run marimo check --fix <notebook_file>`
```

#### Option B: Workflow automation
Use the provided `editor-marimo-check.py` script in your AI agent's workflow:
```bash
# After AI generates/modifies a notebook
python editor-marimo-check.py path/to/notebook.py
```

### 4. CI/CD Integration

For GitHub Actions or other CI systems:

```yaml
- name: Check Marimo Notebooks
  run: |
    find . -name "*.py" -type f | while read file; do
      if grep -q "@app.cell" "$file"; then
        echo "Checking $file"
        uv run marimo check --strict "$file"
      fi
    done
```

## Best Practices

1. **Always use `--fix`** in development workflows to automatically resolve fixable issues
2. **Use `--strict`** in CI/CD to ensure high code quality
3. **Run checks before committing** to catch issues early
4. **Watch for variable naming conflicts** - marimo's reactive model requires unique variable names across cells
5. **Remove empty cells** - they add no value and create clutter

## Common Issues and Fixes

### Variable Name Conflicts
```python
# ❌ Bad: Same variable name in multiple cells
@app.cell
def _():
    df = load_data()
    return df,

@app.cell
def _():
    df = process_data()  # Conflict!
    return df,

# ✅ Good: Unique descriptive names
@app.cell
def _():
    df_raw = load_data()
    return df_raw,

@app.cell
def _(df_raw):
    df_processed = process_data(df_raw)
    return df_processed,
```

### Path Resolution Issues
Always use the standardized path resolution pattern from the project rules:
```python
@app.cell
def _():
    from pathlib import Path
    
    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent
    
    DATA_ROOT = project_root / "data"
    return DATA_ROOT,
```

## Troubleshooting

### Command not found: marimo
This project has its Python environment in the `python/` subdirectory. Make sure you're using the correct command:

```bash
# ❌ Wrong: marimo not found
marimo check notebook.py

# ❌ Wrong: uses wrong project
uv run marimo check notebook.py

# ✅ Correct: uses python subdirectory project
uv run --project python marimo check notebook.py

# ✅ Alternative: change to python directory first
cd python && uv run marimo check ../notebook.py
```

The pre-commit hook and helper scripts handle this automatically.

### No issues detected but notebook has problems
Try running with `--verbose` to see more detailed analysis:
```bash
uv run marimo check --verbose --fix notebook.py
```

### Files not being detected as marimo notebooks
The detection looks for `@app.cell` in the file content. Make sure your notebook has the proper marimo cell structure.