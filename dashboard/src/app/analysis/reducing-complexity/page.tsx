'use client';

import { CorrelationMatrix } from '@/components/charts/CorrelationMatrix';
import { useCorrelationMatrix } from '@/lib/data/useCorrelationMatrix';

export default function ReducingComplexityPage() {
  const { data: correlationData, loading, error } = useCorrelationMatrix();
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Reducing Complexity
          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl">
            With 56+ acoustic indices, we need to identify which ones provide unique, meaningful information for biodiversity prediction. 
            Here&apos;s how we reduce the complexity while preserving the signal.
          </p>
        </div>

        {/* The Challenge */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-foreground mb-6">The Challenge</h2>
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Too Many Variables, Not Enough Signal</h3>
                <p className="text-muted-foreground mb-4">
                  Our acoustic analysis pipeline generates 56+ indices per hour of audio. Many of these indices are highly correlated, 
                  measuring similar aspects of the soundscape. Using all indices makes 
                  it difficult to identify which acoustic features truly predict biodiversity.
                </p>
                <div className="bg-muted/50 rounded p-4">
                  <div className="text-sm text-muted-foreground">
                    <strong>The numbers:</strong> 56 indices × ~8,700 hours = 487,200 data points to analyze
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Correlation Analysis */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-foreground mb-6">Step 1: Finding Redundant Indices</h2>
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-card-foreground mb-4">Correlation Matrix Analysis</h3>
            <p className="text-muted-foreground mb-4">
              We examine correlations between all acoustic indices. Highly correlated indices (|r| {'>'}0.95) 
              likely measure similar acoustic properties and can be reduced to representative indices.
            </p>
            <div className="bg-muted/30 rounded-lg p-4 text-sm text-muted-foreground mb-6">
              <strong>Method:</strong> Pearson correlation for linear relationships, with threshold-based filtering 
              to remove redundant indices while preserving acoustic diversity.
            </div>
          </div>

          {/* Interactive Correlation Matrix */}
          {loading && (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-2 text-muted-foreground">Loading correlation matrix...</span>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="text-red-800">Error loading correlation data: {error}</div>
            </div>
          )}
          
          {correlationData && (
            <>
              <div className="bg-card rounded-lg border p-6 mb-6">
                <h4 className="font-semibold text-card-foreground mb-3">Key Findings</h4>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {correlationData.statistics.total_indices}
                    </div>
                    <div className="text-muted-foreground">Acoustic indices analyzed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600 mb-1">
                      {correlationData.statistics.high_correlation_pairs}
                    </div>
                    <div className="text-muted-foreground">High correlation pairs (|r| ≥ 0.95)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-amber-600 mb-1">
                      {correlationData.statistics.suggested_removals}
                    </div>
                    <div className="text-muted-foreground">Indices flagged for removal</div>
                  </div>
                </div>
                <p className="text-muted-foreground mt-4 text-center">
                  By removing highly redundant indices, we can reduce our feature space by{' '}
                  <strong className="text-foreground">
                    {Math.round((correlationData.statistics.suggested_removals / correlationData.statistics.total_indices) * 100)}%
                  </strong>{' '}
                  while preserving unique acoustic information.
                </p>
              </div>
              
              <CorrelationMatrix data={correlationData} />
            </>
          )}
        </section>

        {/* PCA Analysis */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-foreground mb-6">Step 2: Principal Component Analysis</h2>
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-card rounded-lg border p-6">
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-2/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-chart-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h4 className="font-medium text-card-foreground mb-2">Scree Plot</h4>
                  <p className="text-sm">Variance explained by each component</p>
                </div>
              </div>
            </div>
            <div className="bg-card rounded-lg border p-6">
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-3/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-chart-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                  </div>
                  <h4 className="font-medium text-card-foreground mb-2">Cumulative Variance</h4>
                  <p className="text-sm">How many components capture 80% of variance?</p>
                </div>
              </div>
            </div>
            <div className="bg-card rounded-lg border p-6">
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-4/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-chart-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                    </svg>
                  </div>
                  <h4 className="font-medium text-card-foreground mb-2">Loadings Heatmap</h4>
                  <p className="text-sm">Which indices contribute to top components?</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-card rounded-lg border p-6">
            <h3 className="text-lg font-semibold text-card-foreground mb-4">Understanding the Components</h3>
            <p className="text-muted-foreground mb-4">
              PCA transforms our 56 correlated indices into uncorrelated principal components. The first few components 
              typically capture most of the acoustic variation in our data. By examining component loadings, we can 
              understand which acoustic properties each component represents.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-muted/30 rounded-lg p-4">
                <h4 className="font-medium text-card-foreground mb-2">Component Interpretation</h4>
                <p className="text-sm text-muted-foreground">
                  Each component represents a different aspect of the acoustic environment - perhaps one captures 
                  temporal complexity, another spectral diversity, and another anthropogenic noise levels.
                </p>
              </div>
              <div className="bg-muted/30 rounded-lg p-4">
                <h4 className="font-medium text-card-foreground mb-2">Dimensionality Goal</h4>
                <p className="text-sm text-muted-foreground">
                  We aim to reduce 56 indices to 3-5 meaningful components that retain 80%+ of the original 
                  acoustic information while being interpretable for biodiversity analysis.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Results Preview */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-foreground mb-6">The Path Forward</h2>
          <div className="bg-gradient-to-r from-chart-1/10 to-chart-2/10 rounded-lg border p-8">
            <div className="max-w-3xl">
              <h3 className="text-xl font-semibold text-card-foreground mb-4">From Complexity to Clarity</h3>
              <p className="text-muted-foreground mb-6">
                Through correlation analysis and PCA, we identify the most informative acoustic indices for 
                biodiversity prediction. This reduced set becomes the foundation for all subsequent analysis - 
                from pattern discovery to predictive modeling.
              </p>
              <div className="flex flex-wrap gap-3">
                <div className="bg-white/80 dark:bg-slate-800/80 rounded-full px-4 py-2 text-sm font-medium">
                  56 indices → 3-5 components
                </div>
                <div className="bg-white/80 dark:bg-slate-800/80 rounded-full px-4 py-2 text-sm font-medium">
                  Remove redundancy
                </div>
                <div className="bg-white/80 dark:bg-slate-800/80 rounded-full px-4 py-2 text-sm font-medium">
                  Preserve signal
                </div>
                <div className="bg-white/80 dark:bg-slate-800/80 rounded-full px-4 py-2 text-sm font-medium">
                  Enable interpretation
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Next Steps */}
        <section>
          <div className="bg-card rounded-lg border p-6">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-card-foreground mb-1">Next: Finding Patterns</h3>
                <p className="text-sm text-muted-foreground">
                  With our reduced set of acoustic indices, we can now explore temporal and spatial patterns 
                  in marine soundscapes and their relationships to biodiversity.
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}