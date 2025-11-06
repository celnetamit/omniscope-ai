'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
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
  Upload,
  FileText,
  CheckCircle,
  AlertCircle,
  Clock,
  Download,
  Eye,
  Trash2,
  RefreshCw,
  BarChart3,
  Database,
  FileSpreadsheet
} from 'lucide-react';
import { useDropzone } from 'react-dropzone';

interface UploadedFile {
  file_id: string;
  name: string;
  status: 'processing' | 'complete' | 'error';
  message: string;
  report?: {
    summary: {
      filename: string;
      rows: number;
      columns: number;
      duplicates: number;
    };
    findings: Array<{
      type: string;
      severity: string;
      description: string;
    }>;
    recommendations: Array<{
      action: string;
      target_column: string;
      suggestion: string;
      reasoning: string;
    }>;
    data_types: Record<string, string>;
    missing_values: Record<string, number>;
  };
  uploadTime: Date;
}

export function DataHarbor() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      await handleFileUpload(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/proxy?url=/api/data/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      const newFile: UploadedFile = {
        file_id: data.file_id,
        name: file.name,
        status: 'processing',
        message: data.message,
        uploadTime: new Date()
      };

      setUploadedFiles(prev => [...prev, newFile]);
      
      // Poll for analysis results
      pollFileAnalysis(data.file_id);
    } catch (error) {
      console.error('Failed to upload file:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const pollFileAnalysis = async (fileId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/proxy?url=/api/data/${fileId}/report`);
        const data = await response.json();
        
        setUploadedFiles(prev => prev.map(file => 
          file.file_id === fileId 
            ? { ...file, status: data.status, message: data.message, report: data.report }
            : file
        ));
        
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
      case 'complete':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive'> = {
      'complete': 'default',
      'processing': 'secondary',
      'error': 'destructive',
    };
    
    return (
      <Badge variant={variants[status] || 'secondary'}>
        {status}
      </Badge>
    );
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Upload className="h-8 w-8" />
            Data Harbor
          </h1>
          <p className="text-muted-foreground">
            Upload and analyze your datasets with automated quality assessment
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.location.reload()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Upload Section */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Upload Dataset</CardTitle>
              <CardDescription>
                Drag and drop files or click to browse
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive 
                    ? 'border-primary bg-primary/5' 
                    : 'border-muted-foreground/25 hover:border-primary/50'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                {isDragActive ? (
                  <p className="text-primary">Drop the files here...</p>
                ) : (
                  <div>
                    <p className="text-lg font-medium mb-2">Drop files here</p>
                    <p className="text-sm text-muted-foreground mb-4">
                      or click to select files
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Supports CSV, Excel files up to 10MB
                    </p>
                  </div>
                )}
              </div>
              
              {isUploading && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-4 w-4 animate-pulse" />
                    <span className="text-sm">Uploading...</span>
                  </div>
                  <Progress value={undefined} className="w-full" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-base">Upload Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Total Files</span>
                  <span className="font-medium">{uploadedFiles.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Completed</span>
                  <span className="font-medium text-green-600">
                    {uploadedFiles.filter(f => f.status === 'complete').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Processing</span>
                  <span className="font-medium text-blue-600">
                    {uploadedFiles.filter(f => f.status === 'processing').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Errors</span>
                  <span className="font-medium text-red-600">
                    {uploadedFiles.filter(f => f.status === 'error').length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Files List and Analysis */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="files" className="space-y-4">
            <TabsList>
              <TabsTrigger value="files">Uploaded Files</TabsTrigger>
              <TabsTrigger value="analysis">Analysis Report</TabsTrigger>
            </TabsList>

            <TabsContent value="files" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Your Datasets</CardTitle>
                  <CardDescription>
                    Manage and view analysis results for your uploaded files
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {uploadedFiles.length === 0 ? (
                    <div className="text-center py-8">
                      <Database className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                      <p className="text-muted-foreground">No files uploaded yet</p>
                      <p className="text-sm text-muted-foreground">
                        Upload your first dataset to get started
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {uploadedFiles.map((file) => (
                        <div
                          key={file.file_id}
                          className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                          onClick={() => setSelectedFile(file)}
                        >
                          <div className="flex items-center gap-3">
                            <FileSpreadsheet className="h-8 w-8 text-green-600" />
                            <div>
                              <p className="font-medium">{file.name}</p>
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <span>{file.uploadTime.toLocaleString()}</span>
                                {file.report && (
                                  <>
                                    <span>•</span>
                                    <span>{file.report.summary.rows} rows</span>
                                    <span>•</span>
                                    <span>{file.report.summary.columns} columns</span>
                                  </>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {getStatusIcon(file.status)}
                            {getStatusBadge(file.status)}
                            {file.status === 'complete' && (
                              <Button variant="outline" size="sm">
                                <Eye className="mr-2 h-4 w-4" />
                                View Report
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analysis" className="space-y-4">
              {selectedFile && selectedFile.report ? (
                <div className="space-y-4">
                  {/* Summary Card */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Dataset Summary</CardTitle>
                      <CardDescription>{selectedFile.name}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">
                            {selectedFile.report.summary.rows}
                          </div>
                          <div className="text-sm text-muted-foreground">Rows</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {selectedFile.report.summary.columns}
                          </div>
                          <div className="text-sm text-muted-foreground">Columns</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-orange-600">
                            {selectedFile.report.summary.duplicates}
                          </div>
                          <div className="text-sm text-muted-foreground">Duplicates</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">
                            {Object.values(selectedFile.report.missing_values).filter(v => v > 0).length}
                          </div>
                          <div className="text-sm text-muted-foreground">Missing Cols</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Data Types */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Data Types</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Column</TableHead>
                            <TableHead>Data Type</TableHead>
                            <TableHead>Missing %</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {Object.entries(selectedFile.report.data_types).map(([column, type]) => (
                            <TableRow key={column}>
                              <TableCell className="font-medium">{column}</TableCell>
                              <TableCell>
                                <Badge variant="outline">{type}</Badge>
                              </TableCell>
                              <TableCell>
                                <span className={selectedFile.report!.missing_values[column] > 0 ? 'text-red-600' : 'text-green-600'}>
                                  {selectedFile.report!.missing_values[column].toFixed(1)}%
                                </span>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>

                  {/* Findings */}
                  {selectedFile.report.findings.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Quality Assessment</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {selectedFile.report.findings.map((finding, index) => (
                            <Alert key={index}>
                              <AlertCircle className="h-4 w-4" />
                              <AlertDescription>
                                <div className="flex items-center justify-between">
                                  <span>{finding.description}</span>
                                  <Badge className={getSeverityColor(finding.severity)}>
                                    {finding.severity}
                                  </Badge>
                                </div>
                              </AlertDescription>
                            </Alert>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Recommendations */}
                  {selectedFile.report.recommendations.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Recommendations</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {selectedFile.report.recommendations.map((rec, index) => (
                            <div key={index} className="p-4 border rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium">{rec.suggestion}</h4>
                                <Badge variant="outline">{rec.target_column}</Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">{rec.reasoning}</p>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <Card>
                  <CardContent className="text-center py-8">
                    <BarChart3 className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">Select a completed file to view analysis</p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}