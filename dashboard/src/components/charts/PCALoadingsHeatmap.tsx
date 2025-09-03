import React, { useState } from 'react';
import { LoadingsData } from '../../lib/data/usePCAAnalysis';

interface PCALoadingsHeatmapProps {
  data: LoadingsData[];
  indices: string[];
  components: string[];
  className?: string;
}

function getLoadingColor(loading: number): string {
  const abs = Math.abs(loading);
  const hue = loading > 0 ? 220 : 0; // Blue for positive, red for negative
  const saturation = Math.min(abs * 80 + 20, 100);
  const lightness = Math.max(100 - (abs * 50), 40);
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

export function PCALoadingsHeatmap({ data, indices, components, className = '' }: PCALoadingsHeatmapProps) {
  const [selectedCell, setSelectedCell] = useState<{ index: string; component: string; loading: number } | null>(null);

  // Create lookup map for loadings
  const loadingMap = new Map<string, number>();
  data.forEach(item => {
    loadingMap.set(`${item.index}-${item.component}`, item.loading);
  });

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Heatmap */}
      <div className="overflow-auto max-h-[500px] border rounded-lg">
        <div className="min-w-fit">
          <div className="grid gap-0.5 text-xs bg-gray-50" 
               style={{ gridTemplateColumns: `120px repeat(${components.length}, 60px)` }}>
            
            {/* Header row */}
            <div className="bg-white p-2 font-semibold border-r border-b sticky top-0 z-10">
              Acoustic Index
            </div>
            {components.map(component => (
              <div key={component} className="bg-white p-2 font-semibold border-b text-center sticky top-0 z-10">
                {component}
              </div>
            ))}
            
            {/* Data rows */}
            {indices.map(index => (
              <React.Fragment key={index}>
                <div className="bg-white p-2 font-medium border-r text-right sticky left-0 z-10">
                  {index}
                </div>
                {components.map(component => {
                  const loading = loadingMap.get(`${index}-${component}`) || 0;
                  return (
                    <div
                      key={`${index}-${component}`}
                      className="p-1 text-center cursor-pointer hover:ring-2 hover:ring-blue-400 transition-all duration-200"
                      style={{
                        backgroundColor: getLoadingColor(loading),
                        color: Math.abs(loading) > 0.5 ? 'white' : 'black'
                      }}
                      onClick={() => setSelectedCell({ index, component, loading })}
                      title={`${index} - ${component}: ${loading.toFixed(3)}`}
                    >
                      {loading.toFixed(2)}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* Legend and info */}
      <div className="flex flex-wrap gap-6 items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: getLoadingColor(-0.8) }}></div>
            <span>Negative loading</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-white border"></div>
            <span>No loading</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: getLoadingColor(0.8) }}></div>
            <span>Positive loading</span>
          </div>
        </div>
        
        <div className="text-gray-600">
          {indices.length} indices × {components.length} components
        </div>
      </div>

      {/* Selected cell info */}
      {selectedCell && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="font-semibold text-blue-900 mb-2">Loading Details</div>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium">Index:</span> {selectedCell.index}
            </div>
            <div>
              <span className="font-medium">Component:</span> {selectedCell.component}
            </div>
            <div>
              <span className="font-medium">Loading:</span> {selectedCell.loading.toFixed(4)}
            </div>
          </div>
          <div className="mt-3 text-sm text-blue-800">
            {Math.abs(selectedCell.loading) > 0.3 
              ? `Strong ${selectedCell.loading > 0 ? 'positive' : 'negative'} contributor to ${selectedCell.component}`
              : `Weak contributor to ${selectedCell.component}`
            }
          </div>
        </div>
      )}
    </div>
  );
}