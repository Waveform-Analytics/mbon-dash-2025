import { NextRequest, NextResponse } from 'next/server';

interface CorrelationData {
  metadata?: {
    generated_at: string;
    version: string;
    data_sources: string[];
    total_correlations: number;
    method?: string;
    processing_time_ms?: number;
    filters_applied?: any;
    processing_info?: {
      indices_count: number;
      stations: string[];
      bandwidths: string[];
    };
  };
  correlation_matrix?: {
    [station: string]: {
      [bandwidth: string]: {
        indices: string[];
        matrix: number[][];
        p_values?: number[][];
        sample_sizes?: number[][];
      };
    };
  };
  matrix_data?: {
    [station: string]: {
      [bandwidth: string]: {
        indices: string[];
        matrix: number[][];
      };
    };
  };
  indices?: string[];
  statistics?: {
    total_indices: number;
    total_pairs: number;
    high_correlation_pairs: number;
    suggested_removals: number;
    mean_abs_correlation: number;
    max_off_diagonal_correlation: number;
    correlation_distribution?: {
      bins: number[];
      counts: number[];
    };
  };
  high_correlations?: Array<{
    index1: string;
    index2: string;
    correlation: number;
    abs_correlation: number;
  }>;
  suggested_removals?: string[];
  indices_metadata?: Record<string, {
    name: string;
    category: string;
    description?: string;
  }>;
}

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

// Cache large file in memory
let correlationData: CorrelationData | null = null;
let lastLoadTime = 0;
const CACHE_TTL = 60 * 60 * 1000; // 1 hour cache

async function loadCorrelationData(): Promise<CorrelationData> {
  const now = Date.now();
  
  // Return cached data if still valid
  if (correlationData && (now - lastLoadTime) < CACHE_TTL) {
    return correlationData;
  }
  
  console.log('Loading correlation matrix data from CDN...');
  const response = await fetch(`${CDN_BASE_URL}/processed/correlation_matrix.json`);
  
  if (!response.ok) {
    throw new Error(`Failed to load correlation data: ${response.statusText}`);
  }
  
  correlationData = await response.json();
  lastLoadTime = now;
  
  console.log(`Correlation data loaded: ${Object.keys(correlationData?.correlation_matrix || {}).length} stations`);
  return correlationData!;
}

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const { searchParams } = new URL(request.url);
    
    // Extract filter parameters
    const station = searchParams.get('station');
    const bandwidth = searchParams.get('bandwidth');
    const threshold = searchParams.get('threshold'); // correlation threshold filter
    const includeMetadata = searchParams.get('include_metadata') !== 'false';
    
    // Load full dataset
    const fullData = await loadCorrelationData();
    
    // Handle both old and new data structures
    let filteredMatrix = fullData.correlation_matrix || fullData.matrix_data || {};
    
    // Filter by station
    if (station) {
      if (filteredMatrix[station]) {
        filteredMatrix = { [station]: filteredMatrix[station] };
      } else {
        filteredMatrix = {};
      }
    }
    
    // Filter by bandwidth within each station
    if (bandwidth) {
      const bandwidthFiltered: typeof filteredMatrix = {};
      
      for (const [stationName, stationData] of Object.entries(filteredMatrix)) {
        if (stationData[bandwidth]) {
          bandwidthFiltered[stationName] = { [bandwidth]: stationData[bandwidth] };
        }
      }
      
      filteredMatrix = bandwidthFiltered;
    }
    
    // Apply correlation threshold filter if specified
    if (threshold) {
      const thresholdValue = parseFloat(threshold);
      if (!isNaN(thresholdValue)) {
        const thresholdFiltered: typeof filteredMatrix = {};
        
        for (const [stationName, stationData] of Object.entries(filteredMatrix)) {
          const filteredStationData: typeof stationData = {};
          
          for (const [bandwidthName, matrixData] of Object.entries(stationData)) {
            // Create a copy of matrix data with filtered correlations
            const filteredIndices: string[] = [];
            const filteredMatrix: number[][] = [];
            const filteredPValues: number[][] = [];
            
            // First pass: identify indices with significant correlations
            const { matrix, indices, p_values } = matrixData;
            const significantIndices = new Set<number>();
            
            for (let i = 0; i < matrix.length; i++) {
              for (let j = i + 1; j < matrix[i].length; j++) {
                if (Math.abs(matrix[i][j]) >= thresholdValue) {
                  significantIndices.add(i);
                  significantIndices.add(j);
                }
              }
            }
            
            // Build filtered arrays
            const significantIndexArray = Array.from(significantIndices).sort((a, b) => a - b);
            
            if (significantIndexArray.length > 0) {
              // Map indices to names
              for (const idx of significantIndexArray) {
                filteredIndices.push(indices[idx]);
              }
              
              // Build filtered matrix
              for (const i of significantIndexArray) {
                const row: number[] = [];
                const pRow: number[] = [];
                
                for (const j of significantIndexArray) {
                  row.push(matrix[i][j]);
                  if (p_values) {
                    pRow.push(p_values[i][j]);
                  }
                }
                
                filteredMatrix.push(row);
                if (p_values) {
                  filteredPValues.push(pRow);
                }
              }
              
              filteredStationData[bandwidthName] = {
                indices: filteredIndices,
                matrix: filteredMatrix,
                ...(p_values && filteredPValues.length > 0 && { p_values: filteredPValues }),
                ...(matrixData.sample_sizes && { sample_sizes: matrixData.sample_sizes }),
              };
            }
          }
          
          if (Object.keys(filteredStationData).length > 0) {
            thresholdFiltered[stationName] = filteredStationData;
          }
        }
        
        filteredMatrix = thresholdFiltered;
      }
    }
    
    const endTime = Date.now();
    
    // Build response - include all fields from original data
    const response: CorrelationData = {
      metadata: {
        ...fullData.metadata,
        processing_time_ms: endTime - startTime,
        filters_applied: {
          station: station || null,
          bandwidth: bandwidth || null,
          threshold: threshold || null,
          include_metadata: includeMetadata,
        },
      },
      // Include the filtered matrix in the expected field name
      ...(fullData.correlation_matrix && { correlation_matrix: filteredMatrix }),
      ...(fullData.matrix_data && { matrix_data: filteredMatrix }),
      
      // Include all other fields from the original data
      ...(fullData.indices && { indices: fullData.indices }),
      ...(fullData.statistics && { statistics: fullData.statistics }),
      ...(fullData.high_correlations && { high_correlations: fullData.high_correlations }),
      ...(fullData.suggested_removals && { suggested_removals: fullData.suggested_removals }),
      ...(includeMetadata && fullData.indices_metadata && { indices_metadata: fullData.indices_metadata }),
    };
    
    const totalStations = Object.keys(filteredMatrix).length;
    console.log(`Correlation matrix API: ${endTime - startTime}ms, ${totalStations} stations`);
    
    return NextResponse.json(response);
    
  } catch (error) {
    console.error('Error in correlation-matrix API:', error);
    
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Internal server error',
        processing_time_ms: Date.now() - startTime,
      },
      { status: 500 }
    );
  }
}