'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Target, FlaskConical } from 'lucide-react';
import Link from 'next/link';

export default function NotebookPage() {

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="container mx-auto px-4 py-4 flex-shrink-0">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-4"
        >
          <Link 
            href="/analysis" 
            className="inline-flex items-center text-primary hover:text-primary/80 transition-colors mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analysis
          </Link>
          <div className="mb-4">
            <h1 className="text-3xl font-bold text-primary mb-2">Data Prep</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <motion.div
                className="bg-card rounded-lg border p-3"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <div className="flex items-center mb-1">
                  <Target className="h-4 w-4 text-chart-1 mr-2" />
                  <span className="font-semibold text-xs">PURPOSE</span>
                </div>
                <p className="text-xs text-muted-foreground">Load all data streams and perform initial quality assessment</p>
              </motion.div>

              <motion.div
                className="bg-card rounded-lg border p-3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="flex items-center mb-1">
                  <FlaskConical className="h-4 w-4 text-chart-2 mr-2" />
                  <span className="font-semibold text-xs">KEY OUTPUTS</span>
                </div>
                <p className="text-xs text-muted-foreground">Raw data summaries, temporal coverage plots, missing data visualization</p>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="flex-grow container mx-auto px-4 pb-4"
        style={{ minHeight: '70vh' }}
      >
        <div 
          className="bg-card rounded-lg shadow-lg border overflow-hidden relative h-full"
          style={{ minHeight: '70vh' }}
        >
          <iframe
            src="/analysis/notebooks/html/01_data_prep.html"
            className="w-full h-full border-0"
            title="Data Prep"
            sandbox="allow-scripts allow-same-origin allow-forms"
            style={{ minHeight: '70vh' }}
          />
        </div>
      </motion.div>
    </div>
  );
}
