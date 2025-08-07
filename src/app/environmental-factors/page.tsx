'use client';

import { 
  FireIcon,
  Squares2X2Icon,
  ChartBarIcon,
  CalendarIcon,
  ArrowTrendingUpIcon,
  ScaleIcon,
  MapIcon,
  HomeModernIcon,
  TruckIcon
} from '@heroicons/react/24/outline';

export default function EnvironmentalFactorsPage() {
  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-4xl">
          Environmental &
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Spatial Influences</span>
        </h1>
        <p className="section-description">
          Understanding how temperature, depth, seasonal patterns, and spatial factors 
          influence acoustic indices and their effectiveness as biodiversity predictors.
        </p>
      </div>

      {/* Research Question */}
      <div className="bg-orange-50 border border-orange-200 rounded-xl p-8 mb-12">
        <h2 className="text-2xl font-bold text-orange-900 mb-4 flex items-center gap-2">
          <FireIcon className="w-6 h-6" />
          Key Research Questions
        </h2>
        <div className="space-y-3 text-orange-800">
          <p><strong>1. Environmental Confounders:</strong> Do temperature and depth significantly affect acoustic indices?</p>
          <p><strong>2. Correction Necessity:</strong> Should indices be environmentally corrected for better biodiversity prediction?</p>
          <p><strong>3. Driving Forces:</strong> Are indices primarily driven by environmental conditions or biological activity?</p>
        </div>
        <div className="mt-4 p-4 bg-orange-100 rounded-lg">
          <p className="text-sm text-orange-700">
            <strong>Why This Matters:</strong> If acoustic indices are strongly influenced by environmental factors, 
            we may need to correct for these effects to get meaningful biodiversity information, or understand 
            the limits of when and where indices can be reliably used.
          </p>
        </div>
      </div>

      {/* Analysis Sections */}
      <div className="space-y-8">
        
        {/* Environmental Confounders */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <Squares2X2Icon className="w-5 h-5 inline mr-2" />Environmental Confounding Analysis
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Systematic analysis of how temperature and depth measurements correlate with 
              each acoustic index to identify potential confounding relationships.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-3 flex items-center gap-2">
                  <FireIcon className="w-4 h-4" />
                  Temperature Effects
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-blue-700">
                  <li>Correlation analysis: temperature vs each acoustic index</li>
                  <li>Seasonal temperature cycles and index variations</li>
                  <li>Temperature-dependent biological activity patterns</li>
                  <li>Physical effects of temperature on sound transmission</li>
                </ul>
              </div>
              
              <div className="bg-teal-50 p-6 rounded-lg border border-teal-200">
                <h4 className="font-medium text-teal-800 mb-3">📏 Depth Effects</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-teal-700">
                  <li>Depth vs acoustic index relationships</li>
                  <li>Water column effects on sound propagation</li>
                  <li>Depth-related habitat preferences of species</li>
                  <li>Tidal and depth variation impacts on recordings</li>
                </ul>
              </div>
            </div>

            <div className="mt-6 p-4 bg-slate-50 rounded-lg">
              <h4 className="font-medium text-slate-800 mb-2"><ChartBarIcon className="w-4 h-4" /> Planned Visualizations</h4>
              <div className="grid md:grid-cols-3 gap-4 text-sm text-slate-600">
                <div>• Scatterplot matrices: indices vs environmental variables</div>
                <div>• Correlation heatmaps with significance testing</div>
                <div>• Partial correlation analysis controlling for other factors</div>
              </div>
            </div>
          </div>
        </div>

        {/* Seasonal Patterns */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <CalendarIcon className="w-5 h-5 inline mr-2" />Seasonal Pattern Analysis
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Decomposition of temporal patterns to separate environmental seasonality 
              from biological seasonal activity in acoustic indices.
            </p>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-800 mb-2">🔄 Seasonal Decomposition</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                  <li>Time series decomposition: trend, seasonal, residual components</li>
                  <li>Identification of dominant seasonal frequencies</li>
                  <li>Comparison of seasonal patterns across indices and species</li>
                  <li>Environmental vs biological drivers of seasonality</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-800 mb-2"><ArrowTrendingUpIcon className="w-4 h-4" /> Monthly Pattern Analysis</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                  <li>Monthly boxplots for each acoustic index</li>
                  <li>Species activity peaks by season</li>
                  <li>Environmental variable cycles (temperature, depth)</li>
                  <li>Cross-correlation analysis between environmental and acoustic patterns</li>
                </ul>
              </div>
            </div>

            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-medium text-yellow-800 mb-2">🤔 Research Questions</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                <li>Are seasonal fluctuations in indices driven by environmental changes or biological activity cycles?</li>
                <li>Do breeding seasons correlate with specific acoustic index peaks?</li>
                <li>Can we separate temperature-driven vs biologically-driven seasonal patterns?</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Environmental Correction Models */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <ScaleIcon className="w-5 h-5 inline mr-2" />Environmental Correction Analysis
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Development and testing of environmental correction methods to improve 
              acoustic indices as biodiversity predictors.
            </p>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-800 mb-2">🔧 Correction Methods</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                  <li>Linear regression models: index ~ temperature + depth</li>
                  <li>Residual analysis: environmentally-corrected indices</li>
                  <li>Non-linear correction approaches (GAM, splines)</li>
                  <li>Multi-variable environmental corrections</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-800 mb-2"><ChartBarIcon className="w-4 h-4" /> Performance Comparison</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                  <li>Raw vs corrected index performance for biodiversity prediction</li>
                  <li>Improvement in species correlation after correction</li>
                  <li>Cross-validation of correction models</li>
                  <li>Recommendations for when correction is beneficial</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Spatial Factors - Future */}
        <div className="chart-container bg-slate-50 border-dashed">
          <h3 className="text-xl font-semibold text-slate-700 mb-4">
            <MapIcon className="w-5 h-5 inline mr-2" />Spatial Factor Analysis
            <span className="badge bg-slate-200 text-slate-700 ml-3">Future Phase</span>
          </h3>
          <div className="space-y-4 text-slate-500">
            <p className="mb-4">
              <strong>Advanced spatial analysis</strong> incorporating geographic and anthropogenic 
              factors that may influence acoustic indices and biodiversity patterns.
            </p>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <h4 className="font-medium text-slate-600 mb-2 flex items-center gap-2">
                  <HomeModernIcon className="w-4 h-4" />
                  River Gradient Effects
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Distance from river mouth analysis</li>
                  <li>Salinity gradient effects</li>
                  <li>Habitat type variations</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-600 mb-2 flex items-center gap-2">
                  <TruckIcon className="w-4 h-4" />
                  Anthropogenic Proximity
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Distance to marinas and boat traffic</li>
                  <li>Shipping lane proximity effects</li>
                  <li>Development pressure indicators</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-600 mb-2">📍 Station Characteristics</h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Site-specific environmental profiles</li>
                  <li>Habitat complexity measures</li>
                  <li>Local anthropogenic signatures</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Implementation Notes */}
      <div className="mt-12 p-6 bg-slate-100 rounded-xl">
        <h3 className="text-lg font-semibold text-slate-800 mb-3">🔧 Implementation Notes</h3>
        <div className="text-sm text-slate-600 space-y-2">
          <p><strong>Data Sources:</strong> Temperature and depth measurements from hydrophone deployments, rmsSPL acoustic indices, deployment metadata</p>
          <p><strong>Analysis Methods:</strong> Correlation analysis, time series decomposition, regression modeling, GAM/spline fitting</p>
          <p><strong>Visualization Tools:</strong> Observable Plot for time series and scatterplots, D3.js for interactive environmental data exploration</p>
          <p><strong>Key Outputs:</strong> Environmental correction recommendations, seasonal pattern identification, spatial factor importance</p>
        </div>
      </div>

    </div>
  );
}