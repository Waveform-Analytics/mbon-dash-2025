'use client';

/**
 * Custom hook for loading optimized view data from CDN.
 * 
 * This hook provides type-safe loading of dashboard view files with:
 * - Loading states
 * - Error handling 
 * - Type inference based on view type
 * - Automatic URL construction
 */

import { useState, useEffect } from 'react';
import type { ViewType, StationOverviewData, SpeciesTimelineData, AcousticSummaryData } from '@/types/data';

// Type mapping for different view types
type ViewDataMap = {
  'station-overview': StationOverviewData;
  'species-timeline': SpeciesTimelineData;
  'acoustic-summary': AcousticSummaryData;
};

// URL mapping for view types to file names
const VIEW_FILE_MAP: Record<ViewType, string> = {
  'station-overview': 'station_overview.json',
  'species-timeline': 'species_timeline.json',
  'acoustic-summary': 'acoustic_summary.json',
};

// Valid view types for runtime validation
const VALID_VIEW_TYPES: ViewType[] = ['station-overview', 'species-timeline', 'acoustic-summary'];

interface UseViewDataResult<T extends ViewType> {
  data: ViewDataMap[T] | null;
  loading: boolean;
  error: string | null;
}

/**
 * Hook to load view-specific data from CDN
 * 
 * @param viewType - The type of view data to load
 * @returns Object with data, loading state, and error state
 */
export function useViewData<T extends ViewType>(viewType: T): UseViewDataResult<T> {
  const [data, setData] = useState<ViewDataMap[T] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Reset states when view type changes
    setData(null);
    setError(null);
    setLoading(true);

    // Validate view type
    if (!VALID_VIEW_TYPES.includes(viewType)) {
      setError(`Invalid view type: ${viewType}`);
      setLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        const fileName = VIEW_FILE_MAP[viewType];
        // Use relative URL if no base URL is set (local development)
        const baseUrl = process.env.NEXT_PUBLIC_DATA_URL;
        const url = baseUrl ? `${baseUrl}/views/${fileName}` : `/views/${fileName}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`${response.status} ${response.statusText}`);
        }
        
        const jsonData = await response.json();
        setData(jsonData);
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setError(`Failed to load ${viewType} data: ${errorMessage}`);
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [viewType]);

  return { data, loading, error };
}

// Convenience hooks for specific view types
export function useStationOverview() {
  return useViewData('station-overview');
}

export function useSpeciesTimeline() {
  return useViewData('species-timeline');
}

export function useAcousticSummary() {
  return useViewData('acoustic-summary');
}