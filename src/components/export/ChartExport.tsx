'use client';

import { useState } from 'react';
import { saveAs } from 'file-saver';

interface ChartExportProps {
  chartRef: React.RefObject<HTMLDivElement | null>;
  filename?: string;
  className?: string;
}

export function ChartExport({ chartRef, filename = 'chart', className = '' }: ChartExportProps) {
  const [isExporting, setIsExporting] = useState(false);

  const exportAsPNG = async () => {
    setIsExporting(true);
    
    try {
      const svgElements = chartRef.current?.querySelectorAll('svg');
      if (!svgElements || svgElements.length === 0) {
        console.error('No SVG elements found in chart');
        setIsExporting(false);
        return;
      }

      let combinedSvg: SVGElement;
      let totalWidth = 0;
      let maxHeight = 0;

      // If there's only one SVG, use it directly
      if (svgElements.length === 1) {
        combinedSvg = svgElements[0].cloneNode(true) as SVGElement;
        const bbox = svgElements[0].getBoundingClientRect();
        totalWidth = bbox.width;
        maxHeight = bbox.height;
        
        // Add styles
        const styleElement = document.createElement('style');
        styleElement.textContent = `
          text { font-family: system-ui, -apple-system, sans-serif; }
          .tick text { font-size: 12px; fill: #666; }
          .domain { stroke: #ddd; }
          .tick line { stroke: #ddd; }
        `;
        combinedSvg.insertBefore(styleElement, combinedSvg.firstChild);
      } else {
        // Multiple SVGs - combine them vertically
        const svgData: { svg: SVGElement, width: number, height: number }[] = [];
        let maxWidth = 0;
        let totalHeight = 0;

        // Calculate dimensions and clone SVGs
        svgElements.forEach(svg => {
          const clone = svg.cloneNode(true) as SVGElement;
          const bbox = svg.getBoundingClientRect();
          svgData.push({ svg: clone, width: bbox.width, height: bbox.height });
          maxWidth = Math.max(maxWidth, bbox.width);
          totalHeight += bbox.height + 20; // Add padding between elements
        });

        // Create a combined SVG with vertical stacking
        combinedSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        combinedSvg.setAttribute('width', maxWidth.toString());
        combinedSvg.setAttribute('height', totalHeight.toString());
        combinedSvg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');

        // Add styles
        const styleElement = document.createElement('style');
        styleElement.textContent = `
          text { font-family: system-ui, -apple-system, sans-serif; }
          .tick text { font-size: 12px; fill: #666; }
          .domain { stroke: #ddd; }
          .tick line { stroke: #ddd; }
        `;
        combinedSvg.appendChild(styleElement);

        // Add each SVG as a group with vertical positioning
        let currentY = 0;
        svgData.forEach(({ svg, width, height }) => {
          const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
          // Center smaller elements horizontally
          const xOffset = (maxWidth - width) / 2;
          group.setAttribute('transform', `translate(${xOffset}, ${currentY})`);
          
          // Copy all children from the cloned SVG to the group
          while (svg.firstChild) {
            group.appendChild(svg.firstChild);
          }
          
          combinedSvg.appendChild(group);
          currentY += height + 20; // Add padding after each element
        });

        // Update dimensions for canvas
        totalWidth = maxWidth;
        maxHeight = totalHeight;
      }

      // Create a canvas
      const canvas = document.createElement('canvas');
      const scale = 2; // For better resolution
      canvas.width = totalWidth * scale;
      canvas.height = maxHeight * scale;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        setIsExporting(false);
        return;
      }

      // Scale for better resolution
      ctx.scale(scale, scale);

      // Set white background on the combined SVG
      combinedSvg.setAttribute('style', 'background-color: white;');

      const svgData = new XMLSerializer().serializeToString(combinedSvg);
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(svgBlob);

      const img = new Image();
      img.onload = () => {
        // Draw white background
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, totalWidth, maxHeight);
        
        // Draw the image
        ctx.drawImage(img, 0, 0, totalWidth, maxHeight);
        
        // Convert to blob and download
        canvas.toBlob((blob) => {
          if (blob) {
            saveAs(blob, `${filename}.png`);
          }
          URL.revokeObjectURL(url);
          setIsExporting(false);
        }, 'image/png');
      };

      img.onerror = (err) => {
        console.error('Error loading SVG:', err);
        setIsExporting(false);
        URL.revokeObjectURL(url);
      };

      img.src = url;
    } catch (error) {
      console.error('Error exporting chart:', error);
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={exportAsPNG}
      disabled={isExporting}
      className={`px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${className}`}
      title="Download as PNG"
    >
      {isExporting ? (
        <span className="flex items-center gap-1">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Exporting...
        </span>
      ) : (
        <span className="flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Export PNG
        </span>
      )}
    </button>
  );
}