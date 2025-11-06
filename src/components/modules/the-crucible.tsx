'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  Cpu,
  Play,
  Square,
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Brain,
  Zap,
  Target,
  Activity,
  Download
} from 'lucide-react';

interface TrainingJob {
  job_id: string;
  name: string;
  status: 'running' | 'completed' | 'failed';
  progress: {
    current_epoch: number;
    total_epochs: number;
  };
  metrics: {
    accuracy: number;
    loss: number;
  };
  explanation: string;
  pipeline_id: string;
  data_ids: string[];
  start_time: Date;
  end_time?: Date;
  final_metrics?: {
    accuracy: number;
    auc: number;
    precision: number;
    recall: number;
  };
}

interface Pipeline {
  pipeline_id: string;
  name: string;
  project_id: string;
}

interface DataFile {
  file_id: string;
  name: string;
  status: string;
}

const modelTypes = [
  { id: 'xgboost', name: 'XGBoost', description: 'Gradient boosting for structured data' },
  { id: 'random_forest', name: 'Random Forest', description: 'Ensemble learning method' },
  { id: 'neural_network', name: 'Neural Network', description: 'Deep learning model' },
  { id: 'svm', name: 'Support Vector Machine', description: 'Kernel-based classifier' },
];

export function TheCrucible() {
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([]);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [dataFiles, setDataFiles] = useState<DataFile[]>([]);
  const [selectedJob, setSelectedJob] = useState<TrainingJob | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedPipeline, setSelectedPipeline] = useState('');
  const [selectedDataFiles, setSelectedDataFiles] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState('xgboost');

  useEffect(() => {
    fetchTrainingJobs();
    fetchPipelines();
    fetchDataFiles();
    
    // Set up polling for active jobs
    const interval = setInterval(fetchTrainingJobs, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchTrainingJobs = async () => {
    // Mock data for now - in real app would fetch from API
    const mockJobs: TrainingJob[] = [
      {
        job_id: 'job_001',
        name: 'Cancer Classification Model',
        status: 'completed',
        progress: { current_epoch: 10, total_epochs: 10 },
        metrics: { accuracy: 0.95, loss: 0.12 },
        explanation: 'Training completed successfully. Model achieved excellent performance.',
        pipeline_id: 'pipeline_001',
        data_ids: ['data_001'],
        start_time: new Date(Date.now() - 300000),
        end_time: new Date(Date.now() - 60000),
        final_metrics: { accuracy: 0.95, auc: 0.97, precision: 0.93, recall: 0.96 }
      },
      {
        job_id: 'job_002',
        name: 'Biomarker Discovery',
        status: 'running',
        progress: { current_epoch: 7, total_epochs: 15 },
        metrics: { accuracy: 0.87, loss: 0.28 },
        explanation: 'Training in progress. Model is learning complex patterns in the data.',
        pipeline_id: 'pipeline_002',
        data_ids: ['data_002', 'data_003'],
        start_time: new Date(Date.now() - 120000)
      }
    ];
    setTrainingJobs(mockJobs);
  };

  const fetchPipelines = async () => {
    try {
      const response = await fetch('/api/proxy?url=/api/pipelines/project/default_project/list');
      const data = await response.json();
      setPipelines(data.pipelines || []);
    } catch (error) {
      console.error('Failed to fetch pipelines:', error);
    }
  };

  const fetchDataFiles = async () => {
    // Mock data files
    const mockFiles: DataFile[] = [
      { file_id: 'c27b62bf-26bd-4939-8d57-3bd2ef34ba53', name: 'genomics_expression.csv', status: 'complete' },
      { file_id: 'd1d891a5-937e-42c1-9f01-7733b18a7f61', name: 'clinical_data_with_missing.csv', status: 'complete' },
      { file_id: 'f8e9d2c1-4b5a-6789-0123-456789abcdef', name: 'proteomics_data.csv', status: 'complete' }
    ];
    setDataFiles(mockFiles);
  };

  const startTrainingJob = async () => {
    if (!selectedPipeline || selectedDataFiles.length === 0) return;

    const jobData = {
      pipeline_id: selectedPipeline,
      data_ids: selectedDataFiles
    };

    try {
      const response = await fetch('/api/proxy?url=/api/models/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jobData)
      });

      const data = await response.json();
      
      // Add new job to list
      const newJob: TrainingJob = {
        job_id: data.job_id,
        name: `${selectedModel} Training`,
        status: 'running',
        progress: { current_epoch: 0, total_epochs: 10 },
        metrics: { accuracy: 0.5, loss: 1.0 },
        explanation: 'Training started. Initializing model parameters.',
        pipeline_id: selectedPipeline,
        data_ids: selectedDataFiles,
        start_time: new Date()
      };

      setTrainingJobs(prev => [newJob, ...prev]);
      setIsCreating(false);
      setSelectedPipeline('');
      setSelectedDataFiles([]);
    } catch (error) {
      console.error('Failed to start training job:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running':
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive'> = {
      'completed': 'default',
      'running': 'secondary',
      'failed': 'destructive',
    };
    
    return (
      <Badge variant={variants[status] || 'secondary'}>
        {status}
      </Badge>
    );
  };

  const formatDuration = (start: Date, end?: Date) => {
    const endTime = end || new Date();
    const duration = Math.floor((endTime.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) return `${duration}s`;
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Cpu className="h-8 w-8" />
            The Crucible
          </h1>
          <p className="text-muted-foreground">
            Train and monitor machine learning models with real-time progress tracking
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={isCreating} onOpenChange={setIsCreating}>
            <DialogTrigger asChild>
              <Button>
                <Play className="mr-2 h-4 w-4" />
                Start Training
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Start New Training Job</DialogTitle>
                <DialogDescription>
                  Configure and launch a new model training session
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-6">
                <div>
                  <label className="text-sm font-medium">Model Type</label>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {modelTypes.map(model => (
                        <SelectItem key={model.id} value={model.id}>
                          <div>
                            <div className="font-medium">{model.name}</div>
                            <div className="text-xs text-muted-foreground">{model.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Pipeline</label>
                  <Select value={selectedPipeline} onValueChange={setSelectedPipeline}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a pipeline" />
                    </SelectTrigger>
                    <SelectContent>
                      {pipelines.map(pipeline => (
                        <SelectItem key={pipeline.pipeline_id} value={pipeline.pipeline_id}>
                          {pipeline.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Training Data</label>
                  <div className="mt-2 space-y-2 max-h-40 overflow-y-auto">
                    {dataFiles.map(file => (
                      <div key={file.file_id} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={file.file_id}
                          checked={selectedDataFiles.includes(file.file_id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedDataFiles(prev => [...prev, file.file_id]);
                            } else {
                              setSelectedDataFiles(prev => prev.filter(id => id !== file.file_id));
                            }
                          }}
                          className="rounded"
                        />
                        <label htmlFor={file.file_id} className="text-sm cursor-pointer">
                          {file.name}
                        </label>
                        <Badge variant="outline" className="text-xs">
                          {file.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreating(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={startTrainingJob}
                  disabled={!selectedPipeline || selectedDataFiles.length === 0}
                >
                  Start Training
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Training Jobs List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Training Jobs</CardTitle>
              <CardDescription>
                Monitor active and completed training sessions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {trainingJobs.length === 0 ? (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">No training jobs yet</p>
                    <p className="text-sm text-muted-foreground">
                      Start your first training session
                    </p>
                  </div>
                ) : (
                  trainingJobs.map((job) => (
                    <div
                      key={job.job_id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors hover:bg-accent ${
                        selectedJob?.job_id === job.job_id ? 'bg-accent' : ''
                      }`}
                      onClick={() => setSelectedJob(job)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(job.status)}
                          <span className="font-medium text-sm">{job.name}</span>
                        </div>
                        {getStatusBadge(job.status)}
                      </div>
                      
                      {job.status === 'running' && (
                        <div className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span>Epoch {job.progress.current_epoch}/{job.progress.total_epochs}</span>
                            <span>{((job.progress.current_epoch / job.progress.total_epochs) * 100).toFixed(0)}%</span>
                          </div>
                          <Progress value={(job.progress.current_epoch / job.progress.total_epochs) * 100} className="h-1" />
                        </div>
                      )}
                      
                      <div className="flex justify-between text-xs text-muted-foreground mt-2">
                        <span>Acc: {(job.metrics.accuracy * 100).toFixed(1)}%</span>
                        <span>{formatDuration(job.start_time, job.end_time)}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-base">Training Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Total Jobs</span>
                  <span className="font-medium">{trainingJobs.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Running</span>
                  <span className="font-medium text-blue-600">
                    {trainingJobs.filter(j => j.status === 'running').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Completed</span>
                  <span className="font-medium text-green-600">
                    {trainingJobs.filter(j => j.status === 'completed').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Avg Accuracy</span>
                  <span className="font-medium">
                    {trainingJobs.length > 0 
                      ? (trainingJobs.reduce((acc, job) => acc + job.metrics.accuracy, 0) / trainingJobs.length * 100).toFixed(1) + '%'
                      : 'N/A'
                    }
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Job Details */}
        <div className="lg:col-span-2">
          {selectedJob ? (
            <Tabs defaultValue="progress" className="space-y-4">
              <TabsList>
                <TabsTrigger value="progress">Progress</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
                <TabsTrigger value="details">Details</TabsTrigger>
              </TabsList>

              <TabsContent value="progress" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{selectedJob.name}</span>
                      {getStatusBadge(selectedJob.status)}
                    </CardTitle>
                    <CardDescription>
                      Training progress and real-time metrics
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Progress Bar */}
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span>Training Progress</span>
                        <span>
                          Epoch {selectedJob.progress.current_epoch} of {selectedJob.progress.total_epochs}
                        </span>
                      </div>
                      <Progress 
                        value={(selectedJob.progress.current_epoch / selectedJob.progress.total_epochs) * 100} 
                        className="h-3"
                      />
                      <div className="text-center text-xs text-muted-foreground mt-1">
                        {((selectedJob.progress.current_epoch / selectedJob.progress.total_epochs) * 100).toFixed(1)}% Complete
                      </div>
                    </div>

                    {/* Current Metrics */}
                    <div className="grid grid-cols-2 gap-4">
                      <Card>
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-muted-foreground">Accuracy</p>
                              <p className="text-2xl font-bold text-green-600">
                                {(selectedJob.metrics.accuracy * 100).toFixed(1)}%
                              </p>
                            </div>
                            <TrendingUp className="h-8 w-8 text-green-600" />
                          </div>
                        </CardContent>
                      </Card>
                      
                      <Card>
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-muted-foreground">Loss</p>
                              <p className="text-2xl font-bold text-blue-600">
                                {selectedJob.metrics.loss.toFixed(3)}
                              </p>
                            </div>
                            <Target className="h-8 w-8 text-blue-600" />
                          </div>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Explanation */}
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <div className="flex items-start gap-3">
                        <Brain className="h-5 w-5 text-primary mt-0.5" />
                        <div>
                          <p className="font-medium text-sm mb-1">AI Explanation</p>
                          <p className="text-sm text-muted-foreground">
                            {selectedJob.explanation}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Duration */}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="font-medium">
                        {formatDuration(selectedJob.start_time, selectedJob.end_time)}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="metrics" className="space-y-4">
                {selectedJob.final_metrics ? (
                  <Card>
                    <CardHeader>
                      <CardTitle>Final Model Performance</CardTitle>
                      <CardDescription>
                        Comprehensive evaluation metrics
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-4">
                          <div className="text-center">
                            <div className="text-3xl font-bold text-green-600">
                              {(selectedJob.final_metrics.accuracy * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-muted-foreground">Accuracy</div>
                          </div>
                          <div className="text-center">
                            <div className="text-3xl font-bold text-blue-600">
                              {(selectedJob.final_metrics.auc * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-muted-foreground">AUC</div>
                          </div>
                        </div>
                        <div className="space-y-4">
                          <div className="text-center">
                            <div className="text-3xl font-bold text-purple-600">
                              {(selectedJob.final_metrics.precision * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-muted-foreground">Precision</div>
                          </div>
                          <div className="text-center">
                            <div className="text-3xl font-bold text-orange-600">
                              {(selectedJob.final_metrics.recall * 100).toFixed(1)}%
                            </div>
                            <div className="text-sm text-muted-foreground">Recall</div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="text-center py-8">
                      <Activity className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">
                        Final metrics will be available when training completes
                      </p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="details" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Job Configuration</CardTitle>
                    <CardDescription>
                      Training job settings and parameters
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium">Job ID</label>
                          <p className="text-sm text-muted-foreground font-mono">{selectedJob.job_id}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Pipeline ID</label>
                          <p className="text-sm text-muted-foreground font-mono">{selectedJob.pipeline_id}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Start Time</label>
                          <p className="text-sm text-muted-foreground">{selectedJob.start_time.toLocaleString()}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium">Status</label>
                          <p className="text-sm">{getStatusBadge(selectedJob.status)}</p>
                        </div>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium">Training Data</label>
                        <div className="mt-2 space-y-1">
                          {selectedJob.data_ids.map(dataId => (
                            <Badge key={dataId} variant="outline" className="mr-2">
                              {dataFiles.find(f => f.file_id === dataId)?.name || dataId}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {selectedJob.status === 'completed' && (
                        <div className="pt-4 border-t">
                          <Button className="w-full">
                            <Download className="mr-2 h-4 w-4" />
                            Download Model
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <Card>
              <CardContent className="text-center py-16">
                <Cpu className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">No Job Selected</p>
                <p className="text-muted-foreground mb-4">
                  Select a training job to view detailed progress and metrics
                </p>
                <Button onClick={() => setIsCreating(true)}>
                  <Play className="mr-2 h-4 w-4" />
                  Start New Training
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}