import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { TrendingUp, Calendar, MapPin, Lightbulb, ArrowRight } from 'lucide-react';
import { SoundWaveAnimation, FloatingParticles } from './LoadingSpinner';
import { SeasonalTrendsChart } from './charts/SeasonalTrendsChart';
import { CorrelationMatrix } from './charts/CorrelationMatrix';
import { InstrumentComparisonChart } from './charts/InstrumentComparisonChart';
import { TimeSeriesChart } from './charts/TimeSeriesChart';
import { acousticIndices, instrumentLocations, annotatedEvents } from '../data/mockData';

export function AnalysisPage() {
  const [selectedIndex, setSelectedIndex] = useState('aci');
  const [currentStep, setCurrentStep] = useState(0);

  const analysisSteps = [
    {
      title: "Seasonal Patterns in Acoustic Complexity",
      description: "Our analysis reveals strong seasonal variations in soundscape complexity across all instruments.",
      component: "seasonal"
    },
    {
      title: "Cross-Correlation Between Indices",
      description: "Understanding how different acoustic measures relate to each other provides insights into ecosystem dynamics.",
      component: "correlation"
    },
    {
      title: "Spatial Variations Across Instruments",
      description: "Each monitoring location shows unique acoustic characteristics influenced by habitat type and human proximity.",
      component: "spatial"
    },
    {
      title: "Environmental Drivers of Acoustic Activity",
      description: "Temperature, humidity, and wind patterns significantly influence biological acoustic activity.",
      component: "environmental"
    }
  ];

  const insights = [
    {
      title: "Spring Migration Peak",
      description: "ACI values show a 40% increase during April-May, coinciding with migratory bird arrivals",
      metric: "ACI: 65-85 range",
      trend: "↗️ +40%"
    },
    {
      title: "Tidal Influence on Marine Acoustics",
      description: "Hydrophone data reveals 6-hour cyclical patterns matching tidal schedules",
      metric: "BI: 2.1-4.8 cycle",
      trend: "🌊 Periodic"
    },
    {
      title: "Dawn Chorus Dominance",
      description: "ADI peaks consistently between 5:30-7:00 AM across all terrestrial sites",
      metric: "ADI: 0.8-0.95 peak",
      trend: "⏰ Daily"
    },
    {
      title: "Habitat-Specific Signatures",
      description: "Combined systems show intermediate values, bridging terrestrial and aquatic patterns",
      metric: "NDSI: 0.2-0.6 range",
      trend: "🔀 Gradient"
    }
  ];

  return (
    <motion.div 
      className="space-y-8 relative"
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
            Acoustic Analysis & Discovery
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
          A narrative exploration of soundscape patterns, correlations, and ecological insights 
          from 18 months of continuous acoustic monitoring in the May River ecosystem.
        </motion.p>
      </motion.div>

      {/* Key Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative z-10">
        {insights.map((insight, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
            whileTap={{ scale: 0.95 }}
          >
            <Card className="relative overflow-hidden group cursor-pointer h-full">
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-yellow-500/10 to-orange-500/10"
                initial={{ scale: 0, opacity: 0 }}
                whileHover={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.3 }}
              />
              <CardHeader className="pb-3 relative z-10">
                <div className="flex items-start justify-between">
                  <motion.div
                    animate={{ 
                      rotateY: [0, 10, 0, -10, 0],
                      scale: [1, 1.1, 1]
                    }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: "easeInOut",
                      delay: index * 0.5
                    }}
                  >
                    <Lightbulb className="h-5 w-5 text-yellow-500" />
                  </motion.div>
                  <motion.div
                    whileHover={{ scale: 1.05, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 400 }}
                  >
                    <Badge variant="outline" className="text-xs hover:bg-yellow-50">
                      {insight.trend}
                    </Badge>
                  </motion.div>
                </div>
                <CardTitle className="text-base group-hover:text-yellow-700 transition-colors">
                  {insight.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="relative z-10">
                <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                <motion.div 
                  className="text-xs font-mono bg-muted p-2 rounded group-hover:bg-yellow-50 transition-colors"
                  whileHover={{ scale: 1.02 }}
                >
                  {insight.metric}
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Navigation Steps */}
      <motion.div 
        className="flex flex-wrap gap-2 relative z-10"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1 }}
      >
        {analysisSteps.map((step, index) => (
          <motion.div
            key={index}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button
              variant={currentStep === index ? "default" : "outline"}
              size="sm"
              onClick={() => setCurrentStep(index)}
              className={`text-xs transition-all duration-200 ${
                currentStep === index 
                  ? "bg-teal-600 hover:bg-teal-700 shadow-lg shadow-teal-500/25" 
                  : "hover:bg-teal-50 hover:border-teal-300"
              }`}
            >
              {index + 1}. {step.title.split(' ')[0]} {step.title.split(' ')[1]}
            </Button>
          </motion.div>
        ))}
      </motion.div>

      {/* Current Analysis Step */}
      <Card className="min-h-[600px]">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-primary text-primary-foreground w-6 h-6 rounded-full flex items-center justify-center text-sm">
                  {currentStep + 1}
                </span>
                {analysisSteps[currentStep].title}
              </CardTitle>
              <CardDescription className="mt-2">
                {analysisSteps[currentStep].description}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                disabled={currentStep === 0}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep(Math.min(analysisSteps.length - 1, currentStep + 1))}
                disabled={currentStep === analysisSteps.length - 1}
              >
                Next <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {currentStep === 0 && (
            <div className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Discovery: Seasonal Acoustic Rhythms</h4>
                <p className="text-blue-800 text-sm">
                  The May River soundscape follows predictable seasonal patterns, with spring showing the highest 
                  acoustic complexity due to migratory species arrivals. Summer maintains moderate activity, 
                  while winter shows the lowest diversity indices.
                </p>
              </div>
              <SeasonalTrendsChart data={acousticIndices} selectedIndex={selectedIndex} />
              <div className="flex gap-4 items-center">
                <label className="text-sm font-medium">Explore Index:</label>
                <Select value={selectedIndex} onValueChange={setSelectedIndex}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="aci">Acoustic Complexity Index</SelectItem>
                    <SelectItem value="adi">Acoustic Diversity Index</SelectItem>
                    <SelectItem value="aei">Acoustic Evenness Index</SelectItem>
                    <SelectItem value="bi">Bioacoustic Index</SelectItem>
                    <SelectItem value="ndsi">NDSI</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">Discovery: Index Relationships</h4>
                <p className="text-green-800 text-sm">
                  Strong positive correlations exist between ACI and BI (r=0.73), indicating that complex 
                  soundscapes typically contain more biological activity. NDSI shows negative correlation 
                  with most indices near human-impacted areas, confirming its utility as an anthropogenic impact measure.
                </p>
              </div>
              <CorrelationMatrix data={acousticIndices} />
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-semibold text-purple-900 mb-2">Discovery: Habitat-Specific Patterns</h4>
                <p className="text-purple-800 text-sm">
                  Terrestrial sites (MR003, MR005) show distinct dawn and dusk peaks, while hydrophone 
                  locations (MR001, MR004) exhibit more consistent activity throughout the day. 
                  Combined systems capture the full spectrum of ecosystem interactions.
                </p>
              </div>
              <InstrumentComparisonChart data={acousticIndices} instruments={instrumentLocations} />
            </div>
          )}

          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-semibold text-orange-900 mb-2">Discovery: Environmental Correlations</h4>
                <p className="text-orange-800 text-sm">
                  Temperature shows the strongest correlation with acoustic activity (r=0.67 with ACI), 
                  while wind speed above 15 m/s significantly reduces all acoustic indices. 
                  Humidity between 70-85% appears optimal for acoustic diversity.
                </p>
              </div>
              <TimeSeriesChart data={acousticIndices} selectedIndex={selectedIndex} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Annotation Integration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Species Detection Integration
          </CardTitle>
          <CardDescription>
            How manual annotations correlate with acoustic index patterns
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3">Recent Detections</h4>
              <div className="space-y-3">
                {annotatedEvents.slice(0, 4).map((event) => (
                  <div key={event.id} className="flex items-center gap-3 p-3 bg-muted rounded">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <div className="flex-1">
                      <div className="font-medium text-sm">{event.species}</div>
                      <div className="text-xs text-muted-foreground">
                        {event.date} at {event.time} • {event.instrumentId}
                      </div>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {Math.round(event.confidence * 100)}%
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-3">Pattern Validation</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                  <span className="font-medium text-green-900">Dolphin detections</span>
                  <div className="text-right text-green-800">
                    <div className="font-bold">89%</div>
                    <div className="text-xs">correlation with BI peaks</div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                  <span className="font-medium text-blue-900">Bird chorus events</span>
                  <div className="text-right text-blue-800">
                    <div className="font-bold">94%</div>
                    <div className="text-xs">correlation with ADI peaks</div>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded">
                  <span className="font-medium text-purple-900">Fish vocalizations</span>
                  <div className="text-right text-purple-800">
                    <div className="font-bold">76%</div>
                    <div className="text-xs">correlation with ACI</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Research Implications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Research Implications & Future Directions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-3 text-green-700">Conservation Insights</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Critical dawn chorus periods need protection from human disturbance</li>
                <li>• Tidal zone restoration shows measurable acoustic recovery</li>
                <li>• Combined monitoring reveals ecosystem connectivity patterns</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 text-blue-700">Methodological Advances</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Real-time processing enables rapid response to changes</li>
                <li>• Multi-habitat monitoring provides landscape-scale insights</li>
                <li>• Integration of environmental data improves predictions</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 text-purple-700">Next Steps</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Expand network to include offshore monitoring</li>
                <li>• Develop machine learning species classification</li>
                <li>• Long-term climate change impact assessment</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}