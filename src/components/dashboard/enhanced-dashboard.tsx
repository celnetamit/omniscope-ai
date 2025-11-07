'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '@/components/auth/auth-provider';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  Activity,
  Users,
  Database,
  Cpu,
  Brain,
  Upload,
  GitBranch,
  Zap,
  BarChart3,
  FileText,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react';

interface ModuleInfo {
  status: string;
  description: string;
  storage?: string;
  supported_formats?: string[];
  max_file_size?: string;
  features?: string[];
}

interface ModuleStatus {
  data_harbor: ModuleInfo;
  the_weaver: ModuleInfo;
  the_crucible: ModuleInfo;
  the_insight_engine: ModuleInfo;
}

interface EnhancedDashboardProps {
  moduleStatus: ModuleStatus | null;
  onTabChange: (tab: string) => void;
}

export function EnhancedDashboard({ moduleStatus, onTabChange }: EnhancedDashboardProps) {
  const { user } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [systemMetrics, setSystemMetrics] = useState({
    cpuUsage: 45,
    memoryUsage: 62,
    diskUsage: 38,
    networkActivity: 78
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      // Simulate changing metrics
      setSystemMetrics(prev => ({
        cpuUsage: Math.max(20, Math.min(90, prev.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(30, Math.min(95, prev.memoryUsage + (Math.random() - 0.5) * 8)),
        diskUsage: Math.max(20, Math.min(80, prev.diskUsage + (Math.random() - 0.5) * 5)),
        networkActivity: Math.max(10, Math.min(100, prev.networkActivity + (Math.random() - 0.5) * 15))
      }));
    }, 3000);

    return () => clearInterval(timer);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'complete':
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running':
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'error':
      case 'failed':
      case 'unknown':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 100
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Welcome Header */}
      <motion.div variants={itemVariants} className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              OmniScope AI
            </h1>
            <p className="text-xl text-muted-foreground">
              Multi-Omics Data Analysis Platform
            </p>
          </div>
        </div>
        
        {user && (
          <div className="flex items-center justify-center gap-2 text-muted-foreground">
            <span>{getGreeting()}, {user.name.split(' ')[0]}!</span>
            <span>•</span>
            <span>{currentTime.toLocaleDateString()}</span>
            <span>•</span>
            <span>{currentTime.toLocaleTimeString()}</span>
          </div>
        )}
      </motion.div>

      {/* Quick Stats */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Datasets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 text-green-500" />
              +2 from yesterday
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Jobs</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">
              2 training, 1 analysis
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Accuracy</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.2%</div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <TrendingUp className="h-3 w-3 text-green-500" />
              +2.1% from last week
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">
              +1 from last month
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* System Metrics */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Performance
            </CardTitle>
            <CardDescription>
              Real-time system metrics and resource usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>CPU Usage</span>
                  <span>{Math.round(systemMetrics.cpuUsage)}%</span>
                </div>
                <Progress value={systemMetrics.cpuUsage} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Memory</span>
                  <span>{Math.round(systemMetrics.memoryUsage)}%</span>
                </div>
                <Progress value={systemMetrics.memoryUsage} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Disk Usage</span>
                  <span>{Math.round(systemMetrics.diskUsage)}%</span>
                </div>
                <Progress value={systemMetrics.diskUsage} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Network</span>
                  <span>{Math.round(systemMetrics.networkActivity)}%</span>
                </div>
                <Progress value={systemMetrics.networkActivity} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Module Status */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5" />
              Module Status
            </CardTitle>
            <CardDescription>
              Real-time status of all integrated modules
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {moduleStatus && Object.entries(moduleStatus).map(([module, info], index) => {
                const moduleIcons = {
                  'data_harbor': Upload,
                  'the_weaver': GitBranch,
                  'the_crucible': Cpu,
                  'the_insight_engine': Brain
                };
                const Icon = moduleIcons[module as keyof typeof moduleIcons] || Cpu;
                
                return (
                  <motion.div
                    key={module}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="group"
                  >
                    <Card className="cursor-pointer hover:shadow-md transition-all duration-300 group-hover:scale-105"
                          onClick={() => {
                            const moduleMap: Record<string, string> = {
                              'data_harbor': 'data-harbor',
                              'the_weaver': 'the-weaver', 
                              'the_crucible': 'the-crucible',
                              'the_insight_engine': 'insight-engine'
                            };
                            onTabChange(moduleMap[module] || module);
                          }}>
                      <CardContent className="p-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <Icon className="h-5 w-5 text-primary" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              {getStatusIcon(info.status)}
                              <p className="font-medium capitalize">
                                {module.replace('_', ' ')}
                              </p>
                            </div>
                            <p className="text-sm text-muted-foreground">{info.status}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button
                variant="outline"
                className="h-20 flex-col gap-2 hover:bg-primary/5"
                onClick={() => onTabChange('data-harbor')}
              >
                <Upload className="h-6 w-6" />
                Upload Data
              </Button>
              <Button
                variant="outline"
                className="h-20 flex-col gap-2 hover:bg-primary/5"
                onClick={() => onTabChange('the-weaver')}
              >
                <GitBranch className="h-6 w-6" />
                Create Pipeline
              </Button>
              <Button
                variant="outline"
                className="h-20 flex-col gap-2 hover:bg-primary/5"
                onClick={() => onTabChange('the-crucible')}
              >
                <Play className="h-6 w-6" />
                Train Model
              </Button>
              <Button
                variant="outline"
                className="h-20 flex-col gap-2 hover:bg-primary/5"
                onClick={() => onTabChange('insight-engine')}
              >
                <Brain className="h-6 w-6" />
                Analyze Results
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Activity */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest updates across all modules
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  type: 'success',
                  title: 'Training job completed successfully',
                  description: 'Cancer Classification Model achieved 95% accuracy',
                  time: '2 min ago',
                  icon: CheckCircle
                },
                {
                  type: 'info',
                  title: 'New dataset uploaded',
                  description: 'genomics_expression.csv processed and analyzed',
                  time: '15 min ago',
                  icon: Upload
                },
                {
                  type: 'warning',
                  title: 'Pipeline created',
                  description: 'Multi-omics Integration pipeline saved to project',
                  time: '1 hour ago',
                  icon: GitBranch
                }
              ].map((activity, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-4 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === 'success' ? 'bg-green-500' :
                    activity.type === 'info' ? 'bg-blue-500' : 'bg-yellow-500'
                  }`} />
                  <activity.icon className={`h-4 w-4 ${
                    activity.type === 'success' ? 'text-green-500' :
                    activity.type === 'info' ? 'text-blue-500' : 'text-yellow-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-xs text-muted-foreground">{activity.description}</p>
                  </div>
                  <span className="text-xs text-muted-foreground">{activity.time}</span>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}