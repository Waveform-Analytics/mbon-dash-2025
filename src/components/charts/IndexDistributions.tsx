'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as Plot from '@observablehq/plot';
import { useIndexDistributions, type IndexAnalysis } from '@/lib/hooks/useData';

interface IndexDistributionsProps {
  /** Width of the chart container */
  width?: number;
  /** Height of the chart container */
  height?: number;
}

// Individual PDF chart component for each index
function IndexDensityChart({ analysis, width = 200, height = 150 }: {
  analysis: IndexAnalysis;
  width?: number;
  height?: number;
}) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!analysis?.combined_density || !chartRef.current) return;

    const { x, density, x_original } = analysis.combined_density;
    if (!x.length || !density.length) return;

    // Prepare data for plotting
    const plotData = x.map((xVal, i) => ({
      x: xVal,           // Already normalized 0-1
      density: density[i],
      original_x: x_original[i] || 0
    }));

    // Category colors
    const categoryColors: Record<string, string> = {
      'Complexity Indices': '#377eb8',
      'Diversity Indices': '#e41a1c', 
      'Amplitude Indices': '#4daf4a',
      'Temporal Indices': '#984ea3',
      'Spectral Indices': '#ff7f00',
      'Other Indices': '#a65628'
    };

    const color = categoryColors[analysis.category] || '#999999';

    // Create PDF line chart
    const plot = Plot.plot({
      width,
      height,
      marginLeft: 25,
      marginRight: 10,
      marginTop: 35,
      marginBottom: 20,
      
      x: {
        domain: [0, 1],
        ticks: 3,
        tickFormat: d => d.toFixed(1),
        label: null
      },
      
      y: {
        label: null,
        ticks: 3,
        tickFormat: d => d.toFixed(2)
      },
      
      marks: [
        // PDF line
        Plot.line(plotData, {
          x: "x",
          y: "density",
          stroke: color,
          strokeWidth: 2,
          title: d => `Normalized: ${d.x.toFixed(2)}\nOriginal: ${d.original_x.toFixed(3)}\nDensity: ${d.density.toFixed(3)}`
        }),
        
        // Area under curve
        Plot.areaY(plotData, {
          x: "x",
          y: "density",
          fill: color,
          fillOpacity: 0.2
        }),
        
        // Index name as prominent title
        Plot.text([{ label: analysis.index }], {
          x: 0.5,
          y: Math.max(...density) * 1.1,
          text: d => d.label,
          fontSize: 12,
          fontWeight: "bold",
          textAnchor: "middle",
          fill: color,
          dy: -5
        })
      ]
    });

    chartRef.current.innerHTML = '';
    chartRef.current.appendChild(plot);

    return () => {
      if (chartRef.current) {
        chartRef.current.innerHTML = '';
      }
    };
  }, [analysis, width, height]);

  return (
    <div className="index-density-chart">
      <div ref={chartRef} />
      <div className="text-xs text-center text-gray-600 mt-1 space-y-0.5">
        <div className="text-xs font-medium text-gray-700">{analysis.category.replace(' Indices', '')}</div>
        <div className="flex justify-between text-xs">
          <span>Skew: {analysis.combined_stats?.skewness?.toFixed(2) || 'N/A'}</span>
          <span>{analysis.combined_stats?.distribution_type?.replace('_', ' ') || 'Unknown'}</span>
        </div>
        <div className="text-xs text-gray-500">
          Range: {analysis.combined_stats?.min?.toFixed(2)} - {analysis.combined_stats?.max?.toFixed(2)}
        </div>
      </div>
    </div>
  );
}

export default function IndexDistributions({ 
  width = 1200, 
  height = 800 
}: IndexDistributionsProps) {
  const { data, loading, error } = useIndexDistributions();
  const [selectedBandwidth, setSelectedBandwidth] = useState<string>('FullBW');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Set default bandwidth when data loads
  useEffect(() => {
    if (data && data.available_bandwidths.length > 0 && selectedBandwidth === 'FullBW') {
      // Prefer FullBW if available, otherwise use first available
      const preferredBandwidth = data.available_bandwidths.includes('FullBW') 
        ? 'FullBW' 
        : data.available_bandwidths[0];
      setSelectedBandwidth(preferredBandwidth);
    }
  }, [data, selectedBandwidth]);

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading index distributions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Index Distributions</h3>
          <p className="text-red-600 text-sm">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <p className="text-gray-500">No index distribution data available</p>
      </div>
    );
  }

  // Get current bandwidth data
  const currentAnalyses = data.index_distributions_by_bandwidth[selectedBandwidth] || [];
  const currentSummary = data.summary_stats_by_bandwidth[selectedBandwidth];

  if (!currentSummary || currentAnalyses.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <p className="text-gray-500">No data available for {selectedBandwidth} bandwidth</p>
      </div>
    );
  }

  // Filter analyses based on selected category
  const filteredAnalyses = currentAnalyses.filter(analysis => {
    if (selectedCategory !== 'all' && analysis.category !== selectedCategory) {
      return false;
    }
    return true;
  });

  // Limit to first 20 for visualization performance
  const displayAnalyses = filteredAnalyses.slice(0, 20);

  return (
    <div className="index-distributions-container">
      {/* Control Panel */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex flex-wrap items-center gap-4 mb-3">
          <h3 className="text-lg font-semibold text-gray-800">
            Index Distribution & Quality Check
          </h3>
          <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
            Probability Density Functions (0-1 Normalized)
          </span>
        </div>
        
        <div className="flex flex-wrap items-center gap-4">
          {/* Bandwidth Selection */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Bandwidth:</label>
            <select 
              value={selectedBandwidth}
              onChange={(e) => setSelectedBandwidth(e.target.value)}
              className="text-sm border rounded px-2 py-1 font-medium"
            >
              {data.available_bandwidths.map(bandwidth => (
                <option key={bandwidth} value={bandwidth}>
                  {bandwidth} ({data.summary_stats_by_bandwidth[bandwidth]?.total_indices || 0})
                </option>
              ))}
            </select>
          </div>

          {/* Category Selection */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Category:</label>
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="all">All Categories ({currentSummary.total_indices})</option>
              {Object.entries(currentSummary.category_counts).map(([cat, count]) => (
                <option key={cat} value={cat}>
                  {cat} ({count})
                </option>
              ))}
            </select>
          </div>
          
          <div className="text-sm text-gray-600">
            <span className="font-medium">Showing:</span> {displayAnalyses.length} of {filteredAnalyses.length} indices
          </div>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-blue-800 font-semibold">Category Distribution</div>
          <div className="text-blue-700 space-y-1 text-sm mt-2">
            {Object.entries(currentSummary.category_counts).slice(0, 4).map(([category, count]) => (
              <div key={category} className="flex justify-between">
                <span className="truncate">{category.replace(' Indices', '')}:</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="text-gray-800 font-semibold">Distribution Types</div>
          <div className="text-gray-700 space-y-1 text-sm mt-2">
            {Object.entries(currentSummary.distribution_type_counts).slice(0, 4).map(([type, count]) => (
              <div key={type} className="flex justify-between">
                <span className="truncate">{type.replace('_', ' ')}:</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-amber-50 p-3 rounded-lg">
          <div className="text-amber-800 font-semibold">Quality Metrics</div>
          <div className="text-amber-700 space-y-1 text-sm mt-2">
            <div className="flex justify-between">
              <span>Highly Skewed:</span>
              <span className="font-medium">{currentSummary.raw_metrics_summary.highly_skewed_count}</span>
            </div>
            <div className="flex justify-between">
              <span>Zero-Heavy:</span>
              <span className="font-medium">{currentSummary.raw_metrics_summary.zero_heavy_count}</span>
            </div>
            <div className="flex justify-between">
              <span>Bandwidth:</span>
              <span className="font-medium">{selectedBandwidth}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Small Multiples Grid - PDF Charts */}
      <div className="mb-6 border border-gray-200 rounded-lg bg-white p-4">
        <div className="grid grid-cols-4 gap-4">
          {displayAnalyses.map((analysis, index) => (
            <div key={`${analysis.index}-${selectedBandwidth}-${index}`} className="border border-gray-100 rounded p-2">
              <IndexDensityChart 
                analysis={analysis}
                width={200}
                height={150}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Explanation */}
      <div className="mt-4 bg-blue-50 p-4 rounded-lg">
        <h4 className="font-semibold text-blue-800 mb-2">Purpose: Quality Control Before Analysis</h4>
        <p className="text-blue-700 text-sm">
          These probability density function curves show the distribution shape of each acoustic index, 
          normalized to a 0-1 scale for comparison. Skewed distributions, multi-modal patterns, 
          or extreme outliers can indicate data quality issues that may affect downstream analysis. 
          The {selectedBandwidth} bandwidth contains {currentSummary.total_indices} acoustic indices 
          across {Object.keys(currentSummary.category_counts).length} categories.
        </p>
      </div>
    </div>
  );
}