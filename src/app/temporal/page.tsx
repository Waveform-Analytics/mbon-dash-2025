export default function TemporalPage() {
  return (
    <div className="page-container">
      <div className="mb-8">
        <h1 className="section-heading">Temporal Patterns</h1>
        <p className="section-description">
          Discover seasonal trends, daily patterns, and long-term changes in marine ecosystem activity.
        </p>
      </div>

      <div className="coming-soon">
        <div>
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-2xl font-semibold text-slate-700 mb-2">Temporal Analysis Coming Soon</h2>
          <p className="text-slate-500 max-w-md mx-auto">
            This section will feature time series visualizations showing seasonal patterns, 
            daily activity cycles, year-over-year comparisons, and anomaly detection.
          </p>
          <div className="mt-8 space-y-2">
            <div className="badge badge-ocean">Seasonal Trends</div>
            <div className="badge badge-coral">Daily Patterns</div>
            <div className="badge badge-ocean">Year Comparisons</div>
            <div className="badge badge-coral">Anomaly Detection</div>
          </div>
        </div>
      </div>
    </div>
  )
}