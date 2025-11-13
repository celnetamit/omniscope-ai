"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { FileText, Sparkles, ExternalLink, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Entity {
  text: string;
  type: "gene" | "disease" | "drug" | "pathway";
  confidence: number;
}

interface Relationship {
  source: string;
  target: string;
  type: string;
  confidence: number;
}

interface PaperSummary {
  pmid: string;
  title: string;
  abstract: string;
  summary: string;
  key_findings: string[];
  entities: Entity[];
  relationships: Relationship[];
  methods: string[];
}

interface PaperSummaryDisplayProps {
  pmid: string;
}

export function PaperSummaryDisplay({ pmid }: PaperSummaryDisplayProps) {
  const [summary, setSummary] = useState<PaperSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/literature/summarize`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ pmid }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
        toast.success("Summary generated");
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to generate summary");
      }
    } catch (error) {
      console.error("Summary error:", error);
      toast.error("Failed to generate summary");
    } finally {
      setLoading(false);
    }
  };

  const getEntityColor = (type: string) => {
    const colors: Record<string, string> = {
      gene: "bg-blue-500",
      disease: "bg-red-500",
      drug: "bg-green-500",
      pathway: "bg-purple-500",
    };
    return colors[type] || "bg-gray-500";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Paper Analysis
            </CardTitle>
            <CardDescription>PMID: {pmid}</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                window.open(`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`, "_blank")
              }
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              View on PubMed
            </Button>
            <Button onClick={fetchSummary} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Summary
                </>
              )}
            </Button>
          </div>
        </div>
      </CardHeader>

      {summary && (
        <CardContent>
          <Tabs defaultValue="summary" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="entities">Entities</TabsTrigger>
              <TabsTrigger value="relationships">Relationships</TabsTrigger>
              <TabsTrigger value="methods">Methods</TabsTrigger>
            </TabsList>

            {/* Summary Tab */}
            <TabsContent value="summary" className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">{summary.title}</h4>
                <Separator className="my-3" />
              </div>

              <div>
                <h4 className="text-sm font-medium mb-2">AI-Generated Summary</h4>
                <p className="text-sm text-muted-foreground">{summary.summary}</p>
              </div>

              <Separator />

              <div>
                <h4 className="text-sm font-medium mb-2">Key Findings</h4>
                <ul className="space-y-2">
                  {summary.key_findings.map((finding, index) => (
                    <li key={index} className="text-sm text-muted-foreground flex gap-2">
                      <span className="text-primary">•</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <Separator />

              <div>
                <h4 className="text-sm font-medium mb-2">Abstract</h4>
                <ScrollArea className="h-[200px]">
                  <p className="text-sm text-muted-foreground">{summary.abstract}</p>
                </ScrollArea>
              </div>
            </TabsContent>

            {/* Entities Tab */}
            <TabsContent value="entities" className="space-y-4">
              <div className="space-y-3">
                {["gene", "disease", "drug", "pathway"].map((type) => {
                  const entities = summary.entities.filter((e) => e.type === type);
                  if (entities.length === 0) return null;

                  return (
                    <div key={type}>
                      <h4 className="text-sm font-medium mb-2 capitalize">{type}s</h4>
                      <div className="flex flex-wrap gap-2">
                        {entities.map((entity, index) => (
                          <Badge
                            key={index}
                            variant="outline"
                            className="flex items-center gap-2"
                          >
                            <div
                              className={`h-2 w-2 rounded-full ${getEntityColor(
                                entity.type
                              )}`}
                            />
                            {entity.text}
                            <span className="text-xs text-muted-foreground">
                              {(entity.confidence * 100).toFixed(0)}%
                            </span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </TabsContent>

            {/* Relationships Tab */}
            <TabsContent value="relationships" className="space-y-3">
              <ScrollArea className="h-[400px]">
                {summary.relationships.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    No relationships extracted
                  </div>
                ) : (
                  <div className="space-y-2">
                    {summary.relationships.map((rel, index) => (
                      <div key={index} className="border rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="secondary" className="text-xs">
                            {rel.type}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {(rel.confidence * 100).toFixed(0)}% confidence
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium">{rel.source}</span>
                          <span className="text-muted-foreground">→</span>
                          <span className="font-medium">{rel.target}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>

            {/* Methods Tab */}
            <TabsContent value="methods" className="space-y-3">
              <ScrollArea className="h-[400px]">
                {summary.methods.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    No methods extracted
                  </div>
                ) : (
                  <ul className="space-y-2">
                    {summary.methods.map((method, index) => (
                      <li key={index} className="text-sm text-muted-foreground flex gap-2">
                        <span className="text-primary">•</span>
                        <span>{method}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      )}
    </Card>
  );
}
