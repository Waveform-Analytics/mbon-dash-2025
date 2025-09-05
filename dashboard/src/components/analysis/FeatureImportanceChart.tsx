'use client'

import { ResponsiveBar } from '@nivo/bar'

interface FeatureImportance {
  model_type: string
  target: string
  rank: number
  feature: string
  importance: number
}

interface FeatureImportanceChartProps {
  data: FeatureImportance[]
  topFeatures: string[]
}

export default function FeatureImportanceChart({ data, topFeatures }: FeatureImportanceChartProps) {
  // Get Random Forest feature importance for fish_presence
  const rfImportance = data
    .filter(d => d.model_type === 'random_forest' && d.target === 'fish_presence')
    .map(d => ({
      feature: d.feature,
      importance: d.importance,
      rank: d.rank
    }))
    .sort((a, b) => b.importance - a.importance)

  // Create chart data
  const chartData = rfImportance.map(item => ({
    feature: item.feature,
    'Feature Importance': item.importance,
    isTopFeature: topFeatures.includes(item.feature)
  }))

  return (
    <div>
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">
          Feature Importance Analysis
        </h4>
        <p className="text-sm text-gray-600 mb-4">
          Random Forest feature importance scores show which PCA components are most predictive 
          of fish presence. PC1, PC4, and PC5 consistently emerge as the most important features 
          across different models.
        </p>
      </div>

      <div style={{ height: '300px' }}>
        <ResponsiveBar
          data={chartData}
          keys={['Feature Importance']}
          indexBy="feature"
          margin={{ top: 20, right: 40, bottom: 60, left: 80 }}
          padding={0.3}
          layout="vertical"
          valueScale={{ type: 'linear' }}
          indexScale={{ type: 'band', round: true }}
          colors={(bar) => bar.data.isTopFeature ? '#3B82F6' : '#9CA3AF'}
          borderRadius={4}
          borderWidth={1}
          borderColor="rgba(255, 255, 255, 0.2)"
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Feature Importance Score',
            legendPosition: 'middle',
            legendOffset: 40
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'PCA Component',
            legendPosition: 'middle',
            legendOffset: -60
          }}
          enableLabel={true}
          label={(d) => d.value.toFixed(3)}
          labelSkipWidth={12}
          labelTextColor="white"
          enableGridX={true}
          enableGridY={false}
          gridXValues={4}
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
                Importance: <span className="font-medium text-gray-900">{value.toFixed(3)}</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {topFeatures.includes(indexValue as string) ? 'Top consistent feature' : 'Secondary feature'}
              </div>
            </div>
          )}
        />
      </div>

      <div className="mt-6 space-y-4">
        <div>
          <h5 className="font-medium text-gray-900 mb-3">Top Predictive Components</h5>
          <div className="grid md:grid-cols-3 gap-4">
            {topFeatures.slice(0, 3).map((feature, idx) => {
              const importance = rfImportance.find(f => f.feature === feature)?.importance || 0
              return (
                <div key={feature} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-blue-800">{feature}</span>
                    <span className="text-sm text-blue-600">#{idx + 1}</span>
                  </div>
                  <p className="text-sm text-blue-700">
                    Importance: {importance.toFixed(3)}
                  </p>
                </div>
              )
            })}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h5 className="font-medium text-gray-900 mb-2">Feature Interpretation</h5>
          <p className="text-sm text-gray-700 mb-3">
            These PCA components represent combinations of the original 20+ acoustic indices. 
            The consistent importance of PC1, PC4, and PC5 across different models suggests 
            they capture fundamental acoustic patterns associated with fish presence.
          </p>
          <div className="grid md:grid-cols-2 gap-4 text-xs text-gray-600">
            <div>
              <p className="font-medium text-gray-700">PC1 (Highest Importance)</p>
              <p>Likely captures overall acoustic activity and energy levels</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">PC4 & PC5 (Consistent Predictors)</p>
              <p>May represent specific frequency patterns or temporal signatures</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}