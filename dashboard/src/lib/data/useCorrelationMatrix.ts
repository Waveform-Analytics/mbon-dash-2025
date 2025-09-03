import { useState, useEffect } from 'react';

interface CorrelationDataPoint {
  x: string;
  y: string;
  value: number;
  x_index: number;
  y_index: number;
  is_high_corr: boolean;
  is_diagonal: boolean;
}

export interface CorrelationMatrixData {
  metadata: {
    generated_at: string;
    description: string;
    threshold: number;
    method: string;
    data_source: string;
  };
  indices: string[];
  matrix_data: CorrelationDataPoint[];
  high_correlations: Array<{
    index1: string;
    index2: string;
    correlation: number;
    abs_correlation: number;
  }>;
  suggested_removals: string[];
  statistics: {
    total_indices: number;
    total_pairs: number;
    high_correlation_pairs: number;
    suggested_removals: number;
    mean_abs_correlation: number;
    max_off_diagonal_correlation: number;
  };
}

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

export function useCorrelationMatrix() {
  const [data, setData] = useState<CorrelationMatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${CDN_BASE_URL}/views/correlation_matrix.json`);
        if (!response.ok) {
          throw new Error(`Failed to fetch correlation matrix: ${response.status}`);
        }
        
        const correlationData = await response.json();
        setData(correlationData);
      } catch (err) {
        console.error('Error loading correlation matrix:', err);
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return { data, loading, error };
}