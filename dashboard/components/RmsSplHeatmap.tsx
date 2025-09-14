'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface DataPoint {
  datetime: number;
  station: string;
  year: number;
  [key: string]: string | number;
}

interface ProcessedDataPoint {
  day: number;
  hour: number;
  value: number;
  date: Date;
}

interface RmsSplHeatmapProps {
  className?: string;
}

const RmsSplHeatmap: React.FC<RmsSplHeatmapProps> = ({ className = '' }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStation, setSelectedStation] = useState<string>('9M');
  const [selectedBandwidth, setSelectedBandwidth] = useState<string>('Broadband (1-40000 Hz)');
  const [stations, setStations] = useState<string[]>([]);
  const [bandwidths, setBandwidths] = useState<{ key: string; label: string }[]>([]);

  // Fetch data from CDN
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const cdnUrl = process.env.NEXT_PUBLIC_CDN_BASE_URL || '';
        const response = await fetch(`${cdnUrl}/views/02_environmental_aligned_2021.json`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.statusText}`);
        }
        
        const jsonData: DataPoint[] = await response.json();
        setData(jsonData);
        
        // Extract unique stations
        const uniqueStations = Array.from(new Set(jsonData.map(d => d.station))).sort();
        setStations(uniqueStations);
        
        // Define bandwidth options based on SPL columns
        const bandwidthOptions = [
          { key: 'Broadband (1-40000 Hz)', label: 'Broadband' },
          { key: 'Low (50-1200 Hz)', label: 'Low Frequency' },
          { key: 'High (7000-40000 Hz)', label: 'High Frequency' }
        ];
        setBandwidths(bandwidthOptions);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Render heatmap
  useEffect(() => {
    if (!data.length || !svgRef.current || !containerRef.current) return;

    // Filter data for selected station
    const stationData = data.filter(d => d.station === selectedStation);
    if (!stationData.length) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove();

    // Set dimensions and margins
    const margin = { top: 80, right: 50, bottom: 140, left: 70 };
    const containerWidth = containerRef.current.clientWidth;
    const width = containerWidth - margin.left - margin.right;
    const height = 450 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', containerWidth)
      .attr('height', 450);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Process data for heatmap
    const processedData: ProcessedDataPoint[] = [];
    stationData.forEach(d => {
      const date = new Date(d.datetime);
      // Use UTC time to avoid timezone issues since data is in UTC
      const dayOfYear = Math.floor((date.getTime() - new Date(Date.UTC(date.getUTCFullYear(), 0, 0)).getTime()) / 86400000);
      const hour = date.getUTCHours();  // Use UTC hours
      const value = d[selectedBandwidth] as number;
      
      // Only add data points where we have valid SPL values
      if (value !== null && value !== undefined && !isNaN(value)) {
        processedData.push({
          day: dayOfYear,
          hour: hour,
          value: value,
          date: date
        });
      }
    });

    if (!processedData.length) {
      // Show message if no data available
      g.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('fill', '#666')
        .text(`No ${selectedBandwidth} data available for station ${selectedStation}`);
      return;
    }

    // Create scales
    const dayExtent = d3.extent(processedData, d => d.day) as [number, number];
    const xScale = d3.scaleLinear()
      .domain(dayExtent)
      .range([0, width]);

    // Create y-scale for 2-hour intervals (0, 2, 4, 6, ..., 22)
    const yScale = d3.scaleLinear()
      .domain([0, 22])
      .range([height, 0]);

    const colorScale = d3.scaleSequential(d3.interpolateViridis)
      .domain(d3.extent(processedData, d => d.value) as [number, number]);

    // Calculate cell dimensions
    const cellWidth = width / (dayExtent[1] - dayExtent[0] + 1);
    const cellHeight = height / 12;  // 12 rows for 2-hour intervals (0, 2, 4, ..., 22)

    // Add cells
    g.selectAll('rect')
      .data(processedData)
      .enter()
      .append('rect')
      .attr('x', d => xScale(d.day))
      .attr('y', d => yScale(d.hour) - cellHeight)
      .attr('width', cellWidth)
      .attr('height', cellHeight)
      .attr('fill', d => colorScale(d.value))
      .attr('stroke', 'none')
      .on('mouseover', function(event, d) {
        // Add tooltip
        const tooltip = d3.select('body').append('div')
          .attr('class', 'heatmap-tooltip')
          .style('position', 'absolute')
          .style('padding', '10px')
          .style('background', 'rgba(0, 0, 0, 0.8)')
          .style('color', 'white')
          .style('border-radius', '5px')
          .style('pointer-events', 'none')
          .style('opacity', 0);

        tooltip.transition()
          .duration(200)
          .style('opacity', 0.9);

        const bandwidthLabel = bandwidths.find(b => b.key === selectedBandwidth)?.label || selectedBandwidth;
        tooltip.html(`
          Date: ${d.date.toLocaleDateString()}<br/>
          Hour: ${d.hour}:00<br/>
          ${bandwidthLabel} SPL: ${d.value.toFixed(1)} dB
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.selectAll('.heatmap-tooltip').remove();
      });

    // Add X axis
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d => {
        // Convert day of year back to date for the current year using UTC
        const year = stationData[0].year;
        const date = new Date(Date.UTC(year, 0, Number(d)));
        return d3.timeFormat('%b %d')(date);
      })
      .ticks(10);

    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis)
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.8em')
      .attr('transform', 'rotate(-45)');

    // Add Y axis - show only 2-hour intervals, centered on cell rows
    const yAxis = d3.axisLeft(yScale)
      .tickValues([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23])
      .tickFormat((_, i) => `${[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22][i]}:00`)
      .tickSize(0);

    g.append('g')
      .call(yAxis);

    // Add X axis label
    svg.append('text')
      .attr('transform', `translate(${containerWidth / 2},${margin.top + height + 60})`)
      .style('text-anchor', 'middle')
      .text('Date');

    // Add Y axis label
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 15)
      .attr('x', -(margin.top + height / 2))
      .style('text-anchor', 'middle')
      .text('Hour of Day');

    // Add color legend
    const legendWidth = 200;
    const legendHeight = 20;
    
    const legendScale = d3.scaleLinear()
      .domain(colorScale.domain())
      .range([0, legendWidth]);

    const legendAxis = d3.axisBottom(legendScale)
      .ticks(5)
      .tickFormat(d => d3.format('.1f')(d));

    const legend = svg.append('g')
      .attr('transform', `translate(${containerWidth - legendWidth - 30},${15})`);

    // Create gradient for legend
    const gradientId = 'gradient-' + Math.random();
    const gradient = svg.append('defs')
      .append('linearGradient')
      .attr('id', gradientId)
      .attr('x1', '0%')
      .attr('x2', '100%')
      .attr('y1', '0%')
      .attr('y2', '0%');

    const nStops = 10;
    const colorRange = d3.range(nStops).map(i => i / (nStops - 1));
    
    colorRange.forEach(t => {
      gradient.append('stop')
        .attr('offset', `${t * 100}%`)
        .attr('stop-color', colorScale(colorScale.domain()[0] + t * (colorScale.domain()[1] - colorScale.domain()[0])));
    });

    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', `url(#${gradientId})`);

    legend.append('g')
      .attr('transform', `translate(0,${legendHeight})`)
      .call(legendAxis);

    const bandwidthLabel = bandwidths.find(b => b.key === selectedBandwidth)?.label || selectedBandwidth;
    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -5)
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text(`${bandwidthLabel} SPL (dB)`);

  }, [data, selectedStation, selectedBandwidth, bandwidths]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-muted-foreground">Loading RMS SPL data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="flex gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium mb-1">Station</label>
          <select 
            className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background"
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
          >
            {stations.map(station => (
              <option key={station} value={station}>{station}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Bandwidth</label>
          <select 
            className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background"
            value={selectedBandwidth}
            onChange={(e) => setSelectedBandwidth(e.target.value)}
          >
            {bandwidths.map(bandwidth => (
              <option key={bandwidth.key} value={bandwidth.key}>{bandwidth.label}</option>
            ))}
          </select>
        </div>
      </div>
      <div ref={containerRef} className="w-full">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
};

export default RmsSplHeatmap;