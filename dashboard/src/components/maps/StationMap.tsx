'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Station } from '@/types/data';

// Set Mapbox access token from environment variable
if (process.env.NEXT_PUBLIC_MAPBOX_TOKEN) {
  mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
}

interface StationMapProps {
  stations: Station[];
  className?: string;
  height?: string;
}

export default function StationMap({ stations, className = '', height = '500px' }: StationMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [selectedStation, setSelectedStation] = useState<Station | null>(null);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Calculate center and bounds
    const validStations = stations.filter(s => s.coordinates.latitude && s.coordinates.longitude);
    
    if (validStations.length === 0) {
      console.warn('No stations with valid coordinates');
      return;
    }

    const bounds = new mapboxgl.LngLatBounds();
    validStations.forEach(station => {
      if (station.coordinates.latitude && station.coordinates.longitude) {
        bounds.extend([station.coordinates.longitude, station.coordinates.latitude]);
      }
    });

    // Initialize map with clean, minimal style
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      // Minimal vector styles - choose your favorite:
      style: 'mapbox://styles/mapbox/light-v11', // Light and clean (current)
      // style: 'mapbox://styles/mapbox/streets-v12', // Classic street map  
      // style: 'mapbox://styles/mapbox/outdoors-v12', // Terrain-focused
      // style: 'mapbox://styles/mapbox/navigation-day-v1', // Navigation style
      center: bounds.getCenter(),
      zoom: 10,
      pitch: 0,
      bearing: 0,
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.current.addControl(new mapboxgl.ScaleControl(), 'bottom-left');

    // Handle map load
    map.current.on('load', () => {
      setMapLoaded(true);
      
      // Fit to bounds with padding
      map.current?.fitBounds(bounds, {
        padding: { top: 100, bottom: 100, left: 100, right: 100 },
        duration: 1000
      });

      // Add stations as a source
      map.current?.addSource('stations', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: validStations.map(station => ({
            type: 'Feature',
            geometry: {
              type: 'Point',
              coordinates: [station.coordinates.longitude!, station.coordinates.latitude!]
            },
            properties: {
              id: station.id,
              name: station.name,
              depth: station.depth_m,
              platform: station.platform,
              hasIndices: station.data_availability.acoustic_indices,
              deployments: station.deployment_periods.length
            }
          }))
        }
      });

      // Add station circles
      map.current?.addLayer({
        id: 'station-circles',
        type: 'circle',
        source: 'stations',
        paint: {
          'circle-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            8, 10,
            12, 20
          ],
          'circle-color': [
            'case',
            ['get', 'hasIndices'],
            '#10b981', // Green for stations with indices
            '#3b82f6'  // Blue for stations without
          ],
          'circle-opacity': 0.8,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#ffffff'
        }
      });

      // Add station labels
      map.current?.addLayer({
        id: 'station-labels',
        type: 'symbol',
        source: 'stations',
        layout: {
          'text-field': ['get', 'id'],
          'text-font': ['DIN Pro Bold', 'Arial Unicode MS Bold'],
          'text-size': 14,
          'text-anchor': 'bottom',
          'text-offset': [0, -1.5]
        },
        paint: {
          'text-color': '#ffffff',
          'text-halo-color': '#000000',
          'text-halo-width': 2
        }
      });

      // Add click interaction
      map.current?.on('click', 'station-circles', (e) => {
        if (!e.features || !e.features[0]) return;
        
        const feature = e.features[0];
        const station = stations.find(s => s.id === feature.properties?.id);
        if (station) {
          setSelectedStation(station);
        }

        // Center on clicked station with animation
        if (feature.geometry.type === 'Point') {
          map.current?.flyTo({
            center: feature.geometry.coordinates as [number, number],
            zoom: 12,
            duration: 1000
          });
        }
      });

      // Change cursor on hover
      map.current?.on('mouseenter', 'station-circles', () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = 'pointer';
        }
      });

      map.current?.on('mouseleave', 'station-circles', () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = '';
        }
      });
    });

    // Cleanup
    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, [stations]);

  // Add popups for selected stations
  useEffect(() => {
    if (!map.current || !mapLoaded || !selectedStation) return;

    // Remove existing popups
    const popups = document.getElementsByClassName('mapboxgl-popup');
    while (popups[0]) {
      popups[0].remove();
    }

    if (selectedStation.coordinates.latitude && selectedStation.coordinates.longitude) {
      const popup = new mapboxgl.Popup({
        closeButton: true,
        closeOnClick: true,
        offset: 25
      })
        .setLngLat([selectedStation.coordinates.longitude, selectedStation.coordinates.latitude])
        .setHTML(`
          <div class="p-3 min-w-[200px]">
            <h3 class="font-bold text-lg mb-2">${selectedStation.name}</h3>
            <div class="space-y-1 text-sm">
              <p><span class="font-semibold">Platform:</span> ${selectedStation.platform}</p>
              <p><span class="font-semibold">Depth:</span> ${selectedStation.depth_m ? Math.abs(selectedStation.depth_m).toFixed(1) + 'm' : 'N/A'}</p>
              <p><span class="font-semibold">Deployments:</span> ${selectedStation.deployment_periods.length}</p>
              <p><span class="font-semibold">Years:</span> ${selectedStation.data_availability.years.join(', ')}</p>
              <div class="mt-2 pt-2 border-t">
                ${selectedStation.data_availability.detection_data ? '<span class="inline-block bg-green-100 text-green-700 px-2 py-1 rounded text-xs mr-1">Detections</span>' : ''}
                ${selectedStation.data_availability.acoustic_indices ? '<span class="inline-block bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">Indices</span>' : ''}
              </div>
            </div>
          </div>
        `)
        .addTo(map.current);

      // Close popup when clicking elsewhere
      popup.on('close', () => {
        setSelectedStation(null);
      });
    }
  }, [selectedStation, mapLoaded]);

  return (
    <div className={`relative ${className}`}>
      <div 
        ref={mapContainer} 
        className="w-full rounded-lg shadow-xl overflow-hidden"
        style={{ height }}
      />
      
      {/* Map Legend */}
      <div className="absolute bottom-4 right-4 bg-white/95 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-gray-200">
        <h4 className="font-semibold text-sm mb-2 text-gray-800">Station Types</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500 border-2 border-white shadow-sm"></div>
            <span className="text-xs text-gray-700">With Acoustic Indices</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500 border-2 border-white shadow-sm"></div>
            <span className="text-xs text-gray-700">Detection Data Only</span>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100/50 backdrop-blur">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <p className="text-sm text-gray-600">Loading map...</p>
          </div>
        </div>
      )}
    </div>
  );
}