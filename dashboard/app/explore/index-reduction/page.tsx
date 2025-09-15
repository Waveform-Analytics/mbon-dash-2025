'use client';

import { motion } from 'framer-motion';
import PageNavigation from '@/components/PageNavigation';
import CorrelationHeatmapSimple from '@/components/CorrelationHeatmapSimple';

const exploreLinks = [
  { href: '/explore', label: 'Overview' },
  { href: '/explore/index-reduction', label: 'Index Reduction' },
];

export default function IndexReductionPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-4xl font-bold text-primary">Index Reduction</h1>
            <PageNavigation links={exploreLinks} />
          </div>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Acoustic Index Correlation Matrix</h2>
            <p className="text-gray-600 mb-6">
              This visualization shows how the 61 acoustic indices correlate with each other, grouped by clusters.
              Indices are ordered by cluster membership, with representative indices highlighted in red.
              The colored dendrograms show the hierarchical clustering structure, with each cluster represented by a different color.
            </p>
            <div className="bg-white rounded-lg shadow-lg p-4">
              <CorrelationHeatmapSimple />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}