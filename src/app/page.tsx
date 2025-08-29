import { HomepageContent } from './page.content';
import StationMapWrapper from '@/components/StationMapWrapper';
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
import { 
  getServerMetadata, 
  getServerSpecies, 
  getServerStations, 
  getServerDeployments 
} from '@/lib/server-data'

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

export default async function DashboardPage() {
  // Server-side data fetching
  const [metadata, species, stations, deployments] = await Promise.all([
    getServerMetadata(),
    getServerSpecies(), 
    getServerStations(),
    getServerDeployments()
  ]);

  // Process deployment data for stations
  const stationsForMap = deployments ? processStationsForMap(deployments) : [];
  const error = null; // Handle errors gracefully

  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-5xl">
          {HomepageContent.hero.title}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500">{HomepageContent.hero.titleHighlight}</span>
        </h1>
        <p className="section-description">
          {HomepageContent.hero.subtitle}
        </p>
      </div>
          
      {/* Metrics Cards */}
      <div className="card-grid gap-6 mb-12">
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-ocean-600 mb-2">
            {metadata?.data_summary?.total_detections?.toLocaleString() || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">{HomepageContent.metrics.detections}</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-coral-500 mb-2">
            {species?.length || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">{HomepageContent.metrics.species}</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-ocean-600 mb-2">
            {stations?.length || '-'}
          </div>
          <div className="text-sm font-medium text-slate-600">{HomepageContent.metrics.stations}</div>
        </div>
        
        <div className="metrics-card group">
          <div className="text-3xl font-bold text-slate-700 mb-2">
            2018 & 2021
          </div>
          <div className="text-sm font-medium text-slate-600">{HomepageContent.metrics.studyPeriod}</div>
        </div>
      </div>

      {/* Preview Charts */}
      <div className="space-y-8 mb-12">
        {/* Placeholder for future optimized visualizations */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center">
          <h3 className="text-lg font-semibold text-slate-800 mb-2">Visualizations Coming Soon</h3>
          <p className="text-slate-600 text-sm">
            We're building optimized data views for better performance. 
            Check out the Explore section for acoustic index visualizations.
          </p>
        </div>
      </div>
      
      {/* Station Map */}
      <div className="mb-12">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between p-6 pb-4">
            <h3 className="text-lg font-semibold text-slate-900">{HomepageContent.stationMap.title}</h3>
          </div>
          <StationMapWrapper stations={stationsForMap} />
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="mb-8 p-6 bg-red-50 border border-red-200 rounded-xl">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="w-6 h-6 text-red-500 mr-3" />
            <div>
              <p className="text-red-800 font-medium">
                {HomepageContent.statusMessages.connectionError}
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
                {HomepageContent.statusMessages.connectionSuccess}
              </p>
              <p className="text-green-600 text-sm mt-1">
                {HomepageContent.statusMessages.lastUpdated}{new Date(metadata.generated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Quick Navigation */}
      <div className="card-grid gap-4">
        <a href="/acoustic-biodiversity" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <MusicalNoteIcon className="w-8 h-8 text-ocean-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">{HomepageContent.quickNavigation.acousticAnalysis.title}</h3>
          <p className="text-sm text-slate-600 mt-1">{HomepageContent.quickNavigation.acousticAnalysis.description}</p>
        </a>
        
        <a href="/environmental-factors" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-coral-300 hover:shadow-md transition-all">
          <SunIcon className="w-8 h-8 text-coral-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-coral-700">{HomepageContent.quickNavigation.environmentalFactors.title}</h3>
          <p className="text-sm text-slate-600 mt-1">{HomepageContent.quickNavigation.environmentalFactors.description}</p>
        </a>
        
        <a href="/acoustic-glossary" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <BookOpenIcon className="w-8 h-8 text-ocean-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">{HomepageContent.quickNavigation.indexGuide.title}</h3>
          <p className="text-sm text-slate-600 mt-1">{HomepageContent.quickNavigation.indexGuide.description}</p>
        </a>
        
        <a href="/stations" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-coral-300 hover:shadow-md transition-all">
          <MapPinIcon className="w-8 h-8 text-coral-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-coral-700">{HomepageContent.quickNavigation.stationProfiles.title}</h3>
          <p className="text-sm text-slate-600 mt-1">{HomepageContent.quickNavigation.stationProfiles.description}</p>
        </a>
        
        <a href="/explorer" className="group p-6 bg-white rounded-xl border border-slate-200 hover:border-ocean-300 hover:shadow-md transition-all">
          <MagnifyingGlassIcon className="w-8 h-8 text-ocean-500 mb-2" />
          <h3 className="font-semibold text-slate-900 group-hover:text-ocean-700">{HomepageContent.quickNavigation.dataExplorer.title}</h3>
          <p className="text-sm text-slate-600 mt-1">{HomepageContent.quickNavigation.dataExplorer.description}</p>
        </a>
      </div>
    </div>
  )
}