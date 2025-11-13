"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, CheckCircle2, XCircle, Clock, TrendingUp, TrendingDown } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface TrainingMetrics {
  epoch: number;
  train_loss: number;
  val_loss?: number;
  train_accuracy?: number;
  val_accuracy?: number;
  learning_rate?: number;
}

interface TrainingJob {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  current_epoch?: number;
  total_epochs?: number;
  metrics: TrainingMetrics[];
  best_metric?: number;
  elapsed_time?: number;
  estimated_time_remaining?: number;
  logs: string[];
}

interface TrainingProgressProps {
  job: TrainingJob;
  onCancel?: () => void;
  onViewResults?: () => void;
}

export function TrainingProgress({ job, onCancel, onViewResults }: TrainingProgressProps) {
  const [autoScroll, setAutoScroll] = useState(true);

  const getStatusIcon = () => {
    switch (job.status) {
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case "running":
        return <Activity className="h-5 w-5 text-blue-500 animate-pulse" />;
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusColor = () => {
    switch (job.status) {
      case "pending":
        return "bg-yellow-500";
      case "running":
        return "bg-blue-500";
      case "completed":
        return "bg-green-500";
      case "failed":
        return "bg-red-500";
    }
  };

  const formatTime = (seconds?: number) => {
    if (!seconds) return "N/A";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  const latestMetrics = job.metrics[job.metrics.length - 1];
  const isImproving =
    job.metrics.length > 1 &&
    latestMetrics?.val_loss &&
    job.metrics[job.metrics.length - 2]?.val_loss &&
    latestMetrics.val_loss < job.metrics[job.metrics.length - 2].val_loss;

  return (
    <div className="space-y-4">
      {/* Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getStatusIcon()}
              <div>
                <CardTitle>Training Job: {job.id}</CardTitle>
                <CardDescription className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className="capitalize">
                    {job.status}
                  </Badge>
                  {job.current_epoch && job.total_epochs && (
                    <span className="text-sm">
                      Epoch {job.current_epoch} / {job.total_epochs}
                    </span>
                  )}
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-2">
              {job.status === "running" && onCancel && (
                <Button variant="outline" size="sm" onClick={onCancel}>
                  Cancel
                </Button>
              )}
              {job.status === "completed" && onViewResults && (
                <Button size="sm" onClick={onViewResults}>
                  View Results
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{job.progress}%</span>
            </div>
            <Progress value={job.progress} className={getStatusColor()} />
          </div>

          {/* Time Information */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Elapsed Time</p>
              <p className="font-medium">{formatTime(job.elapsed_time)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Est. Remaining</p>
              <p className="font-medium">{formatTime(job.estimated_time_remaining)}</p>
            </div>
          </div>

          {/* Current Metrics */}
          {latestMetrics && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
              {latestMetrics.train_loss !== undefined && (
                <div>
                  <p className="text-xs text-muted-foreground">Train Loss</p>
                  <p className="text-lg font-semibold">
                    {latestMetrics.train_loss.toFixed(4)}
                  </p>
                </div>
              )}
              {latestMetrics.val_loss !== undefined && (
                <div>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    Val Loss
                    {isImproving ? (
                      <TrendingDown className="h-3 w-3 text-green-500" />
                    ) : (
                      <TrendingUp className="h-3 w-3 text-red-500" />
                    )}
                  </p>
                  <p className="text-lg font-semibold">
                    {latestMetrics.val_loss.toFixed(4)}
                  </p>
                </div>
              )}
              {latestMetrics.train_accuracy !== undefined && (
                <div>
                  <p className="text-xs text-muted-foreground">Train Acc</p>
                  <p className="text-lg font-semibold">
                    {(latestMetrics.train_accuracy * 100).toFixed(2)}%
                  </p>
                </div>
              )}
              {latestMetrics.val_accuracy !== undefined && (
                <div>
                  <p className="text-xs text-muted-foreground">Val Acc</p>
                  <p className="text-lg font-semibold">
                    {(latestMetrics.val_accuracy * 100).toFixed(2)}%
                  </p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Metrics Chart */}
      {job.metrics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Training Metrics</CardTitle>
            <CardDescription>Loss and accuracy over epochs</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={job.metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="epoch" label={{ value: "Epoch", position: "insideBottom", offset: -5 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="train_loss"
                  stroke="#8884d8"
                  name="Train Loss"
                  strokeWidth={2}
                />
                {job.metrics.some((m) => m.val_loss !== undefined) && (
                  <Line
                    type="monotone"
                    dataKey="val_loss"
                    stroke="#82ca9d"
                    name="Val Loss"
                    strokeWidth={2}
                  />
                )}
                {job.metrics.some((m) => m.train_accuracy !== undefined) && (
                  <Line
                    type="monotone"
                    dataKey="train_accuracy"
                    stroke="#ffc658"
                    name="Train Accuracy"
                    strokeWidth={2}
                  />
                )}
                {job.metrics.some((m) => m.val_accuracy !== undefined) && (
                  <Line
                    type="monotone"
                    dataKey="val_accuracy"
                    stroke="#ff7c7c"
                    name="Val Accuracy"
                    strokeWidth={2}
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Training Logs */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Training Logs</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setAutoScroll(!autoScroll)}
            >
              Auto-scroll: {autoScroll ? "On" : "Off"}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[200px] w-full rounded-md border p-4">
            <div className="space-y-1 font-mono text-xs">
              {job.logs.length === 0 ? (
                <p className="text-muted-foreground">No logs yet...</p>
              ) : (
                job.logs.map((log, index) => (
                  <div key={index} className="text-muted-foreground">
                    {log}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
