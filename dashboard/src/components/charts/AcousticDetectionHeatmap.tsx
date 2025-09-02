'use client';

import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useViewData } from '@/lib/data/useViewData';

interface DetectionData {
  date: string;
  hour: number;
  value: number;
  station: string;
  year: number;
  detection_type: string;
  detection_type_short: string;
  dayOfYear: number;
  timestamp: string;
}

interface HeatmapData {
  metadata: {
    detection_types: Array<{
      long_name: string;
      short_name: string;
      type: string;
    }>;
    stations: string[];
    years: number[];
    value_ranges: Record<string, [number, number]>;
    hours: number[];
  };
  data: DetectionData[];
}

interface AcousticDetectionHeatmapProps {
  className?: string;
}

export default function AcousticDetectionHeatmap({ className = '' }: AcousticDetectionHeatmapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { data, loading, error } = useViewData<HeatmapData>('heatmap.json');
  
  const [selectedDetection, setSelectedDetection] = useState<string>('');
  const [selectedStation, setSelectedStation] = useState<string>('');

  // Dimensions
  const margin = { top: 40, right: 40, bottom: 80, left: 60 };
  const width = 700 - margin.left - margin.right;
  const height = 300 - margin.top - margin.bottom;

  useEffect(() => {
    if (!data) return;

    // Set initial selections
    if (data.metadata.detection_types.length > 0 && !selectedDetection) {
      setSelectedDetection(data.metadata.detection_types[0].long_name);
    }
    if (data.metadata.stations.length > 0 && !selectedStation) {
      setSelectedStation(data.metadata.stations[0]);
    }
  }, [data, selectedDetection, selectedStation]);

  useEffect(() => {
    if (!containerRef.current || !data || !selectedDetection || !selectedStation) return;

    const container = d3.select(containerRef.current);
    container.selectAll('*').remove();

    // Filter data for both years
    const yearData2018 = data.data.filter(d => 
      d.detection_type === selectedDetection &&
      d.station === selectedStation &&
      d.year === 2018
    );
    
    const yearData2021 = data.data.filter(d => 
      d.detection_type === selectedDetection &&
      d.station === selectedStation &&
      d.year === 2021
    );

    // Create color scale
    const valueRange = data.metadata.value_ranges[selectedDetection] || [0, 1];
    const colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain(valueRange);

    // Create single SVG container for both heatmaps
    const totalHeight = (height + margin.top + margin.bottom) * 2 - margin.bottom; // Remove bottom margin from first plot
    const svg = container.append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', totalHeight)
      .style('border', '1px solid #e0e0e0')
      .style('border-radius', '4px');

    // Create year panels
    [2018, 2021].forEach((year, index) => {
      const yearData = year === 2018 ? yearData2018 : yearData2021;
      
      // Calculate y offset for each plot
      const yOffset = index * (height + margin.top);

      if (yearData.length === 0) {
        svg.append('text')
          .attr('x', (width + margin.left + margin.right) / 2)
          .attr('y', yOffset + height / 2)
          .attr('text-anchor', 'middle')
          .style('fill', '#999')
          .style('font-style', 'italic')
          .text('No data available for this selection');
        return;
      }

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${yOffset + margin.top})`);

      // Create scales
      const xScale = d3.scaleTime()
        .domain([new Date(year, 0, 1), new Date(year, 11, 31)])
        .range([0, width]);

      const yScale = d3.scaleBand()
        .domain(data.metadata.hours.map(h => h.toString()))
        .range([0, height])
        .padding(0.02);

      // Create a map for fast lookup
      const dataMap = new Map();
      yearData.forEach(d => {
        const key = `${d.dayOfYear}-${d.hour}`;
        dataMap.set(key, d.value);
      });

      // Create grid
      const cellWidth = width / 365;
      const cellHeight = yScale.bandwidth();

      // Create tooltip
      const tooltip = d3.select('body').append('div')
        .style('position', 'absolute')
        .style('padding', '8px 12px')
        .style('background', 'rgba(0, 0, 0, 0.8)')
        .style('color', 'white')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('z-index', '1000')
        .style('opacity', '0')
        .style('transition', 'opacity 0.2s');

      // Draw cells
      for (let day = 1; day <= 365; day++) {
        for (const hour of data.metadata.hours) {
          const key = `${day}-${hour}`;
          const value = dataMap.get(key) || 0;
          const x = (day - 1) * cellWidth;
          const y = yScale(hour.toString()) || 0;
          const date = new Date(year, 0, day);

          const cell = g.append('rect')
            .attr('x', x)
            .attr('y', y)
            .attr('width', cellWidth)
            .attr('height', cellHeight)
            .attr('fill', value > 0 ? colorScale(value) : '#f8f9fa')
            .attr('stroke', value > 0 ? 'none' : '#e9ecef')
            .attr('stroke-width', 0.5);

          if (value > 0) {
            cell
              .on('mouseover', function(event) {
                tooltip
                  .style('opacity', 1)
                  .html(`
                    <strong>${date.toLocaleDateString()}</strong><br>
                    Hour: ${hour}:00<br>
                    Detections: ${value}
                  `)
                  .style('left', (event.pageX + 10) + 'px')
                  .style('top', (event.pageY - 10) + 'px');
              })
              .on('mouseout', () => {
                tooltip.style('opacity', 0);
              });
          }
        }
      }

      // Add axes
      const xAxis = d3.axisBottom(xScale)
        .tickFormat((d: unknown) => d3.timeFormat('%b')(d as Date))
        .ticks(d3.timeMonth.every(1));

      const yAxis = d3.axisLeft(yScale)
        .tickFormat((d: unknown) => `${d}:00`)
        .tickValues([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22].map(h => h.toString())); // Show only even hours

      // Only show x-axis on the bottom plot (2021)
      if (year === 2021) {
        g.append('g')
          .attr('transform', `translate(0,${height})`)
          .style('font-size', '11px')
          .style('color', '#666')
          .call(xAxis as unknown as (selection: d3.Selection<SVGGElement, unknown, null, undefined>) => void);
      }

      g.append('g')
        .style('font-size', '11px')
        .style('color', '#666')
        .call(yAxis as unknown as (selection: d3.Selection<SVGGElement, unknown, null, undefined>) => void);

      // Add year label to the right side of each plot (rotated 90 degrees clockwise)
      g.append('text')
        .attr('x', width + 15)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('transform', `rotate(90, ${width + 15}, ${height / 2})`)
        .style('font-size', '14px')
        .style('font-weight', '600')
        .style('color', '#333')
        .text(year.toString());

      // Add y-axis label only on the left plot (2018)
      if (year === 2018) {
        g.append('text')
          .attr('transform', 'rotate(-90)')
          .attr('x', -height / 2)
          .attr('y', -40)
          .attr('text-anchor', 'middle')
          .style('font-size', '12px')
          .style('font-weight', '600')
          .style('color', '#333')
          .text('Hour of Day');
      }
    });

    // Create legend
    const legendContainer = container.append('div')
      .style('margin-top', '15px')
      .style('display', 'flex')
      .style('align-items', 'center')
      .style('justify-content', 'center')
      .style('gap', '10px');

    legendContainer.append('span')
      .style('font-size', '11px')
      .style('color', '#666')
      .text('Low');

    const legendGradient = legendContainer.append('div')
      .style('height', '15px')
      .style('width', '200px')
      .style('border', '1px solid #ccc')
      .style('border-radius', '2px');

    const legendSvg = legendGradient.append('svg')
      .attr('width', 200)
      .attr('height', 15);

    const defs = legendSvg.append('defs');
    const linearGradient = defs.append('linearGradient')
      .attr('id', 'legend-gradient');

    const stops = d3.range(0, 1.1, 0.1);
    linearGradient.selectAll('stop')
      .data(stops)
      .enter()
      .append('stop')
      .attr('offset', (d: number) => `${d * 100}%`)
      .attr('stop-color', (d: number) => colorScale(valueRange[0] + d * (valueRange[1] - valueRange[0])));

    legendSvg.append('rect')
      .attr('width', 200)
      .attr('height', 15)
      .attr('fill', 'url(#legend-gradient)');

    legendContainer.append('span')
      .style('font-size', '11px')
      .style('color', '#666')
      .text('High');

    legendContainer.append('span')
      .style('font-size', '11px')
      .style('color', '#666')
      .text(`${valueRange[0]} - ${valueRange[1]} detections`);

  }, [data, selectedDetection, selectedStation]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-muted-foreground">Loading heatmap data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-destructive">Error loading heatmap data: {error.message}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-muted-foreground">No heatmap data available</div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Controls */}
      <div className="mb-6 flex gap-4 items-center flex-wrap">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Detection Type
          </label>
          <select
            value={selectedDetection}
            onChange={(e) => setSelectedDetection(e.target.value)}
            className="px-3 py-2 border border-border rounded-md text-sm bg-background"
          >
            {data.metadata.detection_types.map(detType => (
              <option key={detType.long_name} value={detType.long_name}>
                {detType.long_name}
              </option>
            ))}
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
            {data.metadata.stations.map(station => (
              <option key={station} value={station}>
                Station {station}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Heatmap Container */}
      <div ref={containerRef} className="w-full" />
    </div>
  );
}
