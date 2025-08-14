# For Developers

## Architecture

### Tech Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Visualization**: Observable Plot, Mapbox GL JS
- **Data Processing**: Python with uv, pandas, numpy
- **State**: Zustand
- **Deployment**: Vercel + Cloudflare R2 CDN

### Project Structure
```
mbon-dash-2025/
├── src/                    # Next.js web app
│   ├── app/               # Pages (Next.js 14 app router)
│   ├── components/        # React components
│   ├── lib/hooks/         # Data loading (useData.ts)
│   └── store/             # Zustand state
├── scripts/               # Python data processing
│   ├── dashboard_prep/    # Core data pipeline
│   └── exploratory/       # Analysis scripts
├── mbon_analysis/         # Python analysis package
└── data/                  # Raw data (gitignored)
```

## Development Workflow

### Setup
```bash
# Install dependencies
uv sync      # Python
npm install  # Node.js

# Environment variables
cp .env.example .env.local
```

### Data Pipeline
```bash
# Process Excel → JSON
uv run scripts/dashboard_prep/process_excel_to_json.py

# Or via npm
npm run process-data
```

### Development Server
```bash
npm run dev:fresh   # Process data + start server
npm run dev         # Start server only
```

## Content Helper Pattern

**Required**: All pages must separate content from code.

### Implementation
```typescript
// page.content.tsx - Text only
export const PageContent = {
  title: "Page Title",
  description: "Page description"
}

// page.tsx - Code only
import { PageContent } from './page.content';

export default function Page() {
  return <h1>{PageContent.title}</h1>;
}
```

### Rules
- No user-facing text in `.tsx` files
- Simple object structure in `.content.tsx`
- Clear editing comments for non-programmers

## Data Loading

All data access through `src/lib/hooks/useData.ts`:

```typescript
import { useMetadata, useStations, useCoreData } from '@/lib/hooks/useData';

function Component() {
  const { data: metadata } = useMetadata();
  const { data: stations } = useStations(); 
  const { detections, environmental } = useCoreData();
}
```

## Python Package

The `mbon_analysis` subpackage provides reusable utilities:

```python
from mbon_analysis.core import data_loader
from mbon_analysis.analysis import biodiversity
from mbon_analysis.visualization import plots

# Example usage in scripts
data = data_loader.load_processed_json()
patterns = biodiversity.analyze_temporal_patterns(data)
plots.create_activity_heatmap(patterns)
```

## Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Production build
npm run lint             # ESLint check
npm run type-check       # TypeScript check

# Data Processing
npm run process-data     # Excel → JSON
npm run validate-data    # Data quality checks
npm run data-stats       # View summaries

# Python Analysis
uv run scripts/exploratory/step01_explore_data_for_dashboard.py
```

## Deployment

1. **Data Processing**: Local only (`npm run process-data`)
2. **Upload to CDN**: Manual upload of JSON files to Cloudflare R2
3. **Frontend Deploy**: Vercel automatically builds from GitHub

**Note**: No Python processing during deployment - data served from CDN.

## Contributing

1. Follow content helper pattern for all pages
2. Use TypeScript with strict mode
3. Test data processing after changes
4. Update CLAUDE.md if workflow changes