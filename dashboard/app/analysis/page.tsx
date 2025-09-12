'use client';

import { motion } from 'framer-motion';
import { FlaskConical, TrendingUp, BarChart3, Target, Activity, Database, ArrowRight, BookOpen } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';

interface Notebook {
  slug: string;
  title: string;
  description: string;
  purpose: string;
  keyOutputs: string;
  filename: string;
  order: number;
  lastModified: string;
}

export default function AnalysisPage() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [notebooksLoading, setNotebooksLoading] = useState(true);

  useEffect(() => {
    async function loadNotebooks() {
      try {
        const response = await fetch('/analysis/notebooks/notebooks.json');
        if (response.ok) {
          const data = await response.json();
          setNotebooks(data);
        }
      } catch (error) {
        console.error('Failed to load notebooks:', error);
      } finally {
        setNotebooksLoading(false);
      }
    }
    
    loadNotebooks();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">Analysis</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>



        {/* Interactive Notebooks Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <BookOpen className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">Interactive Analysis Notebooks</h2>
              <p className="text-muted-foreground">
                Computational notebooks with interactive visualizations and reproducible analysis workflows
              </p>
            </div>
          </div>
          
          {notebooksLoading ? (
            <div className="bg-card border shadow-lg rounded-lg p-8 text-center">
              <div className="animate-pulse">
                <div className="h-4 bg-muted rounded w-1/4 mx-auto mb-4"></div>
                <div className="h-2 bg-muted rounded w-1/2 mx-auto"></div>
              </div>
            </div>
          ) : notebooks.length === 0 ? (
            <div className="bg-card border shadow-lg rounded-lg p-8 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Notebooks Available</h3>
              <p className="text-muted-foreground mb-4">
                Run the build script to generate notebook pages from your marimo exports.
              </p>
              <code className="px-3 py-1 bg-muted rounded text-sm">npm run build:notebooks</code>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {notebooks.map((notebook, index) => (
                <motion.div
                  key={notebook.slug}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
                >
                  <Link href={`/analysis/notebooks/${notebook.slug}`}>
                    <motion.div
                      className="bg-card border shadow-lg rounded-lg p-6 h-full cursor-pointer"
                      whileHover={{ y: -4, transition: { duration: 0.2 } }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center">
                          <Activity className="h-6 w-6 text-chart-1 mr-3" />
                          <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            Live
                          </span>
                        </div>
                        <ArrowRight className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <h3 className="text-lg font-semibold mb-3 text-card-foreground">
                        {notebook.title}
                      </h3>
                      
                      <div className="space-y-3 mb-4">
                        <div>
                          <div className="flex items-center mb-1">
                            <Target className="h-3 w-3 text-chart-2 mr-1" />
                            <span className="text-xs font-medium text-muted-foreground">PURPOSE</span>
                          </div>
                          <p className="text-xs text-muted-foreground leading-relaxed">
                            {notebook.purpose}
                          </p>
                        </div>
                        
                        <div>
                          <div className="flex items-center mb-1">
                            <FlaskConical className="h-3 w-3 text-chart-3 mr-1" />
                            <span className="text-xs font-medium text-muted-foreground">KEY OUTPUTS</span>
                          </div>
                          <p className="text-xs text-muted-foreground leading-relaxed">
                            {notebook.keyOutputs}
                          </p>
                        </div>
                      </div>
                      
                      <div className="text-xs text-muted-foreground">
                        Last updated: {new Date(notebook.lastModified).toLocaleDateString()}
                      </div>
                    </motion.div>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </motion.section>

      </div>
    </div>
  );
}