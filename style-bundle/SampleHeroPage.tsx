'use client';

import Link from 'next/link';
import { ArrowRight, Map, BarChart3, Beaker, Activity, Database } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

/**
 * Sample Hero Page Component
 * 
 * This is a template showing how to create a stunning hero section with the MBON design system.
 * Features:
 * - Full-width hero with background image and gradient overlay
 * - Animated text entrance with Framer Motion
 * - Responsive grid layout for content cards
 * - Hover effects and micro-interactions
 * 
 * To customize:
 * 1. Replace the hero background image in /public/images/
 * 2. Update the hero title and description text
 * 3. Modify the gradient overlay colors (from-primary/70 via-primary/60 to-chart-3/65)
 * 4. Adjust the content cards to match your needs
 */

export default function SampleHeroPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section with Background Image */}
      <section className="relative text-primary-foreground pb-24 pt-8 overflow-hidden">
        {/* Background image with gradient overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('/images/yohan-marion-daufuskie-unsplash.jpg')`
          }}
        >
          {/* Gradient overlay for text readability - customize these colors */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/70 via-primary/60 to-chart-3/65" />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 relative">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            {/* Main Hero Title */}
            <motion.h1 
              className="text-4xl md:text-6xl font-bold text-primary-foreground mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              Your Project Title Here
            </motion.h1>
            
            {/* Hero Subtitle/Description */}
            <motion.p 
              className="text-xl md:text-2xl text-primary-foreground/95 mb-8 max-w-4xl mx-auto font-light"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              A compelling description of your project that explains its purpose 
              and value in one or two clear sentences
            </motion.p>
            
            {/* Call to Action Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <Link 
                href="/explore"
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Content Section with Cards */}
      <motion.section 
        className="py-16 px-4 sm:px-6 lg:px-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.0 }}
      >
        <div className="max-w-7xl mx-auto">
          {/* Grid of Feature Cards */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            
            {/* Feature Card 1 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.4 }}
            >
              <Card className="h-full hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Beaker className="h-6 w-6 text-chart-1" />
                    </div>
                    <CardTitle>Feature One</CardTitle>
                  </div>
                  <CardDescription>
                    Brief description of this feature
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    More detailed explanation of what this feature offers and why it matters 
                    to your users. Keep it concise but informative.
                  </p>
                </CardContent>
              </Card>
            </motion.div>

            {/* Feature Card 2 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.5 }}
            >
              <Card className="h-full hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <BarChart3 className="h-6 w-6 text-chart-2" />
                    </div>
                    <CardTitle>Feature Two</CardTitle>
                  </div>
                  <CardDescription>
                    Brief description of this feature
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Explain the value proposition of this feature. What problems does it solve? 
                    How does it improve the user experience?
                  </p>
                </CardContent>
              </Card>
            </motion.div>

            {/* Feature Card 3 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.6 }}
            >
              <Card className="h-full hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Database className="h-6 w-6 text-chart-3" />
                    </div>
                    <CardTitle>Feature Three</CardTitle>
                  </div>
                  <CardDescription>
                    Brief description of this feature
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Describe the technical capabilities or unique aspects of this feature. 
                    Focus on benefits rather than technical details.
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>

          {/* Additional Section */}
          <motion.div
            className="mt-16 text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.8 }}
          >
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Ready to Learn More?
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Explore our comprehensive documentation and examples to get the most out of your project.
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/documentation"
                className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                View Documentation
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="/examples"
                className="inline-flex items-center px-6 py-3 border border-primary text-primary rounded-md hover:bg-primary/10 transition-colors"
              >
                See Examples
              </Link>
            </div>
          </motion.div>
        </div>
      </motion.section>
    </div>
  );
}