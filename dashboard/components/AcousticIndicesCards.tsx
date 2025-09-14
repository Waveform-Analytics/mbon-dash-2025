'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useViewData } from '@/lib/data';

interface HistogramBin {
  bin_center: number;
  bin_start: number;
  bin_end: number;
  count: number;
  frequency: number;
}

interface AcousticIndex {
  index_name: string;
  station: string;
  category: string;
  subcategory: string;
  description: string;
  total_samples: number;
  min_value: number;
  max_value: number;
  mean_value: number;
  std_value: number;
  histogram: HistogramBin[];
}

// Define category colors
const categoryColors: Record<string, { bg: string; border: string; text: string; pill: string }> = {
  'Complexity Indices': {
    bg: 'from-purple-50 to-purple-100',
    border: 'border-purple-200',
    text: 'text-purple-900',
    pill: 'bg-purple-100 text-purple-800 border-purple-300'
  },
  'Diversity Indices': {
    bg: 'from-green-50 to-green-100',
    border: 'border-green-200',
    text: 'text-green-900',
    pill: 'bg-green-100 text-green-800 border-green-300'
  },
  'Temporal Indices': {
    bg: 'from-blue-50 to-blue-100',
    border: 'border-blue-200',
    text: 'text-blue-900',
    pill: 'bg-blue-100 text-blue-800 border-blue-300'
  },
  'Spectral Indices': {
    bg: 'from-amber-50 to-amber-100',
    border: 'border-amber-200',
    text: 'text-amber-900',
    pill: 'bg-amber-100 text-amber-800 border-amber-300'
  },
  'Amplitude Indices': {
    bg: 'from-red-50 to-red-100',
    border: 'border-red-200',
    text: 'text-red-900',
    pill: 'bg-red-100 text-red-800 border-red-300'
  },
  'Unknown': {
    bg: 'from-gray-50 to-gray-100',
    border: 'border-gray-200',
    text: 'text-gray-900',
    pill: 'bg-gray-100 text-gray-800 border-gray-300'
  }
};

const AcousticIndicesCards: React.FC = () => {
  const { data: rawData, loading, error } = useViewData<AcousticIndex[]>('acoustic_indices_histograms');
  const [selectedStation, setSelectedStation] = useState<string>('9M');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());
  const [stations, setStations] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    if (rawData && rawData.length > 0) {
      // Extract unique stations
      const uniqueStations = Array.from(new Set(rawData.map(d => d.station)));
      setStations(uniqueStations);

      // Extract unique categories
      const uniqueCategories = Array.from(new Set(rawData.map(d => d.category)));
      setCategories(['All', ...uniqueCategories.sort()]);
    }
  }, [rawData]);

  const handleCardClick = (indexName: string) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(indexName)) {
        newSet.delete(indexName);
      } else {
        newSet.add(indexName);
      }
      return newSet;
    });
  };

  // Filter data based on selected station and category
  const filteredData = rawData ? rawData.filter(d => {
    const stationMatch = d.station === selectedStation;
    const categoryMatch = selectedCategory === 'All' || d.category === selectedCategory;
    return stationMatch && categoryMatch;
  }) : [];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading acoustic indices data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-red-500">Error loading data: {error}</div>
      </div>
    );
  }

  if (!rawData || rawData.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">No data available</div>
      </div>
    );
  }

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <label htmlFor="station-select" className="text-sm font-medium text-gray-700">
            Station:
          </label>
          <select
            id="station-select"
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            {stations.map(station => (
              <option key={station} value={station}>
                {station}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label htmlFor="category-select" className="text-sm font-medium text-gray-700">
            Category:
          </label>
          <select
            id="category-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        <span className="text-sm text-gray-500 ml-auto">
          Showing {filteredData.length} indices
        </span>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {filteredData.map((index) => (
          <IndexCard
            key={`${index.index_name}-${index.station}`}
            index={index}
            isFlipped={flippedCards.has(index.index_name)}
            onClick={() => handleCardClick(index.index_name)}
            categoryColors={categoryColors[index.category] || categoryColors['Unknown']}
          />
        ))}
      </div>
    </div>
  );
};

interface IndexCardProps {
  index: AcousticIndex;
  isFlipped: boolean;
  onClick: () => void;
  categoryColors: { bg: string; border: string; text: string; pill: string };
}

const IndexCard: React.FC<IndexCardProps> = ({ index, isFlipped, onClick, categoryColors }) => {
  const histogramRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!isFlipped && histogramRef.current) {
      drawHistogram();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isFlipped, index]);

  const drawHistogram = () => {
    const svg = d3.select(histogramRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 25, right: 15, bottom: 30, left: 40 };
    const width = 240 - margin.left - margin.right;
    const height = 160 - margin.top - margin.bottom;

    const g = svg
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // X scale
    const xScale = d3.scaleLinear()
      .domain([index.min_value, index.max_value])
      .range([0, width]);

    // Y scale
    const yScale = d3.scaleLinear()
      .domain([0, d3.max(index.histogram, d => d.frequency) || 1])
      .range([height, 0]);

    // Draw bars
    g.selectAll('.bar')
      .data(index.histogram)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.bin_start))
      .attr('y', d => yScale(d.frequency))
      .attr('width', (width / index.histogram.length) * 0.9)
      .attr('height', d => height - yScale(d.frequency))
      .attr('fill', '#3B82F6')
      .attr('opacity', 0.8);

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(5).tickFormat(d3.format('.2s')))
      .selectAll('text')
      .style('font-size', '10px');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(yScale).ticks(4).tickFormat(d3.format('.0%')))
      .selectAll('text')
      .style('font-size', '10px');

    // Title
    g.append('text')
      .attr('x', width / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .style('font-weight', 'bold')
      .text(index.index_name);

    // Add mean line
    const meanX = xScale(index.mean_value);
    g.append('line')
      .attr('x1', meanX)
      .attr('x2', meanX)
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#EF4444')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '3,3')
      .attr('opacity', 0.7);
  };

  return (
    <div
      className="relative h-64 cursor-pointer preserve-3d transition-transform duration-500"
      style={{
        transformStyle: 'preserve-3d',
        transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
      }}
      onClick={onClick}
    >
      {/* Front of card - Histogram */}
      <div
        className="absolute w-full h-full backface-hidden bg-white rounded-lg shadow-md border border-gray-200 p-3"
        style={{ backfaceVisibility: 'hidden' }}
      >
        <svg ref={histogramRef} className="mx-auto"></svg>

        {/* Category pill at bottom center */}
        <div className="absolute bottom-3 left-0 right-0 flex justify-center">
          <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full border ${categoryColors.pill}`}>
            {index.category}
          </span>
        </div>
      </div>

      {/* Back of card - Description */}
      <div
        className={`absolute w-full h-full backface-hidden bg-gradient-to-br ${categoryColors.bg} rounded-lg shadow-md border ${categoryColors.border} p-4`}
        style={{
          backfaceVisibility: 'hidden',
          transform: 'rotateY(180deg)'
        }}
      >
        <div className="h-full flex flex-col">
          <h3 className={`text-lg font-bold ${categoryColors.text} mb-2`}>{index.index_name}</h3>
          <div className="mb-2">
            <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full border ${categoryColors.pill}`}>
              {index.category}
            </span>
            <span className="text-xs text-gray-600 ml-2">• {index.subcategory}</span>
          </div>
          <p className="text-sm text-gray-700 flex-grow overflow-y-auto">{index.description}</p>
          <div className={`mt-2 pt-2 border-t ${categoryColors.border}`}>
            <div className="grid grid-cols-2 gap-1 text-xs">
              <div>
                <span className="text-gray-600">Mean:</span>
                <span className="ml-1 font-mono">{index.mean_value.toFixed(3)}</span>
              </div>
              <div>
                <span className="text-gray-600">Std:</span>
                <span className="ml-1 font-mono">{index.std_value.toFixed(3)}</span>
              </div>
              <div>
                <span className="text-gray-600">Min:</span>
                <span className="ml-1 font-mono">{index.min_value.toFixed(3)}</span>
              </div>
              <div>
                <span className="text-gray-600">Max:</span>
                <span className="ml-1 font-mono">{index.max_value.toFixed(3)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AcousticIndicesCards;