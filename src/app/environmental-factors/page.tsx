'use client';

import { 
  BeakerIcon,
  ChartBarIcon,
  CalendarIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';

export default function EnvironmentalFactorsPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          Environmental
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Confounders</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          Analysis of how environmental factors influence acoustic indices and their 
          effectiveness as biodiversity indicators.
        </p>
      </div>

      {/* Research Focus */}
      <div className="bg-orange-50 border border-orange-200 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold text-orange-900 mb-3 flex items-center gap-2">
          <QuestionMarkCircleIcon className="w-5 h-5" />
          Research Questions
        </h2>
        <ul className="space-y-2 text-orange-800">
          <li>• Do temperature and depth significantly affect acoustic indices?</li>
          <li>• Should indices be environmentally corrected for biodiversity assessment?</li>
          <li>• Are index patterns driven by environmental conditions or biological activity?</li>
        </ul>
      </div>

      {/* Planned Analyses */}
      <div className="space-y-6">
        
        {/* Temperature Analysis */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <BeakerIcon className="w-5 h-5" />
            Temperature Effects
            <span className="text-sm font-normal text-slate-500 ml-2">(Planned)</span>
          </h3>
          <p className="text-slate-600 mb-4">
            Analysis of temperature correlations with acoustic indices to identify potential 
            confounding effects on biodiversity predictions.
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <ul className="list-disc list-inside space-y-1">
              <li>Temperature-index correlation analysis</li>
              <li>Seasonal temperature cycle effects</li>
            </ul>
            <ul className="list-disc list-inside space-y-1">
              <li>Temperature impacts on sound propagation</li>
              <li>Temperature-dependent biological activity</li>
            </ul>
          </div>
        </div>

        {/* Depth Analysis */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <ChartBarIcon className="w-5 h-5" />
            Depth Effects
            <span className="text-sm font-normal text-slate-500 ml-2">(Planned)</span>
          </h3>
          <p className="text-slate-600 mb-4">
            Evaluation of water depth influences on acoustic measurements and the need 
            for depth-based corrections.
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <ul className="list-disc list-inside space-y-1">
              <li>Depth-index relationships</li>
              <li>Tidal variation impacts</li>
            </ul>
            <ul className="list-disc list-inside space-y-1">
              <li>Water column acoustic effects</li>
              <li>Depth-related habitat preferences</li>
            </ul>
          </div>
        </div>

        {/* Temporal Patterns */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <CalendarIcon className="w-5 h-5" />
            Temporal Patterns
            <span className="text-sm font-normal text-slate-500 ml-2">(Planned)</span>
          </h3>
          <p className="text-slate-600 mb-4">
            Investigation of seasonal and diel patterns in acoustic indices to separate 
            environmental from biological drivers.
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <ul className="list-disc list-inside space-y-1">
              <li>Seasonal variation analysis</li>
              <li>Diel cycle patterns</li>
            </ul>
            <ul className="list-disc list-inside space-y-1">
              <li>Environmental vs biological rhythms</li>
              <li>Multi-year comparisons (2018 vs 2021)</li>
            </ul>
          </div>
        </div>

      </div>

      {/* Data Note */}
      <div className="mt-8 p-4 bg-slate-100 rounded-lg">
        <p className="text-sm text-slate-600">
          <strong>Note:</strong> Environmental analysis will utilize temperature and depth data 
          collected during deployments, combined with the full suite of acoustic indices when available.
        </p>
      </div>

    </div>
  );
}