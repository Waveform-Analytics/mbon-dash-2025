'use client'

import { ResponsiveBar } from '@nivo/bar'

interface MonthlyData {
  month: number
  month_name: string
  total_records: number
  fish_presence_rate: number
  mean_fish_intensity: number
}

interface SeasonalActivityChartProps {
  data: MonthlyData[]
}

export default function SeasonalActivityChart({ data }: SeasonalActivityChartProps) {
  // Transform data for visualization
  const chartData = data.map(item => ({
    month: item.month_name.slice(0, 3), // Short month names
    'Fish Presence Rate': (item.fish_presence_rate * 100), // Convert to percentage
    'Records': item.total_records / 100, // Scale down for dual axis effect
    'Mean Intensity': item.mean_fish_intensity
  }))

  return (
    <div>
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">
          Seasonal Fish Activity Patterns
        </h4>
        <p className="text-sm text-gray-600 mb-4">
          Fish presence rates across all months show clear seasonal patterns with peak activity 
          in spring/summer and lower activity in winter months. This confirms the non-stationary 
          nature of marine soundscapes.
        </p>
      </div>

      <div style={{ height: '400px' }}>
        <ResponsiveBar
          data={chartData}
          keys={['Fish Presence Rate']}
          indexBy="month"
          margin={{ top: 50, right: 60, bottom: 60, left: 60 }}
          padding={0.2}
          valueScale={{ type: 'linear' }}
          indexScale={{ type: 'band', round: true }}
          colors={['#3B82F6']}
          borderRadius={4}
          borderWidth={1}
          borderColor="rgba(255, 255, 255, 0.2)"
          axisTop={null}
          axisRight={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Records (×100)',
            legendPosition: 'middle',
            legendOffset: 40,
            format: (value) => `${Math.round(value * 100)}`
          }}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Month',
            legendPosition: 'middle',
            legendOffset: 40
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Fish Presence Rate (%)',
            legendPosition: 'middle',
            legendOffset: -45
          }}
          enableLabel={false}
          enableGridX={false}
          enableGridY={true}
          gridYValues={5}
          theme={{
            axis: {
              domain: { line: { stroke: '#E5E7EB' } },
              ticks: { line: { stroke: '#E5E7EB' } }
            },
            grid: {
              line: { stroke: '#F3F4F6' }
            }
          }}
          tooltip={({ indexValue, value, color }) => (
            <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="font-medium">{indexValue}</span>
              </div>
              <div className="text-sm text-gray-600">
                Fish Presence: <span className="font-medium text-gray-900">{value.toFixed(1)}%</span>
              </div>
            </div>
          )}
          layers={[
            'grid',
            'axes',
            'bars',
            // Add a line overlay for record counts
            ({ bars, xScale, yScale }) => (
              <g>
                {chartData.map((d, i) => {
                  if (i === 0) return null
                  const prevPoint = chartData[i - 1]
                  const currentPoint = d
                  
                  const x1 = xScale(prevPoint.month) + xScale.bandwidth() / 2
                  const y1 = yScale(prevPoint.Records * 100 / 100) // Convert back
                  const x2 = xScale(currentPoint.month) + xScale.bandwidth() / 2
                  const y2 = yScale(currentPoint.Records * 100 / 100)
                  
                  return (
                    <line
                      key={`line-${i}`}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#EF4444"
                      strokeWidth={2}
                    />
                  )
                })}
                {chartData.map((d) => {
                  const x = xScale(d.month) + xScale.bandwidth() / 2
                  const y = yScale(d.Records * 100 / 100)
                  
                  return (
                    <circle
                      key={`point-${d.month}`}
                      cx={x}
                      cy={y}
                      r={4}
                      fill="#EF4444"
                      stroke="white"
                      strokeWidth={2}
                    />
                  )
                })}
              </g>
            ),
            'legends'
          ]}
        />
      </div>

      <div className="mt-4 grid md:grid-cols-3 gap-4 text-sm">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="font-medium text-blue-800">Peak Activity</span>
          </div>
          <p className="text-blue-700">
            {data.reduce((max, current) => 
              current.fish_presence_rate > max.fish_presence_rate ? current : max
            ).month_name} - {(data.reduce((max, current) => 
              current.fish_presence_rate > max.fish_presence_rate ? current : max
            ).fish_presence_rate * 100).toFixed(1)}%
          </p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="font-medium text-red-800">Lowest Activity</span>
          </div>
          <p className="text-red-700">
            {data.reduce((min, current) => 
              current.fish_presence_rate < min.fish_presence_rate ? current : min
            ).month_name} - {(data.reduce((min, current) => 
              current.fish_presence_rate < min.fish_presence_rate ? current : min
            ).fish_presence_rate * 100).toFixed(1)}%
          </p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="font-medium text-green-800">Annual Average</span>
          </div>
          <p className="text-green-700">
            {(data.reduce((sum, item) => sum + item.fish_presence_rate, 0) / data.length * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  )
}