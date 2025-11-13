'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Info } from 'lucide-react';
import { ProteinViewer } from '@/components/visualization/protein-viewer';
import { NetworkGraph3D } from '@/components/visualization/network-graph-3d';
import { DimensionalityPlot } from '@/components/visualization/dimensionality-plot';
import { VRViewer } from '@/components/visualization/vr-viewer';

// Sample data for demonstrations
const sampleNetworkData = {
  nodes: [
    { id: '1', label: 'Gene A', type: 'gene' },
    { id: '2', label: 'Gene B', type: 'gene' },
    { id: '3', label: 'Protein X', type: 'protein' },
    { id: '4', label: 'Protein Y', type: 'protein' },
    { id: '5', label: 'Metabolite M', type: 'metabolite' },
  ],
  edges: [
    { source: '1', target: '3', weight: 0.8 },
    { source: '2', target: '4', weight: 0.9 },
    { source: '3', target: '5', weight: 0.7 },
    { source: '4', target: '5', weight: 0.6 },
    { source: '1', target: '2', weight: 0.5 },
  ]
};

const sampleDimensionalityData = Array.from({ length: 100 }, (_, i) => {
  const angle = (i / 100) * 2 * Math.PI;
  const radius = 1 + Math.random() * 0.5;
  return [
    radius * Math.cos(angle) + Math.random() * 0.2,
    radius * Math.sin(angle) + Math.random() * 0.2,
    Math.random() * 0.5,
    Math.random() * 0.5,
    Math.random() * 0.5,
  ];
});

const sampleMetadata = Array.from({ length: 100 }, (_, i) => 
  i < 50 ? 'Group A' : 'Group B'
);

export default function ExportDemoPage() {
  const [activeTab, setActiveTab] = useState('protein');

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold">Visualization Export Demo</h1>
        <p className="text-muted-foreground">
          Demonstration of export functionality for all visualization components
        </p>
      </div>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          Each visualization below includes an export dropdown menu with options for PNG, SVG, and Interactive HTML formats.
          Try exporting in different formats to see the results!
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>Export Formats</CardTitle>
          <CardDescription>
            All visualizations support three export formats
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">PNG - High-resolution raster images</Badge>
            <Badge variant="default">SVG - Scalable vector graphics</Badge>
            <Badge variant="default">HTML - Interactive standalone files</Badge>
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="protein">Protein Viewer</TabsTrigger>
          <TabsTrigger value="network">Network Graph</TabsTrigger>
          <TabsTrigger value="dimensionality">Dimensionality Plot</TabsTrigger>
          <TabsTrigger value="vr">VR Viewer</TabsTrigger>
        </TabsList>

        <TabsContent value="protein" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Protein Structure Export</CardTitle>
              <CardDescription>
                Export 3D protein structures in multiple formats. The interactive HTML export includes
                the full NGL viewer with all controls.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ProteinViewer pdbId="1CRN" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Export Features</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li><strong>PNG:</strong> 2x resolution snapshot of current view with selected representation and colors</li>
                <li><strong>SVG:</strong> Vector format with embedded raster image for scalability</li>
                <li><strong>HTML:</strong> Standalone NGL viewer with full interactivity, rotation, zoom, and representation controls</li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>3D Network Graph Export</CardTitle>
              <CardDescription>
                Export force-directed network graphs. The HTML export includes the full 3D force graph
                with node interactions and physics simulation.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <NetworkGraph3D 
                nodes={sampleNetworkData.nodes}
                edges={sampleNetworkData.edges}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Export Features</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li><strong>PNG:</strong> High-resolution snapshot (2x scale) of the current graph layout</li>
                <li><strong>SVG:</strong> Vector snapshot preserving the current view</li>
                <li><strong>HTML:</strong> Interactive 3D force graph with Three.js, including zoom, rotation, and node selection</li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dimensionality" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Dimensionality Reduction Export</CardTitle>
              <CardDescription>
                Export PCA, t-SNE, or UMAP visualizations. The HTML export includes the full Plotly
                chart with all interactive features.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DimensionalityPlot 
                data={sampleDimensionalityData}
                metadata={sampleMetadata}
                metadataName="Group"
                method="pca"
                autoCompute
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Export Features</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li><strong>PNG:</strong> 1920x1080 high-resolution image suitable for presentations</li>
                <li><strong>SVG:</strong> Vector format ideal for publications and print</li>
                <li><strong>HTML:</strong> Full Plotly interactivity with zoom, pan, rotate, and hover tooltips</li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vr" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>VR Scene Export</CardTitle>
              <CardDescription>
                Export WebXR-enabled VR scenes. The HTML export includes VR support with a button
                to enter immersive mode on compatible devices.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <VRViewer enableControllers enableTeleportation />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Export Features</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2 text-sm">
                <li><strong>PNG:</strong> Snapshot of the current 3D scene view</li>
                <li><strong>SVG:</strong> Vector snapshot of the scene</li>
                <li><strong>HTML:</strong> WebXR-enabled scene with VR button, desktop fallback, and full scene controls</li>
              </ul>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Usage Instructions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">How to Export:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm">
              <li>Wait for the visualization to fully load</li>
              <li>Adjust the view, colors, or settings as desired</li>
              <li>Click the export dropdown button (download icon)</li>
              <li>Select your preferred format (PNG, SVG, or HTML)</li>
              <li>The file will download automatically to your browser's download folder</li>
            </ol>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Format Recommendations:</h3>
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li><strong>PNG:</strong> Best for presentations, quick sharing, and embedding in documents</li>
              <li><strong>SVG:</strong> Best for publications, posters, and situations requiring scalability</li>
              <li><strong>HTML:</strong> Best for sharing interactive visualizations with collaborators or for web embedding</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Technical Details:</h3>
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li>PNG exports use <code>canvas.toBlob</code> for high-quality raster images</li>
              <li>SVG exports create vector graphics with embedded images where necessary</li>
              <li>HTML exports include all necessary libraries via CDN for offline functionality</li>
              <li>All exports are performed client-side for privacy and performance</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
