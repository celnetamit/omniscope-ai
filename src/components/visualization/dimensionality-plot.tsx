'use client';

import React, { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Loader2, Download, RotateCcw, FileImage, FileCode, Globe } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import { exportPlotlyToPNG, exportPlotlyToSVG, exportPlotlyToHTML } from '@/lib/visualization-export';

// Dynamically import Plot to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false }) as any;

export interface DimensionalityPlotProps {
  data?: number[][];
  metadata?: any[];
  metadataName?: string;
  method?: 'pca' | 'tsne' | 'umap';
  autoCompute?: boolean;
  onMethodChange?: (method: 'pca' | 'tsne' | 'umap') => void;
  className?: string;
}

interface ReductionResult {
  method: string;
  coordinates: number[][];
  n_samples: number;
  n_features: number;
  metadata?: {
    name: string;
    values: any[];
    color_indices?: number[];
    unique_values?: any[];
  };
  explained_variance?: number[];
  total_variance_explained?: number;
  perplexity?: number;
  kl_divergence?: number;
  n_neighbors?: number;
}

const DEFAULT_COLORS = [
  '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
  '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
  '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5'
];

export function DimensionalityPlot({
  data,
  metadata,
  metadataName = 'group',
  method = 'pca',
  autoCompute = false,
  onMethodChange,
  className = ''
}: DimensionalityPlotProps) {
  const [selectedMethod, setSelectedMethod] = useState<'pca' | 'tsne' | 'umap'>(method);
  const [result, setResult] = useState<ReductionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Method-specific parameters
  const [perplexity, setPerplexity] = useState(30);
  const [nNeighbors, setNNeighbors] = useState(15);

  // Compute dimensionality reduction
  const computeReduction = async () => {
    if (!data || data.length === 0) {
      setError('No data provided');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestBody: any = {
        data,
        method: selectedMethod,
        parameters: {}
      };

      // Add method-specific parameters
      if (selectedMethod === 'tsne') {
        requestBody.parameters.perplexity = perplexity;
      } else if (selectedMethod === 'umap') {
        requestBody.parameters.n_neighbors = nNeighbors;
      }

      // Add metadata if provided
      if (metadata && metadata.length > 0) {
        requestBody.metadata = metadata;
        requestBody.metadata_name = metadataName;
      }

      const response = await fetch('/api/proxy?path=/api/visualization/dimensionality-reduction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to compute dimensionality reduction');
      }

      const resultData: ReductionResult = await response.json();
      setResult(resultData);
      toast.success(`${selectedMethod.toUpperCase()} computation completed`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Auto-compute on mount if enabled
  useEffect(() => {
    if (autoCompute && data && data.length > 0) {
      computeReduction();
    }
  }, []);

  // Handle method change
  const handleMethodChange = (newMethod: 'pca' | 'tsne' | 'umap') => {
    setSelectedMethod(newMethod);
    setResult(null);
    if (onMethodChange) {
      onMethodChange(newMethod);
    }
  };

  // Prepare plot data
  const plotData = useMemo(() => {
    if (!result || !result.coordinates) return [];

    const coords = result.coordinates;
    const x = coords.map(c => c[0]);
    const y = coords.map(c => c[1]);
    const z = coords.map(c => c[2]);

    // Handle metadata coloring
    if (result.metadata && result.metadata.values) {
      const metadataValues = result.metadata.values;
      
      // Check if we have categorical data with color indices
      if (result.metadata.color_indices && result.metadata.unique_values) {
        const colorIndices = result.metadata.color_indices;
        const uniqueValues = result.metadata.unique_values;
        
        // Create separate traces for each category
        return uniqueValues.map((value, idx) => {
          const indices = colorIndices
            .map((ci, i) => ci === idx ? i : -1)
            .filter(i => i !== -1);
          
          return {
            type: 'scatter3d' as const,
            mode: 'markers' as const,
            name: String(value),
            x: indices.map(i => x[i]),
            y: indices.map(i => y[i]),
            z: indices.map(i => z[i]),
            marker: {
              size: 5,
              color: DEFAULT_COLORS[idx % DEFAULT_COLORS.length],
              opacity: 0.8,
              line: {
                color: 'white',
                width: 0.5
              }
            },
            text: indices.map(i => `Sample ${i}<br>${result.metadata!.name}: ${metadataValues[i]}`),
            hovertemplate: '%{text}<br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>'
          };
        });
      } else {
        // Continuous metadata - use color scale
        return [{
          type: 'scatter3d' as const,
          mode: 'markers' as const,
          x,
          y,
          z,
          marker: {
            size: 5,
            color: metadataValues,
            colorscale: 'Viridis',
            showscale: true,
            colorbar: {
              title: result.metadata.name,
              thickness: 15,
              len: 0.7
            },
            opacity: 0.8,
            line: {
              color: 'white',
              width: 0.5
            }
          },
          text: metadataValues.map((val, i) => `Sample ${i}<br>${result.metadata!.name}: ${val}`),
          hovertemplate: '%{text}<br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>'
        }];
      }
    }

    // No metadata - single trace
    return [{
      type: 'scatter3d' as const,
      mode: 'markers' as const,
      x,
      y,
      z,
      marker: {
        size: 5,
        color: '#1f77b4',
        opacity: 0.8,
        line: {
          color: 'white',
          width: 0.5
        }
      },
      text: coords.map((_, i) => `Sample ${i}`),
      hovertemplate: '%{text}<br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>'
    }];
  }, [result]);

  // Plot layout
  const plotLayout = useMemo(() => {
    const methodTitle = selectedMethod.toUpperCase();
    let subtitle = '';
    
    if (result) {
      if (result.method === 'pca' && result.total_variance_explained) {
        subtitle = ` (${(result.total_variance_explained * 100).toFixed(1)}% variance explained)`;
      } else if (result.method === 'tsne' && result.kl_divergence) {
        subtitle = ` (KL divergence: ${result.kl_divergence.toFixed(4)})`;
      } else if (result.method === 'umap' && result.n_neighbors) {
        subtitle = ` (n_neighbors: ${result.n_neighbors})`;
      }
    }

    return {
      title: `${methodTitle} 3D Visualization${subtitle}`,
      autosize: true,
      scene: {
        xaxis: { title: 'Component 1' },
        yaxis: { title: 'Component 2' },
        zaxis: { title: 'Component 3' },
        camera: {
          eye: { x: 1.5, y: 1.5, z: 1.5 }
        }
      },
      margin: { l: 0, r: 0, b: 0, t: 40 },
      hovermode: 'closest' as const,
      showlegend: result?.metadata?.unique_values ? true : false,
      legend: {
        x: 1.02,
        y: 1,
        xanchor: 'left' as const,
        yanchor: 'top' as const
      }
    };
  }, [selectedMethod, result]);

  // Export functions
  const exportToPNG = async () => {
    const plotElement = document.querySelector('.js-plotly-plot') as HTMLElement;
    if (!plotElement) {
      toast.error('No plot to export');
      return;
    }

    try {
      await exportPlotlyToPNG(plotElement, {
        filename: `${selectedMethod}_plot.png`,
        width: 1920,
        height: 1080
      });
      toast.success('PNG exported successfully');
    } catch (error) {
      console.error('Failed to export PNG:', error);
      toast.error('Failed to export PNG');
    }
  };

  const exportToSVG = async () => {
    const plotElement = document.querySelector('.js-plotly-plot') as HTMLElement;
    if (!plotElement) {
      toast.error('No plot to export');
      return;
    }

    try {
      await exportPlotlyToSVG(plotElement, {
        filename: `${selectedMethod}_plot.svg`,
        width: 1920,
        height: 1080
      });
      toast.success('SVG exported successfully');
    } catch (error) {
      console.error('Failed to export SVG:', error);
      toast.error('Failed to export SVG');
    }
  };

  const exportToHTML = async () => {
    if (!result) {
      toast.error('No data to export');
      return;
    }

    try {
      await exportPlotlyToHTML(plotData, plotLayout, {
        filename: `${selectedMethod}_plot.html`,
        title: `${selectedMethod.toUpperCase()} Dimensionality Reduction`,
        description: `Interactive 3D visualization with ${result.n_samples} samples and ${result.n_features} features`
      });
      toast.success('Interactive HTML exported successfully');
    } catch (error) {
      console.error('Failed to export HTML:', error);
      toast.error('Failed to export HTML');
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Dimensionality Reduction</CardTitle>
        <CardDescription>
          Visualize high-dimensional data in 3D space using PCA, t-SNE, or UMAP
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="method">Method</Label>
            <Select value={selectedMethod} onValueChange={handleMethodChange}>
              <SelectTrigger id="method">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="pca">PCA</SelectItem>
                <SelectItem value="tsne">t-SNE</SelectItem>
                <SelectItem value="umap">UMAP</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {selectedMethod === 'tsne' && (
            <div className="space-y-2">
              <Label htmlFor="perplexity">Perplexity</Label>
              <Input
                id="perplexity"
                type="number"
                min="5"
                max="50"
                value={perplexity}
                onChange={(e) => setPerplexity(Number(e.target.value))}
              />
            </div>
          )}

          {selectedMethod === 'umap' && (
            <div className="space-y-2">
              <Label htmlFor="n_neighbors">N Neighbors</Label>
              <Input
                id="n_neighbors"
                type="number"
                min="2"
                max="100"
                value={nNeighbors}
                onChange={(e) => setNNeighbors(Number(e.target.value))}
              />
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button onClick={computeReduction} disabled={loading || !data}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Computing...
              </>
            ) : (
              <>
                <RotateCcw className="mr-2 h-4 w-4" />
                Compute
              </>
            )}
          </Button>
          {result && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  Export
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={exportToPNG}>
                  <FileImage className="mr-2 h-4 w-4" />
                  Export as PNG
                </DropdownMenuItem>
                <DropdownMenuItem onClick={exportToSVG}>
                  <FileCode className="mr-2 h-4 w-4" />
                  Export as SVG
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={exportToHTML}>
                  <Globe className="mr-2 h-4 w-4" />
                  Export Interactive HTML
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-destructive/10 text-destructive rounded-md">
            {error}
          </div>
        )}

        {/* Info Display */}
        {result && (
          <div className="p-4 bg-muted rounded-md space-y-1 text-sm">
            <div><strong>Samples:</strong> {result.n_samples}</div>
            <div><strong>Features:</strong> {result.n_features}</div>
            {result.explained_variance && (
              <div>
                <strong>Explained Variance:</strong>{' '}
                {result.explained_variance.map((v, i) => `PC${i + 1}: ${(v * 100).toFixed(1)}%`).join(', ')}
              </div>
            )}
            {result.metadata && (
              <div><strong>Color by:</strong> {result.metadata.name}</div>
            )}
          </div>
        )}

        {/* Plot */}
        <div className="w-full h-[600px] border rounded-md">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : result ? (
            <Plot
              data={plotData}
              layout={plotLayout}
              config={{
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['sendDataToCloud'],
                toImageButtonOptions: {
                  format: 'png',
                  filename: `${selectedMethod}_plot`,
                  height: 1080,
                  width: 1920,
                  scale: 1
                }
              }}
              style={{ width: '100%', height: '100%' }}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              {data ? 'Click "Compute" to generate visualization' : 'No data provided'}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
