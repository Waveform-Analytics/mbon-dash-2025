'use client';

// Force dynamic rendering for this page since it fetches data from CDN/API
export const dynamic = 'force-dynamic';

import { motion } from 'framer-motion';
import { BarChart3, Map, Fish, TrendingUp, Activity, Database, Target, ArrowRight, Headphones, Users } from 'lucide-react';
import Link from 'next/link';
import StationsMap from '../../components/StationsMap';
import AcousticIndicesHeatmap from '../../components/heatmaps/AcousticIndicesHeatmap';
import DetectionsHeatmap from '../../components/heatmaps/DetectionsHeatmap';
import RmsSplHeatmap from '../../components/heatmaps/RmsSplHeatmap';
import EnvironmentalHeatmap from '../../components/heatmaps/EnvironmentalHeatmap';

export default function ApproachPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">Our Approach</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
          <p className="text-xl text-muted-foreground max-w-3xl">
            Testing whether acoustic indices can serve as community-level screening tools using ESONS data as our validation framework.
          </p>
        </motion.div>

        {/* Study Design Overview */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-12"
        >
          <div className="bg-accent/20 border border-accent rounded-lg p-8 mb-12">
            <div className="flex items-center mb-6">
              <Target className="h-8 w-8 text-primary mr-3" />
              <div>
                <h2 className="text-2xl font-bold text-card-foreground">Proof-of-Concept Study Design</h2>
                <p className="text-muted-foreground">
                  Using May River ESONS data to validate acoustic indices effectiveness
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-card-foreground mb-3">Traditional ESONS Approach</h3>
                <div className="space-y-3 text-muted-foreground mb-4">
                  <div className="flex items-start">
                    <Headphones className="h-5 w-5 text-chart-1 mr-3 mt-0.5 flex-shrink-0" />
                    <div><strong>Expert listens</strong> to 2-minute sample</div>
                  </div>
                  <div className="flex items-start">
                    <Fish className="h-5 w-5 text-chart-2 mr-3 mt-0.5 flex-shrink-0" />
                    <div><strong>Identifies species</strong> and calling intensity (0-3 scale)</div>
                  </div>
                  <div className="flex items-start">
                    <Users className="h-5 w-5 text-chart-3 mr-3 mt-0.5 flex-shrink-0" />
                    <div><strong>Documents patterns</strong> across time and stations</div>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-semibold text-card-foreground mb-3">Our Acoustic Indices Addition</h3>
                <div className="space-y-3 text-muted-foreground mb-4">
                  <div className="flex items-start">
                    <BarChart3 className="h-5 w-5 text-chart-4 mr-3 mt-0.5 flex-shrink-0" />
                    <div><strong>Computer calculates</strong> 56 sound characteristics</div>
                  </div>
                  <div className="flex items-start">
                    <Activity className="h-5 w-5 text-chart-5 mr-3 mt-0.5 flex-shrink-0" />
                    <div><strong>Identifies patterns</strong> indicating community activity</div>
                  </div>
                  <div className="flex items-start">
                    <Target className="h-5 w-5 text-chart-1 mr-3 mt-0.5 flex-shrink-0" />
                    <div><strong>Flags periods</strong> for expert review</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 p-4 bg-card/50 rounded-lg">
              <p className="text-sm text-muted-foreground">
                <strong>Validation approach:</strong> We use existing expert manual detections as "ground truth" 
                to test whether acoustic indices can identify the same patterns that experienced listeners detect.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Study Scope - Statistics Cards */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-primary mb-6">Study Scope & Data</h2>
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-6 border"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-2">
                <Map className="h-5 w-5 text-chart-1 mr-2" />
                <span className="text-sm text-muted-foreground">STATIONS</span>
              </div>
              <div className="text-3xl font-bold text-card-foreground">3</div>
              <div className="text-sm text-muted-foreground">May River sites</div>
            </motion.div>

            <motion.div 
              className="bg-card rounded-lg shadow-lg p-6 border"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-2">
                <TrendingUp className="h-5 w-5 text-chart-2 mr-2" />
                <span className="text-sm text-muted-foreground">TIME PERIOD</span>
              </div>
              <div className="text-3xl font-bold text-card-foreground">1</div>
              <div className="text-sm text-muted-foreground">Year (2021)</div>
            </motion.div>

            <motion.div 
              className="bg-card rounded-lg shadow-lg p-6 border"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-2">
                <Fish className="h-5 w-5 text-chart-3 mr-2" />
                <span className="text-sm text-muted-foreground">SPECIES</span>
              </div>
              <div className="text-3xl font-bold text-card-foreground">15+</div>
              <div className="text-sm text-muted-foreground">Detected</div>
            </motion.div>

            <motion.div 
              className="bg-card rounded-lg shadow-lg p-6 border"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-2">
                <BarChart3 className="h-5 w-5 text-chart-4 mr-2" />
                <span className="text-sm text-muted-foreground">INDICES</span>
              </div>
              <div className="text-3xl font-bold text-card-foreground">56</div>
              <div className="text-sm text-muted-foreground">Acoustic</div>
            </motion.div>

            <motion.div 
              className="bg-card rounded-lg shadow-lg p-6 border"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-2">
                <Activity className="h-5 w-5 text-chart-5 mr-2" />
                <span className="text-sm text-muted-foreground">ENVIRONMENTAL</span>
              </div>
              <div className="text-3xl font-bold text-card-foreground">2</div>
              <div className="text-sm text-muted-foreground">Temp, Depth</div>
            </motion.div>

            <motion.div 
              className="bg-card rounded-lg shadow-lg p-6 border"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-2">
                <Database className="h-5 w-5 text-chart-1 mr-2" />
                <span className="text-sm text-muted-foreground">SAMPLES</span>
              </div>
              <div className="text-3xl font-bold text-card-foreground">8.7K</div>
              <div className="text-sm text-muted-foreground">2-hour periods</div>
            </motion.div>
          </motion.div>
        </motion.section>

        {/* Monitoring Stations */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <Map className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">Study Area: May River ESONS Stations</h2>
              <p className="text-muted-foreground">
                Three hydrophone monitoring stations (9M, 14M, 37M) providing diverse estuarine habitats for validation
              </p>
            </div>
          </div>
          
          <div className="bg-card rounded-lg shadow-lg border p-6 mb-8">
            <StationsMap className="h-[400px]" />
          </div>

          <div className="bg-accent/10 border border-accent/30 rounded-lg p-6">
            <p className="text-muted-foreground">
              <strong>Why May River?</strong> This system provides an ideal test case with established fish communities, 
              diverse acoustic environments, and high-quality manual detection data from the Montie Lab's ongoing ESONS monitoring.
            </p>
          </div>
        </motion.section>

        {/* Data Visualization Overview */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-primary mb-6">The Data: Expert Detections vs. Acoustic Indices</h2>
          <div className="space-y-8">
            {/* Ground Truth: Manual Detections */}
            <div className="bg-card border shadow-lg rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Fish className="h-6 w-6 text-chart-1 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Ground Truth: Expert Manual Detections</h3>
                  <p className="text-sm text-muted-foreground">
                    ESONS protocol manual analysis showing when and where fish were actually calling
                  </p>
                </div>
              </div>
              <DetectionsHeatmap />
            </div>

            {/* Acoustic Indices */}
            <div className="bg-card border shadow-lg rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Activity className="h-6 w-6 text-chart-2 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Acoustic Indices: Automated Sound Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    56 indices capturing different aspects of underwater soundscape characteristics
                  </p>
                </div>
              </div>
              <AcousticIndicesHeatmap />
            </div>

            {/* Environmental Context */}
            <div className="bg-card border shadow-lg rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Database className="h-6 w-6 text-chart-4 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Environmental Context</h3>
                  <p className="text-sm text-muted-foreground">
                    Temperature and depth patterns that influence fish calling behavior
                  </p>
                </div>
              </div>
              <EnvironmentalHeatmap />
            </div>
          </div>
        </motion.section>

        {/* The Core Question */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="mb-12"
        >
          <div className="text-center bg-primary/5 border border-primary/20 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-card-foreground mb-4">
              Can acoustic indices identify the same biological patterns that expert listeners detect?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Our validation compares acoustic index patterns against expert manual detections to test whether 
              automated approaches can serve as effective community-level screening tools.
            </p>
            <Link 
              href="/findings"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
            >
              See What We Found
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </motion.section>

      </div>
    </div>
  );
}
