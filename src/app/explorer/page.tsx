import MonthlyDetectionsTimeline from '@/components/charts/MonthlyDetectionsTimeline';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

export default function ExplorerPage() {
  return (
    <div className="page-container">
      <div className="mb-8">
        <h1 className="section-heading">Data Explorer</h1>
        <p className="section-description">
          Interactive exploration of marine biodiversity detection patterns across stations and time periods.
        </p>
      </div>

      {/* Detection Timeline Section */}
      <section className="mb-12">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">Detection Timeline</h2>
          <p className="text-slate-600">
            Monthly detection patterns comparing 2018 vs 2021 data across all stations. 
            Use the dropdown to explore different species and detection categories.
          </p>
        </div>
        
        <MonthlyDetectionsTimeline />
      </section>

      {/* Coming Soon Section - Additional Tools */}
      <section className="mt-16">
        <div className="coming-soon">
          <div>
            <MagnifyingGlassIcon className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">More Tools Coming Soon</h3>
            <p className="text-slate-500 max-w-md mx-auto">
              Additional data exploration features will be added to support advanced research workflows.
            </p>
            <div className="mt-6 space-y-2">
              <div className="badge badge-coral">Advanced Filters</div>
              <div className="badge badge-ocean">Data Table View</div>
              <div className="badge badge-coral">Query Builder</div>
              <div className="badge badge-ocean">Export Tools</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}