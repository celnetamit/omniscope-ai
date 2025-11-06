'use client';

import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/header';
import { HelpCenter } from '@/components/help/help-center';
import { DataExplorer } from '@/components/data-explorer/data-explorer';
import { Settings } from '@/components/settings/settings';
import { DataHarbor } from '@/components/modules/data-harbor';
import { TheWeaver } from '@/components/modules/the-weaver';
import { TheCrucible } from '@/components/modules/the-crucible';
import { InsightEngine } from '@/components/modules/insight-engine';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  GitBranch, 
  Cpu, 
  Brain, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  FileText,
  BarChart3,
  MessageSquare,
  TrendingUp,
  Activity,
  Users,
  Database
} from 'lucide-react';

interface ModuleInfo {
  status: string;
  description: string;
  storage?: string;
  supported_formats?: string[];
  max_file_size?: string;
  features?: string[];
}

interface ModuleStatus {
  data_harbor: ModuleInfo;
  the_weaver: ModuleInfo;
  the_crucible: ModuleInfo;
  the_insight_engine: ModuleInfo;
}

interface FileUpload {
  file_id: string;
  status: string;
  message: string;
}

interface Pipeline {
  pipeline_id: string;
  name: string;
  project_id: string;
}

interface TrainingJob {
  job_id: string;
  status: string;
  progress: { current_epoch: number; total_epochs: number };
  metrics: { accuracy: number; loss: number };
  explanation: string;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [moduleStatus, setModuleStatus] = useState<ModuleStatus | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileUpload, setFileUpload] = useState<FileUpload | null>(null);
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch module status on component mount
  useEffect(() => {
    fetchModuleStatus();
    fetchPipelines();
    fetchTrainingJobs();
    
    // Set up polling for training jobs
    const interval = setInterval(fetchTrainingJobs, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchModuleStatus = async () => {
    try {
      const response = await fetch('/api/proxy?url=/api/modules/status');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setModuleStatus(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch module status:', error);
      // Set fallback data to prevent rendering errors
      setModuleStatus({
        data_harbor: { status: 'unknown', description: 'Connection failed' },
        the_weaver: { status: 'unknown', description: 'Connection failed' },
        the_crucible: { status: 'unknown', description: 'Connection failed' },
        the_insight_engine: { status: 'unknown', description: 'Connection failed' }
      });
      setLoading(false);
    }
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

  const fetchTrainingJobs = async () => {
    try {
      // This would normally fetch from a jobs endpoint
      // For now, we'll simulate with mock data
      const mockJobs: TrainingJob[] = [
        {
          job_id: 'job_001',
          status: 'completed',
          progress: { current_epoch: 10, total_epochs: 10 },
          metrics: { accuracy: 0.92, loss: 0.15 },
          explanation: 'Training complete. The model has finished learning and is ready for evaluation.'
        }
      ];
      setTrainingJobs(mockJobs);
    } catch (error) {
      console.error('Failed to fetch training jobs:', error);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/proxy?url=/api/data/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setFileUpload(data);
      
      // Poll for file analysis results
      if (data.file_id) {
        pollFileAnalysis(data.file_id);
      }
    } catch (error) {
      console.error('Failed to upload file:', error);
    }
  };

  const pollFileAnalysis = async (fileId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/proxy?url=/api/data/${fileId}/report`);
        const data = await response.json();
        
        setFileUpload(data);
        
        if (data.status === 'complete' || data.status === 'error') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Failed to poll file analysis:', error);
        clearInterval(pollInterval);
      }
    }, 2000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'complete':
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running':
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'error':
      case 'failed':
      case 'unknown':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      'completed': 'default',
      'complete': 'default',
      'running': 'secondary',
      'processing': 'secondary',
      'error': 'destructive',
      'failed': 'destructive',
    };
    
    return (
      <Badge variant={variants[status] || 'outline'}>
        {status}
      </Badge>
    );
  };

  // Dashboard Component
  const DashboardContent = () => (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold">Welcome to OmniScope AI</h1>
        <p className="text-xl text-muted-foreground">
          Multi-Omics Data Analysis Platform
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Datasets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              +2 from yesterday
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Jobs</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              2 training, 1 analysis
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Accuracy</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <p className="text-xs text-muted-foreground">
              +2.1% from last week
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">
              +1 from last month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Module Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5" />
            Module Status
          </CardTitle>
          <CardDescription>
            Real-time status of all integrated modules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {moduleStatus && Object.entries(moduleStatus).map(([module, info]) => (
              <div key={module} className="flex items-center gap-2 p-3 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                   onClick={() => {
                     const moduleMap: Record<string, string> = {
                       'data_harbor': 'data-harbor',
                       'the_weaver': 'the-weaver', 
                       'the_crucible': 'the-crucible',
                       'the_insight_engine': 'insight-engine'
                     };
                     setActiveTab(moduleMap[module] || module);
                   }}>
                {getStatusIcon(info.status)}
                <div>
                  <p className="font-medium capitalize">
                    {module.replace('_', ' ')}
                  </p>
                  <p className="text-sm text-muted-foreground">{info.status}</p>
                  <p className="text-xs text-muted-foreground">{info.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest updates across all modules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">Training job completed successfully</p>
                <p className="text-xs text-muted-foreground">Cancer Classification Model achieved 95% accuracy</p>
              </div>
              <span className="text-xs text-muted-foreground">2 min ago</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">New dataset uploaded</p>
                <p className="text-xs text-muted-foreground">genomics_expression.csv processed and analyzed</p>
              </div>
              <span className="text-xs text-muted-foreground">15 min ago</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-2 h-2 rounded-full bg-purple-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">Pipeline created</p>
                <p className="text-xs text-muted-foreground">Multi-omics Integration pipeline saved to project</p>
              </div>
              <span className="text-xs text-muted-foreground">1 hour ago</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Cpu className="h-12 w-12 animate-spin mx-auto mb-4" />
          <p>Loading OmniScope AI...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      
      <div className="lg:pl-72">
        <main className="p-6">
          {activeTab === 'dashboard' && <DashboardContent />}
          {activeTab === 'help' && <HelpCenter />}
          {activeTab === 'data-explorer' && <DataExplorer />}
          {activeTab === 'settings' && <Settings />}
          {activeTab === 'reports' && (
            <div className="text-center py-12">
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-2xl font-bold mb-2">Reports Module</h2>
              <p className="text-muted-foreground">Coming soon - Generate and export analysis reports</p>
            </div>
          )}
          {activeTab === 'analytics' && (
            <div className="text-center py-12">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-2xl font-bold mb-2">Analytics Module</h2>
              <p className="text-muted-foreground">Coming soon - Advanced analytics and insights</p>
            </div>
          )}
          
          {/* Functional Modules */}
          {activeTab === 'data-harbor' && <DataHarbor />}
          {activeTab === 'the-weaver' && <TheWeaver />}
          {activeTab === 'the-crucible' && <TheCrucible />}
          {activeTab === 'insight-engine' && <InsightEngine />}
        </main>
      </div>
    </div>
  );
}