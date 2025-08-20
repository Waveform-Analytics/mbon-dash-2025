'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import * as Plot from '@observablehq/plot';
import { useAcousticIndicesCSV } from '@/lib/hooks/useAcousticIndicesCSV';
import { 
  getUniqueCategories, 
  getIndicesByCategory, 
  getIndexInfo 
} from '@/lib/utils/indexCategories';

interface BandwidthComparisonBoxPlotProps {
  className?: string;
}

export default function BandwidthComparisonBoxPlot({ className = "" }: BandwidthComparisonBoxPlotProps) {
  const [selectedIndex, setSelectedIndex] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedYear, setSelectedYear] = useState<string>('both'); // 'both', '2018', '2021'
  const containerRef = useRef<HTMLDivElement>(null);

  const categories = useMemo(() => getUniqueCategories(), []);
  
  const availableIndices = useMemo(() => {
    if (!selectedCategory) return [];
    return getIndicesByCategory(selectedCategory);
  }, [selectedCategory]);

  // Load data for all stations and both bandwidths
  const { data: data9M_FullBW } = useAcousticIndicesCSV({ station: '9M', bandwidth: 'FullBW' });
  const { data: data9M_8kHz } = useAcousticIndicesCSV({ station: '9M', bandwidth: '8kHz' });
  const { data: data14M_FullBW } = useAcousticIndicesCSV({ station: '14M', bandwidth: 'FullBW' });
  const { data: data14M_8kHz } = useAcousticIndicesCSV({ station: '14M', bandwidth: '8kHz' });
  const { data: data37M_FullBW } = useAcousticIndicesCSV({ station: '37M', bandwidth: 'FullBW' });
  const { data: data37M_8kHz } = useAcousticIndicesCSV({ station: '37M', bandwidth: '8kHz' });

  // Set initial category and index
  useEffect(() => {
    if (categories.length > 0 && !selectedCategory) {
      const initialCategory = 'Diversity Indices';
      setSelectedCategory(initialCategory);
      const indices = getIndicesByCategory(initialCategory);
      if (indices.length > 0) {
        setSelectedIndex(indices[0]);
      }
    }
  }, [categories, selectedCategory]);

  // Update selected index when category changes
  useEffect(() => {
    if (availableIndices.length > 0 && !availableIndices.includes(selectedIndex)) {
      setSelectedIndex(availableIndices[0]);
    }
  }, [availableIndices, selectedIndex]);

  // Prepare box plot data
  const boxPlotData = useMemo(() => {
    if (!selectedIndex) return [];

    const allData = [
      ...(data9M_FullBW || []).map(d => ({ ...d, station: '9M', bandwidth: 'FullBW' })),
      ...(data9M_8kHz || []).map(d => ({ ...d, station: '9M', bandwidth: '8kHz' })),
      ...(data14M_FullBW || []).map(d => ({ ...d, station: '14M', bandwidth: 'FullBW' })),
      ...(data14M_8kHz || []).map(d => ({ ...d, station: '14M', bandwidth: '8kHz' })),
      ...(data37M_FullBW || []).map(d => ({ ...d, station: '37M', bandwidth: 'FullBW' })),
      ...(data37M_8kHz || []).map(d => ({ ...d, station: '37M', bandwidth: '8kHz' }))
    ];

    return allData
      .filter(record => {
        // Filter by year if specified
        if (selectedYear !== 'both') {
          const recordYear = new Date(record.Date).getFullYear().toString();
          if (recordYear !== selectedYear) return false;
        }
        
        // Check if the selected index exists and is numeric
        const value = record[selectedIndex as keyof typeof record];
        return typeof value === 'number' || !isNaN(parseFloat(value as string));
      })
      .map(record => {
        const value = typeof record[selectedIndex as keyof typeof record] === 'number' 
          ? record[selectedIndex as keyof typeof record] 
          : parseFloat(record[selectedIndex as keyof typeof record] as string);
        
        return {
          station: record.station,
          bandwidth: record.bandwidth,
          stationBandwidth: `${record.station}_${record.bandwidth}`, // For grouping
          value: value,
          date: record.Date
        };
      });
  }, [selectedIndex, selectedYear, data9M_FullBW, data9M_8kHz, data14M_FullBW, data14M_8kHz, data37M_FullBW, data37M_8kHz]);

  // Create the plot
  useEffect(() => {
    if (boxPlotData.length === 0 || !containerRef.current || !selectedIndex) return;

    const container = containerRef.current;
    container.innerHTML = '';

    const plot = Plot.plot({
      width: Math.max(container.clientWidth - 48, 800),
      height: 500,
      marginLeft: 80,
      marginBottom: 80,
      marginRight: 140,
      marginTop: 50,
      style: {
        fontSize: "13px",
        fontFamily: "Inter, system-ui, sans-serif",
        background: "#fafafa"
      },
      
      x: {
        domain: ['9M_FullBW', '9M_8kHz', '14M_FullBW', '14M_8kHz', '37M_FullBW', '37M_8kHz'],
        label: "Station →",
        labelAnchor: "center",
        labelOffset: 40,
        tickFormat: (d: string) => {
          const [station] = d.split('_');
          return station;
        },
        tickSize: 6,
        grid: false,
        axis: "bottom"
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
        // Subtle background grid
        Plot.gridY({
          stroke: "#e2e8f0", 
          strokeWidth: 0.5,
          strokeDasharray: "2,2"
        }),
        
        // Box plots grouped by station and bandwidth
        Plot.boxY(boxPlotData, {
          x: "stationBandwidth",
          y: "value",
          fill: "bandwidth",
          stroke: "bandwidth", // Match stems to fill colors
          strokeWidth: 1.5,
          fillOpacity: 0.7,
          tip: false
        })
      ]
    });

    container.appendChild(plot);

    return () => {
      if (plot) plot.remove();
    };
  }, [boxPlotData, selectedIndex]);

  const indexInfo = selectedIndex ? getIndexInfo(selectedIndex) : null;

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-xl font-semibold text-slate-800">
          Bandwidth Comparison: {selectedIndex || 'Select an Index'}
        </h3>
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
        
        {/* Index Description */}
        {indexInfo && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>{selectedIndex}:</strong> Index information available
            </p>
          </div>
        )}
      </div>

      {/* Chart Container - Inner card */}
      <div className="p-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <div ref={containerRef} className="w-full" />
        </div>
      </div>

      {/* Summary Stats */}
      {boxPlotData.length > 0 && (
        <div className="px-6 pb-6">
          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
            <div className="text-center">
              <div className="font-medium text-gray-900">Data Points</div>
              <div>{boxPlotData.length.toLocaleString()} total measurements</div>
            </div>
            <div className="text-center">
              <div className="font-medium text-gray-900">Year Filter</div>
              <div>{selectedYear === 'both' ? 'Both 2018 & 2021' : selectedYear}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}