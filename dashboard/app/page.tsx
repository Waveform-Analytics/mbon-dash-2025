'use client';

import Link from 'next/link';
import { ArrowRight, BarChart3, FlaskConical, Compass, BookOpen } from 'lucide-react';
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
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            
            {/* Data Section */}
            <Link href="/data">
              <motion.div 
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <BarChart3 className="h-8 w-8 text-chart-1 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Data</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Explore manual detections, environmental measurements, and acoustic indices from the MBON / ESONS project.
                </p>
                <div className="bg-accent p-4 rounded-md">
                  <p className="text-sm text-accent-foreground">
                    Interactive visualizations and data exploration tools
                  </p>
                </div>
              </motion.div>
            </Link>

            {/* Explore Section */}
            <Link href="/explore">
              <motion.div
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.0 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Compass className="h-8 w-8 text-chart-3 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Explore</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Interactive exploration tools and specialized views for investigating different aspects of the research.
                </p>
                <div className="bg-secondary p-4 rounded-md">
                  <p className="text-sm text-secondary-foreground">
                    Interactive visualizations and custom analysis tools
                  </p>
                </div>
              </motion.div>
            </Link>

            {/* Notebooks Section */}
            <Link href="/analysis">
              <motion.div
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.2 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <FlaskConical className="h-8 w-8 text-chart-2 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Notebooks</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Computational notebooks with analytical workflows for marine acoustic data analysis.
                </p>
                <div className="bg-muted p-4 rounded-md">
                  <p className="text-sm text-muted-foreground">
                    Marimo notebooks with interactive analysis workflows
                  </p>
                </div>
              </motion.div>
            </Link>

            {/* Background Section */}
            <Link href="/background">
              <motion.div
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.4 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <BookOpen className="h-8 w-8 text-chart-4 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Background</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Project background, research context, and detailed information about the MBON / ESONS initiatives.
                </p>
                <div className="bg-accent p-4 rounded-md">
                  <p className="text-sm text-accent-foreground">
                    Research goals, methodology, and project details
                  </p>
                </div>
              </motion.div>
            </Link>

          </motion.div>
        </div>
      </motion.section>

    </div>
  );
}