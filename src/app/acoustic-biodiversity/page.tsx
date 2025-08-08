'use client';

import { 
  BeakerIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';

export default function AcousticBiodiversityPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          Acoustic Indices as
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Biodiversity Proxies</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          Analysis to identify which acoustic indices best predict marine soundscape biodiversity patterns.
        </p>
      </div>

      {/* Research Focus */}
      <div className="bg-ocean-50 border border-ocean-200 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold text-ocean-900 mb-3 flex items-center gap-2">
          <QuestionMarkCircleIcon className="w-5 h-5" />
          Research Question
        </h2>
        <p className="text-ocean-800">
          Which acoustic indices most accurately predict species presence and can serve as 
          cost-effective proxies for manual species detection?
        </p>
      </div>

      {/* Planned Analyses */}
      <div className="space-y-6">
        
        {/* Correlation Analysis */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <ChartBarIcon className="w-5 h-5" />
            Index-Species Correlations
            <span className="text-sm font-normal text-slate-500 ml-2">(Planned)</span>
          </h3>
          <p className="text-slate-600 mb-4">
            Statistical analysis of relationships between acoustic indices and species detections 
            to identify the most informative indices for biodiversity assessment.
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <ul className="list-disc list-inside space-y-1">
              <li>Correlation coefficients between indices and species presence</li>
              <li>Identification of biodiversity-relevant indices</li>
            </ul>
            <ul className="list-disc list-inside space-y-1">
              <li>Performance rankings of individual indices</li>
              <li>Statistical significance testing</li>
            </ul>
          </div>
        </div>

        {/* PCA */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <MagnifyingGlassIcon className="w-5 h-5" />
            Principal Component Analysis
            <span className="text-sm font-normal text-slate-500 ml-2">(Planned)</span>
          </h3>
          <p className="text-slate-600 mb-4">
            Dimensionality reduction to understand relationships among acoustic indices and 
            their combined ability to explain biodiversity patterns.
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <ul className="list-disc list-inside space-y-1">
              <li>Identify clusters of related indices</li>
              <li>Determine principal components of soundscape variation</li>
            </ul>
            <ul className="list-disc list-inside space-y-1">
              <li>Visualize index relationships</li>
              <li>Reduce dimensionality for modeling</li>
            </ul>
          </div>
        </div>

        {/* Biological vs Anthropogenic */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <BeakerIcon className="w-5 h-5" />
            Signal Source Differentiation
            <span className="text-sm font-normal text-slate-500 ml-2">(Planned)</span>
          </h3>
          <p className="text-slate-600 mb-4">
            Analysis of whether acoustic indices can differentiate between biological sounds 
            (species vocalizations) and anthropogenic noise (vessels, human activity).
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <div>
              <strong className="text-slate-700">Biological Sources:</strong>
              <p>Fish calls, marine mammal vocalizations, invertebrate sounds</p>
            </div>
            <div>
              <strong className="text-slate-700">Anthropogenic Sources:</strong>
              <p>Vessel noise, mechanical sounds, human activities</p>
            </div>
          </div>
        </div>

      </div>

      {/* Data Note */}
      <div className="mt-8 p-4 bg-slate-100 rounded-lg">
        <p className="text-sm text-slate-600">
          <strong>Note:</strong> Analysis will be conducted once the full suite of 60+ acoustic indices 
          becomes available. Current explorations use manual species annotations from 2018 and 2021.
        </p>
      </div>

    </div>
  );
}