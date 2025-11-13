"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Server, Cpu, HardDrive, Activity, RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface WorkerNode {
  id: string;
  status: "active" | "idle" | "offline";
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  tasks_running: number;
  tasks_completed: number;
  last_heartbeat: string;
}

interface ClusterStatus {
  scheduler_status: "running" | "stopped";
  total_workers: number;
  active_workers: number;
  total_tasks: number;
  running_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  workers: WorkerNode[];
}

interface ClusterStatusDisplayProps {
  refreshInterval?: number;
}

export function ClusterStatusDisplay({ refreshInterval = 5000 }: ClusterStatusDisplayProps) {
  const [status, setStatus] = useState<ClusterStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchClusterStatus = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/processing/cluster/status`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      } else {
        toast.error("Failed to fetch cluster status");
      }
    } catch (error) {
      console.error("Error fetching cluster status:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusterStatus();
    const interval = setInterval(fetchClusterStatus, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
      case "running":
        return "bg-green-500";
      case "idle":
        return "bg-yellow-500";
      case "offline":
      case "stopped":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusBadge = (status: string) => {
    const variant =
      status === "active" || status === "running"
        ? "default"
        : status === "idle"
        ? "secondary"
        : "destructive";
    return (
      <Badge variant={variant} className="capitalize">
        {status}
      </Badge>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[400px]">
          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground">No cluster data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Cluster Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Cluster Status
              </CardTitle>
              <CardDescription>Distributed processing cluster overview</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {getStatusBadge(status.scheduler_status)}
              <Button variant="ghost" size="icon" onClick={fetchClusterStatus}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <p className="text-3xl font-bold">{status.total_workers}</p>
              <p className="text-sm text-muted-foreground">Total Workers</p>
            </div>
            <div className="text-center p-4 border rounded-lg bg-green-50 dark:bg-green-950">
              <p className="text-3xl font-bold text-green-600">{status.active_workers}</p>
              <p className="text-sm text-muted-foreground">Active Workers</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <p className="text-3xl font-bold">{status.running_tasks}</p>
              <p className="text-sm text-muted-foreground">Running Tasks</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <p className="text-3xl font-bold">{status.completed_tasks}</p>
              <p className="text-sm text-muted-foreground">Completed Tasks</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Worker Nodes */}
      <Card>
        <CardHeader>
          <CardTitle>Worker Nodes</CardTitle>
          <CardDescription>Individual worker node status and resource usage</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {status.workers.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No worker nodes available
              </div>
            ) : (
              status.workers.map((worker) => (
                <div key={worker.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-3 w-3 rounded-full ${getStatusColor(worker.status)}`}
                      />
                      <div>
                        <h4 className="font-medium">Worker {worker.id}</h4>
                        <p className="text-xs text-muted-foreground">
                          Last seen: {new Date(worker.last_heartbeat).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="text-center">
                        <p className="font-medium">{worker.tasks_running}</p>
                        <p className="text-xs text-muted-foreground">Running</p>
                      </div>
                      <div className="text-center">
                        <p className="font-medium">{worker.tasks_completed}</p>
                        <p className="text-xs text-muted-foreground">Completed</p>
                      </div>
                    </div>
                  </div>

                  {/* Resource Usage */}
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Cpu className="h-4 w-4 text-muted-foreground" />
                          <span>CPU</span>
                        </div>
                        <span className="font-medium">{worker.cpu_usage.toFixed(1)}%</span>
                      </div>
                      <Progress value={worker.cpu_usage} className="h-2" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Activity className="h-4 w-4 text-muted-foreground" />
                          <span>Memory</span>
                        </div>
                        <span className="font-medium">{worker.memory_usage.toFixed(1)}%</span>
                      </div>
                      <Progress value={worker.memory_usage} className="h-2" />
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <HardDrive className="h-4 w-4 text-muted-foreground" />
                          <span>Disk</span>
                        </div>
                        <span className="font-medium">{worker.disk_usage.toFixed(1)}%</span>
                      </div>
                      <Progress value={worker.disk_usage} className="h-2" />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
