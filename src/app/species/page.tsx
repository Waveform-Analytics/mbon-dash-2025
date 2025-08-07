'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

export default function SpeciesRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the new acoustic biodiversity page after a short delay
    const timer = setTimeout(() => {
      router.replace('/acoustic-biodiversity');
    }, 3000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="page-container">
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center max-w-md">
          <ArrowPathIcon className="w-24 h-24 text-slate-400 mx-auto mb-6" />
          <h2 className="text-2xl font-semibold text-slate-700 mb-4">Page Moved</h2>
          <p className="text-slate-600 mb-6">
            Species analysis has been reorganized into our new <strong>Acoustic Analysis</strong> section, 
            focused on which acoustic indices best predict species presence.
          </p>
          <div className="space-y-3">
            <Link 
              href="/acoustic-biodiversity"
              className="inline-block bg-ocean-600 hover:bg-ocean-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Go to Acoustic Analysis →
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