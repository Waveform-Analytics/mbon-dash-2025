import RawDataLandscape from '@/components/charts/RawDataLandscape';
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

      {/* More visualizations coming soon */}
      <section className="mb-12">
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center">
          <h3 className="text-lg font-semibold text-slate-800 mb-2">Additional Visualizations In Development</h3>
          <p className="text-slate-600 text-sm mb-4">
            We're rebuilding the following visualizations with optimized data views for better performance:
          </p>
          <ul className="text-slate-600 text-sm space-y-2 max-w-2xl mx-auto text-left">
            <li>• <strong>Index Distributions & Quality Check</strong> - Probability density functions for acoustic indices by bandwidth</li>
            <li>• <strong>Temporal Heatmaps</strong> - Hourly acoustic patterns across months and stations</li>
            <li>• <strong>Bandwidth Comparison</strong> - Statistical comparisons between FullBW and 8kHz measurements</li>
          </ul>
          <p className="text-slate-500 text-xs mt-4">
            These visualizations will use aggregated data views instead of the 175MB raw dataset.
          </p>
        </div>
      </section>
    </div>
  )
}