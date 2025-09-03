import { useState, useEffect } from 'react';

export interface PCAComponent {
  component: string;
  component_number: number;
  explained_variance: number;
  cumulative_variance: number;
}

export interface LoadingsData {
  index: string;
  component: string;
  loading: number;
  abs_loading: number;
}

export interface ComponentInterpretation {
  explained_variance_percent: number;
  top_positive_loadings: string[];
  top_negative_loadings: string[];
  interpretation: string;
}

export interface PCAAnalysisData {
  summary: {
    total_indices: number;
    total_samples: number;
    components_analyzed: number;
    components_for_80_percent: number;
    components_for_90_percent: number;
    variance_explained_top_5: number;
  };
  scree_plot: PCAComponent[];
  loadings_heatmap: {
    data: LoadingsData[];
    indices: string[];
    components: string[];
    metadata: {
      top_components: number;
      top_indices_count: number;
      explained_variance: number[];
    };
  };
  component_interpretation: {
    [key: string]: ComponentInterpretation;
  };
  metadata: {
    analysis_date: string;
    method: string;
    preprocessing: string;
    feature_selection: string;
  };
}

export function usePCAAnalysis() {
  const [data, setData] = useState<PCAAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';
        const response = await fetch(`${CDN_BASE_URL}/views/pca_analysis.json`);
        
        if (!response.ok) {
          throw new Error(`Failed to load PCA analysis data: ${response.status}`);
        }
        
        const pcaData = await response.json();
        setData(pcaData);
      } catch (err) {
        console.error('Error loading PCA analysis data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load PCA analysis data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return { data, loading, error };
}