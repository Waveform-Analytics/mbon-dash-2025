import { NextRequest, NextResponse } from 'next/server';

interface RawDataPoint {
  Date: string;
  Filename: string;
  [key: string]: string | number; // For all the acoustic indices
}

interface FilteredDataPoint {
  date: string;
  hour: number;
  value: number;
  index_name: string;
  station: string;
  year: number;
  bandwidth: string;
}

interface HeatmapMetadata {
  available_indices: string[];
  stations: string[];
  years: number[];
  bandwidths: string[];
  value_ranges: Record<string, [number, number]>;
  filtered_records: number;
  processing_time_ms: number;
  memory_used_bytes: number;
}

interface HeatmapData {
  metadata: HeatmapMetadata;
  data: FilteredDataPoint[];
}

// Cache for optimized data files fetched from CDN
interface OptimizedData {
  metadata: {
    station: string;
    year: number;
    bandwidth: string;
    generated_at?: string;
    total_records: number;
    optimization_version: string;
    description: string;
  };
  data: RawDataPoint[];
}

// CDN configuration
const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

// In-memory cache for optimized files
const optimizedDataCache = new Map<string, { data: OptimizedData; timestamp: number }>();
const CACHE_TTL = 60 * 60 * 1000; // 1 hour

// In-memory cache for filtered results
const resultCache = new Map<string, { data: HeatmapData; timestamp: number }>();
const RESULT_CACHE_TTL = 60 * 60 * 1000; // 1 hour

async function loadOptimizedData(station: string, year: number, bandwidth: string): Promise<OptimizedData> {
  const cacheKey = `${station}_${year}_${bandwidth}`;
  const now = Date.now();
  
  // Return cached data if still valid
  const cached = optimizedDataCache.get(cacheKey);
  if (cached && (now - cached.timestamp) < CACHE_TTL) {
    return cached.data;
  }
  
  try {
    const filename = `indices_${station}_${year}_${bandwidth}.json`;
    const dataUrl = `${CDN_BASE_URL}/processed/optimized/${filename}`;
    console.log(`Fetching optimized indices from CDN: ${dataUrl}`);
    
    const response = await fetch(dataUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const optimizedData: OptimizedData = await response.json();
    
    // Cache the data
    optimizedDataCache.set(cacheKey, { data: optimizedData, timestamp: now });
    
    console.log(`Successfully loaded optimized indices: ${optimizedData.metadata.total_records} records for ${cacheKey}`);
    
    return optimizedData;
  } catch (error) {
    console.error(`Error loading optimized indices from CDN for ${cacheKey}:`, error);
    throw new Error(`Failed to load optimized indices data for ${station}/${year}/${bandwidth}`);
  }
}

function parseDate(dateString: string): { date: string; hour: number } {
  try {
    // Handle format like "12/31/2021 23:00"
    const [datePart, timePart] = dateString.split(' ');
    const [month, day, year] = datePart.split('/');
    const [hourStr] = timePart.split(':');
    
    // Format as YYYY-MM-DD for consistency
    const formattedDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    const hour = parseInt(hourStr, 10);
    
    return { date: formattedDate, hour };
  } catch (error) {
    console.error('Error parsing date:', dateString, error);
    throw new Error(`Invalid date format: ${dateString}`);
  }
}

function getValueRanges(data: FilteredDataPoint[]): Record<string, [number, number]> {
  const ranges: Record<string, [number, number]> = {};
  
  for (const point of data) {
    if (!ranges[point.index_name]) {
      ranges[point.index_name] = [point.value, point.value];
    } else {
      ranges[point.index_name][0] = Math.min(ranges[point.index_name][0], point.value);
      ranges[point.index_name][1] = Math.max(ranges[point.index_name][1], point.value);
    }
  }
  
  return ranges;
}

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  const startMemory = process.memoryUsage();
  
  try {
    const { searchParams } = new URL(request.url);
    
    // Extract and validate parameters
    const index = searchParams.get('index');
    const station = searchParams.get('station');
    const yearParam = searchParams.get('year');
    const bandwidth = searchParams.get('bandwidth');
    
    if (!index || !station || !yearParam || !bandwidth) {
      return NextResponse.json(
        { error: 'Missing required parameters: index, station, year, bandwidth' },
        { status: 400 }
      );
    }
    
    const year = parseInt(yearParam, 10);
    if (isNaN(year)) {
      return NextResponse.json(
        { error: 'Invalid year parameter' },
        { status: 400 }
      );
    }
    
    // Create cache key
    const cacheKey = `${index}-${station}-${year}-${bandwidth}`;
    
    // Check result cache first
    const cached = resultCache.get(cacheKey);
    if (cached && (Date.now() - cached.timestamp) < RESULT_CACHE_TTL) {
      console.log(`Cache hit for ${cacheKey}`);
      return NextResponse.json(cached.data);
    }
    
    // Load optimized data directly from CDN
    const optimizedData = await loadOptimizedData(station, year, bandwidth);
    const rawData = optimizedData.data;
    
    if (!rawData || !Array.isArray(rawData)) {
      return NextResponse.json(
        { error: 'No data found for the specified parameters' },
        { status: 404 }
      );
    }
    
    // Check if the requested index exists in the data
    const sampleRecord = rawData[0];
    if (!sampleRecord || !(index in sampleRecord)) {
      return NextResponse.json(
        { error: `Index '${index}' not found in data` },
        { status: 404 }
      );
    }
    
    // Filter and transform data
    const filteredData: FilteredDataPoint[] = [];
    
    for (const record of rawData) {
      const indexValue = record[index];
      
      // Skip records with null, undefined, or non-numeric values
      if (indexValue === null || indexValue === undefined || typeof indexValue !== 'number' || isNaN(indexValue)) {
        continue;
      }
      
      try {
        const { date, hour } = parseDate(record.Date);
        
        filteredData.push({
          date,
          hour,
          value: indexValue,
          index_name: index,
          station,
          year,
          bandwidth,
        });
      } catch {
        console.warn('Skipping record with invalid date:', record.Date);
        continue;
      }
    }
    
    // Generate metadata
    const availableIndices = Object.keys(sampleRecord).filter(
      key => key !== 'Date' && key !== 'Filename' && typeof sampleRecord[key] === 'number'
    );
    
    // Since we're loading individual files, provide known metadata
    // You can expand this based on your actual data combinations
    const stations = ['9M', '14M', '37M']; // Known stations
    const years = [2021]; // Known years
    const bandwidths = ['FullBW', '8kHz']; // Known bandwidths
    
    const valueRanges = getValueRanges(filteredData);
    
    const endTime = Date.now();
    const endMemory = process.memoryUsage();
    
    const metadata: HeatmapMetadata = {
      available_indices: availableIndices.sort(),
      stations: stations.sort(),
      years: years.sort(),
      bandwidths: bandwidths.sort(),
      value_ranges: valueRanges,
      filtered_records: filteredData.length,
      processing_time_ms: endTime - startTime,
      memory_used_bytes: endMemory.heapUsed - startMemory.heapUsed,
    };
    
    const result: HeatmapData = {
      metadata,
      data: filteredData,
    };
    
    // Cache the result
    resultCache.set(cacheKey, { data: result, timestamp: Date.now() });
    
    console.log(
      `Indices heatmap: ${endTime - startTime}ms, ${endMemory.heapUsed - startMemory.heapUsed} bytes, ${filteredData.length} records for ${cacheKey}`
    );
    
    return NextResponse.json(result);
    
  } catch (error) {
    console.error('Error in indices-heatmap API:', error);
    
    const endTime = Date.now();
    console.log(`Error after ${endTime - startTime}ms`);
    
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Internal server error',
        processing_time_ms: endTime - startTime,
      },
      { status: 500 }
    );
  }
}