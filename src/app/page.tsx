'use client'

import { useCoreData } from '@/hooks/useData'

export default function DashboardPage() {
  const { metadata, stations, species, loading, error } = useCoreData()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading marine biodiversity data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-slate-200 rounded-lg p-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">
            Marine Biodiversity Dashboard
          </h2>
          <p className="text-lg text-slate-600 mb-8">
            Explore acoustic monitoring data from the OSA MBON project
          </p>
          
          {/* Metrics Cards Placeholder */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="metrics-card">
              <div className="text-2xl font-bold text-ocean-600">
                {metadata?.data_summary.total_detections.toLocaleString() || '-'}
              </div>
              <div className="text-sm text-slate-600">Total Detections</div>
            </div>
            <div className="metrics-card">
              <div className="text-2xl font-bold text-ocean-600">
                {species?.length || '-'}
              </div>
              <div className="text-sm text-slate-600">Species Count</div>
            </div>
            <div className="metrics-card">
              <div className="text-2xl font-bold text-ocean-600">
                {stations?.length || '-'}
              </div>
              <div className="text-sm text-slate-600">Active Stations</div>
            </div>
            <div className="metrics-card">
              <div className="text-2xl font-bold text-ocean-600">
                {metadata ? `${metadata.data_summary.date_range.start.substring(0,4)}-${metadata.data_summary.date_range.end.substring(0,4)}` : '2018-2021'}
              </div>
              <div className="text-sm text-slate-600">Date Range</div>
            </div>
          </div>

          {/* Chart Placeholders */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="chart-container h-64 flex items-center justify-center">
              <div className="text-slate-400">Species Detection Timeline</div>
            </div>
            <div className="chart-container h-64 flex items-center justify-center">
              <div className="text-slate-400">Station Activity Map</div>
            </div>
          </div>

          {error && (
            <div className="mt-8 p-4 bg-red-50 rounded-lg">
              <p className="text-red-800">
                ❌ Error loading data: {error.message}
              </p>
              <p className="text-red-600 text-sm mt-2">
                Make sure your data is uploaded to Cloudflare R2 and NEXT_PUBLIC_DATA_URL is configured.
              </p>
            </div>
          )}
          
          {!error && metadata && (
            <div className="mt-8 p-4 bg-green-50 rounded-lg">
              <p className="text-green-800">
                ✅ Successfully connected to data! Last updated: {new Date(metadata.generated_at).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}