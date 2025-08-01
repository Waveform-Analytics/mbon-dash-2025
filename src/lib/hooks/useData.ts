/**
 * React hooks for data loading with proper loading states
 */

import { useState, useEffect } from 'react';
import DataLoader, { Detection, Station, Species, Metadata } from '@/lib/data/dataLoader';

interface UseDataResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

/**
 * Hook to load metadata
 */
export function useMetadata(): UseDataResult<Metadata> {
  const [data, setData] = useState<Metadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const metadata = await DataLoader.loadMetadata();
      setData(metadata);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook to load stations
 */
export function useStations(): UseDataResult<Station[]> {
  const [data, setData] = useState<Station[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const stations = await DataLoader.loadStations();
      setData(stations);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook to load species
 */
export function useSpecies(): UseDataResult<Species[]> {
  const [data, setData] = useState<Species[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const species = await DataLoader.loadSpecies();
      setData(species);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

/**
 * Hook to load detections (large dataset)
 */
export function useDetections(): UseDataResult<Detection[]> {
  const [data, setData] = useState<Detection[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const detections = await DataLoader.loadDetections();
      setData(detections);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
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

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const coreData = await DataLoader.loadCoreData();
      setData(coreData);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { ...data, loading, error, refetch: fetchData };
}