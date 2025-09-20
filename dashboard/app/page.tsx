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
              Can underwater sound patterns reveal marine ecosystem health?
            </motion.h1>
            <motion.p 
              className="text-xl md:text-2xl text-primary-foreground/95 mb-8 max-w-4xl mx-auto font-light"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              We explore whether acoustic indices—automated measurements of underwater sound characteristics—can identify periods of fish community activity, potentially transforming how we monitor marine biodiversity.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <Link 
                href="/challenge"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
              >
                Explore the Challenge
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Project Context Cards */}
      <motion.section 
        className="py-12 bg-accent/10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="container mx-auto px-4">
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
          >
            <motion.div 
              className="bg-card/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border text-center"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="text-3xl font-bold text-primary mb-2">1 Year</div>
              <div className="text-sm text-muted-foreground mb-1">ESONS acoustic data analyzed</div>
              <div className="text-xs text-muted-foreground">May River, South Carolina</div>
            </motion.div>

            <motion.div 
              className="bg-card/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border text-center"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="text-3xl font-bold text-primary mb-2">85%</div>
              <div className="text-sm text-muted-foreground mb-1">Community activity detected</div>
              <div className="text-xs text-muted-foreground">with 40-60% less analysis time</div>
            </motion.div>

            <motion.div 
              className="bg-card/80 backdrop-blur-sm rounded-lg shadow-lg p-6 border text-center"
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="text-3xl font-bold text-primary mb-2">MBON</div>
              <div className="text-sm text-muted-foreground mb-1">Funded proof-of-concept</div>
              <div className="text-xs text-muted-foreground">for scalable monitoring</div>
            </motion.div>
          </motion.div>

          <motion.div 
            className="text-center mt-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.8 }}
          >
            <p className="text-muted-foreground max-w-3xl mx-auto">
              <strong>Building on the ESONS foundation:</strong> This research builds on the Montie Lab&apos;s decade+ of marine acoustic monitoring,
              testing whether acoustic indices can serve as community-level screening tools for broader marine biodiversity monitoring applications.
            </p>
          </motion.div>
        </div>
      </motion.section>

      {/* Main Content Grid */}
      <motion.section 
        className="py-16"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="container mx-auto px-4">
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 items-stretch"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            
            {/* The Challenge Section */}
            <Link href="/challenge">
              <motion.div 
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group h-full flex flex-col"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <BookOpen className="h-8 w-8 text-chart-1 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">The Challenge</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Marine ecosystem monitoring challenges and the ESONS foundation that enables this research.
                </p>
                <div className="bg-accent p-4 rounded-md">
                  <p className="text-sm text-accent-foreground">
                    Context and motivation for scalable monitoring approaches
                  </p>
                </div>
              </motion.div>
            </Link>

            {/* Our Approach Section */}
            <Link href="/approach">
              <motion.div
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group h-full flex flex-col"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.0 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <BarChart3 className="h-8 w-8 text-chart-3 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Our Approach</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Acoustic indices methodology, study design, and validation against expert manual detections.
                </p>
                <div className="bg-secondary p-4 rounded-md">
                  <p className="text-sm text-secondary-foreground">
                    Data visualizations and methodological approach
                  </p>
                </div>
              </motion.div>
            </Link>

            {/* Key Findings Section */}
            <Link href="/findings">
              <motion.div
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group h-full flex flex-col"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.2 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <Compass className="h-8 w-8 text-chart-2 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Key Findings</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Results from our proof-of-concept: 85% detection rate and community-level screening validation.
                </p>
                <div className="bg-muted p-4 rounded-md">
                  <p className="text-sm text-muted-foreground">
                    Interactive results dashboard and broader implications
                  </p>
                </div>
              </motion.div>
            </Link>

            {/* Deep Dive Section */}
            <Link href="/analysis">
              <motion.div
                className="bg-card rounded-lg shadow-lg p-8 border cursor-pointer group h-full flex flex-col"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 1.4 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <FlaskConical className="h-8 w-8 text-chart-4 mr-3" />
                    <h2 className="text-2xl font-bold text-card-foreground">Deep Dive</h2>
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <p className="text-muted-foreground mb-6">
                  Technical methods, computational notebooks, and detailed analysis workflows.
                </p>
                <div className="bg-accent p-4 rounded-md">
                  <p className="text-sm text-accent-foreground">
                    Marimo notebooks, methodology, and future directions
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