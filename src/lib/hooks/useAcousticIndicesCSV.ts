import { useState, useEffect } from 'react';
import Papa from 'papaparse';

export interface AcousticIndicesRecord {
  Date: string;
  Filename: string;
  [key: string]: string | number;
}

interface UseAcousticIndicesOptions {
  station: string;
  bandwidth: string;
}

export function useAcousticIndicesCSV({ station, bandwidth }: UseAcousticIndicesOptions) {
  const [data, setData] = useState<AcousticIndicesRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!station || !bandwidth) {
      setData([]);
      setLoading(false);
      return;
    }

    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const filename = `Acoustic_Indices_${station}_2021_${bandwidth}_v2_Final.csv`;
        
        // Use CDN URL with correct path structure
        const cdnBase = process.env.NEXT_PUBLIC_DATA_URL || '';
        const url = `${cdnBase}/raw-data/indices/${filename}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
          throw new Error(`Failed to load acoustic indices data: ${response.statusText}`);
        }

        const text = await response.text();
        
        Papa.parse(text, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          complete: (results) => {
            if (results.errors.length > 0) {
              console.warn('CSV parsing warnings:', results.errors);
            }
            setData(results.data as AcousticIndicesRecord[]);
            setLoading(false);
          },
          error: (error: Error) => {
            setError(`Failed to parse CSV: ${error.message}`);
            setLoading(false);
          }
        });

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setLoading(false);
      }
    };

    loadData();
  }, [station, bandwidth]);

  return { data, loading, error };
}