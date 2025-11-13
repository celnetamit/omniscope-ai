"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Loader2, TrendingUp } from "lucide-react";
import { toast } from "sonner";

interface TimeSeriesConfig {
  dataset_id: string;
  time_column: string;
  value_column: string;
  method: "arima" | "prophet" | "lstm";
  forecast_periods: number;
  include_confidence_intervals: boolean;
  seasonality?: "auto" | "daily" | "weekly" | "monthly" | "yearly";
  // ARIMA specific
  arima_order?: { p: number; d: number; q: number };
  // LSTM specific
  lstm_lookback?: number;
  lstm_epochs?: number;
}

interface TimeSeriesInterfaceProps {
  datasets: Array<{ id: string; name: string; columns: string[] }>;
  onSubmit: (config: TimeSeriesConfig) => void;
  loading?: boolean;
}

export function TimeSeriesInterface({
  datasets,
  onSubmit,
  loading = false,
}: TimeSeriesInterfaceProps) {
  const [config, setConfig] = useState<TimeSeriesConfig>({
    dataset_id: "",
    time_column: "",
    value_column: "",
    method: "prophet",
    forecast_periods: 30,
    include_confidence_intervals: true,
    seasonality: "auto",
    arima_order: { p: 1, d: 1, q: 1 },
    lstm_lookback: 10,
    lstm_epochs: 50,
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
    if (!config.value_column) {
      toast.error("Please select a value column");
      return;
    }

    onSubmit(config);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Time Series Analysis
        </CardTitle>
        <CardDescription>
          Forecast future values using ARIMA, Prophet, or LSTM models
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Tabs defaultValue="data" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="data">Data</TabsTrigger>
              <TabsTrigger value="method">Method</TabsTrigger>
              <TabsTrigger value="forecast">Forecast</TabsTrigger>
            </TabsList>

            {/* Data Tab */}
            <TabsContent value="data" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="dataset">Dataset</Label>
                <Select
                  value={config.dataset_id}
                  onValueChange={(value) => {
                    setConfig({
                      ...config,
                      dataset_id: value,
                      time_column: "",
                      value_column: "",
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

              <div className="space-y-2">
                <Label htmlFor="value">Value Column</Label>
                <Select
                  value={config.value_column}
                  onValueChange={(value) => setConfig({ ...config, value_column: value })}
                  disabled={!config.dataset_id}
                >
                  <SelectTrigger id="value">
                    <SelectValue placeholder="Select value column" />
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
            </TabsContent>

            {/* Method Tab */}
            <TabsContent value="method" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="method">Forecasting Method</Label>
                <Select
                  value={config.method}
                  onValueChange={(value: any) => setConfig({ ...config, method: value })}
                >
                  <SelectTrigger id="method">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="arima">ARIMA</SelectItem>
                    <SelectItem value="prophet">Prophet</SelectItem>
                    <SelectItem value="lstm">LSTM</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* ARIMA Parameters */}
              {config.method === "arima" && (
                <div className="space-y-4 p-4 border rounded-lg">
                  <h4 className="font-medium text-sm">ARIMA Parameters (p, d, q)</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="arima-p">p (AR order)</Label>
                      <Input
                        id="arima-p"
                        type="number"
                        min={0}
                        max={5}
                        value={config.arima_order?.p}
                        onChange={(e) =>
                          setConfig({
                            ...config,
                            arima_order: {
                              ...config.arima_order!,
                              p: parseInt(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="arima-d">d (Differencing)</Label>
                      <Input
                        id="arima-d"
                        type="number"
                        min={0}
                        max={2}
                        value={config.arima_order?.d}
                        onChange={(e) =>
                          setConfig({
                            ...config,
                            arima_order: {
                              ...config.arima_order!,
                              d: parseInt(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="arima-q">q (MA order)</Label>
                      <Input
                        id="arima-q"
                        type="number"
                        min={0}
                        max={5}
                        value={config.arima_order?.q}
                        onChange={(e) =>
                          setConfig({
                            ...config,
                            arima_order: {
                              ...config.arima_order!,
                              q: parseInt(e.target.value),
                            },
                          })
                        }
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Prophet Parameters */}
              {config.method === "prophet" && (
                <div className="space-y-2">
                  <Label htmlFor="seasonality">Seasonality</Label>
                  <Select
                    value={config.seasonality}
                    onValueChange={(value: any) =>
                      setConfig({ ...config, seasonality: value })
                    }
                  >
                    <SelectTrigger id="seasonality">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Auto-detect</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="yearly">Yearly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* LSTM Parameters */}
              {config.method === "lstm" && (
                <div className="space-y-4 p-4 border rounded-lg">
                  <h4 className="font-medium text-sm">LSTM Parameters</h4>
                  <div className="space-y-2">
                    <Label htmlFor="lookback">
                      Lookback Window: {config.lstm_lookback}
                    </Label>
                    <Slider
                      id="lookback"
                      min={5}
                      max={50}
                      step={5}
                      value={[config.lstm_lookback || 10]}
                      onValueChange={([value]) =>
                        setConfig({ ...config, lstm_lookback: value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="epochs">Epochs: {config.lstm_epochs}</Label>
                    <Slider
                      id="epochs"
                      min={10}
                      max={200}
                      step={10}
                      value={[config.lstm_epochs || 50]}
                      onValueChange={([value]) =>
                        setConfig({ ...config, lstm_epochs: value })
                      }
                    />
                  </div>
                </div>
              )}
            </TabsContent>

            {/* Forecast Tab */}
            <TabsContent value="forecast" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="periods">
                  Forecast Periods: {config.forecast_periods}
                </Label>
                <Slider
                  id="periods"
                  min={1}
                  max={365}
                  step={1}
                  value={[config.forecast_periods]}
                  onValueChange={([value]) =>
                    setConfig({ ...config, forecast_periods: value })
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Number of time steps to forecast into the future
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="confidence">Confidence Intervals</Label>
                  <p className="text-sm text-muted-foreground">
                    Show prediction uncertainty bands
                  </p>
                </div>
                <Switch
                  id="confidence"
                  checked={config.include_confidence_intervals}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, include_confidence_intervals: checked })
                  }
                />
              </div>
            </TabsContent>
          </Tabs>

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Forecast...
              </>
            ) : (
              "Run Time Series Analysis"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
