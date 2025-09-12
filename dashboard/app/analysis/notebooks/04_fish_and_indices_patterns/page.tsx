'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Target, FlaskConical, Maximize2, Minimize2 } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

export default function NotebookPage() {
  const [isFullscreen, setIsFullscreen] = useState(false);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.getElementById('notebook-container')?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

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
            <h1 className="text-3xl font-bold text-primary mb-2">Fish And Indices Patterns</h1>
            
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
                <p className="text-xs text-muted-foreground">Interactive marimo notebook: Fish And Indices Patterns</p>
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
                <p className="text-xs text-muted-foreground">Analysis results and visualizations</p>
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
      >
        <div 
          className="bg-card rounded-lg shadow-lg border overflow-hidden relative h-full"
          id="notebook-container"
        >
          <button
            onClick={toggleFullscreen}
            className="absolute top-4 right-4 z-10 bg-background/80 backdrop-blur-sm border rounded-lg p-2 hover:bg-background/90 transition-colors"
            title={isFullscreen ? "Exit fullscreen" : "View fullscreen"}
          >
            {isFullscreen ? (
              <Minimize2 className="h-5 w-5" />
            ) : (
              <Maximize2 className="h-5 w-5" />
            )}
          </button>
          <iframe
            src="/analysis/notebooks/html/04_fish_and_indices_patterns.html"
            className="w-full h-full border-0"
            title="Fish And Indices Patterns"
            sandbox="allow-scripts allow-same-origin allow-forms"
          />
        </div>
      </motion.div>
    </div>
  );
}
