"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Users, Plus, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface Workspace {
  id: string;
  name: string;
  owner_id: string;
  created_at: string;
  members: any[];
}

interface WorkspaceSelectorProps {
  onWorkspaceSelect: (workspaceId: string) => void;
  currentWorkspaceId?: string;
}

export function WorkspaceSelector({
  onWorkspaceSelect,
  currentWorkspaceId,
}: WorkspaceSelectorProps) {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/collaboration/workspace/list`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setWorkspaces(data);
      } else {
        toast.error("Failed to load workspaces");
      }
    } catch (error) {
      console.error("Error loading workspaces:", error);
      toast.error("Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  };

  const createWorkspace = async () => {
    if (!newWorkspaceName.trim()) {
      toast.error("Please enter a workspace name");
      return;
    }

    setCreating(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001"}/api/collaboration/workspace/create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: newWorkspaceName,
            pipeline_state: {},
          }),
        }
      );

      if (response.ok) {
        const workspace = await response.json();
        toast.success("Workspace created successfully");
        setNewWorkspaceName("");
        setDialogOpen(false);
        loadWorkspaces();
        onWorkspaceSelect(workspace.id);
      } else {
        toast.error("Failed to create workspace");
      }
    } catch (error) {
      console.error("Error creating workspace:", error);
      toast.error("Failed to create workspace");
    } finally {
      setCreating(false);
    }
  };

  return (
    <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Users className="h-4 w-4 mr-2" />
          Workspaces
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Collaborative Workspaces</DialogTitle>
          <DialogDescription>
            Select a workspace to collaborate with your team in real-time
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Create new workspace */}
          <div className="space-y-2">
            <Label htmlFor="workspace-name">Create New Workspace</Label>
            <div className="flex gap-2">
              <Input
                id="workspace-name"
                placeholder="Enter workspace name"
                value={newWorkspaceName}
                onChange={(e) => setNewWorkspaceName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    createWorkspace();
                  }
                }}
              />
              <Button
                onClick={createWorkspace}
                disabled={creating || !newWorkspaceName.trim()}
              >
                {creating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          {/* Workspace list */}
          <div className="space-y-2">
            <Label>Your Workspaces</Label>
            <ScrollArea className="h-[300px] border rounded-md p-4">
              {loading ? (
                <div className="flex items-center justify-center h-full">
                  <Loader2 className="h-6 w-6 animate-spin" />
                </div>
              ) : workspaces.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  No workspaces yet. Create one to get started!
                </div>
              ) : (
                <div className="space-y-2">
                  {workspaces.map((workspace) => (
                    <div
                      key={workspace.id}
                      className={`p-3 border rounded-lg cursor-pointer hover:bg-accent transition-colors ${
                        currentWorkspaceId === workspace.id
                          ? "bg-accent border-primary"
                          : ""
                      }`}
                      onClick={() => {
                        onWorkspaceSelect(workspace.id);
                        setDialogOpen(false);
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{workspace.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            Created {new Date(workspace.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge variant="secondary">
                          {workspace.members?.[0]?.count || 1} members
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
