'use client';

import { useMemo, useState } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { AcousticIndicesDistributionsData, IndexDistributions } from '@/types/data';

interface FilterState {
  stations: string[];
  bandwidth: string;
  searchTerm: string;
  category: string;
}

interface AcousticIndicesSmallMultiplesProps {
  data: AcousticIndicesDistributionsData;
  className?: string;
}

// Station colors for consistent visualization
const STATION_COLORS = {
  '9M': '#2563eb',   // Blue
  '14M': '#dc2626',  // Red  
  '37M': '#059669',  // Green
};

export default function AcousticIndicesSmallMultiples({ 
  data, 
  className = '' 
}: AcousticIndicesSmallMultiplesProps) {
  const [filters, setFilters] = useState<FilterState>({
    stations: data.summary.stations,
    bandwidth: '8kHz',
    searchTerm: '',
    category: 'All',
  });

  // Filter and prepare indices data
  const filteredIndices = useMemo(() => {
    const indices = Object.keys(data.distributions);
    
    return indices.filter(indexName => {
      // Search filter
      if (filters.searchTerm && !indexName.toLowerCase().includes(filters.searchTerm.toLowerCase())) {
        return false;
      }
      
      // Category filter
      const indexMeta = data.indices_metadata[indexName];
      if (filters.category !== 'All' && indexMeta?.category !== filters.category) {
        return false;
      }
      
      // Check if index has data for selected stations and bandwidth
      const indexDistributions = data.distributions[indexName];
      const hasDataForSelectedStations = filters.stations.some(station => {
        const key = `${station}_${filters.bandwidth}`;
        return indexDistributions[key] && indexDistributions[key].count > 0;
      });
      
      return hasDataForSelectedStations;
    });
  }, [data, filters]);

  // Prepare chart data for each index
  const prepareChartData = (indexName: string, distributions: IndexDistributions) => {
    return filters.stations
      .map(station => {
        const key = `${station}_${filters.bandwidth}`;
        const stationData = distributions[key];
        
        if (!stationData || stationData.count === 0) {
          return null;
        }
        
        return {
          id: station,
          color: STATION_COLORS[station as keyof typeof STATION_COLORS],
          data: stationData.x.map((x, i) => ({
            x,
            y: stationData.y[i]
          }))
        };
      })
      .filter(Boolean) as Array<{
        id: string;
        color: string;
        data: Array<{x: number; y: number}>;
      }>;
  };

  // Get unique categories for filter
  const categories = useMemo(() => {
    const cats = new Set(['All']);
    Object.values(data.indices_metadata).forEach(meta => {
      if (meta.category && meta.category !== 'Unknown') {
        cats.add(meta.category);
      }
    });
    return Array.from(cats).sort();
  }, [data.indices_metadata]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Station Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stations
            </label>
            <div className="space-y-1">
              {data.summary.stations.map(station => (
                <label key={station} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={filters.stations.includes(station)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setFilters(prev => ({
                          ...prev,
                          stations: [...prev.stations, station]
                        }));
                      } else {
                        setFilters(prev => ({
                          ...prev,
                          stations: prev.stations.filter(s => s !== station)
                        }));
                      }
                    }}
                    className="mr-2 rounded"
                  />
                  <span 
                    className="text-sm font-medium"
                    style={{ color: STATION_COLORS[station as keyof typeof STATION_COLORS] }}
                  >
                    {station}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Bandwidth Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bandwidth
            </label>
            <select
              value={filters.bandwidth}
              onChange={(e) => setFilters(prev => ({ ...prev, bandwidth: e.target.value }))}
              className="w-full p-2 border rounded-md text-sm"
            >
              {data.summary.bandwidths.map(bw => (
                <option key={bw} value={bw}>{bw}</option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="w-full p-2 border rounded-md text-sm"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          {/* Search Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Indices
            </label>
            <input
              type="text"
              value={filters.searchTerm}
              onChange={(e) => setFilters(prev => ({ ...prev, searchTerm: e.target.value }))}
              placeholder="Filter indices..."
              className="w-full p-2 border rounded-md text-sm"
            />
          </div>
        </div>
      </div>

      {/* Results Summary */}
      <div className="text-sm text-gray-600">
        Showing {filteredIndices.length} of {Object.keys(data.distributions).length} acoustic indices
      </div>

      {/* Small Multiples Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredIndices.map(indexName => {
          const distributions = data.distributions[indexName];
          const chartData = prepareChartData(indexName, distributions);
          const indexMeta = data.indices_metadata[indexName];

          return (
            <div key={indexName} className="bg-white rounded-lg border p-4 flex flex-col h-56">
              {/* Index Header - Fixed Height */}
              <div className="mb-3 h-12 flex-shrink-0">
                <h3 className="font-medium text-sm text-gray-900 truncate leading-tight" title={indexName}>
                  {indexName}
                </h3>
                <div className="h-4 mt-1">
                  {indexMeta?.category && (
                    <p className="text-xs text-gray-500 truncate">{indexMeta.category}</p>
                  )}
                </div>
              </div>

              {/* Mini Chart - Fixed Height */}
              <div className="h-32 flex-shrink-0 mb-2">
                {chartData.length > 0 ? (
                  <ResponsiveLine
                    data={chartData}
                    margin={{ top: 5, right: 5, bottom: 15, left: 5 }}
                    xScale={{ type: 'linear' }}
                    yScale={{ 
                      type: 'linear', 
                      min: 'auto', 
                      max: 'auto',
                      stacked: false,
                      reverse: false
                    }}
                    curve="monotoneX"
                    enableArea={false}
                    enablePoints={false}
                    enableGridX={false}
                    enableGridY={false}
                    colors={({ id }) => STATION_COLORS[id as keyof typeof STATION_COLORS]}
                    lineWidth={1.5}
                    axisTop={null}
                    axisRight={null}
                    axisBottom={null} // Completely hide bottom axis
                    axisLeft={null}   // Completely hide left axis
                    animate={false}
                    isInteractive={false}
                    useMesh={false}
                    enableSlices={false}
                    enableCrosshair={false}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-xs text-gray-400">
                    No data
                  </div>
                )}
              </div>

              {/* Station Counts - Fixed Height, Flex Grow */}
              <div className="text-xs text-gray-500 flex-grow overflow-hidden">
                <div className="flex flex-wrap gap-x-2 gap-y-1">
                  {filters.stations.map(station => {
                    const key = `${station}_${filters.bandwidth}`;
                    const stationData = distributions[key];
                    return stationData ? (
                      <span 
                        key={station} 
                        className="inline-flex items-center"
                        style={{ color: STATION_COLORS[station as keyof typeof STATION_COLORS] }}
                      >
                        {station}: {stationData.count.toLocaleString()}
                      </span>
                    ) : null;
                  }).filter(Boolean)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredIndices.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-2">No indices found</div>
          <div className="text-gray-500 text-sm">
            Try adjusting your filters or search terms
          </div>
        </div>
      )}
    </div>
  );
}