'use client';

import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as d3 from 'd3';
import { useViewData } from '@/lib/data';
import BaseHeatmap, { ProcessedDataPoint } from './heatmaps/BaseHeatmap';
import { MIDNIGHT_CENTERED_Y_AXIS } from './heatmaps/configs/axisConfigs';

interface TimelineEntry {
  datetime: string;
  day_of_year: number;
  hour: number;
  month: number;
  station: string;
  actual_community_activity: {
    total_fish_activity: number;
    num_active_species: number;
    max_species_activity: number;
  };
  environmental_context: {
    water_temp: number | null;
    water_depth: number | null;
  };
  activity_flags: {
    any_activity: boolean;
    high_activity_75th: boolean;
    high_activity_90th: boolean;
    multi_species_active: boolean;
  };
  model_probabilities: Record<string, {
    probability: number;
    model_name: string;
  }>;
}

interface ThresholdScenario {
  target_type: string;
  model_name: string;
  threshold: number;
  estimated_metrics: {
    precision: number;
    recall: number;
    effort_reduction: number;
    detection_rate: number;
    f1_score: number;
  };
}

interface ModelComparison {
  target_type: string;
  model_name: string;
  performance_metrics: {
    f1_score: number;
    precision: number;
    recall: number;
    accuracy: number;
    cv_f1_mean: number;
    cv_f1_std: number;
  };
}

interface FeatureImportance {
  target_type: string;
  feature_name: string;
  mutual_info_score: number;
  rf_importance: number;
  rank: number;
}

interface SummaryStats {
  dataset_overview: {
    total_samples: number;
    date_range: {
      start: string;
      end: string;
    };
    stations: string[];
    activity_rates: {
      any_activity: number;
      high_activity_75th: number;
      high_activity_90th: number;
      multi_species_active: number;
    };
  };
  best_models: Record<string, {
    model_name: string;
    f1_score: number;
    precision: number;
    recall: number;
  }>;
}

interface CommunityScreeningData {
  timeline_data: TimelineEntry[];
  threshold_scenarios: ThresholdScenario[];
  model_comparison: ModelComparison[];
  feature_importance: FeatureImportance[];
  summary_statistics: SummaryStats;
  metadata: {
    generated_at: string;
    data_source: string;
    sample_size: number;
    total_available: number;
    targets: string[];
    models: string[];
  };
}

const CommunityScreeningDashboard: React.FC = () => {
  const { data, loading, error } = useViewData<CommunityScreeningData>('community_screening_dashboard');
  const [selectedTarget, setSelectedTarget] = useState<string>('any_activity');
  const [selectedThreshold, setSelectedThreshold] = useState<number>(0.5);
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [timelineView, setTimelineView] = useState<'activity' | 'predictions' | 'accuracy'>('activity');
  
  const metricsRef = useRef<SVGSVGElement>(null);
  const modelsRef = useRef<SVGSVGElement>(null);
  const featuresRef = useRef<SVGSVGElement>(null);

  // Filter data based on selections
  const filteredData = useMemo(() => {
    if (!data) return null;
    
    let timelineData = data.timeline_data;
    if (selectedStation !== 'all') {
      timelineData = timelineData.filter(d => d.station === selectedStation);
    }
    
    return {
      ...data,
      timeline_data: timelineData
    };
  }, [data, selectedStation]);

  // Current scenario metrics
  const currentScenario = useMemo(() => {
    if (!data) return null;
    return data.threshold_scenarios.find(
      s => s.target_type === selectedTarget && Math.abs(s.threshold - selectedThreshold) < 0.01
    );
  }, [data, selectedTarget, selectedThreshold]);

  // Transform timeline data for heatmap component
  const timelineHeatmapData = useMemo(() => {
    if (!filteredData) return [];
    
    return filteredData.timeline_data.map(d => {
      let value: number;
      
      if (timelineView === 'activity') {
        // View 1: Actual activity intensity
        const isActive = d.activity_flags[selectedTarget as keyof typeof d.activity_flags];
        value = isActive ? d.actual_community_activity.total_fish_activity : 0;
      } else if (timelineView === 'predictions') {
        // View 2: Model predictions (binary: 0 or 1)
        const probability = d.model_probabilities[selectedTarget]?.probability || 0;
        value = probability >= selectedThreshold ? 1 : 0;
      } else {
        // View 3: Prediction accuracy (categorical: 0-3)
        const probability = d.model_probabilities[selectedTarget]?.probability || 0;
        const isPredictedActive = probability >= selectedThreshold;
        const isActuallyActive = d.activity_flags[selectedTarget as keyof typeof d.activity_flags];
        
        if (isPredictedActive && isActuallyActive) {
          value = 3; // True positive (correct prediction)
        } else if (isPredictedActive && !isActuallyActive) {
          value = 1; // False positive (false alarm)
        } else if (!isPredictedActive && isActuallyActive) {
          value = 2; // False negative (missed opportunity)
        } else {
          value = 0; // True negative (correctly identified as inactive)
        }
      }
      
      return {
        day: d.day_of_year,
        hour: d.hour,
        value: value,
        date: new Date(d.datetime),
        originalData: d // Store original data for tooltips
      } as ProcessedDataPoint & { originalData: TimelineEntry };
    });
  }, [filteredData, selectedTarget, timelineView, selectedThreshold]);
  
  // Create color schemes for different views
  const getColorConfig = useMemo(() => {
    if (timelineView === 'activity') {
      // Activity view: sequential scale from low to high
      const maxActivity = Math.max(...timelineHeatmapData.map(d => d.value), 1);
      return {
        colorScheme: 'rdylbu' as const,
        reverseColorScale: true,
        colorDomain: [0, maxActivity] as [number, number],
        legendLabel: 'Fish Activity Level'
      };
    } else if (timelineView === 'predictions') {
      // Predictions view: binary (flagged vs not flagged)
      return {
        colorScale: (value: number) => value >= 1 ? '#2563eb' : '#e5e7eb', // Blue for flagged, light gray for not flagged
        colorDomain: [0, 1] as [number, number],
        legendLabel: 'Model Decision'
      };
    } else {
      // Accuracy view: categorical colors
      return {
        colorScale: (value: number) => {
          if (value === 3) return '#22c55e'; // Green: True positive
          if (value === 1) return '#ef4444'; // Red: False positive
          if (value === 2) return '#f59e0b'; // Orange: False negative
          return '#6b7280'; // Gray: True negative
        },
        colorDomain: [0, 3] as [number, number],
        legendLabel: 'Prediction Accuracy'
      };
    }
  }, [timelineView, timelineHeatmapData]);
  
  // Custom tooltip formatter
  const formatTooltip = useMemo(() => {
    return (d: ProcessedDataPoint & { originalData?: TimelineEntry }) => {
      const original = d.originalData;
      if (!original) return `Date: ${d.date.toLocaleDateString()}<br/>Hour: ${d.hour}:00<br/>Value: ${d.value}`;
      
      const baseInfo = `<strong>Date:</strong> ${new Date(original.datetime).toLocaleDateString()}<br/>
                        <strong>Hour:</strong> ${original.hour}:00<br/>
                        <strong>Station:</strong> ${original.station}`;
      
      if (timelineView === 'activity') {
        return `${baseInfo}<br/>
                <strong>Total Fish Activity:</strong> ${original.actual_community_activity.total_fish_activity}<br/>
                <strong>Active Species:</strong> ${original.actual_community_activity.num_active_species}<br/>
                <strong>Water Temp:</strong> ${original.environmental_context.water_temp?.toFixed(1) || 'N/A'}°C`;
      } else if (timelineView === 'predictions') {
        const probability = original.model_probabilities[selectedTarget]?.probability || 0;
        const isPredictedActive = probability >= selectedThreshold;
        return `${baseInfo}<br/>
                <strong>Model Probability:</strong> ${(probability * 100).toFixed(1)}%<br/>
                <strong>Model Decision:</strong> ${isPredictedActive ? 'Flag for review' : 'Skip'}<br/>
                <strong>Threshold:</strong> ${(selectedThreshold * 100).toFixed(0)}%`;
      } else {
        const probability = original.model_probabilities[selectedTarget]?.probability || 0;
        const isPredictedActive = probability >= selectedThreshold;
        const isActuallyActive = original.activity_flags[selectedTarget as keyof typeof original.activity_flags];
        
        let resultType = '';
        if (isPredictedActive && isActuallyActive) resultType = 'Correct: True Positive';
        else if (isPredictedActive && !isActuallyActive) resultType = 'False Alarm';
        else if (!isPredictedActive && isActuallyActive) resultType = 'Missed Opportunity';
        else resultType = 'Correct: True Negative';
        
        return `${baseInfo}<br/>
                <strong>Result:</strong> ${resultType}<br/>
                <strong>Model Probability:</strong> ${(probability * 100).toFixed(1)}%<br/>
                <strong>Actually Active:</strong> ${isActuallyActive ? 'Yes' : 'No'}`;
      }
    };
  }, [timelineView, selectedTarget, selectedThreshold]);

  useEffect(() => {
    if (!data || !metricsRef.current) return;
    drawMetricsChart();
  }, [data, selectedTarget, selectedThreshold]);

  useEffect(() => {
    if (!data || !modelsRef.current) return;
    drawModelsComparison();
  }, [data, selectedTarget]);

  useEffect(() => {
    if (!data || !featuresRef.current) return;
    drawFeatureImportance();
  }, [data, selectedTarget]);


  const drawMetricsChart = () => {
    if (!data || !metricsRef.current) return;

    const svg = d3.select(metricsRef.current);
    svg.selectAll('*').remove();

    const scenarios = data.threshold_scenarios.filter(s => s.target_type === selectedTarget);
    
    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const width = 400 - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleLinear()
      .domain([0, 1])
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, 1])
      .range([height, 0]);

    // Draw lines for each metric
    const metrics = ['precision', 'recall', 'f1_score', 'effort_reduction'];
    const colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'];

    metrics.forEach((metric, i) => {
      const line = d3.line<ThresholdScenario>()
        .x(d => xScale(d.threshold))
        .y(d => yScale(d.estimated_metrics[metric as keyof typeof d.estimated_metrics]))
        .curve(d3.curveMonotoneX);

      g.append('path')
        .datum(scenarios)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', colors[i])
        .attr('stroke-width', 2);

      // Add legend
      g.append('text')
        .attr('x', width - 100)
        .attr('y', 20 + i * 15)
        .attr('fill', colors[i])
        .style('font-size', '12px')
        .text(metric.replace('_', ' '));
    });

    // Add current threshold line
    g.append('line')
      .attr('x1', xScale(selectedThreshold))
      .attr('x2', xScale(selectedThreshold))
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#333')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5');

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .append('text')
      .attr('x', width / 2)
      .attr('y', 35)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('Threshold');

    g.append('g')
      .call(d3.axisLeft(yScale))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -40)
      .attr('x', -height / 2)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('Score');
  };

  const drawModelsComparison = () => {
    if (!data || !modelsRef.current) return;

    const svg = d3.select(modelsRef.current);
    svg.selectAll('*').remove();

    const models = data.model_comparison.filter(m => m.target_type === selectedTarget);
    
    const margin = { top: 20, right: 20, bottom: 60, left: 100 };
    const width = 300 - margin.left - margin.right;
    const height = 200 - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const yScale = d3.scaleBand()
      .domain(models.map(d => d.model_name))
      .range([0, height])
      .padding(0.1);

    const xScale = d3.scaleLinear()
      .domain([0, 1])
      .range([0, width]);

    // Draw bars
    g.selectAll('.model-bar')
      .data(models)
      .enter().append('rect')
      .attr('class', 'model-bar')
      .attr('x', 0)
      .attr('y', d => yScale(d.model_name)!)
      .attr('width', d => xScale(d.performance_metrics.f1_score))
      .attr('height', yScale.bandwidth())
      .attr('fill', '#4ECDC4');

    // Add labels
    g.selectAll('.model-label')
      .data(models)
      .enter().append('text')
      .attr('class', 'model-label')
      .attr('x', d => xScale(d.performance_metrics.f1_score) + 5)
      .attr('y', d => yScale(d.model_name)! + yScale.bandwidth() / 2)
      .attr('dy', '0.35em')
      .style('font-size', '10px')
      .text(d => d.performance_metrics.f1_score.toFixed(3));

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .append('text')
      .attr('x', width / 2)
      .attr('y', 35)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('F1 Score');

    g.append('g')
      .call(d3.axisLeft(yScale));
  };

  const drawFeatureImportance = () => {
    if (!data || !featuresRef.current) return;

    const svg = d3.select(featuresRef.current);
    svg.selectAll('*').remove();

    const features = data.feature_importance
      .filter(f => f.target_type === selectedTarget)
      .sort((a, b) => b.mutual_info_score - a.mutual_info_score)
      .slice(0, 10); // Top 10
    
    const margin = { top: 20, right: 20, bottom: 40, left: 120 };
    const width = 400 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const yScale = d3.scaleBand()
      .domain(features.map(d => d.feature_name))
      .range([0, height])
      .padding(0.1);

    const xScale = d3.scaleLinear()
      .domain([0, d3.max(features, d => d.mutual_info_score) || 1])
      .range([0, width]);

    // Draw bars
    g.selectAll('.feature-bar')
      .data(features)
      .enter().append('rect')
      .attr('class', 'feature-bar')
      .attr('x', 0)
      .attr('y', d => yScale(d.feature_name)!)
      .attr('width', d => xScale(d.mutual_info_score))
      .attr('height', yScale.bandwidth())
      .attr('fill', '#FF6B6B');

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .append('text')
      .attr('x', width / 2)
      .attr('y', 35)
      .attr('fill', 'black')
      .style('text-anchor', 'middle')
      .text('Mutual Information Score');

    g.append('g')
      .call(d3.axisLeft(yScale));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-muted-foreground">Loading community screening dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-red-500">Error loading data: {error instanceof Error ? error.message : String(error)}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="text-muted-foreground">No data available</div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-8">
      {/* Educational Intro */}
      <div className="bg-accent/20 border border-accent rounded-lg p-4">
        <h3 className="font-semibold text-accent-foreground mb-2">Understanding the Screening Concept</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-accent-foreground">
          <div>
            <p>
              <strong>Not identifying species</strong> - just detecting &quot;something biological happening&quot; vs &quot;ocean noise.&quot;
              The machine learning model learns patterns in acoustic properties that indicate when fish are active.
            </p>
          </div>
          <div>
            <p>
              <strong>Trade-off decisions</strong> - Higher sensitivity catches more real activity but also creates more false alarms. 
              Lower sensitivity misses some events but reduces manual review time.
            </p>
          </div>
        </div>
        <div className="mt-3 text-sm text-accent-foreground/80">
          <strong>How to explore:</strong> (1) Start with &quot;Activity View&quot; to see ground truth → (2) Switch to &quot;Model Flags&quot; to see screening → (3) Check &quot;Accuracy&quot; to evaluate performance → (4) Adjust sensitivity and repeat.
        </div>
      </div>
      
      {/* Controls */}
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Dashboard Controls</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">What to look for:</label>
            <select
              value={selectedTarget}
              onChange={(e) => setSelectedTarget(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="any_activity">Any fish activity</option>
              <option value="high_activity_75th">High activity periods</option>
              <option value="high_activity_90th">Very high activity periods</option>
              <option value="multi_species_active">Multiple species events</option>
            </select>
            <div className="text-xs text-muted-foreground mt-1">
              Choose what type of biological activity to screen for
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Detector sensitivity: {selectedThreshold.toFixed(1)}</label>
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.1"
              value={selectedThreshold}
              onChange={(e) => setSelectedThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-muted-foreground mt-1">
              Higher = more sensitive but more false alarms
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Station</label>
            <select
              value={selectedStation}
              onChange={(e) => setSelectedStation(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Stations</option>
              {data.summary_statistics.dataset_overview.stations.map(station => (
                <option key={station} value={station}>{station}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Timeline View</label>
            <div className="flex rounded-lg border overflow-hidden">
              <button
                onClick={() => setTimelineView('activity')}
                className={`px-3 py-2 text-sm font-medium flex-1 ${
                  timelineView === 'activity'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-background hover:bg-accent'
                }`}
              >
                Activity
              </button>
              <button
                onClick={() => setTimelineView('predictions')}
                className={`px-3 py-2 text-sm font-medium flex-1 border-x ${
                  timelineView === 'predictions'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-background hover:bg-accent'
                }`}
              >
                Model Flags
              </button>
              <button
                onClick={() => setTimelineView('accuracy')}
                className={`px-3 py-2 text-sm font-medium flex-1 ${
                  timelineView === 'accuracy'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-background hover:bg-accent'
                }`}
              >
                Accuracy
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      {currentScenario && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card border rounded-lg p-4">
            <div className="text-sm text-muted-foreground">Catches real fish activity</div>
            <div className="text-2xl font-bold text-chart-1">
              {(currentScenario.estimated_metrics.detection_rate * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              of genuine events detected
            </div>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <div className="text-sm text-muted-foreground">When flagged, correct</div>
            <div className="text-2xl font-bold text-chart-2">
              {(currentScenario.estimated_metrics.precision * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              of the time
            </div>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <div className="text-sm text-muted-foreground">Review only</div>
            <div className="text-2xl font-bold text-chart-3">
              {(100 - currentScenario.estimated_metrics.effort_reduction * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              of recordings
            </div>
          </div>
          <div className="bg-card border rounded-lg p-4">
            <div className="text-sm text-muted-foreground">Overall performance</div>
            <div className="text-2xl font-bold text-chart-4">
              {currentScenario.estimated_metrics.f1_score.toFixed(2)}/1.0
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              balance of precision & recall
            </div>
          </div>
        </div>
      )}

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Timeline */}
        <div className="bg-card border rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">
              {timelineView === 'activity' && 'When Fish Were Actually Active'}
              {timelineView === 'predictions' && 'What the Model Would Flag for Review'}
              {timelineView === 'accuracy' && 'How Accurate Were the Model Predictions'}
            </h3>
            <div className="text-sm text-muted-foreground">
              {timelineView === 'activity' && 'Color intensity shows biological activity levels throughout the year'}
              {timelineView === 'predictions' && `Blue periods would be flagged at ${(selectedThreshold * 100).toFixed(0)}% threshold`}
              {timelineView === 'accuracy' && 'Green=correct, Red=false alarm, Orange=missed opportunity, Gray=correct negative'}
            </div>
          </div>
          <div className="w-full">
            <BaseHeatmap
              data={timelineHeatmapData}
              height={350}
              yAxisConfig={MIDNIGHT_CENTERED_Y_AXIS}
              formatTooltip={formatTooltip}
              {...getColorConfig}
            />
          </div>
        </div>

        {/* Threshold Performance */}
        <div className="bg-card border rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Sensitivity vs. Performance Trade-offs</h3>
            <div className="text-sm text-muted-foreground">
              See how different sensitivity levels affect accuracy and workload. Current setting shown as dashed line.
            </div>
          </div>
          <svg ref={metricsRef} width={400} height={200} />
        </div>

        {/* Model Comparison */}
        <div className="bg-card border rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">Which detection method works best</h3>
            <div className="text-sm text-muted-foreground">
              Comparison of different machine learning approaches for screening underwater recordings.
            </div>
          </div>
          <svg ref={modelsRef} width={300} height={200} />
        </div>

        {/* Feature Importance */}
        <div className="bg-card border rounded-lg p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-2">What the model pays attention to</h3>
            <div className="text-sm text-muted-foreground">
              The environmental and temporal patterns that help predict fish activity. Month captures seasonal patterns, temperature drives fish behavior.
            </div>
          </div>
          <div className="w-full overflow-x-auto">
            <svg ref={featuresRef} width={400} height={300} />
          </div>
        </div>
      </div>
      
      {/* Key Insights */}
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Key Results from Real Monitoring Data</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-accent-foreground mb-2">What We Found</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>• <strong>Seasonal patterns work:</strong> The timeline shows clear biological rhythms that machine learning models can learn to recognize across different monitoring stations.</li>
              <li>• <strong>Practical time savings:</strong> At moderate sensitivity, researchers could skip 40-60% of recordings while still catching most real activity.</li>
              <li>• <strong>Environmental cues matter:</strong> Water temperature and seasonal timing are the strongest predictors of fish activity patterns.</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-accent-foreground mb-2">Practical Implications</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>• <strong>Smart sampling:</strong> Focus manual analysis efforts on high-probability periods rather than random sampling.</li>
              <li>• <strong>Quality control:</strong> Flag unusual acoustic patterns that might indicate equipment issues or interesting biological events.</li>
              <li>• <strong>Scalable monitoring:</strong> Enable continuous ecosystem monitoring with limited human resources.</li>
            </ul>
          </div>
        </div>
        <div className="mt-4 p-3 bg-muted rounded-md">
          <p className="text-sm text-muted-foreground">
            <strong>Study limitations:</strong> These results come from three monitoring stations in one marine system. The approach shows promise but needs testing across different environments, fish communities, and operational contexts before widespread implementation.
          </p>
        </div>
      </div>
    </div>
  );
};

export default CommunityScreeningDashboard;