'use client';

/**
 * Acoustic Summary Page (Version 2)
 * 
 * This page loads optimized acoustic analysis data (19.6KB vs 166MB) and displays:
 * - PCA analysis with explained variance
 * - Index categorization by research domain
 * - Station-level acoustic summaries
 * - Performance metrics showing data size improvements
 */

import { useAcousticSummary } from '@/lib/hooks/useViewData';
import { PageContent } from './page.content';

export default function AcousticV2Page() {
  const { data, loading, error } = useAcousticSummary();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="text-gray-600 text-lg">{PageContent.loading.message}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-red-600 mb-4">{PageContent.error.title}</h1>
              <p className="text-gray-600 mb-4">{PageContent.error.message}</p>
              <p className="text-sm text-red-500 bg-red-50 p-3 rounded">{error}</p>
              <p className="text-sm text-gray-500 mt-4">{PageContent.error.suggestion}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-slate-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center text-gray-500">
              <p>{PageContent.noData.message}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Calculate performance improvement
  const originalSizeMB = 166; // Original acoustic_indices.json size
  const currentSizeKB = 19.6; // Current optimized size
  const improvementFactor = Math.round((originalSizeMB * 1024) / currentSizeKB);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="text-center bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">{PageContent.header.title}</h1>
          <p className="text-xl text-gray-600 mb-4">{PageContent.header.subtitle}</p>
          
          {/* Performance Indicator */}
          <div className="bg-green-100 border-l-4 border-green-500 p-4 rounded-r-lg">
            <div className="flex items-center justify-center space-x-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-700">{improvementFactor}x</div>
                <div className="text-sm text-green-600">Performance Improvement</div>
              </div>
              <div className="text-gray-400">•</div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">{data.metadata.total_indices}</div>
                <div className="text-sm text-blue-600">Acoustic Indices</div>
              </div>
              <div className="text-gray-400">•</div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-700">{data.pca_analysis.components.length}</div>
                <div className="text-sm text-purple-600">PCA Components</div>
              </div>
            </div>
          </div>
        </div>

        {/* PCA Analysis Section */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">{PageContent.pca.title}</h2>
          <p className="text-gray-600 mb-6">{PageContent.pca.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* PCA Components */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-4">{PageContent.pca.components.title}</h3>
              <div className="space-y-3">
                {data.pca_analysis.components.map((component, index) => (
                  <div key={component} className="bg-blue-50 p-3 rounded-lg">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-blue-800">{component}</span>
                      <span className="text-blue-600">
                        {(data.pca_analysis.explained_variance[index] * 100).toFixed(1)}% variance
                      </span>
                    </div>
                    <div className="mt-1">
                      <div className="w-full bg-blue-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${data.pca_analysis.explained_variance[index] * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Total Variance Explained */}
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-4">{PageContent.pca.variance.title}</h3>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-center mb-4">
                  <div className="text-3xl font-bold text-purple-700">
                    {(data.pca_analysis.explained_variance.reduce((sum, val) => sum + val, 0) * 100).toFixed(1)}%
                  </div>
                  <div className="text-purple-600">{PageContent.pca.variance.subtitle}</div>
                </div>
                <p className="text-sm text-gray-600">{PageContent.pca.variance.description}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Index Categories Section */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">{PageContent.categories.title}</h2>
          <p className="text-gray-600 mb-6">{PageContent.categories.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(data.index_categories).map(([categoryName, categoryData]) => (
              <div key={categoryName} className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-3 capitalize">
                  {categoryName.replace(/_/g, ' ')}
                </h3>
                <p className="text-sm text-gray-600 mb-4">{categoryData.description}</p>
                
                <div className="mb-4">
                  <div className="text-2xl font-bold text-indigo-600">
                    {categoryData.indices.length}
                  </div>
                  <div className="text-sm text-indigo-500">indices in category</div>
                </div>
                
                {categoryData.summary_stats && (
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Data availability:</span>
                      <span className="font-medium">
                        {(categoryData.summary_stats.data_availability * 100).toFixed(0)}%
                      </span>
                    </div>
                    {categoryData.summary_stats.avg_correlation && (
                      <div className="flex justify-between">
                        <span className="text-gray-500">Avg correlation:</span>
                        <span className="font-medium">
                          {categoryData.summary_stats.avg_correlation.toFixed(2)}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Station Summaries Section */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">{PageContent.stations.title}</h2>
          <p className="text-gray-600 mb-6">{PageContent.stations.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {data.acoustic_summary.map((stationData) => (
              <div key={stationData.station} className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg p-6">
                <h3 className="text-xl font-bold text-cyan-800 mb-4">
                  Station {stationData.station}
                </h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-cyan-600">Total Records:</span>
                    <span className="font-semibold text-cyan-800">
                      {stationData.temporal_stats.total_records.toLocaleString()}
                    </span>
                  </div>
                  
                  {stationData.temporal_stats.date_range.start && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-cyan-600">Start Date:</span>
                        <span className="font-semibold text-cyan-800">
                          {new Date(stationData.temporal_stats.date_range.start).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-cyan-600">End Date:</span>
                        <span className="font-semibold text-cyan-800">
                          {new Date(stationData.temporal_stats.date_range.end!).toLocaleDateString()}
                        </span>
                      </div>
                    </>
                  )}
                  
                  <div className="text-sm text-cyan-600 mt-4">
                    {Object.keys(stationData.acoustic_metrics).length} acoustic indices measured
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Metadata Footer */}
        <div className="bg-gray-100 rounded-lg p-6 text-center">
          <div className="text-sm text-gray-600 space-y-2">
            <div>
              <strong>Generated:</strong> {new Date(data.metadata.generated_at).toLocaleString()}
            </div>
            <div>
              <strong>Records Processed:</strong> {data.metadata.total_records_processed.toLocaleString()}
            </div>
            <div>
              <strong>Stations:</strong> {data.metadata.stations_included.join(', ')}
            </div>
            <div className="text-xs text-gray-500 mt-4">
              Version {data.metadata.version} • Generated by {data.metadata.generator}
            </div>
          </div>
        </div>
        
      </div>
    </div>
  );
}