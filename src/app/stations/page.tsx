'use client';

import { 
  MapPinIcon,
  CalendarIcon,
  BeakerIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { StationMap } from '@/components/maps/StationMap';
import { useStationOverview } from '@/lib/hooks/useViewData';

// Loading spinner component
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600"></div>
    </div>
  );
}

// Error display component
function ErrorMessage({ error }: { error: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
      <div className="flex items-center gap-2 text-red-800 mb-2">
        <ExclamationTriangleIcon className="w-5 h-5" />
        <h3 className="font-semibold">Error Loading Station Data</h3>
      </div>
      <p className="text-red-700 text-sm">{error}</p>
      <p className="text-red-600 text-xs mt-2">
        Please check your internet connection or try refreshing the page.
      </p>
    </div>
  );
}

// Helper function to determine station color based on ID
function getStationColor(stationId: string): string {
  const colors = {
    '9M': '#3B82F6',   // blue
    '14M': '#10B981',  // green  
    '37M': '#F59E0B',  // amber
  };
  return colors[stationId as keyof typeof colors] || '#6B7280';
}

// Helper function to format coordinates
function formatCoordinate(coord: number, type: 'lat' | 'lon'): string {
  const abs = Math.abs(coord);
  const direction = type === 'lat' ? (coord >= 0 ? 'N' : 'S') : (coord >= 0 ? 'E' : 'W');
  return `${abs.toFixed(5)}°${direction}`;
}

export default function StationsPage() {
  const { data, loading, error } = useStationOverview();

  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          Monitoring
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Stations</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          Three hydrophone monitoring stations in May River, South Carolina. 
          Data collected during 2018 and 2021 deployment periods.
        </p>
        
        {/* Performance indicator */}
        {data && (
          <div className="mt-4 text-sm text-slate-600">
            Station data loaded from optimized view • {(JSON.stringify(data).length / 1024).toFixed(1)} KB
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner />}
      
      {/* Error State */}
      {error && <ErrorMessage error={error} />}

      {/* Content - only show when data is loaded */}
      {data && !loading && !error && (
        <>
          {/* Station Map */}
          <div className="chart-container mb-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <MapPinIcon className="w-5 h-5" />
              Station Locations
            </h2>
            <div className="h-[500px] rounded-lg overflow-hidden border border-slate-200">
              <StationMap 
                stations={data.stations.map(station => ({
                  id: station.id,
                  name: station.name,
                  lat: station.coordinates.lat,
                  lng: station.coordinates.lon,
                  deploymentCount: station.deployments.length,
                  years: station.summary_stats.years_active,
                  color: getStationColor(station.id),
                  description: `Station ${station.id} - ${station.summary_stats.total_detections.toLocaleString()} detections`
                }))} 
              />
            </div>
          </div>

          {/* Station Information Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {data.stations.map((station) => (
              <div key={station.id} className="bg-white rounded-xl border border-slate-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">{station.name}</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      {station.summary_stats.total_detections.toLocaleString()} total detections
                    </p>
                  </div>
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: getStationColor(station.id) }}
                  />
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between py-2 border-b border-slate-100">
                    <span className="text-slate-600 flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4" />
                      Coordinates
                    </span>
                    <span className="font-medium text-slate-900">
                      {formatCoordinate(station.coordinates.lat, 'lat')}, {formatCoordinate(station.coordinates.lon, 'lon')}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between py-2 border-b border-slate-100">
                    <span className="text-slate-600 flex items-center gap-1">
                      <BeakerIcon className="w-4 h-4" />
                      Recording Hours
                    </span>
                    <span className="font-medium text-slate-900">
                      {station.summary_stats.recording_hours.toLocaleString()} hours
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between py-2 border-b border-slate-100">
                    <span className="text-slate-600 flex items-center gap-1">
                      <CalendarIcon className="w-4 h-4" />
                      Deployments
                    </span>
                    <span className="font-medium text-slate-900">
                      {station.deployments.length} total
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2">
                    <span className="text-slate-600">Species Detected</span>
                    <span className="font-medium text-slate-900">
                      {station.summary_stats.species_count} species
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Deployment Timeline */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
            <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
              <CalendarIcon className="w-5 h-5" />
              Deployment Timeline
            </h3>
            
            <div className="space-y-6">
              {data.stations.map((station) => (
                <div key={station.id} className="border-l-4 border-blue-300 pl-4">
                  <h4 className="font-medium text-blue-800 mb-2">{station.name}</h4>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {station.deployments
                      .filter(dep => dep.start && dep.end)
                      .sort((a, b) => new Date(a.start!).getTime() - new Date(b.start!).getTime())
                      .map((deployment, index) => {
                        const start = new Date(deployment.start!);
                        const end = new Date(deployment.end!);
                        const startFormatted = start.toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'short'
                        });
                        const endFormatted = end.toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'short' 
                        });
                        
                        return (
                          <div key={deployment.deployment_id || index} className="text-xs text-blue-700 bg-blue-100 px-2 py-1 rounded">
                            {startFormatted} - {endFormatted}
                          </div>
                        );
                      })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Environmental Conditions (Static for now) */}
          <div className="chart-container">
            <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <BeakerIcon className="w-5 h-5" />
              Environmental Conditions
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-slate-50 p-4 rounded-lg">
                <h4 className="font-medium text-slate-800 mb-3">Temperature Range</h4>
                <p className="text-sm text-slate-600 mb-2">
                  Water temperatures across deployments ranged from approximately:
                </p>
                <ul className="text-sm text-slate-700 space-y-1">
                  <li>• <strong>Winter:</strong> 10-13°C</li>
                  <li>• <strong>Spring:</strong> 17-21°C</li>
                  <li>• <strong>Summer:</strong> 29-31°C</li>
                  <li>• <strong>Fall:</strong> 22-25°C</li>
                </ul>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-lg">
                <h4 className="font-medium text-slate-800 mb-3">Salinity Variation</h4>
                <p className="text-sm text-slate-600 mb-2">
                  Salinity measurements showed tidal and seasonal variation:
                </p>
                <ul className="text-sm text-slate-700 space-y-1">
                  <li>• <strong>Range:</strong> 17-35 ppt</li>
                  <li>• <strong>Highest:</strong> Summer months (low freshwater input)</li>
                  <li>• <strong>Lowest:</strong> Following rain events</li>
                  <li>• <strong>Pattern:</strong> Tidal influence at all stations</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Data Summary */}
          <div className="mt-8 p-4 bg-slate-100 rounded-lg">
            <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <InformationCircleIcon className="w-4 h-4" />
              Data Summary
            </h4>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-slate-600">
              <div>
                <strong>Total Stations:</strong> {data.metadata.total_stations}
              </div>
              <div>
                <strong>Total Detections:</strong> {data.stations.reduce((sum, s) => sum + s.summary_stats.total_detections, 0).toLocaleString()}
              </div>
              <div>
                <strong>Total Recording Hours:</strong> {data.stations.reduce((sum, s) => sum + s.summary_stats.recording_hours, 0).toLocaleString()}
              </div>
              <div>
                <strong>Data Generated:</strong> {new Date(data.metadata.generated_at).toLocaleDateString()}
              </div>
            </div>
            <ul className="text-sm text-slate-600 space-y-1 mt-3">
              <li>• Hydrophones deployed at approximately 0.2m above seafloor</li>
              <li>• Continuous recording with 2-hour manual annotation samples</li>
              <li>• Station codes (9M, 14M, 37M) represent distance markers in the estuary</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}