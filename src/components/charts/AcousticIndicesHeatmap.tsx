'use client';

import { useState, useEffect, useMemo } from 'react';
import * as Plot from '@observablehq/plot';
import { useAcousticIndicesCSV } from '@/lib/hooks/useAcousticIndicesCSV';
import { 
  getUniqueCategories, 
  getIndicesByCategory, 
  getIndexInfo 
} from '@/lib/utils/indexCategories';

export default function AcousticIndicesHeatmap() {
  const [station, setStation] = useState<string>('9M');
  const [bandwidth, setBandwidth] = useState<string>('FullBW');
  const [category, setCategory] = useState<string>('');
  const [selectedIndex, setSelectedIndex] = useState<string>('');
  
  const { data, loading, error } = useAcousticIndicesCSV({ station, bandwidth });

  const categories = useMemo(() => getUniqueCategories(), []);
  
  const availableIndices = useMemo(() => {
    if (!category) return [];
    return getIndicesByCategory(category);
  }, [category]);

  // Set initial category and index when component mounts
  useEffect(() => {
    if (categories.length > 0 && !category) {
      const initialCategory = 'Diversity Indices'; // Start with Diversity indices
      setCategory(initialCategory);
      const indices = getIndicesByCategory(initialCategory);
      if (indices.length > 0) {
        setSelectedIndex(indices[0]);
      }
    }
  }, [categories, category]);

  // Update selected index when category changes
  useEffect(() => {
    if (availableIndices.length > 0 && !availableIndices.includes(selectedIndex)) {
      setSelectedIndex(availableIndices[0]);
    }
  }, [availableIndices, selectedIndex]);

  // Process data for the heatmap
  const heatmapData = useMemo(() => {
    if (!data || data.length === 0 || !selectedIndex) return [];

    return data.map(record => {
      const date = new Date(record.Date);
      return {
        date: date.toISOString().split('T')[0], // YYYY-MM-DD format for band scale
        hour: date.getHours(),
        value: typeof record[selectedIndex] === 'number' ? record[selectedIndex] : parseFloat(record[selectedIndex] as string) || 0
      };
    });
  }, [data, selectedIndex]);

  // Create the plot
  useEffect(() => {
    if (heatmapData.length === 0) return;

    const container = document.getElementById('indices-heatmap');
    if (!container) return;

    // Clear previous plot
    container.innerHTML = '';

    // Calculate appropriate width and height based on data density
    const uniqueDates = new Set(heatmapData.map(d => d.date)).size;
    
    // Year view: pcolormesh-style continuous heatmap
    const cellWidth = 8; // Narrower cells for year view
    const calculatedWidth = Math.max(3000, uniqueDates * cellWidth + 200);
    const calculatedHeight = 600; // Taller for better visibility
    const cellInset = 0; // No gaps between cells

    // Generate month-centered ticks
    const getMonthTicks = () => {
      const monthCenters = new Map();
      heatmapData.forEach(d => {
        const date = new Date(d.date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        if (!monthCenters.has(monthKey)) {
          // Use middle of month for positioning
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
      marginRight: 120, // Space for legend
      style: {
        fontSize: "14px" // Larger fonts for readability
      },
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
          tip: true,
          inset: cellInset
        })
      ],
      x: {
        type: "band",
        label: "Month",
        tickRotate: 0,
        ticks: getMonthTicks(),
        tickFormat: d => {
          const date = new Date(d);
          return date.toLocaleDateString('en-US', { month: 'short' });
        }
      },
      y: {
        label: "Hour of Day",
        domain: Array.from({ length: 24 }, (_, i) => i),
        reverse: true,
        ticks: [0, 6, 12, 18],
        tickFormat: d => {
          return d === 0 ? "12am" : d === 6 ? "6am" : d === 12 ? "12pm" : d === 18 ? "6pm" : `${d}h`;
        }
      }
    });

    container.appendChild(plot);

    return () => {
      plot.remove();
    };
  }, [heatmapData, selectedIndex]);

  const indexInfo = selectedIndex ? getIndexInfo(selectedIndex) : null;

  return (
    <div className="chart-container mb-8">
      <h2 className="text-xl font-semibold text-slate-900 mb-4">
        Acoustic Index Temporal Patterns
      </h2>
      
      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Station Selector */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Station
          </label>
          <select
            value={station}
            onChange={(e) => setStation(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-500"
          >
            <option value="9M">9M</option>
            <option value="14M">14M</option>
          </select>
        </div>

        {/* Bandwidth Selector */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Bandwidth
          </label>
          <select
            value={bandwidth}
            onChange={(e) => setBandwidth(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-500"
          >
            <option value="FullBW">Full Bandwidth</option>
            <option value="8kHz">8 kHz</option>
          </select>
        </div>

        {/* Category Selector */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Index Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-500"
          >
            <option value="">Select a category</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Index Selector */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Index
          </label>
          <select
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value)}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-ocean-500"
            disabled={availableIndices.length === 0}
          >
            {availableIndices.map(index => (
              <option key={index} value={index}>{index}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Index Description */}
      {indexInfo && (
        <div className="bg-ocean-50 border border-ocean-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-ocean-900">
            <span className="font-semibold">{selectedIndex}:</span> {indexInfo.description}
          </p>
        </div>
      )}

      {/* Loading/Error States */}
      {loading && (
        <div className="flex items-center justify-center h-64 bg-slate-50 rounded-lg">
          <p className="text-slate-600">Loading acoustic indices data...</p>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error: {error}</p>
        </div>
      )}

      {/* Heatmap Container */}
      {!loading && !error && data.length > 0 && (
        <div className="w-full">
          <div 
            className="overflow-x-auto border border-slate-200 rounded-lg" 
            style={{ 
              maxWidth: '100%',
              maxHeight: '700px' 
            }}
          >
            <div 
              id="indices-heatmap" 
              style={{ 
                minWidth: '3000px',
                minHeight: '600px'
              }}
            ></div>
          </div>
          <p className="mt-2 text-xs text-slate-500 italic">
            <strong>Tip:</strong> Scroll horizontally to explore patterns across months. Each vertical strip represents one day, colored by acoustic index values throughout the day.
          </p>
        </div>
      )}

      {/* Data Summary */}
      {!loading && !error && data.length > 0 && (
        <div className="mt-4 text-sm text-slate-600">
          <p>
            Showing {heatmapData.length} hourly measurements for full year from {station} station at {bandwidth === 'FullBW' ? 'Full Bandwidth' : '8 kHz'}
          </p>
        </div>
      )}
    </div>
  );
}