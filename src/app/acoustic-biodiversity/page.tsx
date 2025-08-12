'use client';

import { 
  BeakerIcon,
  ChartBarIcon,
  MagnifyingGlassIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import { AcousticBiodiversityContent } from './page.content';

export default function AcousticBiodiversityPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          {AcousticBiodiversityContent.header.title}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500">{AcousticBiodiversityContent.header.titleHighlight}</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          {AcousticBiodiversityContent.header.subtitle}
        </p>
      </div>

      {/* Research Focus */}
      <div className="bg-ocean-50 border border-ocean-200 rounded-xl p-6 mb-8">
        <h2 className="text-lg font-semibold text-ocean-900 mb-3 flex items-center gap-2">
          <QuestionMarkCircleIcon className="w-5 h-5" />
          {AcousticBiodiversityContent.researchFocus.title}
        </h2>
        <p className="text-ocean-800">
          {AcousticBiodiversityContent.researchFocus.description}
        </p>
      </div>

      {/* Planned Analyses */}
      <div className="space-y-6">
        
        {/* Correlation Analysis */}
        <div className="chart-container">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <ChartBarIcon className="w-5 h-5" />
            {AcousticBiodiversityContent.correlationAnalysis.title}
            <span className="text-sm font-normal text-slate-500 ml-2">{AcousticBiodiversityContent.correlationAnalysis.status}</span>
          </h3>
          <p className="text-slate-600 mb-4">
            {AcousticBiodiversityContent.correlationAnalysis.description}
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
            {AcousticBiodiversityContent.pca.title}
            <span className="text-sm font-normal text-slate-500 ml-2">{AcousticBiodiversityContent.pca.status}</span>
          </h3>
          <p className="text-slate-600 mb-4">
            {AcousticBiodiversityContent.pca.description}
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
            {AcousticBiodiversityContent.signalDifferentiation.title}
            <span className="text-sm font-normal text-slate-500 ml-2">{AcousticBiodiversityContent.signalDifferentiation.status}</span>
          </h3>
          <p className="text-slate-600 mb-4">
            {AcousticBiodiversityContent.signalDifferentiation.description}
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-600">
            <div>
              <strong className="text-slate-700">{AcousticBiodiversityContent.signalDifferentiation.biological.label}</strong>
              <p>{AcousticBiodiversityContent.signalDifferentiation.biological.description}</p>
            </div>
            <div>
              <strong className="text-slate-700">{AcousticBiodiversityContent.signalDifferentiation.anthropogenic.label}</strong>
              <p>{AcousticBiodiversityContent.signalDifferentiation.anthropogenic.description}</p>
            </div>
          </div>
        </div>

      </div>

      {/* Data Note */}
      <div className="mt-8 p-4 bg-slate-100 rounded-lg">
        <p className="text-sm text-slate-600">
          <strong>{AcousticBiodiversityContent.dataNote.label}</strong> {AcousticBiodiversityContent.dataNote.text}
        </p>
      </div>

    </div>
  );
}