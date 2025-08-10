/**
 * Filter Panel Component
 * Provides global filtering controls using Zustand store
 */

'use client';

import React from 'react';
import { useAppStore, useFilters } from '@/store/useAppStore';
import { FunnelIcon } from '@heroicons/react/24/outline';

export function FilterPanel() {
  const filters = useFilters();
  const {
    setSelectedStations,
    setSelectedSpecies: _setSelectedSpecies,
    setSelectedYear,
    setAggregationLevel,
    resetFilters,
    availableStations: _availableStations,
    availableSpecies: _availableSpecies,
  } = useAppStore();

  const years = [2018, 2021]; // Available years from data

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5 text-slate-600" />
          <h3 className="font-semibold text-slate-900">Filters</h3>
        </div>
        <button
          onClick={resetFilters}
          className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
        >
          Reset all
        </button>
      </div>

      {/* Station Filter */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Stations
        </label>
        <div className="space-y-2">
          {['9M', '14M', '37M'].map((station) => (
            <label key={station} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.selectedStations.includes(station)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedStations([...filters.selectedStations, station]);
                  } else {
                    setSelectedStations(
                      filters.selectedStations.filter((s) => s !== station)
                    );
                  }
                }}
                className="mr-2 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-slate-700">{station}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Year Filter */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Year
        </label>
        <select
          value={filters.selectedYear || ''}
          onChange={(e) =>
            setSelectedYear(e.target.value ? parseInt(e.target.value) : null)
          }
          className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Years</option>
          {years.map((year) => (
            <option key={year} value={year}>
              {year}
            </option>
          ))}
        </select>
      </div>

      {/* Aggregation Level */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Data Aggregation
        </label>
        <div className="flex gap-2">
          <button
            onClick={() => setAggregationLevel('monthly')}
            className={`flex-1 px-3 py-2 text-sm rounded-md transition-colors ${
              filters.aggregationLevel === 'monthly'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setAggregationLevel('yearly')}
            className={`flex-1 px-3 py-2 text-sm rounded-md transition-colors ${
              filters.aggregationLevel === 'yearly'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Yearly
          </button>
        </div>
      </div>

      {/* Active Filters Summary */}
      {(filters.selectedStations.length > 0 ||
        filters.selectedSpecies.length > 0 ||
        filters.selectedYear) && (
        <div className="pt-4 border-t border-slate-200">
          <div className="text-sm text-slate-600">
            <span className="font-medium">Active filters:</span>
            {filters.selectedStations.length > 0 && (
              <div className="mt-1">
                Stations: {filters.selectedStations.join(', ')}
              </div>
            )}
            {filters.selectedYear && (
              <div className="mt-1">Year: {filters.selectedYear}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Mobile Filter Button
 * Toggles filter panel on mobile devices
 */
export function MobileFilterButton() {
  const { ui, setMobileMenuOpen } = useAppStore();
  const filters = useFilters();

  const activeFilterCount =
    filters.selectedStations.length +
    filters.selectedSpecies.length +
    (filters.selectedYear ? 1 : 0);

  return (
    <button
      onClick={() => setMobileMenuOpen(!ui.mobileMenuOpen)}
      className="lg:hidden fixed bottom-4 right-4 z-40 bg-blue-600 text-white rounded-full p-3 shadow-lg hover:bg-blue-700 transition-colors"
    >
      <FunnelIcon className="h-6 w-6" />
      {activeFilterCount > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
          {activeFilterCount}
        </span>
      )}
    </button>
  );
}