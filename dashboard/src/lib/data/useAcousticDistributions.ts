/**
 * Hook for acoustic indices distributions data using progressive loading
 */

import { useState, useEffect } from 'react';
import { AcousticIndicesDistributionsData } from '@/types/data';

interface UseAcousticDistributionsParams {
  index?: string;
  station?: string;
  bandwidth?: string;
  category?: string;
}

interface UseAcousticDistributionsResult {
  distributionsData: AcousticIndicesDistributionsData | null;
  loading: boolean;
  error: Error | null;
  // Helper methods for filtering and data access
  getAvailableIndices: () => string[];
  getIndicesMetadata: () => Record<string, any>;
  getFilterOptions: () => { stations: string[]; bandwidths: string[]; years: number[]; available_combinations: any[] };
  getDistributionForIndex: (indexName: string) => any;
  getStationsWithData: (indexName: string) => string[];
}

export function useAcousticDistributions(params: UseAcousticDistributionsParams = {}): UseAcousticDistributionsResult {
  const [data, setData] = useState<AcousticIndicesDistributionsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isCancelled = false;
    
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Build query parameters
        const searchParams = new URLSearchParams();
        
        if (params.index) searchParams.set('index', params.index);
        if (params.station) searchParams.set('station', params.station);
        if (params.bandwidth) searchParams.set('bandwidth', params.bandwidth);
        if (params.category) searchParams.set('category', params.category);
        
        const apiUrl = `/api/acoustic-distributions?${searchParams.toString()}`;
        console.log(`useAcousticDistributions: Loading from ${apiUrl}`);
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`Failed to load acoustic distributions: ${response.statusText}`);
        }
        
        const result: AcousticIndicesDistributionsData = await response.json();
        
        if (!isCancelled) {
          setData(result);
          console.log(`useAcousticDistributions: Loaded ${result.metadata?.total_indices || 0} indices in ${result.metadata?.processing_time_ms}ms`);
        }
      } catch (err) {
        console.error('useAcousticDistributions: Error loading data:', err);
        if (!isCancelled) {
          setError(err instanceof Error ? err : new Error('Unknown error'));
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    loadData();
    
    return () => {
      isCancelled = true;
    };
  }, [params.index, params.station, params.bandwidth, params.category]);

  return {
    distributionsData: data,
    loading,
    error,
    // Helper methods for filtering and data access
    getAvailableIndices: () => data ? Object.keys(data.distributions) : [],
    getIndicesMetadata: () => data?.indices_metadata || {},
    getFilterOptions: () => data?.filters || { stations: [], bandwidths: [], years: [], available_combinations: [] },
    getDistributionForIndex: (indexName: string) => data?.distributions[indexName] || {},
    getStationsWithData: (indexName: string) => {
      if (!data?.distributions[indexName]) return [];
      return Object.keys(data.distributions[indexName]);
    },
  };
}