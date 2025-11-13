'use client';

import React, { useState } from 'react';
import { DimensionalityPlot } from '@/components/visualization';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function DimensionalityReductionExample() {
  const [activeDataset, setActiveDataset] = useState<'iris' | 'random' | 'custom'>('iris');

  // Generate sample Iris dataset (simplified)
  const generateIrisData = () => {
    // Simplified Iris dataset with 4 features
    const data = [
      // Setosa (class 0)
      [5.1, 3.5, 1.4, 0.2], [4.9, 3.0, 1.4, 0.2], [4.7, 3.2, 1.3, 0.2],
      [4.6, 3.1, 1.5, 0.2], [5.0, 3.6, 1.4, 0.2], [5.4, 3.9, 1.7, 0.4],
      [4.6, 3.4, 1.4, 0.3], [5.0, 3.4, 1.5, 0.2], [4.4, 2.9, 1.4, 0.2],
      [4.9, 3.1, 1.5, 0.1], [5.4, 3.7, 1.5, 0.2], [4.8, 3.4, 1.6, 0.2],
      [4.8, 3.0, 1.4, 0.1], [4.3, 3.0, 1.1, 0.1], [5.8, 4.0, 1.2, 0.2],
      // Versicolor (class 1)
      [7.0, 3.2, 4.7, 1.4], [6.4, 3.2, 4.5, 1.5], [6.9, 3.1, 4.9, 1.5],
      [5.5, 2.3, 4.0, 1.3], [6.5, 2.8, 4.6, 1.5], [5.7, 2.8, 4.5, 1.3],
      [6.3, 3.3, 4.7, 1.6], [4.9, 2.4, 3.3, 1.0], [6.6, 2.9, 4.6, 1.3],
      [5.2, 2.7, 3.9, 1.4], [5.0, 2.0, 3.5, 1.0], [5.9, 3.0, 4.2, 1.5],
      [6.0, 2.2, 4.0, 1.0], [6.1, 2.9, 4.7, 1.4], [5.6, 2.9, 3.6, 1.3],
      // Virginica (class 2)
      [6.3, 3.3, 6.0, 2.5], [5.8, 2.7, 5.1, 1.9], [7.1, 3.0, 5.9, 2.1],
      [6.3, 2.9, 5.6, 1.8], [6.5, 3.0, 5.8, 2.2], [7.6, 3.0, 6.6, 2.1],
      [4.9, 2.5, 4.5, 1.7], [7.3, 2.9, 6.3, 1.8], [6.7, 2.5, 5.8, 1.8],
      [7.2, 3.6, 6.1, 2.5], [6.5, 3.2, 5.1, 2.0], [6.4, 2.7, 5.3, 1.9],
      [6.8, 3.0, 5.5, 2.1], [5.7, 2.5, 5.0, 2.0], [5.8, 2.8, 5.1, 2.4]
    ];
    
    const metadata = [
      ...Array(15).fill('Setosa'),
      ...Array(15).fill('Versicolor'),
      ...Array(15).fill('Virginica')
    ];
    
    return { data, metadata };
  };

  // Generate random high-dimensional data
  const generateRandomData = () => {
    const nSamples = 100;
    const nFeatures = 50;
    const nClusters = 3;
    
    const data: number[][] = [];
    const metadata: string[] = [];
    
    for (let cluster = 0; cluster < nClusters; cluster++) {
      const clusterCenter = Array(nFeatures).fill(0).map(() => Math.random() * 10);
      
      for (let i = 0; i < nSamples / nClusters; i++) {
        const sample = clusterCenter.map(center => center + (Math.random() - 0.5) * 2);
        data.push(sample);
        metadata.push(`Cluster ${cluster + 1}`);
      }
    }
    
    return { data, metadata };
  };

  // Get current dataset
  const getCurrentData = () => {
    switch (activeDataset) {
      case 'iris':
        return generateIrisData();
      case 'random':
        return generateRandomData();
      default:
        return { data: [], metadata: [] };
    }
  };

  const { data, metadata } = getCurrentData();

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Dimensionality Reduction Visualization</h1>
        <p className="text-muted-foreground">
          Explore high-dimensional data in 3D using PCA, t-SNE, and UMAP algorithms
        </p>
      </div>

      <Tabs value={activeDataset} onValueChange={(v) => setActiveDataset(v as any)}>
        <TabsList>
          <TabsTrigger value="iris">Iris Dataset</TabsTrigger>
          <TabsTrigger value="random">Random Clusters</TabsTrigger>
        </TabsList>

        <TabsContent value="iris" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Iris Dataset</CardTitle>
              <CardDescription>
                Classic dataset with 3 species of iris flowers, each with 4 measurements
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p><strong>Samples:</strong> 45 (15 per species)</p>
                <p><strong>Features:</strong> 4 (sepal length, sepal width, petal length, petal width)</p>
                <p><strong>Classes:</strong> Setosa, Versicolor, Virginica</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="random" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Random Clustered Data</CardTitle>
              <CardDescription>
                Synthetic high-dimensional data with 3 distinct clusters
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p><strong>Samples:</strong> 100</p>
                <p><strong>Features:</strong> 50</p>
                <p><strong>Clusters:</strong> 3</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <DimensionalityPlot
        data={data}
        metadata={metadata}
        metadataName="Species"
        method="pca"
        autoCompute={false}
      />

      <Card>
        <CardHeader>
          <CardTitle>About the Methods</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">PCA (Principal Component Analysis)</h3>
            <p className="text-sm text-muted-foreground">
              Linear dimensionality reduction that finds orthogonal axes of maximum variance.
              Fast and deterministic, best for linearly separable data. Shows percentage of variance explained.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">t-SNE (t-Distributed Stochastic Neighbor Embedding)</h3>
            <p className="text-sm text-muted-foreground">
              Non-linear method that preserves local structure. Excellent for visualizing clusters.
              Perplexity parameter controls the balance between local and global structure (5-50).
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">UMAP (Uniform Manifold Approximation and Projection)</h3>
            <p className="text-sm text-muted-foreground">
              Modern non-linear method that preserves both local and global structure better than t-SNE.
              Generally faster and more scalable. N_neighbors parameter controls local vs global structure (2-100).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
