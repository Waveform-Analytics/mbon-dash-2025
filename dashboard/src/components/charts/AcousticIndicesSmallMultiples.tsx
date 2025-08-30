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
    bandwidth: 'FullBW',
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
      
      // Check if index has data for selected stations
      const indexDistributions = data.distributions[indexName];
      const hasDataForSelectedStations = filters.stations.some(station => 
        indexDistributions[station] && indexDistributions[station].count > 0
      );
      
      return hasDataForSelectedStations;
    });
  }, [data, filters]);

  // Prepare chart data for each index
  const prepareChartData = (indexName: string, distributions: IndexDistributions) => {
    return filters.stations
      .filter(station => distributions[station] && distributions[station].count > 0)
      .map(station => ({
        id: station,
        color: STATION_COLORS[station as keyof typeof STATION_COLORS],
        data: distributions[station].x.map((x, i) => ({
          x,
          y: distributions[station].y[i]
        }))
      }));
  };

  // Get unique categories for filter
  const categories = useMemo(() => {
    const cats = new Set(['All']);
    Object.values(data.indices_metadata).forEach(meta => {
      if (meta.category) cats.add(meta.category);
    });
    return Array.from(cats);
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
            <div key={indexName} className="bg-white rounded-lg border p-4">
              {/* Index Header */}
              <div className="mb-3">
                <h3 className="font-medium text-sm text-gray-900 truncate" title={indexName}>
                  {indexName}
                </h3>
                {indexMeta?.category && (
                  <p className="text-xs text-gray-500 mt-1">{indexMeta.category}</p>
                )}
              </div>

              {/* Mini Chart */}
              <div className="h-32">
                {chartData.length > 0 ? (
                  <ResponsiveLine
                    data={chartData}
                    margin={{ top: 10, right: 10, bottom: 20, left: 25 }}
                    xScale={{ type: 'linear' }}
                    yScale={{ type: 'linear', min: 'auto', max: 'auto' }}
                    curve="monotoneX"
                    enableArea={false}
                    enablePoints={false}
                    enableGridX={false}
                    enableGridY={false}
                    colors={({ id }) => STATION_COLORS[id as keyof typeof STATION_COLORS]}
                    lineWidth={2}
                    axisTop={null}
                    axisRight={null}
                    axisBottom={{
                      tickSize: 0,
                      tickPadding: 5,
                      tickRotation: 0,
                      tickValues: 0, // Hide ticks for cleaner look
                    }}
                    axisLeft={{
                      tickSize: 0,
                      tickPadding: 5,
                      tickRotation: 0,
                      tickValues: 0, // Hide ticks for cleaner look
                    }}
                    animate={false} // Disable animation for better performance
                    isInteractive={false} // Disable interactions for small multiples
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-xs text-gray-400">
                    No data
                  </div>
                )}
              </div>

              {/* Station Counts */}
              <div className="mt-2 text-xs text-gray-500">
                {filters.stations.map(station => {
                  const stationData = distributions[station];
                  return stationData ? (
                    <span 
                      key={station} 
                      className="inline-block mr-2"
                      style={{ color: STATION_COLORS[station as keyof typeof STATION_COLORS] }}
                    >
                      {station}: {stationData.count}
                    </span>
                  ) : null;
                }).filter(Boolean)}
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