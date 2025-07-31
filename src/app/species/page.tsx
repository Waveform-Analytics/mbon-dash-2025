export default function SpeciesPage() {
  return (
    <div className="page-container">
      <div className="mb-8">
        <h1 className="mb-4">Species Analysis</h1>
        <p className="text-xl text-slate-600">
          Explore species detection patterns, diversity, and behavioral insights across the monitoring network.
        </p>
      </div>

      <div className="coming-soon">
        <div>
          <div className="text-6xl mb-4">🐟</div>
          <h2 className="text-2xl font-semibold text-slate-700 mb-2">Species Analysis Coming Soon</h2>
          <p className="text-slate-500 max-w-md mx-auto">
            This section will feature interactive visualizations showing species detection frequencies, 
            temporal activity patterns, co-occurrence analysis, and diversity metrics.
          </p>
          <div className="mt-8 space-y-2">
            <div className="badge badge-ocean">Detection Rankings</div>
            <div className="badge badge-coral">Temporal Activity</div>
            <div className="badge badge-ocean">Species Co-occurrence</div>
            <div className="badge badge-coral">Diversity Analysis</div>
          </div>
        </div>
      </div>
    </div>
  )
}