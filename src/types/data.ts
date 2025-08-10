/**
 * Type definitions for MBON Dashboard data structures
 */

// Detection data types
export interface DetectionRecord {
  station: string;
  year: number;
  date: string; // Compatible with Detection interface in timelineProcessing
  date_time?: string; // Optional for backward compatibility
  [speciesCode: string]: string | number | undefined; // Species detection columns are dynamic
}

// Environmental data types
export interface EnvironmentalRecord {
  station: string;
  year: number;
  date_time: string;
  temperature?: number;
  depth?: number;
}

// Acoustic data types
export interface AcousticRecord {
  station: string;
  year: number;
  date_time: string;
  rmsSPL?: number;
  [index: string]: string | number | undefined; // Other acoustic indices
}

// Station information
export interface Station {
  id: string;
  name: string;
  coordinates: [number, number]; // [longitude, latitude]
  depth?: number;
  distance_from_mouth?: number;
  ecosystem_type?: string;
}

// Species information
export interface Species {
  code: string;
  name: string;
  scientific_name?: string;
  category?: 'fish' | 'marine_mammal' | 'invertebrate' | 'other';
}

// Deployment metadata
export interface DeploymentMetadata {
  object_id?: number;
  station: string;
  year: number;
  deployment_start?: string;  // Optional for compatibility
  deployment_end?: string;    // Optional for compatibility
  start_date?: string;         // Alternative naming
  end_date?: string;           // Alternative naming
  gps_lat: number;
  gps_long: number;
  depth_m?: number;
  water_depth_m?: number;
  distance_to_station_m?: number;
  deployment_id?: string;
  platform_type?: string;
  hydrophone_model?: string;
  sampling_rate_hz?: number;
  notes?: string;
}

// Metadata summary
export interface DataMetadata {
  lastUpdated: string;
  dataStats: {
    totalRecords: number;
    stationCount: number;
    speciesCount: number;
    dateRange: {
      start: string;
      end: string;
    };
    recordsByStation: Record<string, number>;
    recordsByYear: Record<number, number>;
  };
}

// Navigation types
export interface NavItem {
  name: string;
  href?: string;
  icon?: React.ComponentType<{ className?: string }>;
  children?: NavChild[];
}

export interface NavChild {
  name: string;
  href: string;
  description?: string;
}