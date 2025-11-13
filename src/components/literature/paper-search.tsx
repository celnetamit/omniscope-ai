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
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Loader2, Search, FileText } from "lucide-react";
import { toast } from "sonner";

interface SearchFilters {
  query: string;
  max_results: number;
  sort_by: "relevance" | "date" | "citations";
  year_from?: number;
  year_to?: number;
  journal?: string;
}

interface Paper {
  pmid: string;
  title: string;
  abstract: string;
  authors: string[];
  journal: string;
  year: number;
  citations: number;
  relevance_score: number;
}

interface PaperSearchProps {
  onResults?: (papers: Paper[]) => void;
}

export function PaperSearch({ onResults }: PaperSearchProps) {
  const [filters, setFilters] = useState<SearchFilters>({
    query: "",
    max_results: 20,
    sort_by: "relevance",
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Paper[]>([]);

  const handleSearch = async () => {
    if (!filters.query.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/literature/search`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(filters),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setResults(data.papers || []);
        onResults?.(data.papers || []);
        toast.success(`Found ${data.papers?.length || 0} papers`);
      } else {
        const error = await response.json();
        toast.error(error.detail || "Search failed");
      }
    } catch (error) {
      console.error("Search error:", error);
      toast.error("Failed to search papers");
    } finally {
      setLoading(false);
    }
  };

  const currentYear = new Date().getFullYear();

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Literature Search
          </CardTitle>
          <CardDescription>
            Search PubMed for relevant research papers
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search Query */}
          <div className="space-y-2">
            <Label htmlFor="query">Search Query</Label>
            <div className="flex gap-2">
              <Input
                id="query"
                placeholder="Enter keywords, genes, diseases..."
                value={filters.query}
                onChange={(e) => setFilters({ ...filters, query: e.target.value })}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleSearch();
                  }
                }}
              />
              <Button onClick={handleSearch} disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sort">Sort By</Label>
              <Select
                value={filters.sort_by}
                onValueChange={(value: any) => setFilters({ ...filters, sort_by: value })}
              >
                <SelectTrigger id="sort">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevance</SelectItem>
                  <SelectItem value="date">Publication Date</SelectItem>
                  <SelectItem value="citations">Citation Count</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-results">
                Max Results: {filters.max_results}
              </Label>
              <Slider
                id="max-results"
                min={10}
                max={100}
                step={10}
                value={[filters.max_results]}
                onValueChange={([value]) =>
                  setFilters({ ...filters, max_results: value })
                }
              />
            </div>
          </div>

          {/* Year Range */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="year-from">Year From</Label>
              <Input
                id="year-from"
                type="number"
                min={1900}
                max={currentYear}
                placeholder="e.g., 2020"
                value={filters.year_from || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    year_from: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="year-to">Year To</Label>
              <Input
                id="year-to"
                type="number"
                min={1900}
                max={currentYear}
                placeholder="e.g., 2024"
                value={filters.year_to || ""}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    year_to: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
              />
            </div>
          </div>

          {/* Example Queries */}
          <div className="text-sm">
            <p className="text-muted-foreground mb-2">Example queries:</p>
            <div className="flex flex-wrap gap-2">
              <Badge
                variant="outline"
                className="cursor-pointer"
                onClick={() => setFilters({ ...filters, query: "BRCA1 breast cancer" })}
              >
                BRCA1 breast cancer
              </Badge>
              <Badge
                variant="outline"
                className="cursor-pointer"
                onClick={() =>
                  setFilters({ ...filters, query: "machine learning genomics" })
                }
              >
                machine learning genomics
              </Badge>
              <Badge
                variant="outline"
                className="cursor-pointer"
                onClick={() =>
                  setFilters({ ...filters, query: "multi-omics integration" })
                }
              >
                multi-omics integration
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results ({results.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {results.map((paper) => (
                <div key={paper.pmid} className="border rounded-lg p-4 hover:bg-accent transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-medium mb-1">{paper.title}</h4>
                      <p className="text-sm text-muted-foreground mb-2">
                        {paper.authors.slice(0, 3).join(", ")}
                        {paper.authors.length > 3 && ` et al.`}
                      </p>
                    </div>
                    <FileText className="h-5 w-5 text-muted-foreground" />
                  </div>

                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {paper.abstract}
                  </p>

                  <div className="flex items-center gap-3 text-xs">
                    <Badge variant="outline">PMID: {paper.pmid}</Badge>
                    <span className="text-muted-foreground">{paper.journal}</span>
                    <span className="text-muted-foreground">{paper.year}</span>
                    <span className="text-muted-foreground">
                      {paper.citations} citations
                    </span>
                    {paper.relevance_score && (
                      <Badge variant="secondary">
                        {(paper.relevance_score * 100).toFixed(0)}% relevant
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
