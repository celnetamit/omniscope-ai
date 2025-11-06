'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Search,
  BookOpen,
  Video,
  MessageCircle,
  Download,
  ExternalLink,
  Play,
  FileText,
  Lightbulb,
  Zap,
  Users,
  Mail
} from 'lucide-react';

const quickStartGuides = [
  {
    title: 'Getting Started with OmniScope AI',
    description: 'Learn the basics of multi-omics data analysis',
    duration: '10 min',
    level: 'Beginner',
    icon: Zap,
    steps: [
      'Upload your first dataset',
      'Create a basic pipeline',
      'Run model training',
      'Analyze biomarkers'
    ]
  },
  {
    title: 'Data Harbor: File Upload & Analysis',
    description: 'Master file upload and automated analysis features',
    duration: '15 min',
    level: 'Beginner',
    icon: FileText,
    steps: [
      'Supported file formats',
      'Data quality assessment',
      'Missing value handling',
      'Export analysis reports'
    ]
  },
  {
    title: 'The Weaver: Pipeline Creation',
    description: 'Build complex multi-omics analysis workflows',
    duration: '20 min',
    level: 'Intermediate',
    icon: BookOpen,
    steps: [
      'Drag-and-drop interface',
      'Node configuration',
      'AI-powered suggestions',
      'Pipeline validation'
    ]
  },
  {
    title: 'Advanced Biomarker Discovery',
    description: 'Discover and interpret biomarkers with AI assistance',
    duration: '25 min',
    level: 'Advanced',
    icon: Lightbulb,
    steps: [
      'Feature importance analysis',
      'Statistical significance',
      'Biological interpretation',
      'Literature integration'
    ]
  }
];

const videoTutorials = [
  {
    title: 'OmniScope AI Overview',
    description: 'Complete platform walkthrough and key features',
    duration: '12:34',
    thumbnail: '/api/placeholder/320/180',
    category: 'Overview'
  },
  {
    title: 'Multi-omics Data Integration',
    description: 'Learn how to integrate genomics, proteomics, and metabolomics data',
    duration: '18:45',
    thumbnail: '/api/placeholder/320/180',
    category: 'Integration'
  },
  {
    title: 'Machine Learning for Biomarker Discovery',
    description: 'Advanced techniques for identifying disease biomarkers',
    duration: '22:15',
    thumbnail: '/api/placeholder/320/180',
    category: 'ML'
  },
  {
    title: 'Interpreting Results with AI',
    description: 'Use AI assistance to understand your analysis results',
    duration: '15:30',
    thumbnail: '/api/placeholder/320/180',
    category: 'AI'
  }
];

const faqItems = [
  {
    question: 'What file formats are supported?',
    answer: 'OmniScope AI supports CSV, TSV, Excel (.xlsx), and various bioinformatics formats including VCF, GFF, and FASTA files.',
    category: 'Data'
  },
  {
    question: 'How do I handle missing values in my dataset?',
    answer: 'The platform automatically detects missing values and suggests appropriate imputation methods based on your data type and missing percentage.',
    category: 'Data'
  },
  {
    question: 'Can I integrate multiple omics datasets?',
    answer: 'Yes! The Weaver module supports multi-omics integration using advanced methods like MOFA+ for factor analysis across different data types.',
    category: 'Integration'
  },
  {
    question: 'How accurate are the AI suggestions?',
    answer: 'Our AI suggestions are based on established bioinformatics workflows and best practices, with accuracy improving through user feedback.',
    category: 'AI'
  },
  {
    question: 'Is my data secure and private?',
    answer: 'All data is processed locally and encrypted. We follow GDPR and HIPAA compliance standards for data protection.',
    category: 'Security'
  },
  {
    question: 'How do I export my results?',
    answer: 'Results can be exported in multiple formats including PDF reports, CSV data files, and interactive visualizations.',
    category: 'Export'
  }
];

export function HelpCenter() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const filteredFAQ = faqItems.filter(item => 
    (selectedCategory === 'all' || item.category.toLowerCase() === selectedCategory) &&
    (item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
     item.answer.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Help Center</h1>
        <p className="text-lg text-muted-foreground">
          Everything you need to master OmniScope AI
        </p>
      </div>

      {/* Search */}
      <div className="max-w-md mx-auto">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search help articles..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <Tabs defaultValue="guides" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="guides">Quick Start</TabsTrigger>
          <TabsTrigger value="videos">Video Tutorials</TabsTrigger>
          <TabsTrigger value="faq">FAQ</TabsTrigger>
          <TabsTrigger value="support">Support</TabsTrigger>
        </TabsList>

        {/* Quick Start Guides */}
        <TabsContent value="guides" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {quickStartGuides.map((guide, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <guide.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{guide.title}</CardTitle>
                        <CardDescription>{guide.description}</CardDescription>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="secondary">{guide.level}</Badge>
                    <Badge variant="outline">{guide.duration}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 mb-4">
                    {guide.steps.map((step, stepIndex) => (
                      <div key={stepIndex} className="flex items-center gap-2 text-sm">
                        <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
                          {stepIndex + 1}
                        </div>
                        <span>{step}</span>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full">
                    <Play className="mr-2 h-4 w-4" />
                    Start Guide
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Video Tutorials */}
        <TabsContent value="videos" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {videoTutorials.map((video, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <div className="relative">
                  <div className="aspect-video bg-muted rounded-t-lg flex items-center justify-center">
                    <Play className="h-12 w-12 text-muted-foreground" />
                  </div>
                  <Badge className="absolute top-2 right-2">{video.duration}</Badge>
                </div>
                <CardHeader>
                  <CardTitle className="text-base">{video.title}</CardTitle>
                  <CardDescription>{video.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <Badge variant="outline">{video.category}</Badge>
                    <Button size="sm">
                      <Video className="mr-2 h-4 w-4" />
                      Watch
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* FAQ */}
        <TabsContent value="faq" className="space-y-6">
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={selectedCategory === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory('all')}
            >
              All
            </Button>
            {['Data', 'Integration', 'AI', 'Security', 'Export'].map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category.toLowerCase() ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(category.toLowerCase())}
              >
                {category}
              </Button>
            ))}
          </div>

          <div className="space-y-4">
            {filteredFAQ.map((item, index) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{item.question}</CardTitle>
                    <Badge variant="outline">{item.category}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{item.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Support */}
        <TabsContent value="support" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <MessageCircle className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Live Chat</CardTitle>
                <CardDescription>
                  Get instant help from our support team
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full">Start Chat</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Mail className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Email Support</CardTitle>
                <CardDescription>
                  Send us a detailed message about your issue
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Contact Us
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Users className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Community Forum</CardTitle>
                <CardDescription>
                  Connect with other researchers and experts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Join Forum
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Documentation</CardTitle>
              <CardDescription>
                Comprehensive guides and API documentation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <Button variant="outline" className="justify-start">
                  <BookOpen className="mr-2 h-4 w-4" />
                  User Manual
                </Button>
                <Button variant="outline" className="justify-start">
                  <FileText className="mr-2 h-4 w-4" />
                  API Documentation
                </Button>
                <Button variant="outline" className="justify-start">
                  <Download className="mr-2 h-4 w-4" />
                  Sample Datasets
                </Button>
                <Button variant="outline" className="justify-start">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Best Practices
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}