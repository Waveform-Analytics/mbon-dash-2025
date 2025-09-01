'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, Calendar, Activity } from 'lucide-react';
import AcousticIndicesSmallMultiples from '@/components/charts/AcousticIndicesSmallMultiples';
import AcousticDetectionHeatmap from '@/components/charts/AcousticDetectionHeatmap';
import AcousticIndicesHeatmap from '@/components/charts/AcousticIndicesHeatmap';
import { useAcousticDistributions } from '@/lib/data/useAcousticDistributions';
import VisualizationCard from '@/components/ui/VisualizationCard';
import NarrativeSection from '@/components/ui/NarrativeSection';

export default function ExplorePage() {
  const { distributionsData, loading, error } = useAcousticDistributions();

  return (
    <div className="min-h-screen bg-background pt-8">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12" style={{ opacity: 0, transform: 'translateY(20px)' }}>
          <h1 className="text-4xl font-medium mb-4">Data Explorer</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Interactive visualizations and acoustic indices reference for exploring marine acoustic data and biodiversity patterns
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mx-auto mt-6"></div>
        </div>

        {/* Narrative Section: Introduction to Analysis */}
        <NarrativeSection delay={0.4}>
          <h2 className="text-2xl font-semibold text-gray-900">
            Understanding Acoustic Patterns
          </h2>
          <p className="text-lg text-gray-600 leading-relaxed">
            Marine soundscapes contain rich information about biodiversity and ecosystem health. 
            Our research analyzes over <strong>60 acoustic indices</strong> computed from hydrophone recordings 
            at three monitoring stations in South Carolina estuaries.
          </p>
          <p className="text-base text-gray-500">
            Each visualization below reveals different aspects of how acoustic complexity, 
            temporal patterns, and frequency distributions vary across our monitoring locations.
          </p>
        </NarrativeSection>

        {/* Analysis Section 1: Acoustic Detection Heatmap */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mb-12"
        >
          <VisualizationCard
            title="Acoustic Detection Patterns"
            description="Temporal heatmap showing detection patterns across time and hours of day for different species and anthropogenic sounds"
            icon={Calendar}
          > 
            <AcousticDetectionHeatmap className="mt-4" />
          </VisualizationCard>
        </motion.div>

        {/* Analysis Section 2: Acoustic Indices Distributions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mb-12"
        >
          <VisualizationCard
            title="Acoustic Indices Distributions"
            description="Probability density distributions of acoustic indices across monitoring stations"
            icon={BarChart3}
            loading={loading}
            error={error}
          >
            {distributionsData && (
              <AcousticIndicesSmallMultiples 
                data={distributionsData}
                className="mt-4"
              />
            )}
          </VisualizationCard>
        </motion.div>

        {/* Analysis Section 3: Acoustic Indices Heatmap */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mb-12"
        >
          <VisualizationCard
            title="Acoustic Indices Temporal Patterns (2021)"
            description="Interactive heatmap showing how acoustic indices vary across time and hours of day for 2021 data"
            icon={Activity}
          >
            <AcousticIndicesHeatmap className="mt-4" />
          </VisualizationCard>
        </motion.div>

        {/* Narrative Section: Interpreting the Visualizations */}
        <NarrativeSection 
          title="Understanding Acoustic Patterns"
          emoji="📊"
          variant="info"
          delay={0.8}
        >
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-800">Distribution Analysis:</h4>
            <div className="space-y-2 ml-3">
              <p>
                • <strong>Station Differences:</strong> Notice how the three colored lines (stations 9M, 14M, 37M) 
                show different distribution shapes for many indices, indicating distinct acoustic environments.
              </p>
              <p>
                • <strong>Index Categories:</strong> Use the category filter to focus on specific types - 
                Complexity Indices reveal soundscape richness, while Diversity Indices relate to species variety.
              </p>
              <p>
                • <strong>Bandwidth Effects:</strong> Switch between FullBW and 8kHz to see how frequency range 
                affects index calculations and station comparisons.
              </p>
            </div>
            
            <h4 className="font-semibold text-gray-800 mt-4">Temporal Pattern Analysis:</h4>
            <div className="space-y-2 ml-3">
              <p>
                • <strong>Daily Rhythms:</strong> The heatmap reveals daily patterns - look for consistent bands 
                of high/low activity at specific hours across multiple days.
              </p>
              <p>
                • <strong>Seasonal Changes:</strong> Notice how index values change across dates, potentially 
                reflecting seasonal shifts in marine activity and soundscapes.
              </p>
              <p>
                • <strong>Index Comparison:</strong> Switch between different acoustic indices to see how 
                various measures of complexity, diversity, and energy show different temporal patterns.
              </p>
              <p>
                • <strong>Interactive Exploration:</strong> Use the dropdowns to explore different stations, 
                years, and bandwidth settings to understand how environmental factors influence acoustic patterns.
              </p>
            </div>
          </div>
        </NarrativeSection>
      </div>
    </div>
  );
}