import React from 'react';
import { motion } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Activity, Mic, Waves, BarChart3, Info } from 'lucide-react';
import { SoundWaveAnimation, FloatingParticles } from './LoadingSpinner';
import { dataTypeDescriptions } from '../data/mockData';

export function DataTypesPage() {
  return (
    <motion.div 
      className="space-y-6 relative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <FloatingParticles />
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10"
      >
        <motion.div className="flex items-center gap-3 mb-2">
          <motion.h1
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
          >
            Data Types & Methodology
          </motion.h1>
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <SoundWaveAnimation />
          </motion.div>
        </motion.div>
        <motion.p 
          className="text-muted-foreground mt-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
        >
          Understanding the acoustic indices, recording methods, and data processing techniques 
          used in the May River soundscape analysis project.
        </motion.p>
      </motion.div>

      {/* Acoustic Indices Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.6 }}
        className="relative z-10"
      >
        <Card className="relative overflow-hidden group">
          <motion.div
            className="absolute inset-0 bg-gradient-to-br from-teal-500/5 to-cyan-500/5"
            initial={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
          />
          <CardHeader className="relative z-10">
            <CardTitle className="flex items-center gap-2">
              <motion.div
                whileHover={{ scale: 1.2, rotate: 5 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                <BarChart3 className="h-5 w-5 text-teal-600" />
              </motion.div>
              {dataTypeDescriptions.acousticIndices.title}
            </CardTitle>
            <CardDescription>
              {dataTypeDescriptions.acousticIndices.description}
            </CardDescription>
          </CardHeader>
          <CardContent className="relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {dataTypeDescriptions.acousticIndices.indices.map((index, i) => (
                <motion.div 
                  key={index.abbreviation} 
                  className="border rounded-lg p-4 space-y-3 hover:shadow-lg transition-shadow relative overflow-hidden group"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.8 + i * 0.1 }}
                  whileHover={{ scale: 1.02, y: -2 }}
                >
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5"
                    initial={{ scale: 0, opacity: 0 }}
                    whileHover={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  />
                  
                  <div className="flex items-start justify-between relative z-10">
                    <div>
                      <motion.h3 
                        className="font-semibold"
                        whileHover={{ color: "#0891b2" }}
                      >
                        {index.name}
                      </motion.h3>
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Badge variant="outline" className="mt-1 cursor-pointer hover:bg-teal-50">
                          {index.abbreviation}
                        </Badge>
                      </motion.div>
                    </div>
                    <motion.div 
                      className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded"
                      whileHover={{ scale: 1.05, backgroundColor: "#e6fffa" }}
                    >
                      Range: {index.range}
                    </motion.div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground relative z-10">
                    {index.description}
                  </p>
                  
                  <motion.div 
                    className="bg-blue-50 p-3 rounded text-sm relative z-10"
                    whileHover={{ backgroundColor: "#e0f7fa" }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="flex items-start gap-2">
                      <motion.div
                        animate={{ 
                          rotate: [0, 10, 0, -10, 0],
                          scale: [1, 1.1, 1]
                        }}
                        transition={{
                          duration: 3,
                          repeat: Infinity,
                          ease: "easeInOut"
                        }}
                      >
                        <Info className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                      </motion.div>
                      <div>
                        <span className="font-medium text-blue-900">Interpretation: </span>
                        <span className="text-blue-800">{index.interpretation}</span>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Instrument Types Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mic className="h-5 w-5" />
            {dataTypeDescriptions.instrumentTypes.title}
          </CardTitle>
          <CardDescription>
            {dataTypeDescriptions.instrumentTypes.description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {dataTypeDescriptions.instrumentTypes.types.map((type, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    {type.name.includes('Hydrophone') && <Waves className="h-6 w-6 text-blue-600" />}
                    {type.name.includes('Terrestrial') && <Activity className="h-6 w-6 text-green-600" />}
                    {type.name.includes('Combined') && <BarChart3 className="h-6 w-6 text-purple-600" />}
                  </div>
                  
                  <div className="flex-1 space-y-3">
                    <div>
                      <h3 className="font-semibold">{type.name}</h3>
                      <p className="text-muted-foreground text-sm mt-1">{type.description}</p>
                    </div>
                    
                    <div className="bg-gray-50 p-3 rounded text-sm">
                      <span className="font-medium">Technical Specifications: </span>
                      <span className="text-muted-foreground">{type.specifications}</span>
                    </div>
                    
                    <div>
                      <span className="font-medium text-sm">Primary Applications:</span>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {type.applications.map((app, appIndex) => (
                          <Badge key={appIndex} variant="secondary" className="text-xs">
                            {app}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Data Processing Workflow */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Data Processing Workflow
          </CardTitle>
          <CardDescription>
            Step-by-step process from raw audio recordings to acoustic indices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                step: 1,
                title: 'Raw Audio Collection',
                description: 'Continuous recording at high sample rates (44.1-96 kHz) with synchronized timestamps',
                duration: '24/7 continuous'
              },
              {
                step: 2,
                title: 'Quality Assessment',
                description: 'Automated detection of recording artifacts, weather interference, and equipment malfunctions',
                duration: 'Real-time processing'
              },
              {
                step: 3,
                title: 'Segmentation',
                description: 'Division of recordings into standardized time windows for analysis (typically 1-minute segments)',
                duration: '~5 minutes processing per hour'
              },
              {
                step: 4,
                title: 'Spectral Analysis',
                description: 'Fast Fourier Transform (FFT) to convert time-domain signals to frequency domain',
                duration: '~2 minutes per segment'
              },
              {
                step: 5,
                title: 'Index Calculation',
                description: 'Computation of ACI, ADI, AEI, BI, and NDSI values from spectrograms',
                duration: '~30 seconds per segment'
              },
              {
                step: 6,
                title: 'Environmental Correlation',
                description: 'Integration with weather data, tidal information, and habitat conditions',
                duration: 'Daily batch processing'
              }
            ].map((step) => (
              <div key={step.step} className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-medium">
                  {step.step}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium">{step.title}</h4>
                  <p className="text-sm text-muted-foreground mt-1">{step.description}</p>
                  <div className="text-xs text-primary mt-1">⏱️ {step.duration}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Data Quality & Validation */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Data Quality Standards</CardTitle>
            <CardDescription>Ensuring reliable and consistent measurements</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">Signal-to-noise ratio &gt; 15dB</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">&lt; 5% data loss per deployment</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">Cross-validation with manual annotations</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm">Calibrated reference recordings monthly</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Environmental Metadata</CardTitle>
            <CardDescription>Contextual data collected alongside acoustics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm">Temperature</span>
              <Badge variant="outline">°C, hourly</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Humidity</span>
              <Badge variant="outline">%, hourly</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Wind Speed</span>
              <Badge variant="outline">m/s, hourly</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Tidal Stage</span>
              <Badge variant="outline">m, 15-min</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-sm">Moon Phase</span>
              <Badge variant="outline">%, daily</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}