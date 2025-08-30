import React, { useState } from 'react';
import { instrumentLocations, InstrumentLocation } from '../data/mockData';
import { Tooltip } from './ui/tooltip';

export function InstrumentMap() {
  const [hoveredInstrument, setHoveredInstrument] = useState<string | null>(null);

  // Convert lat/lng to SVG coordinates
  // May River SC bounds: roughly 32.29-32.33°N, 80.81-80.78°W
  const bounds = {
    north: 32.33,
    south: 32.29,
    east: -80.78,
    west: -80.81
  };

  const svgWidth = 400;
  const svgHeight = 300;

  const latLngToSvg = (lat: number, lng: number) => {
    const x = ((lng - bounds.west) / (bounds.east - bounds.west)) * svgWidth;
    const y = ((bounds.north - lat) / (bounds.north - bounds.south)) * svgHeight;
    return { x, y };
  };

  const getInstrumentColor = (status: string) => {
    switch (status) {
      case 'active': return '#22c55e';
      case 'maintenance': return '#eab308';
      case 'offline': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const getInstrumentIcon = (type: string) => {
    switch (type) {
      case 'hydrophone': return '🌊';
      case 'terrestrial': return '🌿';
      case 'combined': return '🔀';
      default: return '📍';
    }
  };

  return (
    <div className="relative">
      <svg 
        width="100%" 
        height="300" 
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="border rounded-lg bg-blue-50"
      >
        {/* Background water areas */}
        <defs>
          <pattern id="water" patternUnits="userSpaceOnUse" width="4" height="4">
            <rect width="4" height="4" fill="#e0f2fe"/>
            <path d="M 0,4 l 4,-4 M -1,1 l 2,-2 M 3,5 l 2,-2" stroke="#0891b2" strokeWidth="0.5" opacity="0.3"/>
          </pattern>
        </defs>
        
        {/* May River main channel */}
        <path
          d="M 50 150 Q 150 120 250 140 Q 320 155 380 170"
          stroke="#0891b2"
          strokeWidth="8"
          fill="none"
          opacity="0.6"
        />
        
        {/* Oyster Creek */}
        <path
          d="M 180 180 Q 200 160 220 140"
          stroke="#0891b2"
          strokeWidth="4"
          fill="none"
          opacity="0.6"
        />
        
        {/* Bluffton Creek */}
        <path
          d="M 100 220 Q 130 200 160 185"
          stroke="#0891b2"
          strokeWidth="4"
          fill="none"
          opacity="0.6"
        />

        {/* Marsh areas */}
        <circle cx="320" cy="100" r="30" fill="#86efac" opacity="0.3" />
        <circle cx="120" cy="80" r="25" fill="#86efac" opacity="0.3" />
        <circle cx="280" cy="220" r="20" fill="#86efac" opacity="0.3" />

        {/* Land masses */}
        <rect x="0" y="0" width="80" height="120" fill="#fbbf24" opacity="0.2" />
        <rect x="350" y="50" width="50" height="100" fill="#fbbf24" opacity="0.2" />
        <rect x="200" y="250" width="200" height="50" fill="#fbbf24" opacity="0.2" />

        {/* Instrument locations */}
        {instrumentLocations.map((instrument) => {
          const { x, y } = latLngToSvg(instrument.lat, instrument.lng);
          const isHovered = hoveredInstrument === instrument.id;
          
          return (
            <g key={instrument.id}>
              {/* Instrument marker */}
              <circle
                cx={x}
                cy={y}
                r={isHovered ? 12 : 8}
                fill={getInstrumentColor(instrument.status)}
                stroke="white"
                strokeWidth="2"
                className="cursor-pointer transition-all duration-200"
                onMouseEnter={() => setHoveredInstrument(instrument.id)}
                onMouseLeave={() => setHoveredInstrument(null)}
              />
              
              {/* Instrument type icon */}
              <text
                x={x}
                y={y + 1}
                textAnchor="middle"
                className="text-xs pointer-events-none select-none"
              >
                {instrument.type === 'hydrophone' ? '🌊' : 
                 instrument.type === 'terrestrial' ? '🌿' : '🔀'}
              </text>
              
              {/* Label */}
              <text
                x={x}
                y={y - 15}
                textAnchor="middle"
                className="text-xs font-medium fill-slate-700 pointer-events-none select-none"
                opacity={isHovered ? 1 : 0.7}
              >
                {instrument.id}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Hover tooltip */}
      {hoveredInstrument && (
        <div className="absolute top-4 left-4 bg-white p-3 rounded-lg shadow-lg border text-sm">
          {(() => {
            const instrument = instrumentLocations.find(i => i.id === hoveredInstrument);
            if (!instrument) return null;
            
            return (
              <div>
                <div className="font-semibold">{instrument.name}</div>
                <div className="text-muted-foreground text-xs space-y-1">
                  <div>ID: {instrument.id}</div>
                  <div>Type: {instrument.type}</div>
                  <div>Status: <span className={`capitalize ${
                    instrument.status === 'active' ? 'text-green-600' :
                    instrument.status === 'maintenance' ? 'text-yellow-600' :
                    'text-gray-600'
                  }`}>{instrument.status}</span></div>
                  <div>Deployed: {new Date(instrument.deploymentDate).toLocaleDateString()}</div>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* Map legend */}
      <div className="mt-4 text-xs text-muted-foreground space-y-1">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-200 rounded"></div>
          <span>Water bodies (May River, creeks)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-200 rounded"></div>
          <span>Salt marsh and wetlands</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-200 rounded"></div>
          <span>Land areas</span>
        </div>
      </div>
    </div>
  );
}