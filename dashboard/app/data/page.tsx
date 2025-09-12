'use client';

import { motion } from 'framer-motion';
import { BarChart3, Map, Fish, TrendingUp, Activity, Database } from 'lucide-react';

export default function DataPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">Data Overview</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>
        
        {/* Statistics Cards */}
        <motion.div 
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-12"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Map className="h-5 w-5 text-chart-1 mr-2" />
              <span className="text-sm text-muted-foreground">ANALYSIS STATIONS</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">3</div>
            <div className="text-sm text-muted-foreground">of 12 total</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <TrendingUp className="h-5 w-5 text-chart-2 mr-2" />
              <span className="text-sm text-muted-foreground">YEARS</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">2</div>
            <div className="text-sm text-muted-foreground">2018, 2021</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Fish className="h-5 w-5 text-chart-3 mr-2" />
              <span className="text-sm text-muted-foreground">SPECIES</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">15+</div>
            <div className="text-sm text-muted-foreground">Detected</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <BarChart3 className="h-5 w-5 text-chart-4 mr-2" />
              <span className="text-sm text-muted-foreground">INDICES</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">56</div>
            <div className="text-sm text-muted-foreground">Acoustic</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Activity className="h-5 w-5 text-chart-5 mr-2" />
              <span className="text-sm text-muted-foreground">ENVIRONMENTAL</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">2</div>
            <div className="text-sm text-muted-foreground">Temp, Depth</div>
          </motion.div>

          <motion.div 
            className="bg-card rounded-lg shadow-lg p-6 border"
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
          >
            <div className="flex items-center mb-2">
              <Database className="h-5 w-5 text-chart-1 mr-2" />
              <span className="text-sm text-muted-foreground">RECORDS</span>
            </div>
            <div className="text-3xl font-bold text-card-foreground">157K</div>
            <div className="text-sm text-muted-foreground">Total</div>
          </motion.div>
        </motion.div>

        {/* Monitoring Station Locations */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="flex items-center mb-4">
            <Map className="h-8 w-8 text-primary mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-card-foreground">Monitoring Station Locations</h2>
              <p className="text-muted-foreground">
                Three primary hydrophone monitoring stations in May River, SC (9M, 14M, 37M) with additional regional context stations. 
                Toggle between Study Area view (3 stations) and All Stations view.
              </p>
            </div>
          </div>
          
          <div className="bg-card rounded-lg shadow-lg border p-6">
            <div className="h-[400px] bg-muted rounded-lg">
              {/* Map container - blank for now */}
            </div>
          </div>
        </motion.section>

        {/* Stacked Visualization Panels */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-primary mb-6">Data Visualizations</h2>
          <div className="space-y-6">
            {/* Manual Detections Panel */}
            <div className="bg-card border shadow-lg rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Fish className="h-6 w-6 text-chart-1 mr-3" />
                  <h3 className="text-xl font-semibold">Manual Detections</h3>
                </div>
                <select className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background">
                  <option>Select Species</option>
                  <option>Dolphin clicks</option>
                  <option>Fish choruses</option>
                  <option>Snapping shrimp</option>
                </select>
              </div>
              <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">Heatmap visualization (day x hour)</p>
                  <p className="text-sm text-muted-foreground">D3.js implementation will be added here</p>
                </div>
              </div>
            </div>

            {/* Acoustic Indices Panel */}
            <div className="bg-card border shadow-lg rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <Activity className="h-6 w-6 text-chart-2 mr-3" />
                  <h3 className="text-xl font-semibold">Acoustic Indices</h3>
                </div>
                <select className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background">
                  <option>Select Index</option>
                  <option>Acoustic Complexity Index</option>
                  <option>Bioacoustic Index</option>
                  <option>Spectral Entropy</option>
                </select>
              </div>
              <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">Acoustic indices visualization (day x hour)</p>
                  <p className="text-sm text-muted-foreground">D3.js implementation will be added here</p>
                </div>
              </div>
            </div>

            {/* RMS SPL Panel */}
            <div className="bg-card border shadow-lg rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <TrendingUp className="h-6 w-6 text-chart-3 mr-3" />
                  <h3 className="text-xl font-semibold">RMS SPL</h3>
                </div>
                <select className="px-3 py-2 border border-gray-200 rounded-md text-sm bg-background">
                  <option>Select Bandwidth</option>
                  <option>Broadband</option>
                  <option>Low Frequency</option>
                  <option>High Frequency</option>
                </select>
              </div>
              <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-muted-foreground">RMS SPL visualization (day x hour)</p>
                  <p className="text-sm text-muted-foreground">D3.js implementation will be added here</p>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Environmental Data Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-12"
        >
          <h2 className="text-2xl font-semibold text-primary mb-6">Environmental Data</h2>
          <div className="bg-card border shadow-lg rounded-lg p-6">
            <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Database className="h-12 w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Environmental time series will be displayed here</p>
                <p className="text-sm text-muted-foreground">Temperature and depth measurements over time</p>
              </div>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}