'use client';

import { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { useIndicesHeatmap } from '@/lib/data/useIndicesHeatmap';
// Types are imported but not used in this file currently

interface AcousticIndicesHeatmapProps {
  className?: string;
}

export default function AcousticIndicesHeatmap({ className = '' }: AcousticIndicesHeatmapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  // State for user selections (2021 is the only year with acoustic indices data)
  const [selectedIndex, setSelectedIndex] = useState<string>('');
  const [selectedStation, setSelectedStation] = useState<string>('');
  const [selectedBandwidth, setSelectedBandwidth] = useState<string>('');
  const selectedYear = 2021; // Fixed to 2021 (only year with acoustic indices)

  // Fetch data and metadata
  const { data, loading, error, metadata } = useIndicesHeatmap({
    index: selectedIndex,
    station: selectedStation,
    year: selectedYear,
    bandwidth: selectedBandwidth,
  });

  // Dimensions
  const margin = useMemo(() => ({ top: 40, right: 40, bottom: 80, left: 60 }), []);
  const width = 700 - margin.left - margin.right;
  const height = 300 - margin.top - margin.bottom;
  const totalHeight = height + margin.top + margin.bottom + 60; // +60 for legend

  // Set initial selections when metadata loads
  useEffect(() => {
    if (!metadata) return;

    if (metadata.available_indices.length > 0 && !selectedIndex) {
      setSelectedIndex('ACI'); // Default to ACI (Acoustic Complexity Index)
    }
    if (metadata.stations.length > 0 && !selectedStation) {
      setSelectedStation('14M'); // Default to station 14M (has most reliable data)
    }
    // Note: Year is fixed to 2021 (only year with acoustic indices data)
    if (metadata.bandwidths.length > 0 && !selectedBandwidth) {
      setSelectedBandwidth('FullBW'); // Default to Full Bandwidth (has more data)
    }
  }, [metadata, selectedIndex, selectedStation, selectedBandwidth]);

  useEffect(() => {
    if (!containerRef.current || !selectedIndex || !selectedStation || !selectedBandwidth) return;
    
    // If data is null (loading new data), clear the visualization immediately
    if (!data) {
      const container = d3.select(containerRef.current);
      const cellsGroup = container.select('.cells-group');
      
      if (!cellsGroup.empty()) {
        // Immediately hide existing cells when data becomes null
        cellsGroup.selectAll('rect.heatmap-cell')
          .transition()
          .duration(150)
          .style('opacity', 0)
          .remove();
      }
      return;
    }

    const container = d3.select(containerRef.current);
    
    // Check if the complete structure exists
    let svgContainer: d3.Selection<d3.BaseType, unknown, null, undefined> = container.select('div.heatmap-svg-container');
    let legendContainer: d3.Selection<d3.BaseType, unknown, null, undefined> = container.select('div.legend-container');
    
    // Create complete structure if it doesn't exist (only happens first time)
    if (svgContainer.empty()) {
      // Clear any existing content first
      container.selectAll('*').remove();
      // Create container structure
      svgContainer = (container.append('div')
        .attr('class', 'heatmap-svg-container')
        .style('position', 'relative') as unknown) as d3.Selection<d3.BaseType, unknown, null, undefined>;
      
      legendContainer = (container.append('div')
        .attr('class', 'legend-container')
        .style('margin-top', '15px')
        .style('display', 'flex')
        .style('align-items', 'center')
        .style('justify-content', 'center')
        .style('gap', '10px') as unknown) as d3.Selection<d3.BaseType, unknown, null, undefined>;
      
      // Create SVG
      const svg = svgContainer.append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('border', '1px solid #e0e0e0')
        .style('border-radius', '4px');
      
      const g = svg.append('g')
        .attr('class', 'main-group')
        .attr('transform', `translate(${margin.left},${margin.top})`);
        
      // Create persistent groups for different elements
      g.append('g').attr('class', 'cells-group');
      g.append('g').attr('class', 'x-axis');
      g.append('g').attr('class', 'y-axis');
      g.append('text').attr('class', 'x-label');
      g.append('text').attr('class', 'y-label');
      
      // Create legend structure
      legendContainer.append('span')
        .attr('class', 'legend-low')
        .style('font-size', '11px')
        .style('color', '#666')
        .text('Low');
      
      const legendGradient = legendContainer.append('div')
        .attr('class', 'legend-gradient-container')
        .style('height', '15px')
        .style('width', '200px')
        .style('border', '1px solid #ccc')
        .style('border-radius', '2px');
      
      const legendSvg = legendGradient.append('svg')
        .attr('width', 200)
        .attr('height', 15);
      
      const defs = legendSvg.append('defs');
      defs.append('linearGradient')
        .attr('id', 'indices-legend-gradient');
      
      legendSvg.append('rect')
        .attr('class', 'legend-gradient-rect')
        .attr('width', 200)
        .attr('height', 15)
        .attr('fill', 'url(#indices-legend-gradient)');
      
      legendContainer.append('span')
        .attr('class', 'legend-high')
        .style('font-size', '11px')
        .style('color', '#666')
        .text('High');
      
      legendContainer.append('span')
        .attr('class', 'legend-range')
        .style('font-size', '11px')
        .style('color', '#666');
    }
    
    // Get references to existing elements
    const svg = svgContainer.select('svg');
    const g = svg.select('g.main-group');
    
    // Clean up tooltip
    d3.select('body').selectAll('div.d3-tooltip').remove();

    const heatmapData = data.data;
    const cellsGroup = g.select('.cells-group');

    if (heatmapData.length === 0) {
      // Fade out existing cells first, then show no data message
      cellsGroup.selectAll('rect.heatmap-cell')
        .transition()
        .duration(200)
        .style('opacity', 0)
        .remove();
      
      // Remove any existing no-data message
      cellsGroup.select('text.no-data-message').remove();
      
      // Add no data message with fade in
      cellsGroup.append('text')
        .attr('class', 'no-data-message')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .style('fill', '#999')
        .style('font-style', 'italic')
        .style('font-size', '14px')
        .style('opacity', 0)
        .text('No data available for this selection')
        .transition()
        .duration(300)
        .style('opacity', 1);
      return;
    }

    // Remove any no-data message
    cellsGroup.select('text.no-data-message')
      .transition()
      .duration(200)
      .style('opacity', 0)
      .remove();

    // Create color scale based on value range for this index
    const valueRange = data.metadata.value_ranges[selectedIndex] || [0, 1];
    const colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain(valueRange);

    // Create scales
    const dates = [...new Set(heatmapData.map(d => d.date))].sort();
    const hours = [...new Set(heatmapData.map(d => d.hour))].sort((a, b) => a - b);
    
    const xScale = d3.scaleBand()
      .domain(dates)
      .range([0, width])
      .padding(0.02);

    const yScale = d3.scaleBand()
      .domain(hours.map(h => h.toString()))
      .range([0, height])
      .padding(0.02);

    // Create data map for fast lookup
    const dataMap = new Map();
    heatmapData.forEach(d => {
      const key = `${d.date}-${d.hour}`;
      dataMap.set(key, d.value);
    });

    // Create or select tooltip
    let tooltip: d3.Selection<d3.BaseType, unknown, HTMLElement, unknown> = d3.select('body').select('div.d3-tooltip');
    if (tooltip.empty()) {
      tooltip = (d3.select('body').append('div')
        .attr('class', 'd3-tooltip')
        .style('position', 'absolute')
        .style('padding', '8px 12px')
        .style('background', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('z-index', '1000')
        .style('opacity', '0')
        .style('transition', 'opacity 0.2s') as unknown) as d3.Selection<d3.BaseType, unknown, HTMLElement, unknown>;
    }

    // Create unique keys for data binding
    const keyedData = heatmapData.map(d => ({
      ...d,
      key: `${d.date}-${d.hour}`
    }));

    // Draw heatmap cells in the cells group with proper data binding
    const cells = cellsGroup.selectAll('rect.heatmap-cell')
      .data(keyedData, (d: unknown) => (d as {key: string}).key);
    
    // Remove old cells first (cells that no longer exist in new data)
    cells.exit()
      .transition()
      .duration(200)
      .style('opacity', 0)
      .remove();
    
    // Enter new cells
    const cellsEnter = cells.enter()
      .append('rect')
      .attr('class', 'heatmap-cell')
      .attr('x', d => xScale(d.date) || 0)
      .attr('y', d => yScale(d.hour.toString()) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .style('cursor', 'pointer')
      .style('opacity', 0);
    
    // Update all cells (new and existing) - position first, then transition colors and opacity
    const allCells = cells.merge(cellsEnter as unknown as d3.Selection<d3.BaseType, { key: string; date: string; hour: number; value: number; index_name: string; station: string; year: number; bandwidth: string; }, d3.BaseType, unknown>);
    
    // Update positions immediately (no transition for layout)
    allCells
      .attr('x', d => xScale(d.date) || 0)
      .attr('y', d => yScale(d.hour.toString()) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth());
    
    // Transition colors and opacity
    allCells
      .transition()
      .duration(300)
      .attr('fill', d => colorScale(d.value))
      .style('opacity', 1);
    
    // Add hover interactions to all cells (apply to the merged selection)
    allCells
      .on('mouseover', function(event, d: {date: string; hour: number; value: number}) {
        tooltip
          .style('opacity', 1)
          .html(`
            <strong>${new Date(d.date).toLocaleDateString()}</strong><br>
            Hour: ${d.hour}:00<br>
            ${selectedIndex}: ${d.value.toFixed(2)}
          `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', () => {
        tooltip.style('opacity', 0);
      });

    // Update axes
    const xAxis = d3.axisBottom(xScale)
      .tickFormat((d: unknown) => {
        const date = new Date(d as string);
        return d3.timeFormat('%b %d')(date);
      })
      .tickValues(dates.filter((_, i) => i % Math.ceil(dates.length / 8) === 0)); // Show ~8 ticks

    const yAxis = d3.axisLeft(yScale)
      .tickFormat((d: unknown) => `${d}:00`)
      .tickValues(['0', '4', '8', '12', '16', '20']); // Show every 4 hours

    // Update x-axis
    const xAxisSelection = g.select('.x-axis')
      .attr('transform', `translate(0,${height})`)
      .style('font-size', '11px')
      .style('color', '#666')
      .call(xAxis as unknown as (selection: unknown) => void);
    
    xAxisSelection.selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end');

    // Update y-axis
    g.select('.y-axis')
      .style('font-size', '11px')
      .style('color', '#666')
      .call(yAxis as unknown as (selection: unknown) => void);

    // Update axis labels
    g.select('.x-label')
      .attr('x', width / 2)
      .attr('y', height + 60)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('color', '#333')
      .text('Date');

    g.select('.y-label')
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -40)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('color', '#333')
      .text('Hour of Day');

    // Update legend smoothly
    const linearGradient = legendContainer.select('#indices-legend-gradient');
    const stops = d3.range(0, 1.1, 0.1);
    
    // Smooth gradient transition
    const gradientStops = linearGradient.selectAll('stop')
      .data(stops);
    
    gradientStops.enter()
      .append('stop')
      .merge(gradientStops as unknown as d3.Selection<SVGStopElement, number, d3.BaseType, unknown>)
      .attr('offset', (d: number) => `${d * 100}%`)
      .transition()
      .duration(300)
      .attr('stop-color', (d: number) => colorScale(valueRange[0] + d * (valueRange[1] - valueRange[0])));
    
    gradientStops.exit().remove();
    
    // Update legend range text with transition
    const rangeText = legendContainer.select('.legend-range');
    const newRangeText = `${valueRange[0].toFixed(1)} - ${valueRange[1].toFixed(1)} ${selectedIndex}`;
    
    rangeText
      .transition()
      .duration(150)
      .style('opacity', 0)
      .on('end', function() {
        d3.select(this)
          .text(newRangeText)
          .transition()
          .duration(150)
          .style('opacity', 1);
      });

    // Cleanup function
    return () => {
      d3.select('body').selectAll('.tooltip').remove();
    };

  }, [data, selectedIndex, selectedStation, selectedBandwidth, width, height, margin]);

  // Always render the container with consistent height
  const showLoadingOverlay = loading && (selectedIndex || selectedStation || selectedBandwidth);
  const showError = error && !loading;

  return (
    <div className={className}>
      {/* Controls */}
      <div className="mb-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="font-medium">2021 Data</span>
            <span>•</span>
            <span>Acoustic indices are available for 2021 only</span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Acoustic Index
            </label>
            <select
              value={selectedIndex}
              onChange={(e) => setSelectedIndex(e.target.value)}
              className="px-3 py-2 border border-border rounded-md text-sm bg-background"
            >
              {metadata?.available_indices?.map(index => (
                <option key={index} value={index}>
                  {index}
                </option>
              )) || []}
            </select>
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Station
            </label>
            <select
              value={selectedStation}
              onChange={(e) => setSelectedStation(e.target.value)}
              className="px-3 py-2 border border-border rounded-md text-sm bg-background"
            >
              {metadata?.stations?.map(station => (
                <option key={station} value={station}>
                  Station {station}
                </option>
              )) || []}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Bandwidth
            </label>
            <select
              value={selectedBandwidth}
              onChange={(e) => setSelectedBandwidth(e.target.value)}
              className="px-3 py-2 border border-border rounded-md text-sm bg-background"
            >
              {metadata?.bandwidths?.map(bandwidth => (
                <option key={bandwidth} value={bandwidth}>
                  {bandwidth === 'FullBW' ? 'Full Bandwidth' : bandwidth}
                </option>
              )) || []}
            </select>
          </div>
        </div>
      </div>

      {/* Performance Info */}
      {data && (
        <div className="mb-4 text-xs text-muted-foreground">
          Showing {data.data.length.toLocaleString()} data points • 
          Processed in {data.metadata.processing_time_ms}ms
        </div>
      )}

      {/* Heatmap Container with consistent height */}
      <div className="relative w-full" style={{ minHeight: `${totalHeight}px` }}>
        {/* Main heatmap container */}
        <div ref={containerRef} className="w-full" style={{ minHeight: `${totalHeight}px` }} />
        
        {/* Loading overlay */}
        {showLoadingOverlay && (
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              <span className="text-muted-foreground">Loading heatmap...</span>
            </div>
          </div>
        )}
        
        {/* Error overlay */}
        {showError && (
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center">
            <div className="text-center">
              <div className="text-destructive mb-2">Error loading heatmap</div>
              <div className="text-sm text-muted-foreground">{error?.message}</div>
            </div>
          </div>
        )}
        
        {/* No metadata state */}
        {!metadata && !loading && !error && (
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center">
            <div className="text-muted-foreground">No metadata available</div>
          </div>
        )}
      </div>
    </div>
  );
}