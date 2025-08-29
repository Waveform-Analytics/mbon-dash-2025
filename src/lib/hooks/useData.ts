/**
 * React hooks for data loading with proper loading states
 */

import { useState, useEffect } from 'react';
import type { 
  DetectionRecord as Detection
} from '@/types/data';

// Use local proxy in development to bypass CORS, CDN in production
const DATA_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? '/api/cdn'  // Use local proxy in development
  : (process.env.NEXT_PUBLIC_DATA_URL || 'https://waveformdata.work');

// Re-export types with compatibility aliases
export type { Detection };

export interface Station {
  id: string;
  name: string;
  coordinates: {
    lat: number;
    lon: number;
  };
  years: string[];
  data_types: string[];
}

export interface Species {
  short_name: string;
  long_name: string;
  total_detections: number;
  category: string;
}

export interface Metadata {
  generated_at: string;
  column_mapping: Record<string, string>;
  data_summary: {
    total_detections: number;
    total_environmental_records: number;
    total_acoustic_records: number;
    stations_count: number;
    species_count: number;
    date_range: {
      start: string;
      end: string;
    };
  };
}

interface UseDataResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

// Simple fetch wrapper with cache busting in development
async function fetchData<T>(endpoint: string): Promise<T> {
  // Add timestamp in development to bypass cache
  const cacheBuster = process.env.NODE_ENV === 'development' ? `?t=${Date.now()}` : '';
  const response = await fetch(`${DATA_URL}/processed/${endpoint}${cacheBuster}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
  }
  return response.json();
}

// Fetch function for optimized view files (directly from CDN)
async function fetchViewData<T>(endpoint: string): Promise<T> {
  // Add timestamp in development to bypass cache
  const cacheBuster = process.env.NODE_ENV === 'development' ? `?t=${Date.now()}` : '';
  
  // Use local proxy in development to bypass CORS, CDN in production
  const baseUrl = typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? '/api/cdn'  // Use local proxy in development
    : (process.env.NEXT_PUBLIC_DATA_URL || 'https://waveformdata.work');
  
  const response = await fetch(`${baseUrl}/${endpoint}${cacheBuster}`);
  
  if (!response.ok) {
    throw new Error(`Failed to fetch view ${endpoint}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Hook to load metadata
 */
export function useMetadata(): UseDataResult<Metadata> {
  const [data, setData] = useState<Metadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMetadata = async () => {
    try {
      setLoading(true);
      setError(null);
      const metadata = await fetchData<Metadata>('metadata.json');
      setData(metadata);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetadata();
  }, []);

  return { data, loading, error, refetch: fetchMetadata };
}

/**
 * Hook to load stations
 */
export function useStations(): UseDataResult<Station[]> {
  const [data, setData] = useState<Station[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStations = async () => {
    try {
      setLoading(true);
      setError(null);
      const stations = await fetchData<Station[]>('stations.json');
      setData(stations);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStations();
  }, []);

  return { data, loading, error, refetch: fetchStations };
}

/**
 * Hook to load species
 */
export function useSpecies(): UseDataResult<Species[]> {
  const [data, setData] = useState<Species[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchSpecies = async () => {
    try {
      setLoading(true);
      setError(null);
      const species = await fetchData<Species[]>('species.json');
      setData(species);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSpecies();
  }, []);

  return { data, loading, error, refetch: fetchSpecies };
}

/**
 * Hook to load all core data (metadata, stations, species)
 */
export function useCoreData() {
  const [data, setData] = useState<{
    metadata: Metadata | null;
    stations: Station[] | null;
    species: Species[] | null;
  }>({
    metadata: null,
    stations: null,
    species: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchCoreData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [metadata, stations, species] = await Promise.all([
        fetchData<Metadata>('metadata.json'),
        fetchData<Station[]>('stations.json'),
        fetchData<Species[]>('species.json')
      ]);
      
      setData({ metadata, stations, species });
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCoreData();
  }, []);

  return { ...data, loading, error, refetch: fetchCoreData };
}

// Tell typescript what to expect in each deployement record
export interface DeploymentMetadata {
  object_id: number;
  station: string;      // e.g., "9M", "14M", "37M"
  year: number;
  gps_lat:number;
  gps_long: number;
  start_date: string;
  end_date: string;
  depth_m: number;
  deployment_id: string;
  platform_type?: string;
  salinity_ppt?: number;
  temperature_c?: number;
}

// Hook to load deployment metadata
export function useDeploymentMetadata(): UseDataResult<DeploymentMetadata[]> {
  const [data, setData] = useState<DeploymentMetadata[] | null>(null); // The actual data
  const [loading, setLoading] = useState(true);                         // Loading indicator
  const [error, setError] = useState<Error | null>(null);               // Any errors

  // data-fetching function
  const fetchDeploymentMetadata = async () => {
    try {
      setLoading(true);
      setError(null);
      const deployments = await fetchData<DeploymentMetadata[]>('deployment_metadata.json');
      setData(deployments);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeploymentMetadata();
  }, []);

  return { data, loading, error, refetch: fetchDeploymentMetadata };
}

/**
 * Hook to load detection data for timeline heatmap
 */
export function useTimelineData() {
  const [data, setData] = useState<{
    detections: Detection[] | null;
    speciesMapping: Record<string, string>;
    deploymentMetadata: DeploymentMetadata[] | null;
  }>({
    detections: null,
    speciesMapping: {},
    deploymentMetadata: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTimelineData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [detections, metadata, deployments] = await Promise.all([
        fetchData<Detection[]>('detections.json'),
        fetchData<Metadata>('metadata.json'),
        fetchData<DeploymentMetadata[]>('deployment_metadata.json')
      ]);
      
      setData({ 
        detections, 
        speciesMapping: metadata.column_mapping,
        deploymentMetadata: deployments
      });
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimelineData();
  }, []);

  return { ...data, loading, error, refetch: fetchTimelineData };
}

/**
 * Monthly detection summary data types
 */
export interface MonthlyDetection {
  year: number;
  month: number;
  station: string;
  detection_type: string;
  count: number;
}

export interface MonthlyDetectionsData {
  monthly_summary: MonthlyDetection[];
  detection_types: string[];
  type_labels: Record<string, string>;
  metadata: {
    generated_at: string;
    description: string;
    years_included: number[];
    stations_included: string[];
    total_records: number;
  };
}

/**
 * Hook to load monthly detection aggregations for timeline visualization
 */
export function useMonthlyDetections(): UseDataResult<MonthlyDetectionsData> {
  const [data, setData] = useState<MonthlyDetectionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMonthlyDetections = async () => {
    try {
      setLoading(true);
      setError(null);
      const monthlyData = await fetchData<MonthlyDetectionsData>('monthly_detections.json');
      setData(monthlyData);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonthlyDetections();
  }, []);

  return { data, loading, error, refetch: fetchMonthlyDetections };
}

/**
 * PCA Biplot data types
 */
export interface PCAPoint {
  datetime: string;
  station: string;
  species_count: number;
  pc1: number;
  pc2: number;
  pc3: number;
  pc4: number;
  pc5: number;
  pc6: number;
  pc7: number;
  pc8: number;
}

export interface PCALoading {
  index: string;
  category: string;
  pc1: number;
  pc2: number;
  pc3: number;
  pc4: number;
  pc5: number;
  pc6: number;
  pc7: number;
  pc8: number;
}

export interface PCABiplotData {
  pca_biplot: {
    points: PCAPoint[];
    loadings: PCALoading[];
    variance_explained: number[];
    metadata: {
      total_variance: number;
      n_components: number;
      n_indices: number;
      n_observations: number;
      analysis_date: string;
      indices_used?: string[];
      temporal_aggregation?: string;
    };
    performance?: {
      original_n_indices: number;
      original_n_points: number;
      reduced_n_indices: number;
      reduced_n_points: number;
      reduction_ratio: string;
    };
    stations?: string[];
  };
  generated_at: string;
  bandwidth?: string;
  data_sources: {
    acoustic_indices_records: number;
    detection_records?: number;
    stations?: string[];
    optimization_settings?: {
      max_indices: number;
      temporal_aggregation: string;
      max_visualization_points: number;
      bandwidth?: string;
    };
  };
}

/**
 * Hook to load PCA biplot data for dimensionality analysis
 * @param bandwidth - Which bandwidth to load ('FullBW' or '8kHz')
 */
export function usePCABiplot(bandwidth: 'FullBW' | '8kHz' = 'FullBW'): UseDataResult<PCABiplotData> {
  const [data, setData] = useState<PCABiplotData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchPCABiplot = async () => {
    try {
      setLoading(true);
      setError(null);
      const filename = bandwidth === '8kHz' ? 'pca_biplot_8khz.json' : 'pca_biplot_fullbw.json';
      const pcaData = await fetchData<PCABiplotData>(filename);
      setData(pcaData);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPCABiplot();
  }, [bandwidth]);

  return { data, loading, error, refetch: fetchPCABiplot };
}

/**
 * Raw Data Landscape data types
 */
export interface IndexInfo {
  index: string;
  category: string;
  availability: Record<string, {
    available: boolean;
    station: string;
    bandwidth: string;
    n_values?: number;
    coverage_pct?: number;
    n_missing?: number;
    mean?: number;
    std?: number;
    min?: number;
    max?: number;
  }>;
}

export interface RawDataLandscapeData {
  raw_data_landscape: {
    indices_overview: IndexInfo[];
    datasets_info: Record<string, {
      station: string;
      bandwidth: string;
      n_records: number;
      filename: string;
      date_range?: {
        start: string;
        end: string;
        days: number;
      } | null;
    }>;
    summary_stats: {
      total_indices: number;
      total_datasets: number;
      category_counts: Record<string, number>;
      coverage_percentage: number;
      station_stats: Record<string, any>;
      bandwidth_stats: Record<string, any>;
      missing_patterns: {
        indices_missing_from_all: string[];
        indices_in_all: string[];
      };
    };
    metadata: {
      analysis_date: string;
      description: string;
      purpose: string;
    };
  };
  generated_at: string;
}

/**
 * Hook to load raw data landscape for Step 1A visualization
 */
export function useRawDataLandscape(): UseDataResult<RawDataLandscapeData> {
  const [data, setData] = useState<RawDataLandscapeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchRawDataLandscape = async () => {
    try {
      setLoading(true);
      setError(null);
      // Updated to use optimized view from views endpoint (32KB vs 100KB+)
      const landscapeData = await fetchViewData<RawDataLandscapeData>('views/raw_data_landscape.json');
      setData(landscapeData);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRawDataLandscape();
  }, []);

  return { data, loading, error, refetch: fetchRawDataLandscape };
}

/**
 * Index Distributions data types (with bandwidth separation)
 */
export interface IndexAnalysis {
  index: string;
  category: string;
  bandwidth: string;
  combined_stats: {
    mean: number;
    std: number;
    skewness: number;
    zero_pct: number;
    missing_pct: number;
    outlier_pct: number;
    distribution_type: string;
    min: number;
    max: number;
  };
  combined_density: {
    x: number[];           // Normalized 0-1 x values
    density: number[];     // PDF density values
    x_original: number[];  // Original x values
  };
  quality_metrics: {
    missing_pct: number;
    zero_pct: number;
    skewness_abs: number;
    outlier_pct: number;
    std: number;
    distribution_type: string;
  };
}

export interface BandwidthSummary {
  total_indices: number;
  distribution_type_counts: Record<string, number>;
  category_counts: Record<string, number>;
  raw_metrics_summary: {
    skewness_median: number;
    zero_pct_median: number;
    missing_pct_median: number;
    highly_skewed_count: number;
    zero_heavy_count: number;
    missing_heavy_count: number;
  };
}

export interface IndexDistributionsData {
  index_distributions_by_bandwidth: Record<string, IndexAnalysis[]>;
  summary_stats_by_bandwidth: Record<string, BandwidthSummary>;
  available_bandwidths: string[];
  metadata: {
    analysis_date: string;
    description: string;
    purpose: string;
    total_indices_analyzed: number;
    datasets_included: number;
    bandwidths_analyzed: string[];
    visualization_type: string;
    normalization: string;
  };
  generated_at: string;
}

/**
 * Hook to load index distributions for quality analysis
 */
export function useIndexDistributions(): UseDataResult<IndexDistributionsData> {
  const [data, setData] = useState<IndexDistributionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchIndexDistributions = async () => {
    try {
      setLoading(true);
      setError(null);
      // Updated to use optimized view from CDN (119KB vs 2.8MB = 23x smaller!)
      const distributionsData = await fetchViewData<IndexDistributionsData>('views/index_distributions.json');
      setData(distributionsData);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndexDistributions();
  }, []);

  return { data, loading, error, refetch: fetchIndexDistributions };
}