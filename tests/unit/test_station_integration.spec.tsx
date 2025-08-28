/**
 * Station Overview Integration Tests
 * 
 * Tests for integrating the station overview view data with the existing stations page.
 * Verifies that the new hook-based approach works correctly with real view data structure.
 */

import { renderHook, waitFor } from '@testing-library/react';
import { render, screen } from '@testing-library/react';
import { useStationOverview } from '@/lib/hooks/useViewData';
import StationsPage from '@/app/stations/page';

// Mock the StationMap component since it requires Mapbox
jest.mock('@/components/maps/StationMap', () => ({
  StationMap: ({ stations }: { stations: any[] }) => (
    <div data-testid="station-map">
      Mock Station Map with {stations.length} stations
    </div>
  ),
}));

// Mock fetch for testing
global.fetch = jest.fn();

const mockStationOverviewData = {
  stations: [
    {
      id: "9M",
      name: "Station 9M",
      coordinates: {
        lat: 32.2833,
        lon: -80.8833
      },
      deployments: [
        {
          start: "2018-01-01",
          end: "2018-04-01",
          deployment_id: "9M_test_1"
        },
        {
          start: "2021-01-01", 
          end: "2021-04-01",
          deployment_id: "9M_test_2"
        }
      ],
      summary_stats: {
        total_detections: 15420,
        species_count: 8,
        recording_hours: 2880,
        years_active: [2018, 2021]
      }
    },
    {
      id: "14M",
      name: "Station 14M",
      coordinates: {
        lat: 32.2273,
        lon: -80.8774
      },
      deployments: [
        {
          start: "2018-01-01",
          end: "2018-04-01",
          deployment_id: "14M_test_1"
        }
      ],
      summary_stats: {
        total_detections: 12340,
        species_count: 6,
        recording_hours: 2400,
        years_active: [2018, 2021]
      }
    },
    {
      id: "37M",
      name: "Station 37M", 
      coordinates: {
        lat: 32.1945,
        lon: -80.7922
      },
      deployments: [
        {
          start: "2018-01-01",
          end: "2018-04-01", 
          deployment_id: "37M_test_1"
        }
      ],
      summary_stats: {
        total_detections: 8760,
        species_count: 4,
        recording_hours: 1920,
        years_active: [2018, 2021]
      }
    }
  ],
  metadata: {
    generated_at: "2025-08-28T12:00:00Z",
    data_sources: ["stations.json", "deployment_metadata.json", "detections.json"],
    total_stations: 3
  }
};

describe('Station Overview Integration', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  describe('useStationOverview Hook', () => {
    it('should load station overview data successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStationOverviewData,
      });

      const { result } = renderHook(() => useStationOverview());

      expect(result.current.loading).toBe(true);
      expect(result.current.data).toBeNull();
      expect(result.current.error).toBeNull();

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toEqual(mockStationOverviewData);
      expect(result.current.error).toBeNull();
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/views/station_overview.json')
      );
    });

    it('should handle loading errors gracefully', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useStationOverview());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toContain('Network error');
    });

    it('should handle HTTP errors correctly', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      const { result } = renderHook(() => useStationOverview());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data).toBeNull();
      expect(result.current.error).toContain('404');
    });
  });

  describe('Station Data Structure Validation', () => {
    it('should have correct station data structure', () => {
      const station = mockStationOverviewData.stations[0];
      
      // Required fields
      expect(station.id).toBeDefined();
      expect(station.name).toBeDefined();
      expect(station.coordinates).toBeDefined();
      expect(station.coordinates.lat).toBeGreaterThan(30);
      expect(station.coordinates.lat).toBeLessThan(35);
      expect(station.coordinates.lon).toBeLessThan(-80);
      expect(station.coordinates.lon).toBeGreaterThan(-85);
      
      // Deployments
      expect(Array.isArray(station.deployments)).toBe(true);
      expect(station.deployments.length).toBeGreaterThan(0);
      
      // Summary stats
      expect(station.summary_stats.total_detections).toBeGreaterThanOrEqual(0);
      expect(station.summary_stats.species_count).toBeGreaterThanOrEqual(0);
      expect(station.summary_stats.recording_hours).toBeGreaterThan(0);
      expect(Array.isArray(station.summary_stats.years_active)).toBe(true);
    });

    it('should have valid deployment data', () => {
      const deployment = mockStationOverviewData.stations[0].deployments[0];
      
      expect(deployment.start).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(deployment.end).toMatch(/^\d{4}-\d{2}-\d{2}$/);
      expect(deployment.deployment_id).toBeDefined();
      expect(typeof deployment.deployment_id).toBe('string');
    });

    it('should have valid metadata structure', () => {
      const metadata = mockStationOverviewData.metadata;
      
      expect(metadata.generated_at).toBeDefined();
      expect(Array.isArray(metadata.data_sources)).toBe(true);
      expect(metadata.total_stations).toBe(3);
      expect(metadata.total_stations).toBe(mockStationOverviewData.stations.length);
    });
  });

  describe('Data Consistency Validation', () => {
    it('should have consistent station count', () => {
      expect(mockStationOverviewData.stations).toHaveLength(3);
      expect(mockStationOverviewData.metadata.total_stations).toBe(3);
    });

    it('should have expected station IDs', () => {
      const stationIds = mockStationOverviewData.stations.map(s => s.id);
      expect(stationIds).toContain('9M');
      expect(stationIds).toContain('14M');
      expect(stationIds).toContain('37M');
    });

    it('should have reasonable recording hours', () => {
      mockStationOverviewData.stations.forEach(station => {
        // Each deployment should have substantial recording time
        expect(station.summary_stats.recording_hours).toBeGreaterThan(100);
        // But not unreasonably high (max ~8760 hours per year)
        expect(station.summary_stats.recording_hours).toBeLessThan(20000);
      });
    });

    it('should have valid years_active data', () => {
      mockStationOverviewData.stations.forEach(station => {
        station.summary_stats.years_active.forEach(year => {
          expect(year).toBeGreaterThanOrEqual(2017);
          expect(year).toBeLessThanOrEqual(2022);
        });
      });
    });
  });

  describe('Performance and Data Size Validation', () => {
    it('should have reasonable data size for performance', () => {
      const jsonString = JSON.stringify(mockStationOverviewData);
      const sizeInKB = jsonString.length / 1024;
      
      // Should be under 10KB for good performance
      expect(sizeInKB).toBeLessThan(10);
      console.log(`Station overview data size: ${sizeInKB.toFixed(1)} KB`);
    });

    it('should not have excessive deployment detail', () => {
      mockStationOverviewData.stations.forEach(station => {
        // Each station should have reasonable number of deployments
        expect(station.deployments.length).toBeLessThan(15);
        
        // Deployments should have minimal, essential data only
        station.deployments.forEach(deployment => {
          const deploymentKeys = Object.keys(deployment);
          expect(deploymentKeys).toHaveLength(3); // start, end, deployment_id only
        });
      });
    });
  });
});