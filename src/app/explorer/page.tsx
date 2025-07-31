export default function ExplorerPage() {
  return (
    <div className="page-container">
      <div className="mb-8">
        <h1 className="section-heading">Data Explorer</h1>
        <p className="section-description">
          Filter, search, and export the complete marine biodiversity dataset with advanced query tools.
        </p>
      </div>

      <div className="coming-soon">
        <div>
          <div className="text-6xl mb-4">🔍</div>
          <h2 className="text-2xl font-semibold text-slate-700 mb-2">Data Explorer Coming Soon</h2>
          <p className="text-slate-500 max-w-md mx-auto">
            This section will feature advanced filtering tools, data table views, 
            custom query builder, and export functionality for researchers and analysts.
          </p>
          <div className="mt-8 space-y-2">
            <div className="badge badge-coral">Advanced Filters</div>
            <div className="badge badge-ocean">Data Table View</div>
            <div className="badge badge-coral">Query Builder</div>
            <div className="badge badge-ocean">Export Tools</div>
          </div>
        </div>
      </div>
    </div>
  )
}