/**
 * Hook for acoustic indices distributions data
 */

import { useViewData } from './useViewData';
import { AcousticIndicesDistributionsData } from '@/types/data';

export function useAcousticDistributions() {
  const { data, loading, error } = useViewData<AcousticIndicesDistributionsData>('acoustic_indices_distributions.json');
  
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