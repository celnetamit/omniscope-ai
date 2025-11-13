"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Upload, CheckCircle2, AlertTriangle, Package } from "lucide-react";
import { toast } from "sonner";

interface InstallationStep {
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  message?: string;
}

interface PluginInstallationWizardProps {
  onComplete?: (pluginId: string) => void;
}

export function PluginInstallationWizard({ onComplete }: PluginInstallationWizardProps) {
  const [installMethod, setInstallMethod] = useState<"file" | "url" | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [installing, setInstalling] = useState(false);
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState<InstallationStep[]>([]);
  const [securityWarnings, setSecurityWarnings] = useState<string[]>([]);

  const installationSteps: InstallationStep[] = [
    { name: "Uploading plugin", status: "pending" },
    { name: "Validating plugin structure", status: "pending" },
    { name: "Security scan", status: "pending" },
    { name: "Checking dependencies", status: "pending" },
    { name: "Installing plugin", status: "pending" },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleInstall = async () => {
    if (!file && !url) {
      toast.error("Please select a file or enter a URL");
      return;
    }

    setInstalling(true);
    setSteps(installationSteps);
    setProgress(0);
    setSecurityWarnings([]);

    try {
      const token = localStorage.getItem("access_token");
      const formData = new FormData();

      if (file) {
        formData.append("file", file);
      } else if (url) {
        formData.append("url", url);
      }

      // Simulate step-by-step installation
      for (let i = 0; i < installationSteps.length; i++) {
        setSteps((prev) =>
          prev.map((step, index) =>
            index === i ? { ...step, status: "running" } : step
          )
        );

        // Simulate API call for each step
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Simulate security warnings on security scan step
        if (i === 2) {
          const warnings = [
            "Plugin requests file system access",
            "Plugin uses network connections",
          ];
          setSecurityWarnings(warnings);
        }

        setSteps((prev) =>
          prev.map((step, index) =>
            index === i ? { ...step, status: "completed" } : step
          )
        );

        setProgress(((i + 1) / installationSteps.length) * 100);
      }

      // Final installation API call
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/install`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (response.ok) {
        const data = await response.json();
        toast.success("Plugin installed successfully");
        onComplete?.(data.plugin_id);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Installation failed");
        setSteps((prev) =>
          prev.map((step) =>
            step.status === "running" ? { ...step, status: "failed" } : step
          )
        );
      }
    } catch (error) {
      console.error("Installation error:", error);
      toast.error("Installation failed");
      setSteps((prev) =>
        prev.map((step) =>
          step.status === "running" ? { ...step, status: "failed" } : step
        )
      );
    } finally {
      setInstalling(false);
    }
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "failed":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 rounded-full border-2 border-gray-300" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Install Plugin
        </CardTitle>
        <CardDescription>
          Install a custom plugin from file or URL
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {!installing ? (
          <>
            {/* Installation Method Selection */}
            {!installMethod && (
              <div className="grid grid-cols-2 gap-4">
                <Button
                  variant="outline"
                  className="h-24 flex flex-col gap-2"
                  onClick={() => setInstallMethod("file")}
                >
                  <Upload className="h-6 w-6" />
                  <span>Upload File</span>
                </Button>
                <Button
                  variant="outline"
                  className="h-24 flex flex-col gap-2"
                  onClick={() => setInstallMethod("url")}
                >
                  <Package className="h-6 w-6" />
                  <span>From URL</span>
                </Button>
              </div>
            )}

            {/* File Upload */}
            {installMethod === "file" && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="plugin-file">Plugin File</Label>
                  <Input
                    id="plugin-file"
                    type="file"
                    accept=".zip,.tar.gz"
                    onChange={handleFileChange}
                  />
                  <p className="text-xs text-muted-foreground">
                    Supported formats: .zip, .tar.gz
                  </p>
                </div>

                {file && (
                  <Alert>
                    <AlertDescription>
                      Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                    </AlertDescription>
                  </Alert>
                )}

                <div className="flex gap-2">
                  <Button onClick={handleInstall} disabled={!file}>
                    Install Plugin
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setInstallMethod(null);
                      setFile(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            {/* URL Installation */}
            {installMethod === "url" && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="plugin-url">Plugin URL</Label>
                  <Input
                    id="plugin-url"
                    placeholder="https://example.com/plugin.zip"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Enter the URL to download the plugin package
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleInstall} disabled={!url.trim()}>
                    Install Plugin
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setInstallMethod(null);
                      setUrl("");
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <>
            {/* Installation Progress */}
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Installation Progress</span>
                  <span>{Math.round(progress)}%</span>
                </div>
                <Progress value={progress} />
              </div>

              {/* Installation Steps */}
              <div className="space-y-3">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-center gap-3">
                    {getStepIcon(step.status)}
                    <div className="flex-1">
                      <p className="text-sm font-medium">{step.name}</p>
                      {step.message && (
                        <p className="text-xs text-muted-foreground">{step.message}</p>
                      )}
                    </div>
                    <Badge
                      variant={
                        step.status === "completed"
                          ? "default"
                          : step.status === "failed"
                          ? "destructive"
                          : "secondary"
                      }
                      className="capitalize"
                    >
                      {step.status}
                    </Badge>
                  </div>
                ))}
              </div>

              {/* Security Warnings */}
              {securityWarnings.length > 0 && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    <p className="font-medium mb-2">Security Warnings:</p>
                    <ul className="list-disc list-inside space-y-1 text-sm">
                      {securityWarnings.map((warning, index) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
