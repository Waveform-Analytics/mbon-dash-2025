'use client';

import { motion } from 'framer-motion';
import { Activity, Target, TrendingUp, Zap } from 'lucide-react';
import PageNavigation from '@/components/PageNavigation';
import CommunityScreeningDashboard from '@/components/CommunityScreeningDashboard';

const exploreLinks = [
  { href: '/explore', label: 'Overview' },
  { href: '/explore/community-screening', label: 'Community Screening' },
  { href: '/explore/index-reduction', label: 'Index Reduction' },
  { href: '/explore/fish-and-indices', label: 'Fish and Indices' },
];

export default function CommunityScreeningPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Standard header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-4xl font-bold text-primary">Community Activity Screening</h1>
            <PageNavigation links={exploreLinks} />
          </div>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>

        {/* Introduction */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-card border shadow-lg rounded-lg p-6">
            <div className="flex items-center mb-4">
              <Activity className="h-6 w-6 text-chart-1 mr-3" />
              <h2 className="text-xl font-semibold">How Machine Learning Can Screen Underwater Recordings</h2>
            </div>
            <p className="text-muted-foreground mb-4">
              This page shows how well machine learning can screen underwater recordings for biological activity. Instead of 
              listening to every recording manually, ML models can detect patterns that suggest "something biological happening" 
              versus just "ocean noise," helping researchers focus their efforts on the most interesting periods.
            </p>
            <div className="bg-accent/30 border border-accent rounded-md p-4 mb-4">
              <h3 className="font-medium text-accent-foreground mb-2">Try the Interactive Demo:</h3>
              <p className="text-sm text-accent-foreground">
                Use the controls below to experiment with different sensitivity settings and see how it affects the trade-offs between catching real fish activity and avoiding false alarms.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-accent p-3 rounded-md">
                <strong className="text-accent-foreground">Activity View:</strong> Shows actual fish activity throughout the year - this is the ground truth we're trying to detect.
              </div>
              <div className="bg-secondary p-3 rounded-md">
                <strong className="text-secondary-foreground">Model Flags View:</strong> Shows what periods the ML model would flag for manual review at your chosen sensitivity level.
              </div>
              <div className="bg-muted p-3 rounded-md">
                <strong className="text-muted-foreground">Accuracy View:</strong> Shows where the model got it right (green) vs. false alarms (red) and missed opportunities (orange).
              </div>
            </div>
          </div>
        </motion.div>

        {/* Key Findings Cards */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Target className="h-5 w-5 text-chart-1 mr-2" />
              <span className="text-sm text-muted-foreground">BEST DETECTION</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">89%</div>
            <div className="text-sm text-muted-foreground">Activity captured</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <TrendingUp className="h-5 w-5 text-chart-2 mr-2" />
              <span className="text-sm text-muted-foreground">PRECISION</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">79%</div>
            <div className="text-sm text-muted-foreground">When flagged</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Zap className="h-5 w-5 text-chart-3 mr-2" />
              <span className="text-sm text-muted-foreground">EFFORT SAVED</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">40%</div>
            <div className="text-sm text-muted-foreground">Manual analysis</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Activity className="h-5 w-5 text-chart-4 mr-2" />
              <span className="text-sm text-muted-foreground">F1 SCORE</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">0.84</div>
            <div className="text-sm text-muted-foreground">Overall performance</div>
          </motion.div>
        </motion.div>

        {/* Main Dashboard */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="bg-card border shadow-lg rounded-lg p-6">
            <CommunityScreeningDashboard />
          </div>
        </motion.section>

        {/* Scientific Context */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-8"
        >
          <div className="bg-card border shadow-lg rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Scientific Context & Applications</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium mb-3">Why Community-Level Screening?</h3>
                <ul className="space-y-2 text-muted-foreground">
                  <li>• Individual species have weak, irregular calling patterns</li>
                  <li>• Aggregating across species amplifies consistent biological signals</li>
                  <li>• Matches practical monitoring needs: "when to listen" vs "exactly which species"</li>
                  <li>• Enables continuous monitoring at ecosystem scales</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium mb-3">Potential Applications</h3>
                <ul className="space-y-2 text-muted-foreground">
                  <li>• <strong>Smart sampling:</strong> Target manual analysis to high-activity periods</li>
                  <li>• <strong>Quality control:</strong> Flag unusual patterns for investigation</li>
                  <li>• <strong>Rapid assessment:</strong> Characterize new monitoring sites quickly</li>
                  <li>• <strong>Long-term monitoring:</strong> Track ecosystem changes over time</li>
                </ul>
              </div>
            </div>
            <div className="mt-6 p-4 bg-accent rounded-md">
              <p className="text-sm text-accent-foreground">
                <strong>Important Note:</strong> These results are from one study system and require validation across 
                different marine environments, fish communities, and operational contexts before broader implementation. 
                The approach shows promise but needs extensive testing for operational deployment.
              </p>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}