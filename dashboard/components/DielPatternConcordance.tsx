'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useViewData } from '@/lib/data';

interface DielPattern {
  season: string;
  hour: number;
  variable: string;
  variable_type: 'acoustic_index' | 'manual_detection';
  mean: number;
  std: number;
  count: number;
}

interface DielData {
  patterns: DielPattern[];
  metadata: {
    seasons: string[];
    hours: number[];
    variables: {
      acoustic_indices: string[];
      manual_detections: string[];
    };
    total_records: number;
  };
}

const DielPatternConcordance: React.FC = () => {
  const { data, loading, error } = useViewData<DielData>('seasonal_diel_patterns');
  const [selectedSeason, setSelectedSeason] = useState<string>('Spring');
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!data || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Filter data for selected season
    const seasonData = data.patterns.filter(d => d.season === selectedSeason);

    // Get unique variables in order (indices first, then fish)
    const indices = data.metadata.variables.acoustic_indices;
    const fish = data.metadata.variables.manual_detections;
    const allVariables = [...indices, ...fish];

    // Set up dimensions
    const margin = { top: 40, right: 40, bottom: 50, left: 60 };
    const panelWidth = 280;
    const panelHeight = 200;
    const panelSpacing = 20;
    const cols = 4;
    const rows = 2;

    const totalWidth = cols * panelWidth + (cols - 1) * panelSpacing + margin.left + margin.right;
    const totalHeight = rows * panelHeight + (rows - 1) * panelSpacing + margin.top + margin.bottom;

    svg
      .attr('width', totalWidth)
      .attr('height', totalHeight);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Create panels for each variable
    allVariables.forEach((variable, i) => {
      const col = i % cols;
      const row = Math.floor(i / cols);
      const x = col * (panelWidth + panelSpacing);
      const y = row * (panelHeight + panelSpacing);

      const panelG = g.append('g')
        .attr('transform', `translate(${x}, ${y})`);

      // Get data for this variable
      const varData = seasonData
        .filter(d => d.variable === variable)
        .sort((a, b) => a.hour - b.hour);

      if (varData.length === 0) return;

      // Determine if this is an index or fish
      const isIndex = indices.includes(variable);

      // Create scales
      const xScale = d3.scaleLinear()
        .domain([0, 23])
        .range([0, panelWidth]);

      const yScale = d3.scaleLinear()
        .domain([0, d3.max(varData, d => d.mean + d.std) || 1])
        .range([panelHeight, 0]);

      // Add day/night shading
      panelG.append('rect')
        .attr('x', xScale(0))
        .attr('y', 0)
        .attr('width', xScale(6) - xScale(0))
        .attr('height', panelHeight)
        .attr('fill', '#4C5270')
        .attr('opacity', 0.1);

      panelG.append('rect')
        .attr('x', xScale(6))
        .attr('y', 0)
        .attr('width', xScale(18) - xScale(6))
        .attr('height', panelHeight)
        .attr('fill', '#FDB462')
        .attr('opacity', 0.1);

      panelG.append('rect')
        .attr('x', xScale(18))
        .attr('y', 0)
        .attr('width', xScale(24) - xScale(18))
        .attr('height', panelHeight)
        .attr('fill', '#4C5270')
        .attr('opacity', 0.1);

      // Add confidence band (std deviation)
      const areaGenerator = d3.area<DielPattern>()
        .x(d => xScale(d.hour))
        .y0(d => yScale(Math.max(0, d.mean - d.std)))
        .y1(d => yScale(d.mean + d.std))
        .curve(d3.curveMonotoneX);

      panelG.append('path')
        .datum(varData)
        .attr('d', areaGenerator)
        .attr('fill', isIndex ? '#3B82F6' : '#DC2626')
        .attr('opacity', 0.2);

      // Add line
      const lineGenerator = d3.line<DielPattern>()
        .x(d => xScale(d.hour))
        .y(d => yScale(d.mean))
        .curve(d3.curveMonotoneX);

      panelG.append('path')
        .datum(varData)
        .attr('d', lineGenerator)
        .attr('fill', 'none')
        .attr('stroke', isIndex ? '#3B82F6' : '#DC2626')
        .attr('stroke-width', 2);

      // Add axes
      const xAxis = d3.axisBottom(xScale)
        .tickValues([0, 6, 12, 18, 23])
        .tickFormat(d => d === 23 ? '23' : d.toString());

      panelG.append('g')
        .attr('transform', `translate(0, ${panelHeight})`)
        .call(xAxis)
        .append('text')
        .attr('x', panelWidth / 2)
        .attr('y', 35)
        .attr('fill', 'black')
        .style('text-anchor', 'middle')
        .style('font-size', '11px')
        .text('Hour of Day');

      const yAxis = d3.axisLeft(yScale)
        .ticks(4)
        .tickFormat(d3.format('.2f'));

      panelG.append('g')
        .call(yAxis);

      // Add title
      panelG.append('text')
        .attr('x', panelWidth / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('font-weight', 'bold')
        .style('fill', isIndex ? '#3B82F6' : '#DC2626')
        .text(variable);

      // Add subtitle
      panelG.append('text')
        .attr('x', panelWidth / 2)
        .attr('y', 5)
        .attr('text-anchor', 'middle')
        .style('font-size', '10px')
        .style('fill', '#666')
        .text(isIndex ? '(Acoustic Index)' : '(Manual Detection)');

      // Add Y axis label
      panelG.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -panelHeight / 2)
        .attr('text-anchor', 'middle')
        .style('font-size', '10px')
        .text('Index Value');
    });

    // Add overall title
    g.append('text')
      .attr('x', (totalWidth - margin.left - margin.right) / 2)
      .attr('y', -20)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text(`Diel Pattern Concordance: Acoustic Indices vs Manual Fish Detections - ${selectedSeason}`);

  }, [data, selectedSeason]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-gray-500">Loading diel patterns...</div>
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

  if (!data) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-gray-500">No data available</div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-4 flex items-center gap-4">
        <label htmlFor="season-select" className="font-semibold">Select Season:</label>
        <select
          id="season-select"
          value={selectedSeason}
          onChange={(e) => setSelectedSeason(e.target.value)}
          className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {data.metadata.seasons.map(season => (
            <option key={season} value={season}>{season}</option>
          ))}
        </select>
      </div>
      <div className="overflow-auto">
        <svg ref={svgRef} />
      </div>
      <div className="mt-4 text-sm text-gray-600">
        <p><strong>Note:</strong> Shaded regions indicate night (blue), day (yellow), and night (blue) periods.
        Blue lines represent acoustic indices, red lines represent manual fish detections.
        Shaded bands show ±1 standard deviation.</p>
      </div>
    </div>
  );
};

export default DielPatternConcordance;