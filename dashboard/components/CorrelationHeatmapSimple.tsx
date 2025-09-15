'use client';

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { useViewData } from '@/lib/data';

interface MatrixData {
  row_index: string;
  col_index: string;
  correlation: number;
  row_cluster: number | null;
  col_cluster: number | null;
  row_position: number;
  col_position: number;
}

interface IndexMetadata {
  index_name: string;
  cluster_id: number | null;
  is_selected: boolean;
  display_order: number;
  cluster_color: string;
}

interface ClusterData {
  cluster_id: number;
  start_position: number;
  end_position: number;
  color: string;
  size: number;
}

interface DendrogramData {
  icoord: number[][];
  dcoord: number[][];
  ivl: string[];
  leaves: number[];
}

interface HeatmapData {
  matrix_data: MatrixData[];
  index_metadata: IndexMetadata[];
  dendrogram: DendrogramData;
  clusters: ClusterData[];
  dimensions: {
    n_indices: number;
    n_clusters: number;
  };
}

const CorrelationHeatmapSimple: React.FC = () => {
  const { data: heatmapData, loading, error } = useViewData<HeatmapData>('correlation_heatmap');
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!heatmapData || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 200, right: 100, bottom: 150, left: 200 };
    const cellSize = 8;
    const n = heatmapData.dimensions.n_indices;
    const matrixSize = n * cellSize;

    const width = margin.left + matrixSize + margin.right;
    const height = margin.top + matrixSize + margin.bottom;

    svg
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Color scale for correlations
    const colorScale = d3.scaleSequential(d3.interpolateRdBu)
      .domain([1, -1]);

    // Cluster color mapping
    const clusterColorMap = new Map();
    heatmapData.clusters.forEach(cluster => {
      clusterColorMap.set(cluster.cluster_id, cluster.color);
    });

    // Draw correlation matrix
    g.selectAll('.matrix-cell')
      .data(heatmapData.matrix_data)
      .enter().append('rect')
      .attr('class', 'matrix-cell')
      .attr('x', d => d.col_position * cellSize)
      .attr('y', d => d.row_position * cellSize)
      .attr('width', cellSize - 0.5)
      .attr('height', cellSize - 0.5)
      .attr('fill', d => colorScale(d.correlation))
      .attr('stroke', '#fff')
      .attr('stroke-width', 0.2);

    // Draw row labels (close to matrix)
    g.selectAll('.row-label')
      .data(heatmapData.index_metadata)
      .enter().append('text')
      .attr('class', 'row-label')
      .attr('x', -5)
      .attr('y', d => d.display_order * cellSize + cellSize/2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .style('font-size', '9px')
      .style('font-weight', d => d.is_selected ? 'bold' : 'normal')
      .style('fill', d => d.is_selected ? '#EF4444' : '#333')
      .text(d => d.index_name);

    // Draw column labels (rotated, close to matrix)
    g.selectAll('.col-label')
      .data(heatmapData.index_metadata)
      .enter().append('text')
      .attr('class', 'col-label')
      .attr('x', d => d.display_order * cellSize + cellSize/2)
      .attr('y', -5)
      .attr('text-anchor', 'start')
      .attr('transform', d => `rotate(-90, ${d.display_order * cellSize + cellSize/2}, -5)`)
      .style('font-size', '9px')
      .style('font-weight', d => d.is_selected ? 'bold' : 'normal')
      .style('fill', d => d.is_selected ? '#EF4444' : '#333')
      .text(d => d.index_name);

    // Draw dendrogram on the left (vertical, shifted left and positioned better)
    drawDendrogram(g, heatmapData, 'left', -150, 0, 80, matrixSize, clusterColorMap);

    // Draw dendrogram on the top (horizontal, nudged up)
    drawDendrogram(g, heatmapData, 'top', 0, -150, matrixSize, 80, clusterColorMap);

    // Add correlation color legend below the heatmap
    addColorLegend(svg, colorScale, margin.left + matrixSize/2 - 100, margin.top + matrixSize + 50, 200, 20);

  }, [heatmapData]);

  const drawDendrogram = (
    g: d3.Selection<SVGGElement, unknown, null, undefined>,
    data: HeatmapData,
    orientation: 'left' | 'top',
    x: number,
    y: number,
    width: number,
    height: number,
    clusterColorMap: Map<number, string>
  ) => {
    const { dendrogram } = data;

    // Create scales based on orientation
    const xScale = orientation === 'left'
      ? d3.scaleLinear().domain([0, d3.max(dendrogram.dcoord.flat()) || 1]).range([width, 0]) // Reversed for left dendrogram
      : d3.scaleLinear().domain([0, data.dimensions.n_indices * 10]).range([0, width]);

    const yScale = orientation === 'left'
      ? d3.scaleLinear().domain([0, data.dimensions.n_indices * 10]).range([0, height])
      : d3.scaleLinear().domain([0, d3.max(dendrogram.dcoord.flat()) || 1]).range([height, 0]);

    const dendrogramG = g.append('g')
      .attr('transform', `translate(${x}, ${y})`);

    // Draw dendrogram branches with cluster colors
    for (let i = 0; i < dendrogram.icoord.length; i++) {
      const icoord = dendrogram.icoord[i];
      const dcoord = dendrogram.dcoord[i];

      // Determine cluster color based on the branch position
      const midPoint = (icoord[0] + icoord[3]) / 2;
      const clusterIndex = Math.floor(midPoint / 10);
      const metadata = data.index_metadata[clusterIndex];
      const branchColor = metadata && metadata.cluster_id !== null ? clusterColorMap.get(metadata.cluster_id) || '#666' : '#666';

      const pathData = orientation === 'left'
        ? d3.line<number>()
            .x((d, j) => xScale(dcoord[j]))
            .y((d, j) => yScale(icoord[j]))
            (icoord)
        : d3.line<number>()
            .x((d, j) => xScale(icoord[j]))
            .y((d, j) => yScale(dcoord[j]))
            (icoord);

      dendrogramG.append('path')
        .attr('d', pathData!)
        .attr('fill', 'none')
        .attr('stroke', branchColor)
        .attr('stroke-width', 2)
        .attr('opacity', 0.8);
    }
  };

  const addColorLegend = (
    svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
    colorScale: d3.ScaleSequential<string, never>,
    x: number,
    y: number,
    width: number,
    height: number
  ) => {
    const legendG = svg.append('g')
      .attr('transform', `translate(${x}, ${y})`);

    // Create horizontal gradient
    const defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
    const gradient = defs.append('linearGradient')
      .attr('id', 'correlation-gradient-horizontal')
      .attr('x1', '0%').attr('y1', '0%')
      .attr('x2', '100%').attr('y2', '0%');

    const steps = 10;
    for (let i = 0; i <= steps; i++) {
      const value = -1 + (2 * i / steps); // From -1 to 1 (left to right)
      gradient.append('stop')
        .attr('offset', `${(i / steps) * 100}%`)
        .attr('stop-color', colorScale(value));
    }

    // Legend rectangle (horizontal)
    legendG.append('rect')
      .attr('width', width)
      .attr('height', height)
      .style('fill', 'url(#correlation-gradient-horizontal)')
      .attr('stroke', '#333')
      .attr('stroke-width', 1);

    // Legend labels (horizontal)
    const legendScale = d3.scaleLinear()
      .domain([-1, 1])
      .range([0, width]);

    const legendAxis = d3.axisBottom(legendScale)
      .tickValues([-1, -0.5, 0, 0.5, 1])
      .tickFormat(d3.format('.1f'));

    legendG.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(legendAxis);

    legendG.append('text')
      .attr('x', width/2)
      .attr('y', height + 35)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .text('Correlation');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-gray-500">Loading correlation heatmap...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-red-500">Error loading data: {error instanceof Error ? error.message : String(error)}</div>
      </div>
    );
  }

  if (!heatmapData) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-gray-500">No data available</div>
      </div>
    );
  }

  return (
    <div className="w-full flex justify-center">
      <div className="overflow-auto max-w-full">
        <svg ref={svgRef} />
      </div>
    </div>
  );
};

export default CorrelationHeatmapSimple;