/**
 * Hook for loading view data from CDN or local API
 */

import { useState, useEffect } from 'react';

interface UseViewDataResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useViewData<T>(viewName: string): UseViewDataResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isCancelled = false;
    console.log(`useViewData: useEffect triggered for ${viewName}`);
    
    const loadData = async () => {
      try {
        console.log(`useViewData: Loading ${viewName}`);
        setLoading(true);
        setError(null);
        
        // Try CDN first, fallback to local API
        const cdnUrl = process.env.NEXT_PUBLIC_CDN_BASE_URL;
        const apiUrl = `/api/views/${viewName}`;
        
        let response: Response;
        let dataSource: 'cdn' | 'local' = 'local';
        
        if (cdnUrl) {
          // Try CDN first
          try {
            const fullCdnUrl = `${cdnUrl}/views/${viewName}`;
            console.log(`useViewData: Attempting CDN request to: ${fullCdnUrl}`);
            const cdnResponse = await fetch(fullCdnUrl);
            console.log(`useViewData: CDN response status: ${cdnResponse.status} for ${viewName}`);
            if (cdnResponse.ok) {
              response = cdnResponse;
              dataSource = 'cdn';
              console.log(`useViewData: Successfully loading from CDN: ${fullCdnUrl}`);
            } else {
              throw new Error(`CDN returned ${cdnResponse.status}: ${cdnResponse.statusText}`);
            }
          } catch (cdnError) {
            console.warn(`useViewData: CDN failed for ${viewName}, falling back to local API:`, cdnError);
            response = await fetch(apiUrl);
            dataSource = 'local';
          }
        } else {
          // Use local API only
          console.log(`useViewData: CDN URL not set, using local API: ${apiUrl}`);
          response = await fetch(apiUrl);
          dataSource = 'local';
        }
        
        console.log(`useViewData: Response status for ${viewName}:`, response.status, `(from ${dataSource})`);
        
        if (!response.ok) {
          throw new Error(`Failed to load ${viewName}: ${response.statusText}`);
        }
        
        const jsonData = await response.json();
        console.log(`useViewData: Successfully loaded ${viewName} from ${dataSource}:`, {
          dataType: typeof jsonData,
          hasData: !!jsonData,
          keys: jsonData ? Object.keys(jsonData) : 'no data',
          dataSize: JSON.stringify(jsonData).length
        });
        
        if (!isCancelled) {
          setData(jsonData);
        }
      } catch (err) {
        console.error(`useViewData: Error loading ${viewName}:`, err);
        if (!isCancelled) {
          setError(err instanceof Error ? err : new Error('Unknown error'));
        }
      } finally {
        if (!isCancelled) {
          console.log(`useViewData: Setting loading=false for ${viewName}`);
          setLoading(false);
        }
      }
    };

    loadData();
    
    return () => {
      isCancelled = true;
    };
  }, [viewName]);

  return { data, loading, error };
}