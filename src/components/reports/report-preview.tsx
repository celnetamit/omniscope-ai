"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Download, Eye, FileText, Image, Table } from "lucide-react";
import { toast } from "sonner";

interface ReportSection {
  title: string;
  content: string;
  type: "text" | "figure" | "table";
  order: number;
}

interface ReportPreviewData {
  id: string;
  title: string;
  abstract?: string;
  format: string;
  citation_style: string;
  sections: ReportSection[];
  references?: string[];
  generated_at: string;
  file_path?: string;
}

interface ReportPreviewProps {
  report: ReportPreviewData;
  onDownload?: () => void;
}

export function ReportPreview({ report, onDownload }: ReportPreviewProps) {
  const handleDownload = async () => {
    if (!report.file_path) {
      toast.error("Report file not available");
      return;
    }

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/reports/${report.id}/download`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `report-${report.id}.${report.format}`;
        link.click();
        URL.revokeObjectURL(url);
        toast.success("Report downloaded");
        onDownload?.();
      } else {
        toast.error("Failed to download report");
      }
    } catch (error) {
      console.error("Download error:", error);
      toast.error("Failed to download report");
    }
  };

  const getSectionIcon = (type: string) => {
    switch (type) {
      case "figure":
        return <Image className="h-4 w-4" />;
      case "table":
        return <Table className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-4">
      {/* Report Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">{report.title}</CardTitle>
              <div className="flex items-center gap-2 mb-3">
                <Badge variant="outline">{report.format.toUpperCase()}</Badge>
                <Badge variant="secondary">{report.citation_style.toUpperCase()}</Badge>
                <span className="text-sm text-muted-foreground">
                  Generated: {new Date(report.generated_at).toLocaleString()}
                </span>
              </div>
              {report.abstract && (
                <CardDescription className="text-base">{report.abstract}</CardDescription>
              )}
            </div>
            <Button onClick={handleDownload}>
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Report Content */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Report Preview
          </CardTitle>
          <CardDescription>
            Preview of the generated report content
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[600px] pr-4">
            <div className="space-y-6">
              {report.sections
                .sort((a, b) => a.order - b.order)
                .map((section, index) => (
                  <div key={index}>
                    {/* Section Header */}
                    <div className="flex items-center gap-2 mb-3">
                      {getSectionIcon(section.type)}
                      <h3 className="text-lg font-semibold">{section.title}</h3>
                      <Badge variant="outline" className="text-xs">
                        {section.type}
                      </Badge>
                    </div>

                    {/* Section Content */}
                    <div className="pl-6">
                      {section.type === "text" && (
                        <div className="prose prose-sm max-w-none">
                          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                            {section.content}
                          </p>
                        </div>
                      )}

                      {section.type === "figure" && (
                        <div className="border rounded-lg p-4 bg-muted/50">
                          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
                            <div className="text-center">
                              <Image className="h-12 w-12 mx-auto mb-2" />
                              <p className="text-sm">Figure: {section.title}</p>
                              <p className="text-xs mt-1">{section.content}</p>
                            </div>
                          </div>
                        </div>
                      )}

                      {section.type === "table" && (
                        <div className="border rounded-lg overflow-hidden">
                          <div className="bg-muted p-4">
                            <div className="flex items-center justify-center h-[150px] text-muted-foreground">
                              <div className="text-center">
                                <Table className="h-12 w-12 mx-auto mb-2" />
                                <p className="text-sm">Table: {section.title}</p>
                                <p className="text-xs mt-1">{section.content}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {index < report.sections.length - 1 && <Separator className="mt-6" />}
                  </div>
                ))}

              {/* References Section */}
              {report.references && report.references.length > 0 && (
                <>
                  <Separator />
                  <div>
                    <h3 className="text-lg font-semibold mb-3">References</h3>
                    <div className="pl-6 space-y-2">
                      {report.references.map((ref, index) => (
                        <div key={index} className="text-sm text-muted-foreground">
                          <span className="font-medium">[{index + 1}]</span> {ref}
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Report Metadata */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Report Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Report ID</p>
              <p className="font-mono">{report.id}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Format</p>
              <p className="font-medium">{report.format.toUpperCase()}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Citation Style</p>
              <p className="font-medium">{report.citation_style.toUpperCase()}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Sections</p>
              <p className="font-medium">{report.sections.length}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
