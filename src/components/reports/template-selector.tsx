"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, Plus, Eye, Edit, Trash2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  sections: string[];
  format: string;
  is_custom: boolean;
  created_at?: string;
}

interface TemplateSelectorProps {
  templates: ReportTemplate[];
  selectedTemplateId?: string;
  onSelect: (templateId: string) => void;
  onCreateTemplate?: (template: Omit<ReportTemplate, "id" | "created_at">) => void;
  onDeleteTemplate?: (templateId: string) => void;
}

export function TemplateSelector({
  templates,
  selectedTemplateId,
  onSelect,
  onCreateTemplate,
  onDeleteTemplate,
}: TemplateSelectorProps) {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState<ReportTemplate | null>(null);
  const [newTemplate, setNewTemplate] = useState({
    name: "",
    description: "",
    sections: "Introduction\nMethods\nResults\nDiscussion\nReferences",
    format: "pdf",
  });

  const handleCreateTemplate = () => {
    if (!newTemplate.name.trim()) {
      toast.error("Please enter a template name");
      return;
    }

    const sections = newTemplate.sections
      .split("\n")
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    onCreateTemplate?.({
      name: newTemplate.name,
      description: newTemplate.description,
      sections,
      format: newTemplate.format,
      is_custom: true,
    });

    setNewTemplate({
      name: "",
      description: "",
      sections: "Introduction\nMethods\nResults\nDiscussion\nReferences",
      format: "pdf",
    });
    setCreateDialogOpen(false);
    toast.success("Template created successfully");
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Report Templates</CardTitle>
              <CardDescription>
                Choose a template or create your own custom template
              </CardDescription>
            </div>
            {onCreateTemplate && (
              <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    New Template
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Custom Template</DialogTitle>
                    <DialogDescription>
                      Define a custom report structure for your needs
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="template-name">Template Name</Label>
                      <Input
                        id="template-name"
                        placeholder="e.g., Clinical Trial Report"
                        value={newTemplate.name}
                        onChange={(e) =>
                          setNewTemplate({ ...newTemplate, name: e.target.value })
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="template-description">Description</Label>
                      <Input
                        id="template-description"
                        placeholder="Brief description of the template"
                        value={newTemplate.description}
                        onChange={(e) =>
                          setNewTemplate({ ...newTemplate, description: e.target.value })
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="template-sections">Sections (one per line)</Label>
                      <Textarea
                        id="template-sections"
                        rows={8}
                        value={newTemplate.sections}
                        onChange={(e) =>
                          setNewTemplate({ ...newTemplate, sections: e.target.value })
                        }
                      />
                    </div>

                    <Button onClick={handleCreateTemplate} className="w-full">
                      Create Template
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px]">
            <div className="space-y-3">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedTemplateId === template.id
                      ? "border-primary bg-primary/5"
                      : "hover:border-primary/50"
                  }`}
                  onClick={() => onSelect(template.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <FileText className="h-4 w-4" />
                        <h4 className="font-medium">{template.name}</h4>
                        {template.is_custom && (
                          <Badge variant="secondary" className="text-xs">
                            Custom
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {template.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {template.sections.slice(0, 3).map((section, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {section}
                          </Badge>
                        ))}
                        {template.sections.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{template.sections.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-1 ml-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={(e) => {
                          e.stopPropagation();
                          setPreviewTemplate(template);
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {template.is_custom && onDeleteTemplate && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (
                              confirm(
                                `Are you sure you want to delete "${template.name}"?`
                              )
                            ) {
                              onDeleteTemplate(template.id);
                              toast.success("Template deleted");
                            }
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Preview Dialog */}
      <Dialog
        open={previewTemplate !== null}
        onOpenChange={(open) => !open && setPreviewTemplate(null)}
      >
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{previewTemplate?.name}</DialogTitle>
            <DialogDescription>{previewTemplate?.description}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium mb-2">Template Structure</h4>
              <div className="space-y-2">
                {previewTemplate?.sections.map((section, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-2 border rounded-lg"
                  >
                    <Badge variant="outline">{index + 1}</Badge>
                    <span className="text-sm">{section}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-muted-foreground">
                Format: <Badge variant="secondary">{previewTemplate?.format.toUpperCase()}</Badge>
              </div>
              {previewTemplate?.created_at && (
                <div className="text-sm text-muted-foreground">
                  Created: {new Date(previewTemplate.created_at).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
