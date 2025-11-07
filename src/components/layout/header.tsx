'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Sidebar } from './sidebar';
import { useAuth } from '@/components/auth/auth-provider';
import { LoginDialog } from '@/components/auth/login-dialog';
import { ProfileDialog } from '@/components/profile/profile-dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Bell,
  User,
  Settings,
  LogOut,
  Wifi,
  WifiOff,
  Activity,
  LogIn
} from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

interface SystemStatus {
  frontend: boolean;
  backend: boolean;
  lastCheck: Date;
}

export function Header({ activeTab, onTabChange }: HeaderProps) {
  const { user, logout } = useAuth();
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    frontend: true,
    backend: false,
    lastCheck: new Date()
  });
  const [notifications, setNotifications] = useState(3);
  const [showLoginDialog, setShowLoginDialog] = useState(false);
  const [showProfileDialog, setShowProfileDialog] = useState(false);

  // Check system status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch('/api/proxy?url=/health');
        const backendStatus = response.ok;
        setSystemStatus({
          frontend: true,
          backend: backendStatus,
          lastCheck: new Date()
        });
      } catch (error) {
        setSystemStatus({
          frontend: true,
          backend: false,
          lastCheck: new Date()
        });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (systemStatus.frontend && systemStatus.backend) return 'bg-green-500';
    if (systemStatus.frontend && !systemStatus.backend) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusText = () => {
    if (systemStatus.frontend && systemStatus.backend) return 'All Systems Operational';
    if (systemStatus.frontend && !systemStatus.backend) return 'Backend Disconnected';
    return 'System Error';
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-4 lg:px-6">
        {/* Left side - Mobile menu and breadcrumb */}
        <div className="flex items-center gap-4">
          <Sidebar activeTab={activeTab} onTabChange={onTabChange} />
          <div className="hidden lg:block">
            <div className="flex items-center gap-2">
              <button 
                onClick={() => onTabChange('dashboard')}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
              >
                OmniScope AI
              </button>
              <span className="text-sm text-muted-foreground">/</span>
              <span className="text-sm font-medium capitalize">
                {activeTab.replace('-', ' ')}
              </span>
            </div>
          </div>
        </div>

        {/* Right side - Status and user menu */}
        <div className="flex items-center gap-4">
          {/* System Status */}
          <div className="hidden md:flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${getStatusColor()}`} />
            <span className="text-sm text-muted-foreground">
              {getStatusText()}
            </span>
          </div>

          {/* Connection Status */}
          <Button variant="ghost" size="sm" className="gap-2">
            {systemStatus.backend ? (
              <Wifi className="h-4 w-4 text-green-500" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-500" />
            )}
            <span className="hidden sm:inline">
              {systemStatus.backend ? 'Connected' : 'Offline'}
            </span>
          </Button>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-4 w-4" />
                {notifications > 0 && (
                  <Badge 
                    variant="destructive" 
                    className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-xs"
                  >
                    {notifications}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <Activity className="mr-2 h-4 w-4" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Training job completed</p>
                  <p className="text-xs text-muted-foreground">Model achieved 95% accuracy</p>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Activity className="mr-2 h-4 w-4" />
                <div className="flex-1">
                  <p className="text-sm font-medium">New biomarkers discovered</p>
                  <p className="text-xs text-muted-foreground">15 significant markers found</p>
                </div>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Activity className="mr-2 h-4 w-4" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Data analysis complete</p>
                  <p className="text-xs text-muted-foreground">Genomics dataset processed</p>
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={user.avatar} alt={user.name} />
                    <AvatarFallback>
                      {user.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user.name}</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => setShowProfileDialog(true)}>
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onTabChange('settings')}>
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onTabChange('help')}>
                  <Bell className="mr-2 h-4 w-4" />
                  Help & Support
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button onClick={() => setShowLoginDialog(true)} size="sm">
              <LogIn className="mr-2 h-4 w-4" />
              Sign In
            </Button>
          )}
        </div>
      </div>

      {/* Dialogs */}
      <LoginDialog open={showLoginDialog} onOpenChange={setShowLoginDialog} />
      <ProfileDialog open={showProfileDialog} onOpenChange={setShowProfileDialog} />
    </header>
  );
}