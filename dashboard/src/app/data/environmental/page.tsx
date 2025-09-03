export default function EnvironmentalDataPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Environmental Data
          </h1>
          <p className="text-lg text-muted-foreground">
            Temperature and depth measurements from hydrophone monitoring stations.
          </p>
        </div>

        {/* Coming Soon Content */}
        <div className="flex flex-col items-center justify-center py-16 bg-card rounded-lg border">
          <div className="text-center max-w-md">
            <div className="w-16 h-16 bg-chart-2/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-chart-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-card-foreground mb-3">
              Environmental Analysis Coming Soon
            </h2>
            <p className="text-muted-foreground mb-6">
              We're preparing comprehensive visualizations and analysis tools for temperature and depth data from our monitoring stations.
            </p>
            <div className="text-sm text-muted-foreground">
              <p>This section will include:</p>
              <ul className="mt-2 space-y-1">
                <li>• Temperature trends over time</li>
                <li>• Depth measurements and variations</li>
                <li>• Environmental correlation analysis</li>
                <li>• Interactive data visualization tools</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}