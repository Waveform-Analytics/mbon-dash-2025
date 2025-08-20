'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import * as Plot from "@observablehq/plot";
import { useMonthlyDetections } from '@/lib/hooks/useData';

interface MonthlyDetectionsTimelineProps {
  className?: string;
}

export default function MonthlyDetectionsTimeline({ className = "" }: MonthlyDetectionsTimelineProps) {
  const { data, loading, error } = useMonthlyDetections();
  const [selectedDetectionType, setSelectedDetectionType] = useState<string>('all');
  const containerRef = useRef<HTMLDivElement>(null);

  // Station color mapping - memoized to prevent re-renders
  const stationColors = useMemo(() => ({
    '9M': '#0ea5e9',   // Sky blue
    '14M': '#22c55e',  // Green
    '37M': '#f59e0b'   // Amber
  }), []);

  // Month labels for x-axis - memoized to prevent re-renders
  const monthLabels = useMemo(() => [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ], []);

  useEffect(() => {
    if (!data || !containerRef.current) return;

    // Capture the container ref to avoid stale closure
    const container = containerRef.current;

    // Filter data for selected detection type
    const filteredData = data.monthly_summary.filter(
      record => record.detection_type === selectedDetectionType
    );

    
    let mounted = true; // Guard against unmounted component updates

    const createPlot = () => {
      if (!mounted) return null;
      if (!containerRef.current) return null;
      
      // Clear previous plot - more thorough cleanup
      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }

      // Get container width for responsive sizing
      const containerWidth = containerRef.current.clientWidth;
      
      // Create the plot with two vertical panels
      const plot = Plot.plot({
        width: Math.max(containerWidth - 48, 600), // Subtract padding, minimum 600px
        height: 500,
        marginTop: 40,
        marginBottom: 80,
        marginLeft: 80,
        marginRight: 120,
        grid: true,
        style: {
          fontSize: "14px",
          fontFamily: "Inter, system-ui, sans-serif"
        },
        
        // Two-panel layout with faceting by year
        fy: {
          domain: [2018, 2021],
          label: null,
          ticks: [] // Hide the year axis ticks/labels
        },
        
        // Y-axis configuration
        y: {
          label: "Number of detections",
          labelAnchor: "center",
          grid: true,
          nice: true
        },
        
        // X-axis configuration
        x: {
          label: "Month",
          domain: [1, 12],
          ticks: 12,
          tickFormat: (d: number) => monthLabels[d - 1],
          grid: true
        },
        
        // Color scale for stations
        color: {
          domain: ['9M', '14M', '37M'],
          range: [stationColors['9M'], stationColors['14M'], stationColors['37M']],
          legend: true,
          label: "Station"
        },
        
        marks: [
          // Scatter plot points
          Plot.dot(filteredData, {
            x: "month",
            y: "count",
            fy: "year", // Add facet year channel
            fill: "station",
            stroke: "station",
            strokeWidth: 2,
            r: 6,
            fillOpacity: 0.8,
            tip: {
              format: {
                fy: false, // Hide the facet year from tooltip
                year: (d: number) => d.toString(), // Format year without comma
                month: (d: number) => monthLabels[d - 1], // Show month name
                count: true, // Keep default formatting for count
                station: true // Keep default formatting for station
              }
            }
          }),
          
          // Year labels for each facet
          Plot.text(
            [{ year: 2018, label: "2018" }, { year: 2021, label: "2021" }],
            {
              fy: "year",
              x: 6.5, // Center of x-axis
              y: (d: { year: number; label: string }) => {
                const yearData = filteredData.filter(record => record.year === d.year);
                const maxCount = Math.max(...yearData.map(record => record.count), 0);
                return maxCount * 0.9; // Position near top of panel
              },
              text: "label",
              fontSize: 16,
              fontWeight: "bold",
              fill: "#374151",
              textAnchor: "middle"
            }
          )
        ]
      });

      // Append plot to container
      containerRef.current.appendChild(plot);
      
      return plot;
    };

    // Create initial plot
    let currentPlot = createPlot();

    // Set up resize observer for responsive behavior with debounce
    let resizeTimeout: NodeJS.Timeout;
    const resizeObserver = new ResizeObserver(() => {
      if (!mounted) return;
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (!mounted) return;
        if (currentPlot) {
          currentPlot.remove();
        }
        currentPlot = createPlot();
      }, 100); // Debounce resize events
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // Cleanup function
    return () => {
      mounted = false; // Prevent updates after unmount
      clearTimeout(resizeTimeout); // Clear any pending resize
      if (currentPlot) {
        currentPlot.remove();
      }
      resizeObserver.disconnect();
      // Extra cleanup - clear the container using captured ref
      if (container) {
        while (container.firstChild) {
          container.removeChild(container.firstChild);
        }
      }
    };
  }, [data, selectedDetectionType, monthLabels, stationColors]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-96 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading monthly detection data...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-6 bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <p className="text-red-800">Error loading data: {error.message}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`p-6 bg-gray-50 border border-gray-200 rounded-lg ${className}`}>
        <p className="text-gray-600">No data available</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      {/* Detection Type Selector */}
      <div className="mb-6">
        <label htmlFor="detection-type" className="block text-sm font-medium text-gray-700 mb-2">
          Detection Type:
        </label>
        <select
          id="detection-type"
          value={selectedDetectionType}
          onChange={(e) => setSelectedDetectionType(e.target.value)}
          className="block w-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          {[...new Set(data.detection_types)].map((type) => (
            <option key={type} value={type}>
              {data.type_labels[type] || type}
            </option>
          ))}
        </select>
      </div>

      {/* Chart Container */}
      <div ref={containerRef} className="w-full" />

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-3 gap-4 text-sm text-gray-600">
        <div className="text-center">
          <div className="font-medium text-gray-900">Years Compared</div>
          <div>{data.metadata.years_included.join(', ')}</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-gray-900">Stations</div>
          <div>{data.metadata.stations_included.join(', ')}</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-gray-900">Detection Types</div>
          <div>{data.detection_types.length} available</div>
        </div>
      </div>
    </div>
  );
}