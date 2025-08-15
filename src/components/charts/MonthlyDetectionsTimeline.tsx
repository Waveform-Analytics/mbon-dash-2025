'use client';

import React, { useState, useEffect, useRef } from 'react';
import * as Plot from "@observablehq/plot";
import { useMonthlyDetections, type MonthlyDetection } from '@/lib/hooks/useData';

interface MonthlyDetectionsTimelineProps {
  className?: string;
}

export default function MonthlyDetectionsTimeline({ className = "" }: MonthlyDetectionsTimelineProps) {
  const { data, loading, error } = useMonthlyDetections();
  const [selectedDetectionType, setSelectedDetectionType] = useState<string>('all');
  const containerRef = useRef<HTMLDivElement>(null);

  // Station color mapping
  const stationColors = {
    '9M': '#0ea5e9',   // Sky blue
    '14M': '#22c55e',  // Green
    '37M': '#f59e0b'   // Amber
  };

  // Month labels for x-axis
  const monthLabels = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  useEffect(() => {
    if (!data || !containerRef.current) return;

    // Filter data for selected detection type
    const filteredData = data.monthly_summary.filter(
      record => record.detection_type === selectedDetectionType
    );

    // Separate data by year for two-panel display
    const data2018 = filteredData.filter(d => d.year === 2018);
    const data2021 = filteredData.filter(d => d.year === 2021);

    const createPlot = () => {
      if (!containerRef.current) return null;
      
      // Clear previous plot
      containerRef.current.innerHTML = '';

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
        facet: {
          data: filteredData,
          y: "year",
          marginRight: 100
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
            fill: "station",
            stroke: "station",
            strokeWidth: 2,
            r: 6,
            fillOpacity: 0.8,
            tip: true
          }),
          
          // Year labels for each facet
          Plot.text(
            [{ year: 2018, label: "2018" }, { year: 2021, label: "2021" }],
            {
              fx: null, // Don't facet this mark
              fy: "year",
              x: 6.5, // Center of x-axis
              y: (d: any) => {
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

    // Set up resize observer for responsive behavior
    const resizeObserver = new ResizeObserver(() => {
      if (currentPlot) {
        currentPlot.remove();
      }
      currentPlot = createPlot();
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // Cleanup function
    return () => {
      if (currentPlot) {
        currentPlot.remove();
      }
      resizeObserver.disconnect();
    };
  }, [data, selectedDetectionType]);

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