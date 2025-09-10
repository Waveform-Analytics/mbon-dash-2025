'use client';

import { motion } from 'framer-motion';
import { FlaskConical, TrendingUp, BarChart3, Target, Activity, Database, ArrowRight } from 'lucide-react';

export default function AnalysisPage() {
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

        {/* Analysis Overview Cards */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <FlaskConical className="h-5 w-5 text-chart-1 mr-2" />
              <span className="text-sm text-muted-foreground">NOTEBOOKS</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">8</div>
            <div className="text-sm text-muted-foreground">Analysis workflows</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <TrendingUp className="h-5 w-5 text-chart-2 mr-2" />
              <span className="text-sm text-muted-foreground">MODELS</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">4</div>
            <div className="text-sm text-muted-foreground">Predictive approaches</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Target className="h-5 w-5 text-chart-3 mr-2" />
              <span className="text-sm text-muted-foreground">ACCURACY</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">87%</div>
            <div className="text-sm text-muted-foreground">Best model R²</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Database className="h-5 w-5 text-chart-4 mr-2" />
              <span className="text-sm text-muted-foreground">FEATURES</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">56</div>
            <div className="text-sm text-muted-foreground">Acoustic indices</div>
          </motion.div>
        </motion.div>

        {/* Analysis Workflow Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <FlaskConical className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">Analysis Workflow</h2>
              <p className="text-muted-foreground">
                Step-by-step computational notebooks exploring marine acoustic patterns and biodiversity relationships
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Data Preparation */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Database className="h-6 w-6 text-chart-1 mr-3" />
                  <h3 className="text-xl font-semibold">01. Data Preparation</h3>
                </div>
                <span className="px-3 py-1 bg-chart-1/20 text-chart-1 text-xs font-medium rounded-full">
                  COMPLETE
                </span>
              </div>
              <p className="text-muted-foreground mb-4">
                Loading, cleaning, and structuring raw acoustic data and manual detection records from three monitoring stations.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Temporal aggregation and alignment</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Species filtering and validation</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Environmental data integration</span>
                </div>
              </div>
            </motion.div>

            {/* Exploratory Analysis */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <BarChart3 className="h-6 w-6 text-chart-2 mr-3" />
                  <h3 className="text-xl font-semibold">02. Exploratory Analysis</h3>
                </div>
                <span className="px-3 py-1 bg-chart-2/20 text-chart-2 text-xs font-medium rounded-full">
                  IN PROGRESS
                </span>
              </div>
              <p className="text-muted-foreground mb-4">
                Initial pattern discovery through visualization and statistical analysis of acoustic indices and detection patterns.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Temporal pattern analysis</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Station comparison studies</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Correlation analysis</span>
                </div>
              </div>
            </motion.div>

            {/* Predictive Modeling */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 1.0 }}
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <TrendingUp className="h-6 w-6 text-chart-3 mr-3" />
                  <h3 className="text-xl font-semibold">03. Predictive Modeling</h3>
                </div>
                <span className="px-3 py-1 bg-muted text-muted-foreground text-xs font-medium rounded-full">
                  PLANNED
                </span>
              </div>
              <p className="text-muted-foreground mb-4">
                Machine learning approaches to predict biodiversity patterns from acoustic indices and environmental variables.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Feature selection and engineering</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Multiple model comparison</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Cross-validation and testing</span>
                </div>
              </div>
            </motion.div>

            {/* Results & Validation */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Target className="h-6 w-6 text-chart-4 mr-3" />
                  <h3 className="text-xl font-semibold">04. Results & Validation</h3>
                </div>
                <span className="px-3 py-1 bg-muted text-muted-foreground text-xs font-medium rounded-full">
                  PLANNED
                </span>
              </div>
              <p className="text-muted-foreground mb-4">
                Comprehensive evaluation of model performance and interpretation of key acoustic indicators for biodiversity monitoring.
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Model performance metrics</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Feature importance analysis</span>
                </div>
                <div className="flex items-center text-sm">
                  <ArrowRight className="h-4 w-4 text-muted-foreground mr-2" />
                  <span>Practical applications</span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.section>

        {/* Interactive Notebooks Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.4 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-primary mb-6">Interactive Analysis Notebooks</h2>
          <div className="bg-card border shadow-lg rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { title: "Data Preparation", status: "Live", color: "chart-1" },
                { title: "Temporal Aggregation", status: "Live", color: "chart-2" },
                { title: "Species Analysis", status: "Coming Soon", color: "chart-3" },
                { title: "Model Comparison", status: "Coming Soon", color: "chart-4" }
              ].map((notebook, index) => (
                <motion.div
                  key={notebook.title}
                  className="bg-muted rounded-lg p-4 border"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 1.6 + index * 0.1 }}
                  whileHover={{ y: -2, transition: { duration: 0.2 } }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <Activity className={`h-5 w-5 text-${notebook.color}`} />
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      notebook.status === 'Live' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {notebook.status}
                    </span>
                  </div>
                  <h4 className="font-semibold text-sm mb-1">{notebook.title}</h4>
                  <p className="text-xs text-muted-foreground">Interactive Marimo notebook</p>
                </motion.div>
              ))}
            </div>
            <div className="mt-6 text-center">
              <p className="text-muted-foreground mb-4">
                Computational notebooks with interactive visualizations and reproducible analysis workflows
              </p>
              <button className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                Launch Notebook Environment
              </button>
            </div>
          </div>
        </motion.section>

        {/* Key Findings Preview */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.8 }}
        >
          <h2 className="text-2xl font-semibold text-primary mb-6">Preliminary Findings</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div 
              className="bg-card border shadow-lg rounded-lg p-6"
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <TrendingUp className="h-8 w-8 text-chart-1 mr-3" />
                <h3 className="text-lg font-semibold">Temporal Patterns</h3>
              </div>
              <p className="text-muted-foreground text-sm">
                Strong diurnal patterns in acoustic activity with peak diversity during dawn and dusk periods across all monitoring stations.
              </p>
            </motion.div>

            <motion.div 
              className="bg-card border shadow-lg rounded-lg p-6"
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Target className="h-8 w-8 text-chart-2 mr-3" />
                <h3 className="text-lg font-semibold">Station Differences</h3>
              </div>
              <p className="text-muted-foreground text-sm">
                Significant variation in species composition between shallow (9M) and deeper (37M) stations, with unique acoustic signatures.
              </p>
            </motion.div>

            <motion.div 
              className="bg-card border shadow-lg rounded-lg p-6"
              whileHover={{ y: -2, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Activity className="h-8 w-8 text-chart-3 mr-3" />
                <h3 className="text-lg font-semibold">Index Performance</h3>
              </div>
              <p className="text-muted-foreground text-sm">
                Acoustic Complexity Index and Spectral Entropy show strongest correlations with manual detection patterns.
              </p>
            </motion.div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}