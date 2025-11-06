'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Brain,
  Search,
  MessageSquare,
  ExternalLink,
  TrendingUp,
  Filter,
  Download,
  BookOpen,
  Lightbulb,
  Target,
  Dna,
  Microscope,
  FlaskConical
} from 'lucide-react';

interface Biomarker {
  gene_id: string;
  gene_name: string;
  type: 'gene' | 'protein' | 'metabolite';
  importance_score: number;
  p_value: number;
  external_links: Record<string, string>;
}

interface BiomarkerExplanation {
  gene_id: string;
  gene_name: string;
  explanation: string;
  socratic_question: string;
  related_concepts: string[];
  learn_more_link: string;
}

interface QueryResponse {
  query: string;
  response: string;
  data: Array<{
    gene_name: string;
    importance_score: number;
  }>;
}

const mockTrainingJobs = [
  { job_id: 'a469f275-3b36-4dd2-8b4e-5ff4cdc9a49e', name: 'Cancer Classification Model' },
  { job_id: 'job_002', name: 'Biomarker Discovery' },
  { job_id: 'job_003', name: 'Drug Response Prediction' }
];

export function InsightEngine() {
  const [selectedModel, setSelectedModel] = useState('');
  const [biomarkers, setBiomarkers] = useState<Biomarker[]>([]);
  const [selectedBiomarker, setSelectedBiomarker] = useState<Biomarker | null>(null);
  const [explanation, setExplanation] = useState<BiomarkerExplanation | null>(null);
  const [query, setQuery] = useState('');
  const [queryResponse, setQueryResponse] = useState<QueryResponse | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('importance');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (selectedModel) {
      fetchBiomarkers();
    }
  }, [selectedModel]);

  const fetchBiomarkers = async () => {
    if (!selectedModel) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/proxy?url=/api/results/${selectedModel}/biomarkers`);
      const data = await response.json();
      setBiomarkers(data.biomarkers || []);
    } catch (error) {
      console.error('Failed to fetch biomarkers:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchExplanation = async (geneId: string) => {
    if (!selectedModel) return;
    
    try {
      const response = await fetch(`/api/proxy?url=/api/results/${selectedModel}/biomarkers/${geneId}/explain`);
      const data = await response.json();
      setExplanation(data);
    } catch (error) {
      console.error('Failed to fetch explanation:', error);
    }
  };

  const submitQuery = async () => {
    if (!query.trim() || !selectedModel) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/proxy?url=/api/results/${selectedModel}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await response.json();
      setQueryResponse(data);
    } catch (error) {
      console.error('Failed to submit query:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'gene': return <Dna className="h-4 w-4 text-blue-500" />;
      case 'protein': return <Microscope className="h-4 w-4 text-green-500" />;
      case 'metabolite': return <FlaskConical className="h-4 w-4 text-purple-500" />;
      default: return <Target className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'gene': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300';
      case 'protein': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
      case 'metabolite': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getImportanceColor = (score: number) => {
    if (score >= 0.9) return 'text-red-600 font-bold';
    if (score >= 0.8) return 'text-orange-600 font-semibold';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const filteredBiomarkers = biomarkers
    .filter(b => 
      (typeFilter === 'all' || b.type === typeFilter) &&
      (searchTerm === '' || 
       b.gene_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
       b.gene_id.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'importance': return b.importance_score - a.importance_score;
        case 'pvalue': return a.p_value - b.p_value;
        case 'name': return a.gene_name.localeCompare(b.gene_name);
        default: return 0;
      }
    });

  const sampleQueries = [
    "What are the top 5 biomarkers for cancer diagnosis?",
    "Explain the role of p53 in cancer development",
    "Which biomarkers are related to DNA repair mechanisms?",
    "How do these biomarkers interact with each other?",
    "What pathways are most affected by these biomarkers?"
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8" />
            Insight Engine
          </h1>
          <p className="text-muted-foreground">
            Discover and interpret biomarkers with AI-powered analysis and Socratic learning
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Results
          </Button>
        </div>
      </div>

      {/* Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Training Model</CardTitle>
          <CardDescription>
            Choose a completed training job to analyze biomarkers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={selectedModel} onValueChange={setSelectedModel}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a trained model..." />
            </SelectTrigger>
            <SelectContent>
              {mockTrainingJobs.map(job => (
                <SelectItem key={job.job_id} value={job.job_id}>
                  {job.name} ({job.job_id.slice(0, 8)}...)
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {selectedModel && (
        <Tabs defaultValue="biomarkers" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="biomarkers">Biomarker Discovery</TabsTrigger>
            <TabsTrigger value="explanation">Detailed Analysis</TabsTrigger>
            <TabsTrigger value="query">AI Assistant</TabsTrigger>
          </TabsList>

          <TabsContent value="biomarkers" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-4">
              {/* Filters */}
              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Filters & Search</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Search</label>
                      <div className="relative mt-1">
                        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Search biomarkers..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-10"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Type</label>
                      <Select value={typeFilter} onValueChange={setTypeFilter}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Types</SelectItem>
                          <SelectItem value="gene">Genes</SelectItem>
                          <SelectItem value="protein">Proteins</SelectItem>
                          <SelectItem value="metabolite">Metabolites</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Sort By</label>
                      <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="importance">Importance Score</SelectItem>
                          <SelectItem value="pvalue">P-Value</SelectItem>
                          <SelectItem value="name">Name</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="pt-4 border-t">
                      <p className="text-sm font-medium mb-2">Summary</p>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Total:</span>
                          <span className="font-medium">{biomarkers.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Filtered:</span>
                          <span className="font-medium">{filteredBiomarkers.length}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>High Impact:</span>
                          <span className="font-medium text-red-600">
                            {filteredBiomarkers.filter(b => b.importance_score >= 0.9).length}
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Biomarkers Table */}
              <div className="lg:col-span-3">
                <Card>
                  <CardHeader>
                    <CardTitle>Discovered Biomarkers</CardTitle>
                    <CardDescription>
                      Ranked by importance score and statistical significance
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {isLoading ? (
                      <div className="text-center py-8">
                        <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
                        <p className="text-muted-foreground">Loading biomarkers...</p>
                      </div>
                    ) : filteredBiomarkers.length === 0 ? (
                      <div className="text-center py-8">
                        <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                        <p className="text-muted-foreground">No biomarkers found</p>
                        <p className="text-sm text-muted-foreground">
                          Try adjusting your filters or select a different model
                        </p>
                      </div>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Biomarker</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Importance</TableHead>
                            <TableHead>P-Value</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {filteredBiomarkers.map((biomarker) => (
                            <TableRow 
                              key={biomarker.gene_id}
                              className="cursor-pointer hover:bg-accent"
                              onClick={() => {
                                setSelectedBiomarker(biomarker);
                                fetchExplanation(biomarker.gene_id);
                              }}
                            >
                              <TableCell>
                                <div>
                                  <p className="font-medium">{biomarker.gene_name}</p>
                                  <p className="text-xs text-muted-foreground font-mono">
                                    {biomarker.gene_id}
                                  </p>
                                </div>
                              </TableCell>
                              <TableCell>
                                <Badge className={getTypeColor(biomarker.type)}>
                                  <div className="flex items-center gap-1">
                                    {getTypeIcon(biomarker.type)}
                                    {biomarker.type}
                                  </div>
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <span className={getImportanceColor(biomarker.importance_score)}>
                                  {biomarker.importance_score.toFixed(3)}
                                </span>
                              </TableCell>
                              <TableCell>
                                <span className={biomarker.p_value < 0.001 ? 'text-green-600 font-medium' : ''}>
                                  {biomarker.p_value.toExponential(2)}
                                </span>
                              </TableCell>
                              <TableCell>
                                <div className="flex gap-1">
                                  {Object.entries(biomarker.external_links).map(([db, url]) => (
                                    <Button
                                      key={db}
                                      variant="ghost"
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        window.open(url, '_blank');
                                      }}
                                    >
                                      <ExternalLink className="h-3 w-3" />
                                    </Button>
                                  ))}
                                </div>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="explanation" className="space-y-4">
            {selectedBiomarker && explanation ? (
              <div className="grid gap-6 lg:grid-cols-3">
                <div className="lg:col-span-2">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        {getTypeIcon(selectedBiomarker.type)}
                        {selectedBiomarker.gene_name}
                      </CardTitle>
                      <CardDescription>
                        {selectedBiomarker.gene_id} • Importance: {selectedBiomarker.importance_score.toFixed(3)}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Explanation */}
                      <div>
                        <h3 className="font-semibold mb-2 flex items-center gap-2">
                          <BookOpen className="h-4 w-4" />
                          Biological Significance
                        </h3>
                        <p className="text-muted-foreground leading-relaxed">
                          {explanation.explanation}
                        </p>
                      </div>

                      {/* Socratic Question */}
                      <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <h3 className="font-semibold mb-2 flex items-center gap-2 text-blue-700 dark:text-blue-300">
                          <Lightbulb className="h-4 w-4" />
                          Think Deeper
                        </h3>
                        <p className="text-blue-600 dark:text-blue-400">
                          {explanation.socratic_question}
                        </p>
                      </div>

                      {/* Related Concepts */}
                      <div>
                        <h3 className="font-semibold mb-3">Related Concepts</h3>
                        <div className="flex flex-wrap gap-2">
                          {explanation.related_concepts.map((concept) => (
                            <Badge key={concept} variant="outline">
                              {concept}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* External Resources */}
                      <div>
                        <h3 className="font-semibold mb-3">External Resources</h3>
                        <div className="space-y-2">
                          {Object.entries(selectedBiomarker.external_links).map(([db, url]) => (
                            <Button
                              key={db}
                              variant="outline"
                              className="w-full justify-start"
                              onClick={() => window.open(url, '_blank')}
                            >
                              <ExternalLink className="mr-2 h-4 w-4" />
                              View in {db}
                            </Button>
                          ))}
                          <Button
                            variant="outline"
                            className="w-full justify-start"
                            onClick={() => window.open(explanation.learn_more_link, '_blank')}
                          >
                            <BookOpen className="mr-2 h-4 w-4" />
                            Learn More
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div className="lg:col-span-1">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Quick Stats</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">
                          {selectedBiomarker.importance_score.toFixed(3)}
                        </div>
                        <div className="text-sm text-muted-foreground">Importance Score</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          {selectedBiomarker.p_value.toExponential(2)}
                        </div>
                        <div className="text-sm text-muted-foreground">P-Value</div>
                      </div>

                      <div className="text-center">
                        <Badge className={getTypeColor(selectedBiomarker.type)}>
                          <div className="flex items-center gap-1">
                            {getTypeIcon(selectedBiomarker.type)}
                            {selectedBiomarker.type}
                          </div>
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-16">
                  <Target className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg font-medium mb-2">No Biomarker Selected</p>
                  <p className="text-muted-foreground">
                    Click on a biomarker from the discovery tab to view detailed analysis
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="query" className="space-y-4">
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="h-5 w-5" />
                      AI Assistant
                    </CardTitle>
                    <CardDescription>
                      Ask questions about your biomarkers in natural language
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex gap-2">
                      <Input
                        placeholder="Ask about biomarkers, pathways, or biological processes..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && submitQuery()}
                        className="flex-1"
                      />
                      <Button onClick={submitQuery} disabled={!query.trim() || isLoading}>
                        <MessageSquare className="mr-2 h-4 w-4" />
                        Ask
                      </Button>
                    </div>

                    {queryResponse && (
                      <div className="space-y-4">
                        <div className="p-4 bg-muted/50 rounded-lg">
                          <p className="font-medium mb-2">Question:</p>
                          <p className="text-muted-foreground">{queryResponse.query}</p>
                        </div>
                        
                        <div className="p-4 border rounded-lg">
                          <p className="font-medium mb-2">AI Response:</p>
                          <p className="leading-relaxed">{queryResponse.response}</p>
                        </div>

                        {queryResponse.data && queryResponse.data.length > 0 && (
                          <div>
                            <p className="font-medium mb-2">Related Biomarkers:</p>
                            <div className="space-y-2">
                              {queryResponse.data.map((item, index) => (
                                <div key={index} className="flex justify-between items-center p-2 border rounded">
                                  <span>{item.gene_name}</span>
                                  <Badge variant="outline">
                                    {(item.importance_score * 100).toFixed(1)}%
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Sample Questions</CardTitle>
                    <CardDescription>
                      Try these example queries
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {sampleQueries.map((sampleQuery, index) => (
                        <Button
                          key={index}
                          variant="ghost"
                          className="w-full text-left justify-start h-auto p-3"
                          onClick={() => setQuery(sampleQuery)}
                        >
                          <div className="text-sm leading-relaxed">
                            {sampleQuery}
                          </div>
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}