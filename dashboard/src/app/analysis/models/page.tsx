'use client'

import { Suspense } from 'react'
import { motion } from 'framer-motion'
import ModelingAnalysis from '@/components/analysis/ModelingAnalysis'

export default function ModelsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Predictive Models
          </h1>
          <p className="text-lg text-muted-foreground max-w-3xl">
            We're testing whether acoustic recordings can reliably predict fish presence. Using machine 
            learning models trained on our acoustic data, we want to determine if underwater sound patterns 
            contain enough information to serve as a biodiversity monitoring tool.
          </p>
        </motion.div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Suspense fallback={
            <div className="flex items-center justify-center py-16">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-4 text-lg text-muted-foreground">Loading modeling analysis...</span>
            </div>
          }>
            <ModelingAnalysis />
          </Suspense>
        </motion.div>
      </div>
    </div>
  )
}