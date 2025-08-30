import React, { useMemo } from 'react';
import { ResponsiveLine } from '@nivo/line';
import { AcousticIndex } from '../../data/mockData';

interface SeasonalTrendsChartProps {
  data: AcousticIndex[];
  selectedIndex: string;
}

export function SeasonalTrendsChart({ data, selectedIndex }: SeasonalTrendsChartProps) {
  const chartData = useMemo(() => {
    // Group data by month and calculate monthly averages
    const monthlyData: { [key: string]: { sum: number; count: number } } = {};
    
    data.forEach(d => {
      const date = new Date(d.date);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = { sum: 0, count: 0 };
      }
      
      const value = d[selectedIndex as keyof AcousticIndex] as number;
      if (typeof value === 'number') {
        monthlyData[monthKey].sum += value;
        monthlyData[monthKey].count += 1;
      }
    });

    // Convert to chart format
    const chartPoints = Object.entries(monthlyData)
      .map(([month, values]) => ({
        x: month,
        y: values.sum / values.count
      }))
      .sort((a, b) => a.x.localeCompare(b.x));

    return [
      {
        id: selectedIndex.toUpperCase(),
        data: chartPoints
      }
    ];
  }, [data, selectedIndex]);

  const indexDetails = {
    aci: { name: 'Acoustic Complexity Index', color: '#3b82f6' },
    adi: { name: 'Acoustic Diversity Index', color: '#10b981' },
    aei: { name: 'Acoustic Evenness Index', color: '#f59e0b' },
    bi: { name: 'Bioacoustic Index', color: '#ef4444' },
    ndsi: { name: 'Normalized Difference Soundscape Index', color: '#8b5cf6' }
  };

  const currentIndex = indexDetails[selectedIndex as keyof typeof indexDetails];

  return (
    <div className="h-96">
      <ResponsiveLine
        data={chartData}
        margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
        xScale={{ type: 'point' }}
        yScale={{
          type: 'linear',
          min: 'auto',
          max: 'auto',
          stacked: false,
          reverse: false
        }}
        curve="cardinal"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: -45,
          legend: 'Month',
          legendOffset: 46,
          legendPosition: 'middle',
          format: (value) => {
            const [year, month] = value.split('-');
            return new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('en-US', { 
              month: 'short', 
              year: '2-digit' 
            });
          }
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: currentIndex?.name || selectedIndex.toUpperCase(),
          legendOffset: -50,
          legendPosition: 'middle'
        }}
        pointSize={8}
        pointColor={{ theme: 'background' }}
        pointBorderWidth={2}
        pointBorderColor={{ from: 'serieColor' }}
        pointLabelYOffset={-12}
        useMesh={true}
        colors={[currentIndex?.color || '#3b82f6']}
        legends={[
          {
            anchor: 'bottom-right',
            direction: 'column',
            justify: false,
            translateX: 100,
            translateY: 0,
            itemsSpacing: 0,
            itemDirection: 'left-to-right',
            itemWidth: 80,
            itemHeight: 20,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: 'circle',
            symbolBorderColor: 'rgba(0, 0, 0, .5)',
            effects: [
              {
                on: 'hover',
                style: {
                  itemBackground: 'rgba(0, 0, 0, .03)',
                  itemOpacity: 1
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
            },
            legend: {
              text: {
                fontSize: 14,
                fill: '#374151'
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
        tooltip={({ point }) => (
          <div className="bg-white p-3 border rounded-lg shadow-lg">
            <div className="font-semibold">{currentIndex?.name}</div>
            <div className="text-sm text-muted-foreground">
              Month: {(() => {
                const [year, month] = (point.data.x as string).split('-');
                return new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('en-US', { 
                  month: 'long', 
                  year: 'numeric' 
                });
              })()}
            </div>
            <div className="text-sm">
              Value: <span className="font-semibold">{(point.data.y as number).toFixed(2)}</span>
            </div>
          </div>
        )}
      />
    </div>
  );
}