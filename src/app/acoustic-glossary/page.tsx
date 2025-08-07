'use client';

import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  SpeakerWaveIcon,
  BeakerIcon,
  MapPinIcon,
  ScaleIcon,
  ClockIcon,
  BoltIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  MusicalNoteIcon
} from '@heroicons/react/24/outline';

export default function AcousticGlossaryPage() {
  return (
    <div className="page-container">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="section-heading text-4xl">
          Understanding
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Acoustic Indices</span>
        </h1>
        <p className="section-description">
          A comprehensive guide to acoustic indices, what they measure, and their biological relevance 
          for marine soundscape biodiversity monitoring.
        </p>
      </div>

      {/* Introduction */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 mb-12">
        <h2 className="text-2xl font-bold text-blue-900 mb-4 flex items-center gap-2">
          <MusicalNoteIcon className="w-6 h-6" />
          What Are Acoustic Indices?
        </h2>
        <div className="space-y-4 text-blue-800">
          <p>
            <strong>Acoustic indices</strong> are computed metrics that summarize key characteristics 
            of audio recordings in standardized, quantitative ways. Instead of manually listening to 
            hours of recordings, these indices automatically extract meaningful patterns from soundscapes.
          </p>
          <div className="grid md:grid-cols-2 gap-6 mt-6">
            <div className="bg-blue-100 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <SpeakerWaveIcon className="w-5 h-5" />
                Traditional Approach
              </h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Manual listening to recordings</li>
                <li>• Time-intensive species identification</li>
                <li>• Expert knowledge required</li>
                <li>• Limited scalability</li>
                <li>• High cost per hour analyzed</li>
              </ul>
            </div>
            <div className="bg-green-100 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2 flex items-center gap-2">
                <ChartBarIcon className="w-5 h-5" />
                Acoustic Indices Approach
              </h3>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Automated computation from audio</li>
                <li>• Rapid processing of large datasets</li>
                <li>• Standardized, repeatable metrics</li>
                <li>• Highly scalable analysis</li>
                <li>• Cost-effective monitoring</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Index Categories */}
      <div className="space-y-8">
        
        {/* Amplitude-Based Indices */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <ArrowTrendingUpIcon className="w-5 h-5 inline mr-2" />Amplitude-Based Indices
            <span className="badge badge-coral ml-3">Category 1</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Indices that measure the loudness, intensity, and volume characteristics of soundscapes.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                <h4 className="font-medium text-purple-800 mb-3 flex items-center gap-2">
                  <SpeakerWaveIcon className="w-4 h-4" />
                  RMS Sound Pressure Level (rmsSPL)
                </h4>
                <p className="text-sm text-purple-700 mb-3">
                  <strong>Current Data Available</strong> - Root mean square of sound pressure over time periods.
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-purple-600">
                  <li><strong>Measures:</strong> Overall acoustic energy/loudness</li>
                  <li><strong>Biological Relevance:</strong> Total biological activity, calling intensity</li>
                  <li><strong>Applications:</strong> General activity levels, anthropogenic noise detection</li>
                  <li><strong>Data Issues:</strong> Current rmsSPL data has known quality issues being addressed</li>
                </ul>
              </div>
              
              <div className="bg-indigo-50 p-6 rounded-lg border border-indigo-200">
                <h4 className="font-medium text-indigo-800 mb-3 flex items-center gap-2">
                  <ChartBarIcon className="w-4 h-4" />
                  Additional Amplitude Indices
                </h4>
                <p className="text-sm text-indigo-700 mb-3">
                  <strong>Future Data</strong> - Additional amplitude-based metrics (60+ indices planned).
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-indigo-600">
                  <li><strong>Peak Amplitude:</strong> Maximum sound levels</li>
                  <li><strong>Dynamic Range:</strong> Variation in loudness over time</li>
                  <li><strong>Percentile Levels:</strong> Distribution of amplitude values</li>
                  <li><strong>Temporal Variability:</strong> Changes in amplitude patterns</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Frequency-Based Indices */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            <MusicalNoteIcon className="w-5 h-5 inline mr-2" />Frequency-Based Indices
            <span className="badge badge-ocean ml-3">Category 2</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Indices that characterize the spectral content and frequency distribution of sounds.
            </p>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-teal-50 p-4 rounded-lg border border-teal-200">
                <h4 className="font-medium text-teal-800 mb-2 flex items-center gap-2">
                  <MusicalNoteIcon className="w-4 h-4" />
                  Spectral Centroid
                </h4>
                <p className="text-sm text-teal-700 mb-2">
                  "Center of mass" of the frequency spectrum
                </p>
                <ul className="list-disc list-inside space-y-1 text-xs text-teal-600">
                  <li>Higher values = more high-frequency content</li>
                  <li>Useful for distinguishing call types</li>
                </ul>
              </div>
              
              <div className="bg-cyan-50 p-4 rounded-lg border border-cyan-200">
                <h4 className="font-medium text-cyan-800 mb-2 flex items-center gap-2">
                  <ChartBarIcon className="w-4 h-4" />
                  Spectral Bandwidth
                </h4>
                <p className="text-sm text-cyan-700 mb-2">
                  Width of frequency distribution
                </p>
                <ul className="list-disc list-inside space-y-1 text-xs text-cyan-600">
                  <li>Broader bandwidth = wider frequency range</li>
                  <li>Related to call complexity</li>
                </ul>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2 flex items-center gap-2">
                  <MapPinIcon className="w-4 h-4" />
                  Peak Frequency
                </h4>
                <p className="text-sm text-blue-700 mb-2">
                  Dominant frequency in the spectrum
                </p>
                <ul className="list-disc list-inside space-y-1 text-xs text-blue-600">
                  <li>Species-specific frequency preferences</li>
                  <li>Habitat-related frequency filtering</li>
                </ul>
              </div>
            </div>

            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2 flex items-center gap-2">
                <BeakerIcon className="w-4 h-4" />
                Biological Relevance for Marine Species
              </h4>
              <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-700">
                <div>
                  <strong>Fish Calls:</strong> Many fish species have characteristic frequency ranges 
                  (e.g., oyster toadfish boat whistle ~140-200 Hz)
                </div>
                <div>
                  <strong>Marine Mammals:</strong> Dolphin echolocation and whistles occupy different 
                  frequency bands that these indices can distinguish
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Complexity & Diversity Indices */}
        <div className="chart-container">
          <h3 className="text-xl font-semibold text-slate-900 mb-4">
            🌐 Complexity & Diversity Indices
            <span className="badge badge-coral ml-3">Category 3</span>
          </h3>
          <div className="space-y-4">
            <p className="text-slate-600 mb-4">
              Indices that measure the complexity, diversity, and richness of soundscapes.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-emerald-50 p-6 rounded-lg border border-emerald-200">
                <h4 className="font-medium text-emerald-800 mb-3">🧬 Acoustic Complexity Index (ACI)</h4>
                <p className="text-sm text-emerald-700 mb-3">
                  Measures variability in amplitude over time and frequency
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-emerald-600">
                  <li><strong>High ACI:</strong> Complex soundscapes with many species/sounds</li>
                  <li><strong>Low ACI:</strong> Simple soundscapes or continuous noise</li>
                  <li><strong>Biological Use:</strong> Directly related to biodiversity</li>
                  <li><strong>Research Application:</strong> Primary metric for species richness prediction</li>
                </ul>
              </div>
              
              <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                <h4 className="font-medium text-green-800 mb-3">📐 Acoustic Diversity Index (ADI)</h4>
                <p className="text-sm text-green-700 mb-3">
                  Shannon diversity applied to frequency bands
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm text-green-600">
                  <li><strong>Measures:</strong> Evenness of acoustic energy across frequencies</li>
                  <li><strong>Higher ADI:</strong> More equal distribution of acoustic activity</li>
                  <li><strong>Ecological Meaning:</strong> Frequency niche partitioning among species</li>
                  <li><strong>Marine Context:</strong> Different species using different frequency ranges</li>
                </ul>
              </div>
            </div>

            <div className="mt-6 grid md:grid-cols-3 gap-4">
              <div className="bg-lime-50 p-4 rounded-lg border border-lime-200">
                <h4 className="font-medium text-lime-800 mb-2 flex items-center gap-2">
                  <ScaleIcon className="w-4 h-4" />
                  Acoustic Evenness Index
                </h4>
                <p className="text-sm text-lime-700">
                  Distribution of acoustic activity across frequency bands
                </p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <h4 className="font-medium text-yellow-800 mb-2">🔀 Spectral Entropy</h4>
                <p className="text-sm text-yellow-700">
                  Randomness/predictability in frequency content
                </p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h4 className="font-medium text-orange-800 mb-2 flex items-center gap-2">
                  <ChartBarIcon className="w-4 h-4" />
                  Frequency Diversity
                </h4>
                <p className="text-sm text-orange-700">
                  Number of distinct frequency bands with activity
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Temporal Pattern Indices */}
        <div className="chart-container bg-slate-50 border-dashed">
          <h3 className="text-xl font-semibold text-slate-700 mb-4">
            <ClockIcon className="w-5 h-5 inline mr-2" />Temporal Pattern Indices
            <span className="badge bg-slate-200 text-slate-700 ml-3">Future Data</span>
          </h3>
          <div className="space-y-4 text-slate-500">
            <p className="mb-4">
              <strong>Advanced temporal analysis</strong> indices that will be available with 
              the full 60+ index dataset at 5-minute resolution.
            </p>
            
            <div className="grid md:grid-cols-2 gap-6 text-sm">
              <div>
                <h4 className="font-medium text-slate-600 mb-2 flex items-center gap-2">
                  <MusicalNoteIcon className="w-4 h-4" />
                  Rhythm & Periodicity
                </h4>
                <ul className="list-disc list-inside space-y-1">
                  <li>Temporal regularity in calling patterns</li>
                  <li>Dawn/dusk chorus detection</li>
                  <li>Tidal cycle correlations</li>
                  <li>Species-specific temporal signatures</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-slate-600 mb-2 flex items-center gap-2">
                  <BoltIcon className="w-4 h-4" />
                  Event Detection
                </h4>
                <ul className="list-disc list-inside space-y-1">
                  <li>Onset/offset detection for calls</li>
                  <li>Burst pattern identification</li>
                  <li>Silent period analysis</li>
                  <li>Activity clustering metrics</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Interactive Index Explorer - Future */}
      <div className="chart-container bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200">
        <h3 className="text-xl font-semibold text-slate-900 mb-4">
          <MagnifyingGlassIcon className="w-5 h-5 inline mr-2" />Interactive Index Explorer
          <span className="badge badge-coral ml-3">Coming Soon</span>
        </h3>
        <div className="space-y-4">
          <p className="text-slate-600 mb-4">
            Planned interactive tool for exploring individual acoustic indices with real data examples.
          </p>
          
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                <ChartBarIcon className="w-4 h-4" />
                Index Selection
              </h4>
              <p className="text-slate-600">
                Dropdown menu to explore each of the 60+ acoustic indices individually
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                <MusicalNoteIcon className="w-4 h-4" />
                Audio Examples
              </h4>
              <p className="text-slate-600">
                Listen to audio samples showing high vs low index values
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg shadow-sm border">
              <h4 className="font-medium text-slate-800 mb-2 flex items-center gap-2">
                <ArrowTrendingUpIcon className="w-4 h-4" />
                Data Visualization
              </h4>
              <p className="text-slate-600">
                See how each index varies across time and relates to species presence
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Implementation Notes */}
      <div className="mt-12 p-6 bg-slate-100 rounded-xl">
        <h3 className="text-lg font-semibold text-slate-800 mb-3">🔧 Current Implementation Status</h3>
        <div className="text-sm text-slate-600 space-y-2">
          <p><strong>Available Data:</strong> rmsSPL index (with known quality issues being addressed)</p>
          <p><strong>Future Data:</strong> 60+ acoustic indices computed at 5-minute resolution from hydrophone recordings</p>
          <p><strong>Visualization Tools:</strong> Observable Plot for index distributions, D3.js for interactive exploration</p>
          <p><strong>Educational Goal:</strong> Make acoustic indices accessible to marine biologists and non-acoustics researchers</p>
          <p><strong>Target Outcome:</strong> Understanding which indices are most useful for marine biodiversity monitoring</p>
        </div>
      </div>

    </div>
  );
}