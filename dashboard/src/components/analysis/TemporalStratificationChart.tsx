'use client'

import { ResponsiveLine } from '@nivo/line'

interface MonthlyDistribution {
  month: number
  total_records: number
  activity_rate: number
}

interface TemporalStratificationChartProps {
  data: MonthlyDistribution[]
}

export default function TemporalStratificationChart({ data }: TemporalStratificationChartProps) {
  const monthNames = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ]

  // Transform data for line chart
  const chartData = [
    {
      id: 'Activity Rate',
      data: data.map(d => ({
        x: monthNames[d.month - 1],
        y: d.activity_rate * 100
      }))
    },
    {
      id: 'Record Count (×10)',
      data: data.map(d => ({
        x: monthNames[d.month - 1],
        y: d.total_records / 10 // Scale down for visualization
      }))
    }
  ]

  return (
    <div>
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">
          Temporal Distribution Validation
        </h4>
        <p className="text-sm text-gray-600 mb-4">
          This chart shows how temporal stratification preserves the seasonal patterns in the data. 
          Both training and testing sets maintain proportional representation from each month, 
          ensuring models can learn and be evaluated on the full range of seasonal variation.
        </p>
      </div>

      <div style={{ height: '400px' }}>
        <ResponsiveLine
          data={chartData}
          margin={{ top: 50, right: 110, bottom: 60, left: 60 }}
          xScale={{ type: 'point' }}
          yScale={{
            type: 'linear',
            min: 0,
            max: 'auto',
            stacked: false,
            reverse: false
          }}
          yFormat=" >-.2f"
          curve="cardinal"
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Month',
            legendOffset: 40,
            legendPosition: 'middle'
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Value',
            legendOffset: -45,
            legendPosition: 'middle'
          }}
          enableGridX={false}
          enableGridY={true}
          colors={['#3B82F6', '#EF4444']}
          pointSize={8}
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
          theme={{
            axis: {
              domain: { line: { stroke: '#E5E7EB' } },
              ticks: { line: { stroke: '#E5E7EB' } }
            },
            grid: {
              line: { stroke: '#F3F4F6' }
            }
          }}
          tooltip={({ point }) => (
            <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: point.serieColor }}
                />
                <span className="font-medium">{point.serieId}</span>
              </div>
              <div className="text-sm text-gray-600">
                {point.data.x}: <span className="font-medium text-gray-900">
                  {point.serieId === 'Activity Rate' 
                    ? `${point.data.y.toFixed(1)}%`
                    : `${(point.data.y * 10).toFixed(0)} records`
                  }
                </span>
              </div>
            </div>
          )}
        />
      </div>

      <div className="mt-6 grid md:grid-cols-2 gap-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h5 className="font-medium text-green-800 mb-2">✅ Stratification Benefits</h5>
          <ul className="space-y-1 text-sm text-green-700">
            <li>• Preserves seasonal patterns in both train/test sets</li>
            <li>• Ensures model sees full range of temporal variation</li>
            <li>• Provides realistic performance estimates</li>
            <li>• Enables better generalization across seasons</li>
          </ul>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h5 className="font-medium text-red-800 mb-2">❌ Random Split Problems</h5>
          <ul className="space-y-1 text-sm text-red-700">
            <li>• Ignores temporal structure of marine data</li>
            <li>• May create train/test sets with different seasons</li>
            <li>• Overly optimistic performance estimates</li>
            <li>• Poor generalization to unseen time periods</li>
          </ul>
        </div>
      </div>
    </div>
  )
}