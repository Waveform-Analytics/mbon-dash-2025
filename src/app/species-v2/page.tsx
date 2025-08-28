'use client';

/**
 * Species V2 Page - Optimized species timeline using view data
 * 
 * This page demonstrates the dramatic performance improvement of the view-based architecture:
 * - Loads ~1.6KB instead of potentially MB+ of raw detection data
 * - Shows monthly aggregated species detection timelines
 * - Only includes biological species (filters out anthropogenic sounds)
 */

import { useSpeciesTimeline } from '@/lib/hooks/useViewData';
import { SpeciesV2PageContent } from './page.content';

export default function SpeciesV2Page() {
  const { data, loading, error } = useSpeciesTimeline();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-teal-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-gray-700">
              {SpeciesV2PageContent.loading.message}
            </h2>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-teal-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-bold text-red-800 mb-2">
              {SpeciesV2PageContent.error.title}
            </h2>
            <p className="text-red-600 mb-2">
              {SpeciesV2PageContent.error.message}
            </p>
            <p className="text-red-500">
              {error}
            </p>
            <p className="text-sm text-red-500 mt-2">
              {SpeciesV2PageContent.error.details}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.species_timeline || data.species_timeline.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-teal-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
            <h2 className="text-xl font-bold text-yellow-800 mb-2">
              {SpeciesV2PageContent.noData.title}
            </h2>
            <p className="text-yellow-600">
              {SpeciesV2PageContent.noData.message}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-teal-50">
      {/* Header Section */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {SpeciesV2PageContent.header.title}
          </h1>
          <p className="text-gray-600">
            {SpeciesV2PageContent.header.subtitle}
          </p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-8 py-6">
        {/* Performance Indicator */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-semibold text-green-800 mb-2">
            {SpeciesV2PageContent.sections.performance.title}
          </h2>
          <p className="text-green-700">
            {SpeciesV2PageContent.sections.performance.description}
          </p>
          <div className="mt-2 text-sm text-green-600">
            <strong>Data loaded:</strong> ~1.6KB | <strong>Species count:</strong> {data.metadata.total_species} | 
            <strong> Aggregation:</strong> {data.metadata.aggregation_level}
          </div>
        </div>

        {/* Species Timeline Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {SpeciesV2PageContent.sections.timeline.title}
          </h2>
          <p className="text-gray-600 mb-6">
            {SpeciesV2PageContent.sections.timeline.description}
          </p>

          {/* Species Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.species_timeline.map((species) => (
              <div key={species.species_code} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {species.species_name}
                  </h3>
                  <p className="text-sm text-gray-500 mb-2">
                    Code: {species.species_code}
                  </p>
                  <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                    {species.category}
                  </span>
                </div>

                <div className="space-y-3">
                  {/* Detection Summary */}
                  <div>
                    <p className="text-sm font-medium text-gray-700">Total Detections:</p>
                    <p className="text-xl font-bold text-blue-600">{species.total_detections}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-700">Detection Frequency:</p>
                    <p className="text-lg font-semibold text-purple-600">
                      {(species.detection_frequency * 100).toFixed(1)}%
                    </p>
                  </div>

                  {/* Monthly Timeline (simplified visualization) */}
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Timeline:</p>
                    {species.monthly_detections.length > 0 ? (
                      <div className="space-y-1">
                        {species.monthly_detections.slice(0, 3).map((month) => (
                          <div key={month.year_month} className="text-xs text-gray-600">
                            <span className="font-medium">{month.year_month}:</span> {month.detection_count} detections
                            {month.stations.length > 0 && (
                              <span className="text-gray-400"> at {month.stations.join(', ')}</span>
                            )}
                          </div>
                        ))}
                        {species.monthly_detections.length > 3 && (
                          <div className="text-xs text-gray-400">
                            ...and {species.monthly_detections.length - 3} more months
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-400">No monthly data available</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Methodology Section */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {SpeciesV2PageContent.sections.methodology.title}
          </h2>
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
            <p className="text-gray-700 mb-4">
              {SpeciesV2PageContent.sections.methodology.description}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Data Sources:</h3>
                <ul className="text-gray-600 space-y-1">
                  {data.metadata.data_sources.map((source, index) => (
                    <li key={index}>• {source}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Processing Details:</h3>
                <ul className="text-gray-600 space-y-1">
                  <li>• Aggregation: {data.metadata.aggregation_level}</li>
                  <li>• Species included: {data.metadata.total_species}</li>
                  <li>• Generated: {new Date(data.metadata.generated_at).toLocaleString()}</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}