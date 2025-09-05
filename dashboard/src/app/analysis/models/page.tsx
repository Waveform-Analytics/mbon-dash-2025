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
            Can underwater sound patterns tell us about fish activity? We're testing machine learning 
            models to see if acoustic recordings can predict when fish are present. Since marine life 
            follows seasonal patterns (think spawning seasons), we had to be smart about how we train 
            and test our models to get realistic results.
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