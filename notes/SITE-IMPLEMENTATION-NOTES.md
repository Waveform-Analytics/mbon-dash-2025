Building a nextjs site as an interactive dashboard plus scientific descriptions and methodological overview. Will be shared on Vercel. 

## Project Organization
- **Site Location**: All Next.js code lives in `/dashboard` folder
- **Python Analysis**: Separate `/python` folder contains marimo notebooks and data prep
- **Style Reference**: `/style-bundle` folder contains design system reference (not used directly)
- **Data**: `/data` folder contains raw data and metadata

## Tech Stack
- **Framework**: Next.js with TypeScript (App Router)
- **Styling**: Tailwind CSS (configured to match teal theme from style-bundle)
- **Icons**: Lucide React
- **Visualizations**: D3.js for all plots and charts
- **Maps**: Mapbox GL JS (token in .env.local)
- **Routing**: Nested routes to support sub-pages in each section

## Site Structure

### Landing page (/)
- hero image at the top that's a photograph, with an overlay that matches the overall style (so, teal) - yohan-marion-daufuskie-unsplash.jpg <- that's the image i want to use. 
- Map showing the stations of interest - use mapbox, I already have a token in env.local. Station locations are in the raw data metadata folder 
- Very brief description of the project, including intro to the ESONS project (i'll fill in more later)

### Data (/data)
- A stacked view with three panels (day along x axis, hour of day on y axis) - top panel shows heatmap of manual detections, middle shows acoustic indices, bottom shows rms spl. Users should be able to use drop down selectors for each. manual detections - choose species. acoustic indices - choose index. rms spl - choose bandwidth.
- Environmental data plots - probably time series summaries.
- **Potential sub-pages**: /data/acoustic, /data/environmental, etc.

### Analysis (/analysis)
- This section will be basically for the marimo notebooks. Again: placeholder for now.
- **Will have sub-pages**: Each notebook/analysis as its own sub-page (e.g., /analysis/temporal-patterns, /analysis/species-diversity, etc.)

### Explore (/explore)
- this will eventually be split up into sections to look at different aspects of the work but for now will just be a placeholder.
- **Potential sub-pages**: Different exploration tools/views

### Background (/background)
- this page will be where the ESONS folks can more fully describe previous work, including citations as needed. For now just a placeholder.
- **Potential sub-pages**: /background/methods, /background/publications, etc.

---

## Navigation

### Nav bar
- semi transparent so you can see through it a bit when you scroll
- Persistent across all pages
- Will include dropdown menus for sections with sub-pages

## Styling

- All styling information can be found in a folder, "style-bundle", which is at the repo root. It contains examples and definitions and patterns to use as a reference when building this site. It also contains the image I want in that main landing page hero header. 

