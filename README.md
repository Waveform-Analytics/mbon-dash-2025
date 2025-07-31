# MBON Marine Biodiversity Dashboard

Interactive web dashboard for exploring marine acoustic monitoring data from the OSA MBON project (2018-2021).

## Quick Start

1. **Install dependencies**
   ```bash
   uv sync          # Python dependencies
   npm install      # Node.js dependencies
   ```

2. **Process data** (first time only)
   ```bash
   npm run build-data
   ```

3. **Configure Cloudflare R2** (see [docs/CLOUDFLARE_R2_SETUP.md](docs/CLOUDFLARE_R2_SETUP.md))
   ```bash
   cp .env.local.example .env.local
   # Edit with your R2 URL
   ```

4. **Start development**
   ```bash
   npm run dev
   ```

## Documentation

- [Dashboard Plan](docs/dashboard_plan.md) - Original project specification
- [Cloudflare R2 Setup](docs/CLOUDFLARE_R2_SETUP.md) - CDN configuration guide
- [CLAUDE.md](CLAUDE.md) - Detailed development documentation

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Visualization**: Plotly.js, Mapbox GL
- **Data Processing**: Python (pandas, numpy)
- **CDN**: Cloudflare R2

## Data Overview

- **61,067** detection records
- **10** monitoring stations
- **28** species tracked
- **2** years of data (2018, 2021)