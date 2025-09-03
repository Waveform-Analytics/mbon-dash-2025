export default function AnalysisOverviewPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Analysis Overview
          </h1>
          <p className="text-lg text-muted-foreground">
            Systematic exploration of acoustic indices and marine biodiversity patterns.
          </p>
        </div>

        {/* Coming Soon Content */}
        <div className="flex flex-col items-center justify-center py-16 bg-card rounded-lg border">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-chart-1/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-chart-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-card-foreground mb-3">
              Analysis Methodology Coming Soon
            </h2>
            <p className="text-muted-foreground mb-6">
              We're building comprehensive analysis tools and visualizations to explore the relationships between acoustic indices and marine biodiversity.
            </p>
            <div className="text-sm text-muted-foreground">
              <p>This section will include:</p>
              <ul className="mt-2 space-y-1">
                <li>• Progressive analysis pipeline</li>
                <li>• Statistical methodology overview</li>
                <li>• Feature reduction techniques</li>
                <li>• Predictive modeling approaches</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}