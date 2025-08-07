'use client'  // This tells Next.js this is a client-side component

import { useEffect, useRef, useState } from 'react';
import 'mapbox-gl/dist/mapbox-gl.css';  // CSS can stay as static import

// Import the ProcessedStation type from the page file
import type { ProcessedStation } from '@/app/page';

// Define the props (inputs) this component expects
interface StationMapProps {
  stations: ProcessedStation[];  // Array of processed stations from Step 2
}

export function StationMap({ stations }: StationMapProps) {
  // State to track if mapbox is loaded
  const [mapboxgl, setMapboxgl] = useState<typeof import('mapbox-gl') | null>(null);
  
  // useRef creates a reference to DOM elements and values that persist between renders
  const mapContainer = useRef<HTMLDivElement>(null);  // Reference to the map's DOM container
  const map = useRef<any>(null);     // Reference to the Mapbox instance
  
  // Load mapbox-gl dynamically
  useEffect(() => {
    import('mapbox-gl').then((module) => {
      setMapboxgl(module.default);
    });
  }, []);
  
  // Initialize map once mapbox is loaded
  useEffect(() => {
    // Safety checks
    if (!mapContainer.current || !mapboxgl || map.current) return;
    
    // Configure Mapbox with the access token
    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';
    
    // Create the map instance
    map.current = new mapboxgl.Map({
      container: mapContainer.current,           // HTML element to render in
      style: 'mapbox://styles/mapbox/light-v11', // Map style (light theme)
      center: [-80.9, 32.2],                    // Starting position [lng, lat] - South Carolina coast
      zoom: 9                                    // Starting zoom level
    });
    
    // Add navigation controls (zoom buttons)
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');
    
    // Wait for the map to load before adding markers
    map.current.on('load', () => {
      // Add a marker for each station
      stations.forEach(station => {
        // Create the popup content with HTML
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
        
        // Create the popup
        const popup = new mapboxgl.Popup({
          offset: 25,  // Offset from the marker
          closeButton: false  // No close button (click away to close)
        }).setHTML(popupContent);
        
        // Create the marker
        new mapboxgl.Marker({
          color: '#0891b2'  // Ocean blue color to match the theme
        })
          .setLngLat([station.lng, station.lat])  // Set position
          .setPopup(popup)                        // Attach popup
          .addTo(map.current!);                   // Add to map
      });
      
      // If we have stations, fit the map to show all of them
      if (stations.length > 0) {
        const bounds = new mapboxgl.LngLatBounds();
        stations.forEach(station => {
          bounds.extend([station.lng, station.lat]);
        });
        map.current!.fitBounds(bounds, { padding: 50 });
      }
    });
    
    // Cleanup function (runs when component unmounts)
    return () => {
      map.current?.remove();
    };
  }, [mapboxgl, stations]);  // Re-run if mapbox loads or stations change
  
  // Show loading state while mapbox is loading
  if (!mapboxgl) {
    return (
      <div className="h-64 w-full rounded-lg flex items-center justify-center bg-slate-50">
        <div className="text-slate-500">Loading map...</div>
      </div>
    );
  }
  
  // The actual HTML element that will contain the map
  return (
    <div 
      ref={mapContainer} 
      className="h-64 w-full rounded-lg"
      style={{ minHeight: '256px' }}  // Ensure minimum height
    />
  );
}