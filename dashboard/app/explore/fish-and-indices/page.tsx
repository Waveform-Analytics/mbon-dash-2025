'use client';

import { motion } from 'framer-motion';
import { Fish } from 'lucide-react';
import PageNavigation from '@/components/PageNavigation';
import DielPatternConcordance from '@/components/DielPatternConcordance';

const exploreLinks = [
  { href: '/explore', label: 'Overview' },
  { href: '/explore/index-reduction', label: 'Index Reduction' },
  { href: '/explore/fish-and-indices', label: 'Fish and Indices' },
];

export default function FishAndIndicesPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-4xl font-bold text-primary">Fish and Indices</h1>
            <PageNavigation links={exploreLinks} />
          </div>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">Diel Pattern Concordance</h2>
            <p className="text-gray-600 mb-6">
              This visualization compares diel (24-hour) activity patterns between acoustic indices and manual fish detections.
              By examining these patterns across seasons, we can assess whether acoustic indices capture the same biological rhythms
              as manual detection methods, validating their use as proxies for fish activity monitoring.
            </p>
            <div className="bg-white rounded-lg shadow-lg p-6">
              <DielPatternConcordance />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}