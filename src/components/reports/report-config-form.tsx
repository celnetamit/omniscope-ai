"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Loader2, FileText, Download } from "lucide-react";
import { toast } from "sonner";

interface ReportConfig {
  title: string;
  abstract?: string;
  format: "pdf" | "docx" | "latex";
  citation_style: "apa" | "mla" | "chicago" | "nature" | "science";
  include_methods: boolean;
  include_figures: boolean;
  include_tables: boolean;
  include_references: boolean;
  template_id?: string;
  analysis_ids: string[];
}

interface ReportConfigFormProps {
  analyses: Array<{ id: string; name: string; type: string }>;
  templates?: Array<{ id: string; name: string; description: string }>;
  onSubmit: (config: ReportConfig) => void;
  loading?: boolean;
}

export function ReportConfigForm({
  analyses,
  templates = [],
  onSubmit,
  loading = false,
}: ReportConfigFormProps) {
  const [config, setConfig] = useState<ReportConfig>({
    title: "",
    abstract: "",
    format: "pdf",
    citation_style: "apa",
    include_methods: true,
    include_figures: true,
    include_tables: true,
    include_references: true,
    analysis_ids: [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!config.title.trim()) {
      toast.error("Please enter a report title");
      return;
    }

    if (config.analysis_ids.length === 0) {
      toast.error("Please select at least one analysis to include");
      return;
    }

    onSubmit(config);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Report Configuration
        </CardTitle>
        <CardDescription>
          Configure your publication-ready scientific report
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Report Title *</Label>
              <Input
                id="title"
                placeholder="Enter report title..."
                value={config.title}
                onChange={(e) => setConfig({ ...config, title: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="abstract">Abstract (Optional)</Label>
              <Textarea
                id="abstract"
                placeholder="Enter a brief abstract or summary..."
                value={config.abstract}
                onChange={(e) => setConfig({ ...config, abstract: e.target.value })}
                rows={4}
              />
            </div>
          </div>

          <Separator />

          {/* Format and Style */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="format">Output Format</Label>
              <Select
                value={config.format}
                onValueChange={(value: any) => setConfig({ ...config, format: value })}
              >
                <SelectTrigger id="format">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="docx">Word (DOCX)</SelectItem>
                  <SelectItem value="latex">LaTeX</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="citation-style">Citation Style</Label>
              <Select
                value={config.citation_style}
                onValueChange={(value: any) => setConfig({ ...config, citation_style: value })}
              >
                <SelectTrigger id="citation-style">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="apa">APA</SelectItem>
                  <SelectItem value="mla">MLA</SelectItem>
                  <SelectItem value="chicago">Chicago</SelectItem>
                  <SelectItem value="nature">Nature</SelectItem>
                  <SelectItem value="science">Science</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Template Selection */}
          {templates.length > 0 && (
            <div className="space-y-2">
              <Label htmlFor="template">Template (Optional)</Label>
              <Select
                value={config.template_id}
                onValueChange={(value) => setConfig({ ...config, template_id: value })}
              >
                <SelectTrigger id="template">
                  <SelectValue placeholder="Use default template" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Default Template</SelectItem>
                  {templates.map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      {template.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          <Separator />

          {/* Content Options */}
          <div className="space-y-4">
            <Label>Include in Report</Label>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="methods">Methods Section</Label>
                  <p className="text-sm text-muted-foreground">
                    Auto-generated from analysis pipeline
                  </p>
                </div>
                <Switch
                  id="methods"
                  checked={config.include_methods}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, include_methods: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="figures">Figures</Label>
                  <p className="text-sm text-muted-foreground">
                    Include all visualizations
                  </p>
                </div>
                <Switch
                  id="figures"
                  checked={config.include_figures}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, include_figures: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="tables">Tables</Label>
                  <p className="text-sm text-muted-foreground">
                    Include statistical tables
                  </p>
                </div>
                <Switch
                  id="tables"
                  checked={config.include_tables}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, include_tables: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="references">References</Label>
                  <p className="text-sm text-muted-foreground">
                    Bibliography and citations
                  </p>
                </div>
                <Switch
                  id="references"
                  checked={config.include_references}
                  onCheckedChange={(checked) =>
                    setConfig({ ...config, include_references: checked })
                  }
                />
              </div>
            </div>
          </div>

          <Separator />

          {/* Analysis Selection */}
          <div className="space-y-2">
            <Label>Select Analyses to Include *</Label>
            <div className="border rounded-md p-3 max-h-[200px] overflow-y-auto space-y-2">
              {analyses.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No analyses available
                </p>
              ) : (
                analyses.map((analysis) => (
                  <div key={analysis.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`analysis-${analysis.id}`}
                      checked={config.analysis_ids.includes(analysis.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setConfig({
                            ...config,
                            analysis_ids: [...config.analysis_ids, analysis.id],
                          });
                        } else {
                          setConfig({
                            ...config,
                            analysis_ids: config.analysis_ids.filter(
                              (id) => id !== analysis.id
                            ),
                          });
                        }
                      }}
                      className="rounded"
                    />
                    <label
                      htmlFor={`analysis-${analysis.id}`}
                      className="text-sm cursor-pointer flex-1"
                    >
                      <span className="font-medium">{analysis.name}</span>
                      <span className="text-muted-foreground ml-2">({analysis.type})</span>
                    </label>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Submit Button */}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Report...
              </>
            ) : (
              <>
                <Download className="mr-2 h-4 w-4" />
                Generate Report
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
