'use client'

import { StationMap } from '@/components/maps/StationMap';
import type { ProcessedStation } from '@/app/page';

interface StationMapWrapperProps {
  stations: ProcessedStation[];
}

export default function StationMapWrapper({ stations }: StationMapWrapperProps) {
  if (stations.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 rounded-b-lg p-6">
        <div className="text-center">
          <div className="text-slate-500 font-medium">No station data available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[400px] w-full rounded-b-xl overflow-hidden">
      <StationMap stations={stations} />
    </div>
  );
}