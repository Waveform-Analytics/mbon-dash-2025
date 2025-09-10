'use client';

import Link from 'next/link';
import { ArrowRight, Map, BarChart3, Beaker } from 'lucide-react';
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
            backgroundImage: `url('/images/yohan-marion-daufuskie-unsplash.jpg')`
          }}
        >
          {/* Dark overlay for text readability */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/70 via-primary/60 to-chart-3/65" />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative">
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
              Marine Biodiversity Dashboard
            </motion.h1>
            <motion.p 
              className="text-xl md:text-2xl text-primary-foreground/95 mb-8 max-w-4xl mx-auto font-light"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              Exploring whether acoustic indices can predict marine soundscape biodiversity 
              and serve as proxies for complex biodiversity monitoring
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
        className="py-16 px-4 sm:px-6 lg:px-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.0 }}
      >
        <div className="max-w-7xl mx-auto">
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            
            {/* The Challenge */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-8 border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.4 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Beaker className="h-8 w-8 text-chart-1 mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">The Challenge</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Manual species detection is labor-intensive and time-consuming. 
                Can we use automated acoustic analysis as an alternative?
              </p>
              <div className="bg-accent p-4 rounded-md">
                <p className="text-sm text-accent-foreground">
                  Quick visual: Manual detection effort vs need for automation
                </p>
              </div>
            </motion.div>

            {/* Our Approach */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-8 border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.6 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <BarChart3 className="h-8 w-8 text-chart-2 mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Our Approach</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                We analyze 60+ acoustic indices from 3 marine stations over 2 years, 
                comparing them to manual species detections.
              </p>
              <div className="bg-muted p-4 rounded-md">
                <p className="text-sm text-muted-foreground">
                  Interactive flowchart: Data → Analysis → Insights
                </p>
              </div>
            </motion.div>

            {/* Key Findings */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg p-8 border"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.8 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Map className="h-8 w-8 text-chart-3 mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Key Findings</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Discover which acoustic indices best predict biodiversity patterns 
                and their potential as monitoring tools.
              </p>
              <div className="bg-secondary p-4 rounded-md">
                <p className="text-sm text-secondary-foreground">
                  3-4 major discoveries with visual previews
                </p>
              </div>
            </motion.div>

          </motion.div>
        </div>
      </motion.section>

      {/* Quick Access Navigation */}
      <motion.section 
        className="py-16 px-4 sm:px-6 lg:px-8 bg-muted/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 2.0 }}
      >
        <div className="max-w-7xl mx-auto">
          <motion.h2 
            className="text-3xl font-bold text-center text-foreground mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 2.2 }}
          >
            Explore Our Research
          </motion.h2>
          
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 2.4 }}
          >
            
            {/* Data Overview */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 2.6 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <Link 
                href="/data" 
                className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border block h-full"
              >
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-1/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-1/30 transition-colors">
                    <Map className="h-6 w-6 text-chart-1" />
                  </div>
                  <h3 className="text-lg font-semibold text-card-foreground mb-2">Data Overview</h3>
                  <p className="text-sm text-muted-foreground">Study sites, soundscapes, and data collection methods</p>
                </div>
              </Link>
            </motion.div>

            {/* Analysis Journey */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 2.8 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <Link 
                href="/analysis" 
                className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border block h-full"
              >
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-2/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-2/30 transition-colors">
                    <BarChart3 className="h-6 w-6 text-chart-2" />
                  </div>
                  <h3 className="text-lg font-semibold text-card-foreground mb-2">Analysis Journey</h3>
                  <p className="text-sm text-muted-foreground">Step-by-step exploration of patterns and models</p>
                </div>
              </Link>
            </motion.div>

            {/* Insights */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 3.0 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <Link 
                href="/insights" 
                className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border block h-full"
              >
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-3/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-3/30 transition-colors">
                    <Beaker className="h-6 w-6 text-chart-3" />
                  </div>
                  <h3 className="text-lg font-semibold text-card-foreground mb-2">Insights</h3>
                  <p className="text-sm text-muted-foreground">Key indicators and practical applications</p>
                </div>
              </Link>
            </motion.div>


          </motion.div>
        </div>
      </motion.section>

      {/* Call to Action */}
      <motion.section 
        className="py-16 px-4 sm:px-6 lg:px-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 3.4 }}
      >
        <div className="max-w-4xl mx-auto text-center">
          <motion.h2 
            className="text-3xl font-bold text-foreground mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 3.6 }}
          >
            Ready to Dive In?
          </motion.h2>
          <motion.p 
            className="text-xl text-muted-foreground mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 3.8 }}
          >
            Start exploring our data and discover the connections between acoustic patterns and marine biodiversity.
          </motion.p>
          <motion.div 
            className="space-x-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 4.0 }}
          >
            <Link 
              href="/data"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
            >
              View Study Data
            </Link>
            <Link 
              href="/analysis"
              className="inline-flex items-center px-6 py-3 border border-border text-base font-medium rounded-md text-foreground bg-card hover:bg-accent transition-colors"
            >
              See Analysis Methods
            </Link>
          </motion.div>
        </div>
      </motion.section>
    </div>
  );
}