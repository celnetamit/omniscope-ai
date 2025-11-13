"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Download, Star, Package, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Plugin {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  category: string;
  rating: number;
  downloads: number;
  installed: boolean;
  enabled: boolean;
  tags: string[];
}

interface MarketplaceBrowserProps {
  onInstall?: (pluginId: string) => void;
}

export function MarketplaceBrowser({ onInstall }: MarketplaceBrowserProps) {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [filteredPlugins, setFilteredPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("popular");

  useEffect(() => {
    fetchPlugins();
  }, []);

  useEffect(() => {
    filterAndSortPlugins();
  }, [plugins, searchQuery, categoryFilter, sortBy]);

  const fetchPlugins = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/marketplace`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPlugins(data);
      } else {
        toast.error("Failed to load marketplace");
      }
    } catch (error) {
      console.error("Error fetching plugins:", error);
      toast.error("Failed to load marketplace");
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortPlugins = () => {
    let filtered = [...plugins];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (p) =>
          p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Apply category filter
    if (categoryFilter !== "all") {
      filtered = filtered.filter((p) => p.category === categoryFilter);
    }

    // Apply sorting
    switch (sortBy) {
      case "popular":
        filtered.sort((a, b) => b.downloads - a.downloads);
        break;
      case "rating":
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case "name":
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case "recent":
        // Assuming plugins are already sorted by recent
        break;
    }

    setFilteredPlugins(filtered);
  };

  const handleInstall = async (pluginId: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/plugins/install`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ plugin_id: pluginId }),
        }
      );

      if (response.ok) {
        toast.success("Plugin installed successfully");
        fetchPlugins();
        onInstall?.(pluginId);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Failed to install plugin");
      }
    } catch (error) {
      console.error("Install error:", error);
      toast.error("Failed to install plugin");
    }
  };

  const categories = ["all", ...new Set(plugins.map((p) => p.category))];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Plugin Marketplace
        </CardTitle>
        <CardDescription>
          Discover and install plugins to extend OmniScope functionality
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="space-y-4 mb-6">
          <div className="flex gap-2">
            <div className="flex-1">
              <Input
                placeholder="Search plugins..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <Button variant="outline" size="icon">
              <Search className="h-4 w-4" />
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat} value={cat}>
                      {cat === "all" ? "All Categories" : cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Sort By</label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="popular">Most Popular</SelectItem>
                  <SelectItem value="rating">Highest Rated</SelectItem>
                  <SelectItem value="name">Name (A-Z)</SelectItem>
                  <SelectItem value="recent">Recently Added</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Plugin List */}
        <ScrollArea className="h-[600px]">
          {loading ? (
            <div className="flex items-center justify-center h-[400px]">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredPlugins.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No plugins found matching your criteria
            </div>
          ) : (
            <div className="space-y-4">
              {filteredPlugins.map((plugin) => (
                <div key={plugin.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{plugin.name}</h4>
                        <Badge variant="outline">{plugin.version}</Badge>
                        {plugin.installed && (
                          <Badge variant="secondary">Installed</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        by {plugin.author}
                      </p>
                      <p className="text-sm text-muted-foreground mb-3">
                        {plugin.description}
                      </p>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-3">
                    {plugin.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>

                  {/* Stats and Actions */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span>{plugin.rating.toFixed(1)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Download className="h-4 w-4" />
                        <span>{plugin.downloads.toLocaleString()}</span>
                      </div>
                      <Badge variant="secondary">{plugin.category}</Badge>
                    </div>

                    {!plugin.installed ? (
                      <Button
                        size="sm"
                        onClick={() => handleInstall(plugin.id)}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Install
                      </Button>
                    ) : (
                      <Button size="sm" variant="outline" disabled>
                        Installed
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
