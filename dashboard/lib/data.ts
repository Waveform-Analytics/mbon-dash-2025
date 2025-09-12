/**
 * Data loading utilities for MBON Dashboard
 * Handles CDN-first loading with local fallback
 */

import React from 'react';

// Configuration
const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL;
const CDN_VIEWS_PATH = '/views';

export interface ViewDataOptions {
  timeout?: number;
  fallbackToLocal?: boolean;
}

/**
 * Load view data with CDN-first strategy and local fallback
 */
export async function loadViewData<T>(
  viewName: string, 
  options: ViewDataOptions = {}
): Promise<T> {
  const { timeout = 5000, fallbackToLocal = true } = options;
  
  console.log('[loadViewData] Starting load with params:', { viewName, options, CDN_BASE_URL });
  
  // Add .json extension if not present
  const fileName = viewName.endsWith('.json') ? viewName : `${viewName}.json`;
  console.log('[loadViewData] File name resolved to:', fileName);
  
  // Try CDN first if available
  if (CDN_BASE_URL) {
    try {
      console.log(`[loadViewData] Attempting CDN load: ${CDN_BASE_URL}${CDN_VIEWS_PATH}/${fileName}`);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      const response = await fetch(`${CDN_BASE_URL}${CDN_VIEWS_PATH}/${fileName}`, {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache', // Allow fresh data when needed
        }
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`[loadViewData] ✅ Successfully loaded ${fileName} from CDN`);
        return data;
      } else {
        throw new Error(`CDN responded with status: ${response.status}`);
      }
      
    } catch (error) {
      console.warn(`[loadViewData] CDN load failed for ${fileName}:`, error);
      
      if (!fallbackToLocal) {
        throw error;
      }
      
      console.log(`[loadViewData] Falling back to local API...`);
    }
  } else {
    console.log(`[loadViewData] No CDN URL configured, using local API only`);
  }
  
  // Fallback to local API
  if (fallbackToLocal) {
    try {
      console.log(`[Data] Attempting local load: /api/views/${fileName.replace('.json', '')}`);
      
      const response = await fetch(`/api/views/${fileName.replace('.json', '')}`);
      
      if (!response.ok) {
        throw new Error(`Local API responded with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`[Data] ✅ Successfully loaded ${fileName} from local API`);
      return data;
      
    } catch (error) {
      console.error(`[Data] ❌ Failed to load ${fileName} from both CDN and local API:`, error);
      throw new Error(`Failed to load ${fileName}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
  
  throw new Error(`Failed to load ${fileName} from CDN and fallback is disabled`);
}

/**
 * React hook for loading view data
 */
export function useViewData<T>(viewName: string, options?: ViewDataOptions) {
  console.log('[useViewData] Hook created for:', viewName);
  
  const [data, setData] = React.useState<T | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);
  const [source, setSource] = React.useState<'cdn' | 'local' | null>(null);
  
  console.log('[useViewData] Hook state:', { data: !!data, loading, error: !!error, source });

  React.useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      console.log('[useViewData] Starting to load data for:', viewName);
      try {
        setLoading(true);
        setError(null);
        
        console.log('[useViewData] Calling loadViewData with options:', options);
        const result = await loadViewData<T>(viewName, options);
        console.log('[useViewData] Data loaded successfully:', result);
        
        if (isMounted) {
          setData(result);
          // Determine source based on whether CDN was attempted
          setSource(CDN_BASE_URL ? 'cdn' : 'local');
          console.log('[useViewData] Set data and source:', { hasData: !!result, source: CDN_BASE_URL ? 'cdn' : 'local' });
        }
      } catch (err) {
        console.error('[useViewData] Error in loadData:', err);
        if (isMounted) {
          const error = err instanceof Error ? err : new Error('Unknown error');
          setError(error);
          console.error(`[useViewData] Error loading ${viewName}:`, error);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
          console.log('[useViewData] Loading set to false');
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [viewName]);

  return { data, loading, error, source };
}

/**
 * Station location data interface
 */
export interface StationLocation {
  Station: string;
  'GPS Lat': number;
  'GPS Long': number;
  total_deployments: number;
  avg_depth_m: number;
  avg_hydrophone_depth_m: number;
  current_study: boolean;
}

/**
 * Load station locations data
 */
export function loadStationLocations(): Promise<StationLocation[]> {
  return loadViewData<StationLocation[]>('stations_locations');
}

/**
 * React hook for station locations
 */
export function useStationLocations() {
  return useViewData<StationLocation[]>('stations_locations');
}