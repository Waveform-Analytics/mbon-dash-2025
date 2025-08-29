'use client';

import { useState, useEffect, useRef, useMemo } from 'react';
import * as Plot from '@observablehq/plot';
import { useAcousticSummary } from '@/lib/hooks/useViewData';

interface BandwidthComparisonBoxPlotProps {
  className?: string;
}

export default function BandwidthComparisonBoxPlot({ className = "" }: BandwidthComparisonBoxPlotProps) {
  const [selectedMetric, setSelectedMetric] = useState<string>('');
  const containerRef = useRef<HTMLDivElement>(null);

  // Load the acoustic summary data (optimized view)
  const { data: acousticSummary, loading, error } = useAcousticSummary();

  // Get available acoustic metrics from the summary data
  const availableMetrics = useMemo(() => {
    if (!acousticSummary || !acousticSummary.acoustic_summary.length) return [];
    
    const firstStation = acousticSummary.acoustic_summary[0];
    return Object.keys(firstStation.acoustic_metrics || {}).sort();
  }, [acousticSummary]);

  // Set initial metric selection
  useEffect(() => {
    if (availableMetrics.length > 0 && !selectedMetric) {
      // Try to select a diversity-related metric first
      const initialMetric = availableMetrics.find(metric => 
        metric.toLowerCase().includes('diversity') || 
        metric.toLowerCase().includes('h_') ||
        metric.toLowerCase().includes('aci')
      ) || availableMetrics[0];
      setSelectedMetric(initialMetric);
    }
  }, [availableMetrics, selectedMetric]);

  // Prepare comparison data from acoustic summary
  const comparisonData = useMemo(() => {
    if (!selectedMetric || !acousticSummary) return [];

    const data: Array<{
      station: string;
      metric: string;
      mean: number;
      std: number;
      type: 'Mean' | 'Std Dev';
      value: number;
    }> = [];
    
    // Convert summary data to comparison format
    acousticSummary.acoustic_summary.forEach(stationData => {
      const metricStats = stationData.acoustic_metrics[selectedMetric];
      if (metricStats && metricStats.mean !== null && metricStats.std !== null) {
        // Add mean value
        data.push({
          station: stationData.station,
          metric: selectedMetric,
          mean: metricStats.mean,
          std: metricStats.std,
          type: 'Mean',
          value: metricStats.mean
        });
        
        // Add standard deviation value
        data.push({
          station: stationData.station,
          metric: selectedMetric,
          mean: metricStats.mean,
          std: metricStats.std,
          type: 'Std Dev',
          value: metricStats.std
        });
      }
    });

    return data;
  }, [selectedMetric, acousticSummary]);

  // Create the plot
  useEffect(() => {
    if (comparisonData.length === 0 || !containerRef.current || !selectedMetric) return;

    const container = containerRef.current;
    container.innerHTML = '';

    // Get unique stations for x-axis domain
    const stations = [...new Set(comparisonData.map(d => d.station))].sort();

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
        domain: ['Mean', 'Std Dev'],
        paddingOuter: 0.2,
        paddingInner: 0.1,  // Small space between metrics within station
        axis: null  // Hide the metric axis since it's shown in the legend
      },
      
      y: {
        label: `↑ ${selectedMetric} Value`,
        labelAnchor: "center", 
        labelOffset: 45,
        grid: true,
        nice: true,
        tickFormat: "~s"
      },
      
      color: {
        domain: ['Mean', 'Std Dev'],
        range: ['#0ea5e9', '#f59e0b'], // Ocean blue and coral amber
        legend: true,
        label: "Statistic"
      },
      
      marks: [
        // Background grid
        Plot.gridY({
          stroke: "#e2e8f0",
          strokeWidth: 0.5,
          strokeDasharray: "2,2"
        }),
        
        // Bar chart grouped by station and metric type
        Plot.rectY(comparisonData, {
          fx: "station",  // Facet by station
          x: "type", // Group by mean/std within station
          y: "value",
          fill: "type",
          stroke: "type",
          strokeWidth: 1.5,
          fillOpacity: 0.7,
          tip: {
            format: {
              fx: false, // Hide station from tooltip (already in facet)
              station: true,
              metric: true,
              value: (d: number) => d.toFixed(4),
              type: true
            }
          }
        })
      ]
    });

    container.appendChild(plot);

    return () => {
      if (plot) plot.remove();
    };
  }, [comparisonData, selectedMetric]);

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className} p-8`}>
        <div className="flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-600 text-sm">Loading acoustic metrics comparison...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !acousticSummary) {
    return (
      <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className} p-8`}>
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Data</h3>
          <p className="text-red-600 text-sm">{error || 'No acoustic summary data available'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-xl font-semibold text-slate-800">
          Acoustic Metrics Comparison: {selectedMetric || 'Select a Metric'}
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Compare mean values and standard deviations across monitoring stations
        </p>
      </div>
      
      {/* Controls */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Metric Selector */}
          <div>
            <label htmlFor="metric" className="block text-sm font-medium text-gray-700 mb-2">
              Acoustic Metric:
            </label>
            <select
              id="metric"
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select metric...</option>
              {availableMetrics.map((metric) => (
                <option key={metric} value={metric}>
                  {metric}
                </option>
              ))}
            </select>
          </div>

          {/* Data Source Info */}
          <div className="flex items-end">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Data Source:</span> Acoustic Summary View<br/>
              <span className="text-xs text-gray-500">19.6KB optimized (vs 166MB raw data)</span>
            </div>
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
      {comparisonData.length > 0 && (
        <div className="px-6 pb-6">
          <div className="bg-blue-50 p-3 rounded-lg">
            <div className="font-medium text-blue-800 mb-2">Acoustic Metrics Comparison</div>
            <div className="text-blue-700 text-sm">
              Each bar shows the <strong>{selectedMetric}</strong> acoustic metric values across stations. 
              The blue bars represent mean values, while orange bars show standard deviations. 
              This comparison helps identify which stations have the highest acoustic activity and variability 
              for the selected metric. Data is aggregated from the acoustic summary view for fast loading.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}