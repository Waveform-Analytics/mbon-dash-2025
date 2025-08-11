/**
 * React hooks for data loading with proper loading states
 */

import { useState, useEffect } from 'react';
import type { 
  DetectionRecord as Detection
} from '@/types/data';

// Use proxy in development to bypass CORS
const DATA_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? '/api/cdn'  // Use local proxy in development
  : (process.env.NEXT_PUBLIC_DATA_URL || 'http://localhost:3000/data');

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

// Simple fetch wrapper
async function fetchData<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${DATA_URL}/processed/${endpoint}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
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