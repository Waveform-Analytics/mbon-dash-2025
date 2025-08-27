/**
 * Test-Driven Development tests for view data hooks.
 * 
 * Tests the useViewData hook that loads optimized view files from CDN.
 * These tests define the expected behavior before implementation.
 */

import { renderHook, waitFor } from '@testing-library/react'
import { act } from 'react'

// Mock fetch globally
global.fetch = jest.fn()

// Import the hook we're testing (will fail initially - that's expected in TDD)
import { useViewData } from '@/lib/hooks/useViewData'

describe('useViewData Hook', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    (fetch as jest.Mock).mockReset()
  })

  describe('Station Overview Loading', () => {
    it('should load station overview data successfully', async () => {
      const mockStationData = {
        stations: [
          {
            id: '9M',
            name: 'Station 9M',
            coordinates: { lat: 32.2833, lon: -80.8833 },
            deployments: [
              {
                start: '2021-01-25',
                end: '2021-04-26',
                deployment_id: '9M_1081_042621'
              }
            ],
            summary_stats: {
              total_detections: 1500,
              species_count: 12,
              recording_hours: 2190,
              years_active: [2021]
            }
          }
        ],
        metadata: {
          generated_at: '2025-08-26T16:02:28.477276Z',
          data_sources: ['stations.json', 'detections.json'],
          total_stations: 1
        }
      }

      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStationData
      })

      const { result } = renderHook(() => useViewData('station-overview'))

      // Initially should be loading
      expect(result.current.loading).toBe(true)
      expect(result.current.data).toBeNull()
      expect(result.current.error).toBeNull()

      // Wait for data to load
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Should have loaded data successfully
      expect(result.current.data).toEqual(mockStationData)
      expect(result.current.error).toBeNull()
      expect(fetch).toHaveBeenCalledWith(
        `${process.env.NEXT_PUBLIC_DATA_URL}/views/station_overview.json`
      )
    })

    it('should handle fetch errors gracefully', async () => {
      ;(fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useViewData('station-overview'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.data).toBeNull()
      expect(result.current.error).toBe('Failed to load station-overview data: Network error')
    })

    it('should handle HTTP error responses', async () => {
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      const { result } = renderHook(() => useViewData('station-overview'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.data).toBeNull()
      expect(result.current.error).toBe('Failed to load station-overview data: 404 Not Found')
    })
  })

  describe('Hook State Management', () => {
    it('should maintain loading state correctly', async () => {
      const mockData = { test: 'data' }
      ;(fetch as jest.Mock).mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => mockData
        }), 100))
      )

      const { result } = renderHook(() => useViewData('station-overview'))

      // Should start loading
      expect(result.current.loading).toBe(true)
      expect(result.current.data).toBeNull()

      // Should finish loading
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.data).toEqual(mockData)
    })

    it('should not refetch on re-render with same view', async () => {
      const mockData = { test: 'data' }
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const { result, rerender } = renderHook(() => useViewData('station-overview'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Re-render with same view
      rerender()

      // Should not fetch again
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(result.current.data).toEqual(mockData)
    })

    it('should refetch when view changes', async () => {
      const stationData = { stations: [] }
      const speciesData = { species: [] }

      ;(fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => stationData
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => speciesData
        })

      const { result, rerender } = renderHook(
        ({ view }) => useViewData(view),
        { initialProps: { view: 'station-overview' } }
      )

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(result.current.data).toEqual(stationData)

      // Change view
      rerender({ view: 'species-overview' })

      // Should fetch new data
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      expect(fetch).toHaveBeenCalledTimes(2)
      expect(result.current.data).toEqual(speciesData)
    })
  })

  describe('View Type Support', () => {
    it('should support different view types', async () => {
      const mockData = { data: 'test' }
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const { result: stationResult } = renderHook(() => useViewData('station-overview'))
      await waitFor(() => expect(stationResult.current.loading).toBe(false))

      // Reset mock for next test
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const { result: speciesResult } = renderHook(() => useViewData('species-overview'))
      await waitFor(() => expect(speciesResult.current.loading).toBe(false))

      // Should have called different URLs
      expect(fetch).toHaveBeenCalledWith(
        `${process.env.NEXT_PUBLIC_DATA_URL}/views/station_overview.json`
      )
      expect(fetch).toHaveBeenCalledWith(
        `${process.env.NEXT_PUBLIC_DATA_URL}/views/species_overview.json`
      )
    })

    it('should handle invalid view types', () => {
      const { result } = renderHook(() => useViewData('invalid-view' as any))

      expect(result.current.loading).toBe(false)
      expect(result.current.data).toBeNull()
      expect(result.current.error).toBe('Invalid view type: invalid-view')
    })
  })

  describe('TypeScript Type Safety', () => {
    it('should infer correct return types for station-overview', async () => {
      const mockData = {
        stations: [],
        metadata: { total_stations: 0, generated_at: '', data_sources: [] }
      }
      
      ;(fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      })

      const { result } = renderHook(() => useViewData('station-overview'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })

      // Type should be inferred as StationOverviewData
      if (result.current.data) {
        expect(result.current.data).toHaveProperty('stations')
        expect(result.current.data).toHaveProperty('metadata')
        expect(Array.isArray(result.current.data.stations)).toBe(true)
      }
    })
  })
})