Please refer to the following project planning files:

notes/PROJECT-PLAN.md -- this is the big picture plan, which describes in detail how we can build upon previous work. 

notes/MVP-PLAN.md -- this is the minimum viable product plan, which describes in detail what we need to build to get the MVP up and running. We will start with this but it will be good to have an awareness of the main project plan, even if it is not fully implemented yet. 

notes/RAW-DATA-DESCRIPTION.md -- this describes all the raw data that we have access to at this time. All raw data are stored in data/raw/ with specifics on content and format included in this description file. 

notes/SITE-IMPLEMENTATION-NOTES.md -- this describes the site implementation plan - how it's laid out, styling, navigation, etc. 

# Extra notes for claude code
- don't write code or run anything unless I specifically say to do so. I like to discuss things first.
- use uv for python dependency management

# setup / layout
- the heavy lifting in terms of analysis and data prep is all done in python - and is contained within the python folder. 
- the site is build using nextjs and is contained with the dashboard folder.

# Special marimo notebook rules

## Variable Conflict Rules
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

## Markdown Documentation Style for Notebooks
- **Target audience**: Intelligent readers (stats people, biologists) who haven't been immersed in this specific data process
- **Tone**: Direct, plainspoken, respectful - avoid jargon but don't talk down to people  
- **Goal**: Enable quick understanding when returning to notebooks months/years later

  **Section Structure:**
  - **Introduction**: Provide context about data sources, collection methods, and why different streams are combined
  - **Before each major section**: 2-3 sentences explaining what the data represents and why it matters
  - **Before analyses**: Brief explanation of what the analysis accomplishes and why it's useful
  - **After key results**: Practical interpretation guidance (what patterns to look for, what results mean)

  **Writing Guidelines:**
  - Focus on "why" not just "what" - explain the purpose behind each step
  - Define technical terms in context (e.g., "SPL (Sound Pressure Level) measurements quantify...")
  - Use bullet points and clear formatting for readability
  - Add result interpretation with → arrows for key takeaways
  - Keep explanations concise but complete - assume intelligence, provide necessary context