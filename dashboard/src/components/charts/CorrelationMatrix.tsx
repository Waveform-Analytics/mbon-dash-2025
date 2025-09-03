import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { CorrelationMatrixData } from '../../lib/data/useCorrelationMatrix';

interface CorrelationMatrixProps {
  data: CorrelationMatrixData;
}

function getCorrelationColor(correlation: number): string {
  const abs = Math.abs(correlation);
  const hue = correlation > 0 ? 0 : 240; // red for positive, blue for negative
  const saturation = Math.min(abs * 100, 100);
  const lightness = Math.max(100 - (abs * 50), 50);
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

export function CorrelationMatrix({ data }: CorrelationMatrixProps) {
  const [selectedCell, setSelectedCell] = useState<{ x: string; y: string; value: number } | null>(null);
  const [showOnlyHigh, setShowOnlyHigh] = useState(false);

  // Create correlation lookup
  const correlationMap = useMemo(() => {
    const map = new Map<string, number>();
    data.matrix_data.forEach(point => {
      map.set(`${point.x}-${point.y}`, point.value);
    });
    return map;
  }, [data.matrix_data]);

  const filteredIndices = useMemo(() => {
    if (!showOnlyHigh) return data.indices; // Show ALL indices when unchecked
    
    // Get indices involved in high correlations
    const highCorrIndices = new Set<string>();
    data.high_correlations.forEach(corr => {
      highCorrIndices.add(corr.index1);
      highCorrIndices.add(corr.index2);
    });
    
    return data.indices.filter(idx => highCorrIndices.has(idx));
  }, [data, showOnlyHigh]);

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={showOnlyHigh}
              onChange={(e) => setShowOnlyHigh(e.target.checked)}
              className="rounded"
            />
            Show only indices with high correlations (|r| ≥ {data.metadata.threshold})
          </label>
        </div>
        
        <div className="text-sm text-gray-600">
          Showing {filteredIndices.length} of {data.statistics.total_indices} indices
        </div>
      </div>

      {/* Matrix visualization */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main matrix */}
        <div className="lg:col-span-2">
          <Card className="overflow-hidden">
            <CardHeader>
              <CardTitle>Correlation Matrix</CardTitle>
              <p className="text-sm text-gray-600">
                Click on cells to see correlation details. Colors: blue (negative) to red (positive).
              </p>
            </CardHeader>
            <CardContent>
              <div className="relative overflow-auto max-h-[600px]">
                {/* Matrix grid with fixed sizing for scrolling */}
                <div className="min-w-fit">
                  <div className="grid gap-0.5 text-xs" 
                       style={{ gridTemplateColumns: `100px repeat(${filteredIndices.length}, 25px)` }}>
                    
                    {/* Header row - sticky */}
                    <div className="sticky top-0 left-0 z-20 bg-white border-b border-r border-gray-300"></div>
                    {filteredIndices.map(colIndex => (
                      <div key={colIndex} 
                           className="sticky top-0 z-10 bg-white border-b border-gray-300 h-20 flex items-end justify-center text-gray-600 font-mono text-xs">
                        <span className="transform -rotate-90 whitespace-nowrap origin-bottom" title={colIndex}>{colIndex}</span>
                      </div>
                    ))}
                    
                    {/* Data rows */}
                    {filteredIndices.map(rowIndex => (
                      <React.Fragment key={rowIndex}>
                        {/* Row header - sticky */}
                        <div className="sticky left-0 z-10 bg-white border-r border-gray-300 flex items-center justify-end pr-2 h-6 text-gray-600 font-mono text-xs">
                          <span className="truncate max-w-[90px]" title={rowIndex}>{rowIndex}</span>
                        </div>
                        
                        {/* Row cells */}
                        {filteredIndices.map(colIndex => {
                          const correlation = correlationMap.get(`${rowIndex}-${colIndex}`) ?? 0;
                          const isHighCorr = Math.abs(correlation) >= data.metadata.threshold && rowIndex !== colIndex;
                          const isSelected = selectedCell?.x === rowIndex && selectedCell?.y === colIndex;
                          
                          return (
                            <div
                              key={colIndex}
                              className={`h-6 w-full cursor-pointer border border-gray-200 hover:ring-1 hover:ring-blue-300 transition-all ${
                                isSelected ? 'ring-2 ring-blue-500 z-10' : ''
                              }`}
                              style={{ 
                                backgroundColor: getCorrelationColor(correlation),
                                opacity: rowIndex === colIndex ? 0.3 : 1
                              }}
                              onClick={() => setSelectedCell({ x: rowIndex, y: colIndex, value: correlation })}
                              title={`${rowIndex} ↔ ${colIndex}: ${correlation.toFixed(3)}`}
                            >
                              {isHighCorr && (
                                <div className="w-full h-full flex items-center justify-center">
                                  <div className="w-1.5 h-1.5 bg-white rounded-full shadow-sm"></div>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </React.Fragment>
                    ))}
                  </div>
                  
                  {/* Color legend */}
                  <div className="mt-4 flex items-center justify-center gap-2 text-xs">
                    <span>-1</span>
                    <div className="flex">
                      {[-1, -0.5, 0, 0.5, 1].map(val => (
                        <div key={val} 
                             className="w-6 h-3 border border-gray-300"
                             style={{ backgroundColor: getCorrelationColor(val) }}
                        />
                      ))}
                    </div>
                    <span>+1</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Selected cell details - moved to sidebar */}
        <div className="lg:col-span-1">
          <Card className={`sticky top-4 ${selectedCell ? 'bg-blue-50 border-blue-200' : 'bg-gray-50'}`}>
            <CardHeader>
              <CardTitle className="text-lg">
                {selectedCell ? 'Selected Correlation' : 'Click a Cell'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedCell ? (
                <div className="space-y-3">
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Indices</div>
                    <div className="font-mono font-medium text-lg">
                      {selectedCell.x} ↔ {selectedCell.y}
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-sm text-gray-600 mb-1">Correlation</div>
                    <div className={`font-mono font-bold text-2xl ${
                      selectedCell.value > 0 ? 'text-red-600' : selectedCell.value < 0 ? 'text-blue-600' : 'text-gray-600'
                    }`}>
                      {selectedCell.value.toFixed(3)}
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    {Math.abs(selectedCell.value) >= data.metadata.threshold && selectedCell.x !== selectedCell.y && (
                      <div className="bg-red-100 text-red-800 p-2 rounded text-center">
                        <strong>High correlation</strong><br/>
                        (≥{data.metadata.threshold})
                      </div>
                    )}
                    {selectedCell.x === selectedCell.y && (
                      <div className="bg-gray-100 text-gray-700 p-2 rounded text-center">
                        Self-correlation<br/>(diagonal)
                      </div>
                    )}
                    {Math.abs(selectedCell.value) < data.metadata.threshold && selectedCell.x !== selectedCell.y && (
                      <div className="bg-green-100 text-green-800 p-2 rounded text-center">
                        <strong>Low correlation</strong><br/>
                        (&lt;{data.metadata.threshold})
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <div className="mb-2">📊</div>
                  <div className="text-sm">
                    Click on any cell in the matrix to see detailed correlation information
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-blue-600">
              {data.statistics.total_indices}
            </div>
            <div className="text-sm text-gray-600">Total Indices</div>
          </CardContent>
        </Card>
        
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-red-600">
              {data.statistics.high_correlation_pairs}
            </div>
            <div className="text-sm text-gray-600">High Correlations</div>
          </CardContent>
        </Card>
        
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-amber-600">
              {data.statistics.suggested_removals}
            </div>
            <div className="text-sm text-gray-600">Suggested Removals</div>
          </CardContent>
        </Card>
        
        <Card className="text-center">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {data.statistics.mean_abs_correlation.toFixed(3)}
            </div>
            <div className="text-sm text-gray-600">Mean |Correlation|</div>
          </CardContent>
        </Card>
      </div>

      {/* High correlation pairs table */}
      <Card>
        <CardHeader>
          <CardTitle>High Correlation Pairs (|r| ≥ {data.metadata.threshold})</CardTitle>
          <p className="text-sm text-gray-600">
            All {data.high_correlations.length} pairs showing high correlation - scroll to view more
          </p>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <div className="max-h-96 overflow-y-auto border rounded">
              <table className="min-w-full text-sm">
                <thead className="sticky top-0 bg-gray-50 border-b">
                  <tr>
                    <th className="text-left p-3 font-medium">Index 1</th>
                    <th className="text-left p-3 font-medium">Index 2</th>
                    <th className="text-right p-3 font-medium">Correlation</th>
                    <th className="text-left p-3 font-medium">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {data.high_correlations.map((corr, index) => (
                    <tr 
                      key={index} 
                      className="border-b hover:bg-gray-50 cursor-pointer"
                      onClick={() => setSelectedCell({ x: corr.index1, y: corr.index2, value: corr.correlation })}
                    >
                      <td className="p-3 font-mono text-xs">{corr.index1}</td>
                      <td className="p-3 font-mono text-xs">{corr.index2}</td>
                      <td className="p-3 text-right font-mono">
                        <span className={corr.correlation > 0 ? 'text-red-600' : 'text-blue-600'}>
                          {corr.correlation.toFixed(3)}
                        </span>
                      </td>
                      <td className="p-3">
                        {(data.suggested_removals.includes(corr.index1) || 
                          data.suggested_removals.includes(corr.index2)) && (
                          <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
                            Consider removal
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>

    </div>
  );
}