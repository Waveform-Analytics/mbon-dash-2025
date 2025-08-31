'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';
import AcousticIndicesSmallMultiples from '@/components/charts/AcousticIndicesSmallMultiples';
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
            Click the info icon (ℹ️) on any chart to learn about the scientific meaning and calculation methods for each index.
          </p>
        </NarrativeSection>

        {/* Analysis Section 1: Acoustic Indices Distributions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
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

        {/* Narrative Section: Interpreting the Distributions */}
        <NarrativeSection 
          title="What do these distributions tell us?"
          emoji="📊"
          variant="info"
          delay={0.6}
        >
          <div className="space-y-2">
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
            <p>
              • <strong>Interactive Details:</strong> Click the info icon (ℹ️) on any chart to flip the card and view 
              detailed descriptions of each acoustic index, including their scientific meaning and calculation methods.
            </p>
          </div>
        </NarrativeSection>
      </div>
    </div>
  );
}