/**
 * Loading State Components
 * Reusable loading indicators and skeletons
 */

'use client';

import React from 'react';

/**
 * Spinner Loading Indicator
 */
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  };

  return (
    <div className="flex justify-center">
      <div
        className={`${sizeClasses[size]} border-slate-200 border-t-blue-600 rounded-full animate-spin`}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
}

/**
 * Full Page Loading
 */
export function PageLoading({ message = 'Loading data...' }: { message?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50">
      <div className="text-center">
        <Spinner size="lg" />
        <p className="mt-4 text-slate-600">{message}</p>
      </div>
    </div>
  );
}

/**
 * Chart Loading Skeleton
 */
export function ChartSkeleton({ height = 400 }: { height?: number }) {
  return (
    <div
      className="bg-slate-100 rounded-lg animate-pulse"
      style={{ height: `${height}px` }}
    >
      <div className="h-full flex items-end justify-around p-4">
        {[40, 70, 50, 80, 60, 90, 45].map((h, i) => (
          <div
            key={i}
            className="bg-slate-200 rounded"
            style={{
              width: '10%',
              height: `${h}%`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Table Loading Skeleton
 */
export function TableSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200">
      {/* Header */}
      <div className="bg-slate-50 border-b border-slate-200 p-4">
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, i) => (
            <div key={i} className="h-4 bg-slate-200 rounded animate-pulse" />
          ))}
        </div>
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={rowIndex}
          className="border-b border-slate-100 p-4 last:border-b-0"
        >
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, colIndex) => (
              <div
                key={colIndex}
                className="h-4 bg-slate-100 rounded animate-pulse"
                style={{
                  animationDelay: `${(rowIndex * columns + colIndex) * 50}ms`,
                }}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Card Loading Skeleton
 */
export function CardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 animate-pulse">
      <div className="h-4 bg-slate-200 rounded w-3/4 mb-4" />
      <div className="space-y-3">
        <div className="h-3 bg-slate-100 rounded" />
        <div className="h-3 bg-slate-100 rounded w-5/6" />
        <div className="h-3 bg-slate-100 rounded w-4/6" />
      </div>
      <div className="mt-6 flex gap-2">
        <div className="h-8 bg-slate-200 rounded flex-1" />
        <div className="h-8 bg-slate-200 rounded flex-1" />
      </div>
    </div>
  );
}

/**
 * Data Grid Loading
 */
export function DataGridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}

/**
 * Loading Overlay
 * Shows loading spinner over existing content
 */
export function LoadingOverlay({ visible = true }: { visible?: boolean }) {
  if (!visible) return null;

  return (
    <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50 rounded-lg">
      <div className="text-center">
        <Spinner size="lg" />
        <p className="mt-2 text-sm text-slate-600">Updating...</p>
      </div>
    </div>
  );
}

/**
 * Inline Loading
 * Small loading indicator for inline content
 */
export function InlineLoading({ text = 'Loading' }: { text?: string }) {
  return (
    <span className="inline-flex items-center text-sm text-slate-600">
      <svg
        className="animate-spin -ml-1 mr-2 h-4 w-4 text-slate-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {text}...
    </span>
  );
}