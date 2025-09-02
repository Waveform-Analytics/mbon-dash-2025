import Link from 'next/link';
import { ArrowRight, Map, BarChart3, Beaker } from 'lucide-react';

export default function Landing2Page() {
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
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-primary-foreground mb-6">
              Marine Biodiversity Dashboard
            </h1>
            <p className="text-xl md:text-2xl text-primary-foreground/95 mb-8 max-w-4xl mx-auto font-light">
              Exploring whether acoustic indices can predict marine soundscape biodiversity 
              and serve as proxies for complex biodiversity monitoring
            </p>
            <Link 
              href="/explore"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 transition-colors"
            >
              Explore the Data
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Main Content Grid */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* The Challenge */}
            <div className="bg-card rounded-lg shadow-lg p-8 border">
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
            </div>

            {/* Our Approach */}
            <div className="bg-card rounded-lg shadow-lg p-8 border">
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
            </div>

            {/* Key Findings */}
            <div className="bg-card rounded-lg shadow-lg p-8 border">
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
            </div>

          </div>
        </div>
      </section>

      {/* Quick Access Navigation */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-muted/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-foreground mb-12">
            Explore Our Research
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            {/* Data Overview */}
            <Link 
              href="/data" 
              className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border"
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-1/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-1/30 transition-colors">
                  <Map className="h-6 w-6 text-chart-1" />
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Data Overview</h3>
                <p className="text-sm text-muted-foreground">Study sites, soundscapes, and data collection methods</p>
              </div>
            </Link>

            {/* Analysis Journey */}
            <Link 
              href="/analysis" 
              className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border"
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-2/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-2/30 transition-colors">
                  <BarChart3 className="h-6 w-6 text-chart-2" />
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Analysis Journey</h3>
                <p className="text-sm text-muted-foreground">Step-by-step exploration of patterns and models</p>
              </div>
            </Link>

            {/* Insights */}
            <Link 
              href="/insights" 
              className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border"
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-3/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-3/30 transition-colors">
                  <Beaker className="h-6 w-6 text-chart-3" />
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Insights</h3>
                <p className="text-sm text-muted-foreground">Key indicators and practical applications</p>
              </div>
            </Link>

            {/* Interactive Explorer */}
            <Link 
              href="/explore" 
              className="group bg-card p-6 rounded-lg shadow hover:shadow-lg transition-shadow border"
            >
              <div className="text-center">
                <div className="w-12 h-12 bg-chart-4/20 rounded-lg flex items-center justify-center mx-auto mb-4 group-hover:bg-chart-4/30 transition-colors">
                  <BarChart3 className="h-6 w-6 text-chart-4" />
                </div>
                <h3 className="text-lg font-semibold text-card-foreground mb-2">Interactive Explorer</h3>
                <p className="text-sm text-muted-foreground">Custom analysis and data export tools</p>
              </div>
            </Link>

          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            Ready to Dive In?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Start exploring our data and discover the connections between acoustic patterns and marine biodiversity.
          </p>
          <div className="space-x-4">
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
          </div>
        </div>
      </section>
    </div>
  );
}