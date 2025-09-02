'use client';

import { useViewData } from '@/lib/data/useViewData';
import { StationsData, DatasetsData } from '@/types/data';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { 
  Map, 
  MapPin, 
  TrendingUp, 
  Calendar,
  Waves,
  Fish,
  Volume2,
  Thermometer,
  BarChart3,
  FileText
} from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamically import the map to avoid SSR issues with Mapbox
const StationMap = dynamic(
  () => import('@/components/maps/StationMap'),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-[500px] bg-muted animate-pulse rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-muted-foreground">Loading map...</p>
        </div>
      </div>
    )
  }
);

export default function DataPage() {
  const { data: stationsData, loading: stationsLoading } = useViewData<StationsData>('stations.json');
  const { data: datasetsData, loading: datasetsLoading } = useViewData<DatasetsData>('datasets_summary.json');

  const loading = stationsLoading || datasetsLoading;

  // Define the 3 main analysis stations
  const analysisStationIds = ['9M', '14M', '37M'];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            animate={{ 
              rotateY: [0, 15, 0, -15, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="inline-block"
          >
            <Waves className="h-12 w-12 text-primary mx-auto mb-4" />
          </motion.div>
          <p className="text-muted-foreground">Loading data...</p>
        </motion.div>
      </div>
    );
  }

  // Filter stations to only the 3 analysis stations
  const analysisStations = stationsData?.stations.filter(s => analysisStationIds.includes(s.id)) || [];

  // Calculate stats from the data
  const acousticIndicesCount = 56; // From project description
  const totalRecords = datasetsData?.summary.total_records || 0;
  const stations = stationsData?.summary.total_stations || 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold mb-4">Data Overview</h1>
          <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mb-6"></div>
        </motion.div>

        {/* Stats Cards */}
        <motion.div 
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <MapPin className="h-4 w-4 text-primary" />
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Analysis Stations</span>
              </div>
              <p className="text-2xl font-bold">3</p>
              <p className="text-xs text-muted-foreground">of {stations} total</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="h-4 w-4 text-chart-1" />
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Years</span>
              </div>
              <p className="text-2xl font-bold">2</p>
              <p className="text-xs text-muted-foreground">2018, 2021</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Fish className="h-4 w-4 text-chart-2" />
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Species</span>
              </div>
              <p className="text-2xl font-bold">15+</p>
              <p className="text-xs text-muted-foreground">Detected</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-chart-3" />
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Indices</span>
              </div>
              <p className="text-2xl font-bold">{acousticIndicesCount}</p>
              <p className="text-xs text-muted-foreground">Acoustic</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <Thermometer className="h-4 w-4 text-chart-4" />
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Environmental</span>
              </div>
              <p className="text-2xl font-bold">2</p>
              <p className="text-xs text-muted-foreground">Temp, Depth</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-accent-foreground" />
                <span className="text-xs text-muted-foreground uppercase tracking-wider">Records</span>
              </div>
              <p className="text-2xl font-bold">{(totalRecords / 1000).toFixed(0)}K</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Station Map */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-12"
        >
          <Card className="shadow-xl border-0 bg-card/95 backdrop-blur-sm overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-accent/50 to-accent/30 border-b">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Map className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Monitoring Station Locations</CardTitle>
                  <CardDescription className="text-base mt-1">
                    Three primary hydrophone monitoring stations in May River, SC (9M, 14M, 37M) with additional regional context stations.
                    Toggle between Study Area view (3 stations) and All Stations view.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {stationsData && (
                <StationMap 
                  stations={stationsData.stations} 
                  height="500px"
                  className="rounded-b-xl"
                  focusStations={analysisStationIds}
                />
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Station Information - filtered to only show 3 analysis stations */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
            <MapPin className="h-7 w-7 text-primary" />
            Analysis Stations
          </h2>
          <Card className="overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-accent/20 to-accent/10">
              <CardTitle>Station Details & Data Availability</CardTitle>
              <CardDescription>
                The three primary hydrophone monitoring stations used for acoustic analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <div className="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x">
                {analysisStations.map((station, index) => (
                  <motion.div 
                    key={station.id}
                    className="p-6 hover:bg-accent/10 transition-colors"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <div className="p-2 bg-primary/10 rounded-lg">
                        <Waves className="h-5 w-5 text-primary" />
                      </div>
                      <h3 className="font-semibold text-lg">{station.name}</h3>
                    </div>
                    <div className="space-y-3 text-sm">
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <span className="text-muted-foreground text-xs uppercase tracking-wide">Platform</span>
                          <p className="font-medium">{station.platform}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground text-xs uppercase tracking-wide">Depth</span>
                          <p className="font-medium">{station.depth_m ? `${Math.abs(station.depth_m).toFixed(1)}m` : 'N/A'}</p>
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground text-xs uppercase tracking-wide">Deployments</span>
                        <p className="font-medium">{station.deployment_periods.length}</p>
                      </div>
                      <div className="pt-2 border-t">
                        <span className="text-muted-foreground text-xs uppercase tracking-wide block mb-2">Data Available</span>
                        <div className="flex flex-wrap gap-2">
                          {station.data_availability.detection_data && (
                            <span className="bg-chart-1/20 text-chart-1 px-2 py-1 rounded-full text-xs font-medium border border-chart-1/30">
                              Detections
                            </span>
                          )}
                          {station.data_availability.acoustic_indices && (
                            <span className="bg-primary/20 text-primary px-2 py-1 rounded-full text-xs font-medium border border-primary/30">
                              Indices
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Merged Dataset Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mb-12"
        >
          <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
            <FileText className="h-7 w-7 text-primary" />
            Data Types & Datasets
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* Manual Detections */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 }}
              whileHover={{ y: -4 }}
            >
              <Card className="h-full group hover:shadow-xl transition-all duration-300 border-l-4 border-l-primary">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 group-hover:text-primary transition-colors">
                    <Volume2 className="h-5 w-5 text-primary" />
                    Manual Detections
                  </CardTitle>
                  <CardDescription className="text-sm leading-relaxed">
                    Species and sound type annotations from manual analysis of acoustic recordings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-1">
                      <span className="text-muted-foreground text-xs uppercase tracking-wide">Records</span>
                      <p className="font-medium text-lg">{datasetsData?.datasets.find(d => d.id === 'detections')?.record_count.toLocaleString() || 'N/A'}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-muted-foreground text-xs uppercase tracking-wide">Resolution</span>
                      <p className="font-medium">{datasetsData?.datasets.find(d => d.id === 'detections')?.temporal_resolution || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <span className="text-muted-foreground text-xs uppercase tracking-wide block mb-2">Categories</span>
                    <ul className="space-y-1 text-xs text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-primary rounded-full"></div>
                        Fish vocalizations
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-primary rounded-full"></div>
                        Marine mammal sounds
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-primary rounded-full"></div>
                        Environmental noise
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-primary rounded-full"></div>
                        Anthropogenic sounds
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Acoustic Indices */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.7 }}
              whileHover={{ y: -4 }}
            >
              <Card className="h-full group hover:shadow-xl transition-all duration-300 border-l-4 border-l-chart-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 group-hover:text-chart-2 transition-colors">
                    <BarChart3 className="h-5 w-5 text-chart-2" />
                    Acoustic Indices
                  </CardTitle>
                  <CardDescription className="text-sm leading-relaxed">
                    Computed soundscape metrics derived from audio analysis algorithms
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-1">
                      <span className="text-muted-foreground text-xs uppercase tracking-wide">Records</span>
                      <p className="font-medium text-lg">{datasetsData?.datasets.find(d => d.id === 'acoustic_indices')?.record_count.toLocaleString() || 'N/A'}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-muted-foreground text-xs uppercase tracking-wide">Resolution</span>
                      <p className="font-medium">{datasetsData?.datasets.find(d => d.id === 'acoustic_indices')?.temporal_resolution || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <span className="text-muted-foreground text-xs uppercase tracking-wide block mb-2">Index Types</span>
                    <ul className="space-y-1 text-xs text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-2 rounded-full"></div>
                        Temporal domain (6 indices)
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-2 rounded-full"></div>
                        Frequency domain (5 indices)
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-2 rounded-full"></div>
                        Acoustic complexity (4 indices)
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-2 rounded-full"></div>
                        Diversity indices (15+ indices)
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Environmental Data */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              whileHover={{ y: -4 }}
            >
              <Card className="h-full group hover:shadow-xl transition-all duration-300 border-l-4 border-l-chart-3">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 group-hover:text-chart-3 transition-colors">
                    <Thermometer className="h-5 w-5 text-chart-3" />
                    Environmental Data
                  </CardTitle>
                  <CardDescription className="text-sm leading-relaxed">
                    Physical oceanographic measurements from in-situ sensors
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-1">
                      <span className="text-muted-foreground text-xs uppercase tracking-wide">Records</span>
                      <p className="font-medium text-lg">{datasetsData?.datasets.find(d => d.id === 'environmental')?.record_count.toLocaleString() || 'N/A'}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-muted-foreground text-xs uppercase tracking-wide">Resolution</span>
                      <p className="font-medium">{datasetsData?.datasets.find(d => d.id === 'environmental')?.temporal_resolution || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <span className="text-muted-foreground text-xs uppercase tracking-wide block mb-2">Measurements</span>
                    <ul className="space-y-1 text-xs text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-3 rounded-full"></div>
                        Water temperature
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-3 rounded-full"></div>
                        Depth measurements
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-3 rounded-full"></div>
                        Hourly resolution
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1 h-1 bg-chart-3 rounded-full"></div>
                        Station-specific data
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </motion.div>

        {/* Project Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mb-12"
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl flex items-center gap-3">
                <Waves className="h-6 w-6 text-primary" />
                Project Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2 text-lg">Data Collection</h3>
                <p className="text-muted-foreground leading-relaxed">
                  This dashboard presents marine acoustic data collected at three monitoring stations in May River, South Carolina, 
                  during two study periods: 2018 and 2021. The current analysis focuses primarily on the 2021 dataset, which includes 
                  comprehensive acoustic indices computed from the raw hydrophone recordings.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2 text-lg">Manual Detections</h3>
                <p className="text-muted-foreground leading-relaxed">
                  The dataset includes manual annotations of various acoustic events, categorized into four main groups:
                  fish vocalizations (silver perch, oyster toadfish, etc.), marine mammal sounds (bottlenose dolphin echolocation and clicks),
                  environmental noise (rain, wind, waves), and anthropogenic sounds (boat engines, sonar). These manual detections 
                  serve as ground truth data for our analysis.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2 text-lg">Acoustic Indices</h3>
                <p className="text-muted-foreground leading-relaxed">
                  Approximately 60 acoustic indices have been computed from the raw audio data, spanning multiple categories including 
                  temporal domain metrics, frequency domain characteristics, acoustic complexity measures, diversity indices, 
                  bioacoustic indicators, and spectral coverage metrics. These indices capture different aspects of the underwater 
                  soundscape and its ecological properties.
                </p>
              </div>

              <div className="bg-accent/10 p-4 rounded-lg border border-accent/20">
                <h3 className="font-semibold mb-2 text-lg flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Research Goal
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  The primary objective is to determine whether computed acoustic indices can serve as effective proxies for 
                  biodiversity monitoring. By correlating these automated metrics with manual species detections, we aim to 
                  develop a more efficient method for marine biodiversity assessment. If successful, acoustic indices could 
                  indicate where to focus manual detection efforts, significantly reducing the time and resources required 
                  for comprehensive marine ecosystem monitoring.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}