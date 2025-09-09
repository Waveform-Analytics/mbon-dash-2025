Please refer to the following project planning files:

notes/PROJECT-PLAN.md -- this is the big picture plan, which describes in detail how we can build upon previous work. 

notes/MVP-PLAN.md -- this is the minimum viable product plan, which describes in detail what we need to build to get the MVP up and running. We will start with this but it will be good to have an awareness of the main project plan, even if it is not fully implemented yet. 

notes/RAW-DATA-DESCRIPTION.md -- this describes all the raw data that we have access to at this time. All raw data are stored in data/raw/ with specifics on content and format included in this description file. 

# Extra notes for claude code
- don't write code or run anything unless I specifically say to do so. I like to discuss things first.
- use uv for python dependency management


# Special marimo notebook rules
- **Marimo Variable Conflict Rules**: Marimo notebooks are reactive - ALL variables are globally scoped across the entire notebook. Never define the same variable name in multiple cells or there will be conflicts.

  **Common Conflict Patterns to Avoid:**
  - Loop variables: `for station in STATIONS` → Use unique names like `station_idx`, `station_det`, `station_temp`
  - DataFrame variables: `df = pd.read_csv()` → Use unique names like `df_idx`, `df_det`, `df_temp` 
  - File path variables: `file_path = ...` → Use unique names like `file_path_idx`, `file_path_det`
  - Temporary variables: `summary = {}` → Use unique names like `data_summary`, `stats_summary`
  - Plot variables: `fig, axes = plt.subplots()` → Use unique names like `fig_temporal`, `axes_temporal`

  **Naming Strategy:**
  - Add descriptive suffixes: `_idx` (indices), `_det` (detection), `_temp` (temperature), `_spl` (SPL), `_stats` (statistics)
  - Use descriptive prefixes: `temporal_`, `coverage_`, `summary_` 
  - Make all variables semantically unique across the entire notebook

  **Return Statement Rules:**
  - Each cell must return ALL variables it creates: `return (var1, var2, var3)`
  - Single variable: `return (variable,)` (note the comma for tuple)
  - No variables: `return` (empty return)

  **Before writing any marimo notebook, scan for these common conflicts and use unique names from the start.**