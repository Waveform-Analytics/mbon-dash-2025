'use client';

import { motion } from 'framer-motion';
import PageNavigation from '@/components/PageNavigation';

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
        </motion.div>
      </div>
    </div>
  );
}