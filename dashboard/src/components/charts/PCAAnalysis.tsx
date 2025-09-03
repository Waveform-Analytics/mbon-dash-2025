import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { PCAAnalysisData } from '../../lib/data/usePCAAnalysis';
import { PCAScreePlot } from './PCAScreePlot';
import { PCALoadingsHeatmap } from './PCALoadingsHeatmap';

interface PCAAnalysisProps {
  data: PCAAnalysisData;
}

export function PCAAnalysis({ data }: PCAAnalysisProps) {
  // Validate and sanitize summary data
  const safeValue = (value: any, fallback: number = 0): number => {
    return typeof value === 'number' && !isNaN(value) && isFinite(value) ? value : fallback;
  };

  const safeSummary = {
    total_indices: safeValue(data.summary.total_indices),
    components_for_80_percent: safeValue(data.summary.components_for_80_percent),
    components_for_90_percent: safeValue(data.summary.components_for_90_percent),
    variance_explained_top_5: safeValue(data.summary.variance_explained_top_5)
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 mb-1">
                {safeSummary.total_indices}
              </div>
              <div className="text-sm text-muted-foreground">Original indices</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 mb-1">
                {safeSummary.components_for_80_percent}
              </div>
              <div className="text-sm text-muted-foreground">Components for 80% variance</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 mb-1">
                {safeSummary.components_for_90_percent}
              </div>
              <div className="text-sm text-muted-foreground">Components for 90% variance</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600 mb-1">
                {Math.round(safeSummary.variance_explained_top_5)}%
              </div>
              <div className="text-sm text-muted-foreground">Top 5 components variance</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabbed Analysis */}
      <Tabs defaultValue="scree" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="scree">Scree Plot</TabsTrigger>
          <TabsTrigger value="loadings">Component Loadings</TabsTrigger>
          <TabsTrigger value="interpretation">Interpretation</TabsTrigger>
        </TabsList>
        
        <TabsContent value="scree" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Variance Explained by Principal Components</CardTitle>
              <p className="text-sm text-muted-foreground">
                The scree plot shows how much variance each principal component explains. 
                Components with higher explained variance capture more acoustic variation.
              </p>
            </CardHeader>
            <CardContent>
              <PCAScreePlot data={data.scree_plot} />
              
              <div className="mt-6 bg-muted/50 rounded-lg p-4">
                <div className="text-sm text-muted-foreground mb-2">
                  <strong>Key Finding:</strong> The first {data.summary.components_for_80_percent} principal component{data.summary.components_for_80_percent === 1 ? '' : 's'} capture{data.summary.components_for_80_percent === 1 ? 's' : ''} 80% of the acoustic variation, 
                  reducing dimensionality from {data.summary.total_indices} indices to just {data.summary.components_for_80_percent} component{data.summary.components_for_80_percent === 1 ? '' : 's'}.
                </div>
                {data.summary.components_for_80_percent < 5 && (
                  <div className="text-sm text-green-700 bg-green-50 p-3 rounded mt-2">
                    💡 This suggests strong redundancy among acoustic indices - most information can be captured in very few dimensions.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="loadings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Principal Component Loadings</CardTitle>
              <p className="text-sm text-muted-foreground">
                Loadings show how much each acoustic index contributes to each principal component. 
                Darker colors indicate stronger contributions (positive in blue, negative in red).
              </p>
            </CardHeader>
            <CardContent>
              <PCALoadingsHeatmap 
                data={data.loadings_heatmap.data}
                indices={data.loadings_heatmap.indices}
                components={data.loadings_heatmap.components}
              />
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="interpretation" className="space-y-4">
          <div className="grid gap-4">
            {Object.entries(data.component_interpretation).map(([component, interpretation]) => (
              <Card key={component}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{component}</span>
                    <span className="text-sm font-normal text-muted-foreground">
                      {interpretation.explained_variance_percent.toFixed(1)}% variance explained
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    {interpretation.interpretation}
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-sm mb-2 text-green-800">Top Positive Contributors</h4>
                      <div className="space-y-1">
                        {interpretation.top_positive_loadings.map((index, i) => (
                          <div key={index} className="text-sm bg-green-50 px-2 py-1 rounded">
                            {i + 1}. {index}
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm mb-2 text-red-800">Top Negative Contributors</h4>
                      <div className="space-y-1">
                        {interpretation.top_negative_loadings.map((index, i) => (
                          <div key={index} className="text-sm bg-red-50 px-2 py-1 rounded">
                            {i + 1}. {index}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}