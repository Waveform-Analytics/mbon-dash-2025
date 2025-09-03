'use client';

import { motion } from 'framer-motion';
import { 
  Calendar, 
  Activity, 
  BarChart3, 
  Info,
  ChevronRight,
  Waves,
  Volume2,
  Users,
  AlertCircle
} from 'lucide-react';
import Link from 'next/link';
import AcousticIndicesSmallMultiples from '@/components/charts/AcousticIndicesSmallMultiples';
import AcousticDetectionHeatmap from '@/components/charts/AcousticDetectionHeatmap';
import AcousticIndicesHeatmap from '@/components/charts/AcousticIndicesHeatmap';
import { useAcousticDistributions } from '@/lib/data/useAcousticDistributions';
import { useViewData } from '@/lib/data/useViewData';
import { ProjectMetadata } from '@/types/data';
import VisualizationCard from '@/components/ui/VisualizationCard';
import NarrativeSection from '@/components/ui/NarrativeSection';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function AcousticAnalysisPage() {
  const { distributionsData, loading, error } = useAcousticDistributions();
  const { data: projectData } = useViewData<ProjectMetadata>('project_metadata.json');

  return (
    <div className="min-h-screen bg-background">
      {/* Breadcrumb */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-3">
          <nav className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Link href="/data" className="hover:text-foreground transition-colors">
              Data Overview
            </Link>
            <ChevronRight className="h-4 w-4" />
            <span className="text-foreground font-medium">Acoustic Analysis</span>
          </nav>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div 
          className="mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-medium mb-4 text-left">Acoustic Dataset Analysis</h1>
          <p className="text-xl text-muted-foreground max-w-4xl text-left">
            Comprehensive analysis of marine acoustic data combining manual annotations of biological 
            and anthropogenic sounds with computed acoustic indices to understand soundscape patterns
          </p>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mt-6"></div>
        </motion.div>

        {/* Dataset Overview */}
        <NarrativeSection delay={0.2}>
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4 flex items-center gap-2 text-left">
                <Volume2 className="h-6 w-6 text-primary" />
                About the Acoustic Dataset
              </h2>
              <p className="text-lg text-gray-600 leading-relaxed mb-4 text-left">
                Our dataset consists of continuous hydrophone recordings from three monitoring stations 
                in South Carolina estuaries, collected during 2018 and 2021. 
              </p>
              <p className="text-base text-gray-500 text-left">
                The raw audio data has been processed using two complementary approaches to enable 
                comprehensive soundscape analysis.
              </p>
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Users className="h-5 w-5 text-blue-500" />
                    Manual Annotations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    Expert listeners manually identified and annotated specific biological and 
                    anthropogenic sounds in 2-minute audio samples every 2 hours:
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-green-50">Biological</Badge>
                      <span className="text-xs text-gray-600">Fish choruses, dolphin clicks, snapping shrimp</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-orange-50">Anthropogenic</Badge>
                      <span className="text-xs text-gray-600">Boat engines, sonar, construction noise</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Activity className="h-5 w-5 text-purple-500" />
                    Acoustic Indices
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    Approximately 60 computational metrics automatically extracted from the audio to 
                    quantify soundscape characteristics:
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">Complexity (ACI)</Badge>
                    <Badge variant="secondary">Diversity (H-indices)</Badge>
                    <Badge variant="secondary">Energy (RMS)</Badge>
                    <Badge variant="secondary">Frequency (NDSI)</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </NarrativeSection>

        {/* Comparison Section */}
        <NarrativeSection delay={0.3}>
          <Alert className="mb-8">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Why Compare Both Methods?</AlertTitle>
            <AlertDescription className="mt-2">
              Manual annotations provide ground truth for specific species presence, while acoustic indices 
              offer continuous, scalable metrics of overall soundscape complexity. By visualizing both approaches 
              side-by-side, we can identify which indices best predict biological activity and develop more 
              efficient automated monitoring methods.
            </AlertDescription>
          </Alert>
        </NarrativeSection>

        {/* Heatmap Comparisons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2 text-left">
              Temporal Pattern Comparison
            </h2>
            <p className="text-base text-gray-600 text-left">
              Compare manual detection patterns with acoustic index patterns to identify correlations 
              between specific sounds and computational metrics
            </p>
          </div>

          {/* Manual Detections Heatmap */}
          <div className="mb-8">
            <VisualizationCard
              title="Manual Detection Patterns"
              description="Temporal heatmap showing expert-annotated detection patterns across time and hours of day for different species and anthropogenic sounds"
              icon={Calendar}
            > 
              <AcousticDetectionHeatmap className="mt-4" />
            </VisualizationCard>
          </div>

          {/* Acoustic Indices Heatmap */}
          <div>
            <VisualizationCard
              title="Acoustic Indices Patterns (2021)"
              description="Computational metrics showing how acoustic characteristics vary across time and hours of day - compare with manual detections above"
              icon={Activity}
            >
              <AcousticIndicesHeatmap className="mt-4" />
            </VisualizationCard>
          </div>
        </motion.div>

        {/* Index Distributions Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mb-12"
        >
          <NarrativeSection delay={0.6}>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4 text-left">
              Statistical Distribution Analysis
            </h2>
            <p className="text-lg text-gray-600 leading-relaxed mb-4 text-left">
              The distribution patterns of acoustic indices can reveal underlying soundscape characteristics. 
              Bimodal distributions may indicate distinct day/night patterns, while skewed distributions 
              can highlight episodic events like boat passages or feeding aggregations.
            </p>
            <p className="text-base text-gray-500 text-left">
              Compare distributions across stations to identify site-specific acoustic signatures and 
              environmental influences on soundscape composition.
            </p>
          </NarrativeSection>

          <VisualizationCard
            title="Acoustic Index Distributions by Station"
            description="Kernel density estimates showing the probability distributions of key acoustic indices across monitoring stations"
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

        {/* Key Insights */}
        <NarrativeSection delay={0.7}>
          <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5 text-blue-600" />
                Key Research Questions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">•</span>
                  <span>
                    <strong>Predictive Power:</strong> Which acoustic indices best predict the presence 
                    of specific biological sounds identified through manual annotation?
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">•</span>
                  <span>
                    <strong>Temporal Patterns:</strong> Do computational metrics capture the same diel 
                    and seasonal patterns observed in manual detections?
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">•</span>
                  <span>
                    <strong>Spatial Variation:</strong> How do acoustic signatures differ between shallow 
                    (9M), intermediate (14M), and deep (37M) monitoring stations?
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-1">•</span>
                  <span>
                    <strong>Efficiency:</strong> Can we develop automated monitoring protocols using 
                    acoustic indices as proxies for labor-intensive manual annotation?
                  </span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </NarrativeSection>

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-12 pt-8 border-t"
        >
          <div className="flex justify-between items-center">
            <Link 
              href="/data" 
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2"
            >
              <ChevronRight className="h-4 w-4 rotate-180" />
              Back to Data Overview
            </Link>
            <Link 
              href="/indices" 
              className="text-primary hover:text-primary/80 transition-colors flex items-center gap-2"
            >
              View Indices Reference
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}