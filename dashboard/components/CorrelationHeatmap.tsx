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

const CELL_SIZE = 12; // Larger cells to force scrolling
const ROW_LABEL_WIDTH = 100;
const COL_LABEL_HEIGHT = 80;
const DENDROGRAM_WIDTH = 120;
const CONTAINER_WIDTH = 1000;
const CONTAINER_HEIGHT = 600;
const MATRIX_AREA_WIDTH = CONTAINER_WIDTH - ROW_LABEL_WIDTH - DENDROGRAM_WIDTH; // 780px
const MATRIX_AREA_HEIGHT = CONTAINER_HEIGHT - COL_LABEL_HEIGHT; // 520px

const CorrelationHeatmap: React.FC = () => {
  const { data: heatmapData, loading, error } = useViewData<HeatmapData>('correlation_heatmap');
  const containerRef = useRef<HTMLDivElement>(null);

  console.log('Component render - loading:', loading, 'error:', error, 'data:', heatmapData);

  useEffect(() => {
    if (!heatmapData || !containerRef.current) return;

    console.log('Heatmap data:', {
      matrixEntries: heatmapData.matrix_data.length,
      indices: heatmapData.index_metadata.length,
      clusters: heatmapData.clusters.length,
      dimensions: heatmapData.dimensions
    });

    const container = d3.select(containerRef.current);
    container.selectAll('*').remove();

    // Create the main grid structure
    const gridContainer = container
      .append('div')
      .attr('class', 'heatmap-grid')
      .style('display', 'grid')
      .style('grid-template-columns', `${ROW_LABEL_WIDTH}px ${MATRIX_AREA_WIDTH}px ${DENDROGRAM_WIDTH}px`)
      .style('grid-template-rows', `${COL_LABEL_HEIGHT}px ${MATRIX_AREA_HEIGHT}px`)
      .style('width', `${CONTAINER_WIDTH}px`)
      .style('height', `${CONTAINER_HEIGHT}px`)
      .style('gap', '0px');

    // Corner 1 (top-left)
    gridContainer
      .append('div')
      .attr('class', 'corner-1')
      .style('background', '#f8f9fa')
      .style('border-right', '1px solid #ccc')
      .style('border-bottom', '1px solid #ccc')
      .style('grid-column', '1')
      .style('grid-row', '1');

    // Column labels container (sticky top, only over matrix area)
    const colLabelsContainer = gridContainer
      .append('div')
      .attr('class', 'column-labels')
      .style('overflow', 'hidden')
      .style('position', 'relative')
      .style('background', '#f8f9fa')
      .style('border-bottom', '1px solid #ccc')
      .style('border-right', '1px solid #ccc')
      .style('grid-column', '2')
      .style('grid-row', '1');

    // Corner 2 (top-right, above dendrogram)
    gridContainer
      .append('div')
      .attr('class', 'corner-2')
      .style('background', '#f8f9fa')
      .style('border-bottom', '1px solid #ccc')
      .style('grid-column', '3')
      .style('grid-row', '1');

    // Row labels container (sticky left)
    const rowLabelsContainer = gridContainer
      .append('div')
      .attr('class', 'row-labels')
      .style('overflow', 'hidden')
      .style('position', 'relative')
      .style('background', '#f8f9fa')
      .style('border-right', '1px solid #ccc')
      .style('grid-column', '1')
      .style('grid-row', '2');

    // Matrix container (scrollable)
    const matrixContainer = gridContainer
      .append('div')
      .attr('class', 'matrix-container')
      .style('overflow', 'auto')
      .style('position', 'relative')
      .style('grid-column', '2')
      .style('grid-row', '2');

    // Dendrogram container (always visible, aligned with matrix)
    const dendrogramContainer = gridContainer
      .append('div')
      .attr('class', 'dendrogram-container')
      .style('background', '#f8f9fa')
      .style('border-left', '1px solid #ccc')
      .style('grid-column', '3')
      .style('grid-row', '2')
      .style('overflow', 'hidden')
      .style('position', 'relative');

    // Create SVGs with proper sizing
    const colLabelsSvg = colLabelsContainer
      .append('svg')
      .style('width', `${heatmapData.dimensions.n_indices * CELL_SIZE}px`)
      .style('height', `${COL_LABEL_HEIGHT}px`)
      .style('display', 'block');

    const rowLabelsSvg = rowLabelsContainer
      .append('svg')
      .style('width', `${ROW_LABEL_WIDTH}px`)
      .style('height', `${heatmapData.dimensions.n_indices * CELL_SIZE}px`)
      .style('display', 'block');

    const matrixSvg = matrixContainer
      .append('svg')
      .style('width', `${heatmapData.dimensions.n_indices * CELL_SIZE}px`)
      .style('height', `${heatmapData.dimensions.n_indices * CELL_SIZE}px`)
      .style('display', 'block');

    const dendrogramSvg = dendrogramContainer
      .append('svg')
      .style('width', `${DENDROGRAM_WIDTH}px`)
      .style('height', `${heatmapData.dimensions.n_indices * CELL_SIZE}px`)
      .style('display', 'block');

    // Draw the correlation matrix
    drawMatrix(matrixSvg, heatmapData);

    // Draw labels
    drawRowLabels(rowLabelsSvg, heatmapData);
    drawColumnLabels(colLabelsSvg, heatmapData);

    // Draw dendrogram
    drawDendrogram(dendrogramSvg, heatmapData);

    // Set up synchronized scrolling
    setupSynchronizedScrolling(matrixContainer, rowLabelsContainer, colLabelsContainer, dendrogramContainer);

  }, [heatmapData]);

  const drawMatrix = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: HeatmapData) => {
    console.log('Drawing matrix with', data.matrix_data.length, 'entries');
    console.log('First few matrix entries:', data.matrix_data.slice(0, 5));

    const colorScale = d3.scaleSequential(d3.interpolateRdBu)
      .domain([1, -1]); // Reverse for red=positive, blue=negative

    // Remove any existing tooltip
    d3.select('.correlation-tooltip').remove();

    // Create tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'correlation-tooltip')
      .style('position', 'absolute')
      .style('padding', '8px')
      .style('background', 'rgba(0,0,0,0.8)')
      .style('color', 'white')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', '1000');

    const cells = svg.selectAll('.matrix-cell')
      .data(data.matrix_data)
      .enter().append('rect')
      .attr('class', 'matrix-cell')
      .attr('x', d => d.col_position * CELL_SIZE)
      .attr('y', d => d.row_position * CELL_SIZE)
      .attr('width', CELL_SIZE - 0.5)
      .attr('height', CELL_SIZE - 0.5)
      .attr('fill', d => colorScale(d.correlation))
      .attr('stroke', '#fff')
      .attr('stroke-width', 0.2)
      .on('mouseover', function(event, d) {
        tooltip.transition().duration(200).style('opacity', .9);
        tooltip.html(`
          <strong>${d.row_index} × ${d.col_index}</strong><br/>
          Correlation: ${d.correlation.toFixed(3)}<br/>
          Clusters: ${d.row_cluster} × ${d.col_cluster}
        `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0);
      });

    console.log('Created', cells.size(), 'matrix cells');
  };

  const drawRowLabels = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: HeatmapData) => {
    // Cluster background rectangles first
    data.clusters.forEach(cluster => {
      svg.append('rect')
        .attr('x', 0)
        .attr('y', cluster.start_position * CELL_SIZE)
        .attr('width', ROW_LABEL_WIDTH)
        .attr('height', cluster.size * CELL_SIZE)
        .attr('fill', cluster.color)
        .attr('opacity', 0.1)
        .attr('stroke', cluster.color)
        .attr('stroke-width', 1)
        .attr('stroke-opacity', 0.3);
    });

    // Then add labels
    const labels = svg.selectAll('.row-label')
      .data(data.index_metadata)
      .enter().append('g')
      .attr('class', 'row-label')
      .attr('transform', d => `translate(0, ${d.display_order * CELL_SIZE + CELL_SIZE/2})`);

    labels.append('text')
      .attr('x', ROW_LABEL_WIDTH - 5)
      .attr('y', 0)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'end')
      .style('font-size', '9px')
      .style('font-weight', d => d.is_selected ? 'bold' : 'normal')
      .style('fill', d => d.is_selected ? '#EF4444' : '#333')
      .text(d => d.index_name);
  };

  const drawColumnLabels = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: HeatmapData) => {
    // Cluster background rectangles first
    data.clusters.forEach(cluster => {
      svg.append('rect')
        .attr('x', cluster.start_position * CELL_SIZE)
        .attr('y', 0)
        .attr('width', cluster.size * CELL_SIZE)
        .attr('height', COL_LABEL_HEIGHT)
        .attr('fill', cluster.color)
        .attr('opacity', 0.1)
        .attr('stroke', cluster.color)
        .attr('stroke-width', 1)
        .attr('stroke-opacity', 0.3);
    });

    // Then add labels
    const labels = svg.selectAll('.col-label')
      .data(data.index_metadata)
      .enter().append('g')
      .attr('class', 'col-label')
      .attr('transform', d => `translate(${d.display_order * CELL_SIZE + CELL_SIZE/2}, ${COL_LABEL_HEIGHT - 15})`);

    labels.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .attr('transform', 'rotate(-90)')
      .attr('text-anchor', 'start')
      .style('font-size', '9px')
      .style('font-weight', d => d.is_selected ? 'bold' : 'normal')
      .style('fill', d => d.is_selected ? '#EF4444' : '#333')
      .text(d => d.index_name);
  };

  const drawDendrogram = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: HeatmapData) => {
    const { dendrogram } = data;
    const height = data.dimensions.n_indices * CELL_SIZE;

    // Scale for dendrogram coordinates (reversed x to face left toward matrix)
    const xScale = d3.scaleLinear()
      .domain([0, d3.max(dendrogram.dcoord.flat()) || 1])
      .range([20, DENDROGRAM_WIDTH - 20]); // Reversed: left side toward matrix

    const yScale = d3.scaleLinear()
      .domain([0, data.dimensions.n_indices * 10])
      .range([0, height]);

    // Draw dendrogram lines
    for (let i = 0; i < dendrogram.icoord.length; i++) {
      const icoord = dendrogram.icoord[i];
      const dcoord = dendrogram.dcoord[i];

      const pathData = d3.line<number>()
        .x((d, j) => xScale(dcoord[j]))
        .y((d, j) => yScale(icoord[j]))
        (icoord);

      svg.append('path')
        .attr('d', pathData!)
        .attr('fill', 'none')
        .attr('stroke', '#666')
        .attr('stroke-width', 1.5);
    }
  };

  const setupSynchronizedScrolling = (
    matrixContainer: d3.Selection<HTMLDivElement, unknown, null, undefined>,
    rowLabelsContainer: d3.Selection<HTMLDivElement, unknown, null, undefined>,
    colLabelsContainer: d3.Selection<HTMLDivElement, unknown, null, undefined>,
    dendrogramContainer: d3.Selection<HTMLDivElement, unknown, null, undefined>
  ) => {
    const matrixElement = matrixContainer.node();
    const rowLabelsElement = rowLabelsContainer.node();
    const colLabelsElement = colLabelsContainer.node();
    const dendrogramElement = dendrogramContainer.node();

    if (!matrixElement || !rowLabelsElement || !colLabelsElement || !dendrogramElement) return;

    let isScrolling = false;

    matrixElement.addEventListener('scroll', () => {
      if (isScrolling) return;
      isScrolling = true;

      // Sync row labels with vertical scroll
      rowLabelsElement.scrollTop = matrixElement.scrollTop;

      // Sync column labels with horizontal scroll
      colLabelsElement.scrollLeft = matrixElement.scrollLeft;

      // Sync dendrogram with vertical scroll (so it moves with the rows)
      const dendrogramSvg = dendrogramElement.querySelector('svg');
      if (dendrogramSvg) {
        dendrogramSvg.style.transform = `translateY(-${matrixElement.scrollTop}px)`;
      }

      requestAnimationFrame(() => {
        isScrolling = false;
      });
    });
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
    <div className="w-full">
      <div
        ref={containerRef}
        className="mx-auto border rounded-lg overflow-hidden"
        style={{
          width: CONTAINER_WIDTH,
          height: CONTAINER_HEIGHT,
          maxWidth: '100%'
        }}
      />
    </div>
  );
};

export default CorrelationHeatmap;