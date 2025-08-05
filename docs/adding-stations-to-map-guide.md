# Complete Guide: Adding Stations to the Map

## Table of Contents
1. [Overview](#overview)
2. [Understanding the Data Flow](#understanding-the-data-flow)
3. [Step 1: Creating a Custom Hook](#step-1-creating-a-custom-hook)
4. [Step 2: Processing Station Data](#step-2-processing-station-data)
5. [Step 3: Creating the Map Component](#step-3-creating-the-map-component)
6. [Step 4: Integrating Everything](#step-4-integrating-everything)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

## Overview

This guide walks through adding an interactive map to the Marine Biodiversity Dashboard that displays all monitoring stations. The implementation uses:

- **Data Source**: `deployment_metadata.json` from Cloudflare R2
- **Map Library**: Mapbox GL JS (already in the project)
- **Framework**: Next.js with TypeScript
- **Goal**: Display station locations with popup information

### Key Concepts Covered
- How React hooks work to fetch data
- How to process JSON data in JavaScript
- How to create a map component
- How to integrate components in Next.js

## Understanding the Data Flow

Before coding, it's important to understand how data flows through the application:

```
Cloudflare R2 (deployment_metadata.json)
    ↓
React Hook (fetches data)
    ↓
Processing Function (groups by station)
    ↓
Map Component (displays markers)
    ↓
Main Page (shows the map)
```

## Step 1: Creating a Custom Hook

### What is a Hook?

In React, a "hook" is a special function that enables the use of React features (like state and lifecycle methods). Custom hooks allow reusing logic between components. They always start with "use" (like `useData`, `useState`, etc.).

### Adding the Deployment Metadata Hook

Open `/src/lib/hooks/useData.ts` and add this code at the end of the file:

```typescript
// First, add the TypeScript interface (this defines the shape of our data)
// This tells TypeScript what fields to expect in each deployment record
export interface DeploymentMetadata {
  object_id: number;
  station: string;           // e.g., "9M", "14M", "37M"
  year: number;             // e.g., 2017, 2018, 2021
  gps_lat: number;          // latitude coordinate
  gps_long: number;         // longitude coordinate (note: it's "long" not "lng" in the data)
  start_date: string;       // deployment start date
  end_date: string;         // deployment end date
  depth_m: number;          // depth in meters (might be negative)
  deployment_id: string;    // unique identifier like "9M_1082_020217"
  // Add other fields as needed for the map popups
  platform_type?: string;
  salinity_ppt?: number;
  temperature_c?: number;
}

/**
 * Hook to load deployment metadata
 * This follows the same pattern as the other hooks in this file
 */
export function useDeploymentMetadata(): UseDataResult<DeploymentMetadata[]> {
  // useState is a React hook that manages state in functional components
  // We're creating three pieces of state:
  const [data, setData] = useState<DeploymentMetadata[] | null>(null);  // The actual data
  const [loading, setLoading] = useState(true);                         // Loading indicator
  const [error, setError] = useState<Error | null>(null);              // Any errors

  // This function does the actual data fetching
  const fetchDeploymentMetadata = async () => {
    try {
      setLoading(true);      // Tell the UI we're loading
      setError(null);        // Clear any previous errors
      
      // Fetch the data using the helper function already in this file
      const deployments = await fetchData<DeploymentMetadata[]>('deployment_metadata.json');
      
      setData(deployments);  // Store the data in state
    } catch (err) {
      setError(err as Error);  // If something goes wrong, store the error
    } finally {
      setLoading(false);     // We're done loading (success or failure)
    }
  };

  // useEffect runs code after the component renders
  // The empty array [] means "run this only once when the component mounts"
  useEffect(() => {
    fetchDeploymentMetadata();
  }, []);

  // Return an object with our data, loading state, error state, and a refetch function
  return { data, loading, error, refetch: fetchDeploymentMetadata };
}
```

### Why This Pattern?

This hook pattern is powerful because:
1. It separates data fetching from UI rendering
2. It provides loading and error states automatically
3. It can be reused in any component that needs deployment data
4. It follows the same pattern as the other hooks for consistency

## Step 2: Processing Station Data

### The Challenge

The `deployment_metadata.json` file has multiple records per station (one for each deployment period). For the map, the requirements are:
- One marker per station (not per deployment)
- The station's coordinates
- Summary information about all deployments at that station

### Creating a Processing Function

Add this to the main page file (`/src/app/page.tsx`) after the imports:

```typescript
// This interface defines what our processed station data will look like
interface ProcessedStation {
  name: string;              // Station name (e.g., "9M")
  lat: number;               // Latitude
  lng: number;               // Longitude (note: we rename from "long" to "lng")
  deploymentCount: number;   // How many times was equipment deployed here?
  years: number[];           // Which years had deployments?
  dateRange: {              // Overall date range for this station
    start: string;
    end: string;
  };
  // Additional summary fields can be added as needed
}

// This function processes the raw deployment data into station summaries
function processStationsForMap(deployments: DeploymentMetadata[]): ProcessedStation[] {
  // A Map is like an object but better for grouping data
  // The key will be the station name, the value will be our processed data
  const stationMap = new Map<string, ProcessedStation>();
  
  // Loop through each deployment record
  deployments.forEach(deployment => {
    const stationName = deployment.station;
    
    // If we haven't seen this station before, create a new entry
    if (!stationMap.has(stationName)) {
      stationMap.set(stationName, {
        name: stationName,
        lat: deployment.gps_lat,
        lng: deployment.gps_long,  // Note: renaming "long" to "lng"
        deploymentCount: 0,
        years: [],
        dateRange: {
          start: deployment.start_date,
          end: deployment.end_date
        }
      });
    }
    
    // Get the existing station data
    const station = stationMap.get(stationName)!;
    
    // Update the station's aggregate data
    station.deploymentCount += 1;
    
    // Add year if we haven't seen it before
    if (!station.years.includes(deployment.year)) {
      station.years.push(deployment.year);
    }
    
    // Update date range (keep earliest start and latest end)
    if (deployment.start_date < station.dateRange.start) {
      station.dateRange.start = deployment.start_date;
    }
    if (deployment.end_date > station.dateRange.end) {
      station.dateRange.end = deployment.end_date;
    }
  });
  
  // Convert the Map back to an array and sort by station name
  return Array.from(stationMap.values()).sort((a, b) => a.name.localeCompare(b.name));
}
```

### What This Does

1. Takes all deployment records
2. Groups them by station name
3. Creates one summary object per station with:
   - Combined date range
   - Number of deployments
   - Years with data
   - Single coordinate pair (assumes coordinates don't change per station)

## Step 3: Creating the Map Component

### Setting Up Mapbox

First, ensure the Mapbox token is set in `.env.local`:
```
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
```

### Create the Map Component

Create a new file at `/src/components/maps/StationMap.tsx`:

```typescript
'use client'  // This tells Next.js this is a client-side component

import { useEffect, useRef } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';  // Don't forget the CSS!

// Configure Mapbox with the access token
mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

// Define the props (inputs) this component expects
interface StationMapProps {
  stations: ProcessedStation[];  // Array of processed stations from Step 2
}

// Define the station type (this can be imported from the page file instead)
interface ProcessedStation {
  name: string;
  lat: number;
  lng: number;
  deploymentCount: number;
  years: number[];
  dateRange: {
    start: string;
    end: string;
  };
}

export function StationMap({ stations }: StationMapProps) {
  // useRef creates a reference to DOM elements and values that persist between renders
  const mapContainer = useRef<HTMLDivElement>(null);  // Reference to the map's DOM container
  const map = useRef<mapboxgl.Map | null>(null);     // Reference to the Mapbox instance
  
  // useEffect runs after the component renders
  useEffect(() => {
    // Safety check: make sure we have a container
    if (!mapContainer.current || map.current) return;
    
    // Create the map instance
    map.current = new mapboxgl.Map({
      container: mapContainer.current,           // HTML element to render in
      style: 'mapbox://styles/mapbox/light-v11', // Map style (light theme)
      center: [-80.9, 32.2],                    // Starting position [lng, lat]
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
  }, [stations]);  // Re-run if stations change
  
  // The actual HTML element that will contain the map
  return (
    <div 
      ref={mapContainer} 
      className="h-64 w-full rounded-lg"
      style={{ minHeight: '256px' }}  // Ensure minimum height
    />
  );
}
```

### Key Concepts Explained

1. **useRef**: Keeps references to things that shouldn't trigger re-renders (like DOM elements)
2. **useEffect**: Runs code after render (perfect for initializing maps)
3. **Cleanup**: The return function in useEffect prevents memory leaks
4. **Mapbox coordinates**: Use [longitude, latitude] (opposite of Google Maps!)

## Step 4: Integrating Everything

### Update the Main Page

Now let's put it all together in `/src/app/page.tsx`:

```typescript
'use client'

import { useMemo } from 'react';  // Add this import
import { useCoreData, useDeploymentMetadata } from '@/lib/hooks/useData'
import { StationMap } from '@/components/maps/StationMap';  // Add this import

// Add the interfaces and processing function from Step 2 here
// (or better yet, move them to a separate utils file)

export default function DashboardPage() {
  // Existing data fetching
  const { metadata, stations, species, loading, error } = useCoreData()
  
  // NEW: Fetch deployment metadata
  const { 
    data: deployments, 
    loading: deploymentsLoading, 
    error: deploymentsError 
  } = useDeploymentMetadata();
  
  // NEW: Process the deployment data for the map
  // useMemo prevents recalculating on every render
  const stationsForMap = useMemo(() => {
    if (!deployments) return [];
    return processStationsForMap(deployments);
  }, [deployments]);  // Only recalculate if deployments change
  
  // Combine loading states
  const isLoading = loading || deploymentsLoading;
  
  if (isLoading) {
    // Existing loading UI
  }
  
  return (
    <div className="page-container">
      {/* Existing hero section and metrics cards */}
      
      {/* Update the map section */}
      <div className="card-grid lg:grid-cols-2 gap-8 mb-12">
        {/* Existing timeline chart */}
        
        <div className="chart-container group">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Station Distribution Map</h3>
            {deploymentsLoading && (
              <span className="badge badge-ocean">Loading...</span>
            )}
          </div>
          
          {/* Show the map if we have data, otherwise show placeholder */}
          {stationsForMap.length > 0 ? (
            <StationMap stations={stationsForMap} />
          ) : deploymentsLoading ? (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ocean-600 mx-auto"></div>
                <div className="text-slate-500 font-medium mt-4">Loading station locations...</div>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg">
              <div className="text-center">
                <div className="text-4xl mb-2">📍</div>
                <div className="text-slate-500 font-medium">No station data available</div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Rest of the page */}
    </div>
  )
}
```

### What's Happening Here

1. **useMemo**: This is a performance optimization. It only recalculates `stationsForMap` when `deployments` changes
2. **Multiple loading states**: We check both data sources for loading
3. **Conditional rendering**: Show map if data exists, loading spinner while loading, or placeholder if no data

## Troubleshooting

### Common Issues and Solutions

1. **Map doesn't appear**
   - Check browser console for errors
   - Verify the Mapbox token is set in `.env.local`
   - Make sure the map container has a height

2. **"Cannot read property 'lat' of undefined"**
   - Check that `gps_lat` and `gps_long` exist in the data
   - Verify the field names match exactly (it's `gps_long` not `gps_lng` in the data)

3. **Markers don't show up**
   - Check that coordinates are valid numbers
   - Verify they're in the correct order [lng, lat]
   - Check browser console for Mapbox errors

4. **TypeScript errors**
   - Make sure all interfaces are defined
   - Check that imports are correct
   - Run `npm run type-check` to see all TypeScript errors

### Debugging Tips

Add console.logs to understand the data:

```typescript
// In the processing function
console.log('Raw deployments:', deployments);
console.log('Processed stations:', stationsForMap);

// In the map component
console.log('Stations received by map:', stations);
```

## Next Steps

Once the basic map is working, possible enhancements include:

1. **Color-code markers** by number of deployments or years
2. **Add clustering** for overlapping stations
3. **Create custom markers** with station names
4. **Add a legend** explaining what the markers mean
5. **Link to station detail pages** from popups
6. **Add filters** to show/hide stations by year

### Example: Color-Coding Markers

```typescript
// In the map component, determine marker color based on data
const markerColor = station.deploymentCount > 5 ? '#dc2626' : '#0891b2';  // Red for busy stations

new mapboxgl.Marker({
  color: markerColor
})
```

## Resources for Learning More

- **React Hooks**: https://react.dev/learn/state-a-components-memory
- **Mapbox GL JS**: https://docs.mapbox.com/mapbox-gl-js/guides/
- **TypeScript Basics**: https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html
- **Next.js Data Fetching**: https://nextjs.org/docs/app/building-your-application/data-fetching

## Summary

This guide covered how to:
1. Create a custom React hook for data fetching
2. Process complex JSON data into a simpler format
3. Build an interactive map component
4. Integrate everything into a Next.js page

The key pattern is: **Fetch → Process → Display**

Remember: Web development is all about breaking complex problems into smaller, manageable pieces. Each piece (hook, component, function) should do one thing well!