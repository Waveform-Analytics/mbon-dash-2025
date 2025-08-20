'use client';

// Icons removed since text sections were removed
import { AcousticBiodiversityContent } from './page.content';
// Charts will be moved to explore pages for detailed analysis

export default function AcousticBiodiversityPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          {AcousticBiodiversityContent.header.title}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500">{AcousticBiodiversityContent.header.titleHighlight}</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          {AcousticBiodiversityContent.header.subtitle}
        </p>
      </div>

      {/* Placeholder for methodological content */}
      <div className="mb-12">
        <div className="bg-blue-50 p-6 rounded-lg">
          <h2 className="text-2xl font-bold text-blue-800 mb-3">
            Acoustic Indices Analysis Framework
          </h2>
          <p className="text-blue-700 max-w-4xl">
            This page will present our systematic approach to identifying which acoustic indices 
            best predict marine soundscape biodiversity. The analysis workflow and visualizations 
            are being developed in the <strong>Explore → Acoustic Indices</strong> section.
          </p>
        </div>
      </div>

    </div>
  );
}