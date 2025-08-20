'use client';

// Icons removed since text sections were removed
import { AcousticBiodiversityContent } from './page.content';
import AcousticIndicesHeatmap from '@/components/charts/AcousticIndicesHeatmap';
import BandwidthComparisonBoxPlot from '@/components/charts/BandwidthComparisonBoxPlot';

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

      {/* Acoustic Indices Heatmap - NEW VISUALIZATION */}
      <AcousticIndicesHeatmap />

      {/* Bandwidth Comparison Box Plot */}
      <div className="mt-8">
        <BandwidthComparisonBoxPlot />
      </div>


    </div>
  );
}