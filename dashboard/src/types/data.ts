/**
 * Data type definitions for MBON Dashboard
 */

export interface Station {
  id: string;
  name: string;
  coordinates: {
    latitude: number | null;
    longitude: number | null;
  };
  depth_m: number | null;
  platform: string;
  deployment_periods: Array<{
    deploy_date: string;
    recover_date: string;
    duration_days: number | null;
  }>;
  data_availability: {
    years: number[];
    detection_data: boolean;
    environmental_data: boolean;
    acoustic_indices: boolean;
  };
}

export interface StationsData {
  metadata: {
    generated_at: string;
    version: string;
    description: string;
  };
  summary: {
    total_stations: number;
    years_covered: number[];
    stations_with_indices: number;
    coordinate_bounds: {
      north: number | null;
      south: number | null;
      east: number | null;
      west: number | null;
    };
  };
  stations: Station[];
}

export interface Dataset {
  id: string;
  name: string;
  description: string;
  record_count: number;
  stations: string[];
  years: number[];
  temporal_resolution: string;
  data_type: string;
  [key: string]: any; // Allow additional properties
}

export interface DatasetsData {
  metadata: {
    generated_at: string;
    version: string;
    description: string;
  };
  summary: {
    total_records: number;
    total_datasets: number;
    stations: {
      count: number;
      list: string[];
    };
    temporal_coverage: {
      years: number[];
      deployment_years: number[];
      earliest: number | null;
      latest: number | null;
    };
    data_types: {
      biological: string[];
      environmental: string[];
      acoustic: string[];
    };
  };
  datasets: Dataset[];
}

export interface ProjectMetadata {
  metadata: {
    generated_at: string;
    version: string;
    description: string;
  };
  project: {
    title: string;
    subtitle: string;
    organization: string;
    principal_investigators: string[];
    funding_sources: string[];
    project_period: {
      start: string;
      end: string;
      data_years: number[];
    };
  };
  research_context: {
    primary_question: string;
    objectives: Array<{
      id: string;
      title: string;
      description: string;
      status: string;
    }>;
    significance: string;
  };
  methodology: any; // Complex nested structure
  study_area: {
    location: string;
    ecosystem: string;
    coordinates: {
      center: {
        latitude: number;
        longitude: number;
      };
      bounding_box: {
        north: number;
        south: number;
        east: number;
        west: number;
      };
    };
    stations: {
      count: number;
      names: string[];
      habitat_types: string[];
    };
  };
  data_availability: any;
  citations: any;
}