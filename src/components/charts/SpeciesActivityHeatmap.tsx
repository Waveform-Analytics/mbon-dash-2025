/**
 * Species Activity Timeline Heatmap Component
 * Interactive heatmap showing species detection activity across time and stations
 * Built with Observable Plot for optimal performance and simplicity
 */

'use client';

import React, { useMemo, useState, useRef, useEffect } from 'react';
import * as Plot from '@observablehq/plot';
import * as d3 from 'd3';
import { 
  processTimelineData, 
  aggregateTimelineData, 
  type Detection 
} from '@/lib/utils/timelineProcessing';
import { ChartExport } from '@/components/export/ChartExport';

interface SpeciesActivityHeatmapProps {
  detections: Detection[];
  speciesMapping: Record<string, string>;
  deploymentMetadata?: any[];
  className?: string;
  height?: number;
  topSpeciesCount?: number;
}

export function SpeciesActivityHeatmap({
  detections,
  speciesMapping,
  deploymentMetadata = [],
  className = '',
  height = 500,
  topSpeciesCount = 12
}: SpeciesActivityHeatmapProps) {
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [containerWidth, setContainerWidth] = useState<number>(800);
  const plotRef = useRef<HTMLDivElement>(null);
  
  // Process data for heatmap
  const { processedData, availableStations } = useMemo(() => {
    if (!detections || detections.length === 0) {
      return { processedData: [], availableStations: [] };
    }

    // Process timeline data
    const timelineData = processTimelineData(
      detections,
      speciesMapping,
      deploymentMetadata
    );
    
    // Aggregate by month/station/species
    const aggregated = aggregateTimelineData(timelineData);
    
    // Filter by selected station if not "all"
    const filteredData = selectedStation === 'all' 
      ? aggregated 
      : aggregated.filter(d => d.station === selectedStation);
    
    // Get top species by detection count
    const speciesCount = new Map<string, number>();
    filteredData.forEach(point => {
      const current = speciesCount.get(point.species) || 0;
      speciesCount.set(point.species, current + point.detections);
    });

    const topSpecies = Array.from(speciesCount.entries())
      .sort(([,a], [,b]) => b - a)
      .slice(0, topSpeciesCount)
      .map(([species]) => species);

    // Filter to top species only
    const topSpeciesData = filteredData.filter(d => topSpecies.includes(d.species));
    
    // Get available stations
    const stations = Array.from(new Set(aggregated.map(d => d.station))).sort();
    
    return { 
      processedData: topSpeciesData, 
      availableStations: ['all', ...stations] 
    };
  }, [detections, speciesMapping, deploymentMetadata, selectedStation, topSpeciesCount]);

  // Handle container resize
  useEffect(() => {
    if (!plotRef.current) return;

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setContainerWidth(entry.contentRect.width);
      }
    });

    resizeObserver.observe(plotRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // Create the plot using Observable Plot
  useEffect(() => {
    if (!plotRef.current || processedData.length === 0) return;

    // Clear previous plot
    plotRef.current.innerHTML = '';

    // Aggregate data by year for mobile-friendly display
    const yearlyData = new Map<string, Map<string, number>>();
    
    processedData.forEach(d => {
      const year = d.month.split('-')[0]; // Extract year from "YYYY-MM"
      const key = `${year}-${d.species}`;
      
      if (!yearlyData.has(key)) {
        yearlyData.set(key, new Map([
          ['year', year],
          ['species', d.species], 
          ['detections', 0],
          ['station', d.station]
        ]));
      }
      
      const existing = yearlyData.get(key)!;
      existing.set('detections', (existing.get('detections') as number) + d.detections);
    });

    // Convert back to array format
    const plotData = Array.from(yearlyData.values()).map(dataMap => ({
      year: dataMap.get('year') as string,
      species: dataMap.get('species') as string,
      detections: dataMap.get('detections') as number,
      station: dataMap.get('station') as string
    }));

    // Get unique years in chronological order
    const uniqueYears = Array.from(new Set(plotData.map(d => d.year))).sort();

    // Create responsive dimensions
    const actualWidth = containerWidth || plotRef.current.clientWidth || 800;
    const isMobile = actualWidth < 600;
    
    // Create the plot
    const plot = Plot.plot({
      width: actualWidth,
      height: isMobile ? Math.min(height, 400) : height,
      marginLeft: isMobile ? 150 : 200,
      marginBottom: isMobile ? 60 : 80,
      marginTop: 40,
      marginRight: isMobile ? 60 : 80,
      
      // Explicit scale definitions
      x: {
        type: "band",  // Use band scale to suppress the warning
        domain: uniqueYears,  // Set explicit domain for chronological order
        label: "Year"
      },
      y: {
        type: "band", 
        label: "Species"
      },
      color: {
        type: "linear",
        scheme: "blues",
        domain: [0, d3.max(processedData, d => d.detections) || 1],
        label: "Detections",
        legend: true
      },
      
      // Marks
      marks: [
        // Heatmap cells aggregated by year
        Plot.cell(plotData, {
          x: "year",  // Use year instead of month
          y: "species", 
          fill: "detections",
          title: d => `${d.species}\n${d.year}\nDetections: ${d.detections}`,
          stroke: "white",
          strokeWidth: 1
        }),
        
        // X-axis with year labels - fixed font size
        Plot.axisX({
          label: "Year",
          fontSize: isMobile ? 14 : 16,
          tickSize: 6,
          labelAnchor: "center"
        }),
        
        // Y-axis - fixed font size
        Plot.axisY({
          label: "Species",
          fontSize: isMobile ? 11 : 12,
          tickSize: 6,
          labelAnchor: "center"
        })
      ],
      
      // Style - fixed base font size
      style: {
        fontSize: isMobile ? "11px" : "12px",
        fontFamily: "Inter, system-ui, sans-serif"
      }
    });

    plotRef.current.appendChild(plot);

    // Cleanup
    return () => {
      if (plotRef.current) {
        plotRef.current.innerHTML = '';
      }
    };
  }, [processedData, height, containerWidth]);

  if (!detections.length) {
    return (
      <div className={`flex items-center justify-center h-96 bg-slate-50 rounded-lg ${className}`}>
        <div className="text-slate-500 text-center">
          <div className="text-lg font-medium">No detection data available</div>
          <div className="text-sm">Timeline will appear when data is loaded</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header with controls */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">
            Species Activity Timeline
          </h3>
          <p className="text-sm text-slate-600 mt-1">
            Annual detection totals across {selectedStation === 'all' ? 'all stations' : `station ${selectedStation}`} (2018 vs 2021)
          </p>
        </div>
        
        {/* Controls section */}
        <div className="flex items-center space-x-4">
          {/* Station selector */}
          {availableStations.length > 1 && (
            <div className="flex items-center space-x-2">
              <label htmlFor="station-select" className="text-sm font-medium text-slate-700">
                Station:
              </label>
              <select
                id="station-select"
                value={selectedStation}
                onChange={(e) => setSelectedStation(e.target.value)}
                className="px-3 py-1.5 text-sm border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {availableStations.map(station => (
                  <option key={station} value={station}>
                    {station === 'all' ? 'All Stations' : station}
                  </option>
                ))}
              </select>
            </div>
          )}
          
          {/* Export buttons */}
          <ChartExport 
            chartRef={plotRef} 
            filename={`species-activity-timeline-${selectedStation}-${new Date().toISOString().split('T')[0]}`}
          />
        </div>
      </div>

      {/* Heatmap visualization */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <div ref={plotRef} style={{ width: '100%', minHeight: `${height}px` }} />
      </div>

      {/* Legend and context */}
      <div className="flex items-start space-x-6 text-xs text-slate-600">
        <div className="flex-1 space-y-1">
          <div className="font-medium text-slate-700">Data Context</div>
          <div>Showing top {topSpeciesCount} species by detection frequency</div>
          <div>
            Stations: {availableStations.filter(s => s !== 'all').join(', ')}
          </div>
          <div>
            Coverage: 2018-2021 marine biodiversity monitoring
          </div>
        </div>
        
        <div className="flex-1 space-y-1">
          <div className="font-medium text-slate-700">Visualization</div>
          <div>Hover over cells for detailed detection counts</div>
          <div>Darker colors indicate higher activity</div>
          <div>White gaps indicate periods with no deployments</div>
        </div>
      </div>
    </div>
  );
}

export default SpeciesActivityHeatmap;