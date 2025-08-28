'use client';

/**
 * Stations V2 Page - Optimized version using view data
 * 
 * This page demonstrates the new view-based architecture:
 * - Loads ~4.5KB instead of 159MB+ 
 * - Uses optimized station_overview.json from CDN
 * - Maintains all functionality while improving performance
 */

import { useStationOverview } from '@/lib/hooks/useViewData';
import { StationsV2PageContent } from './page.content';

export default function StationsV2Page() {
  const { data, loading, error } = useStationOverview();

  if (loading) {
    return (
      <main data-testid="stations-v2-page" className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          {StationsV2PageContent.header.title}
        </h1>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">{StationsV2PageContent.loading.message}</p>
            <p className="text-sm text-gray-500 mt-2">{StationsV2PageContent.loading.details}</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main data-testid="stations-v2-page" className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          {StationsV2PageContent.header.title}
        </h1>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-2">
            {StationsV2PageContent.error.title}
          </h2>
          <p className="text-red-700 mb-2">{StationsV2PageContent.error.message}</p>
          <p className="text-red-600">{error}</p>
          <p className="text-sm text-red-600 mt-4">{StationsV2PageContent.error.retry}</p>
        </div>
      </main>
    );
  }

  if (!data || data.stations.length === 0) {
    return (
      <main data-testid="stations-v2-page" className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          {StationsV2PageContent.header.title}
        </h1>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-700 mb-2">
            {StationsV2PageContent.empty.title}
          </h2>
          <p className="text-gray-600">{StationsV2PageContent.empty.message}</p>
        </div>
      </main>
    );
  }

  return (
    <main data-testid="stations-v2-page" className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {StationsV2PageContent.header.title}
        </h1>
        <p className="text-gray-600">{StationsV2PageContent.header.subtitle}</p>
      </div>

      {/* Station Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {data.stations.map((station) => (
          <div key={station.id} className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {station.name}
            </h2>
            
            {/* Coordinates */}
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 mb-1">
                {StationsV2PageContent.stats.coordinates}
              </h3>
              <p className="text-sm text-gray-600">
                {station.coordinates.lat.toFixed(4)}, {station.coordinates.lon.toFixed(4)}
              </p>
            </div>

            {/* Summary Statistics */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {station.summary_stats.total_detections.toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">{StationsV2PageContent.stats.detections}</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">
                  {station.summary_stats.species_count}
                </p>
                <p className="text-sm text-gray-600">{StationsV2PageContent.stats.species}</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-purple-600">
                  {station.summary_stats.recording_hours.toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">{StationsV2PageContent.stats.hours}</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-orange-600">
                  {station.deployments.length}
                </p>
                <p className="text-sm text-gray-600">{StationsV2PageContent.stats.deployments}</p>
              </div>
            </div>

            {/* Years Active */}
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">Active Years</h3>
              <div className="flex flex-wrap gap-1">
                {station.summary_stats.years_active.map((year) => (
                  <span 
                    key={year}
                    className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
                  >
                    {year}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Metadata */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Data Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="font-medium text-gray-700">{StationsV2PageContent.metadata.generated}</p>
            <p className="text-gray-600">
              {new Date(data.metadata.generated_at).toLocaleDateString()}
            </p>
          </div>
          <div>
            <p className="font-medium text-gray-700">{StationsV2PageContent.metadata.stations}</p>
            <p className="text-gray-600">{data.metadata.total_stations}</p>
          </div>
          <div>
            <p className="font-medium text-gray-700">{StationsV2PageContent.metadata.sources}</p>
            <p className="text-gray-600">{data.metadata.data_sources.join(', ')}</p>
          </div>
        </div>
      </div>
    </main>
  );
}