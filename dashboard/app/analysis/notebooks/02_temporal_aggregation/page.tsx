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
            <div className="flex items-center mb-2">
              <div className="w-10 h-10 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-lg font-bold mr-4">
                02
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Notebook 02</div>
                <h1 className="text-3xl font-bold text-primary">Temporal Aggregation</h1>
              </div>
            </div>
            
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
                <p className="text-xs text-muted-foreground">Align all data to consistent 2-hour temporal resolution matching manual detections</p>
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
                <p className="text-xs text-muted-foreground">Temporally aligned dataset ready for analysis</p>
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
            src="/analysis/notebooks/html/02_temporal_aggregation.html"
            className="w-full h-full border-0"
            title="Temporal Aggregation"
            sandbox="allow-scripts allow-same-origin allow-forms"
            style={{ minHeight: '70vh' }}
          />
        </div>
      </motion.div>
    </div>
  );
}
