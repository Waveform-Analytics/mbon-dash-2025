/**
 * Test-Driven Development tests for stations-v2 page.
 * 
 * Tests the new optimized stations page that uses view data instead of raw data.
 * These tests define the expected behavior before implementation.
 */

import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'

// Mock the entire hook module
jest.mock('../../src/lib/hooks/useViewData')

// Import the mocked module
import { useStationOverview } from '../../src/lib/hooks/useViewData'
// Import the page component we're testing
import StationsV2Page from '../../src/app/stations-v2/page'

// Get the mocked function
const mockUseStationOverview = useStationOverview as jest.MockedFunction<typeof useStationOverview>

describe('Stations V2 Page', () => {
  beforeEach(() => {
    mockUseStationOverview.mockReset()
  })

  describe('Page Rendering', () => {
    it('should render without crashing', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      expect(screen.getByRole('main')).toBeInTheDocument()
    })

    it('should have correct page title and structure', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/station.*overview/i)
    })
  })

  describe('Loading State', () => {
    it('should display loading state initially', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      expect(screen.getByText(/loading/i)).toBeInTheDocument()
    })

    it('should not show station data while loading', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      expect(screen.queryByText('Station 9M')).not.toBeInTheDocument()
      expect(screen.queryByText('Station 14M')).not.toBeInTheDocument()
      expect(screen.queryByText('Station 37M')).not.toBeInTheDocument()
    })
  })

  describe('Error State', () => {
    it('should display error message when data fails to load', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: false,
        error: 'Failed to load station data: Network error',
      })

      render(<StationsV2Page />)
      expect(screen.getByText(/error.*loading.*data/i)).toBeInTheDocument()
      expect(screen.getByText(/unable.*to.*load/i)).toBeInTheDocument()
    })

    it('should not show loading or station data when error occurs', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: false,
        error: 'Network error',
      })

      render(<StationsV2Page />)
      expect(screen.queryByText(/loading.*station/i)).not.toBeInTheDocument()
      expect(screen.queryByText('Station 9M')).not.toBeInTheDocument()
    })
  })

  describe('Data Display', () => {
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
        },
        {
          id: '14M',
          name: 'Station 14M',
          coordinates: { lat: 32.2667, lon: -80.9 },
          deployments: [
            {
              start: '2021-01-25',
              end: '2021-04-26',
              deployment_id: '14M_1084_042621'
            }
          ],
          summary_stats: {
            total_detections: 1200,
            species_count: 8,
            recording_hours: 2100,
            years_active: [2021]
          }
        },
        {
          id: '37M',
          name: 'Station 37M',
          coordinates: { lat: 32.25, lon: -80.9167 },
          deployments: [
            {
              start: '2021-01-25',
              end: '2021-04-26',
              deployment_id: '37M_1152_042621'
            }
          ],
          summary_stats: {
            total_detections: 980,
            species_count: 6,
            recording_hours: 1890,
            years_active: [2021]
          }
        }
      ],
      metadata: {
        generated_at: '2025-08-26T16:02:28.477276Z',
        data_sources: ['stations.json', 'detections.json'],
        total_stations: 3
      }
    }

    it('should display station data when loaded successfully', () => {
      mockUseStationOverview.mockReturnValue({
        data: mockStationData,
        loading: false,
        error: null,
      })

      render(<StationsV2Page />)
      
      expect(screen.getByText('Station 9M')).toBeInTheDocument()
      expect(screen.getByText('Station 14M')).toBeInTheDocument()
      expect(screen.getByText('Station 37M')).toBeInTheDocument()
    })

    it('should display summary statistics for each station', () => {
      mockUseStationOverview.mockReturnValue({
        data: mockStationData,
        loading: false,
        error: null,
      })

      render(<StationsV2Page />)
      
      // Check for detection counts (may have commas formatting)
      expect(screen.getByText('1,500')).toBeInTheDocument() // Station 9M detections
      expect(screen.getByText('1,200')).toBeInTheDocument() // Station 14M detections
      expect(screen.getByText('980')).toBeInTheDocument()    // Station 37M detections
      
      // Check for species counts
      expect(screen.getByText('12')).toBeInTheDocument()
      expect(screen.getByText('8')).toBeInTheDocument()
      expect(screen.getByText('6')).toBeInTheDocument()
    })

    it('should display coordinates for each station', () => {
      mockUseStationOverview.mockReturnValue({
        data: mockStationData,
        loading: false,
        error: null,
      })

      render(<StationsV2Page />)
      
      // Check coordinates are displayed (formatted to 4 decimal places)
      expect(screen.getByText(/32\.2833/)).toBeInTheDocument()
      expect(screen.getByText(/-80\.8833/)).toBeInTheDocument()
      expect(screen.getByText(/32\.2667/)).toBeInTheDocument()
      expect(screen.getByText(/-80\.9000/)).toBeInTheDocument()
    })

    it('should display deployment information', () => {
      mockUseStationOverview.mockReturnValue({
        data: mockStationData,
        loading: false,
        error: null,
      })

      render(<StationsV2Page />)
      
      // Check that years are shown in the active years section
      expect(screen.getAllByText('2021')).toHaveLength(3) // Should appear for all 3 stations
      
      // Check for deployment count - each station has 1 deployment in mock data
      expect(screen.getAllByText('1')).toHaveLength(3) // Deployment counts for each station
    })

    it('should not display loading or error when data is loaded', () => {
      mockUseStationOverview.mockReturnValue({
        data: mockStationData,
        loading: false,
        error: null,
      })

      render(<StationsV2Page />)
      
      expect(screen.queryByText(/loading.*station/i)).not.toBeInTheDocument()
      expect(screen.queryByText(/error.*loading/i)).not.toBeInTheDocument()
    })
  })

  describe('Performance Indicators', () => {
    it('should indicate this is the new optimized version', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      
      // Should have some indicator this is the v2 page
      const pageElement = screen.getByRole('main')
      expect(pageElement).toHaveAttribute('data-testid', 'stations-v2-page')
    })

    it('should handle empty stations array gracefully', () => {
      const emptyData = {
        stations: [],
        metadata: {
          generated_at: '2025-08-26T16:02:28.477276Z',
          data_sources: [],
          total_stations: 0
        }
      }

      mockUseStationOverview.mockReturnValue({
        data: emptyData,
        loading: false,
        error: null,
      })

      render(<StationsV2Page />)
      
      expect(screen.getByText(/no stations/i)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      
      const h1 = screen.getByRole('heading', { level: 1 })
      expect(h1).toBeInTheDocument()
    })

    it('should have semantic HTML structure', () => {
      mockUseStationOverview.mockReturnValue({
        data: null,
        loading: true,
        error: null,
      })

      render(<StationsV2Page />)
      
      expect(screen.getByRole('main')).toBeInTheDocument()
    })
  })
})