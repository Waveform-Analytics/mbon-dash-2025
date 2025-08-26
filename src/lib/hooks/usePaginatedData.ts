/**
 * React hooks for paginated data loading with performance optimization
 */

import { useState, useEffect, useCallback, useMemo } from 'react';

// Use proxy in development to bypass CORS
const DATA_URL = typeof window !== 'undefined' && window.location.hostname === 'localhost'
  ? '/api/cdn'  // Use local proxy in development
  : (process.env.NEXT_PUBLIC_DATA_URL || 'http://localhost:3000/data');

interface PaginationInfo {
  page: number;
  filename: string;
  records: number;
  start_index: number;
  end_index: number;
  date_range?: {
    start: string;
    end: string;
  };
}

interface PaginationMetadata {
  dataset: string;
  total_records: number;
  total_pages: number;
  page_size: number;
  sorted_by?: string;
  generated_at: string;
  pages: PaginationInfo[];
}

interface SummaryData<T> {
  dataset: string;
  sample_records: T[];
  summary_info: {
    total_records: number;
    total_pages: number;
    sample_size: number;
    pagination_available: boolean;
  };
  pagination_index: string;
  generated_at: string;
}

interface UsePaginatedDataResult<T> {
  // Data
  data: T[];
  summary: SummaryData<T> | null;
  metadata: PaginationMetadata | null;
  
  // Loading states
  loading: boolean;
  loadingPage: number | null;
  
  // Pagination state
  currentPage: number;
  totalPages: number;
  totalRecords: number;
  
  // Actions
  loadPage: (page: number) => Promise<void>;
  loadNextPage: () => Promise<void>;
  loadPreviousPage: () => Promise<void>;
  loadRange: (startPage: number, endPage: number) => Promise<void>;
  refetch: () => void;
  
  // Status
  error: Error | null;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  loadedPages: Set<number>;
}

// Simple fetch wrapper
async function fetchPaginatedData<T>(endpoint: string): Promise<T> {
  const cacheBuster = process.env.NODE_ENV === 'development' ? `?t=${Date.now()}` : '';
  const response = await fetch(`${DATA_URL}/processed/paginated/${endpoint}${cacheBuster}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Hook for loading paginated datasets with smart caching and preloading
 */
export function usePaginatedData<T = any>(
  datasetName: string,
  options: {
    initialPage?: number;
    preloadNext?: boolean;
    cacheSize?: number;
  } = {}
): UsePaginatedDataResult<T> {
  
  const { initialPage = 1, preloadNext = true, cacheSize = 10 } = options;
  
  // State management
  const [summary, setSummary] = useState<SummaryData<T> | null>(null);
  const [metadata, setMetadata] = useState<PaginationMetadata | null>(null);
  const [pageCache, setPageCache] = useState<Map<number, T[]>>(new Map());
  const [loadedPages, setLoadedPages] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [loading, setLoading] = useState(true);
  const [loadingPage, setLoadingPage] = useState<number | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  // Initialize: Load summary and metadata
  const initialize = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [summaryData, metadataData] = await Promise.all([
        fetchPaginatedData<SummaryData<T>>(`${datasetName}_summary.json`),
        fetchPaginatedData<PaginationMetadata>(`${datasetName}_pagination_index.json`)
      ]);
      
      setSummary(summaryData);
      setMetadata(metadataData);
      
      // Initialize cache with summary data
      const initialCache = new Map<number, T[]>();
      initialCache.set(0, summaryData.sample_records); // Page 0 = summary/sample
      setPageCache(initialCache);
      
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [datasetName]);
  
  // Load a specific page
  const loadPage = useCallback(async (page: number) => {
    if (!metadata || loadedPages.has(page) || page < 1 || page > metadata.total_pages) {
      return;
    }
    
    try {
      setLoadingPage(page);
      setError(null);
      
      const pageInfo = metadata.pages[page - 1]; // pages array is 0-indexed
      const pageData = await fetchPaginatedData<T[]>(pageInfo.filename);
      
      setPageCache(prev => {
        const newCache = new Map(prev);
        newCache.set(page, pageData);
        
        // Implement LRU cache cleanup if cache size exceeded
        if (newCache.size > cacheSize) {
          const oldestKey = newCache.keys().next().value;
          if (oldestKey !== undefined && oldestKey !== currentPage) { // Don't remove current page
            newCache.delete(oldestKey);
          }
        }
        
        return newCache;
      });
      
      setLoadedPages(prev => new Set(prev).add(page));
      
      // Preload next page if enabled
      if (preloadNext && metadata && page < metadata.total_pages && !loadedPages.has(page + 1)) {
        setTimeout(() => loadPage(page + 1), 100); // Small delay
      }
      
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoadingPage(null);
    }
  }, [metadata, loadedPages, cacheSize, preloadNext, currentPage]);
  
  // Navigation actions
  const loadNextPage = useCallback(async () => {
    if (metadata && currentPage < metadata.total_pages) {
      const nextPage = currentPage + 1;
      await loadPage(nextPage);
      setCurrentPage(nextPage);
    }
  }, [currentPage, metadata, loadPage]);
  
  const loadPreviousPage = useCallback(async () => {
    if (currentPage > 1) {
      const prevPage = currentPage - 1;
      await loadPage(prevPage);
      setCurrentPage(prevPage);
    }
  }, [currentPage, loadPage]);
  
  // Load multiple pages at once
  const loadRange = useCallback(async (startPage: number, endPage: number) => {
    if (!metadata) return;
    
    const validStart = Math.max(1, startPage);
    const validEnd = Math.min(metadata.total_pages, endPage);
    
    const loadPromises = [];
    for (let page = validStart; page <= validEnd; page++) {
      if (!loadedPages.has(page)) {
        loadPromises.push(loadPage(page));
      }
    }
    
    await Promise.all(loadPromises);
  }, [metadata, loadedPages, loadPage]);
  
  // Computed values
  const data = useMemo(() => {
    if (currentPage === 0) {
      // Return summary data
      return summary?.sample_records || [];
    }
    return pageCache.get(currentPage) || [];
  }, [currentPage, pageCache, summary]);
  
  const hasNextPage = useMemo(() => 
    metadata ? currentPage < metadata.total_pages : false,
    [currentPage, metadata]
  );
  
  const hasPreviousPage = useMemo(() => 
    currentPage > 1,
    [currentPage]
  );
  
  // Initialize on mount
  useEffect(() => {
    initialize();
  }, [initialize]);
  
  // Load initial page after initialization
  useEffect(() => {
    if (metadata && !loadedPages.has(initialPage)) {
      loadPage(initialPage);
      setCurrentPage(initialPage);
    }
  }, [metadata, initialPage, loadedPages, loadPage]);
  
  return {
    // Data
    data,
    summary,
    metadata,
    
    // Loading states
    loading,
    loadingPage,
    
    // Pagination state
    currentPage,
    totalPages: metadata?.total_pages || 0,
    totalRecords: metadata?.total_records || 0,
    
    // Actions
    loadPage,
    loadNextPage, 
    loadPreviousPage,
    loadRange,
    refetch: initialize,
    
    // Status
    error,
    hasNextPage,
    hasPreviousPage,
    loadedPages
  };
}

/**
 * Hook for loading acoustic indices with pagination
 */
export function usePaginatedAcousticIndices(options = {}) {
  return usePaginatedData('acoustic_indices', options);
}

/**
 * Hook for loading environmental data with pagination
 */
export function usePaginatedEnvironmental(options = {}) {
  return usePaginatedData('environmental', options);
}

/**
 * Hook for loading detection data with pagination
 */
export function usePaginatedDetections(options = {}) {
  return usePaginatedData('detections', options);
}