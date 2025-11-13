"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { WorkspaceSelector } from "./workspace-selector";
import { UserPresence } from "./user-presence";
import { CursorDisplay } from "./cursor-display";
import { useCollaboration } from "@/hooks/use-collaboration";
import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface CollaborativeEditorProps {
  userId: string;
  userEmail: string;
  userName?: string;
  token: string;
  children?: React.ReactNode;
  onStateChange?: (state: any) => void;
}

export function CollaborativeEditor({
  userId,
  userEmail,
  userName,
  token,
  children,
  onStateChange,
}: CollaborativeEditorProps) {
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [localState, setLocalState] = useState<any>({});
  const containerRef = useRef<HTMLDivElement>(null);

  const {
    connected,
    users,
    syncing,
    sendCursorPosition,
    sendPipelineUpdate,
    requestSync,
  } = useCollaboration({
    workspaceId: workspaceId || "",
    userId,
    userEmail,
    userName,
    token,
    onStateUpdate: (update) => {
      console.log("Received state update:", update);
      // Merge the update into local state
      setLocalState((prev: any) => ({
        ...prev,
        ...update.changes,
      }));
      onStateChange?.(update);
    },
    onUserJoined: (user) => {
      console.log("User joined:", user);
    },
    onUserLeft: (user) => {
      console.log("User left:", user);
    },
  });

  // Track mouse movement for cursor sharing
  useEffect(() => {
    if (!connected || !containerRef.current) return;

    const handleMouseMove = (e: MouseEvent) => {
      sendCursorPosition(e.clientX, e.clientY);
    };

    const container = containerRef.current;
    container.addEventListener("mousemove", handleMouseMove);

    return () => {
      container.removeEventListener("mousemove", handleMouseMove);
    };
  }, [connected, sendCursorPosition]);

  // Initial sync when workspace is selected
  useEffect(() => {
    if (workspaceId && connected) {
      requestSync(0)
        .then((syncData: any) => {
          console.log("Sync complete:", syncData);
          if (syncData?.data?.full_state) {
            setLocalState(syncData.data.full_state);
          }
        })
        .catch((error) => {
          console.error("Sync failed:", error);
          toast.error("Failed to sync workspace state");
        });
    }
  }, [workspaceId, connected, requestSync]);

  const handleWorkspaceSelect = (id: string) => {
    setWorkspaceId(id);
    toast.success("Joined workspace");
  };

  return (
    <div ref={containerRef} className="relative h-full">
      {/* Collaboration toolbar */}
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Collaborative Workspace</CardTitle>
            <div className="flex items-center gap-3">
              {/* Connection status */}
              <Badge
                variant={connected ? "default" : "destructive"}
                className="flex items-center gap-1"
              >
                {connected ? (
                  <>
                    <Wifi className="h-3 w-3" />
                    Connected
                  </>
                ) : (
                  <>
                    <WifiOff className="h-3 w-3" />
                    Disconnected
                  </>
                )}
              </Badge>

              {/* Syncing indicator */}
              {syncing && (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Syncing...
                </Badge>
              )}

              {/* User presence */}
              {workspaceId && <UserPresence users={users} />}

              {/* Workspace selector */}
              <WorkspaceSelector
                onWorkspaceSelect={handleWorkspaceSelect}
                currentWorkspaceId={workspaceId || undefined}
              />
            </div>
          </div>
        </CardHeader>

        {workspaceId && (
          <CardContent className="pt-0">
            <div className="text-sm text-muted-foreground">
              {users.length === 0
                ? "You are the only one in this workspace"
                : `${users.length} ${users.length === 1 ? "person" : "people"} online`}
            </div>
          </CardContent>
        )}
      </Card>

      {/* Main content */}
      <div className="relative">
        {children}

        {/* Cursor display overlay */}
        {connected && workspaceId && (
          <CursorDisplay users={users} />
        )}
      </div>

      {/* No workspace selected message */}
      {!workspaceId && (
        <Card className="mt-8">
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <h3 className="text-lg font-semibold mb-2">
                No Workspace Selected
              </h3>
              <p className="text-muted-foreground mb-4">
                Select or create a workspace to start collaborating with your team
              </p>
              <WorkspaceSelector
                onWorkspaceSelect={handleWorkspaceSelect}
                currentWorkspaceId={workspaceId || undefined}
              />
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
