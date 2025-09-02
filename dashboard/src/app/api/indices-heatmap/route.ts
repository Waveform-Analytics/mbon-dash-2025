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

// Cache for the compiled data file fetched from CDN
interface CompiledData {
  metadata?: {
    total_records?: number;
    [key: string]: unknown;
  };
  stations?: {
    [station: string]: {
      [year: string]: {
        [bandwidth: string]: RawDataPoint[];
      };
    };
  };
  data?: RawDataPoint[];
}
let compiledData: CompiledData | null = null;
let compiledDataTimestamp = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// CDN configuration
const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_BASE_URL || 'https://waveformdata.work';

// In-memory cache for filtered results
const resultCache = new Map<string, { data: HeatmapData; timestamp: number }>();
const RESULT_CACHE_TTL = 60 * 60 * 1000; // 1 hour

async function loadCompiledData() {
  const now = Date.now();
  
  // Return cached data if still valid
  if (compiledData && (now - compiledDataTimestamp) < CACHE_TTL) {
    return compiledData;
  }
  
  try {
    const dataUrl = `${CDN_BASE_URL}/processed/compiled_indices.json`;
    console.log(`Fetching compiled indices from CDN: ${dataUrl}`);
    
    const response = await fetch(dataUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const fileContent = await response.text();
    compiledData = JSON.parse(fileContent);
    compiledDataTimestamp = now;
    
    console.log(`Successfully loaded compiled indices: ${(compiledData as CompiledData)?.metadata?.total_records || 'unknown'} total records`);
    
    return compiledData;
  } catch (error) {
    console.error('Error loading compiled indices from CDN:', error);
    throw new Error('Failed to load compiled indices data from CDN');
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
    
    // Load compiled data from CDN
    const compiledIndices = await loadCompiledData();
    
    // Navigate to the specific dataset
    const stationData = compiledIndices?.stations?.[station];
    if (!stationData) {
      return NextResponse.json(
        { error: `Station '${station}' not found` },
        { status: 404 }
      );
    }
    
    const yearData = stationData[year.toString()];
    if (!yearData) {
      return NextResponse.json(
        { error: `Year '${year}' not found for station '${station}'` },
        { status: 404 }
      );
    }
    
    const bandwidthData = yearData[bandwidth];
    if (!bandwidthData) {
      return NextResponse.json(
        { error: `Bandwidth '${bandwidth}' not found for station '${station}' year '${year}'` },
        { status: 404 }
      );
    }
    
    const rawData: RawDataPoint[] = bandwidthData;
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
    
    const stations = Object.keys(compiledIndices.stations || {});
    const years = [...new Set(
      stations.flatMap(s => 
        Object.keys(compiledIndices.stations?.[s] || {}).map(y => parseInt(y, 10))
      )
    )].filter(y => !isNaN(y));
    
    const bandwidths = [...new Set(
      stations.flatMap(s => 
        Object.keys(compiledIndices.stations?.[s] || {}).flatMap(y =>
          Object.keys(compiledIndices.stations?.[s]?.[y] || {})
        )
      )
    )];
    
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