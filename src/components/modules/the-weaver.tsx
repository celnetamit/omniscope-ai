'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  GitBranch,
  Plus,
  Play,
  Edit,
  Trash2,
  Copy,
  Lightbulb,
  CheckCircle,
  Clock,
  AlertCircle,
  Zap,
  Database,
  BarChart3,
  Brain,
  Settings
} from 'lucide-react';

interface Pipeline {
  pipeline_id: string;
  name: string;
  project_id: string;
  pipeline_json: {
    nodes: Array<{
      id: string;
      type: string;
      position: { x: number; y: number };
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
    }>;
  };
  created_at: string;
}

interface Suggestion {
  node_type: string;
  reason: string;
}

const nodeTypes = [
  { id: 'UploadGenomicsData', name: 'Upload Genomics', icon: Database, color: 'bg-blue-500' },
  { id: 'UploadProteomicsData', name: 'Upload Proteomics', icon: Database, color: 'bg-green-500' },
  { id: 'UploadMetabolomicsData', name: 'Upload Metabolomics', icon: Database, color: 'bg-purple-500' },
  { id: 'NormalizeRNASeq', name: 'Normalize RNA-seq', icon: BarChart3, color: 'bg-orange-500' },
  { id: 'QCProteomics', name: 'QC Proteomics', icon: CheckCircle, color: 'bg-yellow-500' },
  { id: 'IntegrateMOFAPlus', name: 'MOFA+ Integration', icon: GitBranch, color: 'bg-indigo-500' },
  { id: 'TrainXGBoostModel', name: 'XGBoost Training', icon: Brain, color: 'bg-red-500' },
  { id: 'TrainRandomForestModel', name: 'Random Forest', icon: Brain, color: 'bg-pink-500' },
  { id: 'DataVisualization', name: 'Visualization', icon: BarChart3, color: 'bg-teal-500' },
];

export function TheWeaver() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [newPipelineName, setNewPipelineName] = useState('');
  const [selectedProject, setSelectedProject] = useState('default_project');
  const [currentNodes, setCurrentNodes] = useState<Array<{id: string; type: string; position: {x: number; y: number}}>>([]);
  const [currentEdges, setCurrentEdges] = useState<Array<{id: string; source: string; target: string}>>([]);

  useEffect(() => {
    fetchPipelines();
  }, []);

  const fetchPipelines = async () => {
    try {
      const response = await fetch(`/api/proxy?url=/api/pipelines/project/${selectedProject}/list`);
      const data = await response.json();
      setPipelines(data.pipelines || []);
    } catch (error) {
      console.error('Failed to fetch pipelines:', error);
    }
  };

  const loadPipeline = async (pipelineId: string) => {
    try {
      const response = await fetch(`/api/proxy?url=/api/pipelines/${pipelineId}`);
      const data = await response.json();
      setSelectedPipeline(data);
      setCurrentNodes(data.pipeline_json.nodes);
      setCurrentEdges(data.pipeline_json.edges);
      
      // Get AI suggestions for this pipeline
      getSuggestions(data.pipeline_json);
    } catch (error) {
      console.error('Failed to load pipeline:', error);
    }
  };

  const getSuggestions = async (pipelineJson: any) => {
    try {
      const response = await fetch('/api/proxy?url=/api/pipelines/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pipeline_json: pipelineJson })
      });
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to get suggestions:', error);
    }
  };

  const createNewPipeline = async () => {
    if (!newPipelineName.trim()) return;

    const newPipeline = {
      name: newPipelineName,
      project_id: selectedProject,
      pipeline_json: {
        nodes: [],
        edges: []
      }
    };

    try {
      const response = await fetch('/api/proxy?url=/api/pipelines/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPipeline)
      });
      
      const data = await response.json();
      setNewPipelineName('');
      setIsCreating(false);
      fetchPipelines();
      
      // Load the new pipeline
      loadPipeline(data.pipeline_id);
    } catch (error) {
      console.error('Failed to create pipeline:', error);
    }
  };

  const addNodeToPipeline = (nodeType: string) => {
    const newNode = {
      id: `node_${Date.now()}`,
      type: nodeType,
      position: { 
        x: 100 + (currentNodes.length * 150), 
        y: 100 + (Math.floor(currentNodes.length / 4) * 100) 
      }
    };

    const updatedNodes = [...currentNodes, newNode];
    setCurrentNodes(updatedNodes);

    // Auto-connect to previous node if it makes sense
    if (currentNodes.length > 0) {
      const lastNode = currentNodes[currentNodes.length - 1];
      const newEdge = {
        id: `edge_${Date.now()}`,
        source: lastNode.id,
        target: newNode.id
      };
      setCurrentEdges(prev => [...prev, newEdge]);
    }

    // Save pipeline
    savePipeline(updatedNodes, currentEdges);
  };

  const savePipeline = async (nodes: any[], edges: any[]) => {
    if (!selectedPipeline) return;

    const updatedPipeline = {
      pipeline_id: selectedPipeline.pipeline_id,
      name: selectedPipeline.name,
      project_id: selectedPipeline.project_id,
      pipeline_json: { nodes, edges }
    };

    try {
      await fetch('/api/proxy?url=/api/pipelines/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedPipeline)
      });

      // Get new suggestions
      getSuggestions({ nodes, edges });
    } catch (error) {
      console.error('Failed to save pipeline:', error);
    }
  };

  const duplicatePipeline = async (pipeline: Pipeline) => {
    const duplicatedPipeline = {
      name: `${pipeline.name} (Copy)`,
      project_id: pipeline.project_id,
      pipeline_json: pipeline.pipeline_json
    };

    try {
      await fetch('/api/proxy?url=/api/pipelines/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(duplicatedPipeline)
      });
      fetchPipelines();
    } catch (error) {
      console.error('Failed to duplicate pipeline:', error);
    }
  };

  const getNodeIcon = (nodeType: string) => {
    const nodeConfig = nodeTypes.find(n => n.id === nodeType);
    return nodeConfig ? nodeConfig.icon : Settings;
  };

  const getNodeColor = (nodeType: string) => {
    const nodeConfig = nodeTypes.find(n => n.id === nodeType);
    return nodeConfig ? nodeConfig.color : 'bg-gray-500';
  };

  const getNodeName = (nodeType: string) => {
    const nodeConfig = nodeTypes.find(n => n.id === nodeType);
    return nodeConfig ? nodeConfig.name : nodeType;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <GitBranch className="h-8 w-8" />
            The Weaver
          </h1>
          <p className="text-muted-foreground">
            Build and manage multi-omics analysis pipelines with AI assistance
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={isCreating} onOpenChange={setIsCreating}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Pipeline
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Pipeline</DialogTitle>
                <DialogDescription>
                  Start building a new analysis workflow
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Pipeline Name</Label>
                  <Input
                    id="name"
                    value={newPipelineName}
                    onChange={(e) => setNewPipelineName(e.target.value)}
                    placeholder="Enter pipeline name..."
                  />
                </div>
                <div>
                  <Label htmlFor="project">Project</Label>
                  <Select value={selectedProject} onValueChange={setSelectedProject}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="default_project">Default Project</SelectItem>
                      <SelectItem value="genomics_study">Genomics Study</SelectItem>
                      <SelectItem value="cancer_research">Cancer Research</SelectItem>
                      <SelectItem value="biomarker_discovery">Biomarker Discovery</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreating(false)}>
                  Cancel
                </Button>
                <Button onClick={createNewPipeline} disabled={!newPipelineName.trim()}>
                  Create Pipeline
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Pipeline List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Your Pipelines</CardTitle>
              <CardDescription>
                Select a pipeline to edit or create a new one
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {pipelines.length === 0 ? (
                  <div className="text-center py-4">
                    <GitBranch className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">No pipelines yet</p>
                  </div>
                ) : (
                  pipelines.map((pipeline) => (
                    <div
                      key={pipeline.pipeline_id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-accent ${
                        selectedPipeline?.pipeline_id === pipeline.pipeline_id ? 'bg-accent' : ''
                      }`}
                      onClick={() => loadPipeline(pipeline.pipeline_id)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-sm">{pipeline.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {pipeline.pipeline_json.nodes.length} nodes
                          </p>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              duplicatePipeline(pipeline);
                            }}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          {suggestions.length > 0 && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  AI Suggestions
                </CardTitle>
                <CardDescription>
                  Recommended next steps for your pipeline
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {suggestions.map((suggestion, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <Badge variant="outline" className="text-xs">
                          {getNodeName(suggestion.node_type)}
                        </Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => addNodeToPipeline(suggestion.node_type)}
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {suggestion.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Pipeline Editor */}
        <div className="lg:col-span-3">
          {selectedPipeline ? (
            <Tabs defaultValue="editor" className="space-y-4">
              <TabsList>
                <TabsTrigger value="editor">Pipeline Editor</TabsTrigger>
                <TabsTrigger value="nodes">Add Nodes</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
              </TabsList>

              <TabsContent value="editor" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>{selectedPipeline.name}</CardTitle>
                    <CardDescription>
                      Visual pipeline editor - {currentNodes.length} nodes, {currentEdges.length} connections
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {/* Pipeline Canvas */}
                    <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 min-h-[400px] bg-muted/5">
                      {currentNodes.length === 0 ? (
                        <div className="text-center py-16">
                          <GitBranch className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                          <p className="text-lg font-medium mb-2">Empty Pipeline</p>
                          <p className="text-muted-foreground mb-4">
                            Add nodes to start building your workflow
                          </p>
                          <Button onClick={() => addNodeToPipeline('UploadGenomicsData')}>
                            <Plus className="mr-2 h-4 w-4" />
                            Add First Node
                          </Button>
                        </div>
                      ) : (
                        <div className="relative">
                          {/* Render nodes */}
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {currentNodes.map((node, index) => {
                              const Icon = getNodeIcon(node.type);
                              return (
                                <div
                                  key={node.id}
                                  className="relative p-4 border rounded-lg bg-background shadow-sm"
                                >
                                  <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-lg ${getNodeColor(node.type)} text-white`}>
                                      <Icon className="h-4 w-4" />
                                    </div>
                                    <div>
                                      <p className="font-medium text-sm">{getNodeName(node.type)}</p>
                                      <p className="text-xs text-muted-foreground">Step {index + 1}</p>
                                    </div>
                                  </div>
                                  {index < currentNodes.length - 1 && (
                                    <div className="absolute -right-2 top-1/2 transform -translate-y-1/2">
                                      <div className="w-4 h-0.5 bg-muted-foreground/50"></div>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="nodes" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Available Nodes</CardTitle>
                    <CardDescription>
                      Click on any node type to add it to your pipeline
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {nodeTypes.map((nodeType) => {
                        const Icon = nodeType.icon;
                        return (
                          <div
                            key={nodeType.id}
                            className="p-4 border rounded-lg cursor-pointer hover:shadow-md transition-shadow"
                            onClick={() => addNodeToPipeline(nodeType.id)}
                          >
                            <div className="flex items-center gap-3 mb-2">
                              <div className={`p-2 rounded-lg ${nodeType.color} text-white`}>
                                <Icon className="h-4 w-4" />
                              </div>
                              <p className="font-medium">{nodeType.name}</p>
                            </div>
                            <p className="text-sm text-muted-foreground">
                              Click to add to pipeline
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="settings" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Pipeline Settings</CardTitle>
                    <CardDescription>
                      Configure pipeline properties and execution settings
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <Label>Pipeline Name</Label>
                        <Input value={selectedPipeline.name} readOnly />
                      </div>
                      <div>
                        <Label>Project</Label>
                        <Input value={selectedPipeline.project_id} readOnly />
                      </div>
                      <div>
                        <Label>Created</Label>
                        <Input value={new Date(selectedPipeline.created_at).toLocaleString()} readOnly />
                      </div>
                      <div>
                        <Label>Pipeline ID</Label>
                        <Input value={selectedPipeline.pipeline_id} readOnly className="font-mono text-xs" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <Card>
              <CardContent className="text-center py-16">
                <GitBranch className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">No Pipeline Selected</p>
                <p className="text-muted-foreground mb-4">
                  Select an existing pipeline or create a new one to get started
                </p>
                <Button onClick={() => setIsCreating(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Pipeline
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}