import { Metadata } from 'next'
import { Suspense } from 'react'
import Link from 'next/link'
import ModelingAnalysis from '@/components/analysis/ModelingAnalysis'

export const metadata: Metadata = {
  title: 'Predictive Models - MBON Marine Biodiversity Dashboard',
  description: 'Machine learning models predicting marine biodiversity from acoustic indices using temporal stratification methodology.',
  keywords: 'marine biodiversity, acoustic indices, machine learning, temporal stratification, fish detection, predictive modeling'
}

export default function ModelsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-teal-800 text-white">
        <div className="container mx-auto px-4 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Building Predictions
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8">
              Machine learning models to predict marine biodiversity from acoustic patterns
            </p>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 mb-8">
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div>
                  <div className="text-3xl font-bold text-yellow-300">F1 = 0.62</div>
                  <div className="text-sm text-blue-200">Best Model Performance</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-green-300">12 Months</div>
                  <div className="text-sm text-blue-200">Full Year Training</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-orange-300">2 Stations</div>
                  <div className="text-sm text-blue-200">8,672 Records</div>
                </div>
              </div>
            </div>
            <p className="text-lg text-blue-100">
              Step 3 of 4 in the Analysis Journey → 
              <span className="text-yellow-300 font-semibold ml-2">
                Can acoustic indices predict fish presence across seasons?
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Breadcrumbs */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center space-x-2 text-sm">
            <Link href="/" className="text-blue-600 hover:text-blue-800">Home</Link>
            <span className="text-gray-400">/</span>
            <Link href="/analysis" className="text-blue-600 hover:text-blue-800">Analysis</Link>
            <span className="text-gray-400">/</span>
            <span className="text-gray-900 font-semibold">Building Predictions</span>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Suspense fallback={
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-4 text-lg text-gray-600">Loading modeling analysis...</span>
          </div>
        }>
          <ModelingAnalysis />
        </Suspense>

        {/* Navigation */}
        <div className="mt-16 pt-8 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <a 
              href="/analysis/patterns"
              className="flex items-center space-x-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-gray-700"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Previous: Finding Patterns</span>
            </a>
            
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">Step 3 of 4</div>
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
              </div>
            </div>

            <a 
              href="/analysis/validation"
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <span>Next: Validation</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </a>
          </div>
        </div>
      </main>
    </div>
  )
}