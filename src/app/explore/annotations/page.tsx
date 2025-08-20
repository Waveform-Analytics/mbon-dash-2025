import MonthlyDetectionsTimeline from '@/components/charts/MonthlyDetectionsTimeline';
import { AnnotationsContent } from './page.content';

export default function AnnotationsExplorerPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          {AnnotationsContent.header.title}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500">{AnnotationsContent.header.titleHighlight}</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          {AnnotationsContent.header.subtitle}
        </p>
      </div>

      {/* Detection Timeline Section */}
      <section className="mb-12">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">{AnnotationsContent.timeline.title}</h2>
          <p className="text-slate-600">
            {AnnotationsContent.timeline.description}
          </p>
        </div>
        
        <MonthlyDetectionsTimeline />
      </section>
    </div>
  )
}