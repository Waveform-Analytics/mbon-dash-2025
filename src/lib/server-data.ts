/**
 * Server-side data fetching functions
 * These run at build time or on the server, not in the browser
 */

const CDN_URL = process.env.NEXT_PUBLIC_DATA_URL || 'https://waveformdata.work';

export async function fetchServerData<T>(endpoint: string): Promise<T | null> {
  try {
    const response = await fetch(`${CDN_URL}/processed/${endpoint}`, {
      // Cache for 5 minutes in production, no cache in development
      next: { revalidate: process.env.NODE_ENV === 'development' ? 0 : 300 }
    });
    
    if (!response.ok) {
      console.error(`Failed to fetch ${endpoint}: ${response.statusText}`);
      return null;
    }
    
    return response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    return null;
  }
}

// Server-side data fetching functions
export async function getServerMetadata() {
  return fetchServerData<{
    data_summary: {
      total_detections: number;
      species_count: number;
      stations_count: number;
    };
    generated_at: string;
  }>('metadata.json');
}

export async function getServerSpecies() {
  return fetchServerData<Array<{
    short_name: string;
    long_name: string;
    total_detections: number;
    category: string;
  }>>('species.json');
}

export async function getServerStations() {
  return fetchServerData<Array<{
    id: string;
    name: string;
    years: number[];
  }>>('stations.json');
}

export async function getServerDeployments() {
  return fetchServerData<DeploymentMetadata[]>('deployment_metadata.json');
}

// Type definition for deployment metadata
export interface DeploymentMetadata {
  station: string;
  year: number;
  gps_lat: number;
  gps_long: number;
  start_date: string;
  end_date: string;
  deployment_id: string;
}