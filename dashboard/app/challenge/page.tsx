'use client';

import { motion } from 'framer-motion';
import { Waves, Users, Target, Clock, ArrowRight, Headphones, Fish, BarChart3 } from 'lucide-react';
import Link from 'next/link';

export default function ChallengePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">The Challenge</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
          <p className="text-xl text-muted-foreground max-w-3xl">
            Marine ecosystems are changing rapidly, but monitoring them at the scales needed for effective management remains incredibly challenging.
          </p>
        </motion.div>

        {/* The ESONS Foundation */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-12"
        >
          <div className="bg-accent/20 border border-accent rounded-lg p-8 mb-12">
            <div className="flex items-center mb-6">
              <Waves className="h-8 w-8 text-primary mr-3" />
              <div>
                <h2 className="text-2xl font-bold text-card-foreground">The ESONS Foundation</h2>
                <p className="text-muted-foreground">
                  Building on a decade+ of proven marine acoustic monitoring
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <p className="text-card-foreground mb-4">
                  <strong>Dr. Eric Montie's lab</strong> at USC Beaufort has been monitoring marine soundscapes 
                  across South Carolina estuaries for over a decade through the <strong>Estuarine Soundscape 
                  Observatory Network in the Southeast (ESONS)</strong>.
                </p>
                <p className="text-muted-foreground mb-4">
                  Their proven manual detection protocol has revealed rich patterns of fish calling behavior, 
                  seasonal cycles, and ecosystem health indicators throughout the region.
                </p>
              </div>
              <div className="bg-card/50 rounded-lg p-6">
                <h3 className="font-semibold text-card-foreground mb-3">ESONS Protocol</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 text-chart-1 mr-2" />
                    <span>2-minute recordings every 2 hours</span>
                  </div>
                  <div className="flex items-center">
                    <Headphones className="h-4 w-4 text-chart-2 mr-2" />
                    <span>Expert manual analysis and species identification</span>
                  </div>
                  <div className="flex items-center">
                    <Fish className="h-4 w-4 text-chart-3 mr-2" />
                    <span>0-3 scale calling intensity documentation</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* The Scaling Challenge */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <Target className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">The Scaling Challenge</h2>
              <p className="text-muted-foreground">
                Manual detection works beautifully but is resource-intensive
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-card border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-card-foreground">Current Reality</h3>
              <div className="space-y-4 text-muted-foreground">
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-red-500 mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <strong>Resource Intensive:</strong> Each 2-minute recording requires intensive expert analysis regardless of biological content
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-red-500 mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <strong>Undifferentiated Effort:</strong> Current approach analyzes all recordings equally, even those with minimal biological activity
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-red-500 mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <strong>Scalability Gap:</strong> Expanding to ecosystem-wide monitoring requires exponentially more expert hours
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-card border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-card-foreground">What's Needed</h3>
              <div className="space-y-4 text-muted-foreground">
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <strong>Continuous Monitoring:</strong> Detect patterns across full temporal scales
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <strong>Efficient Screening:</strong> Focus expert time where it's most valuable
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2 mr-3 flex-shrink-0"></div>
                  <div>
                    <strong>Broader Applications:</strong> Enable monitoring across diverse marine environments
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* MBON Context */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mb-12"
        >
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-8">
            <div className="flex items-center mb-6">
              <BarChart3 className="h-8 w-8 text-primary mr-3" />
              <div>
                <h2 className="text-2xl font-bold text-card-foreground">MBON's Vision</h2>
                <p className="text-muted-foreground">
                  Marine Biodiversity Observation Network seeks scalable monitoring approaches
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <p className="text-card-foreground mb-4">
                  The <strong>Marine Biodiversity Observation Network (MBON)</strong> recognizes that effective 
                  marine conservation requires monitoring approaches that can scale across different regions 
                  and research contexts.
                </p>
                <p className="text-muted-foreground">
                  This project uses ESONS data as a high-quality test case to explore whether automated 
                  screening approaches could enable broader-scale marine biodiversity monitoring.
                </p>
              </div>
              <div className="bg-card/50 rounded-lg p-6">
                <h3 className="font-semibold text-card-foreground mb-3">The Vision</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• <strong>Ecosystem-scale monitoring</strong> with limited human resources</li>
                  <li>• <strong>Cross-regional applications</strong> for diverse marine environments</li>
                  <li>• <strong>Management-relevant</strong> information at actionable scales</li>
                  <li>• <strong>Community-level insights</strong> for ecosystem health assessment</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.section>

        {/* The Question */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mb-12"
        >
          <div className="text-center bg-card border rounded-lg p-8">
            <h2 className="text-2xl font-bold text-card-foreground mb-4">
              Can we maintain the quality of expert detection while scaling to broader monitoring efforts?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              This proof-of-concept explores whether <strong>acoustic indices</strong>—automated measurements 
              of underwater sound characteristics—can serve as screening tools to identify periods likely 
              to contain fish community activity.
            </p>
            <Link 
              href="/approach"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
            >
              Discover Our Approach
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </motion.section>

      </div>
    </div>
  );
}
