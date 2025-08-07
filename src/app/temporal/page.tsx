'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

export default function TemporalRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the new environmental factors page after a short delay
    const timer = setTimeout(() => {
      router.replace('/environmental-factors');
    }, 3000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="page-container">
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center max-w-md">
          <ArrowPathIcon className="w-24 h-24 text-slate-400 mx-auto mb-6" />
          <h2 className="text-2xl font-semibold text-slate-700 mb-4">Page Reorganized</h2>
          <p className="text-slate-600 mb-6">
            Temporal analysis has been integrated into our <strong>Environmental Factors</strong> section, 
            focusing on seasonal patterns and environmental influences on acoustic indices.
          </p>
          <div className="space-y-3">
            <Link 
              href="/environmental-factors"
              className="inline-block bg-ocean-600 hover:bg-ocean-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Go to Environmental Analysis →
            </Link>
            <p className="text-sm text-slate-500">
              Automatically redirecting in 3 seconds...
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}