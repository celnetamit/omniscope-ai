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
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Loader2, Upload, Download, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";

interface BatchQueryResult {
  query: string;
  status: "pending" | "success" | "failed";
  data?: any;
  error?: string;
}

interface BatchQueryFormProps {
  onComplete?: (results: BatchQueryResult[]) => void;
}

export function BatchQueryForm({ onComplete }: BatchQueryFormProps) {
  const [database, setDatabase] = useState<string>("");
  const [queryType, setQueryType] = useState<string>("");
  const [queries, setQueries] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<BatchQueryResult[]>([]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      const lines = text
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.length > 0);
      setQueries(lines);
      toast.success(`Loaded ${lines.length} queries`);
    };
    reader.readAsText(file);
  };

  const handleBatchQuery = async () => {
    if (!database || queries.length === 0) {
      toast.error("Please select a database and upload queries");
      return;
    }

    setLoading(true);
    setProgress(0);
    const batchResults: BatchQueryResult[] = queries.map((q) => ({
      query: q,
      status: "pending",
    }));
    setResults(batchResults);

    try {
      const token = localStorage.getItem("access_token");
      
      for (let i = 0; i < queries.length; i++) {
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/integration/query`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                database: database,
                query_type: queryType,
                query: queries[i],
              }),
            }
          );

          if (response.ok) {
            const data = await response.json();
            batchResults[i] = {
              query: queries[i],
              status: "success",
              data: data,
            };
          } else {
            const error = await response.json();
            batchResults[i] = {
              query: queries[i],
              status: "failed",
              error: error.detail || "Query failed",
            };
          }
        } catch (error) {
          batchResults[i] = {
            query: queries[i],
            status: "failed",
            error: "Network error",
          };
        }

        setProgress(((i + 1) / queries.length) * 100);
        setResults([...batchResults]);
      }

      toast.success("Batch query completed");
      onComplete?.(batchResults);
    } catch (error) {
      console.error("Batch query error:", error);
      toast.error("Batch query failed");
    } finally {
      setLoading(false);
    }
  };

  const exportResults = () => {
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `batch-results-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success("Results exported");
  };

  const successCount = results.filter((r) => r.status === "success").length;
  const failedCount = results.filter((r) => r.status === "failed").length;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Batch Query Configuration</CardTitle>
          <CardDescription>
            Upload a file with multiple queries to process in batch
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Database Selection */}
          <div className="space-y-2">
            <Label htmlFor="batch-database">Database</Label>
            <Select value={database} onValueChange={setDatabase}>
              <SelectTrigger id="batch-database">
                <SelectValue placeholder="Select database" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ncbi">NCBI</SelectItem>
                <SelectItem value="uniprot">UniProt</SelectItem>
                <SelectItem value="kegg">KEGG</SelectItem>
                <SelectItem value="pubmed">PubMed</SelectItem>
                <SelectItem value="string">STRING</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Query Type */}
          <div className="space-y-2">
            <Label htmlFor="batch-query-type">Query Type</Label>
            <Select value={queryType} onValueChange={setQueryType}>
              <SelectTrigger id="batch-query-type">
                <SelectValue placeholder="Select query type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gene">Gene</SelectItem>
                <SelectItem value="protein">Protein</SelectItem>
                <SelectItem value="pathway">Pathway</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* File Upload */}
          <div className="space-y-2">
            <Label htmlFor="batch-file">Upload Query File</Label>
            <div className="flex items-center gap-2">
              <Input
                id="batch-file"
                type="file"
                accept=".txt,.csv"
                onChange={handleFileUpload}
                disabled={loading}
              />
              <Button variant="outline" size="icon" disabled={loading}>
                <Upload className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Upload a text file with one query per line
            </p>
          </div>

          {/* Query Count */}
          {queries.length > 0 && (
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <span className="text-sm font-medium">Queries loaded:</span>
              <Badge>{queries.length}</Badge>
            </div>
          )}

          {/* Submit Button */}
          <Button
            onClick={handleBatchQuery}
            disabled={loading || !database || queries.length === 0}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing ({Math.round(progress)}%)
              </>
            ) : (
              "Start Batch Query"
            )}
          </Button>

          {/* Progress */}
          {loading && (
            <div className="space-y-2">
              <Progress value={progress} />
              <p className="text-xs text-center text-muted-foreground">
                Processing query {Math.ceil((progress / 100) * queries.length)} of {queries.length}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Summary */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Batch Results</CardTitle>
              <Button variant="outline" size="sm" onClick={exportResults}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 border rounded-lg">
                <p className="text-2xl font-bold">{results.length}</p>
                <p className="text-xs text-muted-foreground">Total</p>
              </div>
              <div className="text-center p-3 border rounded-lg bg-green-50 dark:bg-green-950">
                <p className="text-2xl font-bold text-green-600">{successCount}</p>
                <p className="text-xs text-muted-foreground">Success</p>
              </div>
              <div className="text-center p-3 border rounded-lg bg-red-50 dark:bg-red-950">
                <p className="text-2xl font-bold text-red-600">{failedCount}</p>
                <p className="text-xs text-muted-foreground">Failed</p>
              </div>
            </div>

            {/* Results List */}
            <div className="space-y-2 max-h-[300px] overflow-y-auto">
              {results.map((result, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {result.status === "success" ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : result.status === "failed" ? (
                      <XCircle className="h-4 w-4 text-red-500" />
                    ) : (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )}
                    <span className="text-sm font-mono">{result.query}</span>
                  </div>
                  <Badge
                    variant={
                      result.status === "success"
                        ? "default"
                        : result.status === "failed"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {result.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
