import RawDataLandscape from '@/components/charts/RawDataLandscape';
import IndexDistributions from '@/components/charts/IndexDistributions';
import AcousticIndicesHeatmap from '@/components/charts/AcousticIndicesHeatmap';
import BandwidthComparisonBoxPlot from '@/components/charts/BandwidthComparisonBoxPlot';
import { IndicesContent } from './page.content';

export default function IndicesExplorerPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          {IndicesContent.header.title}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500">{IndicesContent.header.titleHighlight}</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          {IndicesContent.header.subtitle}
        </p>
      </div>

      {/* Raw Data Landscape */}
      <section className="mb-12">
        <RawDataLandscape 
          width={900} 
          height={600} 
        />
      </section>

      {/* Index Distributions & Quality Check */}
      <section className="mb-12">
        <IndexDistributions 
          width={1200} 
          height={800} 
        />
      </section>

      {/* Acoustic Indices Heatmap */}
      <section className="mb-12">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">{IndicesContent.sections.heatmap.title}</h2>
          <p className="text-slate-600">
            {IndicesContent.sections.heatmap.description}
          </p>
        </div>
        <AcousticIndicesHeatmap />
      </section>

      {/* Bandwidth Comparison Box Plot */}
      <section className="mb-12">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">{IndicesContent.sections.bandwidth.title}</h2>
          <p className="text-slate-600">
            {IndicesContent.sections.bandwidth.description}
          </p>
        </div>
        <BandwidthComparisonBoxPlot />
      </section>
    </div>
  )
}