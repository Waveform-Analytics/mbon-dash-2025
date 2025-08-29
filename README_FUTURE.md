# Marine Biodiversity Dashboard (MBON-USC-2025)

Interactive web dashboard exploring whether acoustic indices can predict marine soundscape biodiversity and serve as proxies for complex biodiversity monitoring.

🔬 **Research Question**: "Can computed acoustic indices help us understand and predict marine biodiversity patterns as an alternative to labor-intensive manual species detection methods?"

🎯 **Key Goals**: Identify which acoustic indices best predict species detection patterns, reduce 56+ indices to "super indices" via PCA, and develop automated alternatives to manual annotation.

## 🌊 Live Dashboard
- **Production**: [Your deployed URL]
- **Data Source**: Cloudflare R2 CDN (direct access)
- **Study Area**: May River, South Carolina (Stations 9M, 14M, 37M)
- **Time Period**: 2018, 2021

## 📊 Dashboard Features

### Current Pages
- **Overview** (`/`) - Project introduction and research context
- **Analysis:**
  - **Acoustic Indices** (`/acoustic-biodiversity`) - PCA analysis, index rankings, biodiversity correlations
  - **Environmental Factors** (`/environmental-factors`) - Temperature/depth effects on acoustic patterns
- **Resources:**
  - **Index Guide** (`/acoustic-glossary`) - Educational content about acoustic indices
  - **Station Profiles** (`/stations`) - Study sites and spatial context
- **Explore:**
  - **Species Annotations** (`/explore/annotations`) - Manual detection timelines and patterns
  - **Acoustic Indices** (`/explore/indices`) - Index distributions and quality analysis

### Performance Optimizations
Our view-based architecture delivers lightning-fast loading:
- **Acoustic Summary**: 19.6KB (was 166MB) - 8,686x improvement
- **Species Timeline**: 1.6KB (was MB+) - 1000x+ improvement  
- **Index Distributions**: 119KB (was 2.8MB) - 23x improvement

## 🚀 Quick Start

### For Scientists & Researchers

```bash
# View the dashboard
open https://your-dashboard-url.com

# Download processed data for analysis
curl https://your-cdn-url.com/views/acoustic_summary.json
curl https://your-cdn-url.com/processed/detections.json
```

### For Developers

```bash
# Setup
git clone https://github.com/your-org/mbon-dash-2025
cd mbon-dash-2025
npm install
uv sync

# Run dashboard locally
npm run dev

# Process new data (if you have raw Excel files)
npm run pipeline
```

## 📁 Project Structure

```
mbon-dash-2025/
├── scripts/                          # Clean 3-step data pipeline
│   ├── 1_process_excel_to_json.py    # Excel → Core JSON
│   ├── 2_generate_all_views.py       # JSON → Optimized Views
│   └── 3_upload_to_cdn.py            # Upload to CDN
├── mbon_analysis/                     # Python package for data processing
│   ├── processing/                    # Core processing logic
│   └── views/                         # Individual view generators (extensible)
├── src/                              # Next.js dashboard
│   ├── app/                          # Page routes
│   ├── components/                   # Reusable UI components
│   ├── lib/hooks/                    # Data loading hooks
│   └── types/                        # TypeScript definitions
├── data/cdn/
│   ├── raw-data/                     # Source Excel files
│   ├── processed/                    # Core JSON files (6 files)
│   └── views/                        # Optimized view files (5 files)
└── public/                           # Static assets
```

## 🛠️ Data Pipeline

### Simple 3-Step Process

```bash
# Step 1: Convert Excel files to JSON
npm run process-data
# → Reads Excel from data/cdn/raw-data/
# → Outputs to data/cdn/processed/

# Step 2: Generate optimized views
npm run generate-views  
# → Reads from data/cdn/processed/
# → Outputs to data/cdn/views/

# Step 3: Upload to CDN
npm run upload-cdn
# → Uploads views/ to Cloudflare R2
# → Dashboard loads from CDN

# All-in-one pipeline
npm run pipeline
```

### Data Flow
```
Raw Excel Files → Core JSON → Optimized Views → CDN → Dashboard
   (200MB+)        (50MB)      (1MB total)    (CDN)  (Fast!)
```

## 📈 Adding New Views (For Developers)

Our extensible architecture makes adding new visualizations simple:

### 1. Create View Generator
```python
# mbon_analysis/views/my_new_views.py
def generate_my_analysis_view(processed_data_dir):
    """Generate data for my new analysis."""
    # Load core data
    detections = pd.read_json(processed_data_dir / 'detections.json')
    
    # Process into view format
    view_data = {
        "analysis_results": [...],
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "description": "My new analysis view",
            "total_records": len(detections)
        }
    }
    
    return view_data
```

### 2. Add TypeScript Types
```typescript
// src/types/data.ts
export interface MyAnalysisViewData {
  analysis_results: MyResult[];
  metadata: ViewMetadata;
}

// Update ViewDataMap
type ViewDataMap = {
  'my-analysis': MyAnalysisViewData;
  // ... existing views
};
```

### 3. Add Data Hook
```typescript
// src/lib/hooks/useViewData.ts
export function useMyAnalysis() {
  return useViewData('my-analysis');
}
```

### 4. Create Dashboard Page
```typescript
// src/app/my-analysis/page.tsx
import { useMyAnalysis } from '@/lib/hooks/useViewData';

export default function MyAnalysisPage() {
  const { data, loading, error } = useMyAnalysis();
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      <h1>My Analysis</h1>
      {/* Your visualization components */}
    </div>
  );
}
```

### 5. Regenerate Views
```bash
npm run generate-views  # Auto-discovers your new view generator
npm run upload-cdn      # Makes it available to dashboard
```

## 🔬 Adding New Stations

The system automatically detects new stations from Excel filenames:

```bash
# Add new Excel files with station in filename:
data/cdn/raw-data/2024/Master_Manual_42M_2h_2024.xlsx  # → Station "42M"
data/cdn/raw-data/2024/Master_Manual_55M_2h_2024.xlsx  # → Station "55M"

# Process normally - no code changes needed
npm run pipeline
```

## 🎨 Dashboard Technology

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom ocean theme
- **Visualization**: Observable Plot (primary), Mapbox GL JS
- **State**: Zustand for client state
- **Data Loading**: Custom React hooks with loading states
- **Deployment**: Vercel (frontend) + Cloudflare R2 (data)

## 📊 Data Sources

### Raw Data Structure
```
data/cdn/raw-data/
├── 2018/                           # First study year
│   ├── Master_Manual_9M_2h_2018.xlsx    # Species detections
│   ├── Master_9M_Temp_2018.xlsx         # Temperature data  
│   ├── Master_9M_Depth_2018.xlsx        # Depth measurements
│   └── [14M, 37M files...]
├── 2021/                           # Second study year  
│   └── [same structure]
├── indices/                        # Acoustic indices from collaborators
│   ├── Acoustic_Indices_9M_2021_FullBW_v2_Final.csv
│   ├── Acoustic_Indices_9M_2021_8kHz_v2_Final.csv
│   └── [14M indices...]
├── det_column_names.csv           # Species/sound classifications
└── Updated_Index_Categories_v2.csv # Index category definitions
```

### Processed Data Files (11 total)
```
data/cdn/processed/                 # Core JSON files (6 files)
├── metadata.json                  # Data summary and column mappings
├── stations.json                  # Station information and coordinates
├── species.json                   # Species list with detection counts
├── detections.json               # All manual species annotations
├── environmental.json            # Temperature and depth measurements
└── deployment_metadata.json     # Deployment details and equipment specs

data/cdn/views/                    # Optimized view files (5 files)
├── station_overview.json         # Station comparison metrics (7KB)
├── species_timeline.json         # Temporal detection patterns (1.6KB)
├── acoustic_summary.json         # PCA and index analysis (19.6KB)
├── raw_data_landscape.json       # Data availability overview (32KB)
└── index_distributions.json      # Index quality analysis (119KB)
```

## 🧪 Research Integration

### For Research Scripts (Future)
Keep research separate from the dashboard pipeline:

```bash
# Recommended structure for future research work
research_scripts/                   # Research-specific analyses
├── exploratory_analysis/          # Initial data exploration
├── statistical_models/            # Advanced statistical analyses  
├── paper_figures/                 # Publication-quality figures
└── collaboration/                 # Shared analysis scripts

# Research scripts can import from the main package:
from mbon_analysis.processing import load_core_data
detections, environmental, species = load_core_data()
```

## 🔧 Development Commands

```bash
# Data Pipeline
npm run process-data              # Excel → JSON conversion
npm run generate-views            # JSON → optimized views
npm run upload-cdn               # Upload to Cloudflare R2
npm run pipeline                 # Full pipeline (all 3 steps)

# Dashboard Development  
npm run dev                      # Start dev server
npm run build                    # Production build
npm run lint                     # ESLint check
npm run type-check              # TypeScript validation

# Python Environment
uv sync                          # Install Python dependencies
uv pip install -e .            # Install mbon_analysis package
```

## 🌐 Deployment

### Production Setup
1. **Data Pipeline** (run locally):
   ```bash
   npm run pipeline  # Processes data and uploads to CDN
   ```

2. **Frontend Deployment** (Vercel):
   ```bash
   # Set environment variables in Vercel dashboard:
   NEXT_PUBLIC_DATA_URL=https://your-r2-bucket-url.com
   
   # Deploy
   vercel --prod
   ```

### Environment Variables
```bash
# .env.local (development)
NEXT_PUBLIC_DATA_URL=https://your-r2-bucket-url.com

# Production (set in Vercel dashboard)
NEXT_PUBLIC_DATA_URL=https://your-production-r2-url.com
```

## 🤝 Contributing

### For Scientists
- **Content Updates**: Edit `page.content.tsx` files for text changes
- **New Analyses**: Request new views via GitHub issues
- **Data Updates**: Provide Excel files following naming conventions

### For Developers
- **View Development**: Follow the 5-step process above
- **UI Components**: Add to `src/components/`
- **Data Processing**: Extend `mbon_analysis/` package

## 📚 Scientific Context

### Research Background
This dashboard supports research into using acoustic indices as proxies for marine biodiversity. Traditional biodiversity monitoring requires manual species identification from audio recordings - a time-intensive process. Our approach investigates whether computed acoustic indices can predict biodiversity patterns automatically.

### Key Research Questions
1. **Index Reduction**: Can we reduce 56+ acoustic indices to 3-5 "super indices" via PCA?
2. **Biodiversity Prediction**: Which indices best predict species detection patterns?
3. **Environmental Confounders**: How do temperature and depth affect acoustic environments?
4. **Spatial Patterns**: How do acoustic environments differ between stations?
5. **Temporal Stability**: Are index patterns consistent across years?

### Acoustic Indices Categories
- **Temporal Domain**: ZCR, MEANt, VARt, SKEWt, KURTt
- **Frequency Domain**: MEANf, VARf, SKEWf, KURTt, NBPEAKS  
- **Acoustic Complexity**: ACI, NDSI, ADI, AEI
- **Diversity Indices**: H_Havrda, H_Renyi, H_pairedShannon
- **Bioacoustic**: BioEnergy, AnthroEnergy, BI, rBA

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **Data Collection**: [Marine Science Lab]
- **Acoustic Analysis**: [Collaborator Institution]  
- **Funding**: [Grant Information]

---

*Built with 💙 for marine conservation and acoustic ecology research*

**Dashboard Performance**: Loading 200MB+ of data in <2 seconds through intelligent view optimization.