/**
 * Hook for heatmap data using progressive loading
 */

import { useState, useEffect } from 'react';

interface HeatmapDataPoint {
  station: string;
  year: number;
  species: string;
  detections_count?: number;
  date?: string;
  [key: string]: any;
}

interface HeatmapData {
  metadata: {
    generated_at?: string;
    version?: string;
    data_sources?: string[];
    total_records: number;
    filtered_records: number;
    processing_time_ms: number;
    stations: string[];
    years: number[];
    detection_types: Array<{
      long_name: string;
      short_name: string;
      type: string;
    }>;
    value_ranges: Record<string, [number, number]>;
    hours: number[];
    filters_applied: {
      station: string | null;
      year: string | null;
      species: string | null;
      limit: number | null;
      offset: number;
    };
  };
  data: HeatmapDataPoint[];
}

interface UseHeatmapDataParams {
  station?: string;
  year?: string | number;
  species?: string;
  limit?: number;
  offset?: number;
}

interface UseHeatmapDataResult {
  data: HeatmapDataPoint[] | null;
  metadata: HeatmapData['metadata'] | null;
  loading: boolean;
  error: Error | null;
}

export function useHeatmapData(params: UseHeatmapDataParams = {}): UseHeatmapDataResult {
  const [data, setData] = useState<HeatmapDataPoint[] | null>(null);
  const [metadata, setMetadata] = useState<HeatmapData['metadata'] | null>(null);
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
        
        if (params.station) searchParams.set('station', params.station);
        if (params.year) searchParams.set('year', params.year.toString());
        if (params.species) searchParams.set('species', params.species);
        if (params.limit) searchParams.set('limit', params.limit.toString());
        if (params.offset) searchParams.set('offset', params.offset.toString());
        
        const apiUrl = `/api/heatmap-data?${searchParams.toString()}`;
        console.log(`useHeatmapData: Loading from ${apiUrl}`);
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
          throw new Error(`Failed to load heatmap data: ${response.statusText}`);
        }
        
        const result: HeatmapData = await response.json();
        
        if (!isCancelled) {
          setData(result.data);
          setMetadata(result.metadata);
          console.log(`useHeatmapData: Loaded ${result.data.length} records in ${result.metadata.processing_time_ms}ms`);
        }
      } catch (err) {
        console.error('useHeatmapData: Error loading data:', err);
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
  }, [params.station, params.year, params.species, params.limit, params.offset]);

  return { data, metadata, loading, error };
}