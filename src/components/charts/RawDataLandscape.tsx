'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as Plot from '@observablehq/plot';
import { useRawDataLandscape } from '@/lib/hooks/useData';

interface RawDataLandscapeProps {
  /** Width of the chart container */
  width?: number;
  /** Height of the chart container */
  height?: number;
}

export default function RawDataLandscape({ 
  width = 900, 
  height = 600 
}: RawDataLandscapeProps) {
  const plotRef = useRef<HTMLDivElement>(null);
  const { data, loading, error } = useRawDataLandscape();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    if (!data || !plotRef.current) return;

    const { indices_overview, summary_stats, datasets_info } = data.raw_data_landscape;

    // Filter indices by category
    const filteredIndices = selectedCategory === 'all' 
      ? indices_overview 
      : indices_overview.filter(idx => idx.category === selectedCategory);

    // Prepare data for heatmap visualization
    const heatmapData = [];
    const datasets = Object.keys(datasets_info).sort();

    for (const index of filteredIndices) {
      for (const datasetKey of datasets) {
        const availability = index.availability[datasetKey];
        if (availability) {
          heatmapData.push({
            index: index.index,
            dataset: `${availability.station}_${availability.bandwidth}`,
            station: availability.station,
            bandwidth: availability.bandwidth,
            category: index.category,
            available: availability.available ? 1 : 0,
            coverage_pct: availability.coverage_pct || 0,
            n_values: availability.n_values || 0
          });
        }
      }
    }

    // Category colors
    const categoryColors: Record<string, string> = {
      'complexity': '#377eb8',
      'diversity': '#e41a1c', 
      'bioacoustic': '#4daf4a',
      'temporal': '#984ea3',
      'frequency': '#ff7f00',
      'anthropogenic': '#ffff33',
      'other': '#a65628'
    };

    // Create the plot
    const plot = Plot.plot({
      width,
      height: Math.max(400, filteredIndices.length * 12 + 100),
      marginLeft: 150,
      marginRight: 100,
      marginTop: 60,
      marginBottom: 80,
      
      x: {
        label: "Dataset (Station_Bandwidth)",
        domain: datasets.map(key => {
          const info = datasets_info[key];
          return `${info.station}_${info.bandwidth}`;
        })
      },
      
      y: {
        label: "Acoustic Index",
        domain: filteredIndices.map(idx => idx.index)
      },
      
      color: {
        type: "categorical",
        domain: Object.keys(categoryColors),
        range: Object.values(categoryColors),
        legend: true
      },
      
      marks: [
        // Main heatmap - availability
        Plot.cell(heatmapData, {
          x: "dataset",
          y: "index", 
          fill: d => d.available ? d.category : "#f5f5f5",
          stroke: "white",
          strokeWidth: 1,
          opacity: d => d.available ? 0.8 : 0.3,
          title: d => `${d.index}\nStation: ${d.station}\nBandwidth: ${d.bandwidth}\nAvailable: ${d.available ? 'Yes' : 'No'}\nCoverage: ${d.coverage_pct.toFixed(1)}%\nValues: ${d.n_values.toLocaleString()}`
        }),
        
        // Text overlay for missing data
        Plot.text(heatmapData.filter(d => !d.available), {
          x: "dataset",
          y: "index",
          text: "✗",
          fill: "#999",
          fontSize: 10
        })
      ],
      
      title: `Raw Data Landscape: All ${summary_stats.total_indices} Acoustic Indices`,
      subtitle: `Showing data availability across ${Object.keys(datasets_info).length} datasets before dimensionality reduction`
    });

    // Clear and render
    plotRef.current.innerHTML = '';
    plotRef.current.appendChild(plot);

    return () => {
      if (plotRef.current) {
        plotRef.current.innerHTML = '';
      }
    };
  }, [data, width, height, selectedCategory]);

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading raw data landscape...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Raw Data Landscape</h3>
          <p className="text-red-600 text-sm">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <p className="text-gray-500">No raw data landscape available</p>
      </div>
    );
  }

  const { summary_stats } = data.raw_data_landscape;

  return (
    <div className="raw-data-landscape-container">
      {/* Control Panel */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex flex-wrap items-center gap-4 mb-3">
          <h3 className="text-lg font-semibold text-gray-800">
            Raw Data Landscape
          </h3>
        </div>
        
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Filter by Category:</label>
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="all">All Categories ({summary_stats.total_indices})</option>
              {Object.entries(summary_stats.category_counts).map(([cat, count]) => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)} ({count})
                </option>
              ))}
            </select>
          </div>
          
          <div className="text-sm text-gray-600">
            <span className="font-medium">Coverage:</span> {summary_stats.coverage_percentage.toFixed(1)}%
          </div>
          
          <div className="text-sm text-gray-600">
            <span className="font-medium">Datasets:</span> {Object.keys(data.raw_data_landscape.datasets_info).length}
          </div>
        </div>
      </div>

      {/* Statistics Summary */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-blue-800 font-semibold">Index Categories</div>
          <div className="text-blue-700 space-y-1 text-sm mt-2">
            {Object.entries(summary_stats.category_counts).map(([cat, count]) => (
              <div key={cat} className="flex justify-between">
                <span>{cat}:</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-green-800 font-semibold">Station Coverage</div>
          <div className="text-green-700 space-y-1 text-sm mt-2">
            {Object.entries(summary_stats.station_stats).map(([station, stats]) => (
              <div key={station} className="flex justify-between">
                <span>Station {station}:</span>
                <span className="font-medium">{(stats as any).total_records.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-purple-50 p-3 rounded-lg">
          <div className="text-purple-800 font-semibold">Bandwidth Analysis</div>
          <div className="text-purple-700 space-y-1 text-sm mt-2">
            {Object.entries(summary_stats.bandwidth_stats).map(([bandwidth, stats]) => (
              <div key={bandwidth} className="flex justify-between">
                <span>{bandwidth}:</span>
                <span className="font-medium">{(stats as any).total_records.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Plot Container */}
      <div 
        ref={plotRef} 
        className="raw-data-landscape-plot border border-gray-200 rounded-lg bg-white overflow-auto"
        style={{ width: '100%' }}
      />

      {/* Explanation */}
      <div className="mt-4 bg-yellow-50 p-4 rounded-lg">
        <h4 className="font-semibold text-yellow-800 mb-2">Overview: Complete Index Landscape</h4>
        <p className="text-yellow-700 text-sm">
          This visualization shows all {summary_stats.total_indices} acoustic indices 
          across {Object.keys(data.raw_data_landscape.datasets_info).length} datasets (stations and bandwidths). 
          Each colored cell represents an available index, categorized by acoustic property type. 
          This comprehensive view helps identify data availability patterns and index coverage 
          before conducting focused analyses.
        </p>
      </div>
    </div>
  );
}