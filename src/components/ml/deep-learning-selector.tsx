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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Loader2, Brain, Layers } from "lucide-react";
import { toast } from "sonner";

interface DeepLearningConfig {
  dataset_id: string;
  architecture: "cnn_1d" | "cnn_2d" | "rnn" | "lstm" | "transformer";
  target_column: string;
  feature_columns: string[];
  epochs: number;
  batch_size: number;
  learning_rate: number;
  hidden_layers: number;
  dropout_rate: number;
  optimizer: "adam" | "sgd" | "rmsprop";
}

interface DeepLearningSelectorProps {
  datasets: Array<{ id: string; name: string; columns: string[] }>;
  onSubmit: (config: DeepLearningConfig) => void;
  loading?: boolean;
}

const architectureInfo = {
  cnn_1d: {
    name: "1D CNN",
    description: "Convolutional Neural Network for sequence data",
    useCases: ["Time series", "Genomic sequences", "Signal processing"],
  },
  cnn_2d: {
    name: "2D CNN",
    description: "Convolutional Neural Network for image-like data",
    useCases: ["Heatmaps", "Spatial data", "Image analysis"],
  },
  rnn: {
    name: "RNN",
    description: "Recurrent Neural Network for sequential patterns",
    useCases: ["Time series", "Sequential data", "Pattern recognition"],
  },
  lstm: {
    name: "LSTM",
    description: "Long Short-Term Memory for long-range dependencies",
    useCases: ["Time series forecasting", "Sequence prediction", "Complex patterns"],
  },
  transformer: {
    name: "Transformer",
    description: "Attention-based architecture for complex relationships",
    useCases: ["Multi-omics integration", "Complex patterns", "Feature interactions"],
  },
};

export function DeepLearningSelector({
  datasets,
  onSubmit,
  loading = false,
}: DeepLearningSelectorProps) {
  const [config, setConfig] = useState<DeepLearningConfig>({
    dataset_id: "",
    architecture: "lstm",
    target_column: "",
    feature_columns: [],
    epochs: 50,
    batch_size: 32,
    learning_rate: 0.001,
    hidden_layers: 3,
    dropout_rate: 0.2,
    optimizer: "adam",
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
          <Brain className="h-5 w-5" />
          Deep Learning Configuration
        </CardTitle>
        <CardDescription>
          Configure neural network architecture and training parameters
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Tabs defaultValue="architecture" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="architecture">Architecture</TabsTrigger>
              <TabsTrigger value="data">Data</TabsTrigger>
              <TabsTrigger value="training">Training</TabsTrigger>
            </TabsList>

            {/* Architecture Tab */}
            <TabsContent value="architecture" className="space-y-4">
              <div className="space-y-2">
                <Label>Select Architecture</Label>
                <div className="grid grid-cols-1 gap-3">
                  {Object.entries(architectureInfo).map(([key, info]) => (
                    <div
                      key={key}
                      className={`border rounded-lg p-4 cursor-pointer transition-all ${
                        config.architecture === key
                          ? "border-primary bg-primary/5"
                          : "hover:border-primary/50"
                      }`}
                      onClick={() =>
                        setConfig({ ...config, architecture: key as any })
                      }
                    >
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Layers className="h-4 w-4" />
                            <h4 className="font-medium">{info.name}</h4>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {info.description}
                          </p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {info.useCases.map((useCase) => (
                              <Badge key={useCase} variant="secondary" className="text-xs">
                                {useCase}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        {config.architecture === key && (
                          <div className="h-5 w-5 rounded-full bg-primary flex items-center justify-center">
                            <div className="h-2 w-2 rounded-full bg-white" />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Network Structure */}
              <div className="space-y-2">
                <Label htmlFor="hidden-layers">
                  Hidden Layers: {config.hidden_layers}
                </Label>
                <Slider
                  id="hidden-layers"
                  min={1}
                  max={10}
                  step={1}
                  value={[config.hidden_layers]}
                  onValueChange={([value]) =>
                    setConfig({ ...config, hidden_layers: value })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="dropout">
                  Dropout Rate: {config.dropout_rate.toFixed(2)}
                </Label>
                <Slider
                  id="dropout"
                  min={0}
                  max={0.5}
                  step={0.05}
                  value={[config.dropout_rate]}
                  onValueChange={([value]) =>
                    setConfig({ ...config, dropout_rate: value })
                  }
                />
              </div>
            </TabsContent>

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

              <div className="space-y-2">
                <Label htmlFor="target">Target Column</Label>
                <Select
                  value={config.target_column}
                  onValueChange={(value) =>
                    setConfig({ ...config, target_column: value })
                  }
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
                                feature_columns: config.feature_columns.filter(
                                  (c) => c !== col
                                ),
                              });
                            }
                          }}
                          className="rounded"
                        />
                        <label
                          htmlFor={`feature-${col}`}
                          className="text-sm cursor-pointer"
                        >
                          {col}
                        </label>
                      </div>
                    ))}
                </div>
              </div>
            </TabsContent>

            {/* Training Tab */}
            <TabsContent value="training" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="optimizer">Optimizer</Label>
                <Select
                  value={config.optimizer}
                  onValueChange={(value: any) =>
                    setConfig({ ...config, optimizer: value })
                  }
                >
                  <SelectTrigger id="optimizer">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="adam">Adam</SelectItem>
                    <SelectItem value="sgd">SGD</SelectItem>
                    <SelectItem value="rmsprop">RMSprop</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="learning-rate">
                  Learning Rate: {config.learning_rate}
                </Label>
                <Slider
                  id="learning-rate"
                  min={0.0001}
                  max={0.01}
                  step={0.0001}
                  value={[config.learning_rate]}
                  onValueChange={([value]) =>
                    setConfig({ ...config, learning_rate: value })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="epochs">Epochs: {config.epochs}</Label>
                <Slider
                  id="epochs"
                  min={10}
                  max={200}
                  step={10}
                  value={[config.epochs]}
                  onValueChange={([value]) =>
                    setConfig({ ...config, epochs: value })
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="batch-size">Batch Size</Label>
                <Select
                  value={config.batch_size.toString()}
                  onValueChange={(value) =>
                    setConfig({ ...config, batch_size: parseInt(value) })
                  }
                >
                  <SelectTrigger id="batch-size">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="16">16</SelectItem>
                    <SelectItem value="32">32</SelectItem>
                    <SelectItem value="64">64</SelectItem>
                    <SelectItem value="128">128</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>
          </Tabs>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Training in Progress...
              </>
            ) : (
              "Start Deep Learning Training"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
