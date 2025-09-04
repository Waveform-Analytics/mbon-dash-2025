import { NextRequest, NextResponse } from 'next/server';

interface AcousticDistributionsData {
  metadata?: {
    generated_at: string;
    version: string;
    data_sources: string[];
    total_indices: number;
    processing_time_ms?: number;
    filters_applied?: any;
    processing_info?: {
      stations: string[];
      bandwidths: string[];
      years: number[];
    };
  };
  distributions: Record<string, {
    [station: string]: {
      [bandwidth: string]: {
        mean?: number;
        std?: number;
        min?: number;
        max?: number;
        q25?: number;
        q50?: number;
        q75?: number;
        count?: number;
        [key: string]: any;
      };
    };
  }>;
  indices_metadata?: Record<string, {
    name: string;
    category: string;
    description?: string;
    unit?: string;
  }>;
  filters?: {
    stations: string[];
    bandwidths: string[];
    years: number[];
    available_combinations: Array<{
      station: string;
      bandwidth: string;
      year: number;
    }>;
  };
}

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

// Cache large file in memory
let distributionsData: AcousticDistributionsData | null = null;
let lastLoadTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minute cache for development

async function loadDistributionsData(): Promise<AcousticDistributionsData> {
  const now = Date.now();
  
  // Return cached data if still valid
  if (distributionsData && (now - lastLoadTime) < CACHE_TTL) {
    return distributionsData;
  }
  
  console.log('Loading acoustic distributions data from CDN...');
  const response = await fetch(`${CDN_BASE_URL}/processed/acoustic_indices_distributions.json`);
  
  if (!response.ok) {
    throw new Error(`Failed to load acoustic distributions: ${response.statusText}`);
  }
  
  distributionsData = await response.json();
  lastLoadTime = now;
  
  console.log(`Acoustic distributions loaded: ${Object.keys(distributionsData?.distributions || {}).length} indices`);
  return distributionsData!;
}

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const { searchParams } = new URL(request.url);
    
    // Extract filter parameters
    const index = searchParams.get('index');
    const station = searchParams.get('station');
    const bandwidth = searchParams.get('bandwidth');
    const category = searchParams.get('category');
    
    // Load full dataset
    const fullData = await loadDistributionsData();
    let filteredDistributions = { ...fullData.distributions };
    
    // Filter by specific index
    if (index && filteredDistributions[index]) {
      filteredDistributions = { [index]: filteredDistributions[index] };
    } else if (index) {
      // Index not found
      filteredDistributions = {};
    }
    
    // Filter by category if specified
    if (category && fullData.indices_metadata) {
      const indicesInCategory = Object.keys(fullData.indices_metadata).filter(
        idx => fullData.indices_metadata![idx].category === category
      );
      
      const categoryFiltered: typeof filteredDistributions = {};
      for (const idx of indicesInCategory) {
        if (filteredDistributions[idx]) {
          categoryFiltered[idx] = filteredDistributions[idx];
        }
      }
      filteredDistributions = categoryFiltered;
    }
    
    // Filter by station and/or bandwidth within each index
    if (station || bandwidth) {
      const stationBandwidthFiltered: typeof filteredDistributions = {};
      
      for (const [indexName, indexData] of Object.entries(filteredDistributions)) {
        const filteredIndexData: typeof indexData = {};
        
        for (const [compoundKey, stats] of Object.entries(indexData)) {
          // Parse compound key like "9M_8kHz" or "14M_FullBW"
          const parts = compoundKey.split('_');
          const keyStation = parts[0]; // e.g., "9M"
          const keyBandwidth = parts[1]; // e.g., "8kHz" or "FullBW"
          
          // Skip if station filter specified and doesn't match
          if (station && keyStation !== station) continue;
          
          // Skip if bandwidth filter specified and doesn't match
          if (bandwidth && keyBandwidth !== bandwidth) continue;
          
          filteredIndexData[compoundKey] = stats;
        }
        
        if (Object.keys(filteredIndexData).length > 0) {
          stationBandwidthFiltered[indexName] = filteredIndexData;
        }
      }
      
      filteredDistributions = stationBandwidthFiltered;
    }
    
    const endTime = Date.now();
    
    // Extract unique categories from indices metadata
    const categories = fullData.indices_metadata ? 
      [...new Set(Object.values(fullData.indices_metadata).map(meta => meta.category))].sort() : [];

    // Build response
    const response: AcousticDistributionsData = {
      metadata: {
        ...fullData.metadata,
        total_indices: Object.keys(filteredDistributions).length,
        processing_time_ms: endTime - startTime,
        filters_applied: {
          index: index || null,
          station: station || null,
          bandwidth: bandwidth || null,
          category: category || null,
        },
      },
      summary: {
        indices_count: Object.keys(filteredDistributions).length,
        stations: fullData.filters?.stations || [],
        bandwidths: fullData.filters?.bandwidths || [],
        year: fullData.filters?.years?.[0] || 2021,
        categories: categories,
      },
      distributions: filteredDistributions,
      indices_metadata: fullData.indices_metadata,
      filters: fullData.filters,
    };
    
    console.log(`Acoustic distributions API: ${endTime - startTime}ms, ${Object.keys(filteredDistributions).length} indices`);
    
    return NextResponse.json(response);
    
  } catch (error) {
    console.error('Error in acoustic-distributions API:', error);
    
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Internal server error',
        processing_time_ms: Date.now() - startTime,
      },
      { status: 500 }
    );
  }
}