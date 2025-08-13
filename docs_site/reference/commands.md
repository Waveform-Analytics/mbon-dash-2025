# Command Reference

All available commands for data processing, analysis, and dashboard operations.

## Quick Reference

| Task | Command | Purpose |
|------|---------|---------|
| **Download data** | `npm run download-data` | Get raw data from CDN |
| **Process data** | `npm run process-data` | Excel → JSON for dashboard |
| **Validate** | `npm run validate-data` | Check data quality |
| **Statistics** | `npm run data-stats` | View data summary |
| **Dashboard** | `npm run dev` | Start interactive dashboard |

## Data Processing

### Core Workflow

```bash
# 1. Download raw data from CDN
npm run download-data

# 2. Process Excel files to JSON
npm run process-data

# 3. Validate results
npm run validate-data

# 4. View statistics
npm run data-stats
```

### Individual Commands

#### `npm run download-data`
Downloads raw Excel files from CDN to `data/cdn/raw-data/`
- Detection files (6 Excel files)
- Environmental data (12 Excel files)
- Deployment metadata (1 Excel file)

#### `npm run process-data`
Transforms raw Excel → dashboard JSON in `data/cdn/processed/`
- Creates: detections.json, environmental.json, stations.json, species.json
- Output: 26,280 detection records, 237,334 environmental records

#### `npm run validate-data`
Checks data integrity and completeness
- Verifies all required files exist
- Validates JSON structure
- Reports missing fields

#### `npm run data-stats`
Generates comprehensive data summary
- Record counts by station/year
- Species detection frequencies
- File sizes and data quality

#### `npm run check-freshness`
Checks if data needs reprocessing based on file timestamps

## Dashboard Operations

### Development

```bash
# Start development server
npm run dev                 # http://localhost:3000

# Process data + start server
npm run dev:fresh

# Clean build + start
npm run dev:clean
```

### Production

```bash
# Build for production
npm run build

# Start production server
npm run start
```

### Code Quality

```bash
# TypeScript checking
npm run type-check

# ESLint validation
npm run lint
```

## Data Analysis (Python)

### Direct Python Scripts

```bash
# Run any script directly
uv run scripts/exploratory/your_analysis.py

# Dashboard data preparation
uv run scripts/dashboard_prep/process_excel_to_json.py

# Utilities
uv run scripts/utils/validate_data.py
uv run scripts/utils/data_statistics.py
```

### Working with Data

```python
# Load processed data in Python
import pandas as pd
import json

with open('data/cdn/processed/detections.json') as f:
    detections = pd.DataFrame(json.load(f))

# Your analysis here
detections.groupby('station').size()
```

## Documentation

```bash
# Serve documentation locally
uv run mkdocs serve         # http://localhost:8000

# Build documentation
uv run mkdocs build
```

## Environment Management

### Python (uv)

```bash
# Install/update dependencies
uv sync

# Add new package
uv add pandas

# Check environment
uv run python --version
```

### Node.js

```bash
# Install dependencies
npm install

# Add new package
npm install package-name

# Update all packages
npm update
```

## Troubleshooting

### Data Issues

```bash
# If data is missing
npm run download-data
npm run process-data

# If validation fails
npm run validate-data
# Check error messages for specific issues
```

### Environment Issues

```bash
# Reset Python environment
uv sync --reinstall

# Reset Node modules
rm -rf node_modules
npm install
```

### Clean Slate

```bash
# Remove all generated data
rm -rf data/

# Rebuild everything
npm run download-data
npm run process-data
npm run dev
```

## File Locations

| Data Type | Location |
|-----------|----------|
| Raw data | `data/cdn/raw-data/` |
| Processed JSON | `data/cdn/processed/` |
| Analysis results | `data/intermediate_results/` |
| Scripts | `scripts/` |
| Dashboard | `src/` |

## Common Workflows

### New Analysis

```bash
# 1. Create script in exploratory folder
touch scripts/exploratory/my_analysis.py

# 2. Run your analysis
uv run scripts/exploratory/my_analysis.py

# 3. Save results
# Output to data/intermediate_results/
```

### Update Dashboard Data

```bash
# 1. Get latest raw data
npm run download-data

# 2. Process for dashboard
npm run process-data

# 3. Upload to CDN (manual)
# Copy data/cdn/processed/* to CDN
```

### Development Cycle

```bash
# 1. Process data
npm run process-data

# 2. Start dashboard
npm run dev

# 3. Make changes (hot reload)
# 4. View at http://localhost:3000
```