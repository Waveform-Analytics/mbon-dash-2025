'use client'

import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

import type { ProcessedStation } from '@/app/page';

interface StationMapProps {
  stations: ProcessedStation[];
}

export function StationMap({ stations }: StationMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    // Don't initialize if no container
    if (!mapContainer.current) return;

    // Set token
    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

    // Initialize map if it doesn't exist
    if (!map.current) {
      // Create map
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-80.9, 32.2],
        zoom: 9
      });

      // Add navigation controls
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    }

    // Clear existing markers
    const markers = document.querySelectorAll('.mapboxgl-marker');
    markers.forEach(marker => marker.remove());

    // When map is ready, add markers
    const addMarkers = () => {
      // Add markers for each station
      stations.forEach(station => {
        const popupContent = `
          <div style="padding: 8px;">
            <h3 style="margin: 0 0 8px 0; font-weight: bold;">${station.name}</h3>
            <p style="margin: 4px 0; font-size: 14px;">
              <strong>Deployments:</strong> ${station.deploymentCount}
            </p>
            <p style="margin: 4px 0; font-size: 14px;">
              <strong>Years:</strong> ${station.years.join(', ')}
            </p>
            <p style="margin: 4px 0; font-size: 14px;">
              <strong>Period:</strong> ${new Date(station.dateRange.start).toLocaleDateString()} - 
              ${new Date(station.dateRange.end).toLocaleDateString()}
            </p>
          </div>
        `;
        
        const popup = new mapboxgl.Popup({
          offset: 25,
          closeButton: false
        }).setHTML(popupContent);
        
        new mapboxgl.Marker({
          color: '#0891b2'
        })
          .setLngLat([station.lng, station.lat])
          .setPopup(popup)
          .addTo(map.current!);
      });
      
      // Fit bounds to show all stations
      if (stations.length > 0) {
        const bounds = new mapboxgl.LngLatBounds();
        stations.forEach(station => {
          bounds.extend([station.lng, station.lat]);
        });
        map.current!.fitBounds(bounds, { padding: 50 });
      }
    };

    // Add markers when map is loaded or immediately if already loaded
    if (map.current.loaded()) {
      addMarkers();
    } else {
      map.current.once('load', addMarkers);
    }

    // Cleanup
    return () => {
      // Only remove the map when component unmounts
      if (!stations || stations.length === 0) {
        map.current?.remove();
        map.current = null;
      }
    };
  }, [stations]); // Re-run when stations change
  
  // The actual HTML element that will contain the map
  return (
    <div 
      ref={mapContainer} 
      className="h-full w-full rounded-lg"
      style={{ minHeight: '400px' }}  // Ensure minimum height
    />
  );
}