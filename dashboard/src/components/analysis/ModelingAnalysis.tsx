'use client'

import { useState } from 'react'
import { useViewData } from '@/lib/data/useViewData'
import { Waves } from 'lucide-react'
import { motion } from 'framer-motion'
import SeasonalActivityChart from '@/components/analysis/SeasonalActivityChart'
import ModelPerformanceChart from '@/components/analysis/ModelPerformanceChart'
import FeatureImportanceChart from '@/components/analysis/FeatureImportanceChart'
import TemporalStratificationChart from '@/components/analysis/TemporalStratificationChart'

interface ModelingAnalysisData {
  metadata: {
    generated_at: string
    description: string
    analysis_scope: string
  }
  dataset_summary: {
    total_records: number
    date_range: { start: string; end: string }
    stations: string[]
    temporal_coverage: string
    fish_activity_rate: number
  }
  temporal_patterns: {
    monthly_patterns: Array<{
      month: number
      month_name: string
      total_records: number
      fish_presence_rate: number
      mean_fish_intensity: number
    }>
    seasonal_insights: {
      peak_activity_month: string
      lowest_activity_month: string
      seasonal_variation_coefficient: number
      total_year_activity_rate: number
    }
  }
  model_performance: {
    performance_comparison: Array<{
      model_type: string
      target: string
      f1_score: number
      precision: number
      recall: number
      roc_auc: number
    }>
    feature_importance: Array<{
      model_type: string
      target: string
      rank: number
      feature: string
      importance: number
    }>
    model_insights: {
      best_performing_model: string
      best_f1_score: number
      consistent_top_features: string[]
    }
  }
  temporal_stratification: {
    monthly_distribution: Array<{
      month: number
      total_records: number
      activity_rate: number
    }>
    stratification_benefits: {
      overall_activity_rate: number
      seasonal_variance_preserved: number
      months_with_data: number
    }
    methodology_validation: {
      split_strategy: string
      total_records: number
      train_test_ratio: string
      temporal_coverage: string
    }
  }
  scientific_interpretation: {
    ecological_insights: string[]
    monitoring_implications: {
      year_round_deployment_viable: boolean
      seasonal_calibration_needed: boolean
      key_acoustic_indicators: string[]
      expected_accuracy_range: string
    }
    methodological_contributions: string[]
  }
  methodology: {
    stratification_approach: string
    model_types: string[]
    feature_engineering: string
    target_variables: string[]
  }
}

export default function ModelingAnalysis() {
  const [activeTab, setActiveTab] = useState<'overview' | 'methodology' | 'results' | 'interpretation'>('overview')
  const { data, loading, error } = useViewData<ModelingAnalysisData>('modeling_analysis.json')

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] bg-background">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            animate={{ 
              rotateY: [0, 15, 0, -15, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="inline-block"
          >
            <Waves className="h-12 w-12 text-primary mx-auto mb-4" />
          </motion.div>
          <p className="text-muted-foreground">Loading modeling analysis...</p>
        </motion.div>
      </div>
    );
  }
  
  if (error || !data) {
    return (
      <div className="flex items-center justify-center min-h-[400px] bg-background">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Analysis</h3>
          <p className="text-gray-600">
            {error ? (typeof error === 'string' ? error : error.message) : 'No modeling analysis data available'}
          </p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'methodology', label: 'Methodology', icon: '🔬' },
    { id: 'results', label: 'Results', icon: '📈' },
    { id: 'interpretation', label: 'Interpretation', icon: '🧬' }
  ]

  return (
    <div className="space-y-8">
      {/* Summary Cards */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Records</p>
              <p className="text-2xl font-bold text-gray-900">
                {data.dataset_summary.total_records.toLocaleString()}
              </p>
            </div>
            <div className="text-3xl">📊</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Fish Activity Rate</p>
              <p className="text-2xl font-bold text-blue-600">
                {(data.dataset_summary.fish_activity_rate * 100).toFixed(1)}%
              </p>
            </div>
            <div className="text-3xl">🐟</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Model Accuracy</p>
              <p className="text-2xl font-bold text-green-600">
                {data.model_performance.model_insights.best_f1_score.toFixed(3)}
              </p>
            </div>
            <div className="text-3xl">🎯</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Temporal Coverage</p>
              <p className="text-2xl font-bold text-purple-600">12</p>
              <p className="text-sm text-gray-600">months</p>
            </div>
            <div className="text-3xl">📅</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'overview' | 'methodology' | 'results' | 'interpretation')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  The Challenge: Fish Don't Follow Computer Rules
                </h3>
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                  <p className="text-blue-800">
                    Fish are seasonal creatures - they're much more active during spawning seasons and 
                    quieter at other times of year. Most machine learning expects data to be consistent 
                    over time, but ocean life changes dramatically with the seasons. We need to account 
                    for this natural rhythm when building our prediction models.
                  </p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Dataset Overview</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• <strong>{data.dataset_summary.total_records.toLocaleString()}</strong> total records</li>
                      <li>• <strong>{data.dataset_summary.stations.join(', ')}</strong> stations</li>
                      <li>• <strong>{data.dataset_summary.temporal_coverage}</strong></li>
                      <li>• <strong>5 sound pattern features</strong> (simplified from 56+ acoustic measurements)</li>
                      <li>• <strong>Fish present or not</strong> as what we're trying to predict</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Seasonal Patterns</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• Peak activity: <strong className="text-green-600">{data.temporal_patterns.seasonal_insights.peak_activity_month}</strong></li>
                      <li>• Lowest activity: <strong className="text-red-600">{data.temporal_patterns.seasonal_insights.lowest_activity_month}</strong></li>
                      <li>• Seasonal variation: <strong>{(data.temporal_patterns.seasonal_insights.seasonal_variation_coefficient * 100).toFixed(0)}%</strong> change between seasons</li>
                      <li>• Annual activity rate: <strong>{(data.temporal_patterns.seasonal_insights.total_year_activity_rate * 100).toFixed(1)}%</strong></li>
                    </ul>
                  </div>
                </div>
              </div>

              <SeasonalActivityChart data={data.temporal_patterns.monthly_patterns} />
            </div>
          )}

          {activeTab === 'methodology' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Smart Data Splitting: Why Season Matters
                </h3>
                <p className="text-gray-700 mb-6">
                  Instead of randomly splitting our data for training and testing (which would mix up the seasons), 
                  we carefully sampled from each month proportionally. This way, both our training and test datasets 
                  include winter quiet periods and spring/summer active periods. Why? Because we want to know if our 
                  model will actually work when deployed year-round, not just during the seasons it was trained on.
                </p>

                <div className="grid md:grid-cols-2 gap-8">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">❌ Random Split (What Most People Do)</h4>
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span>Randomly pick 70% for training, 30% for testing</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span>Mixes up seasonal patterns</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span>Makes the model look better than it really is</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span>Fails when deployed in real world</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-green-50 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">✅ Season-Aware Split (Our Approach)</h4>
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Sample the same percentage from each month</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Keeps seasonal patterns intact</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Gives honest performance estimates</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span>Works better in real deployment</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-8">
                  <h4 className="font-semibold text-gray-900 mb-4">How We Did It</h4>
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="text-sm text-gray-700 space-y-2">
                      <p><strong>Step 1:</strong> Take all the January data → randomly pick 70% for training, 30% for testing</p>
                      <p><strong>Step 2:</strong> Take all the February data → randomly pick 70% for training, 30% for testing</p>
                      <p><strong>Step 3:</strong> Repeat for all 12 months</p>
                      <p><strong>Result:</strong> Both training and testing datasets have data from every season, so we can see how well the model handles the full yearly cycle.</p>
                    </div>
                  </div>
                </div>
              </div>

              <TemporalStratificationChart data={data.temporal_stratification.monthly_distribution} />
            </div>
          )}

          {activeTab === 'results' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Which Algorithm Works Better?
                </h3>
                <p className="text-gray-700 mb-6">
                  We tested two different types of machine learning models. Random Forest (which combines many 
                  decision trees) performed slightly better than Logistic Regression (a simpler, more traditional approach). 
                  The Random Forest got about 62% accuracy at detecting when fish were present - not perfect, but definitely 
                  better than guessing.
                </p>
              </div>

              <ModelPerformanceChart data={data.model_performance.performance_comparison} />

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Best Performing Model</h4>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-green-800">Random Forest</span>
                      <span className="text-2xl font-bold text-green-600">
                        Score = {data.model_performance.model_insights.best_f1_score.toFixed(3)}
                      </span>
                    </div>
                    <p className="text-sm text-green-700">
                      Good balance between catching fish when they're there (recall) and not crying wolf when they're not (precision).
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">What Do These Numbers Mean?</h4>
                  {data.model_performance.performance_comparison
                    .filter(m => m.target === 'fish_presence' && m.model_type === 'random_forest')
                    .map((model, idx) => (
                      <div key={idx} className="space-y-3 text-sm">
                        <div className="flex justify-between">
                          <span>Precision (when it says "fish", how often is it right?):</span>
                          <span className="font-medium">{(model.precision * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Recall (when fish are there, how often does it catch them?):</span>
                          <span className="font-medium">{(model.recall * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Overall discrimination ability:</span>
                          <span className="font-medium">{model.roc_auc.toFixed(3)}</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              <FeatureImportanceChart 
                data={data.model_performance.feature_importance}
                topFeatures={data.model_performance.model_insights.consistent_top_features}
              />
            </div>
          )}

          {activeTab === 'interpretation' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  What Does This All Mean?
                </h3>
                <p className="text-gray-700 mb-6">
                  Our results show that acoustic monitoring has real potential for tracking marine life, 
                  but it's not magic - there are clear strengths and limitations we need to understand 
                  before deploying this in the real world.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">🧬 What We Learned About Marine Life</h4>
                  <div className="space-y-3">
                    {data.scientific_interpretation.ecological_insights.map((insight, idx) => (
                      <div key={idx} className="bg-blue-50 border-l-4 border-blue-400 p-3">
                        <p className="text-blue-800 text-sm">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">📊 Can We Use This for Real Monitoring?</h4>
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className={`w-3 h-3 rounded-full mt-1 ${
                        data.scientific_interpretation.monitoring_implications.year_round_deployment_viable 
                          ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <div>
                        <p className="font-medium text-gray-900">Year-round Deployment</p>
                        <p className="text-sm text-gray-600">
                          {data.scientific_interpretation.monitoring_implications.year_round_deployment_viable 
                            ? 'Yes - the system works reasonably well across all seasons' 
                            : 'Not yet - performance too inconsistent across seasons'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-3">
                      <div className={`w-3 h-3 rounded-full mt-1 ${
                        data.scientific_interpretation.monitoring_implications.seasonal_calibration_needed 
                          ? 'bg-yellow-500' : 'bg-green-500'
                      }`}></div>
                      <div>
                        <p className="font-medium text-gray-900">Seasonal Calibration</p>
                        <p className="text-sm text-gray-600">
                          {data.scientific_interpretation.monitoring_implications.seasonal_calibration_needed 
                            ? 'Yes - we need to adjust for seasonal differences to get best results' 
                            : 'No - the system works consistently year-round'}
                        </p>
                      </div>
                    </div>

                    <div>
                      <p className="font-medium text-gray-900 mb-2">Most Important Sound Features</p>
                      <div className="flex flex-wrap gap-2">
                        {data.scientific_interpretation.monitoring_implications.key_acoustic_indicators.map((indicator, idx) => (
                          <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
                            {indicator}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <p className="font-medium text-gray-900">How Accurate Can We Expect It To Be?</p>
                      <p className="text-sm text-gray-600">
                        {data.scientific_interpretation.monitoring_implications.expected_accuracy_range}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-4">🔬 What We Contributed to Science</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  {data.scientific_interpretation.methodological_contributions.map((contribution, idx) => (
                    <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <p className="text-sm text-gray-700">{contribution}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}