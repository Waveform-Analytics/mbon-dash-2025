'use client';

import { 
  MapIcon,
  TruckIcon,
  Squares2X2Icon,
  ChartBarIcon,
  FireIcon,
  BeakerIcon,
  MapPinIcon,
  ClockIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

export default function StationsPage() {
  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-4xl">
          Station Profiles &
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Spatial Context</span>
        </h1>
        <p className="section-description">
          Detailed profiles of the three monitoring stations (9M, 14M, 37M) in May River, South Carolina, 
          including spatial context, deployment details, and environmental characteristics.
        </p>
      </div>

      {/* Research Context */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 mb-12">
        <h2 className="text-2xl font-bold text-slate-900 mb-4"><MapIcon className="w-6 h-6" /> Spatial Research Questions</h2>
        <div className="grid md:grid-cols-2 gap-6 text-slate-700">
          <div>
            <h3 className="font-semibold mb-2"><MapPinIcon className="w-4 h-4" /> Geographic Influences</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li>How does distance from river mouth affect acoustic indices?</li>
              <li>Do habitat differences between stations influence biodiversity patterns?</li>
              <li>Are there spatial gradients in environmental conditions?</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2"><TruckIcon className="w-4 h-4" /> Anthropogenic Proximity</h3>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li>Which stations are closest to marinas and boat traffic?</li>
              <li>How does human activity proximity affect acoustic signatures?</li>
              <li>Can we identify station-specific anthropogenic patterns?</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Station Profiles */}
      <div className="space-y-8">
        
        {/* Enhanced Interactive Map */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <MapIcon className="w-5 h-5 inline mr-2" />Enhanced Station Map
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Interactive map showing station locations with enhanced spatial context for research analysis.
            </p>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2"><Squares2X2Icon className="w-4 h-4" /> Physical Features</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-blue-700">
                  <li>River mouth location and distance</li>
                  <li>Depth contours and bathymetry</li>
                  <li>Tidal flow patterns</li>
                  <li>Habitat type boundaries</li>
                </ul>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h4 className="font-medium text-orange-800 mb-2"><TruckIcon className="w-4 h-4" /> Human Infrastructure</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-orange-700">
                  <li>Marina locations and boat traffic</li>
                  <li>Shipping lanes and navigation channels</li>
                  <li>Coastal development patterns</li>
                  <li>Known noise sources</li>
                </ul>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="font-medium text-green-800 mb-2">🔊 Acoustic Context</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-green-700">
                  <li>Sound propagation modeling</li>
                  <li>Station-specific acoustic signatures</li>
                  <li>Environmental noise sources</li>
                  <li>Species habitat preferences</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Station Comparison Analysis */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <ChartBarIcon className="w-5 h-5 inline mr-2" />Cross-Station Comparison
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Systematic comparison of environmental conditions, species diversity, and acoustic patterns across the three stations.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-800 mb-2"><FireIcon className="w-4 h-4" /> Environmental Profiles</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                  <li>Temperature and depth ranges by station</li>
                  <li>Seasonal environmental variation patterns</li>
                  <li>Water quality and habitat characteristics</li>
                  <li>Tidal influence and current patterns</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-800 mb-2"><BeakerIcon className="w-4 h-4" /> Biodiversity Patterns</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600">
                  <li>Species richness and diversity indices per station</li>
                  <li>Station-specific species preferences</li>
                  <li>Detection frequency comparisons</li>
                  <li>Temporal activity patterns by location</li>
                </ul>
              </div>
            </div>

            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-medium text-yellow-800 mb-2"><MapPinIcon className="w-4 h-4" /> Analysis Goals</h4>
              <p className="text-sm text-yellow-700">
                Identify which environmental and spatial factors most strongly influence acoustic index patterns, 
                helping to understand when and where acoustic monitoring is most effective for biodiversity assessment.
              </p>
            </div>
          </div>
        </div>

        {/* Deployment Timeline */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <ClockIcon className="w-5 h-5 inline mr-2" />Deployment Timeline & Data Quality
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Comprehensive timeline of hydrophone deployments with data quality assessments and known issues.
            </p>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="font-medium text-green-800 mb-2">✅ 2018 Deployments</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-green-700">
                  <li>Active periods for 9M, 14M, 37M</li>
                  <li>Equipment specifications</li>
                  <li>Data collection parameters</li>
                  <li>Quality assessment results</li>
                </ul>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2">✅ 2021 Deployments</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-blue-700">
                  <li>Expanded station network</li>
                  <li>Improved equipment configurations</li>
                  <li>Enhanced data collection protocols</li>
                  <li>Cross-year comparability assessment</li>
                </ul>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h4 className="font-medium text-orange-800 mb-2"><ExclamationTriangleIcon className="w-4 h-4" /> Data Quality Notes</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-orange-700">
                  <li>rmsSPL data quality issues</li>
                  <li>Equipment failures and gaps</li>
                  <li>Environmental contamination events</li>
                  <li>Recommendations for analysis</li>
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
          <p><strong>Current Map:</strong> Basic station locations with Mapbox GL JS integration</p>
          <p><strong>Enhancement Plan:</strong> Add river mouth, marina locations, bathymetry, shipping lanes</p>
          <p><strong>Data Integration:</strong> Deployment metadata, environmental summaries, spatial analysis results</p>
          <p><strong>Visualization Tools:</strong> Enhanced Mapbox layers, Observable Plot for comparisons, interactive timeline</p>
          <p><strong>Research Impact:</strong> Spatial context for interpreting acoustic index performance across locations</p>
        </div>
      </div>

    </div>
  );
}