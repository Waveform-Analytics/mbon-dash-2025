'use client'

import { ResponsiveBar } from '@nivo/bar'

interface ModelPerformance {
  model_type: string
  target: string
  f1_score: number
  precision: number
  recall: number
  roc_auc: number
}

interface ModelPerformanceChartProps {
  data: ModelPerformance[]
}

export default function ModelPerformanceChart({ data }: ModelPerformanceChartProps) {
  // Filter to fish_presence models and transform for chart
  const fishPresenceData = data
    .filter(d => d.target === 'fish_presence')
    .map(d => ({
      model: d.model_type === 'logistic_regression' ? 'Logistic Regression' : 'Random Forest',
      'F1 Score': d.f1_score,
      'Precision': d.precision,
      'Recall': d.recall,
      'ROC-AUC': d.roc_auc
    }))

  return (
    <div>
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-2">
          Model Performance Comparison
        </h4>
        <p className="text-sm text-gray-600 mb-4">
          Performance metrics for fish presence detection across two interpretable machine learning algorithms.
          Random Forest achieves slightly better F1 score with good balance of precision and recall.
        </p>
      </div>

      <div style={{ height: '400px' }}>
        <ResponsiveBar
          data={fishPresenceData}
          keys={['F1 Score', 'Precision', 'Recall', 'ROC-AUC']}
          indexBy="model"
          margin={{ top: 50, right: 130, bottom: 60, left: 60 }}
          padding={0.3}
          valueScale={{ type: 'linear', min: 0, max: 1 }}
          indexScale={{ type: 'band', round: true }}
          colors={['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6']}
          borderRadius={4}
          borderWidth={1}
          borderColor="rgba(255, 255, 255, 0.2)"
          axisTop={null}
          axisRight={null}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Model Type',
            legendPosition: 'middle',
            legendOffset: 40
          }}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'Performance Score',
            legendPosition: 'middle',
            legendOffset: -45,
            format: (value) => value.toFixed(2)
          }}
          enableLabel={true}
          label={(d) => d.value.toFixed(3)}
          labelSkipHeight={12}
          labelTextColor="white"
          enableGridX={false}
          enableGridY={true}
          gridYValues={5}
          legends={[
            {
              dataFrom: 'keys',
              anchor: 'bottom-right',
              direction: 'column',
              justify: false,
              translateX: 120,
              translateY: 0,
              itemsSpacing: 2,
              itemWidth: 100,
              itemHeight: 20,
              itemDirection: 'left-to-right',
              itemOpacity: 0.85,
              symbolSize: 12,
              effects: [
                {
                  on: 'hover',
                  style: {
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
          tooltip={({ indexValue, id, value, color }) => (
            <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
              <div className="flex items-center space-x-2 mb-2">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: color }}
                />
                <span className="font-medium">{indexValue}</span>
              </div>
              <div className="text-sm text-gray-600">
                {id}: <span className="font-medium text-gray-900">{value.toFixed(3)}</span>
              </div>
            </div>
          )}
        />
      </div>

      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <h5 className="font-medium text-gray-900 mb-3">Performance Interpretation</h5>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-medium text-gray-700 mb-2">Random Forest (F1 = 0.618)</p>
            <ul className="space-y-1 text-gray-600">
              <li>• Better overall balance of precision and recall</li>
              <li>• Good for capturing complex feature interactions</li>
              <li>• Slightly higher recall (fewer missed detections)</li>
            </ul>
          </div>
          <div>
            <p className="font-medium text-gray-700 mb-2">Logistic Regression (F1 = 0.595)</p>
            <ul className="space-y-1 text-gray-600">
              <li>• More interpretable coefficients</li>
              <li>• Better precision (fewer false positives)</li>
              <li>• Faster training and prediction</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}