/**
 * Custom hook for managing acoustic indices heatmap data
 * Handles data fetching, caching, and state management
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface HeatmapDataPoint {
  date: string;
  hour: number;
  value: number;
  index_name: string;
  station: string;
  year: number;
  bandwidth: string;
}

interface HeatmapMetadata {
  available_indices: string[];
  stations: string[];
  years: number[];
  bandwidths: string[];
  value_ranges: Record<string, [number, number]>;
  filtered_records: number;
  processing_time_ms: number;
  memory_used_bytes: number;
}

interface HeatmapData {
  metadata: HeatmapMetadata;
  data: HeatmapDataPoint[];
}

interface UseIndicesHeatmapParams {
  index?: string;
  station?: string;
  year?: number;
  bandwidth?: string;
}

interface UseIndicesHeatmapResult {
  data: HeatmapData | null;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
  metadata: HeatmapMetadata | null;
}

// Cache for storing fetched data
const cache = new Map<string, { data: HeatmapData; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Cache for metadata
const metadataCache = new Map<string, { data: HeatmapMetadata; timestamp: number }>();

// Request deduplication
const pendingRequests = new Map<string, Promise<HeatmapData>>();
const pendingMetadataRequests = new Map<string, Promise<HeatmapMetadata>>();

function getCacheKey(params: UseIndicesHeatmapParams): string {
  return `${params.index || 'default'}-${params.station || 'default'}-${params.year || 'default'}-${params.bandwidth || 'default'}`;
}

function getCachedData(key: string): HeatmapData | null {
  const cached = cache.get(key);
  if (!cached) return null;
  
  if (Date.now() - cached.timestamp > CACHE_TTL) {
    cache.delete(key);
    return null;
  }
  
  return cached.data;
}

function setCachedData(key: string, data: HeatmapData): void {
  cache.set(key, { data, timestamp: Date.now() });
}

function getCachedMetadata(key: string): HeatmapMetadata | null {
  const cached = metadataCache.get(key);
  if (!cached) return null;
  
  if (Date.now() - cached.timestamp > CACHE_TTL) {
    metadataCache.delete(key);
    return null;
  }
  
  return cached.data;
}

function setCachedMetadata(key: string, data: HeatmapMetadata): void {
  metadataCache.set(key, { data, timestamp: Date.now() });
}

async function fetchMetadata(): Promise<HeatmapMetadata> {
  const cacheKey = 'metadata';
  
  // Check cache first
  const cached = getCachedMetadata(cacheKey);
  if (cached) {
    console.log('Cache hit for metadata');
    return cached;
  }
  
  // Check if request is already pending
  if (pendingMetadataRequests.has(cacheKey)) {
    console.log('Metadata request already pending');
    return pendingMetadataRequests.get(cacheKey)!;
  }
  
  // Create new request
  const requestPromise = (async () => {
    try {
      console.log('Fetching metadata');
      
      // Use default parameters to get metadata
      const searchParams = new URLSearchParams({
        index: 'ACI',
        station: '14M',
        year: '2021',
        bandwidth: 'FullBW',
      });
      
      const response = await fetch(`/api/indices-heatmap?${searchParams}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: HeatmapData = await response.json();
      
      // Cache the metadata
      setCachedMetadata(cacheKey, data.metadata);
      
      console.log('Successfully fetched metadata');
      
      return data.metadata;
    } finally {
      // Clean up pending request
      pendingMetadataRequests.delete(cacheKey);
    }
  })();
  
  // Store the pending request
  pendingMetadataRequests.set(cacheKey, requestPromise);
  
  return requestPromise;
}

async function fetchHeatmapData(params: UseIndicesHeatmapParams): Promise<HeatmapData> {
  const cacheKey = getCacheKey(params);
  
  // Check cache first
  const cached = getCachedData(cacheKey);
  if (cached) {
    console.log(`Cache hit for ${cacheKey}`);
    return cached;
  }
  
  // Check if request is already pending
  if (pendingRequests.has(cacheKey)) {
    console.log(`Request already pending for ${cacheKey}`);
    return pendingRequests.get(cacheKey)!;
  }
  
  // Create new request
  const requestPromise = (async () => {
    try {
      console.log(`Fetching heatmap data for ${cacheKey}`);
      
      const searchParams = new URLSearchParams({
        index: params.index || 'ACI',
        station: params.station || '14M',
        year: (params.year || 2021).toString(),
        bandwidth: params.bandwidth || 'FullBW',
      });
      
      const response = await fetch(`/api/indices-heatmap?${searchParams}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data: HeatmapData = await response.json();
      
      console.log(`useIndicesHeatmap: Raw API response:`, {
        hasData: !!data,
        hasDataArray: !!data.data,
        dataLength: data?.data?.length,
        hasMetadata: !!data.metadata,
        processingTime: data?.metadata?.processing_time_ms
      });
      
      // Cache the result
      setCachedData(cacheKey, data);
      
      console.log(`Successfully fetched heatmap data: ${data.data.length} records, ${data.metadata.processing_time_ms}ms`);
      
      return data;
    } finally {
      // Clean up pending request
      pendingRequests.delete(cacheKey);
    }
  })();
  
  // Store the pending request
  pendingRequests.set(cacheKey, requestPromise);
  
  return requestPromise;
}

export function useIndicesHeatmap(params: UseIndicesHeatmapParams = {}): UseIndicesHeatmapResult {
  const [data, setData] = useState<HeatmapData | null>(null);
  const [loading, setLoading] = useState(true); // Start with loading true
  const [error, setError] = useState<Error | null>(null);
  const [metadata, setMetadata] = useState<HeatmapMetadata | null>(null);
  
  const paramsRef = useRef(params);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // Update params ref when params change
  useEffect(() => {
    paramsRef.current = params;
  }, [params]);
  
  
  const fetchData = useCallback(async () => {
    const currentParams = paramsRef.current;
    
    console.log('useIndicesHeatmap: fetchData called with params:', currentParams);
    
    // Clear data immediately when parameters change to prevent showing stale data
    setData(null);
    setLoading(true);
    setError(null);
    
    // If we don't have all parameters, just fetch metadata
    if (!currentParams.index || !currentParams.station || !currentParams.year || !currentParams.bandwidth || 
        currentParams.index === '' || currentParams.station === '' || currentParams.year === 0 || currentParams.bandwidth === '') {
      console.log('useIndicesHeatmap: No complete parameters, fetching metadata only');
      
      try {
        const metadataResult = await fetchMetadata();
        setMetadata(metadataResult);
        // Data remains null - already cleared above
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error occurred');
        setError(error);
        setMetadata(null);
        console.error('Error fetching metadata:', error);
      } finally {
        setLoading(false);
      }
      return;
    }
    
    console.log('useIndicesHeatmap: Have complete parameters, fetching data');
    
    try {
      const result = await fetchHeatmapData(currentParams);
      
      console.log(`useIndicesHeatmap: fetchData received result:`, {
        hasResult: !!result,
        resultDataLength: result?.data?.length
      });
      
      console.log(`useIndicesHeatmap: Setting data state with ${result.data.length} records`);
      setData(result);
      setMetadata(result.metadata);
      setError(null);
      
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error occurred');
      setError(error);
      setData(null);
      setMetadata(null);
      console.error('Error fetching heatmap data:', error);
    } finally {
      setLoading(false);
    }
  }, []);  // Remove dependency on fetchMetadataCallback to avoid recreating on every render
  
  // Fetch data when parameters change
  useEffect(() => {
    console.log('useIndicesHeatmap: Parameters changed, refetching data');
    fetchData();
    
    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [params.index, params.station, params.year, params.bandwidth, fetchData]);  // Re-fetch when any parameter changes
  
  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);
  
  return {
    data,
    loading,
    error,
    refetch,
    metadata,
  };
}

// Export types for use in components
export type { HeatmapData, HeatmapDataPoint, HeatmapMetadata, UseIndicesHeatmapParams };
