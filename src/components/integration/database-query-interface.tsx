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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Loader2, Database, Search, Download } from "lucide-react";
import { toast } from "sonner";

interface QueryResult {
  source: string;
  data: any;
  timestamp: string;
}

interface DatabaseQueryInterfaceProps {
  onQueryComplete?: (results: QueryResult[]) => void;
}

const databases = [
  { id: "ncbi", name: "NCBI", description: "Gene information and sequences" },
  { id: "uniprot", name: "UniProt", description: "Protein annotations" },
  { id: "kegg", name: "KEGG", description: "Pathway information" },
  { id: "pubmed", name: "PubMed", description: "Research literature" },
  { id: "string", name: "STRING", description: "Protein-protein interactions" },
];

const queryTypes = {
  ncbi: ["gene", "nucleotide", "protein"],
  uniprot: ["protein", "id_mapping"],
  kegg: ["pathway", "compound", "reaction"],
  pubmed: ["search", "fetch"],
  string: ["interactions", "network"],
};

export function DatabaseQueryInterface({ onQueryComplete }: DatabaseQueryInterfaceProps) {
  const [selectedDb, setSelectedDb] = useState<string>("");
  const [queryType, setQueryType] = useState<string>("");
  const [queryInput, setQueryInput] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QueryResult[]>([]);

  const handleQuery = async () => {
    if (!selectedDb || !queryInput.trim()) {
      toast.error("Please select a database and enter a query");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/integration/query`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            database: selectedDb,
            query_type: queryType,
            query: queryInput,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        const newResult: QueryResult = {
          source: selectedDb,
          data: data,
          timestamp: new Date().toISOString(),
        };
        setResults([newResult, ...results]);
        toast.success("Query completed successfully");
        onQueryComplete?.([newResult]);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Query failed");
      }
    } catch (error) {
      console.error("Query error:", error);
      toast.error("Failed to execute query");
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
    link.download = `integration-results-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success("Results exported");
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            External Database Query
          </CardTitle>
          <CardDescription>
            Query external biological databases for annotations and context
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="single" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="single">Single Query</TabsTrigger>
              <TabsTrigger value="batch">Batch Query</TabsTrigger>
            </TabsList>

            <TabsContent value="single" className="space-y-4">
              {/* Database Selection */}
              <div className="space-y-2">
                <Label>Select Database</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {databases.map((db) => (
                    <div
                      key={db.id}
                      className={`border rounded-lg p-3 cursor-pointer transition-all ${
                        selectedDb === db.id
                          ? "border-primary bg-primary/5"
                          : "hover:border-primary/50"
                      }`}
                      onClick={() => {
                        setSelectedDb(db.id);
                        setQueryType("");
                      }}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium">{db.name}</h4>
                          <p className="text-xs text-muted-foreground mt-1">
                            {db.description}
                          </p>
                        </div>
                        {selectedDb === db.id && (
                          <div className="h-4 w-4 rounded-full bg-primary flex items-center justify-center">
                            <div className="h-1.5 w-1.5 rounded-full bg-white" />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Query Type */}
              {selectedDb && (
                <div className="space-y-2">
                  <Label htmlFor="query-type">Query Type</Label>
                  <Select value={queryType} onValueChange={setQueryType}>
                    <SelectTrigger id="query-type">
                      <SelectValue placeholder="Select query type" />
                    </SelectTrigger>
                    <SelectContent>
                      {queryTypes[selectedDb as keyof typeof queryTypes]?.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* Query Input */}
              <div className="space-y-2">
                <Label htmlFor="query-input">Query</Label>
                <div className="flex gap-2">
                  <Input
                    id="query-input"
                    placeholder="Enter gene ID, protein name, or search term..."
                    value={queryInput}
                    onChange={(e) => setQueryInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleQuery();
                      }
                    }}
                  />
                  <Button onClick={handleQuery} disabled={loading || !selectedDb}>
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Example Queries */}
              {selectedDb && (
                <div className="text-sm text-muted-foreground">
                  <p className="font-medium mb-1">Example queries:</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedDb === "ncbi" && (
                      <>
                        <Badge
                          variant="outline"
                          className="cursor-pointer"
                          onClick={() => setQueryInput("BRCA1")}
                        >
                          BRCA1
                        </Badge>
                        <Badge
                          variant="outline"
                          className="cursor-pointer"
                          onClick={() => setQueryInput("TP53")}
                        >
                          TP53
                        </Badge>
                      </>
                    )}
                    {selectedDb === "uniprot" && (
                      <>
                        <Badge
                          variant="outline"
                          className="cursor-pointer"
                          onClick={() => setQueryInput("P04637")}
                        >
                          P04637
                        </Badge>
                        <Badge
                          variant="outline"
                          className="cursor-pointer"
                          onClick={() => setQueryInput("P38398")}
                        >
                          P38398
                        </Badge>
                      </>
                    )}
                    {selectedDb === "kegg" && (
                      <>
                        <Badge
                          variant="outline"
                          className="cursor-pointer"
                          onClick={() => setQueryInput("hsa04110")}
                        >
                          hsa04110
                        </Badge>
                        <Badge
                          variant="outline"
                          className="cursor-pointer"
                          onClick={() => setQueryInput("hsa05200")}
                        >
                          hsa05200
                        </Badge>
                      </>
                    )}
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="batch" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="batch-input">Batch Query (one per line)</Label>
                <textarea
                  id="batch-input"
                  className="w-full min-h-[200px] p-3 border rounded-md"
                  placeholder="Enter multiple IDs or queries, one per line..."
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                />
              </div>
              <Button onClick={handleQuery} disabled={loading || !selectedDb} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing Batch Query...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Execute Batch Query
                  </>
                )}
              </Button>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Query Results ({results.length})</CardTitle>
              <Button variant="outline" size="sm" onClick={exportResults}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((result, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <Badge>{result.source.toUpperCase()}</Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(result.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <pre className="text-xs bg-muted p-3 rounded overflow-x-auto max-h-[200px]">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
