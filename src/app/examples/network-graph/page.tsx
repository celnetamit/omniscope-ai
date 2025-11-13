"use client";

import React, { useState } from 'react';
import { NetworkGraph3D } from '@/components/visualization';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function NetworkGraphExample() {
  const [graphKey, setGraphKey] = useState(0);

  // Example 1: Simple protein-protein interaction network
  const proteinNetwork = {
    nodes: [
      { id: 'TP53', label: 'TP53', type: 'gene' },
      { id: 'MDM2', label: 'MDM2', type: 'gene' },
      { id: 'CDKN1A', label: 'CDKN1A', type: 'gene' },
      { id: 'BAX', label: 'BAX', type: 'gene' },
      { id: 'BCL2', label: 'BCL2', type: 'gene' },
      { id: 'PUMA', label: 'PUMA', type: 'gene' },
      { id: 'ATM', label: 'ATM', type: 'gene' },
      { id: 'CHK2', label: 'CHK2', type: 'gene' },
    ],
    edges: [
      { source: 'TP53', target: 'MDM2', weight: 0.9, type: 'inhibits' },
      { source: 'TP53', target: 'CDKN1A', weight: 0.8, type: 'activates' },
      { source: 'TP53', target: 'BAX', weight: 0.85, type: 'activates' },
      { source: 'TP53', target: 'PUMA', weight: 0.75, type: 'activates' },
      { source: 'MDM2', target: 'TP53', weight: 0.9, type: 'inhibits' },
      { source: 'BAX', target: 'BCL2', weight: 0.7, type: 'inhibits' },
      { source: 'ATM', target: 'TP53', weight: 0.8, type: 'activates' },
      { source: 'ATM', target: 'CHK2', weight: 0.75, type: 'activates' },
      { source: 'CHK2', target: 'TP53', weight: 0.7, type: 'activates' },
    ],
  };

  // Example 2: Metabolic pathway network
  const metabolicNetwork = {
    nodes: [
      { id: 'Glucose', label: 'Glucose', type: 'metabolite' },
      { id: 'G6P', label: 'Glucose-6-P', type: 'metabolite' },
      { id: 'F6P', label: 'Fructose-6-P', type: 'metabolite' },
      { id: 'F16BP', label: 'Fructose-1,6-BP', type: 'metabolite' },
      { id: 'DHAP', label: 'DHAP', type: 'metabolite' },
      { id: 'G3P', label: 'G3P', type: 'metabolite' },
      { id: 'PEP', label: 'PEP', type: 'metabolite' },
      { id: 'Pyruvate', label: 'Pyruvate', type: 'metabolite' },
      { id: 'AcetylCoA', label: 'Acetyl-CoA', type: 'metabolite' },
      { id: 'Citrate', label: 'Citrate', type: 'metabolite' },
    ],
    edges: [
      { source: 'Glucose', target: 'G6P', weight: 1.0 },
      { source: 'G6P', target: 'F6P', weight: 1.0 },
      { source: 'F6P', target: 'F16BP', weight: 1.0 },
      { source: 'F16BP', target: 'DHAP', weight: 1.0 },
      { source: 'F16BP', target: 'G3P', weight: 1.0 },
      { source: 'DHAP', target: 'G3P', weight: 1.0 },
      { source: 'G3P', target: 'PEP', weight: 1.0 },
      { source: 'PEP', target: 'Pyruvate', weight: 1.0 },
      { source: 'Pyruvate', target: 'AcetylCoA', weight: 1.0 },
      { source: 'AcetylCoA', target: 'Citrate', weight: 1.0 },
    ],
  };

  // Example 3: Complex network with multiple types
  const complexNetwork = {
    nodes: [
      { id: 'BRCA1', label: 'BRCA1', type: 'gene' },
      { id: 'BRCA2', label: 'BRCA2', type: 'gene' },
      { id: 'RAD51', label: 'RAD51', type: 'protein' },
      { id: 'DNA_Repair', label: 'DNA Repair', type: 'pathway' },
      { id: 'Cell_Cycle', label: 'Cell Cycle', type: 'pathway' },
      { id: 'Apoptosis', label: 'Apoptosis', type: 'pathway' },
      { id: 'p53', label: 'p53', type: 'protein' },
      { id: 'ATM', label: 'ATM', type: 'protein' },
      { id: 'CHK1', label: 'CHK1', type: 'protein' },
      { id: 'CHK2', label: 'CHK2', type: 'protein' },
      { id: 'Estrogen', label: 'Estrogen', type: 'metabolite' },
      { id: 'ESR1', label: 'ESR1', type: 'gene' },
    ],
    edges: [
      { source: 'BRCA1', target: 'RAD51', weight: 0.9 },
      { source: 'BRCA2', target: 'RAD51', weight: 0.85 },
      { source: 'BRCA1', target: 'DNA_Repair', weight: 0.95 },
      { source: 'BRCA2', target: 'DNA_Repair', weight: 0.9 },
      { source: 'BRCA1', target: 'Cell_Cycle', weight: 0.7 },
      { source: 'p53', target: 'Apoptosis', weight: 0.9 },
      { source: 'p53', target: 'Cell_Cycle', weight: 0.85 },
      { source: 'ATM', target: 'p53', weight: 0.8 },
      { source: 'ATM', target: 'CHK2', weight: 0.75 },
      { source: 'CHK1', target: 'Cell_Cycle', weight: 0.7 },
      { source: 'CHK2', target: 'Cell_Cycle', weight: 0.7 },
      { source: 'Estrogen', target: 'ESR1', weight: 0.9 },
      { source: 'ESR1', target: 'BRCA1', weight: 0.6 },
    ],
  };

  const [currentNetwork, setCurrentNetwork] = useState(proteinNetwork);

  const loadExample = (network: any) => {
    setCurrentNetwork(network);
    setGraphKey(prev => prev + 1); // Force re-render
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>3D Network Graph Examples</CardTitle>
          <CardDescription>
            Interactive demonstrations of the 3D network visualization component
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            <Button onClick={() => loadExample(proteinNetwork)} variant="outline">
              Protein-Protein Interactions
            </Button>
            <Button onClick={() => loadExample(metabolicNetwork)} variant="outline">
              Metabolic Pathway
            </Button>
            <Button onClick={() => loadExample(complexNetwork)} variant="outline">
              Complex Multi-Type Network
            </Button>
          </div>

          <div className="text-sm text-muted-foreground">
            <p><strong>Instructions:</strong></p>
            <ul className="list-disc list-inside space-y-1 mt-2">
              <li>Click and drag to rotate the graph</li>
              <li>Scroll to zoom in/out</li>
              <li>Click on nodes to see details</li>
              <li>Hover over nodes to see labels</li>
              <li>Use the controls to customize appearance</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <NetworkGraph3D
        key={graphKey}
        nodes={currentNetwork.nodes}
        edges={currentNetwork.edges}
        onNodeClick={(node) => console.log('Node clicked:', node)}
        onNodeHover={(node) => console.log('Node hovered:', node)}
      />
    </div>
  );
}
