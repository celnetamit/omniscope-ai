'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Badge } from '@/components/ui/badge';
import {
  Upload,
  GitBranch,
  Cpu,
  Brain,
  Home,
  HelpCircle,
  Settings,
  FileText,
  BarChart3,
  Database,
  Menu,
  ChevronRight,
  Zap,
  Activity
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const navigation = [
  {
    name: 'Dashboard',
    id: 'dashboard',
    icon: Home,
    description: 'Overview and system status'
  },
  {
    name: 'Data Harbor',
    id: 'data-harbor',
    icon: Upload,
    description: 'File upload and analysis',
    badge: 'Core'
  },
  {
    name: 'The Weaver',
    id: 'the-weaver',
    icon: GitBranch,
    description: 'Pipeline management',
    badge: 'AI'
  },
  {
    name: 'The Crucible',
    id: 'the-crucible',
    icon: Cpu,
    description: 'Model training',
    badge: 'ML'
  },
  {
    name: 'Insight Engine',
    id: 'insight-engine',
    icon: Brain,
    description: 'Biomarker analysis',
    badge: 'AI'
  },
  {
    name: 'Data Explorer',
    id: 'data-explorer',
    icon: Database,
    description: 'Browse and visualize data'
  },
  {
    name: 'Reports',
    id: 'reports',
    icon: FileText,
    description: 'Analysis reports and exports'
  },
  {
    name: 'Analytics',
    id: 'analytics',
    icon: BarChart3,
    description: 'Usage and performance metrics'
  }
];

const bottomNavigation = [
  {
    name: 'Help & Docs',
    id: 'help',
    icon: HelpCircle,
    description: 'Documentation and tutorials'
  },
  {
    name: 'Settings',
    id: 'settings',
    icon: Settings,
    description: 'System configuration'
  }
];

function SidebarContent({ activeTab, onTabChange }: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex h-16 items-center border-b px-6"
      >
        <button 
          onClick={() => onTabChange('dashboard')}
          className="flex items-center gap-3 w-full hover:opacity-80 transition-opacity cursor-pointer"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-600">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div className="text-left">
            <h1 className="text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              OmniScope AI
            </h1>
            <p className="text-xs text-muted-foreground">Multi-Omics Platform</p>
          </div>
        </button>
      </motion.div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="space-y-1"
        >
          {navigation.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Button
                variant={activeTab === item.id ? 'secondary' : 'ghost'}
                className={cn(
                  'w-full justify-start gap-3 h-auto p-3 transition-all duration-200 hover:scale-[1.02]',
                  activeTab === item.id && 'bg-secondary shadow-sm'
                )}
                onClick={() => onTabChange(item.id)}
              >
                <div className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                  activeTab === item.id ? 'bg-primary/10' : 'bg-muted/50'
                )}>
                  <item.icon className={cn(
                    'h-4 w-4 transition-colors',
                    activeTab === item.id ? 'text-primary' : 'text-muted-foreground'
                  )} />
                </div>
                <div className="flex-1 text-left">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{item.name}</span>
                    {item.badge && (
                      <Badge variant="secondary" className={cn(
                        'text-xs px-1.5 py-0.5',
                        item.badge === 'AI' && 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
                        item.badge === 'ML' && 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
                        item.badge === 'Core' && 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
                      )}>
                        {item.badge}
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
                {activeTab === item.id && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <ChevronRight className="h-3 w-3 text-primary" />
                  </motion.div>
                )}
              </Button>
            </motion.div>
          ))}
        </motion.div>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-8 space-y-1"
        >
          <div className="px-3 py-2">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              System
            </h3>
          </div>
          {bottomNavigation.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.05 }}
            >
              <Button
                variant={activeTab === item.id ? 'secondary' : 'ghost'}
                className={cn(
                  'w-full justify-start gap-3 h-auto p-3 transition-all duration-200 hover:scale-[1.02]',
                  activeTab === item.id && 'bg-secondary shadow-sm'
                )}
                onClick={() => onTabChange(item.id)}
              >
                <div className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                  activeTab === item.id ? 'bg-primary/10' : 'bg-muted/50'
                )}>
                  <item.icon className={cn(
                    'h-4 w-4 transition-colors',
                    activeTab === item.id ? 'text-primary' : 'text-muted-foreground'
                  )} />
                </div>
                <div className="flex-1 text-left">
                  <span className="text-sm font-medium">{item.name}</span>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
                {activeTab === item.id && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    <ChevronRight className="h-3 w-3 text-primary" />
                  </motion.div>
                )}
              </Button>
            </motion.div>
          ))}
        </motion.div>

        {/* Status Indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-6 mx-3 p-3 rounded-lg bg-muted/50"
        >
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center">
              <Activity className="h-3 w-3 text-green-500 animate-pulse" />
            </div>
            <div className="flex-1">
              <p className="text-xs font-medium">System Status</p>
              <p className="text-xs text-muted-foreground">All systems operational</p>
            </div>
          </div>
        </motion.div>
      </ScrollArea>
    </div>
  );
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:w-72 lg:flex-col lg:fixed lg:inset-y-0 lg:border-r lg:bg-background">
        <SidebarContent activeTab={activeTab} onTabChange={onTabChange} />
      </div>

      {/* Mobile Sidebar */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-72 p-0">
          <SidebarContent activeTab={activeTab} onTabChange={onTabChange} />
        </SheetContent>
      </Sheet>
    </>
  );
}