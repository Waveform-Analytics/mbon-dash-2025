'use client';

import React from 'react';
import Link from 'next/link';
import AcousticIndicesCards from '@/components/AcousticIndicesCards';

export default function AcousticIndicesPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Acoustic Indices Explorer</h1>
            <nav className="flex items-center space-x-4">
              <Link href="/data" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary transition-colors">
                Overview
              </Link>
              <Link href="/data/acoustic-indices" className="px-4 py-2 text-sm font-medium text-primary border-b-2 border-primary">
                Acoustic Indices Explorer
              </Link>
            </nav>
          </div>
          <p className="mt-2 text-gray-600">
            Explore the distribution patterns of acoustic indices across monitoring stations.
            Click on any card to view detailed descriptions.
          </p>
        </div>

        <AcousticIndicesCards />
      </div>
    </div>
  );
}