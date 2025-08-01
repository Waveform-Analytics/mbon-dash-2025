/**
 * React hooks for data loading with proper loading states
 */

import { useState, useEffect } from 'react';

const DATA_URL = process.env.NEXT_PUBLIC_DATA_URL || 'http://localhost:3000/data';

export interface Detection {
  id: string;
  file: string;
  date: string;
  time: string;
  year: string;
  station: string;
  [key: string]: any;
}

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
  const response = await fetch(`${DATA_URL}/${endpoint}`);
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