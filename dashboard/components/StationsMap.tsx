'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import { useStationLocations, StationLocation } from '../lib/data';

interface StationsMapProps {
  className?: string;
}

export default function StationsMap({ className }: StationsMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [showStudyAreaOnly, setShowStudyAreaOnly] = useState(true);
  
  // Use the new data loading hook
  const { data: stations, loading, error, source } = useStationLocations();

  const fitMapToStations = (studyAreaOnly: boolean) => {
    if (!map.current || !stations || stations.length === 0) return;

    const stationsToShow = studyAreaOnly 
      ? stations.filter(station => station.current_study)
      : stations;

    if (stationsToShow.length === 0) return;

    const bounds = new mapboxgl.LngLatBounds();
    stationsToShow.forEach((station) => {
      bounds.extend([station['GPS Long'], station['GPS Lat']]);
    });
    
    map.current.fitBounds(bounds, { 
      padding: studyAreaOnly ? 100 : 50,
      duration: 1000 
    });
  };

  const toggleView = () => {
    const newViewState = !showStudyAreaOnly;
    setShowStudyAreaOnly(newViewState);
    fitMapToStations(newViewState);
  };

  // Log data source for debugging
  useEffect(() => {
    if (source) {
      console.log(`[StationsMap] Data loaded from: ${source}`);
    }
  }, [source]);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!mapboxToken) {
      console.error('Mapbox token not found');
      return;
    }

    mapboxgl.accessToken = mapboxToken;

    try {
      // Initialize map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-80.0, 32.5], // Centered around South Carolina coast
        zoom: 8
      });

      map.current.on('error', (e) => {
        console.error('Map error:', e);
      });

    } catch (error) {
      console.error('Error initializing map:', error);
    }

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!map.current || !stations || stations.length === 0) return;

    map.current.on('load', () => {
      if (!map.current) return;

      // Add markers for each station
      stations.forEach((station) => {
        const el = document.createElement('div');
        el.className = 'station-marker';
        el.style.backgroundColor = station.current_study ? '#3b82f6' : '#6b7280';
        el.style.width = '12px';
        el.style.height = '12px';
        el.style.borderRadius = '50%';
        el.style.border = '2px solid white';
        el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
        el.style.cursor = 'pointer';

        // Create popup
        const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
          `<div class="p-2">
            <h3 class="font-semibold text-sm">${station.Station}</h3>
            <p class="text-xs text-gray-600">
              ${station.current_study ? 'Current Study' : 'Regional Context'}
            </p>
            <p class="text-xs">Deployments: ${station.total_deployments}</p>
            <p class="text-xs">Avg Depth: ${Math.abs(station.avg_depth_m)}m</p>
            <p class="text-xs text-gray-500">
              ${station['GPS Lat'].toFixed(4)}°, ${station['GPS Long'].toFixed(4)}°
            </p>
          </div>`
        );

        // Add marker to map
        new mapboxgl.Marker(el)
          .setLngLat([station['GPS Long'], station['GPS Lat']])
          .setPopup(popup)
          .addTo(map.current!);
      });

      // Fit map to initial view (study area only by default)
      fitMapToStations(true);
    });
  }, [stations]);

  // Show loading state
  if (loading) {
    return (
      <div className={className}>
        <div className="relative w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
            <p className="text-sm text-muted-foreground">Loading station data...</p>
            {source && <p className="text-xs text-muted-foreground mt-1">From: {source}</p>}
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className={className}>
        <div className="relative w-full h-full bg-red-50 border border-red-200 rounded-lg flex items-center justify-center">
          <div className="text-center p-4">
            <p className="text-sm text-red-600 mb-2">Failed to load station data</p>
            <p className="text-xs text-red-500">{error.message}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="relative w-full h-full">
        <div ref={mapContainer} className="w-full h-full rounded-lg" />
        
        {/* Data source indicator */}
        {source && (
          <div className="absolute top-2 left-2 z-10">
            <div className="bg-black/75 text-white px-2 py-1 rounded text-xs">
              Data: {source === 'cdn' ? '🌐 CDN' : '🏠 Local'}
            </div>
          </div>
        )}
        
        {/* Toggle Button */}
        <div className="absolute top-2 right-2 z-10">
          <button
            onClick={toggleView}
            className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm font-medium shadow-sm hover:bg-gray-50 transition-colors"
          >
            {showStudyAreaOnly ? 'Show All Stations' : 'Show Study Area'}
          </button>
        </div>
      </div>
      
      <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-blue-500 rounded-full border border-white"></div>
          <span>Current Study Stations (3)</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-gray-500 rounded-full border border-white"></div>
          <span>Regional Context Stations (9)</span>
        </div>
      </div>
    </div>
  );
}