export default function StationsPage() {
  return (
    <div className="page-container">
      <div className="mb-8">
        <h1 className="mb-4">Station Comparison</h1>
        <p className="text-xl text-slate-600">
          Compare monitoring stations across geographic locations, environmental conditions, and species activity.
        </p>
      </div>

      <div className="coming-soon">
        <div>
          <div className="text-6xl mb-4">📍</div>
          <h2 className="text-2xl font-semibold text-slate-700 mb-2">Station Analysis Coming Soon</h2>
          <p className="text-slate-500 max-w-md mx-auto">
            This section will feature an interactive map showing station locations, activity comparisons, 
            environmental correlations, and site-specific species diversity metrics.
          </p>
          <div className="mt-8 space-y-2">
            <div className="badge badge-coral">Interactive Map</div>
            <div className="badge badge-ocean">Activity Comparison</div>
            <div className="badge badge-coral">Environmental Data</div>
            <div className="badge badge-ocean">Site-specific Patterns</div>
          </div>
        </div>
      </div>
    </div>
  )
}