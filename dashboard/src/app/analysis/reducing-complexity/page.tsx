'use client';

import { CorrelationMatrix } from '@/components/charts/CorrelationMatrix';
import { useCorrelationMatrix } from '@/lib/data/useCorrelationMatrix';
import { PCAAnalysis } from '@/components/charts/PCAAnalysis';
import { usePCAAnalysis } from '@/lib/data/usePCAAnalysis';

export default function ReducingComplexityPage() {
  const { data: correlationData, loading, error } = useCorrelationMatrix();
  const { data: pcaData, loading: pcaLoading, error: pcaError } = usePCAAnalysis();
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
          
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-card-foreground mb-4">From Many to Few: Dimensionality Reduction</h3>
            <p className="text-muted-foreground mb-4">
              After removing highly correlated indices, we use Principal Component Analysis (PCA) to find the underlying 
              patterns that explain most of the acoustic variation. This transforms our remaining indices into a smaller 
              set of uncorrelated components that capture the essence of the acoustic environment.
            </p>
            
            <div className="bg-muted/30 rounded-lg p-4 text-sm text-muted-foreground mb-6">
              <strong>Method:</strong> Standardized PCA with sklearn preprocessing. Components are ranked by explained variance, 
              with loadings showing how each original index contributes to each component.
            </div>
          </div>

          {/* PCA Loading State */}
          {pcaLoading && (
            <div className="flex items-center justify-center p-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-2 text-muted-foreground">Loading PCA analysis...</span>
            </div>
          )}
          
          {/* PCA Error State */}
          {pcaError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="text-red-800">Error loading PCA analysis: {pcaError}</div>
            </div>
          )}
          
          {/* Interactive PCA Analysis */}
          {pcaData && (
            <>
              <div className="bg-card rounded-lg border p-6 mb-6">
                <h4 className="font-semibold text-card-foreground mb-3">Key PCA Results</h4>
                <div className="grid md:grid-cols-4 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {pcaData.summary.total_indices}
                    </div>
                    <div className="text-muted-foreground">Original indices</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600 mb-1">
                      {pcaData.summary.components_for_80_percent}
                    </div>
                    <div className="text-muted-foreground">Components for 80% variance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600 mb-1">
                      {pcaData.summary.components_for_90_percent}
                    </div>
                    <div className="text-muted-foreground">Components for 90% variance</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600 mb-1">
                      {Math.round(pcaData.summary.variance_explained_top_5)}%
                    </div>
                    <div className="text-muted-foreground">Top 5 components</div>
                  </div>
                </div>
                
                <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
                  <div className="text-sm text-center">
                    <strong className="text-green-800">Remarkable dimensionality reduction:</strong> Just {' '}
                    <span className="text-lg font-bold text-green-700">
                      {pcaData.summary.components_for_80_percent} component{pcaData.summary.components_for_80_percent === 1 ? '' : 's'}
                    </span>{' '}
                    capture{pcaData.summary.components_for_80_percent === 1 ? 's' : ''} 80% of acoustic variation from {pcaData.summary.total_indices} original indices!
                  </div>
                </div>
              </div>
              
              <PCAAnalysis data={pcaData} />
            </>
          )}
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