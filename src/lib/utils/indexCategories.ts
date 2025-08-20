export interface IndexCategory {
  prefix: string;
  category: string;
  subcategory: string;
  description: string;
}

export const indexCategories: IndexCategory[] = [
  { prefix: "ACI", category: "Complexity Indices", subcategory: "Amplitude Variation", description: "Quantifies the complexity of sound by evaluating the variation in amplitude among frequency bands" },
  { prefix: "ACTspCount", category: "Complexity Indices", subcategory: "Spatial Activity", description: "Measures the count of spatial areas showing significant sound activity" },
  { prefix: "ACTspFract", category: "Complexity Indices", subcategory: "Spatial Activity", description: "Measures fraction of spatial areas showing significant sound activity" },
  { prefix: "ACTspMean", category: "Complexity Indices", subcategory: "Spatial Activity", description: "Measures the mean spatial areas showing significant sound activity" },
  { prefix: "ACTtCount", category: "Temporal Indices", subcategory: "Temporal Activity", description: "Evaluates count of temporal sound activity" },
  { prefix: "ACTtFraction", category: "Temporal Indices", subcategory: "Temporal Activity", description: "Evaluates fraction of total time of temporal sound activity" },
  { prefix: "ACTtMean", category: "Temporal Indices", subcategory: "Temporal Activity", description: "Evaluates mean temporal sound activity" },
  { prefix: "ADI", category: "Diversity Indices", subcategory: "Diversity", description: "Measures the variety of sound frequencies present, indicative of biodiversity" },
  { prefix: "AEI", category: "Diversity Indices", subcategory: "Evenness", description: "Evaluates the evenness of the distribution of sound energy across frequencies" },
  { prefix: "AGI", category: "Complexity Indices", subcategory: "Gap Analysis", description: "Measures the gaps or silent intervals within the acoustic signal" },
  { prefix: "AnthroEnergy", category: "Spectral Indices", subcategory: "Energy", description: "Measure of energy associated with human-made sounds" },
  { prefix: "BGNf", category: "Amplitude Indices", subcategory: "Background Noise", description: "Level of background noise in the frequency domain" },
  { prefix: "BGNt", category: "Temporal Indices", subcategory: "Background Noise", description: "Level of background noise in the time domain" },
  { prefix: "BI", category: "Diversity Indices", subcategory: "Biotic Index", description: "Index evaluating the presence of biological sounds" },
  { prefix: "BioEnergy", category: "Diversity Indices", subcategory: "Energy", description: "Measure of energy associated with natural sounds" },
  { prefix: "EAS", category: "Complexity Indices", subcategory: "Energy Spectrum", description: "Total acoustic energy measured across the spectrum" },
  { prefix: "ECU", category: "Complexity Indices", subcategory: "Frequency Channel", description: "Evenness with which different frequency channels are utilized" },
  { prefix: "ECV", category: "Complexity Indices", subcategory: "Energy Variation", description: "Coefficient of variation of the energy across different frequency bands" },
  { prefix: "ENRf", category: "Complexity Indices", subcategory: "Energy Ratio", description: "Ratio of energy within certain frequency bands compared to the total energy" },
  { prefix: "EPS", category: "Spectral Indices", subcategory: "Energy Spectrum", description: "Measure of the peak energy in the spectrum" },
  { prefix: "EPS_KURT", category: "Spectral Indices", subcategory: "Energy Spectrum", description: "Kurtosis of the energy peak spectrum" },
  { prefix: "EPS_SKEW", category: "Spectral Indices", subcategory: "Energy Spectrum", description: "Skewness of the energy peak spectrum" },
  { prefix: "EVNspCount", category: "Complexity Indices", subcategory: "Spatial Event", description: "Count of sound events in spatial areas" },
  { prefix: "EVNspFract", category: "Complexity Indices", subcategory: "Spatial Event", description: "Fraction of the spatial domain where sound events occur" },
  { prefix: "EVNspMean", category: "Complexity Indices", subcategory: "Spatial Event", description: "Average level of sound events across spatial areas" },
  { prefix: "EVNtCount", category: "Temporal Indices", subcategory: "Temporal Event", description: "Number of distinct sound events detected" },
  { prefix: "EVNtFraction", category: "Temporal Indices", subcategory: "Temporal Event", description: "Fraction of time that events occur" },
  { prefix: "EVNtMean", category: "Temporal Indices", subcategory: "Temporal Event", description: "Average sound level during event times" },
  { prefix: "H_gamma", category: "Diversity Indices", subcategory: "Entropy", description: "Entropy measure based on the gamma distribution" },
  { prefix: "H_GiniSimpson", category: "Diversity Indices", subcategory: "Entropy", description: "Entropy based on the Gini-Simpson index" },
  { prefix: "H_Havrda", category: "Diversity Indices", subcategory: "Entropy", description: "Entropy measure based on Havrda-Charvat entropy" },
  { prefix: "H_pairedShannon", category: "Diversity Indices", subcategory: "Entropy", description: "Shannon entropy calculated from paired data sets" },
  { prefix: "H_Renyi", category: "Diversity Indices", subcategory: "Entropy", description: "Generalized entropy measure capturing diversity" },
  { prefix: "Hf", category: "Spectral Indices", subcategory: "Frequency", description: "Extent to which high frequencies are present" },
  { prefix: "HFC", category: "Spectral Indices", subcategory: "Frequency", description: "High frequency content in the soundscape" },
  { prefix: "Ht", category: "Temporal Indices", subcategory: "Time", description: "Median frequency of the acoustic signal" },
  { prefix: "KURTf", category: "Spectral Indices", subcategory: "Frequency Distribution", description: "Tailedness of the frequency distribution" },
  { prefix: "KURTt", category: "Amplitude Indices", subcategory: "Time Distribution", description: "Tailedness of the amplitude distribution in time" },
  { prefix: "LEQf", category: "Amplitude Indices", subcategory: "Frequency", description: "Equivalent constant sound level in frequency domain" },
  { prefix: "LEQt", category: "Temporal Indices", subcategory: "Time", description: "Constant sound level over a specified period" },
  { prefix: "LFC", category: "Spectral Indices", subcategory: "Frequency", description: "Low frequency content in the soundscape" },
  { prefix: "MEANf", category: "Amplitude Indices", subcategory: "Frequency", description: "Average frequency of sounds, weighted by amplitude" },
  { prefix: "MEANt", category: "Temporal Indices", subcategory: "Time", description: "Average amplitude of the audio signal over time" },
  { prefix: "MFC", category: "Spectral Indices", subcategory: "Frequency", description: "Mid-range frequency content in the soundscape" },
  { prefix: "MED", category: "Spectral Indices", subcategory: "Energy Distribution", description: "Median frequency of the acoustic signal" },
  { prefix: "NBPEAKS", category: "Spectral Indices", subcategory: "Frequency", description: "Total number of prominent peaks in frequency spectrum" },
  { prefix: "NDSI", category: "Spectral Indices", subcategory: "Balance", description: "Balance between biological sounds and anthropogenic noise" },
  { prefix: "RAOQ", category: "Complexity Indices", subcategory: "Entropy", description: "Entropy measure considering abundance and dissimilarity" },
  { prefix: "rBA", category: "Spectral Indices", subcategory: "Balance", description: "Relative levels of biophony and anthrophony" },
  { prefix: "ROIcover", category: "Complexity Indices", subcategory: "Spatial Coverage", description: "Extent to which regions of interest cover acoustic space" },
  { prefix: "ROItotal", category: "Complexity Indices", subcategory: "Spatial Count", description: "Total measure or count of regions of interest" },
  { prefix: "ROU", category: "Complexity Indices", subcategory: "Texture", description: "Measure of the texture or roughness of sound profile" },
  { prefix: "SKEWf", category: "Spectral Indices", subcategory: "Frequency Distribution", description: "Asymmetry of the frequency distribution" },
  { prefix: "SKEWt", category: "Temporal Indices", subcategory: "Time Distribution", description: "Asymmetry of the amplitude distribution in time" },
  { prefix: "SNRf", category: "Amplitude Indices", subcategory: "Noise", description: "Signal to noise ratio in frequency domain" },
  { prefix: "SNRt", category: "Amplitude Indices", subcategory: "Noise", description: "Signal to noise ratio in time domain" },
  { prefix: "TFSD", category: "Temporal Indices", subcategory: "Frequency", description: "Diversity of frequencies over time" },
  { prefix: "VARf", category: "Spectral Indices", subcategory: "Frequency", description: "Variance in the frequency of sounds" },
  { prefix: "VARt", category: "Temporal Indices", subcategory: "Time", description: "Variance of the time-domain audio signal amplitude" },
  { prefix: "ZCR", category: "Complexity Indices", subcategory: "Frequency", description: "Rate at which signal changes from positive to negative" }
];

export function getIndexInfo(indexName: string): IndexCategory | undefined {
  return indexCategories.find(cat => cat.prefix === indexName);
}

export function getUniqueCategories(): string[] {
  const categories = new Set(indexCategories.map(cat => cat.category));
  return Array.from(categories).sort();
}

export function getIndicesByCategory(category: string): string[] {
  return indexCategories
    .filter(cat => cat.category === category)
    .map(cat => cat.prefix)
    .sort();
}

// Keep old functions for backward compatibility if needed elsewhere
export function getUniqueSubcategories(): string[] {
  const subcategories = new Set(indexCategories.map(cat => cat.subcategory));
  return Array.from(subcategories).sort();
}

export function getIndicesBySubcategory(subcategory: string): string[] {
  return indexCategories
    .filter(cat => cat.subcategory === subcategory)
    .map(cat => cat.prefix)
    .sort();
}