import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { MapPin, Calendar, Database, Activity } from 'lucide-react';
import { InstrumentMap } from './InstrumentMap';
import { DeploymentGantt } from './DeploymentGantt';
import { instrumentLocations, deploymentSchedule } from '../data/mockData';

export function LandingPage() {
  const activeInstruments = instrumentLocations.filter(i => i.status === 'active').length;
  const totalDataCollected = deploymentSchedule.reduce((sum, d) => sum + d.dataCollected, 0);
  const activeDeployments = deploymentSchedule.filter(d => d.status === 'active').length;
  
  // Animated counters
  const [animatedActiveInstruments, setAnimatedActiveInstruments] = useState(0);
  const [animatedDataCollected, setAnimatedDataCollected] = useState(0);
  const [animatedActiveDeployments, setAnimatedActiveDeployments] = useState(0);
  
  useEffect(() => {
    const animateCounter = (target: number, setter: (value: number) => void, duration = 1000) => {
      let start = 0;
      const increment = target / (duration / 16);
      const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
          setter(target);
          clearInterval(timer);
        } else {
          setter(Math.floor(start));
        }
      }, 16);
    };
    
    setTimeout(() => animateCounter(activeInstruments, setAnimatedActiveInstruments), 300);
    setTimeout(() => animateCounter(totalDataCollected, setAnimatedDataCollected), 500);
    setTimeout(() => animateCounter(activeDeployments, setAnimatedActiveDeployments), 700);
  }, [activeInstruments, totalDataCollected, activeDeployments]);

  return (
    <motion.div 
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
        >
          May River Acoustic Monitoring
        </motion.h1>
        <motion.p 
          className="text-muted-foreground mt-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
        >
          Real-time soundscape analysis across the May River ecosystem in South Carolina. 
          This dashboard presents acoustic indices, species detections, and environmental correlations 
          from our network of hydrophones and terrestrial recorders.
        </motion.p>
      </motion.div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          whileHover={{ scale: 1.05, rotateY: 5 }}
          whileTap={{ scale: 0.95 }}
        >
          <Card className="relative overflow-hidden group cursor-pointer">
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-teal-500/10 to-cyan-500/10"
              initial={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Active Instruments</CardTitle>
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotateZ: [0, 10, 0]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Activity className="h-4 w-4 text-teal-600" />
              </motion.div>
            </CardHeader>
            <CardContent className="relative z-10">
              <motion.div 
                className="text-2xl font-bold text-teal-700"
                key={animatedActiveInstruments}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                {animatedActiveInstruments}
              </motion.div>
              <p className="text-xs text-muted-foreground">
                of {instrumentLocations.length} total deployed
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          whileHover={{ scale: 1.05, rotateY: 5 }}
          whileTap={{ scale: 0.95 }}
        >
          <Card className="relative overflow-hidden group cursor-pointer">
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-blue-500/10"
              initial={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Data Collected</CardTitle>
              <motion.div
                animate={{ 
                  y: [0, -3, 0],
                  rotateX: [0, 180, 360]
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Database className="h-4 w-4 text-cyan-600" />
              </motion.div>
            </CardHeader>
            <CardContent className="relative z-10">
              <motion.div 
                className="text-2xl font-bold text-cyan-700"
                key={animatedDataCollected}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                {(animatedDataCollected / 1000).toFixed(1)}GB
              </motion.div>
              <p className="text-xs text-muted-foreground">
                Across all deployments
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          whileHover={{ scale: 1.05, rotateY: 5 }}
          whileTap={{ scale: 0.95 }}
        >
          <Card className="relative overflow-hidden group cursor-pointer">
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10"
              initial={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Active Deployments</CardTitle>
              <motion.div
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{
                  duration: 2.5,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Calendar className="h-4 w-4 text-blue-600" />
              </motion.div>
            </CardHeader>
            <CardContent className="relative z-10">
              <motion.div 
                className="text-2xl font-bold text-blue-700"
                key={animatedActiveDeployments}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
              >
                {animatedActiveDeployments}
              </motion.div>
              <p className="text-xs text-muted-foreground">
                Currently recording
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          whileHover={{ scale: 1.05, rotateY: 5 }}
          whileTap={{ scale: 0.95 }}
        >
          <Card className="relative overflow-hidden group cursor-pointer">
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10"
              initial={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
              <CardTitle className="text-sm font-medium">Study Duration</CardTitle>
              <motion.div
                animate={{ 
                  y: [0, -2, 0],
                  rotateY: [0, 360]
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <MapPin className="h-4 w-4 text-indigo-600" />
              </motion.div>
            </CardHeader>
            <CardContent className="relative z-10">
              <motion.div 
                className="text-2xl font-bold text-indigo-700"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1, type: "spring", stiffness: 200 }}
              >
                18
              </motion.div>
              <p className="text-xs text-muted-foreground">
                Months of continuous monitoring
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Instrument Locations Map */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.6 }}
          whileHover={{ scale: 1.02 }}
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
                  whileHover={{ scale: 1.2, rotate: 15 }}
                  transition={{ type: "spring", stiffness: 400 }}
                >
                  <MapPin className="h-5 w-5 text-teal-600" />
                </motion.div>
                Instrument Locations
              </CardTitle>
              <CardDescription>
                Distribution of acoustic recording devices across the May River ecosystem
              </CardDescription>
            </CardHeader>
            <CardContent className="relative z-10">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                <InstrumentMap />
              </motion.div>
              
              {/* Legend */}
              <motion.div 
                className="mt-4 space-y-2"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1 }}
              >
                <h4 className="font-medium text-sm">Instrument Status</h4>
                <div className="flex flex-wrap gap-2">
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100 cursor-pointer">
                      Active
                    </Badge>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100 cursor-pointer">
                      Maintenance
                    </Badge>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                    <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100 cursor-pointer">
                      Offline
                    </Badge>
                  </motion.div>
                </div>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Deployment Schedule */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.7 }}
          whileHover={{ scale: 1.02 }}
        >
          <Card className="relative overflow-hidden group">
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5"
              initial={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            />
            <CardHeader className="relative z-10">
              <CardTitle className="flex items-center gap-2">
                <motion.div
                  whileHover={{ scale: 1.2, rotate: -15 }}
                  transition={{ type: "spring", stiffness: 400 }}
                >
                  <Calendar className="h-5 w-5 text-blue-600" />
                </motion.div>
                Deployment Schedule
              </CardTitle>
              <CardDescription>
                Timeline of acoustic monitoring deployments and data collection periods
              </CardDescription>
            </CardHeader>
            <CardContent className="relative z-10">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.9 }}
              >
                <DeploymentGantt />
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Instrument Details Table */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.8 }}
      >
        <Card className="relative overflow-hidden group">
          <motion.div
            className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5"
            initial={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
          />
          <CardHeader className="relative z-10">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 1 }}
            >
              <CardTitle>Instrument Details</CardTitle>
              <CardDescription>
                Current status and specifications of all deployed recording systems
              </CardDescription>
            </motion.div>
          </CardHeader>
          <CardContent className="relative z-10">
            <motion.div 
              className="overflow-x-auto"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1.1 }}
            >
              <table className="w-full text-sm">
                <motion.thead
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 1.2 }}
                >
                  <tr className="border-b">
                    <th className="text-left p-2">ID</th>
                    <th className="text-left p-2">Location</th>
                    <th className="text-left p-2">Type</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-left p-2">Deployed</th>
                    <th className="text-left p-2">Last Sync</th>
                  </tr>
                </motion.thead>
                <tbody>
                  {instrumentLocations.map((instrument, index) => (
                    <motion.tr 
                      key={instrument.id} 
                      className="border-b hover:bg-teal-50/50 transition-colors"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 1.3 + index * 0.05 }}
                      whileHover={{ scale: 1.01, backgroundColor: "rgba(20, 184, 166, 0.05)" }}
                    >
                      <td className="p-2 font-mono">{instrument.id}</td>
                      <td className="p-2">{instrument.name}</td>
                      <td className="p-2 capitalize">{instrument.type}</td>
                      <td className="p-2">
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Badge 
                            variant={
                              instrument.status === 'active' ? 'default' : 
                              instrument.status === 'maintenance' ? 'secondary' : 'outline'
                            }
                            className={`cursor-pointer ${
                              instrument.status === 'active' ? 'bg-green-100 text-green-800 hover:bg-green-100' :
                              instrument.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100' :
                              'bg-gray-100 text-gray-800 hover:bg-gray-100'
                            }`}
                          >
                            {instrument.status}
                          </Badge>
                        </motion.div>
                      </td>
                      <td className="p-2">{new Date(instrument.deploymentDate).toLocaleDateString()}</td>
                      <td className="p-2">{new Date(instrument.lastDataSync).toLocaleDateString()}</td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}