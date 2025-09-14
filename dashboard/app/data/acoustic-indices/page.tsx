'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import AcousticIndicesCards from '@/components/AcousticIndicesCards';

export default function AcousticIndicesPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-4xl font-bold text-primary">Acoustic Indices Explorer</h1>
            <nav className="flex items-center space-x-4">
              <Link href="/data" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary transition-colors">
                Overview
              </Link>
              <Link href="/data/acoustic-indices" className="px-4 py-2 text-sm font-medium text-primary border-b-2 border-primary">
                Acoustic Indices Explorer
              </Link>
            </nav>
          </div>
          <div className="h-1 w-20 bg-primary rounded mb-4"></div>
          <p className="mt-2 text-muted-foreground">
            Explore the distribution patterns of acoustic indices across monitoring stations.
            Click on any card to view detailed descriptions.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <AcousticIndicesCards />
        </motion.div>
      </div>
    </div>
  );
}