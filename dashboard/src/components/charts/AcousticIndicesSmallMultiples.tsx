'use client';

import { useMemo, useState } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { motion } from 'framer-motion';
import { AcousticIndicesDistributionsData, IndexDistributions } from '@/types/data';
import { useViewData } from '@/lib/data/useViewData';
import { Info, BarChart3 } from 'lucide-react';

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

interface AcousticIndex {
  prefix: string;
  category: string;
  subcategory: string;
  description: string;
  full_name: string;
  computational_type: string;
}

interface IndicesData {
  metadata: {
    generated_at: string;
    version: string;
    description: string;
  };
  summary: {
    total_indices: number;
    categories: {
      count: number;
      list: string[];
    };
  };
  indices: AcousticIndex[];
}

// Station colors for consistent visualization
const STATION_COLORS = {
  '9M': '#2563eb',   // Blue
  '14M': '#dc2626',  // Red  
  '37M': '#059669',  // Green
};

// Category colors for consistent theming (available for future styling enhancements)
// const CATEGORY_COLORS: Record<string, { bg: string; border: string; header: string; badge: string }> = {
//   'Complexity Indices': { 
//     bg: 'bg-gradient-to-br from-blue-50 to-blue-100', 
//     border: 'border-blue-200', 
//     header: 'bg-gradient-to-r from-blue-100 to-blue-50',
//     badge: 'bg-blue-100 text-blue-800 border-blue-200'
//   },
//   'Temporal Indices': { 
//     bg: 'bg-gradient-to-br from-green-50 to-green-100', 
//     border: 'border-green-200', 
//     header: 'bg-gradient-to-r from-green-100 to-green-50',
//     badge: 'bg-green-100 text-green-800 border-green-200'
//   },
//   'Diversity Indices': { 
//     bg: 'bg-gradient-to-br from-purple-50 to-purple-100', 
//     border: 'border-purple-200', 
//     header: 'bg-gradient-to-r from-purple-100 to-purple-50',
//     badge: 'bg-purple-100 text-purple-800 border-purple-200'
//   },
//   'Spectral Indices': { 
//     bg: 'bg-gradient-to-br from-orange-50 to-orange-100', 
//     border: 'border-orange-200', 
//     header: 'bg-gradient-to-r from-orange-100 to-orange-50',
//     badge: 'bg-orange-100 text-orange-800 border-orange-200'
//   },
//   'Amplitude Indices': { 
//     bg: 'bg-gradient-to-br from-red-50 to-red-100', 
//     border: 'border-red-200', 
//     header: 'bg-gradient-to-r from-red-100 to-red-50',
//     badge: 'bg-red-100 text-red-800 border-red-200'
//   }
// };

// Flip Card Component
function FlipCard({ 
  indexName, 
  chartData, 
  indexMeta, 
  distributions, 
  filters, 
  isFlipped, 
  onFlip 
}: {
  indexName: string;
  chartData: Array<{id: string; color: string; data: Array<{x: number; y: number}>}>;
  indexMeta?: AcousticIndex;
  distributions: IndexDistributions;
  filters: FilterState;
  isFlipped: boolean;
  onFlip: () => void;
}) {


  return (
    <div className="relative h-56 perspective-1000">
      <motion.div
        className="relative w-full h-full preserve-3d"
        animate={{ rotateY: isFlipped ? 180 : 0 }}
        transition={{ duration: 0.6, ease: "easeInOut" }}
      >
        {/* Front Side - Chart */}
        <div className="absolute inset-0 backface-hidden bg-white rounded-lg border p-4 flex flex-col">
          {/* Index Header - Fixed Height */}
          <div className="mb-3 h-12 flex-shrink-0 flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-sm text-gray-900 truncate leading-tight" title={indexName}>
                {indexName}
              </h3>
              <div className="h-4 mt-1">
                {indexMeta?.category && (
                  <p className="text-xs text-gray-500 truncate">{indexMeta.category}</p>
                )}
              </div>
            </div>
            <button
              onClick={onFlip}
              className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="View details"
            >
              <Info className="h-4 w-4" />
            </button>
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
                axisBottom={null}
                axisLeft={null}
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

        {/* Back Side - Description */}
        <div className="absolute inset-0 backface-hidden bg-white rounded-lg border p-4 flex flex-col rotate-y-180">
          {/* Header with flip button */}
          <div className="mb-3 h-12 flex-shrink-0 flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-sm text-gray-900 truncate leading-tight" title={indexName}>
                {indexName}
              </h3>
              <div className="h-4 mt-1">
                {indexMeta?.subcategory && (
                  <p className="text-xs text-gray-500 truncate">{indexMeta.subcategory}</p>
                )}
              </div>
            </div>
            <button
              onClick={onFlip}
              className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="View chart"
            >
              <BarChart3 className="h-4 w-4" />
            </button>
          </div>

          {/* Description Content */}
          <div className="flex-grow overflow-hidden">
            {indexMeta ? (
              <div className="space-y-3">
                {indexMeta.full_name && (
                  <p className="text-sm font-medium text-gray-900 leading-tight">
                    {indexMeta.full_name}
                  </p>
                )}
                
                {indexMeta.description && (
                  <p className="text-xs text-gray-600 leading-relaxed line-clamp-6">
                    {indexMeta.description}
                  </p>
                )}
                
                {indexMeta.computational_type && (
                  <div className="pt-2 border-t border-gray-200">
                    <span className="text-xs font-mono text-gray-500">
                      {indexMeta.computational_type}
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-xs text-gray-400">
                No description available
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

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

  // Load indices reference data
  const { data: indicesData } = useViewData<IndicesData>('indices_reference.json');
  
  // Track which cards are flipped
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());

  // Create a map of index names to their metadata
  const indexMetadataMap = useMemo(() => {
    if (!indicesData?.indices) return new Map();
    
    const map = new Map<string, AcousticIndex>();
    indicesData.indices.forEach(index => {
      map.set(index.prefix, index);
    });
    return map;
  }, [indicesData]);

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

  // Handle card flip
  const handleCardFlip = (indexName: string) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(indexName)) {
        newSet.delete(indexName);
      } else {
        newSet.add(indexName);
      }
      return newSet;
    });
  };

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
        <span className="ml-2 text-xs text-gray-400">
          • Click the info icon to view index descriptions
        </span>
      </div>

      {/* Small Multiples Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredIndices.map(indexName => {
          const distributions = data.distributions[indexName];
          const chartData = prepareChartData(indexName, distributions);
          const indexMeta = indexMetadataMap.get(indexName);
          const isFlipped = flippedCards.has(indexName);

          return (
            <FlipCard
              key={indexName}
              indexName={indexName}
              chartData={chartData}
              indexMeta={indexMeta}
              distributions={distributions}
              filters={filters}
              isFlipped={isFlipped}
              onFlip={() => handleCardFlip(indexName)}
            />
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