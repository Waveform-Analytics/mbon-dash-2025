import React from 'react';
import { 
  MapPinIcon,
  CalendarIcon,
  BeakerIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { StationMap } from '@/components/maps/StationMap';
import { getServerDeployments, DeploymentMetadata } from '@/lib/server-data';

// Define station colors
const STATION_COLORS = {
  '9M': '#e11d48',   // Rose
  '14M': '#0ea5e9',  // Sky blue  
  '37M': '#f59e0b',  // Amber
} as const;

function getStationColor(stationId: string) {
  return STATION_COLORS[stationId as keyof typeof STATION_COLORS] || '#6b7280';
}

// Interface for processed station data for the map
interface ProcessedStation {
  id: string;
  name: string;
  lat: number;
  lng: number;
  deploymentCount: number;
  years: number[];
  dateRange: {
    start: string;
    end: string;
  };
  color: string;
  description: string;
}

// Process deployment metadata into station data for the map
function processStationsForMap(deployments: DeploymentMetadata[]): ProcessedStation[] {
  // Group deployments by station
  const stationMap = new Map<string, ProcessedStation>();
  
  deployments.forEach(deployment => {
    const stationName = deployment.station;
    
    // Initialize station if we haven't seen it before
    if (!stationMap.has(stationName)) {
      stationMap.set(stationName, {
        id: stationName,
        name: stationName,
        lat: deployment.gps_lat,
        lng: deployment.gps_long,
        deploymentCount: 0,
        years: [],
        dateRange: {
          start: deployment.start_date,
          end: deployment.end_date
        },
        color: getStationColor(stationName),
        description: `Station ${stationName}`
      });
    }
    
    const station = stationMap.get(stationName)!;
    
    // Update the station's aggregate data
    station.deploymentCount += 1;
    
    // Add year if we haven't seen it before
    if (!station.years.includes(deployment.year)) {
      station.years.push(deployment.year);
    }
    
    // Update date range (keep earliest start and latest end)
    if (deployment.start_date < station.dateRange.start) {
      station.dateRange.start = deployment.start_date;
    }
    if (deployment.end_date > station.dateRange.end) {
      station.dateRange.end = deployment.end_date;
    }
  });
  
  // Convert the Map back to an array and sort by station name
  return Array.from(stationMap.values()).sort((a, b) => a.name.localeCompare(b.name));
}

// Loading spinner component
function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-8">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600"></div>
      <span className="ml-3 text-slate-600">Loading station data...</span>
    </div>
  );
}

// Error message component
function ErrorMessage({ error }: { error: string }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-2">
        <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />
        <h3 className="font-semibold">Error Loading Station Data</h3>
      </div>
      <p className="text-red-700 text-sm">{error}</p>
      <p className="text-red-600 text-xs mt-2">
        Please check your internet connection or try refreshing the page.
      </p>
    </div>
  );
}

// Helper function for coordinate formatting
function formatCoordinate(coord: number, type: 'lat' | 'lon'): string {
  const abs = Math.abs(coord);
  const direction = type === 'lat' ? (coord >= 0 ? 'N' : 'S') : (coord >= 0 ? 'E' : 'W');
  return `${abs.toFixed(5)}°${direction}`;
}

export default async function StationsPage() {
  const deployments = await getServerDeployments();
  
  // Process deployment data for the map
  const stationsForMap = deployments ? processStationsForMap(deployments) : [];
  const error = null; // Handle errors gracefully
  const loading = false; // Server-side data is loaded

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
        {deployments && (
          <div className="mt-4 text-sm text-slate-600">
            Station data loaded from deployment metadata • {(JSON.stringify(deployments).length / 1024).toFixed(1)} KB
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && <LoadingSpinner />}
      
      {/* Error State */}
      {error && <ErrorMessage error={error.message} />}

      {/* Content - only show when data is loaded */}
      {deployments && stationsForMap.length > 0 && !loading && !error && (
        <>
          {/* Station Map */}
          <div className="chart-container mb-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <MapPinIcon className="w-5 h-5" />
              Station Locations
            </h2>
            <div className="h-[500px] rounded-lg overflow-hidden border border-slate-200">
              <StationMap stations={stationsForMap} />
            </div>
          </div>

          {/* Station Information Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {stationsForMap.map((station) => (
              <div key={station.id} className="bg-white rounded-xl border border-slate-200 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">{station.name}</h3>
                    <p className="text-sm text-slate-600 mt-1">
                      {station.deploymentCount} deployments
                    </p>
                  </div>
                  <div 
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: station.color }}
                  />
                </div>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between py-2 border-b border-slate-100">
                    <span className="text-slate-600 flex items-center gap-1">
                      <MapPinIcon className="w-4 h-4" />
                      Coordinates
                    </span>
                    <span className="font-medium text-slate-900">
                      {formatCoordinate(station.lat, 'lat')}, {formatCoordinate(station.lng, 'lon')}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between py-2 border-b border-slate-100">
                    <span className="text-slate-600 flex items-center gap-1">
                      <CalendarIcon className="w-4 h-4" />
                      Active Years
                    </span>
                    <span className="font-medium text-slate-900">
                      {station.years.join(', ')}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between py-2 border-b border-slate-100">
                    <span className="text-slate-600 flex items-center gap-1">
                      <BeakerIcon className="w-4 h-4" />
                      Deployments
                    </span>
                    <span className="font-medium text-slate-900">
                      {station.deploymentCount} total
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-2">
                    <span className="text-slate-600">Date Range</span>
                    <span className="font-medium text-slate-900 text-xs">
                      {new Date(station.dateRange.start).getFullYear()} - {new Date(station.dateRange.end).getFullYear()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}