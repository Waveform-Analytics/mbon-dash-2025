import React, { useMemo } from 'react';
import { ResponsiveRadar } from '@nivo/radar';
import { AcousticIndex, InstrumentLocation } from '../../data/mockData';

interface InstrumentComparisonChartProps {
  data: AcousticIndex[];
  instruments: InstrumentLocation[];
}

export function InstrumentComparisonChart({ data, instruments }: InstrumentComparisonChartProps) {
  const radarData = useMemo(() => {
    const indices = ['aci', 'adi', 'aei', 'bi', 'ndsi'];
    const indexNames = {
      aci: 'ACI',
      adi: 'ADI',
      aei: 'AEI', 
      bi: 'BI',
      ndsi: 'NDSI'
    };

    // Calculate averages for each instrument and index
    const instrumentAverages: { [instrumentId: string]: { [index: string]: number } } = {};
    
    instruments.forEach(instrument => {
      instrumentAverages[instrument.id] = {};
      
      indices.forEach(index => {
        const instrumentData = data.filter(d => d.instrumentId === instrument.id);
        const values = instrumentData.map(d => d[index as keyof AcousticIndex] as number)
          .filter(v => typeof v === 'number');
        
        if (values.length > 0) {
          instrumentAverages[instrument.id][index] = values.reduce((sum, val) => sum + val, 0) / values.length;
        } else {
          instrumentAverages[instrument.id][index] = 0;
        }
      });
    });

    // Normalize values to 0-100 scale for radar chart
    const normalizedData = indices.map(index => {
      const allValues = Object.values(instrumentAverages).map(avgs => avgs[index]);
      const minVal = Math.min(...allValues);
      const maxVal = Math.max(...allValues);
      const range = maxVal - minVal;
      
      const dataPoint: any = {
        index: indexNames[index as keyof typeof indexNames]
      };
      
      instruments.forEach(instrument => {
        const rawValue = instrumentAverages[instrument.id][index];
        const normalizedValue = range > 0 ? ((rawValue - minVal) / range) * 100 : 50;
        dataPoint[instrument.name] = normalizedValue;
      });
      
      return dataPoint;
    });

    return normalizedData;
  }, [data, instruments]);

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="h-96">
      <ResponsiveRadar
        data={radarData}
        keys={instruments.map(i => i.name)}
        indexBy="index"
        valueFormat=">-.1f"
        margin={{ top: 70, right: 80, bottom: 40, left: 80 }}
        borderColor={{ from: 'color' }}
        gridLevels={5}
        gridShape="linear"
        gridLabelOffset={36}
        enableDots={true}
        dotSize={8}
        dotColor={{ theme: 'background' }}
        dotBorderWidth={2}
        colors={colors}
        blendMode="multiply"
        fillOpacity={0.1}
        motionConfig="wobbly"
        legends={[
          {
            anchor: 'top-left',
            direction: 'column',
            translateX: -50,
            translateY: -40,
            itemWidth: 80,
            itemHeight: 20,
            itemTextColor: '#374151',
            symbolSize: 12,
            symbolShape: 'circle',
            effects: [
              {
                on: 'hover',
                style: {
                  itemTextColor: '#000'
                }
              }
            ]
          }
        ]}
        theme={{
          axis: {
            ticks: {
              text: {
                fontSize: 12,
                fill: '#6b7280'
              }
            }
          },
          grid: {
            line: {
              stroke: '#e5e7eb',
              strokeWidth: 1
            }
          },
          tooltip: {
            container: {
              background: 'white',
              color: '#374151',
              fontSize: '12px',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb'
            }
          }
        }}
        tooltip={({ index, value, color, formattedValue }) => (
          <div className="bg-white p-3 border rounded-lg shadow-lg">
            <div className="flex items-center gap-2 mb-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: color }}
              />
              <span className="font-semibold">{index}</span>
            </div>
            <div className="text-sm text-muted-foreground">
              Acoustic Index: {value}
            </div>
            <div className="text-sm">
              Normalized Score: <span className="font-semibold">{formattedValue}</span>
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Higher values indicate stronger presence of this acoustic characteristic
            </div>
          </div>
        )}
      />
      
      {/* Interpretation guide */}
      <div className="mt-4 p-3 bg-gray-50 rounded text-xs text-muted-foreground">
        <div className="font-medium mb-1">Interpretation Guide:</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          <div>• Outer edge = Higher relative values</div>
          <div>• Inner area = Lower relative values</div>
          <div>• Overlapping areas show similar patterns</div>
        </div>
      </div>
    </div>
  );
}