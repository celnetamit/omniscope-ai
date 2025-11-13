"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Slider } from '@/components/ui/slider';
import { Loader2, Download, RotateCw, ZoomIn, ZoomOut, Info, FileImage, FileCode, Globe } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import { exportCanvasToPNG, exportSVG, exportForceGraphToHTML } from '@/lib/visualization-export';

interface NetworkNode {
  id: string;
  label?: string;
  type?: string;
  metadata?: Record<string, any>;
}

interface NetworkEdge {
  source: string;
  target: string;
  weight?: number;
  type?: string;
}

interface NetworkGraph3DProps {
  nodes?: NetworkNode[];
  edges?: NetworkEdge[];
  onNodeClick?: (node: any) => void;
  onNodeHover?: (node: any) => void;
}

interface ProcessedNode {
  id: string;
  label: string;
  x: number;
  y: number;
  z: number;
  degree: number;
  [key: string]: any;
}

interface ProcessedEdge {
  source: string;
  target: string;
  weight: number;
  [key: string]: any;
}

interface NetworkData {
  nodes: ProcessedNode[];
  edges: ProcessedEdge[];
  node_count: number;
  edge_count: number;
  density: number;
  is_connected: boolean;
  centrality_metrics?: {
    degree_centrality: Record<string, number>;
    betweenness_centrality: Record<string, number>;
    closeness_centrality: Record<string, number>;
    eigenvector_centrality: Record<string, number>;
  };
}

export function NetworkGraph3D({ 
  nodes: initialNodes, 
  edges: initialEdges,
  onNodeClick,
  onNodeHover
}: NetworkGraph3DProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [networkData, setNetworkData] = useState<NetworkData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ProcessedNode | null>(null);
  
  // Visualization settings
  const [nodeSize, setNodeSize] = useState(5);
  const [linkWidth, setLinkWidth] = useState(1);
  const [nodeColorBy, setNodeColorBy] = useState<'degree' | 'type' | 'centrality'>('degree');
  const [showLabels, setShowLabels] = useState(true);
  const [linkOpacity, setLinkOpacity] = useState(0.6);

  // Initialize 3D Force Graph
  useEffect(() => {
    const initGraph = async () => {
      if (!containerRef.current) return;

      try {
        // Dynamically import ForceGraph3D to avoid SSR issues
        const { default: ForceGraph3D } = await import('three-forcegraph');
        
        // Create graph instance
        const graph = new ForceGraph3D(containerRef.current)
          .backgroundColor('#ffffff')
          .nodeLabel('label')
          .nodeAutoColorBy(nodeColorBy)
          .linkDirectionalParticles(2)
          .linkDirectionalParticleWidth(linkWidth)
          .linkOpacity(linkOpacity)
          .onNodeClick((node: any) => {
            setSelectedNode(node);
            if (onNodeClick) onNodeClick(node);
          })
          .onNodeHover((node: any) => {
            if (onNodeHover) onNodeHover(node);
          });
        
        graphRef.current = graph;

        // Load initial data if provided
        if (initialNodes && initialEdges) {
          await loadNetwork(initialNodes, initialEdges);
        }

        return () => {
          // Cleanup
          if (graphRef.current) {
            graphRef.current._destructor();
          }
        };
      } catch (err) {
        console.error('Failed to initialize 3D graph:', err);
        setError('Failed to initialize 3D graph viewer');
      }
    };

    initGraph();
  }, []);

  // Update graph when settings change
  useEffect(() => {
    if (graphRef.current && networkData) {
      updateGraphSettings();
    }
  }, [nodeSize, linkWidth, nodeColorBy, showLabels, linkOpacity]);

  const loadNetwork = async (nodes: NetworkNode[], edges: NetworkEdge[]) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/visualization/network/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nodes, edges }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate network');
      }

      const data: NetworkData = await response.json();
      setNetworkData(data);

      // Update graph with new data
      if (graphRef.current) {
        graphRef.current
          .graphData({
            nodes: data.nodes,
            links: data.edges.map(e => ({
              source: e.source,
              target: e.target,
              value: e.weight
            }))
          });
        
        updateGraphSettings();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load network');
      console.error('Error loading network:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateGraphSettings = () => {
    if (!graphRef.current || !networkData) return;

    // Update node appearance
    graphRef.current
      .nodeVal((node: ProcessedNode) => nodeSize)
      .nodeLabel((node: ProcessedNode) => 
        showLabels ? `${node.label}\nDegree: ${node.degree}` : ''
      )
      .nodeColor((node: ProcessedNode) => getNodeColor(node))
      .linkWidth(linkWidth)
      .linkOpacity(linkOpacity);
  };

  const getNodeColor = (node: ProcessedNode): string => {
    if (nodeColorBy === 'degree') {
      // Color by degree (connectivity)
      const maxDegree = Math.max(...networkData!.nodes.map(n => n.degree));
      const intensity = node.degree / maxDegree;
      return `rgb(${Math.floor(255 * (1 - intensity))}, ${Math.floor(100 + 155 * intensity)}, ${Math.floor(255 * (1 - intensity))})`;
    } else if (nodeColorBy === 'type' && node.type) {
      // Color by type
      const typeColors: Record<string, string> = {
        'gene': '#3b82f6',
        'protein': '#10b981',
        'metabolite': '#f59e0b',
        'pathway': '#8b5cf6',
        'default': '#6b7280'
      };
      return typeColors[node.type] || typeColors.default;
    } else if (nodeColorBy === 'centrality' && networkData?.centrality_metrics) {
      // Color by betweenness centrality
      const centrality = networkData.centrality_metrics.betweenness_centrality[node.id] || 0;
      const maxCentrality = Math.max(...Object.values(networkData.centrality_metrics.betweenness_centrality));
      const intensity = centrality / maxCentrality;
      return `rgb(${Math.floor(255 * intensity)}, ${Math.floor(100 + 155 * (1 - intensity))}, ${Math.floor(100)})`;
    }
    return '#6b7280';
  };

  const resetView = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400);
    }
  };

  const zoomIn = () => {
    if (graphRef.current) {
      const camera = graphRef.current.camera();
      camera.position.multiplyScalar(0.8);
    }
  };

  const zoomOut = () => {
    if (graphRef.current) {
      const camera = graphRef.current.camera();
      camera.position.multiplyScalar(1.2);
    }
  };

  const exportToPNG = async () => {
    if (!graphRef.current) return;

    try {
      const renderer = graphRef.current.renderer();
      const canvas = renderer.domElement;
      
      await exportCanvasToPNG(canvas, {
        filename: 'network_graph_3d.png',
        scale: 2
      });
      
      toast.success('PNG exported successfully');
    } catch (error) {
      console.error('Failed to export PNG:', error);
      toast.error('Failed to export PNG');
    }
  };

  const exportToSVG = async () => {
    if (!graphRef.current) return;

    try {
      const renderer = graphRef.current.renderer();
      const canvas = renderer.domElement;
      
      // Create SVG with embedded canvas image
      const svgNS = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(svgNS, 'svg');
      svg.setAttribute('width', canvas.width.toString());
      svg.setAttribute('height', canvas.height.toString());
      svg.setAttribute('viewBox', `0 0 ${canvas.width} ${canvas.height}`);
      
      const dataURL = canvas.toDataURL('image/png');
      const image = document.createElementNS(svgNS, 'image');
      image.setAttribute('href', dataURL);
      image.setAttribute('width', canvas.width.toString());
      image.setAttribute('height', canvas.height.toString());
      svg.appendChild(image);
      
      await exportSVG(svg, {
        filename: 'network_graph_3d.svg',
        width: canvas.width,
        height: canvas.height
      });
      
      toast.success('SVG exported successfully');
    } catch (error) {
      console.error('Failed to export SVG:', error);
      toast.error('Failed to export SVG');
    }
  };

  const exportToHTML = async () => {
    if (!networkData) {
      toast.error('No network data loaded');
      return;
    }

    try {
      await exportForceGraphToHTML(
        {
          nodes: networkData.nodes,
          links: networkData.edges.map(e => ({
            source: e.source,
            target: e.target,
            value: e.weight
          }))
        },
        {
          filename: 'network_graph_3d.html',
          title: '3D Network Graph',
          description: `Interactive network with ${networkData.node_count} nodes and ${networkData.edge_count} edges (density: ${networkData.density.toFixed(3)})`
        }
      );
      
      toast.success('Interactive HTML exported successfully');
    } catch (error) {
      console.error('Failed to export HTML:', error);
      toast.error('Failed to export HTML');
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>3D Network Graph</CardTitle>
        <CardDescription>
          Interactive force-directed 3D visualization of network relationships
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Visualization Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <Label>Color By</Label>
            <Select value={nodeColorBy} onValueChange={(v: any) => setNodeColorBy(v)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="degree">Degree (Connectivity)</SelectItem>
                <SelectItem value="type">Node Type</SelectItem>
                <SelectItem value="centrality">Centrality</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>Node Size: {nodeSize}</Label>
            <Slider
              value={[nodeSize]}
              onValueChange={(v) => setNodeSize(v[0])}
              min={1}
              max={20}
              step={1}
              className="mt-2"
            />
          </div>

          <div>
            <Label>Link Width: {linkWidth}</Label>
            <Slider
              value={[linkWidth]}
              onValueChange={(v) => setLinkWidth(v[0])}
              min={0.5}
              max={5}
              step={0.5}
              className="mt-2"
            />
          </div>

          <div>
            <Label>Link Opacity: {linkOpacity.toFixed(2)}</Label>
            <Slider
              value={[linkOpacity]}
              onValueChange={(v) => setLinkOpacity(v[0])}
              min={0.1}
              max={1}
              step={0.1}
              className="mt-2"
            />
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowLabels(!showLabels)}
          >
            {showLabels ? 'Hide' : 'Show'} Labels
          </Button>
          <Button variant="outline" size="icon" onClick={resetView} title="Reset View">
            <RotateCw className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={zoomIn} title="Zoom In">
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={zoomOut} title="Zoom Out">
            <ZoomOut className="h-4 w-4" />
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" title="Export">
                <Download className="h-4 w-4" />
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
        </div>

        {/* Graph Container */}
        <div
          ref={containerRef}
          className="w-full h-[600px] border rounded-lg bg-white relative"
        />

        {/* Network Statistics */}
        {networkData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="font-semibold">Nodes</div>
              <div className="text-muted-foreground">{networkData.node_count}</div>
            </div>
            <div>
              <div className="font-semibold">Edges</div>
              <div className="text-muted-foreground">{networkData.edge_count}</div>
            </div>
            <div>
              <div className="font-semibold">Density</div>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="text-muted-foreground flex items-center gap-1">
                      {networkData.density.toFixed(3)}
                      <Info className="h-3 w-3" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Ratio of actual edges to possible edges</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <div>
              <div className="font-semibold">Connected</div>
              <div className="text-muted-foreground">
                {networkData.is_connected ? 'Yes' : 'No'}
              </div>
            </div>
          </div>
        )}

        {/* Selected Node Info */}
        {selectedNode && (
          <div className="p-4 border rounded-lg bg-muted/50">
            <h4 className="font-semibold mb-2">Selected Node</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="font-medium">ID:</span> {selectedNode.id}
              </div>
              <div>
                <span className="font-medium">Label:</span> {selectedNode.label}
              </div>
              <div>
                <span className="font-medium">Degree:</span> {selectedNode.degree}
              </div>
              {selectedNode.type && (
                <div>
                  <span className="font-medium">Type:</span> {selectedNode.type}
                </div>
              )}
              {networkData?.centrality_metrics && (
                <>
                  <div>
                    <span className="font-medium">Betweenness:</span>{' '}
                    {networkData.centrality_metrics.betweenness_centrality[selectedNode.id]?.toFixed(4) || 'N/A'}
                  </div>
                  <div>
                    <span className="font-medium">Closeness:</span>{' '}
                    {networkData.centrality_metrics.closeness_centrality[selectedNode.id]?.toFixed(4) || 'N/A'}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-2">Loading network...</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
