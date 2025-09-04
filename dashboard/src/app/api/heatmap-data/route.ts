import { NextRequest, NextResponse } from 'next/server';

interface HeatmapData {
  metadata?: {
    generated_at: string;
    version: string;
    data_sources: string[];
    total_records: number;
    processing_info?: {
      stations: string[];
      years: number[];
      species: string[];
    };
  };
  data: Array<{
    station: string;
    year: number;
    species: string;
    detections_count?: number;
    date?: string;
    [key: string]: any;
  }>;
}

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

// Cache large file in memory to avoid repeated CDN requests
let heatmapData: HeatmapData | null = null;
let lastLoadTime = 0;
const CACHE_TTL = 60 * 60 * 1000; // 1 hour cache

async function loadHeatmapData(): Promise<HeatmapData> {
  const now = Date.now();
  
  // Return cached data if still valid
  if (heatmapData && (now - lastLoadTime) < CACHE_TTL) {
    return heatmapData;
  }
  
  console.log('Loading heatmap data from CDN...');
  const response = await fetch(`${CDN_BASE_URL}/processed/heatmap.json`);
  
  if (!response.ok) {
    throw new Error(`Failed to load heatmap data: ${response.statusText}`);
  }
  
  heatmapData = await response.json();
  lastLoadTime = now;
  
  console.log(`Heatmap data loaded: ${heatmapData?.data?.length || 0} records`);
  return heatmapData!;
}

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const { searchParams } = new URL(request.url);
    
    // Extract filter parameters
    const station = searchParams.get('station');
    const year = searchParams.get('year');
    const species = searchParams.get('species');
    const limit = searchParams.get('limit');
    const offset = searchParams.get('offset');
    
    // Load full dataset
    const fullData = await loadHeatmapData();
    let filteredData = fullData.data || [];
    
    // Apply filters
    if (station) {
      filteredData = filteredData.filter(item => item.station === station);
    }
    
    if (year) {
      const yearNum = parseInt(year, 10);
      if (!isNaN(yearNum)) {
        filteredData = filteredData.filter(item => item.year === yearNum);
      }
    }
    
    if (species) {
      filteredData = filteredData.filter(item => item.species === species);
    }
    
    // Apply pagination
    const limitNum = limit ? parseInt(limit, 10) : undefined;
    const offsetNum = offset ? parseInt(offset, 10) : 0;
    
    if (limitNum) {
      filteredData = filteredData.slice(offsetNum, offsetNum + limitNum);
    } else if (offsetNum > 0) {
      filteredData = filteredData.slice(offsetNum);
    }
    
    const endTime = Date.now();
    
    // Build response with metadata
    const response = {
      metadata: {
        ...fullData.metadata,
        filtered_records: filteredData.length,
        total_records: fullData.data?.length || 0,
        processing_time_ms: endTime - startTime,
        filters_applied: {
          station: station || null,
          year: year || null,  
          species: species || null,
          limit: limitNum || null,
          offset: offsetNum || 0,
        },
      },
      data: filteredData,
    };
    
    console.log(`Heatmap API: ${endTime - startTime}ms, ${filteredData.length}/${fullData.data?.length} records`);
    
    return NextResponse.json(response);
    
  } catch (error) {
    console.error('Error in heatmap-data API:', error);
    
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Internal server error',
        processing_time_ms: Date.now() - startTime,
      },
      { status: 500 }
    );
  }
}