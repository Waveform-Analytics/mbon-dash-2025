'use client';

import { motion } from 'framer-motion';
import { BookOpen, Users, MapPin, Calendar, Award, ExternalLink, FileText, Target } from 'lucide-react';

export default function BackgroundPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl font-bold text-primary mb-2">Background</h1>
          <div className="h-1 w-20 bg-primary rounded mb-8"></div>
        </motion.div>

        {/* Project Overview */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-12"
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-card rounded-lg shadow-lg border p-8">
              <div className="flex items-center mb-6">
                <Target className="h-8 w-8 text-primary mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Project Overview</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                The ESONS (Ecoacoustic Surveillance of Ocean Networks) project investigates whether acoustic indices 
                can serve as effective proxies for marine biodiversity monitoring. This interdisciplinary research 
                combines marine biology, acoustic ecology, and computational science.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-chart-1 rounded-full mr-3"></div>
                  <span className="text-sm">Automated acoustic monitoring of marine environments</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-chart-2 rounded-full mr-3"></div>
                  <span className="text-sm">Species detection and biodiversity assessment</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-chart-3 rounded-full mr-3"></div>
                  <span className="text-sm">Machine learning for pattern recognition</span>
                </div>
              </div>
            </div>

            <div className="bg-card rounded-lg shadow-lg border p-8">
              <div className="flex items-center mb-6">
                <MapPin className="h-8 w-8 text-primary mr-3" />
                <h2 className="text-2xl font-bold text-card-foreground">Study Location</h2>
              </div>
              <p className="text-muted-foreground mb-6">
                Research conducted in the May River estuary, South Carolina, utilizing three strategically 
                positioned hydrophone monitoring stations at different depths to capture diverse acoustic 
                environments and marine life.
              </p>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Station 9M:</span>
                  <span className="text-sm font-medium">Shallow water monitoring</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Station 14M:</span>
                  <span className="text-sm font-medium">Mid-depth observations</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Station 37M:</span>
                  <span className="text-sm font-medium">Deep water analysis</span>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Research Timeline */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <Calendar className="h-8 w-8 text-primary mr-3" />
            <h2 className="text-2xl font-bold text-card-foreground">Research Timeline</h2>
          </div>
          <div className="bg-card rounded-lg shadow-lg border p-8">
            <div className="space-y-6">
              {[
                {
                  year: "2018",
                  title: "Initial Data Collection",
                  description: "First year of continuous acoustic monitoring with manual species detection protocols established.",
                  status: "completed"
                },
                {
                  year: "2019-2020",
                  title: "Methodology Development",
                  description: "Refinement of acoustic analysis techniques and expansion of species identification protocols.",
                  status: "completed"
                },
                {
                  year: "2021",
                  title: "Extended Monitoring",
                  description: "Second major data collection period with enhanced acoustic index calculations.",
                  status: "completed"
                },
                {
                  year: "2022-2024",
                  title: "Analysis & Modeling",
                  description: "Computational analysis, machine learning model development, and pattern recognition studies.",
                  status: "in-progress"
                },
                {
                  year: "2025",
                  title: "Publication & Dissemination",
                  description: "Results publication, dashboard development, and research community engagement.",
                  status: "current"
                }
              ].map((phase, index) => (
                <motion.div
                  key={phase.year}
                  className="flex items-start"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.6 + index * 0.1 }}
                >
                  <div className={`flex-shrink-0 w-16 h-16 rounded-full flex items-center justify-center text-sm font-bold ${
                    phase.status === 'completed' ? 'bg-green-100 text-green-800' :
                    phase.status === 'current' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {phase.year}
                  </div>
                  <div className="ml-4 flex-1">
                    <h3 className="font-semibold text-card-foreground mb-1">{phase.title}</h3>
                    <p className="text-sm text-muted-foreground">{phase.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Research Team */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <Users className="h-8 w-8 text-primary mr-3" />
            <h2 className="text-2xl font-bold text-card-foreground">Research Team</h2>
          </div>
          <div className="bg-card rounded-lg shadow-lg border p-8">
            <p className="text-muted-foreground mb-8 text-center">
              Interdisciplinary collaboration between marine scientists, acoustic ecologists, and data scientists 
              at the University of South Carolina and partner institutions.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  role: "Principal Investigator",
                  department: "Marine Science Program",
                  institution: "University of South Carolina",
                  focus: "Marine biodiversity and ecosystem monitoring"
                },
                {
                  role: "Acoustic Ecologist",
                  department: "Biological Sciences",
                  institution: "USC",
                  focus: "Bioacoustic analysis and species identification"
                },
                {
                  role: "Data Scientist",
                  department: "Computer Science",
                  institution: "USC",
                  focus: "Machine learning and pattern recognition"
                },
                {
                  role: "Research Coordinator",
                  department: "ESONS Project",
                  institution: "USC",
                  focus: "Field operations and data management"
                },
                {
                  role: "Graduate Researchers",
                  department: "Multiple Departments",
                  institution: "USC",
                  focus: "Specialized analysis and method development"
                },
                {
                  role: "Collaborating Partners",
                  department: "External Institutions",
                  institution: "Various",
                  focus: "Expertise and resource sharing"
                }
              ].map((member, index) => (
                <motion.div
                  key={member.role}
                  className="bg-muted rounded-lg p-4 border"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 1.0 + index * 0.1 }}
                  whileHover={{ y: -2, transition: { duration: 0.2 } }}
                >
                  <h4 className="font-semibold text-sm mb-1">{member.role}</h4>
                  <p className="text-xs text-muted-foreground mb-1">{member.department}</p>
                  <p className="text-xs text-primary mb-2">{member.institution}</p>
                  <p className="text-xs text-muted-foreground">{member.focus}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Methodology & Approach */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="mb-12"
        >
          <div className="flex items-center mb-6">
            <BookOpen className="h-8 w-8 text-primary mr-3" />
            <h2 className="text-2xl font-bold text-card-foreground">Methodology & Approach</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-card rounded-lg shadow-lg border p-6">
              <h3 className="text-xl font-semibold mb-4">Data Collection</h3>
              <div className="space-y-3">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-1 rounded-full mr-3"></div>
                  <span className="text-sm">Continuous 24/7 acoustic monitoring</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-2 rounded-full mr-3"></div>
                  <span className="text-sm">High-frequency sampling (48kHz)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-3 rounded-full mr-3"></div>
                  <span className="text-sm">Environmental parameter logging</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-4 rounded-full mr-3"></div>
                  <span className="text-sm">Manual species verification protocols</span>
                </div>
              </div>
            </div>

            <div className="bg-card rounded-lg shadow-lg border p-6">
              <h3 className="text-xl font-semibold mb-4">Analysis Framework</h3>
              <div className="space-y-3">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-1 rounded-full mr-3"></div>
                  <span className="text-sm">56+ acoustic indices calculation</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-2 rounded-full mr-3"></div>
                  <span className="text-sm">Temporal pattern analysis</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-3 rounded-full mr-3"></div>
                  <span className="text-sm">Machine learning classification</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-chart-4 rounded-full mr-3"></div>
                  <span className="text-sm">Cross-validation and testing</span>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Publications & Resources */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.4 }}
        >
          <div className="flex items-center mb-6">
            <FileText className="h-8 w-8 text-primary mr-3" />
            <h2 className="text-2xl font-bold text-card-foreground">Publications & Resources</h2>
          </div>
          <div className="bg-card rounded-lg shadow-lg border p-8">
            <p className="text-muted-foreground mb-8 text-center">
              Research outputs, publications, and resources related to the ESONS project and marine acoustic monitoring.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  type: "Journal Article",
                  title: "Acoustic Indices as Marine Biodiversity Proxies",
                  status: "In Preparation",
                  venue: "Marine Ecology Progress Series"
                },
                {
                  type: "Conference Paper",
                  title: "Machine Learning for Marine Soundscape Analysis",
                  status: "Under Review",
                  venue: "IEEE ICASSP 2025"
                },
                {
                  type: "Dataset",
                  title: "May River Acoustic Monitoring Dataset",
                  status: "Available",
                  venue: "ESONS Data Repository"
                },
                {
                  type: "Software",
                  title: "Marine Acoustic Analysis Toolkit",
                  status: "Development",
                  venue: "GitHub Repository"
                },
                {
                  type: "Presentation",
                  title: "ESONS Project Overview",
                  status: "Available",
                  venue: "Marine Biology Conference 2024"
                },
                {
                  type: "Technical Report",
                  title: "Methodology and Preliminary Findings",
                  status: "Draft",
                  venue: "USC Technical Reports"
                }
              ].map((publication, index) => (
                <motion.div
                  key={publication.title}
                  className="bg-muted rounded-lg p-4 border"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: 1.6 + index * 0.1 }}
                  whileHover={{ y: -2, transition: { duration: 0.2 } }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="px-2 py-1 bg-primary/20 text-primary text-xs font-medium rounded-full">
                      {publication.type}
                    </span>
                    <ExternalLink className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <h4 className="font-semibold text-sm mb-2">{publication.title}</h4>
                  <p className="text-xs text-muted-foreground mb-1">{publication.venue}</p>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    publication.status === 'Available' ? 'bg-green-100 text-green-800' :
                    publication.status === 'Under Review' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {publication.status}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}