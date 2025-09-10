'use client';

import { motion } from 'framer-motion';
import { Compass, Search, Filter, Settings, Play, Eye, BarChart3, Map, Calendar, Clock } from 'lucide-react';

export default function ExplorePage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">Explore</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>

        {/* Quick Stats Cards */}
        <motion.div 
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <motion.div 
            className="bg-card rounded-lg shadow-lg p-4 border text-center"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <Search className="h-6 w-6 text-chart-1 mx-auto mb-2" />
            <div className="text-2xl font-bold text-card-foreground">12</div>
            <div className="text-sm text-muted-foreground">Search Views</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-4 border text-center"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <Filter className="h-6 w-6 text-chart-2 mx-auto mb-2" />
            <div className="text-2xl font-bold text-card-foreground">8</div>
            <div className="text-sm text-muted-foreground">Filter Options</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-4 border text-center"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <Eye className="h-6 w-6 text-chart-3 mx-auto mb-2" />
            <div className="text-2xl font-bold text-card-foreground">6</div>
            <div className="text-sm text-muted-foreground">Visual Types</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-4 border text-center"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <Settings className="h-6 w-6 text-chart-4 mx-auto mb-2" />
            <div className="text-2xl font-bold text-card-foreground">20+</div>
            <div className="text-sm text-muted-foreground">Parameters</div>
          </motion.div>
        </motion.div>

        {/* Interactive Exploration Tools */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <Compass className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">Interactive Exploration Tools</h2>
              <p className="text-muted-foreground">
                Specialized interfaces for investigating different aspects of marine acoustic data
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Species Explorer */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Search className="h-8 w-8 text-chart-1 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Species Explorer</h3>
                  <span className="px-2 py-1 bg-chart-1/20 text-chart-1 text-xs font-medium rounded-full">
                    Interactive
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground mb-4">
                Search and explore species detection patterns with dynamic filtering and time-series visualization.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Available Species:</span>
                  <span className="font-medium">15+</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Search Filters:</span>
                  <span className="font-medium">Station, Time, Activity</span>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-chart-1/10 text-chart-1 rounded-md hover:bg-chart-1/20 transition-colors">
                  Launch Explorer
                </button>
              </div>
            </motion.div>

            {/* Temporal Browser */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Calendar className="h-8 w-8 text-chart-2 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Temporal Browser</h3>
                  <span className="px-2 py-1 bg-chart-2/20 text-chart-2 text-xs font-medium rounded-full">
                    Time Series
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground mb-4">
                Navigate through time with interactive calendar and timeline controls for temporal pattern analysis.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Time Range:</span>
                  <span className="font-medium">2018-2021</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Resolution:</span>
                  <span className="font-medium">Hour, Day, Month</span>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-chart-2/10 text-chart-2 rounded-md hover:bg-chart-2/20 transition-colors">
                  Open Timeline
                </button>
              </div>
            </motion.div>

            {/* Acoustic Index Viewer */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.0 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <BarChart3 className="h-8 w-8 text-chart-3 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Index Viewer</h3>
                  <span className="px-2 py-1 bg-chart-3/20 text-chart-3 text-xs font-medium rounded-full">
                    Multi-Metric
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground mb-4">
                Compare multiple acoustic indices with correlation analysis and pattern matching tools.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Available Indices:</span>
                  <span className="font-medium">56</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Comparisons:</span>
                  <span className="font-medium">Multi-select</span>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-chart-3/10 text-chart-3 rounded-md hover:bg-chart-3/20 transition-colors">
                  Compare Indices
                </button>
              </div>
            </motion.div>

            {/* Station Comparator */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Map className="h-8 w-8 text-chart-4 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Station Comparator</h3>
                  <span className="px-2 py-1 bg-chart-4/20 text-chart-4 text-xs font-medium rounded-full">
                    Spatial
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground mb-4">
                Side-by-side comparison of monitoring stations with environmental context and activity patterns.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Stations:</span>
                  <span className="font-medium">9M, 14M, 37M</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Metrics:</span>
                  <span className="font-medium">Depth, Activity, Diversity</span>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-chart-4/10 text-chart-4 rounded-md hover:bg-chart-4/20 transition-colors">
                  Compare Stations
                </button>
              </div>
            </motion.div>

            {/* Pattern Detector */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.4 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Eye className="h-8 w-8 text-chart-5 mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Pattern Detector</h3>
                  <span className="px-2 py-1 bg-chart-5/20 text-chart-5 text-xs font-medium rounded-full">
                    AI-Powered
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground mb-4">
                Automated pattern recognition and anomaly detection with machine learning visualization tools.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Algorithms:</span>
                  <span className="font-medium">4 Models</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Patterns:</span>
                  <span className="font-medium">Temporal, Spectral</span>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-chart-5/10 text-chart-5 rounded-md hover:bg-chart-5/20 transition-colors">
                  Detect Patterns
                </button>
              </div>
            </motion.div>

            {/* Real-time Monitor */}
            <motion.div 
              className="bg-card rounded-lg shadow-lg border p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.6 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <div className="flex items-center mb-4">
                <Clock className="h-8 w-8 text-primary mr-3" />
                <div>
                  <h3 className="text-xl font-semibold">Real-time Monitor</h3>
                  <span className="px-2 py-1 bg-primary/20 text-primary text-xs font-medium rounded-full">
                    Live Data
                  </span>
                </div>
              </div>
              <p className="text-muted-foreground mb-4">
                Live acoustic monitoring dashboard with real-time species detection alerts and activity streams.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Update Rate:</span>
                  <span className="font-medium">30 seconds</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Alerts:</span>
                  <span className="font-medium">Species, Anomalies</span>
                </div>
                <button className="w-full mt-4 px-4 py-2 bg-primary/10 text-primary rounded-md hover:bg-primary/20 transition-colors">
                  Start Monitoring
                </button>
              </div>
            </motion.div>
          </div>
        </motion.section>

        {/* Interactive Demo Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.8 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-primary mb-6">Try Interactive Demo</h2>
          <div className="bg-card border shadow-lg rounded-lg p-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl font-semibold mb-4">Explore Sample Data</h3>
                <p className="text-muted-foreground mb-6">
                  Get started with our interactive demo featuring real data from the May River monitoring stations. 
                  Explore species detections, acoustic patterns, and environmental correlations.
                </p>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <Play className="h-5 w-5 text-chart-1 mr-3" />
                    <span>Interactive visualizations</span>
                  </div>
                  <div className="flex items-center">
                    <Filter className="h-5 w-5 text-chart-2 mr-3" />
                    <span>Dynamic filtering and search</span>
                  </div>
                  <div className="flex items-center">
                    <BarChart3 className="h-5 w-5 text-chart-3 mr-3" />
                    <span>Real-time chart updates</span>
                  </div>
                </div>
                <button className="mt-6 px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                  Launch Demo
                </button>
              </div>
              <div className="bg-muted rounded-lg p-8">
                <div className="text-center">
                  <Compass className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Interactive demo interface will be displayed here</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    Sample data from 3 stations • 2 years • 15+ species
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Quick Access Tools */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 2.0 }}
        >
          <h2 className="text-2xl font-semibold text-primary mb-6">Quick Access Tools</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: "Data Export", icon: Settings, desc: "Download filtered datasets" },
              { name: "Custom Views", icon: Eye, desc: "Save exploration settings" },
              { name: "Collaboration", icon: Search, desc: "Share findings with team" },
              { name: "API Access", icon: Filter, desc: "Programmatic data access" }
            ].map((tool, index) => (
              <motion.div
                key={tool.name}
                className="bg-muted rounded-lg p-4 border text-center"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 2.2 + index * 0.1 }}
                whileHover={{ y: -2, transition: { duration: 0.2 } }}
              >
                <tool.icon className="h-6 w-6 text-primary mx-auto mb-2" />
                <h4 className="font-semibold text-sm mb-1">{tool.name}</h4>
                <p className="text-xs text-muted-foreground">{tool.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>
      </div>
    </div>
  );
}