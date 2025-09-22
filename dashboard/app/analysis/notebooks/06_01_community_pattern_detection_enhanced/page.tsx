'use client';

import { motion } from 'framer-motion';
import { ArrowLeft, Target, FlaskConical, Maximize2, Minimize2, X } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';

export default function NotebookPage() {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const iframeRef = useRef(null);

  // Handle ESC key for fullscreen exit
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    if (isFullscreen) {
      document.addEventListener('keydown', handleKeyPress);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyPress);
      document.body.style.overflow = 'unset';
    };
  }, [isFullscreen]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header - Hidden in fullscreen */}
      {!isFullscreen && (
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
                  06
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Notebook 06</div>
                  <h1 className="text-3xl font-bold text-primary">01 Community Pattern Detection Enhanced</h1>
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
                  <p className="text-xs text-muted-foreground">Interactive marimo notebook: 01 Community Pattern Detection Enhanced</p>
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
      )}

      {/* Notebook Container */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className={isFullscreen ? 
          "fixed inset-0 z-50 bg-background" : 
          "flex-grow container mx-auto px-4 pb-4"
        }
        style={{ minHeight: isFullscreen ? '100vh' : '70vh' }}
      >
        <div 
          className={
            "bg-card rounded-lg shadow-lg border overflow-hidden relative h-full " +
            (isFullscreen ? "rounded-none shadow-none border-0" : "")
          }
          style={{ minHeight: isFullscreen ? '100vh' : '70vh' }}
        >
          {/* Fullscreen Controls */}
          <div className="absolute top-4 right-4 z-10 flex gap-2">
            <button
              onClick={toggleFullscreen}
              className="bg-white/90 hover:bg-white border rounded-lg p-2 shadow-lg transition-all backdrop-blur-sm"
              title={isFullscreen ? "Exit Fullscreen (ESC)" : "Enter Fullscreen"}
              aria-label={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              {isFullscreen ? 
                <Minimize2 className="h-5 w-5 text-gray-700" /> : 
                <Maximize2 className="h-5 w-5 text-gray-700" />
              }
            </button>
          </div>

          {/* Iframe */}
          <iframe
            ref={iframeRef}
            src="/analysis/notebooks/html/06_01_community_pattern_detection_enhanced.html"
            className="w-full h-full border-0"
            title="01 Community Pattern Detection Enhanced"
            sandbox="allow-scripts allow-same-origin allow-forms"
            style={{ 
              minHeight: isFullscreen ? '100vh' : '70vh',
              borderRadius: isFullscreen ? '0' : 'inherit'
            }}
          />
        </div>
      </motion.div>
    </div>
  );
}
