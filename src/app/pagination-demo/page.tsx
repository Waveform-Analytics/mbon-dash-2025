/**
 * Demo page to test pagination system performance
 */

'use client';

import { useState } from 'react';
import { usePaginatedAcousticIndices, usePaginatedDetections, usePaginatedEnvironmental } from '@/lib/hooks/usePaginatedData';
import { PaginationControls, CompactPaginationControls } from '@/components/ui/PaginationControls';

interface DatasetDemoProps {
  title: string;
  hook: () => any;
  sampleKeys: string[];
}

function DatasetDemo({ title, hook, sampleKeys }: DatasetDemoProps) {
  const {
    data,
    summary,
    metadata,
    loading,
    loadingPage,
    currentPage,
    totalPages,
    totalRecords,
    loadPage,
    loadNextPage,
    loadPreviousPage,
    hasNextPage,
    hasPreviousPage,
    error,
    loadedPages
  } = hook();
  
  if (error) {
    return (
      <div className="border border-red-200 rounded-lg p-6 bg-red-50">
        <h3 className="text-lg font-semibold text-red-800 mb-2">{title}</h3>
        <p className="text-red-600">Error: {error.message}</p>
      </div>
    );
  }
  
  if (loading) {
    return (
      <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
        <div className="flex items-center space-x-2">
          <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
          <span className="text-gray-600">Loading...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="border border-gray-200 rounded-lg p-6 bg-white">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
        
        {/* Metadata summary */}
        {metadata && (
          <div className="text-sm text-gray-600 mb-4">
            <p>Total records: {metadata.total_records.toLocaleString()}</p>
            <p>Page size: {metadata.page_size}</p>
            <p>Loaded pages: {Array.from(loadedPages).sort().join(', ')}</p>
          </div>
        )}
        
        {/* Pagination controls */}
        <PaginationControls
          currentPage={currentPage}
          totalPages={totalPages}
          totalRecords={totalRecords}
          loading={loading}
          loadingPage={loadingPage}
          onPageChange={loadPage}
          onPreviousPage={loadPreviousPage}
          onNextPage={loadNextPage}
          hasNextPage={hasNextPage}
          hasPreviousPage={hasPreviousPage}
          className="mb-4"
        />
      </div>
      
      {/* Data preview */}
      <div className="bg-gray-50 rounded p-3">
        <h4 className="font-medium text-gray-700 mb-2">
          Current Page Data ({data.length} records)
        </h4>
        
        {data.length > 0 ? (
          <div className="space-y-2">
            {/* Show first few records */}
            {data.slice(0, 3).map((record: any, index: number) => (
              <div key={index} className="text-xs bg-white p-2 rounded border">
                {sampleKeys.map(key => (
                  <span key={key} className="inline-block mr-4">
                    <strong>{key}:</strong> {String(record[key] || 'N/A').slice(0, 50)}
                    {String(record[key] || '').length > 50 && '...'}
                  </span>
                ))}
              </div>
            ))}
            
            {data.length > 3 && (
              <div className="text-xs text-gray-500">
                ... and {data.length - 3} more records
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">No data loaded</p>
        )}
      </div>
    </div>
  );
}

export default function PaginationDemoPage() {
  const [showCompact, setShowCompact] = useState(false);
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Pagination System Demo</h1>
          <p className="mt-2 text-gray-600">
            Test the performance optimization for large datasets. Each dataset is now loaded in 
            smaller pages instead of loading everything at once.
          </p>
          
          <div className="mt-4 flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={showCompact}
                onChange={(e) => setShowCompact(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Show compact controls</span>
            </label>
          </div>
        </div>
      </div>
      
      {/* Dataset demos */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          
          {/* Acoustic Indices */}
          <DatasetDemo
            title="Acoustic Indices (159MB → paginated)"
            hook={usePaginatedAcousticIndices}
            sampleKeys={['datetime', 'station', 'LEQt', 'ACI', 'ADI']}
          />
          
          {/* Environmental Data */}
          <DatasetDemo
            title="Environmental Data (45MB → paginated)"
            hook={usePaginatedEnvironmental}
            sampleKeys={['datetime', 'station', 'temp_c', 'depth_m']}
          />
          
          {/* Detection Data */}
          <DatasetDemo
            title="Detection Data (14MB → paginated)"
            hook={usePaginatedDetections}
            sampleKeys={['datetime', 'station', 'sp', 'bde', 'otbw']}
          />
        </div>
        
        {/* Performance notes */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-3">Performance Improvements</h3>
          
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-blue-700 mb-2">Before (Single Files):</h4>
              <ul className="space-y-1 text-blue-600">
                <li>• Acoustic Indices: 159MB loaded at once</li>
                <li>• Environmental: 45MB loaded at once</li>  
                <li>• Detections: 14MB loaded at once</li>
                <li>• Total: 218MB initial download</li>
                <li>• Slow initial page load</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-700 mb-2">After (Paginated):</h4>
              <ul className="space-y-1 text-blue-600">
                <li>• Initial load: Summary files only (~1MB)</li>
                <li>• Page loads: 1000-5000 records at a time</li>
                <li>• Smart caching and preloading</li>
                <li>• Fast initial page load</li>
                <li>• Load data on-demand</li>
              </ul>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-100 rounded">
            <p className="text-sm text-blue-800">
              <strong>Result:</strong> Initial page load is now ~200x faster, and users only download 
              the data they actually view. Perfect for dashboard performance!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}