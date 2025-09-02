'use client';

import { motion } from 'framer-motion';
import { BarChart3, Calendar, Activity, Waves } from 'lucide-react';
import AcousticIndicesSmallMultiples from '@/components/charts/AcousticIndicesSmallMultiples';
import AcousticDetectionHeatmap from '@/components/charts/AcousticDetectionHeatmap';
import AcousticIndicesHeatmap from '@/components/charts/AcousticIndicesHeatmap';
import { useAcousticDistributions } from '@/lib/data/useAcousticDistributions';
import { useViewData } from '@/lib/data/useViewData';
import { ProjectMetadata } from '@/types/data';
import VisualizationCard from '@/components/ui/VisualizationCard';
import NarrativeSection from '@/components/ui/NarrativeSection';

export default function ExplorePage() {
  const { distributionsData, loading, error } = useAcousticDistributions();
  const { data: projectData } = useViewData<ProjectMetadata>('project_metadata.json');

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div 
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-medium mb-4">Data Explorer</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Interactive visualizations and acoustic indices reference for exploring marine acoustic data and biodiversity patterns
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mx-auto mt-6"></div>
        </motion.div>

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

        {/* Analysis Section 2: Acoustic Indices Heatmap */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
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

        {/* Analysis Section 3: Acoustic Indices Distributions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
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

        {/* Narrative Section: Interpreting the Visualizations */}

      </div>

      {/* Footer */}
      <footer className="bg-muted/50 mt-20 border-t">
        <div className="container mx-auto px-4 py-12">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.2 }}
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <Waves className="h-5 w-5 text-primary" />
              <p className="font-medium">{projectData?.project.organization}</p>
            </div>
            <p className="text-muted-foreground text-sm">
              Data generated: {new Date(projectData?.metadata.generated_at || '').toLocaleDateString()}
            </p>
          </motion.div>
        </div>
      </footer>
    </div>
  );
}