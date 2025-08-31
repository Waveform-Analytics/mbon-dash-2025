'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, Layers, Zap } from 'lucide-react';
import AcousticIndicesSmallMultiples from '@/components/charts/AcousticIndicesSmallMultiples';
import { useAcousticDistributions } from '@/lib/data/useAcousticDistributions';
import VisualizationCard from '@/components/ui/VisualizationCard';
import NarrativeSection from '@/components/ui/NarrativeSection';

export default function ExplorePage() {
  const { distributionsData, loading, error } = useAcousticDistributions();

  return (
    <div className="min-h-screen bg-background pt-8">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-medium mb-4">Data Explorer</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Interactive visualizations and analysis tools for exploring marine acoustic data and biodiversity patterns
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mx-auto mt-6"></div>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card className="h-full border-l-4 border-l-primary/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <CardTitle>Acoustic Analysis</CardTitle>
                    <CardDescription>Time series and comparative analysis of acoustic indices</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Explore temporal patterns in acoustic complexity, biodiversity indices, and environmental correlations across monitoring stations.
                </p>
                <div className="text-sm text-muted-foreground">
                  <p>• Time series visualization</p>
                  <p>• Station comparisons</p>
                  <p>• Environmental correlations</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card className="h-full border-l-4 border-l-chart-1/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-chart-1/10 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-chart-1" />
                  </div>
                  <div>
                    <CardTitle>Species Detection</CardTitle>
                    <CardDescription>Marine life detection patterns and biodiversity metrics</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Analyze species detection events, occurrence patterns, and relationships between acoustic indices and biodiversity.
                </p>
                <div className="text-sm text-muted-foreground">
                  <p>• Detection timeline</p>
                  <p>• Species occurrence maps</p>
                  <p>• Diversity calculations</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
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
          </div>
        </NarrativeSection>

        {/* Future Analysis Sections Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Development Roadmap</CardTitle>
              <CardDescription>Planned features for the data exploration interface</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">Phase 1: Data Views</h4>
                    <p className="text-sm text-muted-foreground">Generate optimized view files for acoustic indices and detection data</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-chart-4 rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">Phase 2: Interactive Charts</h4>
                    <p className="text-sm text-muted-foreground">Time series visualizations with brushing and zooming capabilities</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-muted rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <h4 className="font-medium">Phase 3: Advanced Analytics</h4>
                    <p className="text-sm text-muted-foreground">PCA analysis, clustering, and biodiversity correlation tools</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}