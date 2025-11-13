"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { ExternalLink, FileText, Network, Dna } from "lucide-react";

interface GeneAnnotation {
  gene_id: string;
  symbol: string;
  name: string;
  description: string;
  pathways?: Array<{ id: string; name: string }>;
  interactions?: Array<{ partner: string; score: number }>;
  publications?: Array<{ pmid: string; title: string }>;
  go_terms?: Array<{ id: string; term: string; category: string }>;
  source: string;
}

interface AnnotationDisplayProps {
  annotation: GeneAnnotation;
}

export function AnnotationDisplay({ annotation }: AnnotationDisplayProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Dna className="h-5 w-5" />
              {annotation.symbol}
            </CardTitle>
            <CardDescription>{annotation.name}</CardDescription>
          </div>
          <Badge variant="outline">{annotation.source}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="pathways">Pathways</TabsTrigger>
            <TabsTrigger value="interactions">Interactions</TabsTrigger>
            <TabsTrigger value="literature">Literature</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div>
              <h4 className="text-sm font-medium mb-2">Gene ID</h4>
              <p className="text-sm text-muted-foreground">{annotation.gene_id}</p>
            </div>

            <Separator />

            <div>
              <h4 className="text-sm font-medium mb-2">Description</h4>
              <p className="text-sm text-muted-foreground">{annotation.description}</p>
            </div>

            {annotation.go_terms && annotation.go_terms.length > 0 && (
              <>
                <Separator />
                <div>
                  <h4 className="text-sm font-medium mb-2">GO Terms</h4>
                  <ScrollArea className="h-[200px]">
                    <div className="space-y-2">
                      {annotation.go_terms.map((term, index) => (
                        <div key={index} className="border rounded-lg p-3">
                          <div className="flex items-center justify-between mb-1">
                            <Badge variant="secondary" className="text-xs">
                              {term.category}
                            </Badge>
                            <span className="text-xs text-muted-foreground">{term.id}</span>
                          </div>
                          <p className="text-sm">{term.term}</p>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              </>
            )}
          </TabsContent>

          {/* Pathways Tab */}
          <TabsContent value="pathways" className="space-y-4">
            {annotation.pathways && annotation.pathways.length > 0 ? (
              <ScrollArea className="h-[300px]">
                <div className="space-y-2">
                  {annotation.pathways.map((pathway, index) => (
                    <div
                      key={index}
                      className="border rounded-lg p-3 hover:bg-accent transition-colors cursor-pointer"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{pathway.name}</h4>
                          <p className="text-xs text-muted-foreground mt-1">{pathway.id}</p>
                        </div>
                        <ExternalLink className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No pathway information available
              </div>
            )}
          </TabsContent>

          {/* Interactions Tab */}
          <TabsContent value="interactions" className="space-y-4">
            {annotation.interactions && annotation.interactions.length > 0 ? (
              <ScrollArea className="h-[300px]">
                <div className="space-y-2">
                  {annotation.interactions.map((interaction, index) => (
                    <div key={index} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Network className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium text-sm">{interaction.partner}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">Confidence:</span>
                          <Badge variant={interaction.score > 0.7 ? "default" : "secondary"}>
                            {(interaction.score * 100).toFixed(0)}%
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No interaction data available
              </div>
            )}
          </TabsContent>

          {/* Literature Tab */}
          <TabsContent value="literature" className="space-y-4">
            {annotation.publications && annotation.publications.length > 0 ? (
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {annotation.publications.map((pub, index) => (
                    <div
                      key={index}
                      className="border rounded-lg p-3 hover:bg-accent transition-colors cursor-pointer"
                    >
                      <div className="flex items-start gap-3">
                        <FileText className="h-4 w-4 text-muted-foreground mt-1" />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{pub.title}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">
                              PMID: {pub.pmid}
                            </Badge>
                            <ExternalLink className="h-3 w-3 text-muted-foreground" />
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                No publications available
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
