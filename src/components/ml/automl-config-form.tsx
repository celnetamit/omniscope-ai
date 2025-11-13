"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Sparkles } from "lucide-react";
import { toast } from "sonner";

interface AutoMLConfig {
  dataset_id: string;
  target_column: string;
  feature_columns: string[];
  task_type: "classification" | "regression";
  time_limit: number;
  quality_preset: "best_quality" | "high_quality" | "good_quality" | "medium_quality";
  enable_ensemble: boolean;
  eval_metric?: string;
}

interface AutoMLConfigFormProps {
  datasets: Array<{ id: string; name: string; columns: string[] }>;
  onSubmit: (config: AutoMLConfig) => void;
  loading?: boolean;
}

export function AutoMLConfigForm({ datasets, onSubmit, loading = false }: AutoMLConfigFormProps) {
  const [config, setConfig] = useState<AutoMLConfig>({
    dataset_id: "",
    target_column: "",
    feature_columns: [],
    task_type: "classification",
    time_limit: 600,
    quality_preset: "good_quality",
    enable_ensemble: true,
  });

  const selectedDataset = datasets.find((d) => d.id === config.dataset_id);
  const availableColumns = selectedDataset?.columns || [];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!config.dataset_id) {
      toast.error("Please select a dataset");
      return;
    }
    if (!config.target_column) {
      toast.error("Please select a target column");
      return;
    }
    if (config.feature_columns.length === 0) {
      toast.error("Please select at least one feature column");
      return;
    }

    onSubmit(config);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          AutoML Configuration
        </CardTitle>
        <CardDescription>
          Configure automated machine learning to find the best model for your data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Dataset Selection */}
          <div className="space-y-2">
            <Label htmlFor="dataset">Dataset</Label>
            <Select
              value={config.dataset_id}
              onValueChange={(value) => {
                setConfig({
                  ...config,
                  dataset_id: value,
                  target_column: "",
                  feature_columns: [],
                });
              }}
            >
              <SelectTrigger id="dataset">
                <SelectValue placeholder="Select a dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map((dataset) => (
                  <SelectItem key={dataset.id} value={dataset.id}>
                    {dataset.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Task Type */}
          <div className="space-y-2">
            <Label htmlFor="task-type">Task Type</Label>
            <Select
              value={config.task_type}
              onValueChange={(value: "classification" | "regression") =>
                setConfig({ ...config, task_type: value })
              }
            >
              <SelectTrigger id="task-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="classification">Classification</SelectItem>
                <SelectItem value="regression">Regression</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Target Column */}
          <div className="space-y-2">
            <Label htmlFor="target">Target Column</Label>
            <Select
              value={config.target_column}
              onValueChange={(value) => setConfig({ ...config, target_column: value })}
              disabled={!config.dataset_id}
            >
              <SelectTrigger id="target">
                <SelectValue placeholder="Select target column" />
              </SelectTrigger>
              <SelectContent>
                {availableColumns.map((col) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Feature Columns */}
          <div className="space-y-2">
            <Label>Feature Columns</Label>
            <div className="border rounded-md p-3 max-h-40 overflow-y-auto space-y-2">
              {availableColumns
                .filter((col) => col !== config.target_column)
                .map((col) => (
                  <div key={col} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`feature-${col}`}
                      checked={config.feature_columns.includes(col)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setConfig({
                            ...config,
                            feature_columns: [...config.feature_columns, col],
                          });
                        } else {
                          setConfig({
                            ...config,
                            feature_columns: config.feature_columns.filter((c) => c !== col),
                          });
                        }
                      }}
                      className="rounded"
                    />
                    <label htmlFor={`feature-${col}`} className="text-sm cursor-pointer">
                      {col}
                    </label>
                  </div>
                ))}
            </div>
          </div>

          {/* Quality Preset */}
          <div className="space-y-2">
            <Label htmlFor="quality">Quality Preset</Label>
            <Select
              value={config.quality_preset}
              onValueChange={(value: any) => setConfig({ ...config, quality_preset: value })}
            >
              <SelectTrigger id="quality">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="best_quality">Best Quality (Slowest)</SelectItem>
                <SelectItem value="high_quality">High Quality</SelectItem>
                <SelectItem value="good_quality">Good Quality</SelectItem>
                <SelectItem value="medium_quality">Medium Quality (Fastest)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Time Limit */}
          <div className="space-y-2">
            <Label htmlFor="time-limit">
              Time Limit: {Math.floor(config.time_limit / 60)} minutes
            </Label>
            <Slider
              id="time-limit"
              min={60}
              max={3600}
              step={60}
              value={[config.time_limit]}
              onValueChange={([value]) => setConfig({ ...config, time_limit: value })}
            />
          </div>

          {/* Enable Ensemble */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="ensemble">Enable Ensemble Models</Label>
              <p className="text-sm text-muted-foreground">
                Combine multiple models for better accuracy
              </p>
            </div>
            <Switch
              id="ensemble"
              checked={config.enable_ensemble}
              onCheckedChange={(checked) => setConfig({ ...config, enable_ensemble: checked })}
            />
          </div>

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Training in Progress...
              </>
            ) : (
              "Start AutoML Training"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
