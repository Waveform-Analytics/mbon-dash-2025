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
  const [activeTab, setActiveTab] = useState<'overview' | 'models' | 'results' | 'interpretation'>('overview')
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
    { id: 'models', label: 'Models', icon: '🤖' },
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
                onClick={() => setActiveTab(tab.id as 'overview' | 'models' | 'results' | 'interpretation')}
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
                  The Question
                </h3>
                <p className="text-gray-700 mb-6">
                  Marine biodiversity monitoring typically requires extensive manual effort to identify 
                  species from recordings. We're investigating whether machine learning models can 
                  automatically detect fish presence using acoustic features extracted from underwater recordings.
                </p>
                
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                  <p className="text-blue-800">
                    <strong>Core hypothesis:</strong> Acoustic indices derived from underwater sound recordings 
                    contain sufficient information to predict fish presence with reasonable accuracy.
                  </p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Our Dataset</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• <strong>{data.dataset_summary.total_records.toLocaleString()}</strong> hourly recordings</li>
                      <li>• <strong>{data.dataset_summary.stations.join(', ')}</strong> monitoring stations</li>
                      <li>• <strong>{data.dataset_summary.temporal_coverage}</strong></li>
                      <li>• <strong>5 acoustic features</strong> (PCA-reduced from 56 original indices)</li>
                      <li>• <strong>Binary target:</strong> Fish present or absent</li>
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Key Challenge</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• Fish activity varies seasonally (spawning cycles, migration)</li>
                      <li>• Peak activity: <strong className="text-green-600">{data.temporal_patterns.seasonal_insights.peak_activity_month}</strong></li>
                      <li>• Lowest activity: <strong className="text-red-600">{data.temporal_patterns.seasonal_insights.lowest_activity_month}</strong></li>
                      <li>• <strong>{(data.temporal_patterns.seasonal_insights.seasonal_variation_coefficient * 100).toFixed(0)}%</strong> seasonal variation in activity</li>
                      <li>• Models must account for this temporal structure</li>
                    </ul>
                  </div>
                </div>
              </div>

              <SeasonalActivityChart data={data.temporal_patterns.monthly_patterns} />
            </div>
          )}

          {activeTab === 'models' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Two Approaches to Fish Detection
                </h3>
                <p className="text-gray-700 mb-6">
                  We tested two different machine learning algorithms to predict fish presence from our 
                  5 acoustic features. Each algorithm has different strengths and works in a different way.
                </p>

                <div className="grid md:grid-cols-2 gap-8">
                  <div className="bg-blue-50 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">🌳 Random Forest</h4>
                    <p className="text-sm text-gray-700 mb-4">
                      Think of this as asking a panel of experts (decision trees) and taking a vote. 
                      Each expert looks at different combinations of our acoustic features and makes a prediction.
                    </p>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <span><strong>Strengths:</strong> Good at finding complex patterns, handles interactions between features well</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <span><strong>Weaknesses:</strong> Harder to interpret exactly why it made a decision</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        <span><strong>How it works:</strong> Creates many decision trees, each trained on different parts of the data, then averages their predictions</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-green-50 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">📊 Logistic Regression</h4>
                    <p className="text-sm text-gray-700 mb-4">
                      Creates a mathematical scoring system where each acoustic feature gets a weight, 
                      and you add them up to get a final prediction.
                    </p>
                    <div className="space-y-2 text-sm text-gray-600">
                      <div className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <span><strong>Strengths:</strong> Simple, interpretable, fast to train and predict</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <span><strong>Weaknesses:</strong> Assumes linear relationships, might miss complex patterns</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                        <span><strong>How it works:</strong> Learns optimal weights for each feature to maximize prediction accuracy</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-8">
                  <h4 className="font-semibold text-gray-900 mb-4">Why These Two Models?</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-700">
                      We wanted to compare a complex method (Random Forest) with a simpler, more traditional approach 
                      (Logistic Regression). This helps us understand whether the complexity is worth it for our task, 
                      and both methods can tell us which acoustic features are most important for detecting fish.
                    </p>
                  </div>
                </div>

                <div className="mt-8">
                  <h4 className="font-semibold text-gray-900 mb-4">Training Strategy</h4>
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <p className="text-sm text-gray-700 mb-3">
                      <strong>Key consideration:</strong> Fish activity varies dramatically by season, so we can't just randomly 
                      split our data for training and testing.
                    </p>
                    <p className="text-sm text-gray-700">
                      Instead, we sampled proportionally from each month to ensure both training and testing datasets 
                      contain the full seasonal cycle. This gives us realistic performance estimates for year-round deployment.
                    </p>
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
                  What We Found: Performance Results
                </h3>
                <p className="text-gray-700 mb-6">
                  Random Forest slightly outperformed Logistic Regression, achieving about 62% accuracy at detecting 
                  fish presence. While not perfect, this is significantly better than random guessing (50%) and shows 
                  that acoustic features do contain predictive information about fish activity.
                </p>
                
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <h4 className="font-semibold text-gray-900 mb-2">What Does 62% Accuracy Mean?</h4>
                  <p className="text-sm text-gray-700">
                    Out of 100 time periods, our model correctly identifies about 62 as either "fish present" or "fish absent." 
                    In practical terms: <strong>better than guessing, but you'd still want to verify important detections.</strong>
                  </p>
                </div>
              </div>

              <ModelPerformanceChart data={data.model_performance.performance_comparison} />

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Winner: Random Forest</h4>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-green-800">Best Overall Performance</span>
                      <span className="text-2xl font-bold text-green-600">
                        {(data.model_performance.model_insights.best_f1_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm text-green-700">
                      Random Forest achieved the best balance between correctly identifying fish when present 
                      and avoiding false alarms when they're absent.
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-4">Breaking Down the Performance</h4>
                  {data.model_performance.performance_comparison
                    .filter(m => m.target === 'fish_presence' && m.model_type === 'random_forest')
                    .map((model, idx) => (
                      <div key={idx} className="space-y-3 text-sm bg-white border rounded-lg p-4">
                        <div className="flex justify-between items-center">
                          <span>When it says "fish are here"</span>
                          <div className="text-right">
                            <div className="font-medium">{(model.precision * 100).toFixed(0)}% correct</div>
                            <div className="text-xs text-gray-500">precision</div>
                          </div>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>When fish are actually present</span>
                          <div className="text-right">
                            <div className="font-medium">{(model.recall * 100).toFixed(0)}% detected</div>
                            <div className="text-xs text-gray-500">recall</div>
                          </div>
                        </div>
                        <div className="flex justify-between items-center pt-2 border-t">
                          <span>Overall ability to distinguish</span>
                          <div className="text-right">
                            <div className="font-medium">{(model.roc_auc * 100).toFixed(0)}% better than random</div>
                            <div className="text-xs text-gray-500">ROC-AUC</div>
                          </div>
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
                  Practical Implications
                </h3>
                <p className="text-gray-700 mb-6">
                  Our results demonstrate that acoustic monitoring shows promise for marine biodiversity tracking, 
                  achieving meaningful predictive accuracy. However, real-world deployment requires understanding 
                  both the capabilities and limitations of this approach.
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