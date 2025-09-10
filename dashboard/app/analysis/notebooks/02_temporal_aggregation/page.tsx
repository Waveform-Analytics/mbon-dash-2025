'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Target, FlaskConical } from 'lucide-react';
import Link from 'next/link';

export default function NotebookPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-6"
        >
          <Link 
            href="/analysis" 
            className="inline-flex items-center text-primary hover:text-primary/80 transition-colors mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Analysis
          </Link>
          <div className="mb-6">
            <h1 className="text-4xl font-bold text-primary mb-4">Temporal Aggregation</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <motion.div
                className="bg-card rounded-lg border p-4"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <div className="flex items-center mb-2">
                  <Target className="h-5 w-5 text-chart-1 mr-2" />
                  <span className="font-semibold text-sm">PURPOSE</span>
                </div>
                <p className="text-sm text-muted-foreground">Align all data to consistent 2-hour temporal resolution matching manual detections</p>
              </motion.div>

              <motion.div
                className="bg-card rounded-lg border p-4"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                <div className="flex items-center mb-2">
                  <FlaskConical className="h-5 w-5 text-chart-2 mr-2" />
                  <span className="font-semibold text-sm">KEY OUTPUTS</span>
                </div>
                <p className="text-sm text-muted-foreground">Temporally aligned dataset ready for analysis</p>
              </motion.div>
            </div>
          </div>
          <div className="h-1 w-20 bg-primary rounded"></div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-card rounded-lg shadow-lg border overflow-hidden"
        >
          <iframe
            src="/analysis/notebooks/html/02_temporal_aggregation.html"
            className="w-full h-[calc(100vh-280px)] border-0"
            title="Temporal Aggregation"
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        </motion.div>
      </div>
    </div>
  );
}
