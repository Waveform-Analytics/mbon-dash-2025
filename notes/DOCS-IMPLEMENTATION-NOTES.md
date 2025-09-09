# Documentation Implementation Notes

## Overview
This document outlines how to implement automated Next.js Nextra documentation for the MBON project using marimo notebooks with auto-exported HTML files.

## Current Setup Status
- ✅ Marimo notebooks configured with `auto_download=["html"]`
- ✅ Auto-exported HTML files generate in `__marimo__/` subdirectories
- ✅ Example: `scripts/notebooks/__marimo__/02_temporal_aggregation.html`

## Architecture Decision
**Chosen Approach**: Next.js Nextra + Static HTML from Marimo Auto-Export
- **Why**: Modern documentation platform, future-proof for dashboard integration, beautiful design
- **Benefits**: React components for interactive elements, excellent performance, unified tech stack
- **Trade-offs**: Slightly more complex setup than MkDocs, but better long-term scalability

## Directory Structure

The following directory structure is not exhaustive, but provides the needed locations for files and assets relating to the Nextra implementation.
```
mbon-dash-2025/
├── docs/                               # Next.js Nextra documentation site
│   ├── package.json                    # Node.js dependencies
│   ├── next.config.js                  # Next.js configuration with Nextra
│   ├── theme.config.tsx                # Nextra theme configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   ├── pages/                          # Documentation pages (file-based routing)
│   │   ├── index.mdx                   # Main landing page
│   │   ├── _app.tsx                    # Custom App component
│   │   ├── _meta.json                  # Page metadata and navigation
│   │   ├── notebooks/                  # Notebook pages
│   │   │   ├── _meta.json             # Notebook section metadata
│   │   │   ├── index.mdx              # Notebook gallery
│   │   │   ├── 01-data-prep.mdx       # Wrapper for marimo HTML
│   │   │   └── 02-temporal-aggregation.mdx
│   │   ├── project-plan.mdx           # Copy from notes/PROJECT-PLAN.md
│   │   └── data-sources.mdx           # Copy from notes/RAW-DATA-DESCRIPTION.md
│   ├── public/                         # Static assets
│   │   ├── notebooks/                  # Processed marimo HTML files
│   │   │   ├── 01-data-prep.html      # From marimo auto-export
│   │   │   └── 02-temporal-aggregation.html
│   │   └── plots/                      # Generated plot images (if needed)
│   └── components/                     # Custom React components
│       ├── NotebookCard.tsx           # Notebook gallery cards
│       ├── NotebookEmbed.tsx          # Marimo HTML embedding
│       └── NotebookGrid.tsx           # Grid layout component
├── python/
│   └── scripts/
│       ├── notebooks/                 # Source notebooks
│       │   ├── __marimo__/           # Auto-exported HTML files
│       │   ├── 01_data_prep.py
│       │   └── 02_temporal_aggregation.py
│       └── build_docs.py             # Build automation script (updated for Nextra)
└── .github/
    └── workflows/
        └── docs.yml                   # GitHub Actions for deployment (updated for Next.js)
```

## Implementation Files

### 1. Next.js Configuration (`docs/next.config.js`)
```javascript
const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
  flexsearch: true,
  codeHighlight: true,
  defaultShowCopyCode: true
});

module.exports = withNextra({
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  basePath: process.env.NODE_ENV === 'production' ? '/mbon-dash-2025' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/mbon-dash-2025' : ''
});
```

### 2. Nextra Theme Configuration (`docs/theme.config.tsx`)
```tsx
import React from 'react';
import { DocsThemeConfig } from 'nextra-theme-docs';

const config: DocsThemeConfig = {
  logo: <span>MBON Data Analysis</span>,
  project: {
    link: 'https://github.com/USERNAME/mbon-dash-2025'
  },
  docsRepositoryBase: 'https://github.com/USERNAME/mbon-dash-2025/tree/main/docs',
  useNextSeoProps() {
    return {
      titleTemplate: '%s – MBON Data Analysis'
    };
  },
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta property="og:title" content="MBON Data Analysis" />
      <meta property="og:description" content="Marine Biodiversity Observatory Network - Data Analysis Documentation" />
    </>
  ),
  footer: {
    text: 'MBON Data Analysis Documentation'
  },
  sidebar: {
    titleComponent({ title, type }) {
      if (type === 'separator') {
        return <div style={{ background: 'currentColor', width: '100%', height: 1 }} />;
      }
      return <>📊 {title}</>;
    }
  }
};

export default config;
```

### 3. Package Configuration (`docs/package.json`)
```json
{
  "name": "mbon-docs",
  "version": "1.0.0",
  "description": "MBON Data Analysis Documentation",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "export": "next build && next export"
  },
  "dependencies": {
    "next": "^14.0.0",
    "nextra": "^2.13.0",
    "nextra-theme-docs": "^2.13.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0"
  }
}
```

### 4. Build Script (`python/scripts/build_docs.py`)
Updated for Nextra - key functions needed:

#### a) Process Marimo Auto-Exports
```python
def process_marimo_exports():
    """
    Find and process marimo auto-exported HTML files
    - Scan notebooks/__marimo__/ directories
    - Copy HTML files to docs/public/notebooks/
    - Rename with consistent naming (e.g., 01_data_prep.html → 01-data-prep.html)
    - Extract metadata from original .py files for indexing
    - Generate MDX wrapper files for each notebook
    """
```

#### b) Generate MDX Wrapper Files
```python
def generate_mdx_wrappers(notebook_metadata):
    """
    Create MDX wrapper files for each notebook:
    - docs/pages/notebooks/01-data-prep.mdx
    - Include NotebookEmbed component with iframe
    - Add frontmatter metadata for Nextra navigation
    - Include description and links to run locally
    """
```

#### c) Update Navigation Metadata
```python
def update_navigation_metadata(notebook_metadata):
    """
    Generate _meta.json files for Nextra navigation:
    - docs/pages/_meta.json (main navigation)
    - docs/pages/notebooks/_meta.json (notebook section)
    - Include titles, descriptions, and ordering
    """
```

#### d) Copy Documentation Files
```python
def copy_documentation():
    """
    Copy and process:
    - notes/PROJECT-PLAN.md → docs/pages/project-plan.mdx
    - notes/RAW-DATA-DESCRIPTION.md → docs/pages/data-sources.mdx
    - Convert markdown to MDX format
    - Add frontmatter metadata
    """
```

### 5. React Components

#### a) Notebook Embed Component (`docs/components/NotebookEmbed.tsx`)
```tsx
interface NotebookEmbedProps {
  src: string;
  title: string;
  height?: string;
}

export function NotebookEmbed({ src, title, height = "800px" }: NotebookEmbedProps) {
  return (
    <div className="my-6">
      <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          📊 Interactive notebook view - <a 
            href={`/notebooks/${src}`} 
            target="_blank" 
            className="underline hover:no-underline"
          >
            Open in new tab
          </a>
        </p>
      </div>
      <iframe
        src={`/notebooks/${src}`}
        title={title}
        className="w-full border rounded-lg shadow-lg"
        style={{ height }}
        loading="lazy"
      />
    </div>
  );
}
```

#### b) Notebook Card Component (`docs/components/NotebookCard.tsx`)
```tsx
interface NotebookCardProps {
  title: string;
  purpose: string;
  keyOutputs: string;
  href: string;
  status?: 'available' | 'coming-soon';
}

export function NotebookCard({ title, purpose, keyOutputs, href, status = 'available' }: NotebookCardProps) {
  return (
    <div className="border rounded-lg p-6 hover:shadow-lg transition-all duration-200 bg-white dark:bg-gray-800">
      <h3 className="text-xl font-semibold mb-3 text-blue-600 dark:text-blue-400">
        <a href={href} className="hover:underline">
          {title}
        </a>
        {status === 'coming-soon' && (
          <span className="ml-2 text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-full">
            Coming Soon
          </span>
        )}
      </h3>
      <p className="mb-2"><strong>Purpose:</strong> {purpose}</p>
      <p className="mb-4"><strong>Key Outputs:</strong> {keyOutputs}</p>
      <a
        href={href}
        className={`inline-block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
          status === 'available'
            ? 'bg-blue-600 text-white hover:bg-blue-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        View Notebook →
      </a>
    </div>
  );
}
```

### 6. GitHub Actions Workflow (`.github/workflows/docs.yml`)
```yaml
name: Deploy Documentation
on:
  push:
    branches: [main]
    paths: 
      - 'python/scripts/notebooks/**'
      - 'docs/**'
      - 'notes/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: 'docs/package-lock.json'
        
    - name: Process notebooks and build docs
      run: |
        # Process marimo notebooks
        cd python/scripts
        pip install beautifulsoup4
        python build_docs.py
        
        # Build Next.js docs
        cd ../../docs
        npm ci
        npm run build
        
    - name: Setup Pages
      uses: actions/configure-pages@v4
      
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
      with:
        path: './docs/out'
        
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

## Content Templates

### Main Index Page (`docs/pages/index.mdx`)
```mdx
---
title: MBON Data Analysis Dashboard
description: Marine Biodiversity Observatory Network - Data Analysis Documentation
---

# MBON Data Analysis Dashboard

Marine Biodiversity Observatory Network - Data analysis and visualization.

## Quick Navigation

- **[Analysis Notebooks](notebooks)** - Interactive data processing and visualization
- **[Project Plan](project-plan)** - Detailed methodology and approach
- **[Data Sources](data-sources)** - Raw data descriptions and formats

## Project Overview

This project analyzes marine biodiversity data from acoustic monitoring stations, focusing on:

- **Acoustic indices analysis** - Temporal patterns and ecological indicators
- **Fish detection patterns** - Manual detection data processing and analysis  
- **Environmental correlations** - Temperature, depth, and SPL relationships
- **Temporal aggregation** - Multi-resolution time series analysis

## Data Processing Pipeline

1. **Data Preparation** - Load and quality-assess all data streams
2. **Temporal Aggregation** - Align data to common time resolution
3. **Analysis & Visualization** - Generate insights and interactive plots

## Technology Stack

- **[Marimo](https://marimo.io/)** - Reactive Python notebooks
- **[Pandas](https://pandas.pydata.org/)** - Data analysis and manipulation  
- **[Matplotlib/Seaborn](https://matplotlib.org/)** - Statistical visualization
- **[Next.js Nextra](https://nextra.site/)** - Modern documentation framework
```

### Notebook Index Template (`docs/pages/notebooks/index.mdx`)
```mdx
---
title: Analysis Notebooks
description: Interactive data analysis notebooks with static outputs
---

import { NotebookCard } from '../../components/NotebookCard';

# Analysis Notebooks

Interactive data analysis notebooks with static outputs. Each notebook processes different aspects of the MBON dataset.

## Available Notebooks

<div className="grid grid-cols-1 md:grid-cols-2 gap-6 my-8">
  <NotebookCard
    title="Data Loading and Initial Exploration"
    purpose="Load all data streams and perform initial quality assessment"
    keyOutputs="Raw data summaries, temporal coverage plots, missing data visualization"
    href="/notebooks/01-data-prep"
    status="available"
  />
  <NotebookCard
    title="Temporal Aggregation"
    purpose="Align all data streams to common temporal resolution"
    keyOutputs="Synchronized datasets, coverage analysis"
    href="/notebooks/02-temporal-aggregation"
    status="available"
  />
  <NotebookCard
    title="Acoustic Index Reduction"
    purpose="Dimensionality reduction of 60+ acoustic indices"
    keyOutputs="Reduced feature set, correlation analysis, PCA results"
    href="/notebooks/03-acoustic-index-reduction"
    status="coming-soon"
  />
</div>

## Running Notebooks Locally

To run these notebooks interactively with live data:

```bash
cd python/scripts
marimo edit notebooks/01_data_prep.py
```

## Data Requirements

All notebooks expect data to be available in `python/data/raw/` following the structure described in [Data Sources](../data-sources).
```

## Implementation Workflow

### Phase 1: Nextra Setup
1. Create `docs/` directory and initialize Next.js project
2. Install Nextra and dependencies (`npm install nextra nextra-theme-docs next react react-dom`)
3. Create `next.config.js` and `theme.config.tsx`
4. Set up basic page structure with `pages/index.mdx`
5. Test locally with `npm run dev`

### Phase 2: Marimo Integration
1. Update `build_docs.py` script for Nextra structure
2. Implement marimo HTML processing to `public/notebooks/`
3. Create MDX wrapper files for each notebook
4. Generate navigation metadata (`_meta.json` files)
5. Build React components for notebook embedding

### Phase 3: Content & Automation
1. Create React components for notebook cards and embedding
2. Generate dynamic notebook gallery with metadata
3. Copy and convert documentation files to MDX
4. Set up GitHub Actions for automated deployment
5. Configure GitHub Pages

### Phase 4: Enhanced Features (Optional)
1. Add interactive components for data exploration
2. Implement notebook preview thumbnails
3. Add download links for data and notebooks  
4. Create dashboard integration hooks
5. Add search and filtering capabilities

## Key Considerations

### Metadata Extraction Strategy (Unchanged)
- Parse marimo `.py` files using AST
- Look for first `mo.md()` call with markdown content
- Extract title from `# Header` pattern
- Extract purpose from `**Purpose**: text` pattern
- Extract outputs from `**Key Outputs**: text` pattern

### File Naming Conventions (Updated for Nextra)
- Source notebooks: `01_data_prep.py` (underscores)
- Static HTML files: `public/notebooks/01-data-prep.html` 
- MDX pages: `pages/notebooks/01-data-prep.mdx`
- Navigation: `pages/notebooks/_meta.json`
- Consistent numbering for ordered workflows

### Performance Considerations (Enhanced for Next.js)
- Marimo HTML files served as static assets in `public/`
- Iframe embedding with lazy loading by default
- Next.js image optimization and static generation
- Tailwind CSS for optimized styling
- Component-level code splitting

### Maintenance & Development
- Build script targets Nextra structure
- Hot reloading during development (`npm run dev`)
- TypeScript support for components and configuration
- Automated deployment with Next.js static export
- Error boundaries for robust notebook embedding

## GitHub Repository Settings (Unchanged)

### Enable GitHub Pages
1. Go to Settings > Pages
2. Source: GitHub Actions
3. No custom domain needed
4. Site will be available at: `https://USERNAME.github.io/mbon-dash-2025/`

### Required Permissions (Same)
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

## Deployment URL
Once set up, documentation will be available at:
`https://USERNAME.github.io/mbon-dash-2025/`

Replace `USERNAME` with your GitHub username.

## Local Development Commands

### Start the development server:
```bash
cd docs
npm run dev
```

### Build for production:
```bash
cd docs
npm run build
```

### Process notebooks and build:
```bash
cd python/scripts
python build_docs.py
cd ../../docs  
npm run build
```

## Migration Benefits

### Advantages over MkDocs:
- **Future-proof**: Same tech stack as planned dashboard
- **Better performance**: Next.js static generation and optimization
- **Interactive components**: React components for enhanced UX
- **Modern design**: Beautiful Nextra theme with dark mode
- **Developer experience**: Hot reloading, TypeScript support
- **Extensibility**: Easy to add custom functionality

### Maintained Features:
- **Marimo integration**: Same notebook processing workflow
- **GitHub Actions**: Automated deployment pipeline
- **Metadata extraction**: Same AST parsing approach
- **Static hosting**: Works with GitHub Pages
- **Search functionality**: Built-in with Nextra