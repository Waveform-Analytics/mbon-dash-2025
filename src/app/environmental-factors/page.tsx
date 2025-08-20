'use client';

export default function EnvironmentalFactorsPage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          Environmental
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500"> Confounders</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          Analysis of potential relationships between acoustic indices and environmental factors like temperature and depth.
        </p>
      </div>

    </div>
  );
}