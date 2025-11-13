"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Circle } from "lucide-react";

export interface UserPresenceData {
  user_id: string;
  user_email: string;
  user_name?: string;
  color?: string;
  status?: string;
  cursor_position?: {
    x: number;
    y: number;
    node_id?: string;
  };
}

interface UserPresenceProps {
  users: UserPresenceData[];
  maxDisplay?: number;
}

export function UserPresence({ users, maxDisplay = 5 }: UserPresenceProps) {
  const displayUsers = users.slice(0, maxDisplay);
  const remainingCount = users.length - maxDisplay;

  const getInitials = (email: string, name?: string) => {
    if (name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    return email.slice(0, 2).toUpperCase();
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "active":
        return "text-green-500";
      case "idle":
        return "text-yellow-500";
      case "away":
        return "text-gray-500";
      default:
        return "text-green-500";
    }
  };

  return (
    <TooltipProvider>
      <div className="flex items-center gap-1">
        {displayUsers.map((user) => (
          <Tooltip key={user.user_id}>
            <TooltipTrigger asChild>
              <div className="relative">
                <Avatar
                  className="h-8 w-8 border-2"
                  style={{ borderColor: user.color || "#888" }}
                >
                  <AvatarFallback
                    style={{ backgroundColor: user.color || "#888" }}
                    className="text-white text-xs"
                  >
                    {getInitials(user.user_email, user.user_name)}
                  </AvatarFallback>
                </Avatar>
                <Circle
                  className={`absolute -bottom-0.5 -right-0.5 h-3 w-3 fill-current ${getStatusColor(
                    user.status
                  )}`}
                />
              </div>
            </TooltipTrigger>
            <TooltipContent>
              <div className="text-sm">
                <p className="font-medium">{user.user_name || user.user_email}</p>
                <p className="text-xs text-muted-foreground capitalize">
                  {user.status || "active"}
                </p>
              </div>
            </TooltipContent>
          </Tooltip>
        ))}

        {remainingCount > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Avatar className="h-8 w-8 border-2 border-border">
                <AvatarFallback className="text-xs">
                  +{remainingCount}
                </AvatarFallback>
              </Avatar>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-sm">{remainingCount} more users online</p>
            </TooltipContent>
          </Tooltip>
        )}
      </div>
    </TooltipProvider>
  );
}
