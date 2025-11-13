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
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Loader2, Layers, Plus, X } from "lucide-react";
import { toast } from "sonner";

interface OmicsLayer {
  dataset_id: string;
  layer_name: string;
  layer_type: "genomics" | "transcriptomics" | "proteomics" | "metabolomics" | "other";
}

interface MultiOmicsConfig {
  layers: OmicsLayer[];
  method: "mofa" | "diablo";
  n_factors: number;
  convergence_threshold: number;
}

interface MultiOmicsIntegrationProps {
  datasets: Array<{ id: string; name: string; type?: string }>;
  onSubmit: (config: MultiOmicsConfig) => void;
  loading?: boolean;
}

export function MultiOmicsIntegration({
  datasets,
  onSubmit,
  loading = false,
}: MultiOmicsIntegrationProps) {
  const [config, setConfig] = useState<MultiOmicsConfig>({
    layers: [],
    method: "mofa",
    n_factors: 10,
    convergence_threshold: 0.001,
  });

  const [newLayer, setNewLayer] = useState<OmicsLayer>({
    dataset_id: "",
    layer_name: "",
    layer_type: "genomics",
  });

  const addLayer = () => {
    if (!newLayer.dataset_id) {
      toast.error("Please select a dataset");
      return;
    }
    if (!newLayer.layer_name.trim()) {
      toast.error("Please enter a layer name");
      return;
    }

    setConfig({
      ...config,
      layers: [...config.layers, newLayer],
    });

    setNewLayer({
      dataset_id: "",
      layer_name: "",
      layer_type: "genomics",
    });

    toast.success("Layer added");
  };

  const removeLayer = (index: number) => {
    setConfig({
      ...config,
      layers: config.layers.filter((_, i) => i !== index),
    });
    toast.success("Layer removed");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (config.layers.length < 2) {
      toast.error("Please add at least 2 omics layers");
      return;
    }

    onSubmit(config);
  };

  const getLayerTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      genomics: "bg-blue-500",
      transcriptomics: "bg-green-500",
      proteomics: "bg-purple-500",
      metabolomics: "bg-orange-500",
      other: "bg-gray-500",
    };
    return colors[type] || colors.other;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Layers className="h-5 w-5" />
          Multi-Omics Integration
        </CardTitle>
        <CardDescription>
          Integrate multiple omics layers using MOFA+ or DIABLO
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Method Selection */}
          <div className="space-y-2">
            <Label htmlFor="method">Integration Method</Label>
            <Select
              value={config.method}
              onValueChange={(value: any) => setConfig({ ...config, method: value })}
            >
              <SelectTrigger id="method">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="mofa">MOFA+ (Multi-Omics Factor Analysis)</SelectItem>
                <SelectItem value="diablo">DIABLO (Data Integration Analysis)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              {config.method === "mofa"
                ? "Unsupervised integration identifying shared and unique variation"
                : "Supervised integration for classification and biomarker discovery"}
            </p>
          </div>

          {/* Add Layer Section */}
          <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
            <h4 className="font-medium text-sm">Add Omics Layer</h4>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="layer-dataset">Dataset</Label>
                <Select
                  value={newLayer.dataset_id}
                  onValueChange={(value) =>
                    setNewLayer({ ...newLayer, dataset_id: value })
                  }
                >
                  <SelectTrigger id="layer-dataset">
                    <SelectValue placeholder="Select dataset" />
                  </SelectTrigger>
                  <SelectContent>
                    {datasets
                      .filter(
                        (d) => !config.layers.some((l) => l.dataset_id === d.id)
                      )
                      .map((dataset) => (
                        <SelectItem key={dataset.id} value={dataset.id}>
                          {dataset.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="layer-type">Layer Type</Label>
                <Select
                  value={newLayer.layer_type}
                  onValueChange={(value: any) =>
                    setNewLayer({ ...newLayer, layer_type: value })
                  }
                >
                  <SelectTrigger id="layer-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="genomics">Genomics</SelectItem>
                    <SelectItem value="transcriptomics">Transcriptomics</SelectItem>
                    <SelectItem value="proteomics">Proteomics</SelectItem>
                    <SelectItem value="metabolomics">Metabolomics</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="layer-name">Layer Name</Label>
              <div className="flex gap-2">
                <Input
                  id="layer-name"
                  placeholder="e.g., RNA-seq expression"
                  value={newLayer.layer_name}
                  onChange={(e) =>
                    setNewLayer({ ...newLayer, layer_name: e.target.value })
                  }
                />
                <Button type="button" onClick={addLayer} size="icon">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Current Layers */}
          <div className="space-y-2">
            <Label>Omics Layers ({config.layers.length})</Label>
            {config.layers.length === 0 ? (
              <div className="text-center text-muted-foreground py-8 border rounded-lg">
                No layers added yet. Add at least 2 layers to proceed.
              </div>
            ) : (
              <div className="space-y-2">
                {config.layers.map((layer, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`h-3 w-3 rounded-full ${getLayerTypeColor(
                          layer.layer_type
                        )}`}
                      />
                      <div>
                        <p className="font-medium text-sm">{layer.layer_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {datasets.find((d) => d.id === layer.dataset_id)?.name}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="capitalize">
                        {layer.layer_type}
                      </Badge>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => removeLayer(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Parameters */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="factors">Number of Factors: {config.n_factors}</Label>
              <Slider
                id="factors"
                min={2}
                max={50}
                step={1}
                value={[config.n_factors]}
                onValueChange={([value]) => setConfig({ ...config, n_factors: value })}
              />
              <p className="text-xs text-muted-foreground">
                Latent factors to extract from the data
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="threshold">
                Convergence Threshold: {config.convergence_threshold}
              </Label>
              <Slider
                id="threshold"
                min={0.0001}
                max={0.01}
                step={0.0001}
                value={[config.convergence_threshold]}
                onValueChange={([value]) =>
                  setConfig({ ...config, convergence_threshold: value })
                }
              />
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full"
            disabled={loading || config.layers.length < 2}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Integration...
              </>
            ) : (
              "Run Multi-Omics Integration"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
