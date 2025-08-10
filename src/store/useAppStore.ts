/**
 * Global application state management using Zustand
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Station, Species } from '@/types/data';

// Filter state interface
interface FilterState {
  selectedStations: string[];
  selectedSpecies: string[];
  dateRange: [Date | null, Date | null];
  selectedYear: number | null;
  aggregationLevel: 'monthly' | 'yearly';
}

// UI state interface
interface UIState {
  sidebarOpen: boolean;
  mobileMenuOpen: boolean;
  activeModal: string | null;
  chartView: 'heatmap' | 'timeline' | 'comparison';
}

// Data cache interface
interface DataCache {
  lastFetch: number;
  cachedData: {
    detections?: unknown[];
    environmental?: unknown[];
    acoustic?: unknown[];
  };
}

// Main app store interface
interface AppStore {
  // Filter state
  filters: FilterState;
  setSelectedStations: (stations: string[]) => void;
  setSelectedSpecies: (species: string[]) => void;
  setDateRange: (range: [Date | null, Date | null]) => void;
  setSelectedYear: (year: number | null) => void;
  setAggregationLevel: (level: 'monthly' | 'yearly') => void;
  resetFilters: () => void;

  // UI state
  ui: UIState;
  setSidebarOpen: (open: boolean) => void;
  setMobileMenuOpen: (open: boolean) => void;
  setActiveModal: (modal: string | null) => void;
  setChartView: (view: 'heatmap' | 'timeline' | 'comparison') => void;

  // Data cache
  cache: DataCache;
  updateCache: (data: Partial<DataCache['cachedData']>) => void;
  clearCache: () => void;

  // Reference data
  availableStations: Station[];
  availableSpecies: Species[];
  setAvailableStations: (stations: Station[]) => void;
  setAvailableSpecies: (species: Species[]) => void;
}

// Initial state values
const initialFilterState: FilterState = {
  selectedStations: [],
  selectedSpecies: [],
  dateRange: [null, null],
  selectedYear: null,
  aggregationLevel: 'monthly',
};

const initialUIState: UIState = {
  sidebarOpen: false,
  mobileMenuOpen: false,
  activeModal: null,
  chartView: 'heatmap',
};

const initialCacheState: DataCache = {
  lastFetch: 0,
  cachedData: {},
};

// Create the store
export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set) => ({
        // Filter state
        filters: initialFilterState,
        setSelectedStations: (stations) =>
          set((state) => ({
            filters: { ...state.filters, selectedStations: stations },
          })),
        setSelectedSpecies: (species) =>
          set((state) => ({
            filters: { ...state.filters, selectedSpecies: species },
          })),
        setDateRange: (range) =>
          set((state) => ({
            filters: { ...state.filters, dateRange: range },
          })),
        setSelectedYear: (year) =>
          set((state) => ({
            filters: { ...state.filters, selectedYear: year },
          })),
        setAggregationLevel: (level) =>
          set((state) => ({
            filters: { ...state.filters, aggregationLevel: level },
          })),
        resetFilters: () =>
          set(() => ({
            filters: initialFilterState,
          })),

        // UI state
        ui: initialUIState,
        setSidebarOpen: (open) =>
          set((state) => ({
            ui: { ...state.ui, sidebarOpen: open },
          })),
        setMobileMenuOpen: (open) =>
          set((state) => ({
            ui: { ...state.ui, mobileMenuOpen: open },
          })),
        setActiveModal: (modal) =>
          set((state) => ({
            ui: { ...state.ui, activeModal: modal },
          })),
        setChartView: (view) =>
          set((state) => ({
            ui: { ...state.ui, chartView: view },
          })),

        // Data cache
        cache: initialCacheState,
        updateCache: (data) =>
          set((state) => ({
            cache: {
              lastFetch: Date.now(),
              cachedData: { ...state.cache.cachedData, ...data },
            },
          })),
        clearCache: () =>
          set(() => ({
            cache: initialCacheState,
          })),

        // Reference data
        availableStations: [],
        availableSpecies: [],
        setAvailableStations: (stations) =>
          set(() => ({
            availableStations: stations,
          })),
        setAvailableSpecies: (species) =>
          set(() => ({
            availableSpecies: species,
          })),
      }),
      {
        name: 'mbon-app-store',
        partialize: (state) => ({
          // Only persist filters and UI preferences
          filters: state.filters,
          ui: {
            chartView: state.ui.chartView,
            aggregationLevel: state.filters.aggregationLevel,
          },
        }),
      }
    ),
    {
      name: 'MBON Dashboard Store',
    }
  )
);

// Selector hooks for common use cases
export const useFilters = () => useAppStore((state) => state.filters);
export const useUIState = () => useAppStore((state) => state.ui);
export const useSelectedStations = () =>
  useAppStore((state) => state.filters.selectedStations);
export const useSelectedSpecies = () =>
  useAppStore((state) => state.filters.selectedSpecies);
export const useChartView = () => useAppStore((state) => state.ui.chartView);