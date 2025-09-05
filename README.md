# MBON Marine Biodiversity Dashboard 2025

**Exploring marine soundscape biodiversity through acoustic indices** – An interactive web dashboard analyzing whether computed acoustic patterns can predict marine biodiversity and serve as proxies for complex biodiversity monitoring.

🔗 **Live Dashboard**: [https://mbon-dash-2025.vercel.app](https://mbon-dash-2025.vercel.app)  
📊 **Research Focus**: Hydrophone recordings from May River, SC coastal stations (2018, 2021)  
🎯 **Core Question**: Can 56+ acoustic indices replace labor-intensive manual species detection?

---

## 📖 For Casual Visitors

### What This Project Does

This dashboard makes marine biodiversity research accessible by transforming complex acoustic data into interactive visualizations. Researchers deployed underwater microphones (hydrophones) at multiple stations in the May River, SC coastal waters to record marine sounds. Instead of manually identifying each fish call or dolphin click – which takes hours – this project explores whether computer-calculated "acoustic indices" can automatically predict biodiversity patterns.

### Key Features

- **🗺️ Interactive Station Map**: Explore hydrophone locations in May River, SC coastal waters
- **📈 Species Detection Patterns**: See when and where marine animals are most active  
- **🎵 Acoustic Analysis**: Discover relationships between sound patterns and biodiversity
- **🔬 Scientific Insights**: Principal Component Analysis reducing 56+ indices to key patterns
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

### The Science

**Marine Biodiversity**: Counting and identifying marine species is crucial for conservation but traditionally requires expert analysis of hours of recordings.

**Acoustic Indices**: Computer algorithms that analyze audio patterns – frequency diversity, temporal patterns, complexity measures – without identifying specific species.

**Research Innovation**: This project tests whether these algorithmic indices can predict biodiversity patterns, potentially revolutionizing marine monitoring efficiency.

---

## 📐 Methods & Analytical Approach

### Temporal Stratification for Non-Stationary Marine Soundscapes

Marine acoustic environments are highly **non-stationary**, exhibiting strong temporal patterns that must be carefully considered in predictive modeling:

#### Temporal Challenges
- **Seasonal Fish Activity**: Fish calling activity peaks during spawning seasons (primarily spring), with different species active at different times of year
- **Species-Specific Temporal Niches**: Each marine species has distinct temporal activity patterns throughout the annual cycle
- **Variable Human Activity**: Vessel traffic and anthropogenic sounds vary seasonally and diurnally
- **Environmental Confounders**: Temperature, tidal cycles, and weather patterns influence both acoustic indices and species behavior

#### Temporal Stratification Strategy
To address non-stationarity, we implement **temporal stratified sampling** rather than random train/test splits:

```python
# Instead of random splitting, preserve temporal patterns
for month in available_months:
    month_data = dataset[dataset.month == month]
    train_sample = month_data.sample(70%)  # Proportional sampling per month
    test_sample = month_data.sample(30%)   # Ensures temporal representation
```

**Benefits of this approach:**
1. **Preserves seasonal patterns** in both training and testing datasets
2. **Enables generalization** across different time periods
3. **Provides realistic performance estimates** for year-round monitoring deployment
4. **Accounts for species-specific temporal activity** patterns

#### Model Validation Philosophy
Traditional machine learning assumes **stationary data distributions**, but marine ecosystems are inherently temporal. Our validation strategy:

- **Temporal Stratification**: Ensures models see representative temporal variation during training
- **Month-Based Sampling**: Maintains proportional representation across all available months
- **Seasonal Balance**: Prevents overfitting to specific seasonal patterns (e.g., spring spawning activity)

This methodological choice is critical for developing acoustic monitoring tools that work reliably across the full annual cycle of marine ecosystem dynamics.

---

## 🏗️ Architecture Overview

### Three-Layer System

```
🐍 Python Processing    →    🌐 Web Dashboard    →    🌍 Global CDN
Heavy data computation      Interactive visualization    Fast worldwide delivery
     (Local/Server)              (Next.js/Vercel)          (Cloudflare R2)
```

### Data Flow

```
Raw Excel/CSV Files → Python Analysis → Optimized JSON Views → CDN → Dashboard
     (50+ files)         (Processing)        (8 files <50KB)    (Global) (<2s load)
```

**Two-Tier Data Strategy**:
- **Small Files (<50KB)**: Pre-processed views loaded instantly from CDN
- **Large Files (>50MB)**: Progressive loading via API with server-side filtering

---

## 🚀 Quick Start

### For Users
Just visit the live dashboard – no installation required!

### For Developers

**Prerequisites**:
- Node.js 18+ with npm
- Python 3.12+ with uv package manager
- Optional: Cloudflare R2 + Mapbox tokens for full functionality

**1. Clone and Setup**
```bash
git clone <repository-url>
cd mbon-dash-2025

# Install everything
npm run setup
```

**2. Environment Configuration**
```bash
# Create .env.local at project root
touch .env.local
```

Add required environment variables:
```bash
# CDN Configuration
NEXT_PUBLIC_CDN_BASE_URL=https://waveformdata.work
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token

# Python CDN Upload (optional for local development)
CLOUDFLARE_R2_ACCOUNT_ID=your_account_id
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=mbon-usc-2025
CLOUDFLARE_R2_ENDPOINT=https://your_account_id.r2.cloudflarestorage.com
CLOUDFLARE_R2_PUBLIC_URL=https://waveformdata.work
```

**3. Development**
```bash
# Start development servers
npm run dev                 # Starts both frontend and data processing

# Or individually:
cd dashboard && npm run dev # Frontend only at http://localhost:3000
cd python && make views     # Generate data views
```

---

## 📁 Project Structure

### High-Level Layout
```
mbon-dash-2025/                    # Monorepo root
├── 📱 dashboard/                  # Next.js web application
├── 🐍 python/                     # Data processing and analysis
├── 📊 data/                       # Local data storage
├── 📝 notes/                      # Documentation and research notes
├── 🔧 .env.local                  # Environment configuration (root level)
└── 📋 README.md                   # This comprehensive guide
```

### Detailed Structure

<details>
<summary><strong>📱 Dashboard (Next.js Frontend)</strong></summary>

```
dashboard/
├── src/app/                       # App Router pages
│   ├── page.tsx                   # Landing page with map & overview
│   ├── analysis/                  # PCA & correlation analysis
│   ├── data/                      # Data exploration pages
│   └── api/                       # 7 API endpoints for data loading
│       ├── views/[name]/route.ts  # Generic view loader
│       ├── indices-heatmap/       # Progressive loading for large datasets
│       └── pca-analysis/          # Principal component analysis
├── src/components/
│   ├── charts/                    # 15+ chart components (Nivo-based)
│   ├── maps/                      # Mapbox station visualization
│   └── ui/                        # Reusable UI components
├── src/lib/data/                  # 6 custom data hooks
│   ├── useViewData.ts            # Generic view loader
│   ├── useIndicesHeatmap.ts      # Large dataset progressive loading
│   └── useAcousticDistributions.ts # Acoustic analysis data
└── src/types/                     # TypeScript definitions
```

</details>

<details>
<summary><strong>🐍 Python Processing Engine</strong></summary>

```
python/
├── pyproject.toml                 # Dependencies & dev tools configuration
├── mbon_analysis/                 # Core analysis package
│   ├── data/                     # Data loading utilities
│   ├── analysis/                 # Scientific analysis modules
│   ├── views/                    # View generators for dashboard
│   └── utils/                    # Shared utilities
├── scripts/                       # 20+ processing scripts
│   ├── upload_to_cdn.py          # CDN deployment
│   ├── generate_*.py             # Data processing pipelines
│   └── validate_pipeline.py      # Health checks
├── tests/                         # Comprehensive test suite
│   ├── test_data_loaders.py      # Raw data validation
│   ├── test_view_generation.py   # View creation testing
│   └── test_view_integrity.py    # Data authenticity validation
└── Makefile                       # Common development tasks
```

</details>

<details>
<summary><strong>📊 Data Storage</strong></summary>

```
data/
├── raw/                          # Original Excel/CSV files
│   ├── 2018/                    # First study year
│   ├── 2021/                    # Second study year
│   ├── indices/                 # Acoustic indices CSVs
│   └── metadata/                # Station metadata & classifications
├── processed/                    # Intermediate JSON files
│   ├── compiled_indices.json   # Large dataset (279MB)
│   └── optimized/               # Station-specific optimizations
└── views/                        # Dashboard-ready JSON files (<50KB each)
    ├── stations.json            # Station metadata & coordinates
    ├── datasets_summary.json    # Dataset overview statistics
    ├── heatmap.json            # Species detection patterns
    └── indices_reference.json   # Acoustic indices documentation
```

</details>

---

## 🔬 Scientific Data Pipeline

### Raw Data Sources

**Detection Files**: Manual species annotations from expert analysis
- Species: Silver perch (sp), Oyster toadfish (otbw), Bottlenose dolphin (bde)
- Coverage: 3 stations × 2 years × thousands of 2-hour recording windows

**Acoustic Indices**: 56+ computed metrics analyzing sound patterns
- **Temporal**: Zero crossing rate, variance, skewness, kurtosis
- **Frequency**: Spectral characteristics and peak distributions
- **Complexity**: Acoustic Complexity Index (ACI), diversity measures
- **Bioacoustic**: Bio vs anthropogenic energy ratios

**Environmental Data**: Temperature and depth measurements for correlation analysis

### Processing Workflow

```bash
# Complete data pipeline
cd python/

# 1. Raw Data Processing (Excel/CSV → JSON)
uv run scripts/compile_detections.py     # Species detection data
uv run scripts/compile_indices.py        # Acoustic indices compilation
uv run scripts/convert_indices_to_json.py # Format standardization

# 2. View Generation (JSON → Dashboard Views)
make views                               # Generate all optimized views
uv run scripts/generate_pca_view.py      # Principal component analysis
uv run scripts/generate_correlation_view.py # Correlation matrices

# 3. CDN Deployment (Views → Global Distribution)
uv run scripts/upload_to_cdn.py         # Deploy to Cloudflare R2

# All-in-one command
make process-data                        # Complete pipeline
```

---

## 🎨 Current Features

### 🏠 Landing Page
- **Interactive Station Map**: Mapbox visualization of May River, SC hydrophone deployments
- **Project Overview**: Research context and scientific objectives  
- **Dataset Summary**: Data coverage statistics and temporal ranges

### 📊 Data Exploration
- **Species Detection Heatmaps**: Temporal activity patterns of marine life
- **Acoustic Indices Browser**: Interactive exploration of 56+ acoustic metrics
- **Environmental Correlations**: Temperature/depth relationship analysis
- **Distribution Analysis**: Probability density visualizations across stations

### 🔬 Advanced Analysis
- **PCA Analysis**: Principal Component Analysis reducing dimensionality
- **Correlation Matrix**: Inter-index relationships and dependencies
- **Station Comparisons**: Cross-location biodiversity pattern analysis
- **Temporal Trends**: Multi-year pattern consistency assessment

---

## 🛠️ Development Guide

### Adding New Visualizations

The architecture supports two approaches based on data size:

#### Small Datasets (<50KB) - Direct CDN Loading

**1. Create Python View Generator**
```python
# python/mbon_analysis/views/my_new_view.py
class MyNewViewGenerator(BaseViewGenerator):
    def generate_view(self) -> Dict[str, Any]:
        loader = create_loader(self.data_root)
        # Process your data here
        return {
            "metadata": {"generated_at": "...", "version": "1.0.0"},
            "data": processed_chart_data
        }
```

**2. Generate View File**
```bash
cd python/
uv run scripts/generate_my_view.py  # Creates data/views/my_new_view.json
```

**3. Create React Hook**
```typescript
// dashboard/src/lib/data/useMyView.ts
export function useMyView() {
  return useViewData<MyViewData>('my_new_view.json');
}
```

**4. Build Chart Component**
```tsx
// dashboard/src/components/charts/MyChart.tsx
export default function MyChart({ data }: { data: MyViewData }) {
  return <ResponsiveBar data={data.chartData} /* ... */ />;
}
```

#### Large Datasets (>50MB) - Progressive Loading

For large datasets, create API routes with server-side filtering:

**1. Create API Route**
```typescript
// dashboard/src/app/api/my-large-data/route.ts
export async function GET(request: NextRequest) {
  const compiledData = await loadFromCDN();
  const filteredData = filterByParams(compiledData, searchParams);
  return NextResponse.json(filteredData);
}
```

**2. Create Progressive Loading Hook**
```typescript
// dashboard/src/lib/data/useMyLargeData.ts
export function useMyLargeData(params: FilterParams) {
  // Handles loading states, caching, and parameter-based fetching
}
```

### Development Commands

**Python (Data Processing)**
```bash
cd python/
make dev-setup          # Install deps + pre-commit hooks
make views              # Generate all view files
make test-cov           # Run tests with coverage
make lint               # Code quality checks
uv run scripts/upload_to_cdn.py # Deploy to CDN
```

**Dashboard (Frontend)**
```bash
cd dashboard/
npm run dev             # Start development server
npm run build           # Production build
npm run lint            # Code quality
npm run typecheck       # TypeScript validation
```

### Testing Strategy

**Python Testing (pytest)**
- `test_data_loaders.py` - Raw data validation
- `test_view_generation.py` - View creation and size limits
- `test_view_integrity.py` - Data authenticity and traceability
- `test_cdn_operations.py` - Upload and deployment validation

```bash
cd python/
uv run pytest tests/ --cov=mbon_analysis --cov-report=html
```

**Frontend Testing (Recommended Setup)**
- Jest + React Testing Library for component tests
- Playwright for end-to-end testing
- API route testing with Next.js test utilities

---

## 🚀 Deployment

### Development Deployment
```bash
# 1. Generate latest data views
cd python/ && make views

# 2. Upload to CDN (optional for local dev)
uv run scripts/upload_to_cdn.py

# 3. Start dashboard
cd dashboard/ && npm run dev  # http://localhost:3000
```

### Production Deployment

**Automatic Frontend Deployment (Vercel)**
- Push to main branch triggers automatic Vercel deployment
- Ensure environment variables are configured in Vercel project settings

**Manual Data Deployment**
```bash
cd python/
make process-data               # Generate all views
uv run scripts/upload_to_cdn.py # Deploy to global CDN
```

**Environment Variables for Production**:
Set these in your Vercel project dashboard:
- `NEXT_PUBLIC_CDN_BASE_URL=https://waveformdata.work`
- `NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token`

---

## 📈 Performance Characteristics

### Load Times
- **Landing Page**: <2 seconds (small view files)
- **Data Exploration**: ~16 seconds first load, <1 second thereafter
- **Chart Interactions**: Real-time with intelligent caching

### Scalability Features
- **CDN-First Architecture**: Global edge caching via Cloudflare R2
- **Progressive Loading**: Server-side filtering of large datasets
- **Intelligent Caching**: Memory caching prevents redundant processing
- **View Optimization**: All dashboard views under 50KB for instant loading

---

## 🔧 Troubleshooting

### Common Issues

**"View not found" errors**
```bash
# Ensure view file exists and was uploaded
cd python/
ls data/views/my_view.json
uv run scripts/upload_to_cdn.py
```

**Chart not rendering**
- Check data structure matches Nivo requirements
- Verify TypeScript interfaces align with actual data
- Use browser dev tools to inspect data flow

**Environment variables not loading**
- Ensure `.env.local` is at project root (not in dashboard/)
- Check `next.config.ts` is loading with correct relative path

**Large dataset performance issues**
- Use progressive loading with API routes
- Pre-aggregate data in Python, not React
- Consider data pagination or windowing

---

## 📚 Documentation

### Technical Documentation (`notes/` directory)
- **ANALYSIS_APPROACH.md**: Scientific methodology and statistical methods
- **CDN_INTEGRATION_GUIDE.md**: Infrastructure setup and deployment
- **DESIGN_SYSTEM.md**: UI/UX guidelines and component standards
- **testing-strategy.md**: Comprehensive testing methodology

### Code Documentation
- **API Routes**: Documented in each route handler file
- **Data Hooks**: TypeScript interfaces with JSDoc comments
- **Components**: Prop interfaces and usage examples

---

## 🤝 Contributing

### Getting Started
1. Fork the repository and clone locally
2. Set up development environment with `npm run setup`
3. Configure environment variables in `.env.local`
4. Run tests to validate setup: `cd python && uv run pytest tests/`

### Development Workflow
1. Create feature branch from main
2. Add comprehensive tests for new functionality
3. Ensure code quality checks pass (`make lint` in Python, `npm run lint` in dashboard)
4. Update documentation as needed
5. Submit PR with clear description

### Code Standards
- **Python**: PEP 8, type hints, comprehensive docstrings
- **TypeScript**: Strict TypeScript, explicit interfaces, React best practices
- **Testing**: >80% coverage for new features
- **Documentation**: Update relevant docs with feature additions

---

## 📊 Project Impact

### Technical Achievements
- **Modern Architecture**: Latest Next.js, React, and Python technologies
- **Global Performance**: Sub-second loading via CDN distribution
- **Scalable Design**: Handles both small views and large datasets efficiently
- **Data Integrity**: Comprehensive testing ensures reliability

### Scientific Contributions
- **Interactive Research**: 56+ acoustic indices made accessible to researchers
- **Data Democratization**: Complex marine data accessible to broader audiences
- **Reproducible Science**: All processing steps documented and version controlled
- **Collaborative Platform**: Multiple researchers can contribute data and analysis

---

## 🔗 Quick Links

- **🌐 Live Dashboard**: [https://mbon-dash-2025.vercel.app](https://mbon-dash-2025.vercel.app)
- **📚 Detailed Architecture**: See `CLAUDE.md` for implementation details
- **🧪 Testing Strategy**: See `notes/testing-strategy.md`
- **🎨 Design System**: See `notes/DESIGN_SYSTEM.md`
- **📊 Analysis Methods**: See `notes/ANALYSIS_APPROACH.md`

---

## 📞 Support

### For Researchers
- Explore the live dashboard to understand the data and visualizations
- Check `notes/` directory for scientific methodology
- Contact maintainers for data questions or collaboration opportunities

### For Developers
- Review existing components in `dashboard/src/components/`
- Examine data hooks in `dashboard/src/lib/data/`
- Check Python view generators in `python/mbon_analysis/views/`
- Use browser dev tools to debug data flow issues

---

**Built with ❤️ for marine biodiversity research and ocean conservation**

*Last updated: January 2025*