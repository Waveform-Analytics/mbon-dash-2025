Please refer to the following project planning files as needed:

notes/PROJECT-PLAN.md -- this is the big picture plan, which describes in detail how we can build upon previous work. 

notes/MVP-PLAN.md -- this is the minimum viable product plan, which describes in detail what we need to build to get the MVP up and running. We will start with this but it will be good to have an awareness of the main project plan, even if it is not fully implemented yet. 

notes/RAW-DATA-DESCRIPTION.md -- this describes all the raw data that we have access to at this time. All raw data are stored in data/raw/ with specifics on content and format included in this description file. 

notes/SITE-IMPLEMENTATION-NOTES.md -- this describes the site implementation plan - how it's laid out, styling, navigation, etc. 

notes/DATA-FILE-NAMING.md -- this describes the naming conventions for data files, and also provides details on every file that is saved by every python marimo notebook. This is a good reference for finding the data we need for any given task (or determining that we need to generate new data)

# Extra notes for claude code
- don't write code or run anything unless I specifically say to do so. I like to discuss things first.
- use uv for python dependency management
-  when adding new features like CDN support, it's better to implement them in the data layer (which we did successfully) rather than rewriting working UI components.
- Python debugging scripts should go in the python/scripts folder

# setup / layout
- the heavy lifting in terms of analysis and data prep is all done in python - and is contained within the python folder.
- the site is build using nextjs and is contained with the dashboard folder.

# Marimo Notebook Standards

## Path Resolution
**IMPORTANT**: All marimo notebooks must use standardized path resolution to work regardless of where they are launched from.

**Standard Pattern**: Every marimo notebook must include this exact pattern in its imports cell:
```python
@app.cell
def _():
    import pandas as pd
    import numpy as np
    # ... other imports ...
    from pathlib import Path

    # Find project root by looking for the data folder
    current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
    project_root = current_dir
    while not (project_root / "data").exists() and project_root != project_root.parent:
        project_root = project_root.parent

    DATA_ROOT = project_root / "data"

    return pd, DATA_ROOT  # Always return DATA_ROOT
```

**File Path Usage**: Always use `DATA_ROOT` for file paths:
- ✅ Correct: `pd.read_parquet(DATA_ROOT / "processed/file.parquet")`
- ❌ Wrong: `pd.read_parquet("../data/processed/file.parquet")`
- ❌ Wrong: `pd.read_parquet("../../data/processed/file.parquet")`

**Function Signatures**: Include `DATA_ROOT` in all cell function signatures that read files:
- ✅ Correct: `def _(pd, DATA_ROOT):`
- ❌ Wrong: `def _(pd):`

This pattern ensures notebooks work when run:
- From marimo UI launched from any directory
- As scripts from any directory
- From different development environments

