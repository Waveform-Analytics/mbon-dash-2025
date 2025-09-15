'use client';

import { motion } from 'framer-motion';
import { BarChart3 } from 'lucide-react';
import PageNavigation from '@/components/PageNavigation';

const exploreLinks = [
  { href: '/explore', label: 'Overview' },
  { href: '/explore/index-reduction', label: 'Index Reduction' },
];

export default function ExplorePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-4xl font-bold text-primary">Explore</h1>
            <PageNavigation links={exploreLinks} />
          </div>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex items-center justify-center min-h-[60vh]"
        >
          <div className="bg-card rounded-lg shadow-lg border p-12 text-center max-w-md">
            <BarChart3 className="h-16 w-16 text-muted-foreground mx-auto mb-6" />
            <h2 className="text-2xl font-bold text-card-foreground mb-4">Coming Soon</h2>
            <p className="text-muted-foreground">
              Interactive data exploration and analysis visualizations.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}