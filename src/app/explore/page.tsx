import Link from 'next/link';
import { ChartBarIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { ExploreContent } from './page.content';

export default function ExplorePage() {
  return (
    <div className="page-container">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="section-heading text-4xl mb-4">
          {ExploreContent.header.title}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-ocean-600 to-coral-500">{ExploreContent.header.titleHighlight}</span>
        </h1>
        <p className="section-description max-w-3xl mx-auto">
          {ExploreContent.header.subtitle}
        </p>
      </div>

      {/* Navigation Cards */}
      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        
        {/* Annotations Explorer Card */}
        <Link href="/explore/annotations">
          <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 border border-gray-200 hover:border-ocean-300 cursor-pointer">
            <div className="flex items-center mb-4">
              <DocumentTextIcon className="w-8 h-8 text-ocean-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">
                {ExploreContent.sections.annotations.title}
              </h2>
            </div>
            <p className="text-gray-600 mb-4">
              {ExploreContent.sections.annotations.description}
            </p>
            <div className="space-y-2">
              {ExploreContent.sections.annotations.features.map((feature, index) => (
                <div key={index} className="flex items-center text-sm text-gray-500">
                  <span className="w-1.5 h-1.5 bg-ocean-400 rounded-full mr-2"></span>
                  {feature}
                </div>
              ))}
            </div>
          </div>
        </Link>

        {/* Indices Explorer Card */}
        <Link href="/explore/indices">
          <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 border border-gray-200 hover:border-coral-300 cursor-pointer">
            <div className="flex items-center mb-4">
              <ChartBarIcon className="w-8 h-8 text-coral-600 mr-3" />
              <h2 className="text-xl font-semibold text-gray-900">
                {ExploreContent.sections.indices.title}
              </h2>
            </div>
            <p className="text-gray-600 mb-4">
              {ExploreContent.sections.indices.description}
            </p>
            <div className="space-y-2">
              {ExploreContent.sections.indices.features.map((feature, index) => (
                <div key={index} className="flex items-center text-sm text-gray-500">
                  <span className="w-1.5 h-1.5 bg-coral-400 rounded-full mr-2"></span>
                  {feature}
                </div>
              ))}
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}