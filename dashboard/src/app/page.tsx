'use client';

import { useViewData } from '@/lib/data/useViewData';
import { ProjectMetadata, StationsData, DatasetsData } from '@/types/data';

export default function Home() {
  const { data: projectData, loading: projectLoading } = useViewData<ProjectMetadata>('project_metadata.json');
  const { data: stationsData, loading: stationsLoading } = useViewData<StationsData>('stations.json');
  const { data: datasetsData, loading: datasetsLoading } = useViewData<DatasetsData>('datasets_summary.json');

  const loading = projectLoading || stationsLoading || datasetsLoading;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="container mx-auto px-4 py-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {projectData?.project.title || 'MBON Marine Biodiversity Dashboard'}
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-8">
            {projectData?.project.subtitle || 'Exploring Acoustic Indices as Marine Biodiversity Predictors'}
          </p>
          <div className="flex flex-wrap gap-4">
            <div className="bg-white/10 backdrop-blur rounded-lg px-4 py-2">
              <span className="text-blue-200 text-sm">Stations</span>
              <p className="text-2xl font-bold">{stationsData?.summary.total_stations || 0}</p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg px-4 py-2">
              <span className="text-blue-200 text-sm">Years</span>
              <p className="text-2xl font-bold">
                {stationsData?.summary.years_covered.join(', ') || 'N/A'}
              </p>
            </div>
            <div className="bg-white/10 backdrop-blur rounded-lg px-4 py-2">
              <span className="text-blue-200 text-sm">Total Records</span>
              <p className="text-2xl font-bold">
                {datasetsData?.summary.total_records.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Research Context */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Research Context</h2>
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <p className="text-lg text-gray-700 mb-4">
              {projectData?.research_context.primary_question}
            </p>
            <p className="text-gray-600">
              {projectData?.research_context.significance}
            </p>
          </div>

          {/* Research Objectives */}
          <h3 className="text-2xl font-semibold text-gray-800 mb-4">Research Objectives</h3>
          <div className="grid gap-4 mb-12">
            {projectData?.research_context.objectives.map((objective) => (
              <div key={objective.id} className="bg-white rounded-lg shadow p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">{objective.title}</h4>
                    <p className="text-gray-600 mt-1">{objective.description}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ml-4 ${
                    objective.status === 'in_progress' 
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {objective.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* Dataset Summary */}
          <h2 className="text-3xl font-bold text-gray-800 mb-6">Available Datasets</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {datasetsData?.datasets.map((dataset) => (
              <div key={dataset.id} className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  {dataset.name}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {dataset.description}
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Records:</span>
                    <span className="font-medium">{dataset.record_count.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Resolution:</span>
                    <span className="font-medium">{dataset.temporal_resolution}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Type:</span>
                    <span className="font-medium">{dataset.data_type.replace('_', ' ')}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Station Information */}
          <h2 className="text-3xl font-bold text-gray-800 mb-6 mt-12">Monitoring Stations</h2>
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="grid md:grid-cols-3 gap-6">
              {stationsData?.stations.map((station) => (
                <div key={station.id} className="border rounded-lg p-4">
                  <h3 className="font-semibold text-lg text-gray-800">{station.name}</h3>
                  <div className="mt-2 space-y-1 text-sm text-gray-600">
                    <p>Platform: {station.platform}</p>
                    <p>Depth: {station.depth_m ? `${Math.abs(station.depth_m).toFixed(1)}m` : 'N/A'}</p>
                    <p>Deployments: {station.deployment_periods.length}</p>
                    <div className="mt-2 flex gap-2">
                      {station.data_availability.detection_data && (
                        <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                          Detections
                        </span>
                      )}
                      {station.data_availability.acoustic_indices && (
                        <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                          Indices
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-100 mt-12">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-gray-600">
            <p>{projectData?.project.organization}</p>
            <p className="text-sm mt-2">
              Data generated: {new Date(projectData?.metadata.generated_at || '').toLocaleDateString()}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}