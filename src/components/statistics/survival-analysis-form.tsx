"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Loader2, Activity } from "lucide-react";
import { toast } from "sonner";

interface SurvivalAnalysisConfig {
  dataset_id: string;
  time_column: string;
  event_column: string;
  method: "kaplan_meier" | "cox";
  covariates?: string[];
  confidence_level: number;
  include_risk_table: boolean;
  group_by?: string;
}

interface SurvivalAnalysisFormProps {
  datasets: Array<{ id: string; name: string; columns: string[] }>;
  onSubmit: (config: SurvivalAnalysisConfig) => void;
  loading?: boolean;
}

export function SurvivalAnalysisForm({
  datasets,
  onSubmit,
  loading = false,
}: SurvivalAnalysisFormProps) {
  const [config, setConfig] = useState<SurvivalAnalysisConfig>({
    dataset_id: "",
    time_column: "",
    event_column: "",
    method: "kaplan_meier",
    covariates: [],
    confidence_level: 0.95,
    include_risk_table: true,
  });

  const selectedDataset = datasets.find((d) => d.id === config.dataset_id);
  const availableColumns = selectedDataset?.columns || [];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!config.dataset_id) {
      toast.error("Please select a dataset");
      return;
    }
    if (!config.time_column) {
      toast.error("Please select a time column");
      return;
    }
    if (!config.event_column) {
      toast.error("Please select an event column");
      return;
    }

    onSubmit(config);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Survival Analysis Configuration
        </CardTitle>
        <CardDescription>
          Configure Kaplan-Meier curves or Cox proportional hazards models
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
                  time_column: "",
                  event_column: "",
                  covariates: [],
                  group_by: "",
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

          {/* Method Selection */}
          <div className="space-y-2">
            <Label htmlFor="method">Analysis Method</Label>
            <Select
              value={config.method}
              onValueChange={(value: any) => setConfig({ ...config, method: value })}
            >
              <SelectTrigger id="method">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="kaplan_meier">Kaplan-Meier</SelectItem>
                <SelectItem value="cox">Cox Proportional Hazards</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {config.method === "kaplan_meier"
                ? "Non-parametric survival curve estimation"
                : "Semi-parametric regression model for survival data"}
            </p>
          </div>

          {/* Time Column */}
          <div className="space-y-2">
            <Label htmlFor="time">Time Column</Label>
            <Select
              value={config.time_column}
              onValueChange={(value) => setConfig({ ...config, time_column: value })}
              disabled={!config.dataset_id}
            >
              <SelectTrigger id="time">
                <SelectValue placeholder="Select time column" />
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

          {/* Event Column */}
          <div className="space-y-2">
            <Label htmlFor="event">Event Column</Label>
            <Select
              value={config.event_column}
              onValueChange={(value) => setConfig({ ...config, event_column: value })}
              disabled={!config.dataset_id}
            >
              <SelectTrigger id="event">
                <SelectValue placeholder="Select event column" />
              </SelectTrigger>
              <SelectContent>
                {availableColumns.map((col) => (
                  <SelectItem key={col} value={col}>
                    {col}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Binary column indicating whether the event occurred (1) or was censored (0)
            </p>
          </div>

          {/* Group By (for Kaplan-Meier) */}
          {config.method === "kaplan_meier" && (
            <div className="space-y-2">
              <Label htmlFor="group-by">Group By (Optional)</Label>
              <Select
                value={config.group_by}
                onValueChange={(value) => setConfig({ ...config, group_by: value })}
                disabled={!config.dataset_id}
              >
                <SelectTrigger id="group-by">
                  <SelectValue placeholder="No grouping" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">No grouping</SelectItem>
                  {availableColumns
                    .filter(
                      (col) => col !== config.time_column && col !== config.event_column
                    )
                    .map((col) => (
                      <SelectItem key={col} value={col}>
                        {col}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Covariates (for Cox) */}
          {config.method === "cox" && (
            <div className="space-y-2">
              <Label>Covariates</Label>
              <div className="border rounded-md p-3 max-h-40 overflow-y-auto space-y-2">
                {availableColumns
                  .filter(
                    (col) => col !== config.time_column && col !== config.event_column
                  )
                  .map((col) => (
                    <div key={col} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`covariate-${col}`}
                        checked={config.covariates?.includes(col)}
                        onChange={(e) => {
                          const covariates = config.covariates || [];
                          if (e.target.checked) {
                            setConfig({
                              ...config,
                              covariates: [...covariates, col],
                            });
                          } else {
                            setConfig({
                              ...config,
                              covariates: covariates.filter((c) => c !== col),
                            });
                          }
                        }}
                        className="rounded"
                      />
                      <label htmlFor={`covariate-${col}`} className="text-sm cursor-pointer">
                        {col}
                      </label>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Confidence Level */}
          <div className="space-y-2">
            <Label htmlFor="confidence">
              Confidence Level: {(config.confidence_level * 100).toFixed(0)}%
            </Label>
            <Slider
              id="confidence"
              min={0.8}
              max={0.99}
              step={0.01}
              value={[config.confidence_level]}
              onValueChange={([value]) =>
                setConfig({ ...config, confidence_level: value })
              }
            />
          </div>

          {/* Include Risk Table */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="risk-table">Include Risk Table</Label>
              <p className="text-sm text-muted-foreground">
                Show number at risk at each time point
              </p>
            </div>
            <Switch
              id="risk-table"
              checked={config.include_risk_table}
              onCheckedChange={(checked) =>
                setConfig({ ...config, include_risk_table: checked })
              }
            />
          </div>

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Analysis...
              </>
            ) : (
              "Run Survival Analysis"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
