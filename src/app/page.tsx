'use client'

import { useMemo } from 'react';
import { useCoreData, useDeploymentMetadata, useTimelineData, DeploymentMetadata } from '@/lib/hooks/useData'
import { StationMap } from '@/components/maps/StationMap';
import { SpeciesActivityHeatmap } from '@/components/charts/SpeciesActivityHeatmap';
import { 
  MusicalNoteIcon, 
  SunIcon, 
  BookOpenIcon, 
  MapPinIcon, 
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

// Define what processed station data will look like
// Export it so other files can import and use it
export interface ProcessedStation {
  name: string;              // Station name (e.g., "9M")
  lat: number;               // Latitude
  lng: number;               // Longitude (note: we rename from "long" to "lng")
  deploymentCount: number;   // Number of equipment deployments at this location
  years: number[];           // Years with deployments
  dateRange: {              // Overall date range for this station
    start: string;
    end: string;
  };
  // Additional summary fields can be added as needed
}

// This function processes the raw deployment data into station summaries
function processStationsForMap(deployments: DeploymentMetadata[]): ProcessedStation[] {
  // A Map is like an object but better for grouping data
  // The key will be the station name, the value will be our processed data
  const stationMap = new Map<string, ProcessedStation>();
  
  // Loop through each deployment record
  deployments.forEach(deployment => {
    const stationName = deployment.station;
    
    // If we haven't seen this station before, create a new entry
    if (!stationMap.has(stationName)) {
      stationMap.set(stationName, {
        name: stationName,
        lat: deployment.gps_lat,
        lng: deployment.gps_long,  // Note: renaming "long" to "lng"
        deploymentCount: 0,
        years: [],
        dateRange: {
          start: deployment.start_date,
          end: deployment.end_date
        }
      });
    }
    
    // Get the existing station data
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

export default function DashboardPage() {
  // Existing data fetching
  const { metadata, stations, species, loading, error } = useCoreData()
  
  // NEW: Fetch deployment metadata
  const { 
    data: deployments, 
    loading: deploymentsLoading, 
    error: deploymentsError 
  } = useDeploymentMetadata();
  
  // NEW: Fetch timeline data for heatmap
  const {
    detections,
    speciesMapping,
    deploymentMetadata,
    loading: timelineLoading,
    error: timelineError
  } = useTimelineData();
  
  // NEW: Process the deployment data for the map
  // useMemo prevents recalculating on every render
  const stationsForMap = useMemo(() => {
    if (!deployments) return [];
    return processStationsForMap(deployments);
  }, [deployments]);  // Only recalculate if deployments change
  
  // Combine loading states
  const isLoading = loading || deploymentsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading marine biodiversity data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-5xl">
          Marine Biodiversity
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Observatory</span>
        </h1>
        <p className="section-description">
          Exploring relationships between computed acoustic indices and species presence using data collected at three
          stations in May River, South Carolina.
        </p>
      </div>
          
      {/* Metrics Cards */}
      <div className="card-grid gap-6 mb-12">
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-ocean-600 mb-2">
            {metadata?.data_summary.total_detections.toLocaleString() || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">Total Detections</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-coral-500 mb-2">
            {species?.length || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">Species Tracked</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-ocean-600 mb-2">
            {stations?.length || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">Monitoring Stations</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-slate-700 mb-2">
            2018-2021
          </div>
          <div className="text-sm font-medium text-slate-600">Study Period</div>
        </div>
      </div>

      {/* Preview Charts */}
      <div className="card-grid lg:grid-cols-1 gap-8 mb-12">
        {/* Species Activity Heatmap - Full width */}
        <div className="chart-container group">
          {detections && detections.length > 0 ? (
            <SpeciesActivityHeatmap
              detections={detections}
              speciesMapping={speciesMapping}
              deploymentMetadata={deploymentMetadata || []}
              height={400}
              topSpeciesCount={10}
            />
          ) : timelineLoading ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900">Species Activity Timeline</h3>
                <span className="badge badge-ocean">Loading...</span>
              </div>
              <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600 mx-auto"></div>
                  <div className="text-slate-500 font-medium mt-4">Loading species detection data...</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900">Species Activity Timeline</h3>
                <span className="badge badge-red">No Data</span>
              </div>
              <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
                <div className="text-center">
                  <ChartBarIcon className="w-16 h-16 text-slate-400 mx-auto mb-2" />
                  <div className="text-slate-500 font-medium">No detection data available</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Station Map - Separate section */}
      <div className="card-grid lg:grid-cols-1 gap-8 mb-12">
        <div className="chart-container group">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Station Distribution Map</h3>
            {deploymentsLoading && (
              <span className="badge badge-ocean">Loading...</span>
            )}
          </div>
          
          {/* Show the map if we have data, otherwise show placeholder */}
          {stationsForMap.length > 0 ? (
            <StationMap stations={stationsForMap} />
          ) : deploymentsLoading ? (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600 mx-auto"></div>
                <div className="text-slate-500 font-medium mt-4">Loading station locations...</div>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
              <div className="text-center">
                <MapPinIcon className="w-16 h-16 text-slate-400 mx-auto mb-2" />
                <div className="text-slate-500 font-medium">No station data available</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="mb-8 p-6 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="w-6 h-6 text-red-500 mr-3" />
            <div>
              <p className="text-red-800 font-medium">
                Unable to connect to data source
              </p>
              <p className="text-red-600 text-sm mt-1">
                {error.message}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {!error && metadata && (
        <div className="mb-8 p-6 bg-green-50 border border-green-200 rounded-xl">
          <div className="flex items-center">
            <CheckCircleIcon className="w-6 h-6 text-green-500 mr-3" />
            <div>
              <p className="text-green-800 font-medium">
                Data connection successful
              </p>
              <p className="text-green-600 text-sm mt-1">
                Last updated: {new Date(metadata.generated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Navigation */}
      <div className="card-grid gap-4">
        <a href="/acoustic-biodiversity" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <MusicalNoteIcon className="w-8 h-8 text-ocean-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">Acoustic Analysis</h3>
          <p className="text-sm text-slate-600 mt-1">Which acoustic indices best predict marine biodiversity?</p>
        </a>
        
        <a href="/environmental-factors" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-coral-300 hover:shadow-md transition-all">
          <SunIcon className="w-8 h-8 text-coral-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-coral-700">Environmental Factors</h3>
          <p className="text-sm text-slate-600 mt-1">How do temperature, depth, and seasonality affect indices?</p>
        </a>
        
        <a href="/acoustic-glossary" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <BookOpenIcon className="w-8 h-8 text-ocean-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">Index Guide</h3>
          <p className="text-sm text-slate-600 mt-1">Understanding acoustic indices and their biological meaning</p>
        </a>
        
        <a href="/stations" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-coral-300 hover:shadow-md transition-all">
          <MapPinIcon className="w-8 h-8 text-coral-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-coral-700">Station Profiles</h3>
          <p className="text-sm text-slate-600 mt-1">Spatial context and deployment details for 9M, 14M, 37M</p>
        </a>
        
        <a href="/explorer" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <MagnifyingGlassIcon className="w-8 h-8 text-ocean-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">Data Explorer</h3>
          <p className="text-sm text-slate-600 mt-1">Filter and explore the full dataset</p>
        </a>
      </div>
    </div>
  )
}