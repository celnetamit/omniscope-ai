'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Search,
  Filter,
  Download,
  Eye,
  BarChart3,
  Database,
  FileText,
  Calendar,
  User,
  Tag,
  TrendingUp,
  Trash2,
  RefreshCw
} from 'lucide-react';

interface DataFile {
  id: string;
  name: string;
  type: 'genomics' | 'proteomics' | 'metabolomics' | 'clinical';
  size: string;
  rows: number;
  columns: number;
  uploadDate: string;
  status: 'processed' | 'processing' | 'error';
  tags: string[];
}

interface Pipeline {
  id: string;
  name: string;
  project: string;
  nodes: number;
  status: 'active' | 'draft' | 'archived';
  lastModified: string;
  creator: string;
}

interface TrainingJob {
  id: string;
  name: string;
  model: string;
  status: 'completed' | 'running' | 'failed';
  accuracy: number;
  startTime: string;
  duration: string;
}

const mockDataFiles: DataFile[] = [
  {
    id: 'c27b62bf-26bd-4939-8d57-3bd2ef34ba53',
    name: 'genomics_expression.csv',
    type: 'genomics',
    size: '2.3 MB',
    rows: 15,
    columns: 9,
    uploadDate: '2024-11-06',
    status: 'processed',
    tags: ['RNA-seq', 'cancer', 'expression']
  },
  {
    id: 'd1d891a5-937e-42c1-9f01-7733b18a7f61',
    name: 'clinical_data_with_missing.csv',
    type: 'clinical',
    size: '1.1 MB',
    rows: 15,
    columns: 9,
    uploadDate: '2024-11-06',
    status: 'processed',
    tags: ['clinical', 'missing-values', 'patients']
  },
  {
    id: 'f8e9d2c1-4b5a-6789-0123-456789abcdef',
    name: 'proteomics_data.csv',
    type: 'proteomics',
    size: '3.7 MB',
    rows: 15,
    columns: 11,
    uploadDate: '2024-11-05',
    status: 'processed',
    tags: ['proteins', 'mass-spec', 'biomarkers']
  }
];

const mockPipelines: Pipeline[] = [
  {
    id: '634a9cf3-04a5-4c88-a448-a0cbe9f85670',
    name: 'Frontend Test Pipeline',
    project: 'frontend_test',
    nodes: 2,
    status: 'active',
    lastModified: '2024-11-06',
    creator: 'System'
  },
  {
    id: 'abc123-def456-ghi789',
    name: 'Multi-omics Integration',
    project: 'cancer_study',
    nodes: 7,
    status: 'draft',
    lastModified: '2024-11-05',
    creator: 'Dr. Smith'
  }
];

const mockTrainingJobs: TrainingJob[] = [
  {
    id: 'a469f275-3b36-4dd2-8b4e-5ff4cdc9a49e',
    name: 'Cancer Classification Model',
    model: 'XGBoost',
    status: 'completed',
    accuracy: 0.95,
    startTime: '2024-11-06 14:00',
    duration: '12s'
  },
  {
    id: 'xyz789-abc123-def456',
    name: 'Biomarker Discovery',
    model: 'Random Forest',
    status: 'running',
    accuracy: 0.87,
    startTime: '2024-11-06 15:30',
    duration: '5m 23s'
  }
];

export function DataExplorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
      case 'completed':
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'processing':
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'error':
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
      case 'draft':
      case 'archived':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'genomics':
        return '🧬';
      case 'proteomics':
        return '🧪';
      case 'metabolomics':
        return '⚗️';
      case 'clinical':
        return '🏥';
      default:
        return '📄';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Data Explorer</h1>
          <p className="text-muted-foreground">
            Browse, search, and manage your datasets, pipelines, and models
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button>
            <Download className="mr-2 h-4 w-4" />
            Export All
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search datasets, pipelines, or models..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Data Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="genomics">Genomics</SelectItem>
                <SelectItem value="proteomics">Proteomics</SelectItem>
                <SelectItem value="metabolomics">Metabolomics</SelectItem>
                <SelectItem value="clinical">Clinical</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="processed">Processed</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="datasets" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="datasets">Datasets</TabsTrigger>
          <TabsTrigger value="pipelines">Pipelines</TabsTrigger>
          <TabsTrigger value="models">Models</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Datasets Tab */}
        <TabsContent value="datasets" className="space-y-4">
          <div className="grid gap-4">
            {mockDataFiles.map((file) => (
              <Card key={file.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="text-2xl">{getTypeIcon(file.type)}</div>
                      <div>
                        <h3 className="font-semibold">{file.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{file.size}</span>
                          <span>{file.rows} rows × {file.columns} columns</span>
                          <span>{file.uploadDate}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge className={getStatusColor(file.status)}>
                            {file.status}
                          </Badge>
                          {file.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="mr-2 h-4 w-4" />
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        <BarChart3 className="mr-2 h-4 w-4" />
                        Analyze
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="mr-2 h-4 w-4" />
                        Export
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Pipelines Tab */}
        <TabsContent value="pipelines" className="space-y-4">
          <div className="grid gap-4">
            {mockPipelines.map((pipeline) => (
              <Card key={pipeline.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900">
                        <Database className="h-5 w-5 text-blue-600 dark:text-blue-300" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{pipeline.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>Project: {pipeline.project}</span>
                          <span>{pipeline.nodes} nodes</span>
                          <span>Modified: {pipeline.lastModified}</span>
                          <span>By: {pipeline.creator}</span>
                        </div>
                        <div className="mt-2">
                          <Badge className={getStatusColor(pipeline.status)}>
                            {pipeline.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="mr-2 h-4 w-4" />
                        Open
                      </Button>
                      <Button variant="outline" size="sm">
                        <FileText className="mr-2 h-4 w-4" />
                        Duplicate
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models" className="space-y-4">
          <div className="grid gap-4">
            {mockTrainingJobs.map((job) => (
              <Card key={job.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900">
                        <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-300" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{job.name}</h3>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>Model: {job.model}</span>
                          <span>Accuracy: {(job.accuracy * 100).toFixed(1)}%</span>
                          <span>Started: {job.startTime}</span>
                          <span>Duration: {job.duration}</span>
                        </div>
                        <div className="mt-2">
                          <Badge className={getStatusColor(job.status)}>
                            {job.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="mr-2 h-4 w-4" />
                        Results
                      </Button>
                      <Button variant="outline" size="sm">
                        <BarChart3 className="mr-2 h-4 w-4" />
                        Metrics
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="mr-2 h-4 w-4" />
                        Export
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Datasets</CardTitle>
                <Database className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24</div>
                <p className="text-xs text-muted-foreground">
                  +3 from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Pipelines</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">
                  +2 from last week
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Trained Models</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8</div>
                <p className="text-xs text-muted-foreground">
                  +1 from yesterday
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. Accuracy</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">94.2%</div>
                <p className="text-xs text-muted-foreground">
                  +2.1% from last month
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest actions across all modules
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Training job completed</p>
                    <p className="text-xs text-muted-foreground">Cancer Classification Model - 95% accuracy</p>
                  </div>
                  <span className="text-xs text-muted-foreground">2 min ago</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 rounded-full bg-blue-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Dataset uploaded</p>
                    <p className="text-xs text-muted-foreground">genomics_expression.csv processed successfully</p>
                  </div>
                  <span className="text-xs text-muted-foreground">15 min ago</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 rounded-full bg-purple-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Pipeline created</p>
                    <p className="text-xs text-muted-foreground">Multi-omics Integration pipeline saved</p>
                  </div>
                  <span className="text-xs text-muted-foreground">1 hour ago</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}