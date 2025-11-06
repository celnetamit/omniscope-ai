'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
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
  Zap
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
      <div className="flex h-16 items-center border-b px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Zap className="h-4 w-4 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">OmniScope AI</h1>
            <p className="text-xs text-muted-foreground">Multi-Omics Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-1">
          {navigation.map((item) => (
            <Button
              key={item.id}
              variant={activeTab === item.id ? 'secondary' : 'ghost'}
              className={cn(
                'w-full justify-start gap-3 h-auto p-3',
                activeTab === item.id && 'bg-secondary'
              )}
              onClick={() => onTabChange(item.id)}
            >
              <item.icon className="h-4 w-4" />
              <div className="flex-1 text-left">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{item.name}</span>
                  {item.badge && (
                    <span className={cn(
                      'px-1.5 py-0.5 text-xs rounded-full',
                      item.badge === 'AI' && 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
                      item.badge === 'ML' && 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
                      item.badge === 'Core' && 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
                    )}>
                      {item.badge}
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
              {activeTab === item.id && <ChevronRight className="h-3 w-3" />}
            </Button>
          ))}
        </div>

        <div className="mt-8 space-y-1">
          <div className="px-3 py-2">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              System
            </h3>
          </div>
          {bottomNavigation.map((item) => (
            <Button
              key={item.id}
              variant={activeTab === item.id ? 'secondary' : 'ghost'}
              className={cn(
                'w-full justify-start gap-3 h-auto p-3',
                activeTab === item.id && 'bg-secondary'
              )}
              onClick={() => onTabChange(item.id)}
            >
              <item.icon className="h-4 w-4" />
              <div className="flex-1 text-left">
                <span className="text-sm font-medium">{item.name}</span>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
              {activeTab === item.id && <ChevronRight className="h-3 w-3" />}
            </Button>
          ))}
        </div>
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