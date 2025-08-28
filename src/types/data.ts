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

// View data types for optimized dashboard views
export interface StationOverviewData {
  stations: Array<{
    id: string;
    name: string;
    coordinates: {
      lat: number;
      lon: number;
    };
    deployments: Array<{
      start?: string;
      end?: string;
      deployment_id?: string;
    }>;
    summary_stats: {
      total_detections: number;
      species_count: number;
      recording_hours: number;
      years_active: number[];
    };
  }>;
  metadata: {
    generated_at: string;
    data_sources: string[];
    total_stations: number;
  };
}

export interface SpeciesTimelineData {
  species_timeline: Array<{
    species_code: string;
    species_name: string;
    category: 'biological';
    monthly_detections: Array<{
      year_month: string; // "2018-01" format
      detection_count: number;
      stations: string[]; // Stations that had detections
    }>;
    detection_frequency: number; // 0-1 ratio
    total_detections: number;
  }>;
  metadata: {
    generated_at: string;
    data_sources: string[];
    total_species: number;
    aggregation_level: 'monthly';
    description: string;
  };
  temporal_aggregation: 'monthly';
}

// Acoustic Summary Data (optimized from 166MB → 19.6KB)
export interface AcousticSummaryData {
  acoustic_summary: Array<{
    station: string;
    temporal_stats: {
      total_records: number;
      date_range: {
        start: string | null;
        end: string | null;
      };
    };
    acoustic_metrics: Record<string, {
      mean: number | null;
      std: number | null;
    }>;
  }>;
  pca_analysis: {
    components: string[]; // e.g., ['PC1', 'PC2', 'PC3', 'PC4', 'PC5']
    explained_variance: number[];
    feature_loadings: Record<string, Record<string, number>>;
  };
  index_categories: Record<string, {
    description: string;
    indices: string[];
    summary_stats?: {
      index_count: number;
      avg_correlation: number | null;
      data_availability: number;
    };
  }>;
  metadata: {
    generated_at: string;
    data_sources: string[];
    total_indices: number;
    stations_included: string[];
    total_records_processed: number;
    date_range: {
      start: string | null;
      end: string | null;
    };
    generator: string;
    version: string;
  };
}

// Union type for all view data types
export type ViewData = StationOverviewData | SpeciesTimelineData | AcousticSummaryData;

// View type identifiers
export type ViewType = 'station-overview' | 'species-timeline' | 'acoustic-summary';