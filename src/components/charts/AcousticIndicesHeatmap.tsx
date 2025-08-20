'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import * as Plot from '@observablehq/plot';
import { useIndexDistributions } from '@/lib/hooks/useData';

// We'll need to create a hook for the raw acoustic indices data
interface AcousticIndicesRawData {
  acoustic_indices: Array<{
    Date: string;
    station: string;
    bandwidth: string;
    [key: string]: string | number; // All the acoustic index columns
  }>;
  metadata: {
    stations: string[];
    bandwidths: string[];
  };
}

function useAcousticIndicesRaw() {
  const [data, setData] = useState<AcousticIndicesRawData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const baseUrl = typeof window !== 'undefined' && window.location.hostname === 'localhost'
          ? '/api/cdn'
          : (process.env.NEXT_PUBLIC_DATA_URL || 'http://localhost:3000/data');
        
        const response = await fetch(`${baseUrl}/processed/acoustic_indices_detailed.json`);
        if (!response.ok) throw new Error('Failed to fetch acoustic indices data');
        
        const jsonData = await response.json();
        setData(jsonData);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
}

// This function is now unused since we get indices from categories
// function getAvailableIndices(data: any[]): string[] {
//   if (!data || data.length === 0) return [];
//   
//   const exclude = ['Date', 'datetime', 'station', 'bandwidth', 'dataset_key', 
//                    'year', 'month', 'day', 'hour'];
//   const firstRecord = data[0];
//   
//   return Object.keys(firstRecord)
//     .filter(key => !exclude.includes(key) && typeof firstRecord[key] === 'number')
//     .sort();
// }

export default function AcousticIndicesHeatmap() {
  const [station, setStation] = useState<string>('9M');
  const [bandwidth, setBandwidth] = useState<string>('FullBW');
  const [selectedCategory, setSelectedCategory] = useState<string>('Diversity Indices');
  const [selectedIndex, setSelectedIndex] = useState<string>('ADI');
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { data: rawData, loading, error } = useAcousticIndicesRaw();
  const { data: indexDistributions } = useIndexDistributions();

  // Get available categories from index distributions
  const categories = useMemo(() => {
    if (!indexDistributions) return [];
    const categorySet = new Set<string>();
    
    Object.values(indexDistributions.index_distributions_by_bandwidth).forEach(analyses => {
      analyses.forEach(analysis => {
        if (analysis.category) {
          categorySet.add(analysis.category);
        }
      });
    });
    
    return Array.from(categorySet).sort();
  }, [indexDistributions]);

  // Get available indices for selected category
  const availableIndices = useMemo(() => {
    if (!selectedCategory || !indexDistributions) return [];
    const indexSet = new Set<string>();
    
    Object.values(indexDistributions.index_distributions_by_bandwidth).forEach(analyses => {
      analyses.forEach(analysis => {
        if (analysis.category === selectedCategory && analysis.index) {
          indexSet.add(analysis.index);
        }
      });
    });
    
    return Array.from(indexSet).sort();
  }, [selectedCategory, indexDistributions]);

  // Filter data for selected station and bandwidth
  const filteredData = useMemo(() => {
    if (!rawData || !rawData.acoustic_indices) return [];
    
    return rawData.acoustic_indices.filter(record => 
      record.station === station && record.bandwidth === bandwidth
    );
  }, [rawData, station, bandwidth]);

  // Set initial category when data loads
  useEffect(() => {
    if (categories.length > 0 && !selectedCategory) {
      const initialCategory = categories.find(cat => cat.includes('Diversity')) || categories[0];
      setSelectedCategory(initialCategory);
    }
  }, [categories, selectedCategory]);

  // Set initial index when category changes
  useEffect(() => {
    if (availableIndices.length > 0 && !availableIndices.includes(selectedIndex)) {
      setSelectedIndex(availableIndices[0]);
    }
  }, [availableIndices, selectedIndex]);

  // Process data for the heatmap
  const heatmapData = useMemo(() => {
    if (!filteredData || filteredData.length === 0 || !selectedIndex) return [];

    return filteredData.map(record => {
      const date = new Date(record.Date);
      return {
        date: date.toISOString().split('T')[0], // YYYY-MM-DD format
        hour: date.getHours(),
        value: record[selectedIndex] || 0
      };
    });
  }, [filteredData, selectedIndex]);

  // Create the plot
  useEffect(() => {
    if (heatmapData.length === 0 || !containerRef.current) return;

    const container = containerRef.current;
    container.innerHTML = '';

    // Calculate appropriate width based on data density
    const uniqueDates = new Set(heatmapData.map(d => d.date)).size;
    const cellWidth = 6; // Narrower cells for year view
    const cellHeight = 20; // Moderate cell height for readability
    const calculatedWidth = Math.max(3000, uniqueDates * cellWidth + 200);
    const calculatedHeight = 24 * cellHeight + 150; // 24 hours * cell height + margins (~630px total)

    // Generate month-centered ticks
    const getMonthTicks = () => {
      const monthCenters = new Map();
      heatmapData.forEach(d => {
        const date = new Date(d.date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        if (!monthCenters.has(monthKey)) {
          const midMonth = new Date(date.getFullYear(), date.getMonth(), 15);
          monthCenters.set(monthKey, midMonth.toISOString().split('T')[0]);
        }
      });
      return Array.from(monthCenters.values()).sort();
    };

    const plot = Plot.plot({
      width: calculatedWidth,
      height: calculatedHeight,
      marginLeft: 80,
      marginBottom: 60,
      marginRight: 120,
      marginTop: 40,
      style: {
        fontSize: "14px",
        fontFamily: "Inter, system-ui, sans-serif",
        overflow: "visible"
      },
      
      // Ensure proper cell sizing
      padding: 0,
      
      color: {
        type: "sequential",
        scheme: "viridis",
        label: selectedIndex,
        legend: true
      },
      
      marks: [
        Plot.cell(heatmapData, {
          x: "date",
          y: "hour",
          fill: "value",
          tip: false, // Disable tooltips as requested
          inset: 0 // No gaps between cells
        })
      ],
      
      x: {
        type: "band",
        label: "Month →",
        tickRotate: 0,
        ticks: getMonthTicks(),
        tickFormat: d => {
          const date = new Date(d);
          return date.toLocaleDateString('en-US', { month: 'short' });
        }
      },
      
      y: {
        label: "↑ Hour of Day",
        domain: Array.from({ length: 24 }, (_, i) => i),
        reverse: true,
        ticks: [0, 6, 12, 18, 23],
        tickFormat: d => {
          return d === 0 ? "12am" : d === 6 ? "6am" : d === 12 ? "12pm" : d === 18 ? "6pm" : d === 23 ? "11pm" : `${d}h`;
        },
        type: "band",
        paddingInner: 0,
        paddingOuter: 0
      }
    });

    container.appendChild(plot);

    return () => {
      if (plot) plot.remove();
    };
  }, [heatmapData, selectedIndex]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8">
        <div className="flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600 text-sm">Loading temporal heatmap...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-8">
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Data</h3>
          <p className="text-red-600 text-sm">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-xl font-semibold text-slate-800">
          Acoustic Index Temporal Patterns
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Hourly patterns across the year - scroll horizontally to explore
        </p>
      </div>
      
      {/* Controls */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Station Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Station:
            </label>
            <select
              value={station}
              onChange={(e) => setStation(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="9M">9M</option>
              <option value="14M">14M</option>
            </select>
          </div>

          {/* Bandwidth Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bandwidth:
            </label>
            <select
              value={bandwidth}
              onChange={(e) => setBandwidth(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="FullBW">Full Bandwidth</option>
              <option value="8kHz">8 kHz</option>
            </select>
          </div>

          {/* Category Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category:
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Index Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Index:
            </label>
            <select
              value={selectedIndex}
              onChange={(e) => setSelectedIndex(e.target.value)}
              disabled={!selectedCategory}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            >
              {availableIndices.map(index => (
                <option key={index} value={index}>
                  {index}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Scrollable Heatmap Container */}
      <div className="p-6">
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-x-auto">
          <div ref={containerRef} className="p-4" style={{ minWidth: '3000px' }} />
        </div>
      </div>

      {/* Legend/Info */}
      <div className="px-6 pb-6">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="font-medium text-blue-800 mb-2">How to Read This Chart</div>
          <div className="text-blue-700 text-sm">
            Each column represents a day, each row represents an hour of the day. 
            Colors indicate the value of <strong>{selectedIndex}</strong> at that time. 
            Darker colors (purple/blue) indicate lower values, brighter colors (yellow/green) indicate higher values.
            Scroll horizontally to see the full year of data.
          </div>
        </div>
      </div>
    </div>
  );
}