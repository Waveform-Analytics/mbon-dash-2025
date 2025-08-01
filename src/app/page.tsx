'use client'

import { useCoreData } from '@/lib/hooks/useData'

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
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-5xl">
          Marine Biodiversity
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Observatory</span>
        </h1>
        <p className="section-description">
          Explore acoustic monitoring data from the OSA MBON project. Discover species patterns, 
          temporal trends, and environmental correlations across marine ecosystems.
        </p>
      </div>
          
      {/* Metrics Cards */}
      <div className="card-grid gap-6 mb-12">
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-ocean-600 mb-2">
            {metadata?.data_summary.total_detections.toLocaleString() || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">Total Detections</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-coral-500 mb-2">
            {species?.length || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">Species Tracked</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-ocean-600 mb-2">
            {stations?.length || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">Monitoring Stations</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-slate-700 mb-2">
            2018-2021
          </div>
          <div className="text-sm font-medium text-slate-600">Study Period</div>
        </div>
      </div>

      {/* Preview Charts */}
      <div className="card-grid lg:grid-cols-2 gap-8 mb-12">
        <div className="chart-container group">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Species Activity Timeline</h3>
            <span className="badge badge-ocean">Coming Soon</span>
          </div>
          <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
            <div className="text-center">
              <div className="text-4xl mb-2">📊</div>
              <div className="text-slate-500 font-medium">Interactive time series visualization</div>
            </div>
          </div>
        </div>
        
        <div className="chart-container group">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Station Distribution Map</h3>
            <span className="badge badge-coral">Coming Soon</span>
          </div>
          <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
            <div className="text-center">
              <div className="text-4xl mb-2">🗺️</div>
              <div className="text-slate-500 font-medium">Geographic station locations & activity</div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="mb-8 p-6 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center">
            <div className="text-red-500 text-xl mr-3">⚠️</div>
            <div>
              <p className="text-red-800 font-medium">
                Unable to connect to data source
              </p>
              <p className="text-red-600 text-sm mt-1">
                {error.message}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {!error && metadata && (
        <div className="mb-8 p-6 bg-green-50 border border-green-200 rounded-xl">
          <div className="flex items-center">
            <div className="text-green-500 text-xl mr-3">✅</div>
            <div>
              <p className="text-green-800 font-medium">
                Data connection successful
              </p>
              <p className="text-green-600 text-sm mt-1">
                Last updated: {new Date(metadata.generated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Navigation */}
      <div className="card-grid gap-4">
        <a href="/species" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">🐟</div>
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">Species Analysis</h3>
          <p className="text-sm text-slate-600 mt-1">Explore detection patterns and species diversity</p>
        </a>
        
        <a href="/stations" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-coral-300 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">📍</div>
          <h3 className="font-semibold text-slate-900 group-hover:text-coral-700">Station Comparison</h3>
          <p className="text-sm text-slate-600 mt-1">Compare activity across monitoring locations</p>
        </a>
        
        <a href="/temporal" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">📊</div>
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">Temporal Patterns</h3>
          <p className="text-sm text-slate-600 mt-1">Discover trends over time and seasons</p>
        </a>
        
        <a href="/explorer" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-coral-300 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">🔍</div>
          <h3 className="font-semibold text-slate-900 group-hover:text-coral-700">Data Explorer</h3>
          <p className="text-sm text-slate-600 mt-1">Filter and explore the full dataset</p>
        </a>
      </div>
    </div>
  )
}