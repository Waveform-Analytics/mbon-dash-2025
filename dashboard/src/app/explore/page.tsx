'use client';

import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp, Layers, Zap } from 'lucide-react';

export default function ExplorePage() {
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
          <Card className="bg-gradient-to-r from-accent/10 to-accent/5">
            <CardHeader className="text-center">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="p-3 bg-primary/10 rounded-xl">
                  <Zap className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Coming Soon</CardTitle>
                  <CardDescription className="text-base">Advanced visualization features in development</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                <div className="p-4">
                  <Layers className="h-8 w-8 text-primary mx-auto mb-2" />
                  <h4 className="font-medium mb-1">Interactive Charts</h4>
                  <p className="text-sm text-muted-foreground">Dynamic scatter plots, heatmaps, and correlation matrices</p>
                </div>
                <div className="p-4">
                  <TrendingUp className="h-8 w-8 text-primary mx-auto mb-2" />
                  <h4 className="font-medium mb-1">Statistical Analysis</h4>
                  <p className="text-sm text-muted-foreground">PCA analysis, clustering, and predictive modeling tools</p>
                </div>
                <div className="p-4">
                  <BarChart3 className="h-8 w-8 text-primary mx-auto mb-2" />
                  <h4 className="font-medium mb-1">Data Export</h4>
                  <p className="text-sm text-muted-foreground">Download charts as PNG and data as CSV/JSON formats</p>
                </div>
              </div>
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