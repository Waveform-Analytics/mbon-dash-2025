/**
 * Pagination controls component for navigating paginated datasets
 */

import React from 'react';

interface PaginationControlsProps {
  currentPage: number;
  totalPages: number;
  totalRecords: number;
  loading?: boolean;
  loadingPage?: number | null;
  onPageChange: (page: number) => void;
  onPreviousPage: () => void;
  onNextPage: () => void;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  className?: string;
}

export function PaginationControls({
  currentPage,
  totalPages,
  totalRecords,
  loading = false,
  loadingPage = null,
  onPageChange,
  onPreviousPage,
  onNextPage,
  hasNextPage,
  hasPreviousPage,
  className = ''
}: PaginationControlsProps) {
  
  // Generate page numbers to show
  const getVisiblePages = () => {
    const delta = 2; // Pages to show on each side of current page
    const range = [];
    const rangeWithDots = [];
    
    for (let i = Math.max(2, currentPage - delta); 
         i <= Math.min(totalPages - 1, currentPage + delta); 
         i++) {
      range.push(i);
    }
    
    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }
    
    rangeWithDots.push(...range);
    
    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages);
    }
    
    return rangeWithDots;
  };
  
  if (totalPages <= 1) {
    return (
      <div className={`flex items-center justify-center text-sm text-gray-600 ${className}`}>
        {totalRecords.toLocaleString()} records
      </div>
    );
  }
  
  const visiblePages = getVisiblePages();
  
  return (
    <div className={`flex items-center justify-between ${className}`}>
      {/* Records info */}
      <div className="text-sm text-gray-600">
        Page {currentPage.toLocaleString()} of {totalPages.toLocaleString()} 
        <span className="hidden sm:inline"> • {totalRecords.toLocaleString()} total records</span>
      </div>
      
      {/* Navigation controls */}
      <div className="flex items-center space-x-1">
        {/* Previous button */}
        <button
          onClick={onPreviousPage}
          disabled={!hasPreviousPage || loading}
          className={`
            px-3 py-2 text-sm font-medium rounded-md border transition-colors
            ${!hasPreviousPage || loading
              ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:text-blue-600'
            }
          `}
        >
          ← Previous
        </button>
        
        {/* Page numbers */}
        <div className="hidden sm:flex items-center space-x-1">
          {visiblePages.map((page, index) => {
            if (page === '...') {
              return (
                <span key={`dots-${index}`} className="px-3 py-2 text-gray-400">
                  ...
                </span>
              );
            }
            
            const pageNum = page as number;
            const isCurrent = pageNum === currentPage;
            const isLoading = loadingPage === pageNum;
            
            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum)}
                disabled={loading || isLoading}
                className={`
                  px-3 py-2 text-sm font-medium rounded-md border transition-colors min-w-[2.5rem]
                  ${isCurrent
                    ? 'bg-blue-600 text-white border-blue-600'
                    : loading || isLoading
                      ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:text-blue-600'
                  }
                  ${isLoading ? 'animate-pulse' : ''}
                `}
              >
                {isLoading ? '...' : pageNum}
              </button>
            );
          })}
        </div>
        
        {/* Mobile page input */}
        <div className="sm:hidden flex items-center space-x-2">
          <input
            type="number"
            min={1}
            max={totalPages}
            value={currentPage}
            onChange={(e) => {
              const page = parseInt(e.target.value, 10);
              if (page >= 1 && page <= totalPages) {
                onPageChange(page);
              }
            }}
            disabled={loading}
            className="w-16 px-2 py-1 text-sm border border-gray-300 rounded text-center"
          />
          <span className="text-sm text-gray-500">of {totalPages}</span>
        </div>
        
        {/* Next button */}
        <button
          onClick={onNextPage}
          disabled={!hasNextPage || loading}
          className={`
            px-3 py-2 text-sm font-medium rounded-md border transition-colors
            ${!hasNextPage || loading
              ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50 hover:text-blue-600'
            }
          `}
        >
          Next →
        </button>
      </div>
      
      {/* Loading indicator */}
      {loading && (
        <div className="flex items-center space-x-2 text-sm text-blue-600">
          <div className="animate-spin h-4 w-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
          <span>Loading...</span>
        </div>
      )}
    </div>
  );
}

/**
 * Compact pagination controls for smaller spaces
 */
export function CompactPaginationControls({
  currentPage,
  totalPages,
  totalRecords,
  loading = false,
  onPageChange,
  onPreviousPage,
  onNextPage,
  hasNextPage,
  hasPreviousPage,
  className = ''
}: PaginationControlsProps) {
  
  if (totalPages <= 1) {
    return (
      <div className={`text-xs text-gray-500 ${className}`}>
        {totalRecords.toLocaleString()} records
      </div>
    );
  }
  
  return (
    <div className={`flex items-center justify-between text-sm ${className}`}>
      <button
        onClick={onPreviousPage}
        disabled={!hasPreviousPage || loading}
        className={`
          px-2 py-1 text-xs font-medium rounded border transition-colors
          ${!hasPreviousPage || loading
            ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
            : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
          }
        `}
      >
        ←
      </button>
      
      <div className="flex items-center space-x-2">
        <input
          type="number"
          min={1}
          max={totalPages}
          value={currentPage}
          onChange={(e) => {
            const page = parseInt(e.target.value, 10);
            if (page >= 1 && page <= totalPages) {
              onPageChange(page);
            }
          }}
          disabled={loading}
          className="w-12 px-1 py-1 text-xs border border-gray-300 rounded text-center"
        />
        <span className="text-xs text-gray-500">/ {totalPages}</span>
      </div>
      
      <button
        onClick={onNextPage}
        disabled={!hasNextPage || loading}
        className={`
          px-2 py-1 text-xs font-medium rounded border transition-colors
          ${!hasNextPage || loading
            ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
            : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
          }
        `}
      >
        →
      </button>
    </div>
  );
}