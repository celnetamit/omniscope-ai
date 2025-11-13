"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import {
  Clock,
  Play,
  CheckCircle2,
  XCircle,
  Pause,
  RefreshCw,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";

interface Job {
  id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed" | "paused";
  priority: number;
  progress: number;
  submitted_at: string;
  started_at?: string;
  completed_at?: string;
  estimated_time_remaining?: number;
  worker_id?: string;
}

interface JobQueueVisualizationProps {
  refreshInterval?: number;
}

export function JobQueueVisualization({ refreshInterval = 3000 }: JobQueueVisualizationProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/processing/jobs`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setJobs(data);
      }
    } catch (error) {
      console.error("Error fetching jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const cancelJob = async (jobId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/processing/job/${jobId}/cancel`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        toast.success("Job cancelled");
        fetchJobs();
      } else {
        toast.error("Failed to cancel job");
      }
    } catch (error) {
      console.error("Error cancelling job:", error);
      toast.error("Failed to cancel job");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case "running":
        return <Play className="h-4 w-4 text-blue-500" />;
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "paused":
        return <Pause className="h-4 w-4 text-gray-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      pending: "secondary",
      running: "default",
      completed: "default",
      failed: "destructive",
      paused: "outline",
    };
    return (
      <Badge variant={variants[status] || "outline"} className="capitalize">
        {status}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: number) => {
    if (priority >= 8) return <Badge variant="destructive">High</Badge>;
    if (priority >= 5) return <Badge variant="default">Medium</Badge>;
    return <Badge variant="secondary">Low</Badge>;
  };

  const formatTime = (seconds?: number) => {
    if (!seconds) return "N/A";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const pendingJobs = jobs.filter((j) => j.status === "pending");
  const runningJobs = jobs.filter((j) => j.status === "running");
  const completedJobs = jobs.filter((j) => j.status === "completed");
  const failedJobs = jobs.filter((j) => j.status === "failed");

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Job Queue</CardTitle>
            <CardDescription>Processing jobs and their current status</CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={fetchJobs}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3 border rounded-lg bg-yellow-50 dark:bg-yellow-950">
            <p className="text-2xl font-bold text-yellow-600">{pendingJobs.length}</p>
            <p className="text-xs text-muted-foreground">Pending</p>
          </div>
          <div className="text-center p-3 border rounded-lg bg-blue-50 dark:bg-blue-950">
            <p className="text-2xl font-bold text-blue-600">{runningJobs.length}</p>
            <p className="text-xs text-muted-foreground">Running</p>
          </div>
          <div className="text-center p-3 border rounded-lg bg-green-50 dark:bg-green-950">
            <p className="text-2xl font-bold text-green-600">{completedJobs.length}</p>
            <p className="text-xs text-muted-foreground">Completed</p>
          </div>
          <div className="text-center p-3 border rounded-lg bg-red-50 dark:bg-red-950">
            <p className="text-2xl font-bold text-red-600">{failedJobs.length}</p>
            <p className="text-xs text-muted-foreground">Failed</p>
          </div>
        </div>

        {/* Job List */}
        <ScrollArea className="h-[500px]">
          <div className="space-y-3">
            {jobs.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No jobs in queue
              </div>
            ) : (
              jobs.map((job) => (
                <div key={job.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3 flex-1">
                      {getStatusIcon(job.status)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{job.name}</h4>
                          {getStatusBadge(job.status)}
                          {getPriorityBadge(job.priority)}
                        </div>
                        <p className="text-xs text-muted-foreground">Job ID: {job.id}</p>
                        {job.worker_id && (
                          <p className="text-xs text-muted-foreground">
                            Worker: {job.worker_id}
                          </p>
                        )}
                      </div>
                    </div>
                    {(job.status === "pending" || job.status === "running") && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => cancelJob(job.id)}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>

                  {/* Progress Bar */}
                  {job.status === "running" && (
                    <div className="space-y-1 mb-3">
                      <div className="flex items-center justify-between text-sm">
                        <span>Progress</span>
                        <span className="font-medium">{job.progress}%</span>
                      </div>
                      <Progress value={job.progress} />
                    </div>
                  )}

                  {/* Timing Information */}
                  <div className="grid grid-cols-3 gap-4 text-xs">
                    <div>
                      <p className="text-muted-foreground">Submitted</p>
                      <p className="font-medium">
                        {new Date(job.submitted_at).toLocaleTimeString()}
                      </p>
                    </div>
                    {job.started_at && (
                      <div>
                        <p className="text-muted-foreground">Started</p>
                        <p className="font-medium">
                          {new Date(job.started_at).toLocaleTimeString()}
                        </p>
                      </div>
                    )}
                    {job.completed_at && (
                      <div>
                        <p className="text-muted-foreground">Completed</p>
                        <p className="font-medium">
                          {new Date(job.completed_at).toLocaleTimeString()}
                        </p>
                      </div>
                    )}
                    {job.estimated_time_remaining && (
                      <div>
                        <p className="text-muted-foreground">Est. Remaining</p>
                        <p className="font-medium">
                          {formatTime(job.estimated_time_remaining)}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
