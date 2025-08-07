/**
 * Timeline data processing utilities for species activity heatmap
 */

import { format, parseISO, startOfMonth, isValid } from 'date-fns';

export interface Detection {
  date: string;
  station: string;
  year: string;
  [speciesCode: string]: any; // Species detection columns
}

export interface TimelineDataPoint {
  month: string; // 'YYYY-MM' format
  station: string;
  species: string;
  detections: number;
  deploymentActive: boolean;
}

export interface HeatmapData {
  x: string[]; // Month labels
  y: string[]; // Species names
  z: number[][]; // Detection counts [species][month]
  stations: string[];
  monthStationMapping: Record<string, string[]>; // Which stations were active each month
}

/**
 * Process raw detection data into timeline format
 */
export function processTimelineData(
  detections: Detection[],
  speciesMapping: Record<string, string>,
  deploymentMetadata: any[] = []
): TimelineDataPoint[] {
  const timelineData: TimelineDataPoint[] = [];
  const speciesColumns = Object.keys(speciesMapping).filter(
    col => !['id', 'file', 'date', 'time', 'year', 'station', 'source_file', 'analyzer'].includes(col)
  );

  // Get deployment periods for context
  const deploymentPeriods = getDeploymentPeriods(deploymentMetadata);

  // Process each detection record
  detections.forEach(detection => {
    // Parse and validate date
    let detectionDate: Date;
    try {
      detectionDate = parseISO(detection.date);
      if (!isValid(detectionDate)) {
        return; // Skip invalid dates
      }
    } catch {
      return; // Skip unparseable dates
    }

    const monthKey = format(startOfMonth(detectionDate), 'yyyy-MM');
    const station = detection.station;

    // Check if station was actively deployed this month
    const deploymentActive = isStationActiveInMonth(station, monthKey, deploymentPeriods);

    // Process each species column
    speciesColumns.forEach(speciesCode => {
      const detectionCount = parseInt(String(detection[speciesCode] || '0'), 10) || 0;
      
      if (detectionCount > 0) {
        timelineData.push({
          month: monthKey,
          station,
          species: speciesMapping[speciesCode] || speciesCode,
          detections: detectionCount,
          deploymentActive
        });
      }
    });
  });

  return timelineData;
}

/**
 * Aggregate timeline data by month/station/species for heatmap display
 */
export function aggregateTimelineData(timelineData: TimelineDataPoint[]): TimelineDataPoint[] {
  const aggregated = new Map<string, TimelineDataPoint>();

  timelineData.forEach(point => {
    const key = `${point.month}-${point.station}-${point.species}`;
    
    if (aggregated.has(key)) {
      const existing = aggregated.get(key)!;
      existing.detections += point.detections;
    } else {
      aggregated.set(key, { ...point });
    }
  });

  return Array.from(aggregated.values());
}

/**
 * Convert timeline data to heatmap format for Plotly
 */
export function prepareHeatmapData(
  timelineData: TimelineDataPoint[],
  topSpeciesCount: number = 12
): HeatmapData {
  // Get top species by total detections
  const speciesCount = new Map<string, number>();
  timelineData.forEach(point => {
    const current = speciesCount.get(point.species) || 0;
    speciesCount.set(point.species, current + point.detections);
  });

  const topSpecies = Array.from(speciesCount.entries())
    .sort(([,a], [,b]) => b - a)
    .slice(0, topSpeciesCount)
    .map(([species]) => species);

  // Get unique months and stations, sorted
  const months = Array.from(new Set(timelineData.map(d => d.month))).sort();
  const stations = Array.from(new Set(timelineData.map(d => d.station))).sort();

  // Create month-station mapping for deployment context
  const monthStationMapping: Record<string, string[]> = {};
  months.forEach(month => {
    monthStationMapping[month] = stations.filter(station => 
      timelineData.some(d => d.month === month && d.station === station && d.deploymentActive)
    );
  });

  // Build data matrix for each station
  const stationHeatmaps: HeatmapData[] = stations.map(station => {
    const z: number[][] = topSpecies.map(species => {
      return months.map(month => {
        const dataPoint = timelineData.find(d => 
          d.month === month && d.station === station && d.species === species
        );
        return dataPoint?.detections || 0;
      });
    });

    return {
      x: months.map(month => formatMonthLabel(month)),
      y: topSpecies,
      z,
      stations: [station],
      monthStationMapping
    };
  });

  // For now, return combined data (we'll enhance this for multi-station display)
  const combinedZ: number[][] = topSpecies.map(species => {
    return months.map(month => {
      // Sum detections across all stations for this month/species
      return stations.reduce((sum, station) => {
        const dataPoint = timelineData.find(d => 
          d.month === month && d.station === station && d.species === species
        );
        return sum + (dataPoint?.detections || 0);
      }, 0);
    });
  });

  return {
    x: months.map(month => formatMonthLabel(month)),
    y: topSpecies,
    z: combinedZ,
    stations,
    monthStationMapping
  };
}

/**
 * Extract deployment periods from metadata
 */
function getDeploymentPeriods(metadata: any[]): Record<string, Array<{start: string, end: string}>> {
  const periods: Record<string, Array<{start: string, end: string}>> = {};
  
  metadata.forEach(deployment => {
    const station = deployment.station;
    if (!periods[station]) {
      periods[station] = [];
    }
    
    if (deployment.start_date && deployment.end_date) {
      periods[station].push({
        start: deployment.start_date,
        end: deployment.end_date
      });
    }
  });
  
  return periods;
}

/**
 * Check if a station was actively deployed in a given month
 */
function isStationActiveInMonth(
  station: string, 
  monthKey: string, 
  deploymentPeriods: Record<string, Array<{start: string, end: string}>>
): boolean {
  const periods = deploymentPeriods[station] || [];
  const monthStart = parseISO(monthKey + '-01');
  
  return periods.some(period => {
    try {
      const deployStart = parseISO(period.start);
      const deployEnd = parseISO(period.end);
      
      // Check if month overlaps with deployment period
      return deployStart <= monthStart && deployEnd >= monthStart;
    } catch {
      return false;
    }
  });
}

/**
 * Format month key for display
 */
function formatMonthLabel(monthKey: string): string {
  try {
    const date = parseISO(monthKey + '-01');
    return format(date, 'MMM yyyy'); // e.g., "Jan 2018"
  } catch {
    return monthKey;
  }
}

/**
 * Get color scale for heatmap based on data range
 */
export function getHeatmapColorScale(maxDetections: number): (string | number)[][] {
  // Ocean-themed color scale matching your dashboard
  const colors = [
    [0, 'rgb(247, 251, 255)'],      // Very light blue (no detections)
    [0.1, 'rgb(222, 235, 247)'],   // Light blue
    [0.3, 'rgb(158, 202, 225)'],   // Medium light blue  
    [0.5, 'rgb(107, 174, 214)'],   // Medium blue
    [0.7, 'rgb(66, 146, 198)'],    // Medium dark blue
    [0.9, 'rgb(33, 113, 181)'],    // Dark blue
    [1.0, 'rgb(8, 69, 148)']       // Very dark blue (high detections)
  ];
  
  return colors;
}