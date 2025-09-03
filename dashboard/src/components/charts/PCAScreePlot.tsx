import React from 'react';
import { Line } from '@nivo/line';
import { PCAComponent } from '../../lib/data/usePCAAnalysis';

interface PCAScreePlotProps {
  data: PCAComponent[];
  className?: string;
}

export function PCAScreePlot({ data, className = '' }: PCAScreePlotProps) {
  // Validate and clean data to prevent NaN values
  const cleanData = data
    .slice(0, 10)
    .filter(d => 
      typeof d.component_number === 'number' && 
      !isNaN(d.component_number) &&
      typeof d.explained_variance === 'number' && 
      !isNaN(d.explained_variance) &&
      typeof d.cumulative_variance === 'number' && 
      !isNaN(d.cumulative_variance)
    );

  // Prepare data for nivo with validation
  const chartData = [
    {
      id: 'explained_variance',
      color: 'hsl(142, 76%, 36%)', // Green
      data: cleanData.map(d => ({
        x: d.component_number,
        y: Math.max(0, d.explained_variance), // Ensure positive values
        component: d.component
      }))
    },
    {
      id: 'cumulative_variance',
      color: 'hsl(217, 91%, 60%)', // Blue
      data: cleanData.map(d => ({
        x: d.component_number,
        y: Math.max(0, Math.min(100, d.cumulative_variance)), // Clamp to 0-100
        component: d.component
      }))
    }
  ];

  // Don't render if we don't have clean data
  if (cleanData.length === 0) {
    return (
      <div className={`h-80 flex items-center justify-center ${className}`}>
        <div className="text-muted-foreground">No valid data for visualization</div>
      </div>
    );
  }

  return (
    <div className={`h-80 ${className}`}>
      <Line
        data={chartData}
        margin={{ top: 20, right: 110, bottom: 50, left: 60 }}
        xScale={{
          type: 'linear',
          min: 1,
          max: 10
        }}
        yScale={{
          type: 'linear',
          min: 0,
          max: 100
        }}
        axisTop={null}
        axisRight={null}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Principal Component',
          legendOffset: 36,
          legendPosition: 'middle',
          tickValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Variance Explained (%)',
          legendOffset: -50,
          legendPosition: 'middle'
        }}
        pointSize={6}
        pointColor={{ theme: 'background' }}
        pointBorderWidth={2}
        pointBorderColor={{ from: 'serieColor' }}
        pointLabelYOffset={-12}
        enableArea={false}
        useMesh={true}
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
        tooltip={({ point }) => (
          <div className="bg-white p-3 shadow-lg rounded border">
            <div className="font-semibold">{(point.data as any).component}</div>
            <div className="text-sm text-gray-600">
              {point.serieId === 'explained_variance' ? 'Individual' : 'Cumulative'}: {point.data.yFormatted}%
            </div>
          </div>
        )}
        theme={{
          background: 'transparent',
          text: {
            fontSize: 12,
            fill: 'hsl(var(--foreground))',
            outlineWidth: 0,
            outlineColor: 'transparent'
          },
          axis: {
            domain: {
              line: {
                stroke: 'hsl(var(--border))',
                strokeWidth: 1
              }
            },
            legend: {
              text: {
                fontSize: 12,
                fill: 'hsl(var(--foreground))'
              }
            },
            ticks: {
              line: {
                stroke: 'hsl(var(--border))',
                strokeWidth: 1
              },
              text: {
                fontSize: 11,
                fill: 'hsl(var(--muted-foreground))'
              }
            }
          },
          grid: {
            line: {
              stroke: 'hsl(var(--border))',
              strokeWidth: 1,
              strokeOpacity: 0.3
            }
          },
          crosshair: {
            line: {
              stroke: 'hsl(var(--border))',
              strokeWidth: 1,
              strokeOpacity: 0.35
            }
          }
        }}
      />
    </div>
  );
}