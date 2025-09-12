'use client';

import Link from 'next/link';
import { ArrowRight, Map, BarChart3, FlaskConical, Compass } from 'lucide-react';
import { motion } from 'framer-motion';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative text-primary-foreground pb-24 pt-8 overflow-hidden">
        {/* Background image with overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('/hero.jpg')`
          }}
        >
          {/* Dark overlay for text readability */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/70 via-primary/60 to-chart-3/65" />
        </div>
        
        <div className="container mx-auto px-4 py-16 relative">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.h1 
              className="text-4xl md:text-6xl font-bold text-primary-foreground mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              Marine Biodiversity Observation Network
            </motion.h1>
            <motion.p 
              className="text-xl md:text-2xl text-primary-foreground/95 mb-8 max-w-4xl mx-auto font-light"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              USC Dashboard for ESONS Project
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <Link 
                href="/data"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
              >
                View the Data
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Main Content Grid */}
      <motion.section 
        className="py-16"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="container mx-auto px-4">
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            
            {/* Data Section */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-8 border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <BarChart3 className="h-8 w-8 text-chart-1 mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Data</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Explore acoustic data, manual detections, and environmental measurements from multiple monitoring stations.
              </p>
              <div className="bg-accent p-4 rounded-md">
                <p className="text-sm text-accent-foreground">
                  Interactive visualizations and data exploration tools
                </p>
              </div>
            </motion.div>

            {/* Analysis Section */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-8 border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.0 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <FlaskConical className="h-8 w-8 text-chart-2 mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Analysis</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Detailed analytical workflows and computational notebooks examining marine acoustic data patterns.
              </p>
              <div className="bg-muted p-4 rounded-md">
                <p className="text-sm text-muted-foreground">
                  Marimo notebooks with interactive analysis workflows
                </p>
              </div>
            </motion.div>

            {/* Explore Section */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-8 border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Compass className="h-8 w-8 text-chart-3 mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Explore</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Interactive exploration tools and specialized views for investigating different aspects of the research.
              </p>
              <div className="bg-secondary p-4 rounded-md">
                <p className="text-sm text-secondary-foreground">
                  Advanced exploration interfaces and custom analysis tools
                </p>
              </div>
            </motion.div>

          </motion.div>
        </div>
      </motion.section>

      {/* Station Locations Section */}
      <motion.section 
        className="py-16 bg-accent/10"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.4 }}
      >
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.6 }}
          >
            <div className="flex items-center mb-8">
              <Map className="h-8 w-8 text-primary mr-3" />
              <h2 className="text-3xl font-semibold text-primary">Station Locations</h2>
            </div>
            <div className="bg-card rounded-lg shadow-lg border p-8">
              <div className="h-[400px] bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Map className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Interactive map will be displayed here</p>
                  <p className="text-sm text-muted-foreground mt-2">Showing monitoring station locations and metadata</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.section>
    </div>
  );
}