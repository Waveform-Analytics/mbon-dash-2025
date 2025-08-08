'use client';

import { 
  MapPinIcon,
  CalendarIcon,
  BeakerIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { StationMap } from '@/components/maps/StationMap';

// Station metadata from deployment file
const STATION_INFO = {
  '9M': {
    name: '9M',
    lat: 32.21162,
    lng: -80.90520,
    deploymentCount: 9, // 4 in 2018 + 5 in 2021
    years: [2018, 2021],
    dateRange: {
      start: '2017-10-24',
      end: '2022-03-02'
    },
    depth: 5.4,
    color: '#3B82F6', // blue
    deployments: {
      2018: 4,
      2021: 5
    },
    description: 'Northwestern station in May River'
  },
  '14M': {
    name: '14M',
    lat: 32.22732,
    lng: -80.87745,
    deploymentCount: 8, // 4 in 2018 + 4 in 2021
    years: [2018, 2021],
    dateRange: {
      start: '2017-10-24',
      end: '2022-03-02'
    },
    depth: 7.1,
    color: '#10B981', // green
    deployments: {
      2018: 4,
      2021: 4
    },
    description: 'Northern station, deepest deployment site'
  },
  '37M': {
    name: '37M',
    lat: 32.19453,
    lng: -80.79223,
    deploymentCount: 8, // 4 in 2018 + 4 in 2021
    years: [2018, 2021],
    dateRange: {
      start: '2017-10-24',
      end: '2022-03-02'
    },
    depth: 5.3,
    color: '#F59E0B', // amber
    deployments: {
      2018: 4,
      2021: 4
    },
    description: 'Eastern station, closest to ocean inlet'
  }
};

export default function StationsPage() {
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
      </div>

      {/* Station Map */}
      <div className="chart-container mb-8">
        <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <MapPinIcon className="w-5 h-5" />
          Station Locations
        </h2>
        <div className="h-[500px] rounded-lg overflow-hidden border border-slate-200">
          <StationMap stations={Object.values(STATION_INFO)} />
        </div>
      </div>

      {/* Station Information Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {Object.entries(STATION_INFO).map(([id, station]) => (
          <div key={id} className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-900">Station {station.name}</h3>
                <p className="text-sm text-slate-600 mt-1">{station.description}</p>
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
                  {station.lat.toFixed(5)}°N, {Math.abs(station.lng).toFixed(5)}°W
                </span>
              </div>
              
              <div className="flex items-center justify-between py-2 border-b border-slate-100">
                <span className="text-slate-600 flex items-center gap-1">
                  <BeakerIcon className="w-4 h-4" />
                  Depth
                </span>
                <span className="font-medium text-slate-900">
                  {station.depth} meters
                </span>
              </div>
              
              <div className="flex items-center justify-between py-2">
                <span className="text-slate-600 flex items-center gap-1">
                  <CalendarIcon className="w-4 h-4" />
                  Deployments
                </span>
                <span className="font-medium text-slate-900">
                  {station.deployments[2018] + station.deployments[2021]} total
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Deployment Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
        <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center gap-2">
          <CalendarIcon className="w-5 h-5" />
          Deployment Summary
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-blue-800 mb-3">2018 Deployments</h4>
            <ul className="space-y-2 text-sm text-blue-700">
              <li>• <strong>Period 1:</strong> Oct 2017 - Jan 2018 (Winter)</li>
              <li>• <strong>Period 2:</strong> Jan - Apr 2018 (Spring)</li>
              <li>• <strong>Period 3:</strong> Apr - Jul 2018 (Summer)</li>
              <li>• <strong>Period 4:</strong> Jul - Oct 2018 (Fall)</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-800 mb-3">2021 Deployments</h4>
            <ul className="space-y-2 text-sm text-blue-700">
              <li>• <strong>Period 1:</strong> Oct 2020 - Jan 2021 (Winter)</li>
              <li>• <strong>Period 2:</strong> Jan - Apr 2021 (Spring)</li>
              <li>• <strong>Period 3:</strong> Apr - Jul 2021 (Summer)</li>
              <li>• <strong>Period 4:</strong> Jul - Oct 2021 (Fall)</li>
              <li>• <strong>Period 5:</strong> Oct 2021 - Mar 2022 (Winter/Spring)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Environmental Conditions */}
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

      {/* Data Notes */}
      <div className="mt-8 p-4 bg-slate-100 rounded-lg">
        <h4 className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
          <InformationCircleIcon className="w-4 h-4" />
          Data Collection Notes
        </h4>
        <ul className="text-sm text-slate-600 space-y-1">
          <li>• Hydrophones deployed at approximately 0.2m above seafloor</li>
          <li>• Continuous recording with 2-hour manual annotation samples</li>
          <li>• Environmental data collected throughout deployment periods</li>
          <li>• Station codes (9M, 14M, 37M) represent distance markers in the estuary</li>
        </ul>
      </div>
    </div>
  );
}