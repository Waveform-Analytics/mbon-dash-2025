'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import * as Plot from '@observablehq/plot';
import { useIndexDistributions } from '@/lib/hooks/useData';

// Hook for raw acoustic indices data (same as heatmap)
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

interface BandwidthComparisonBoxPlotProps {
  className?: string;
}

export default function BandwidthComparisonBoxPlot({ className = "" }: BandwidthComparisonBoxPlotProps) {
  const [selectedIndex, setSelectedIndex] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>('both');
  const containerRef = useRef<HTMLDivElement>(null);

  // Load the index distributions data and raw acoustic indices
  const { data: indexDistributions, loading, error } = useIndexDistributions();
  const { data: rawData, loading: rawLoading, error: rawError } = useAcousticIndicesRaw();

  // Get available categories and indices from the data
  const categories = useMemo(() => {
    if (!indexDistributions) return [];
    const categorySet = new Set<string>();
    
    // Get categories from both bandwidths
    Object.values(indexDistributions.index_distributions_by_bandwidth).forEach(analyses => {
      analyses.forEach(analysis => {
        if (analysis.category) {
          categorySet.add(analysis.category);
        }
      });
    });
    
    return Array.from(categorySet).sort();
  }, [indexDistributions]);
  
  const availableIndices = useMemo(() => {
    if (!selectedCategory || !indexDistributions) return [];
    const indexSet = new Set<string>();
    
    // Get indices for the selected category from both bandwidths
    Object.values(indexDistributions.index_distributions_by_bandwidth).forEach(analyses => {
      analyses.forEach(analysis => {
        if (analysis.category === selectedCategory && analysis.index) {
          indexSet.add(analysis.index);
        }
      });
    });
    
    return Array.from(indexSet).sort();
  }, [selectedCategory, indexDistributions]);

  // Set initial category and index
  useEffect(() => {
    if (categories.length > 0 && !selectedCategory) {
      const initialCategory = categories.find(cat => cat.includes('Diversity')) || categories[0];
      setSelectedCategory(initialCategory);
    }
  }, [categories, selectedCategory]);

  // Update selected index when category changes
  useEffect(() => {
    if (availableIndices.length > 0 && !availableIndices.includes(selectedIndex)) {
      setSelectedIndex(availableIndices[0]);
    }
  }, [availableIndices, selectedIndex]);

  // Prepare box plot data from the raw acoustic indices values
  const boxPlotData = useMemo(() => {
    if (!selectedIndex || !rawData || !rawData.acoustic_indices) return [];

    const data: Array<{
      station: string;
      bandwidth: string;
      value: number;
      group: string;
    }> = [];
    
    // Filter data based on year selection
    const filteredData = rawData.acoustic_indices.filter(record => {
      if (selectedYear === 'both') return true;
      
      const recordDate = new Date(record.Date);
      const recordYear = recordDate.getFullYear().toString();
      
      if (selectedYear === '2018') return recordYear === '2018';
      if (selectedYear === '2021') return recordYear === '2021';
      return true;
    });
    
    // Extract values for each station and bandwidth combination
    filteredData.forEach(record => {
      const value = record[selectedIndex];
      if (value !== undefined && value !== null && typeof value === 'number' && !isNaN(value)) {
        data.push({
          station: record.station,
          bandwidth: record.bandwidth,
          value: value,
          group: `${record.station}_${record.bandwidth}`
        });
      }
    });

    return data;
  }, [selectedIndex, rawData, selectedYear]);

  // Create the plot
  useEffect(() => {
    if (boxPlotData.length === 0 || !containerRef.current || !selectedIndex) return;

    const container = containerRef.current;
    container.innerHTML = '';

    // Get unique stations for x-axis domain
    const stations = [...new Set(boxPlotData.map(d => d.station))].sort();

    const plot = Plot.plot({
      width: Math.max(container.clientWidth - 48, 700),
      height: 450,
      marginLeft: 80,
      marginBottom: 60,
      marginRight: 140,
      marginTop: 50,
      style: {
        fontSize: "13px",
        fontFamily: "Inter, system-ui, sans-serif",
        background: "#fafafa"
      },
      
      fx: {
        domain: stations,
        label: "Station →",
        labelAnchor: "center",
        labelOffset: 35,
        paddingInner: 0.3,  // Space between station groups
        tickSize: 0
      },
      
      x: {
        domain: ['FullBW', '8kHz'],
        paddingOuter: 0.2,
        paddingInner: 0.1,  // Small space between bandwidths within station
        axis: null  // Hide the bandwidth axis since it's shown in the legend
      },
      
      y: {
        label: `↑ ${selectedIndex} Value`,
        labelAnchor: "center", 
        labelOffset: 45,
        grid: true,
        nice: true,
        tickFormat: "~s"
      },
      
      color: {
        domain: ['FullBW', '8kHz'],
        range: ['#0ea5e9', '#f59e0b'], // Ocean blue and coral amber
        legend: true,
        label: "Bandwidth"
      },
      
      marks: [
        // Background grid
        Plot.gridY({
          stroke: "#e2e8f0",
          strokeWidth: 0.5,
          strokeDasharray: "2,2"
        }),
        
        // Box plots grouped by station and bandwidth
        Plot.boxY(boxPlotData, {
          fx: "station",  // Facet by station
          x: "bandwidth", // Group by bandwidth within station
          y: "value",
          fill: "bandwidth",
          stroke: "bandwidth",
          strokeWidth: 1.5,
          fillOpacity: 0.6,
          tip: false
        }),
        
        // Add outlier dots
        Plot.dot(boxPlotData, {
          fx: "station",
          x: "bandwidth",
          y: "value",
          fill: "bandwidth",
          fillOpacity: 0.7,
          stroke: "bandwidth",
          strokeWidth: 1,
          r: 2,
          tip: false
        })
      ]
    });

    container.appendChild(plot);

    return () => {
      if (plot) plot.remove();
    };
  }, [boxPlotData, selectedIndex]);

  if (loading || rawLoading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className} p-8`}>
        <div className="flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600 text-sm">Loading bandwidth comparison...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || rawError || !indexDistributions || !rawData) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className} p-8`}>
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Data</h3>
          <p className="text-red-600 text-sm">{error?.message || 'No data available'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-xl font-semibold text-slate-800">
          Bandwidth Comparison: {selectedIndex || 'Select an Index'}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Compare statistical distributions across different frequency ranges
        </p>
      </div>
      
      {/* Controls */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Category Selector */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              Index Category:
            </label>
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select category...</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Index Selector */}
          <div>
            <label htmlFor="index" className="block text-sm font-medium text-gray-700 mb-2">
              Acoustic Index:
            </label>
            <select
              id="index"
              value={selectedIndex}
              onChange={(e) => setSelectedIndex(e.target.value)}
              disabled={!selectedCategory}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            >
              <option value="">Select index...</option>
              {availableIndices.map((index) => (
                <option key={index} value={index}>
                  {index}
                </option>
              ))}
            </select>
          </div>

          {/* Year Selector */}
          <div>
            <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-2">
              Year:
            </label>
            <select
              id="year"
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="both">Both Years</option>
              <option value="2018">2018 Only</option>
              <option value="2021">2021 Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="p-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <div ref={containerRef} className="w-full" />
        </div>
      </div>

      {/* Statistical Summary */}
      {boxPlotData.length > 0 && (
        <div className="px-6 pb-6">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="font-medium text-blue-800 mb-2">Box Plot Interpretation</div>
            <div className="text-blue-700 text-sm">
              Each box shows the distribution of <strong>{selectedIndex}</strong> values for a specific bandwidth. 
              The box represents the interquartile range (25th to 75th percentile), 
              the line inside shows the median, and whiskers extend to min/max values. 
              Stations are grouped separately with both bandwidth options shown side-by-side for easy comparison.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}