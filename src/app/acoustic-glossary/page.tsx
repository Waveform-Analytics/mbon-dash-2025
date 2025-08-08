'use client';

import React, { useState, useMemo } from 'react';
import { 
  MagnifyingGlassIcon,
  AdjustmentsHorizontalIcon,
  InformationCircleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

// Acoustic indices data from CSV
const ACOUSTIC_INDICES = [
  // Amplitude Indices
  { prefix: 'BGNf', category: 'Amplitude Indices', subcategory: 'Background Noise', description: 'Level of background noise in the frequency domain, indicating the level of ambient noise pollution in the environment.' },
  { prefix: 'KURTt', category: 'Amplitude Indices', subcategory: 'Time Distribution', description: '"Tailedness" of the amplitude distribution in the time domain, indicating infrequent extreme deviations.' },
  { prefix: 'LEQf', category: 'Amplitude Indices', subcategory: 'Frequency', description: 'Equivalent constant sound level in the frequency domain that conveys the same sound energy.' },
  { prefix: 'MEANf', category: 'Amplitude Indices', subcategory: 'Frequency', description: 'Average frequency of sounds, weighted by their amplitude.' },
  { prefix: 'SNRf', category: 'Amplitude Indices', subcategory: 'Noise', description: 'Ratio of signal level to noise level in the frequency domain.' },
  { prefix: 'SNRt', category: 'Amplitude Indices', subcategory: 'Noise', description: 'Ratio of the audio signal level to the level of background noise.' },

  // Complexity Indices
  { prefix: 'ACI', category: 'Complexity Indices', subcategory: 'Amplitude Variation', description: 'Quantifies the complexity of sound by evaluating the variation in amplitude among frequency bands, providing insights into the richness and diversity of the acoustic environment. Based on user defined threshold (Full bandwidth used for these calculations)' },
  { prefix: 'ACTspCount', category: 'Complexity Indices', subcategory: 'Spatial Activity', description: 'Measures the count of spatial areas showing significant sound activity, reflecting spatial patterns of sound distribution and activity. Quantifies how many distinct spatial regions have notable sound events.' },
  { prefix: 'ACTspFract', category: 'Complexity Indices', subcategory: 'Spatial Activity', description: 'Measures fraction of spatial areas showing significant sound activity, reflecting spatial patterns of sound distribution and activity. Represents proportion of the area that is active, providing insight into concentration of sound activity across space' },
  { prefix: 'ACTspMean', category: 'Complexity Indices', subcategory: 'Spatial Activity', description: 'Measures the mean spatial areas showing significant sound activity, reflecting spatial patterns of sound distribution and activity. Provides average intensity of sound activity in the area, or overall sound energy distribution.' },
  { prefix: 'AGI', category: 'Complexity Indices', subcategory: 'Gap Analysis', description: 'Measures the gaps or silent intervals within the acoustic signal, indicative of disturbance or interruptions in natural soundscapes, indicating areas or periods of significnt acoustic change.' },
  { prefix: 'EAS', category: 'Complexity Indices', subcategory: 'Energy Spectrum', description: 'Total acoustic energy measured across the spectrum, providing an overview of the overall energy distribution and composition of the acoustic environment.' },
  { prefix: 'ECU', category: 'Complexity Indices', subcategory: 'Frequency Channel', description: 'Evenness with which different frequency channels are utilized, reflecting the efficient utilization of frequency resources within the acoustic spectrum.' },
  { prefix: 'ECV', category: 'Complexity Indices', subcategory: 'Energy Variation', description: 'Coefficient of variation of the energy across different frequency bands, providing insights into the variability and distribution of acoustic energy within the environment.' },
  { prefix: 'ENRf', category: 'Complexity Indices', subcategory: 'Energy Ratio', description: 'Ratio of energy within certain frequency bands compared to the total energy, offering information about the distribution and allocation of energy across the frequency spectrum.' },
  { prefix: 'EVNspCount', category: 'Complexity Indices', subcategory: 'Spatial Event', description: 'Count of sound events in spatial areas, offering insights into spatial patterns of sound activity and distribution.' },
  { prefix: 'EVNspFract', category: 'Complexity Indices', subcategory: 'Spatial Event', description: 'Fraction of the spatial domain where sound events occur, providing insights into spatial patterns of sound activity and distribution.' },
  { prefix: 'EVNspMean', category: 'Complexity Indices', subcategory: 'Spatial Event', description: 'Average level of sound events across spatial areas, providing insights into spatial patterns of sound activity and distribution.' },
  { prefix: 'RAOQ', category: 'Complexity Indices', subcategory: 'Entropy', description: 'Entropy measure that considers both abundance and dissimilarity among categories.' },
  { prefix: 'ROIcover', category: 'Complexity Indices', subcategory: 'Spatial Coverage', description: 'Extent to which regions of interest cover the acoustic space.' },
  { prefix: 'ROItotal', category: 'Complexity Indices', subcategory: 'Spatial Count', description: 'Total measure or count of regions of interest identified within the soundscape.' },
  { prefix: 'ROU', category: 'Complexity Indices', subcategory: 'Texture', description: 'Measure of the texture or roughness of the sound profile.' },
  { prefix: 'ZCR', category: 'Complexity Indices', subcategory: 'Frequency', description: 'Measures the rate at which the signal changes from positive to negative or back, indicating the frequency content of the sound.' },

  // Diversity Indices
  { prefix: 'ADI', category: 'Diversity Indices', subcategory: 'Diversity', description: 'Measures the variety of sound frequencies present, indicative of biodiversity, and provides valuable information about the ecological integrity and health of the acoustic environment. Based on user defined threshold for andthrophony (0-1,000 Hz for 16 kHz SR; 0-1,500 Hz for Full Bandwidth) and biophony (1,000 Hz - 8,000 Hz for 16 kHz SR; 1,500 Hz and up for Full Bandwidth runs).' },
  { prefix: 'AEI', category: 'Diversity Indices', subcategory: 'Evenness', description: 'Evaluates the evenness of the distribution of sound energy across frequencies, reflecting the balance and uniformity of acoustic energy within the environment. Based on user defined threshold for andthrophony (0-1,000 Hz for 16 kHz SR; 0-1,500 Hz for Full Bandwidth) and biophony (1,000 Hz - 8,000 Hz for 16 kHz SR; 1,500 Hz and up for Full Bandwidth runs).' },
  { prefix: 'BI', category: 'Diversity Indices', subcategory: 'Biotic Index', description: 'Index evaluating the presence of biological sounds. Based on user defined threshold (1,000 Hz - 8,000 Hz for 16 kHz SR; 1,500 Hz and up for Full Bandwidth runs)' },
  { prefix: 'BioEnergy', category: 'Diversity Indices', subcategory: 'Energy', description: 'Measure of energy associated with natural sounds, reflecting the presence and intensity of biological activities within the environment. Based on user defined threshold (1,000 Hz - 8,000 Hz for 16 kHz SR; 1,500 Hz and up for Full Bandwidth runs)' },
  { prefix: 'H_gamma', category: 'Diversity Indices', subcategory: 'Entropy', description: 'Entropy measure based on the gamma distribution, used for sound diversity.' },
  { prefix: 'H_GiniSimpson', category: 'Diversity Indices', subcategory: 'Entropy', description: 'Entropy based on the Gini-Simpson index, reflecting diversity and probability.' },
  { prefix: 'H_Havrda', category: 'Diversity Indices', subcategory: 'Entropy', description: 'Entropy measure based on Havrda-Charvat entropy, reflecting diversity.' },
  { prefix: 'H_pairedShannon', category: 'Diversity Indices', subcategory: 'Entropy', description: 'Shannon entropy calculated from paired data sets for comparing diversity.' },
  { prefix: 'H_Renyi', category: 'Diversity Indices', subcategory: 'Entropy', description: 'Generalized entropy measure capturing diversity and richness of the soundscape.' },

  // Spectral Indices
  { prefix: 'AnthroEnergy', category: 'Spectral Indices', subcategory: 'Energy', description: 'Measure of energy associated with human-made sounds, providing information about anthropogenic influences on the acoustic environment. Based on user defined threshold (1,000 Hz for 16 kHz SR; 1,500 Hz for Full bandwidth)' },
  { prefix: 'EPS', category: 'Spectral Indices', subcategory: 'Energy Spectrum', description: 'Measure of the peak energy in the spectrum, indicating the presence and intensity of dominant acoustic events or phenomena.' },
  { prefix: 'EPS_KURT', category: 'Spectral Indices', subcategory: 'Energy Spectrum', description: 'Kurtosis of the energy peak spectrum, indicating the shape of the peak distribution and providing insights into the distributional characteristics of dominant energy sources.' },
  { prefix: 'EPS_SKEW', category: 'Spectral Indices', subcategory: 'Energy Spectrum', description: 'Skewness of the energy peak spectrum, indicating the asymmetry of the peak distribution and providing information about the uniformity of energy distribution within the spectrum.' },
  { prefix: 'Hf', category: 'Spectral Indices', subcategory: 'Frequency', description: 'Extent to which high frequencies are present in the soundscape.' },
  { prefix: 'HFC', category: 'Spectral Indices', subcategory: 'Frequency', description: 'Reiterates the presence and extent of high frequencies in the soundscape.' },
  { prefix: 'KURTf', category: 'Spectral Indices', subcategory: 'Frequency Distribution', description: '"Tailedness" of the frequency distribution, indicating infrequent extreme frequency deviations.' },
  { prefix: 'LFC', category: 'Spectral Indices', subcategory: 'Frequency', description: 'Extent to which low frequencies are present in the soundscape.' },
  { prefix: 'MED', category: 'Spectral Indices', subcategory: 'Energy Distribution', description: 'Median frequency of the acoustic signal, providing insights into the central tendency of frequency distribution within the environment.' },
  { prefix: 'MFC', category: 'Spectral Indices', subcategory: 'Frequency', description: 'Extent to which mid-range frequencies are present in the soundscape.' },
  { prefix: 'NBPEAKS', category: 'Spectral Indices', subcategory: 'Frequency', description: 'Total number of prominent peaks in the frequency spectrum.' },
  { prefix: 'NDSI', category: 'Spectral Indices', subcategory: 'Balance', description: 'Index of the balance between biological sounds and anthropogenic noise.' },
  { prefix: 'rBA', category: 'Spectral Indices', subcategory: 'Balance', description: 'Relative levels of biophony (natural sounds) and anthrophony (human-made sounds). Based on user defined threshold for andthrophony (0-1,000 Hz for 16 kHz SR; 0-1,500 Hz for Full Bandwidth) and biophony (1,000 Hz - 8,000 Hz for 16 kHz SR; 1,500 Hz and up for Full Bandwidth runs).' },
  { prefix: 'SKEWf', category: 'Spectral Indices', subcategory: 'Frequency Distribution', description: 'Asymmetry of the frequency distribution of the sound.' },
  { prefix: 'VARf', category: 'Spectral Indices', subcategory: 'Frequency', description: 'Variance in the frequency of sounds, indicating dispersion around the mean frequency.' },

  // Temporal Indices
  { prefix: 'ACTtCount', category: 'Temporal Indices', subcategory: 'Temporal Activity', description: 'Evaluates count of temporal sound activity, providing insights into the frequency, duration, and intensity of acoustic events over time. Quantifies how many distinct time intervals have notable sound events' },
  { prefix: 'ACTtFraction', category: 'Temporal Indices', subcategory: 'Temporal Activity', description: 'Evaluates fraction of total time of temporal sound activity, providing insights into the frequency, duration, and intensity of acoustic events over time. Represents proportion of time that is active, relating to the concentration of sound activity over time.' },
  { prefix: 'ACTtMean', category: 'Temporal Indices', subcategory: 'Temporal Activity', description: 'Evaluates mean temporal sound activity, providing insights into the frequency, duration, and intensity of acoustic events over time. Provides average intensity of sound activity in active time segments.' },
  { prefix: 'BGNt', category: 'Temporal Indices', subcategory: 'Background Noise', description: 'Level of background noise in the time domain, indicating the level of ambient noise pollution over time.' },
  { prefix: 'EVNtCount', category: 'Temporal Indices', subcategory: 'Temporal Event', description: 'Number of distinct sound events detected, providing insights into the frequency and occurrence of sound events over time.' },
  { prefix: 'EVNtFraction', category: 'Temporal Indices', subcategory: 'Temporal Event', description: 'Fraction of time that "events" (heightened sound activity) occur, providing insights into the frequency and occurrence of sound events over time.' },
  { prefix: 'EVNtMean', category: 'Temporal Indices', subcategory: 'Temporal Event', description: 'Average sound level during event times, providing insights into the intensity and characteristics of sound events over time.' },
  { prefix: 'Ht', category: 'Temporal Indices', subcategory: 'Time', description: 'Median frequency of the acoustic signal, providing insights into the central tendency of frequency distribution within the environment.' },
  { prefix: 'LEQt', category: 'Temporal Indices', subcategory: 'Time', description: 'Constant sound level that delivers the same sound energy as the varying sound level over a specified period.' },
  { prefix: 'MEANt', category: 'Temporal Indices', subcategory: 'Time', description: 'The average amplitude of the audio signal over time, reflecting the overall loudness.' },
  { prefix: 'SKEWt', category: 'Temporal Indices', subcategory: 'Time Distribution', description: 'Asymmetry of the amplitude distribution of the audio signal in the time domain.' },
  { prefix: 'TFSD', category: 'Temporal Indices', subcategory: 'Frequency', description: 'Diversity of frequencies over time, reflecting temporal variation.' },
  { prefix: 'VARt', category: 'Temporal Indices', subcategory: 'Time', description: 'Variance of the time-domain audio signal amplitude, indicating amplitude fluctuations over time.' }
];

type CategoryType = 'Amplitude Indices' | 'Complexity Indices' | 'Diversity Indices' | 'Spectral Indices' | 'Temporal Indices';

const CATEGORY_COLORS: Record<CategoryType, { bg: string; border: string; text: string; badge: string }> = {
  'Amplitude Indices': { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', badge: 'bg-red-100' },
  'Complexity Indices': { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-800', badge: 'bg-emerald-100' },
  'Diversity Indices': { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', badge: 'bg-blue-100' },
  'Spectral Indices': { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-800', badge: 'bg-purple-100' },
  'Temporal Indices': { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800', badge: 'bg-orange-100' }
};

const CATEGORY_DESCRIPTIONS: Record<CategoryType, string> = {
  'Amplitude Indices': 'Measure sound intensity variations, loudness, and dynamic range of the soundscape.',
  'Complexity Indices': 'Assess soundscape intricacy, capturing diversity and variability of sound sources.',
  'Diversity Indices': 'Quantify sound variety, reflecting ecological diversity and health of the environment.',
  'Spectral Indices': 'Analyze frequency characteristics, providing insights into the spectral characteristics of the soundscape.',
  'Temporal Indices': 'Measure sound changes over time, capturing temporal patterns and dynamics in the soundscape.'
};

export default function AcousticGlossaryPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>('All');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const categories = ['All', ...Object.keys(CATEGORY_COLORS)];
  
  // Get available subcategories based on selected category
  const availableSubcategories = useMemo(() => {
    const subcategories = new Set<string>();
    ACOUSTIC_INDICES
      .filter(index => selectedCategory === 'All' || index.category === selectedCategory)
      .forEach(index => subcategories.add(index.subcategory));
    return ['All', ...Array.from(subcategories).sort()];
  }, [selectedCategory]);
  
  const filteredIndices = useMemo(() => {
    return ACOUSTIC_INDICES.filter(index => {
      const matchesSearch = 
        index.prefix.toLowerCase().includes(searchTerm.toLowerCase()) ||
        index.subcategory.toLowerCase().includes(searchTerm.toLowerCase()) ||
        index.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = selectedCategory === 'All' || index.category === selectedCategory;
      const matchesSubcategory = selectedSubcategory === 'All' || index.subcategory === selectedSubcategory;
      
      return matchesSearch && matchesCategory && matchesSubcategory;
    });
  }, [searchTerm, selectedCategory, selectedSubcategory]);
  
  // Reset subcategory when category changes
  React.useEffect(() => {
    setSelectedSubcategory('All');
  }, [selectedCategory]);

  const indexCounts = Object.keys(CATEGORY_COLORS).reduce((acc, category) => {
    acc[category] = ACOUSTIC_INDICES.filter(index => index.category === category).length;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          Acoustic Indices
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Reference</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          Comprehensive reference for the 60 acoustic indices used in marine soundscape biodiversity analysis.
          Indices are computed at two sample rates with specific frequency thresholds for biological and anthropogenic sounds.
        </p>
      </div>


      {/* Search and Filter Controls */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search indices by name, subcategory, or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-ocean-500 focus:border-ocean-500"
              />
            </div>
          </div>
          
          <div className="flex gap-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-ocean-500"
            >
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
            
            {selectedCategory !== 'All' && availableSubcategories.length > 1 && (
              <select
                value={selectedSubcategory}
                onChange={(e) => setSelectedSubcategory(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-ocean-500 text-sm"
              >
                {availableSubcategories.map(subcategory => (
                  <option key={subcategory} value={subcategory}>
                    {subcategory === 'All' ? 'All Subcategories' : subcategory}
                  </option>
                ))}
              </select>
            )}
            
            {(selectedCategory !== 'All' || selectedSubcategory !== 'All') && (
              <button
                onClick={() => {
                  setSelectedCategory('All');
                  setSelectedSubcategory('All');
                }}
                className="px-4 py-2 bg-ocean-100 text-ocean-700 rounded-lg hover:bg-ocean-200 transition-colors font-medium flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Show All
              </button>
            )}
            
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors flex items-center gap-2"
            >
              <AdjustmentsHorizontalIcon className="w-4 h-4" />
              {viewMode === 'grid' ? 'List' : 'Grid'}
            </button>
          </div>
        </div>
        
        {/* Results count */}
        <div className="mt-4 text-sm text-slate-600">
          Showing {filteredIndices.length} of {ACOUSTIC_INDICES.length} indices
          {selectedCategory !== 'All' && ` in ${selectedCategory}`}
          {selectedSubcategory !== 'All' && ` → ${selectedSubcategory}`}
        </div>
      </div>

      {/* Category Overview */}
      {selectedCategory === 'All' && (
        <div className="grid md:grid-cols-5 gap-4 mb-8">
          {Object.entries(CATEGORY_COLORS).map(([category, colors]) => (
            <div
              key={category}
              className={`${colors.bg} ${colors.border} p-4 rounded-lg border cursor-pointer hover:shadow-md transition-shadow`}
              onClick={() => setSelectedCategory(category)}
            >
              <div className="text-center">
                <div className={`text-2xl font-bold ${colors.text} mb-1`}>
                  {indexCounts[category]}
                </div>
                <div className="text-sm font-medium text-slate-700 mb-2">
                  {category.replace(' Indices', '')}
                </div>
                <div className="text-xs text-slate-600">
                  {CATEGORY_DESCRIPTIONS[category as CategoryType]}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      <div className={viewMode === 'grid' ? 'grid md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
        {filteredIndices.map((index) => {
          const colors = CATEGORY_COLORS[index.category as CategoryType];
          
          return (
            <div
              key={index.prefix}
              className={`${colors.bg} ${colors.border} border rounded-lg p-4 hover:shadow-md transition-shadow`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className={`font-bold text-lg ${colors.text}`}>{index.prefix}</h3>
                  <button
                    onClick={() => setSelectedSubcategory(index.subcategory)}
                    className={`text-sm ${colors.badge} ${colors.text} px-2 py-1 rounded-full inline-block mt-1 hover:opacity-80 hover:shadow-sm transition-all cursor-pointer border-2 border-transparent hover:border-current`}
                    title={`Filter by ${index.subcategory}`}
                  >
                    {index.subcategory}
                  </button>
                </div>
                <div className={`text-xs ${colors.text} opacity-75`}>
                  {index.category.replace(' Indices', '')}
                </div>
              </div>
              
              <p className={`text-sm ${colors.text} opacity-90 leading-relaxed`}>
                {index.description}
              </p>
            </div>
          );
        })}
      </div>

      {filteredIndices.length === 0 && (
        <div className="text-center py-12">
          <DocumentTextIcon className="w-12 h-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No indices found</h3>
          <p className="text-slate-600">Try adjusting your search terms or selected category.</p>
        </div>
      )}

      {/* Sample Rate Information */}
      <div className="mt-12 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
          <InformationCircleIcon className="w-5 h-5" />
          Sample Rate Analysis
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-medium text-blue-800 mb-2">16 kHz Sample Rate</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• <strong>Anthrophony:</strong> 0-1,000 Hz (human-made sounds)</li>
              <li>• <strong>Biophony:</strong> 1,000-8,000 Hz (biological sounds)</li>
              <li>• <strong>Applications:</strong> Standard marine acoustic analysis</li>
            </ul>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h4 className="font-medium text-blue-800 mb-2">Full Bandwidth</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• <strong>Anthrophony:</strong> 0-1,500 Hz (human-made sounds)</li>
              <li>• <strong>Biophony:</strong> 1,500 Hz and up (biological sounds)</li>
              <li>• <strong>Applications:</strong> Extended frequency analysis</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}