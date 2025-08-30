'use client';

import { useViewData } from '@/lib/data/useViewData';
import { ProjectMetadata, StationsData, DatasetsData } from '@/types/data';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'framer-motion';
import { Map, FileText, TrendingUp, Waves, Activity, MapPin } from 'lucide-react';
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

export default function Home() {
  const { data: projectData, loading: projectLoading } = useViewData<ProjectMetadata>('project_metadata.json');
  const { data: stationsData, loading: stationsLoading } = useViewData<StationsData>('stations.json');
  const { data: datasetsData, loading: datasetsLoading } = useViewData<DatasetsData>('datasets_summary.json');

  const loading = projectLoading || stationsLoading || datasetsLoading;

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
          <p className="text-muted-foreground">Loading dashboard...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-primary via-primary/90 to-chart-3 text-primary-foreground pb-24 pt-8 overflow-hidden">
        {/* Animated background pattern */}
        <motion.div
          className="absolute inset-0 opacity-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.1 }}
          transition={{ duration: 2 }}
        >
          <div 
            className="absolute inset-0" 
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fillRule='evenodd'%3E%3Cg fill='%23ffffff' fillOpacity='0.4'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }}
          />
        </motion.div>
        
        <div className="container mx-auto px-4 py-16 relative">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center"
          >
            <div className="flex items-center justify-center gap-3 mb-6">
              <motion.div
                animate={{ 
                  rotateY: [0, 15, 0, -15, 0],
                }}
                transition={{
                  duration: 6,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Waves className="h-8 w-8 text-accent-foreground" />
              </motion.div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-black tracking-tight font-[family-name:var(--font-inter-tight)]">
                {projectData?.project.title || 'MBON Marine Biodiversity Dashboard'}
              </h1>
            </div>
            <p className="text-xl md:text-2xl text-primary-foreground/95 mb-12 max-w-3xl font-light mx-auto">
              {projectData?.project.subtitle || 'Exploring Acoustic Indices as Marine Biodiversity Predictors'}
            </p>
          </motion.div>

          <motion.div 
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.div 
              className="bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20 rounded-xl px-4 py-4 min-w-0"
              whileHover={{ scale: 1.02, y: -2 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <div className="flex items-center gap-2 mb-2">
                <MapPin className="h-4 w-4 text-accent-foreground flex-shrink-0" />
                <span className="text-primary-foreground/80 text-xs font-light uppercase tracking-wider truncate">Monitoring Stations</span>
              </div>
              <p className="text-4xl font-black text-primary-foreground">{stationsData?.summary.total_stations || 0}</p>
            </motion.div>
            
            <motion.div 
              className="bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20 rounded-xl px-4 py-4 min-w-0"
              whileHover={{ scale: 1.02, y: -2 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-accent-foreground flex-shrink-0" />
                <span className="text-primary-foreground/80 text-xs font-light uppercase tracking-wider truncate">Study Years</span>
              </div>
              <p className="text-4xl font-black text-primary-foreground">
                {stationsData?.summary.years_covered.join(', ') || 'N/A'}
              </p>
            </motion.div>
            
            <motion.div 
              className="bg-primary-foreground/10 backdrop-blur-sm border border-primary-foreground/20 rounded-xl px-4 py-4 min-w-0"
              whileHover={{ scale: 1.02, y: -2 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-accent-foreground flex-shrink-0" />
                <span className="text-primary-foreground/80 text-xs font-light uppercase tracking-wider truncate">Total Records</span>
              </div>
              <p className="text-4xl font-black text-primary-foreground">
                {datasetsData?.summary.total_records.toLocaleString() || 0}
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Station Map - Prominent placement right after hero */}
      <div className="container mx-auto px-4 -mt-16 relative z-10 mb-16">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <Card className="shadow-2xl border-0 bg-card/95 backdrop-blur-sm overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-accent/50 to-accent/30 border-b">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Map className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Monitoring Station Locations</CardTitle>
                  <CardDescription className="text-base mt-1">
                    Interactive map showing the three hydrophone monitoring stations off the South Carolina coast. 
                    Click on stations for detailed information.
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
                />
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Research Context */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">Research Context</h2>
            <div className="w-24 h-1 bg-gradient-to-r from-primary to-accent-foreground mx-auto"></div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card className="mb-12 overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-accent/20 to-accent/10">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-primary/10 rounded-xl">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-xl mb-2">Primary Research Question</CardTitle>
                    <CardDescription className="text-base">
                      {projectData?.research_context.primary_question}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground leading-relaxed">
                  {projectData?.research_context.significance}
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Research Objectives */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="mb-16"
          >
            <h3 className="text-2xl font-bold mb-8 flex items-center gap-3">
              <TrendingUp className="h-6 w-6 text-primary" />
              Research Objectives
            </h3>
            <div className="grid gap-6">
              {projectData?.research_context.objectives.map((objective, index) => (
                <motion.div
                  key={objective.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                >
                  <Card className="group hover:shadow-lg transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-lg mb-2">{objective.title}</h4>
                          <p className="text-muted-foreground leading-relaxed">{objective.description}</p>
                        </div>
                        <div className={`px-3 py-1 text-xs font-medium rounded-full ml-6 ${
                          objective.status === 'in_progress' 
                            ? 'bg-chart-4/20 text-chart-4 border border-chart-4/30'
                            : 'bg-muted text-muted-foreground border border-border'
                        }`}>
                          {objective.status.replace('_', ' ')}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Dataset Summary */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="mb-16"
          >
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
              <FileText className="h-7 w-7 text-primary" />
              Available Datasets
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              {datasetsData?.datasets.map((dataset, index) => (
                <motion.div
                  key={dataset.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
                  whileHover={{ y: -4 }}
                >
                  <Card className="h-full group hover:shadow-xl transition-all duration-300 border-l-4 border-l-primary/50">
                    <CardHeader>
                      <CardTitle className="text-lg group-hover:text-primary transition-colors">
                        {dataset.name}
                      </CardTitle>
                      <CardDescription className="text-sm leading-relaxed">
                        {dataset.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="space-y-1">
                          <span className="text-muted-foreground text-xs uppercase tracking-wide">Records</span>
                          <p className="font-medium text-lg">{dataset.record_count.toLocaleString()}</p>
                        </div>
                        <div className="space-y-1">
                          <span className="text-muted-foreground text-xs uppercase tracking-wide">Resolution</span>
                          <p className="font-medium">{dataset.temporal_resolution}</p>
                        </div>
                      </div>
                      <div className="pt-2 border-t">
                        <div className="flex items-center justify-between">
                          <span className="text-muted-foreground text-xs uppercase tracking-wide">Type</span>
                          <span className="px-2 py-1 bg-primary/10 text-primary text-xs rounded-full font-medium">
                            {dataset.data_type.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Station Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          >
            <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
              <MapPin className="h-7 w-7 text-primary" />
              Monitoring Stations
            </h2>
            <Card className="overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-accent/20 to-accent/10">
                <CardTitle>Station Details & Data Availability</CardTitle>
                <CardDescription>
                  Comprehensive overview of each hydrophone monitoring station and available data types
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x">
                  {stationsData?.stations.map((station, index) => (
                    <motion.div 
                      key={station.id}
                      className="p-6 hover:bg-accent/10 transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 1.0 + index * 0.1 }}
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
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-muted/50 mt-20 border-t">
        <div className="container mx-auto px-4 py-12">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.2 }}
          >
            <div className="flex items-center justify-center gap-2 mb-4">
              <Waves className="h-5 w-5 text-primary" />
              <p className="font-medium">{projectData?.project.organization}</p>
            </div>
            <p className="text-muted-foreground text-sm">
              Data generated: {new Date(projectData?.metadata.generated_at || '').toLocaleDateString()}
            </p>
          </motion.div>
        </div>
      </footer>
    </div>
  );
}