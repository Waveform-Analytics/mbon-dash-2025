'use client';

import { 
  BeakerIcon,
  ChartBarIcon,
  MapPinIcon,
  ArrowTrendingUpIcon,
  MagnifyingGlassIcon,
  ScaleIcon,
  DocumentTextIcon,
  TruckIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';

export default function AcousticBiodiversityPage() {
  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-4xl">
          Acoustic Indices as
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Biodiversity Proxies</span>
        </h1>
        <p className="section-description">
          Exploring which computed acoustic indices best predict marine soundscape biodiversity 
          and can serve as cost-effective alternatives to manual species detection methods.
        </p>
      </div>

      {/* Research Question */}
      <div className="bg-ocean-50 border border-ocean-200 rounded-xl p-8 mb-12">
        <h2 className="text-2xl font-bold text-ocean-900 mb-4 flex items-center gap-2">
          <AcademicCapIcon className="w-6 h-6" />
          Primary Research Question
        </h2>
        <p className="text-lg text-ocean-800 mb-4">
          <strong>"Which acoustic indices most accurately predict species presence and soundscape biodiversity patterns?"</strong>
        </p>
        <p className="text-ocean-700">
          This analysis will identify the most informative acoustic indices for biodiversity monitoring, 
          potentially enabling cost-effective, automated assessment of marine ecosystems compared to 
          expensive manual annotation methods.
        </p>
      </div>

      {/* Planned Analysis Sections */}
      <div className="space-y-8">
        
        {/* Index Performance Analysis */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <ChartBarIcon className="w-5 h-5 inline mr-2" />Index Performance Analysis
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4 text-slate-600">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                  <MapPinIcon className="w-4 h-4" />
                  Correlation Analysis
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Correlation matrix: acoustic indices vs species detections</li>
                  <li>Identify which indices correlate with biological vs anthropogenic sounds</li>
                  <li>Interactive heatmap showing strength of relationships</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                  <ArrowTrendingUpIcon className="w-4 h-4" />
                  Performance Rankings
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Ranked list: "Top 10 Most Informative Indices for Biodiversity"</li>
                  <li>Statistical significance testing for each index-species relationship</li>
                  <li>Effect size measurements for practical significance</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* PCA Analysis */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <MagnifyingGlassIcon className="w-5 h-5 inline mr-2" />Principal Component Analysis
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4 text-slate-600">
            <p className="mb-4">
              Dimensionality reduction to identify which acoustic indices cluster together and 
              which combinations best explain biodiversity patterns.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                  <ScaleIcon className="w-4 h-4" />
                  Interactive PCA Biplot
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Visualize relationships between 60+ acoustic indices</li>
                  <li>Show species loadings to identify biodiversity-relevant indices</li>
                  <li>Interactive exploration of principal components</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                  <DocumentTextIcon className="w-4 h-4" />
                  Component Interpretation
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Biological meaning of major principal components</li>
                  <li>Which indices contribute most to biodiversity prediction</li>
                  <li>Variance explained by each component</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Species vs Anthropogenic */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <BeakerIcon className="w-5 h-5 inline mr-2" />Biological vs <TruckIcon className="w-5 h-5 inline mx-2" />Anthropogenic Signals
            <span className="badge badge-coral ml-3">Planned</span>
          </h3>
          <div className="space-y-4 text-slate-600">
            <p className="mb-4">
              Analysis of whether acoustic indices can differentiate between biological sounds 
              (species calls) and anthropogenic noise (vessels, chains, human activity).
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="font-medium text-green-800 mb-2 flex items-center gap-2">
                  <BeakerIcon className="w-4 h-4" />
                  Biological Sounds
                </h4>
                <p className="text-sm text-green-700">
                  Silver perch, oyster toadfish, bottlenose dolphins, spotted seatrout, 
                  and other marine species vocalizations
                </p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h4 className="font-medium text-orange-800 mb-2 flex items-center gap-2">
                  <TruckIcon className="w-4 h-4" />
                  Anthropogenic Sounds
                </h4>
                <p className="text-sm text-orange-700">
                  Vessel noise, chain sounds, unknown anthropogenic sources 
                  from manual annotations
                </p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2 flex items-center gap-2">
                  <ChartBarIcon className="w-4 h-4" />
                  Analysis Methods
                </h4>
                <p className="text-sm text-blue-700">
                  Distribution plots, discriminant analysis, index performance 
                  for sound source classification
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Future: Biodiversity Prediction Models */}
        <div className="chart-container bg-slate-50 border-dashed">
          <h3 className="text-xl font-semibold text-slate-700 mb-4">
            🤖 Biodiversity Prediction Models
            <span className="badge bg-slate-200 text-slate-700 ml-3">Future Phase</span>
          </h3>
          <div className="space-y-4 text-slate-500">
            <p>
              <strong>Advanced analysis</strong> to develop predictive models using the most informative 
              acoustic indices identified in the correlation and PCA analyses.
            </p>
            <div className="grid md:grid-cols-2 gap-6 text-sm">
              <div>
                <h4 className="font-medium text-slate-600 mb-2">Model Development</h4>
                <ul className="list-disc list-inside space-y-1">
                  <li>Multiple regression models: indices → species richness</li>
                  <li>Machine learning approaches (Random Forest, SVM)</li>
                  <li>Cross-validation across time periods and stations</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-600 mb-2">Validation & Application</h4>
                <ul className="list-disc list-inside space-y-1">
                  <li>Model performance metrics and uncertainty quantification</li>
                  <li>Recommendations for monitoring program design</li>
                  <li>Cost-effectiveness analysis vs manual detection methods</li>
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
          <p><strong>Current Data:</strong> Manual species annotations (2018, 2021) + rmsSPL acoustic index data</p>
          <p><strong>Future Data:</strong> 60+ acoustic indices at 5-minute resolution</p>
          <p><strong>Analysis Tools:</strong> Observable Plot for visualizations, D3.js for interactions, Python/R for statistical analysis</p>
          <p><strong>Target Audience:</strong> Marine biologists, acoustics researchers, conservation practitioners</p>
        </div>
      </div>

    </div>
  );
}