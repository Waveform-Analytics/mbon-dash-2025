'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as Plot from '@observablehq/plot';
import { usePCABiplot, type PCAPoint } from '@/lib/hooks/useData';

interface PCABiplotProps {
  /** Width of the chart container */
  width?: number;
  /** Height of the chart container */
  height?: number;
  /** Which principal components to display (default: [1, 2]) */
  components?: [number, number];
  /** Whether to show loading vectors */
  showLoadings?: boolean;
  /** Maximum number of loading vectors to display */
  maxLoadings?: number;
  /** Color scheme for stations */
  colorScheme?: string[];
}

interface ComponentStats {
  pc1Variance: number;
  pc2Variance: number;
  totalVariance: number;
  nPoints: number;
  nLoadings: number;
}

export default function PCABiplot({
  width = 800,
  height = 600,
  components = [1, 2],
  showLoadings = true,
  maxLoadings = 15,
  colorScheme = ['#1f77b4', '#ff7f0e', '#2ca02c']
}: PCABiplotProps) {
  const plotRef = useRef<HTMLDivElement>(null);
  const [bandwidth, setBandwidth] = useState<'FullBW' | '8kHz'>('FullBW');
  const { data, loading, error } = usePCABiplot(bandwidth);
  // For future interactivity
  // const [selectedPoint, setSelectedPoint] = useState<PCAPoint | null>(null);
  const [stats, setStats] = useState<ComponentStats | null>(null);

  // Calculate component indices (1-based to 0-based)
  const pc1Index = components[0] - 1;
  const pc2Index = components[1] - 1;
  const pc1Key = `pc${components[0]}` as keyof PCAPoint;
  const pc2Key = `pc${components[1]}` as keyof PCAPoint;

  useEffect(() => {
    if (!data || !plotRef.current) return;

    const { points, loadings, variance_explained } = data.pca_biplot;

    // Calculate stats only if they've changed
    const newStats: ComponentStats = {
      pc1Variance: variance_explained[pc1Index] || 0,
      pc2Variance: variance_explained[pc2Index] || 0,
      totalVariance: data.pca_biplot.metadata.total_variance,
      nPoints: points.length,
      nLoadings: loadings.length
    };
    
    // Only update stats if they've actually changed
    setStats(prevStats => {
      if (!prevStats || 
          prevStats.pc1Variance !== newStats.pc1Variance ||
          prevStats.pc2Variance !== newStats.pc2Variance ||
          prevStats.totalVariance !== newStats.totalVariance ||
          prevStats.nPoints !== newStats.nPoints ||
          prevStats.nLoadings !== newStats.nLoadings) {
        return newStats;
      }
      return prevStats;
    });

    // Prepare data for plotting
    const plotPoints = points.map(point => ({
      ...point,
      pc1: point[pc1Key] as number,
      pc2: point[pc2Key] as number,
      species_count_capped: Math.min(point.species_count, 10), // Cap for better visualization
      datetime_parsed: new Date(point.datetime)
    }));

    // Filter and prepare loadings (show most influential)
    const plotLoadings = loadings
      .map(loading => ({
        ...loading,
        pc1: (loading as any)[pc1Key] as number,
        pc2: (loading as any)[pc2Key] as number,
        magnitude: Math.sqrt(
          Math.pow((loading as any)[pc1Key] as number, 2) + 
          Math.pow((loading as any)[pc2Key] as number, 2)
        )
      }))
      .sort((a, b) => b.magnitude - a.magnitude)
      .slice(0, maxLoadings);

    // Create the plot
    const marks = [];

    // Main scatter plot points
    marks.push(
      Plot.dot(plotPoints, {
        x: 'pc1',
        y: 'pc2',
        fill: 'station',
        r: d => Math.max(3, Math.sqrt(d.species_count_capped) * 2),
        opacity: 0.7,
        stroke: 'white',
        strokeWidth: 0.5,
        title: d => `Station: ${d.station}\nSpecies: ${d.species_count}\nDate: ${d.datetime.split('T')[0]}\nPC${components[0]}: ${d.pc1.toFixed(3)}\nPC${components[1]}: ${d.pc2.toFixed(3)}`
      })
    );

    // Loading vectors (if enabled)
    if (showLoadings) {
      // Scale factor for loading vectors (to make them visible)
      const maxPC = Math.max(
        Math.max(...plotPoints.map(p => Math.abs(p.pc1))),
        Math.max(...plotPoints.map(p => Math.abs(p.pc2)))
      );
      const loadingScale = maxPC * 0.8;

      // Loading vector arrows
      marks.push(
        Plot.arrow(plotLoadings, {
          x1: 0,
          y1: 0,
          x2: d => d.pc1 * loadingScale,
          y2: d => d.pc2 * loadingScale,
          stroke: d => {
            // Color by category
            const categoryColors: Record<string, string> = {
              'diversity': '#e41a1c',
              'complexity': '#377eb8',
              'bioacoustic': '#4daf4a',
              'temporal': '#984ea3',
              'frequency': '#ff7f00',
              'anthropogenic': '#ffff33',
              'other': '#a65628'
            };
            return categoryColors[d.category] || '#999999';
          },
          strokeWidth: 2,
          // markerEnd: 'arrow', // Observable Plot doesn't support this directly
          opacity: 0.8
        })
      );

      // Loading vector labels
      marks.push(
        Plot.text(plotLoadings, {
          x: d => d.pc1 * loadingScale * 1.1,
          y: d => d.pc2 * loadingScale * 1.1,
          text: 'index',
          fontSize: 10,
          fill: '#333',
          fontWeight: 'bold',
          textAnchor: 'start'  // Simplified for now
        })
      );
    }

    // Create the plot
    const plot = Plot.plot({
      width,
      height,
      marginLeft: 60,
      marginRight: showLoadings ? 100 : 60,
      marginTop: 40,
      marginBottom: 60,
      
      x: {
        label: `PC${components[0]} (${(newStats.pc1Variance * 100).toFixed(1)}% variance)`,
        grid: true,
        nice: true
      },
      y: {
        label: `PC${components[1]} (${(newStats.pc2Variance * 100).toFixed(1)}% variance)`,
        grid: true,
        nice: true
      },
      
      color: {
        type: 'categorical',
        domain: data.pca_biplot.stations || data.data_sources.stations || ['9M', '14M'],
        range: colorScheme,
        legend: true
      },
      
      marks: [
        // Add zero lines
        Plot.ruleX([0], { stroke: '#ccc', strokeDasharray: '2,2' }),
        Plot.ruleY([0], { stroke: '#ccc', strokeDasharray: '2,2' }),
        ...marks
      ],
      
      title: `PCA Biplot - Acoustic Indices Dimensionality Analysis`,
      subtitle: `${newStats.nPoints.toLocaleString()} observations, ${newStats.nLoadings} indices, ${(newStats.totalVariance * 100).toFixed(1)}% total variance explained`
    });

    // Clear previous plot and append new one
    plotRef.current.innerHTML = '';
    plotRef.current.appendChild(plot);

    // Add click interaction
    plot.addEventListener('click', (_event: Event) => {
      // Future: handle plot interactions
    });

    // Cleanup function
    return () => {
      const currentRef = plotRef.current;
      if (currentRef) {
        currentRef.innerHTML = '';
      }
    };
  }, [data, width, height, components, showLoadings, maxLoadings, colorScheme]);

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading PCA analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading PCA Data</h3>
          <p className="text-red-600 text-sm">{error.message}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center" style={{ width, height }}>
        <p className="text-gray-500">No PCA data available</p>
      </div>
    );
  }

  return (
    <div className="pca-biplot-container">
      {/* Control Panel */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Bandwidth:</label>
            <select 
              value={bandwidth}
              onChange={(e) => setBandwidth(e.target.value as 'FullBW' | '8kHz')}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="FullBW">Full Bandwidth</option>
              <option value="8kHz">8kHz Limited</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Components:</label>
            <select 
              value={`${components[0]},${components[1]}`}
              onChange={(e) => {
                const [pc1, pc2] = e.target.value.split(',').map(Number);
                window.location.hash = `pc${pc1}-pc${pc2}`;
                // Note: In a real app, you'd update state properly
              }}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="1,2">PC1 vs PC2</option>
              <option value="1,3">PC1 vs PC3</option>
              <option value="2,3">PC2 vs PC3</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">
              <input 
                type="checkbox" 
                checked={showLoadings}
                onChange={() => {
                  // Note: In a real app, you'd update state properly
                  // Future: implement toggle functionality
                }}
                className="mr-1"
              />
              Show Index Loadings
            </label>
          </div>
          
          {stats && (
            <div className="text-sm text-gray-600">
              <span className="font-medium">Total Variance:</span> {(stats.totalVariance * 100).toFixed(1)}%
            </div>
          )}
          
          {data?.pca_biplot.performance && (
            <div className="text-xs text-green-600 font-medium">
              ⚡ Optimized: {data.pca_biplot.performance.reduced_n_points.toLocaleString()} points 
              (from {data.pca_biplot.performance.original_n_points.toLocaleString()})
            </div>
          )}
          
          {data?.bandwidth && (
            <div className="text-xs text-blue-600 font-medium">
              📡 {data.bandwidth === 'FullBW' ? 'Full Bandwidth' : '8kHz Limited'} Analysis
            </div>
          )}
        </div>
      </div>

      {/* Plot Container */}
      <div 
        ref={plotRef} 
        className="pca-biplot-plot border border-gray-200 rounded-lg bg-white"
        style={{ width: '100%', minHeight: height }}
      />

      {/* Legend and Info */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded-lg">
          <h4 className="font-semibold text-blue-800 mb-2">Interpretation Guide</h4>
          <ul className="text-blue-700 space-y-1">
            <li>• <strong>Point size:</strong> Species detection count</li>
            <li>• <strong>Point color:</strong> Station location</li>
            <li>• <strong>Arrows:</strong> Acoustic index contributions</li>
            <li>• <strong>Arrow direction:</strong> Index influence on components</li>
          </ul>
        </div>
        
        {showLoadings && (
          <div className="bg-green-50 p-3 rounded-lg">
            <h4 className="font-semibold text-green-800 mb-2">Index Categories</h4>
            <div className="grid grid-cols-2 gap-1 text-green-700 text-xs">
              <div><span className="inline-block w-3 h-3 bg-red-500 mr-1"></span>Diversity</div>
              <div><span className="inline-block w-3 h-3 bg-blue-500 mr-1"></span>Complexity</div>
              <div><span className="inline-block w-3 h-3 bg-green-500 mr-1"></span>Bioacoustic</div>
              <div><span className="inline-block w-3 h-3 bg-purple-500 mr-1"></span>Temporal</div>
              <div><span className="inline-block w-3 h-3 bg-orange-500 mr-1"></span>Frequency</div>
              <div><span className="inline-block w-3 h-3 bg-yellow-500 mr-1"></span>Anthropogenic</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}