# MBON Marine Biodiversity Dashboard

## Research Question
Can acoustic indices predict marine biodiversity patterns as an alternative to manual species detection?

## Project Overview
Interactive dashboard analyzing 56+ acoustic indices against species detections from 3 monitoring stations in May River, South Carolina (2018 & 2021 data).

### Key Goals
- Reduce 56 acoustic indices to 3-5 "super indices" via PCA
- Identify which indices best predict species detection patterns
- Develop automated alternatives to manual annotation
- Understand environmental confounding factors

### Dataset
- **26,280** manual species annotations
- **237,334** environmental measurements (temperature, depth)
- **3** stations (9M, 14M, 37M)
- **56** acoustic indices per hour
- **2** years of data (2018, 2021)

## Quick Start

### Installation
```bash
# Clone repository
git clone [repository-url]
cd mbon-dash-2025

# Install dependencies
uv sync          # Python analysis
npm install      # Web dashboard
```

### Basic Workflow
```bash
# Process data
npm run process-data

# Start dashboard
npm run dev      # http://localhost:3000
```

## Documentation

### [For Scientists](scientists.md)
Data analysis workflow, research methods, and acoustic indices guide.

### [For Developers](developers.md)
Technical architecture, code structure, and contribution guide.

### [Data Structure](data.md)
Dataset organization, file formats, and processing pipeline.

## Project Status
Active development focusing on acoustic indices integration and PCA analysis for biodiversity prediction.