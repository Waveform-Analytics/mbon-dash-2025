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

interface ClusterMetadata {
  index_name: string;
  cluster_id: number;
  cluster_size: number;
  is_selected: boolean;
  selection_rationale: string;
}

interface AcousticIndicesHeatmapProps {
  className?: string;
}

const AcousticIndicesHeatmap: React.FC<AcousticIndicesHeatmapProps> = ({ className = '' }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStation, setSelectedStation] = useState<string>('9M');
  const [selectedIndex, setSelectedIndex] = useState<string>('ACTspFract');
  const [selectedCluster, setSelectedCluster] = useState<string>('All');
  const [stations, setStations] = useState<string[]>([]);
  const [indices, setIndices] = useState<string[]>([]);
  const [clusterMetadata, setClusterMetadata] = useState<ClusterMetadata[]>([]);
  const [clusters, setClusters] = useState<string[]>([]);
  const [isComponentMounted, setIsComponentMounted] = useState(false);

  // Fetch data from CDN
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const cdnUrl = process.env.NEXT_PUBLIC_CDN_BASE_URL || '';

        // Fetch both data and cluster metadata - use full dataset to get all indices
        const [dataResponse, metadataResponse] = await Promise.all([
          fetch(`${cdnUrl}/views/acoustic_indices_full.json`),
          fetch(`${cdnUrl}/views/acoustic_indices_clusters.json`)
        ]);

        if (!dataResponse.ok) {
          throw new Error(`Failed to fetch data: ${dataResponse.statusText}`);
        }

        const jsonData: DataPoint[] = await dataResponse.json();
        setData(jsonData);

        // Load cluster metadata if available
        let metadata: ClusterMetadata[] = [];
        if (metadataResponse.ok) {
          metadata = await metadataResponse.json();
          setClusterMetadata(metadata);

          // Extract unique clusters
          const uniqueClusters = Array.from(new Set(metadata.map(m => m.cluster_id)))
            .sort((a, b) => a - b)
            .map(id => `Cluster ${id}`);
          setClusters(['All', ...uniqueClusters]);
        }

        // Extract unique stations
        const uniqueStations = Array.from(new Set(jsonData.map(d => d.station))).sort();
        setStations(uniqueStations);

        // Extract acoustic index keys (excluding metadata fields)
        const excludeKeys = ['datetime', 'station', 'year', 'FrequencyResolution', 'hour'];
        const indexKeys = Object.keys(jsonData[0] || {})
          .filter(key => !excludeKeys.includes(key) && typeof jsonData[0][key] === 'number')
          .sort();
        setIndices(indexKeys);

        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Track component mount state to force re-render when navigating back
  useEffect(() => {
    setIsComponentMounted(true);
    return () => setIsComponentMounted(false);
  }, []);

  // Get available indices based on cluster selection
  const availableIndices = React.useMemo(() => {
    if (selectedCluster === 'All') {
      // When "All" is selected, show ALL indices from the data, not just cluster metadata
      return indices;
    }

    if (!clusterMetadata.length) {
      return indices; // Fall back to all indices if no cluster metadata
    }

    const clusterId = parseInt(selectedCluster.replace('Cluster ', ''));
    return clusterMetadata
      .filter(m => m.cluster_id === clusterId)
      .map(m => m.index_name)
      .filter(name => indices.includes(name))
      .sort();
  }, [clusterMetadata, selectedCluster, indices]);

  // Auto-select representative index when cluster changes
  React.useEffect(() => {
    if (availableIndices.length > 0 && !availableIndices.includes(selectedIndex)) {
      // Find representative index for the cluster, or fall back to first available
      const representative = clusterMetadata
        .filter(m => availableIndices.includes(m.index_name))
        .find(m => m.is_selected);

      setSelectedIndex(representative?.index_name || availableIndices[0]);
    }
  }, [availableIndices, selectedIndex, clusterMetadata]);

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

    // Skip rendering if container width is 0 (not yet rendered)
    if (containerWidth === 0) {
      // Use requestAnimationFrame to retry after the container is rendered
      const rafId = requestAnimationFrame(() => {
        if (containerRef.current) {
          const newWidth = containerRef.current.clientWidth;
          if (newWidth > 0) {
            // Trigger a re-render by updating a dummy state
            setError(null);
          }
        }
      });
      return () => cancelAnimationFrame(rafId);
    }

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
      const value = d[selectedIndex] as number;

      processedData.push({
        day: dayOfYear,
        hour: hour,
        value: value,
        date: date
      });
    });

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

        tooltip.html(`
          Date: ${d.date.toLocaleDateString()}<br/>
          Hour: ${d.hour}:00<br/>
          ${selectedIndex}: ${d.value.toFixed(4)}
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
      .tickFormat(d3.format('.3f'));

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

    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -5)
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .text(selectedIndex);

  }, [data, selectedStation, selectedIndex, isComponentMounted]);

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-muted-foreground">Loading acoustic indices data...</div>
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
      <div className="flex gap-4 mb-4 flex-wrap">
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

        {clusters.length > 0 && (
          <div>
            <label className="block text-sm font-medium mb-1">Cluster Group</label>
            <select
              className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background"
              value={selectedCluster}
              onChange={(e) => setSelectedCluster(e.target.value)}
            >
              {clusters.map(cluster => (
                <option key={cluster} value={cluster}>{cluster}</option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-1">Acoustic Index</label>
          <select
            className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background"
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value)}
          >
            {availableIndices.map(index => {
              const metadata = clusterMetadata.find(m => m.index_name === index);
              const isRepresentative = metadata?.is_selected || false;
              return (
                <option key={index} value={index}>
                  {index} {isRepresentative ? '★' : ''}
                </option>
              );
            })}
          </select>
        </div>
      </div>
      <div ref={containerRef} className="w-full">
        <svg ref={svgRef}></svg>
      </div>
    </div>
  );
};

export default AcousticIndicesHeatmap;