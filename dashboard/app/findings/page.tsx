'use client';

import { motion } from 'framer-motion';
import { CheckCircle2, TrendingUp, Users, Target, ArrowRight, BarChart3, Activity, Fish } from 'lucide-react';
import Link from 'next/link';
import CommunityScreeningDashboard from '../../components/CommunityScreeningDashboard';

export default function FindingsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">Key Findings</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
          <p className="text-xl text-muted-foreground max-w-3xl">
            Our proof-of-concept demonstrates that acoustic indices can effectively serve as community-level screening tools for marine biodiversity monitoring.
          </p>
        </motion.div>

        {/* The Big Result */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-12"
        >
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-8 mb-12">
            <div className="text-center mb-8">
              <motion.div 
                className="inline-flex items-center justify-center w-20 h-20 bg-primary/10 rounded-full mb-6"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
              >
                <CheckCircle2 className="h-10 w-10 text-primary" />
              </motion.div>
              <h2 className="text-3xl font-bold text-card-foreground mb-4">
                Acoustic indices can catch 85% of fish community activity while potentially reducing analysis effort by 40-60%
              </h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                This validation against expert manual detections shows acoustic indices can serve as effective 
                community-level screening tools, focusing expert time where it&apos;s most valuable.
              </p>
            </div>
            
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <motion.div 
                className="bg-card/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border text-center"
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <TrendingUp className="h-8 w-8 text-chart-1 mx-auto mb-3" />
                <div className="text-3xl font-bold text-primary mb-2">85%</div>
                <div className="text-sm text-muted-foreground">Community activity detected</div>
              </motion.div>

              <motion.div 
                className="bg-card/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border text-center"
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <Activity className="h-8 w-8 text-chart-2 mx-auto mb-3" />
                <div className="text-3xl font-bold text-primary mb-2">40-60%</div>
                <div className="text-sm text-muted-foreground">Potential reduction in analysis effort</div>
              </motion.div>

              <motion.div 
                className="bg-card/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border text-center"
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <Fish className="h-8 w-8 text-chart-3 mx-auto mb-3" />
                <div className="text-3xl font-bold text-primary mb-2">Community</div>
                <div className="text-sm text-muted-foreground">Level detection (not species-specific)</div>
              </motion.div>
            </div>
          </div>
        </motion.section>

        {/* Interactive Results Dashboard */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="flex items-center mb-8">
            <BarChart3 className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">Interactive Results: Community Screening Validation</h2>
              <p className="text-muted-foreground">
                Explore how different screening strategies perform against expert-detected community activity patterns
              </p>
            </div>
          </div>
          
          {/* Community Screening Dashboard */}
          <div className="bg-card/30 border rounded-lg p-6">
            <CommunityScreeningDashboard />
          </div>
        </motion.section>

        {/* What This Means */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-primary mb-8">What This Means</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* For Research */}
            <div className="bg-card border rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Target className="h-6 w-6 text-chart-1 mr-3" />
                <h3 className="text-lg font-semibold text-card-foreground">For Marine Researchers</h3>
              </div>
              <div className="space-y-3 text-muted-foreground">
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-chart-1 mt-2 mr-3 flex-shrink-0"></div>
                  <div><strong>Smarter Analysis:</strong> Focus expert listening time on periods most likely to contain biological activity</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-chart-1 mt-2 mr-3 flex-shrink-0"></div>
                  <div><strong>Continuous Insights:</strong> Monitor community-level patterns across full temporal scales</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-chart-1 mt-2 mr-3 flex-shrink-0"></div>
                  <div><strong>Quality Control:</strong> Maintain detection accuracy while improving efficiency</div>
                </div>
              </div>
            </div>

            {/* For Managers */}
            <div className="bg-card border rounded-lg p-6">
              <div className="flex items-center mb-4">
                <Users className="h-6 w-6 text-chart-2 mr-3" />
                <h3 className="text-lg font-semibold text-card-foreground">For Marine Managers</h3>
              </div>
              <div className="space-y-3 text-muted-foreground">
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-chart-2 mt-2 mr-3 flex-shrink-0"></div>
                  <div><strong>Scalable Monitoring:</strong> Enable ecosystem health assessment across broader spatial and temporal scales</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-chart-2 mt-2 mr-3 flex-shrink-0"></div>
                  <div><strong>Early Detection:</strong> Identify changes in marine communities before they become critical</div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-chart-2 mt-2 mr-3 flex-shrink-0"></div>
                  <div><strong>Resource Efficiency:</strong> Maximize monitoring impact within budget constraints</div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Study Limitations & Next Steps */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mb-12"
        >
          <div className="bg-accent/20 border border-accent rounded-lg p-8">
            <h2 className="text-2xl font-bold text-card-foreground mb-6">Study Context & Future Directions</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-card-foreground mb-3">Current Study Scope</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• <strong>Geographic:</strong> Three stations in May River, South Carolina</li>
                  <li>• <strong>Temporal:</strong> One year (2021) of ESONS data</li>
                  <li>• <strong>Detection Level:</strong> Community activity, not species-specific</li>
                  <li>• <strong>Validation:</strong> Against established manual detection protocols</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-card-foreground mb-3">Expanding the Approach</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• <strong>Multi-year validation</strong> across different environmental conditions</li>
                  <li>• <strong>Cross-regional testing</strong> in diverse marine ecosystems</li>
                  <li>• <strong>Integration with management</strong> frameworks and decision-making</li>
                  <li>• <strong>Real-time implementation</strong> for operational monitoring programs</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">
                <strong>Important note:</strong> These results represent a proof-of-concept using high-quality ESONS data 
                from a single marine system. The approach shows promise but requires broader validation before 
                widespread implementation across different environments and operational contexts.
              </p>
            </div>
          </div>
        </motion.section>

        {/* Call to Action */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="mb-12"
        >
          <div className="text-center bg-card border rounded-lg p-8">
            <h2 className="text-2xl font-bold text-card-foreground mb-4">
              Interested in the Technical Details?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Explore our computational notebooks, methodology, and reproducible analysis workflows 
              that generated these results.
            </p>
            <Link 
              href="/analysis"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
            >
              Dive into the Analysis
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </motion.section>

      </div>
    </div>
  );
}
