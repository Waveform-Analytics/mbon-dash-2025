'use client';

import { useState, useEffect, useMemo, useRef } from 'react';
import * as Plot from '@observablehq/plot';
import { useAcousticSummary } from '@/lib/hooks/useViewData';

export default function AcousticIndicesHeatmap() {
  const [selectedMetric, setSelectedMetric] = useState<'mean' | 'std'>('mean');
  const containerRef = useRef<HTMLDivElement>(null);
  
  const { data: acousticSummary, loading, error } = useAcousticSummary();

  // Get available acoustic indices from the summary data
  const availableIndices = useMemo(() => {
    if (!acousticSummary || !acousticSummary.acoustic_summary.length) return [];
    
    const firstStation = acousticSummary.acoustic_summary[0];
    return Object.keys(firstStation.acoustic_metrics || {}).sort();
  }, [acousticSummary]);

  // Prepare heatmap data showing acoustic index statistics across stations
  const heatmapData = useMemo(() => {
    if (!acousticSummary) return [];
    
    return acousticSummary.acoustic_summary.flatMap(stationData => 
      Object.entries(stationData.acoustic_metrics || {}).map(([index, stats]) => ({
        station: stationData.station,
        index,
        mean: stats.mean,
        std: stats.std,
        // Use selected metric for visualization
        value: selectedMetric === 'mean' ? stats.mean : stats.std
      }))
    );
  }, [acousticSummary, selectedMetric]);

  useEffect(() => {
    if (!heatmapData.length || !containerRef.current) return;

    const plot = Plot.plot({
      title: `Acoustic Index ${selectedMetric === 'mean' ? 'Mean Values' : 'Standard Deviations'} by Station`,
      width: 1000,
      height: 400,
      marginLeft: 150,
      marginBottom: 60,
      color: {
        scheme: "viridis",
        legend: true,
        label: selectedMetric === 'mean' ? "Mean Value" : "Standard Deviation"
      },
      marks: [
        Plot.cell(heatmapData, {
          x: "station",
          y: "index", 
          fill: "value",
          title: d => `${d.index} at ${d.station}: ${selectedMetric} = ${d.value?.toFixed(4)}`
        }),
        Plot.text(heatmapData, {
          x: "station",
          y: "index",
          text: d => d.value?.toFixed(2),
          fill: "white",
          fontSize: 10
        })
      ]
    });

    containerRef.current.replaceChildren(plot);

    return () => plot.remove();
  }, [heatmapData, selectedMetric]);

  if (loading) {
    return (
      <div className="chart-container">
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-ocean-600"></div>
          <span className="ml-2 text-slate-600">Loading acoustic indices heatmap...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-container">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error loading acoustic indices: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-800 mb-1">
            Acoustic Indices Overview
          </h3>
          <p className="text-sm text-slate-600">
            Aggregated acoustic metrics across monitoring stations (optimized view)
          </p>
        </div>
        
        {/* Metric Selection */}
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-slate-700">Show:</label>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value as 'mean' | 'std')}
            className="px-3 py-1 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ocean-500"
          >
            <option value="mean">Mean Values</option>
            <option value="std">Standard Deviations</option>
          </select>
        </div>
      </div>

      {/* Performance indicator */}
      <div className="mb-4 text-xs text-slate-500">
        Loading from optimized acoustic summary view • {acousticSummary ? '27.5 KB' : '...'} (vs 166MB raw data)
      </div>

      <div ref={containerRef} className="w-full overflow-x-auto"></div>
      
      {/* Summary stats */}
      {acousticSummary && (
        <div className="mt-4 text-sm text-slate-600">
          <p>
            Showing {availableIndices.length} acoustic indices across {acousticSummary.acoustic_summary.length} stations
          </p>
        </div>
      )}
    </div>
  );
}