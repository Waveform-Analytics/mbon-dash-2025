'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, Layers, Zap, Loader2 } from 'lucide-react';
import AcousticIndicesSmallMultiples from '@/components/charts/AcousticIndicesSmallMultiples';
import { useAcousticDistributions } from '@/lib/data/useAcousticDistributions';

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

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>Acoustic Indices Distributions</CardTitle>
                  <CardDescription>
                    Probability density distributions of acoustic indices across monitoring stations
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading && (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading acoustic data...</span>
                </div>
              )}
              
              {error && (
                <div className="text-center py-12">
                  <div className="text-red-600 mb-2">Error loading data</div>
                  <div className="text-sm text-muted-foreground">{error.message}</div>
                </div>
              )}
              
              {distributionsData && (
                <AcousticIndicesSmallMultiples 
                  data={distributionsData}
                  className="mt-4"
                />
              )}
              
              {!loading && !error && !distributionsData && (
                <div className="text-center py-12 text-muted-foreground">
                  No acoustic indices data available
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
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