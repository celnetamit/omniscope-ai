"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Settings, Play, Trash2, Loader2, AlertCircle } from "lucide-react";
import { toast } from "sonner";

interface PluginConfig {
  [key: string]: any;
}

interface Plugin {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  enabled: boolean;
  config: PluginConfig;
  permissions: string[];
  status: "active" | "inactive" | "error";
  last_run?: string;
  error_message?: string;
}

interface PluginConfigInterfaceProps {
  pluginId: string;
}

export function PluginConfigInterface({ pluginId }: PluginConfigInterfaceProps) {
  const [plugin, setPlugin] = useState<Plugin | null>(null);
  const [config, setConfig] = useState<PluginConfig>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    fetchPlugin();
  }, [pluginId]);

  const fetchPlugin = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/${pluginId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPlugin(data);
        setConfig(data.config || {});
      } else {
        toast.error("Failed to load plugin");
      }
    } catch (error) {
      console.error("Error fetching plugin:", error);
      toast.error("Failed to load plugin");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/${pluginId}/config`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ config }),
        }
      );

      if (response.ok) {
        toast.success("Configuration saved");
        fetchPlugin();
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to save configuration");
      }
    } catch (error) {
      console.error("Save error:", error);
      toast.error("Failed to save configuration");
    } finally {
      setSaving(false);
    }
  };

  const handleToggleEnabled = async () => {
    if (!plugin) return;

    try {
      const token = localStorage.getItem("access_token");
      const endpoint = plugin.enabled ? "disable" : "enable";
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/${pluginId}/${endpoint}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        toast.success(`Plugin ${plugin.enabled ? "disabled" : "enabled"}`);
        fetchPlugin();
      } else {
        toast.error("Failed to toggle plugin");
      }
    } catch (error) {
      console.error("Toggle error:", error);
      toast.error("Failed to toggle plugin");
    }
  };

  const handleExecute = async () => {
    setExecuting(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/${pluginId}/execute`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ config }),
        }
      );

      if (response.ok) {
        const result = await response.json();
        toast.success("Plugin executed successfully");
        console.log("Plugin result:", result);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Execution failed");
      }
    } catch (error) {
      console.error("Execution error:", error);
      toast.error("Execution failed");
    } finally {
      setExecuting(false);
    }
  };

  const handleUninstall = async () => {
    if (!confirm(`Are you sure you want to uninstall ${plugin?.name}?`)) {
      return;
    }

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/${pluginId}/uninstall`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        toast.success("Plugin uninstalled");
        // Redirect or refresh
      } else {
        toast.error("Failed to uninstall plugin");
      }
    } catch (error) {
      console.error("Uninstall error:", error);
      toast.error("Failed to uninstall plugin");
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (!plugin) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground">Plugin not found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Plugin Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                {plugin.name}
              </CardTitle>
              <CardDescription>
                Version {plugin.version} by {plugin.author}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  plugin.status === "active"
                    ? "default"
                    : plugin.status === "error"
                    ? "destructive"
                    : "secondary"
                }
              >
                {plugin.status}
              </Badge>
              <Switch checked={plugin.enabled} onCheckedChange={handleToggleEnabled} />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">{plugin.description}</p>

          {plugin.error_message && (
            <div className="flex items-start gap-2 p-3 border border-red-200 rounded-lg bg-red-50 dark:bg-red-950 mb-4">
              <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-red-900 dark:text-red-100">
                  Error
                </p>
                <p className="text-sm text-red-700 dark:text-red-300">
                  {plugin.error_message}
                </p>
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <Button onClick={handleExecute} disabled={!plugin.enabled || executing}>
              {executing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Execute Plugin
                </>
              )}
            </Button>
            <Button variant="destructive" onClick={handleUninstall}>
              <Trash2 className="mr-2 h-4 w-4" />
              Uninstall
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Configuration</CardTitle>
          <CardDescription>Configure plugin settings and parameters</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="config" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="config">Settings</TabsTrigger>
              <TabsTrigger value="permissions">Permissions</TabsTrigger>
            </TabsList>

            {/* Configuration Tab */}
            <TabsContent value="config" className="space-y-4">
              <ScrollArea className="h-[400px]">
                <div className="space-y-4 pr-4">
                  {Object.keys(config).length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">
                      No configuration options available
                    </p>
                  ) : (
                    Object.entries(config).map(([key, value]) => (
                      <div key={key} className="space-y-2">
                        <Label htmlFor={key} className="capitalize">
                          {key.replace(/_/g, " ")}
                        </Label>
                        {typeof value === "boolean" ? (
                          <Switch
                            id={key}
                            checked={value}
                            onCheckedChange={(checked) =>
                              setConfig({ ...config, [key]: checked })
                            }
                          />
                        ) : typeof value === "string" && value.length > 50 ? (
                          <Textarea
                            id={key}
                            value={value}
                            onChange={(e) =>
                              setConfig({ ...config, [key]: e.target.value })
                            }
                            rows={3}
                          />
                        ) : (
                          <Input
                            id={key}
                            value={String(value)}
                            onChange={(e) =>
                              setConfig({ ...config, [key]: e.target.value })
                            }
                          />
                        )}
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>

              <Separator />

              <Button onClick={handleSaveConfig} disabled={saving} className="w-full">
                {saving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  "Save Configuration"
                )}
              </Button>
            </TabsContent>

            {/* Permissions Tab */}
            <TabsContent value="permissions" className="space-y-4">
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  This plugin requires the following permissions:
                </p>
                {plugin.permissions.map((permission, index) => (
                  <div key={index} className="flex items-center gap-2 p-3 border rounded-lg">
                    <Badge variant="outline">{permission}</Badge>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
