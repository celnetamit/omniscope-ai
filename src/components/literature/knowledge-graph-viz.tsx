"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Network, Download, ZoomIn, ZoomOut, Maximize2 } from "lucide-react";
import { toast } from "sonner";

interface GraphNode {
  id: string;
  label: string;
  type: "gene" | "disease" | "drug" | "pathway";
  properties?: Record<string, any>;
}

interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight?: number;
}

interface KnowledgeGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

interface KnowledgeGraphVizProps {
  query?: string;
  onNodeClick?: (node: GraphNode) => void;
}

export function KnowledgeGraphViz({ query, onNodeClick }: KnowledgeGraphVizProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState(1);

  const fetchGraph = async () => {
    if (!query) {
      toast.error("Please provide a query");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/literature/knowledge-graph`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ query }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setGraphData(data);
        toast.success("Knowledge graph loaded");
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to load graph");
      }
    } catch (error) {
      console.error("Graph error:", error);
      toast.error("Failed to load knowledge graph");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (query) {
      fetchGraph();
    }
  }, [query]);

  useEffect(() => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Simple force-directed layout simulation
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw edges
    ctx.strokeStyle = "#888";
    ctx.lineWidth = 1;
    graphData.edges.forEach((edge) => {
      const sourceNode = graphData.nodes.find((n) => n.id === edge.source);
      const targetNode = graphData.nodes.find((n) => n.id === edge.target);
      if (!sourceNode || !targetNode) return;

      // Simple positioning (in real implementation, use force-directed layout)
      const sourceX = (Math.random() * width * 0.8 + width * 0.1) * zoom;
      const sourceY = (Math.random() * height * 0.8 + height * 0.1) * zoom;
      const targetX = (Math.random() * width * 0.8 + width * 0.1) * zoom;
      const targetY = (Math.random() * height * 0.8 + height * 0.1) * zoom;

      ctx.beginPath();
      ctx.moveTo(sourceX, sourceY);
      ctx.lineTo(targetX, targetY);
      ctx.stroke();
    });

    // Draw nodes
    graphData.nodes.forEach((node) => {
      const x = (Math.random() * width * 0.8 + width * 0.1) * zoom;
      const y = (Math.random() * height * 0.8 + height * 0.1) * zoom;
      const radius = 20 * zoom;

      // Node color based on type
      const colors: Record<string, string> = {
        gene: "#3b82f6",
        disease: "#ef4444",
        drug: "#22c55e",
        pathway: "#a855f7",
      };
      ctx.fillStyle = colors[node.type] || "#888";

      // Draw circle
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();

      // Draw label
      ctx.fillStyle = "#fff";
      ctx.font = `${12 * zoom}px sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(node.label.substring(0, 10), x, y);
    });
  }, [graphData, zoom]);

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.2, 3));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.2, 0.5));

  const exportGraph = () => {
    if (!graphData) return;
    const dataStr = JSON.stringify(graphData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `knowledge-graph-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success("Graph exported");
  };

  const getNodeTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      gene: "bg-blue-500",
      disease: "bg-red-500",
      drug: "bg-green-500",
      pathway: "bg-purple-500",
    };
    return colors[type] || "bg-gray-500";
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                Knowledge Graph
              </CardTitle>
              <CardDescription>
                Interactive visualization of extracted relationships
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="icon" onClick={handleZoomOut}>
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={handleZoomIn}>
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={exportGraph}>
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Legend */}
          <div className="flex items-center gap-4 mb-4 text-sm">
            <span className="text-muted-foreground">Legend:</span>
            {["gene", "disease", "drug", "pathway"].map((type) => (
              <div key={type} className="flex items-center gap-2">
                <div className={`h-3 w-3 rounded-full ${getNodeTypeColor(type)}`} />
                <span className="capitalize">{type}</span>
              </div>
            ))}
          </div>

          {/* Canvas */}
          <div className="border rounded-lg overflow-hidden bg-muted/20">
            <canvas
              ref={canvasRef}
              width={800}
              height={600}
              className="w-full cursor-pointer"
              onClick={(e) => {
                // Handle node click (simplified)
                if (graphData && graphData.nodes.length > 0) {
                  setSelectedNode(graphData.nodes[0]);
                  onNodeClick?.(graphData.nodes[0]);
                }
              }}
            />
          </div>

          {/* Stats */}
          {graphData && (
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="text-center p-3 border rounded-lg">
                <p className="text-2xl font-bold">{graphData.nodes.length}</p>
                <p className="text-xs text-muted-foreground">Nodes</p>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <p className="text-2xl font-bold">{graphData.edges.length}</p>
                <p className="text-xs text-muted-foreground">Relationships</p>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <p className="text-2xl font-bold">{zoom.toFixed(1)}x</p>
                <p className="text-xs text-muted-foreground">Zoom</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Selected Node Details */}
      {selectedNode && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Node Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className={`h-3 w-3 rounded-full ${getNodeTypeColor(selectedNode.type)}`} />
                <h4 className="font-medium">{selectedNode.label}</h4>
                <Badge variant="secondary" className="capitalize">
                  {selectedNode.type}
                </Badge>
              </div>
              {selectedNode.properties && (
                <div className="text-sm space-y-1">
                  {Object.entries(selectedNode.properties).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-muted-foreground capitalize">{key}:</span>
                      <span className="font-medium">{String(value)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
