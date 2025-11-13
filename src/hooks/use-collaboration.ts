"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { io, Socket } from "socket.io-client";
import { toast } from "sonner";
import { UserPresenceData } from "@/components/collaboration/user-presence";

interface UseCollaborationOptions {
  workspaceId: string;
  userId: string;
  userEmail: string;
  userName?: string;
  token: string;
  onStateUpdate?: (update: any) => void;
  onUserJoined?: (user: any) => void;
  onUserLeft?: (user: any) => void;
}

export function useCollaboration({
  workspaceId,
  userId,
  userEmail,
  userName,
  token,
  onStateUpdate,
  onUserJoined,
  onUserLeft,
}: UseCollaborationOptions) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [users, setUsers] = useState<UserPresenceData[]>([]);
  const [syncing, setSyncing] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  // Initialize socket connection
  useEffect(() => {
    if (!workspaceId || !token) return;

    const socketUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

    const newSocket = io(socketUrl, {
      path: "/socket.io",
      auth: {
        token,
        workspace_id: workspaceId,
        user_id: userId,
        user_email: userEmail,
        user_name: userName,
      },
      transports: ["websocket", "polling"],
    });

    socketRef.current = newSocket;
    setSocket(newSocket);

    // Connection events
    newSocket.on("connect", () => {
      console.log("✅ Connected to collaboration server");
      setConnected(true);
      toast.success("Connected to workspace");
    });

    newSocket.on("disconnect", () => {
      console.log("❌ Disconnected from collaboration server");
      setConnected(false);
      toast.error("Disconnected from workspace");
    });

    newSocket.on("connect_error", (error) => {
      console.error("Connection error:", error);
      toast.error("Failed to connect to workspace");
    });

    // Presence events
    newSocket.on("presence_list", (data: { users: UserPresenceData[] }) => {
      console.log("Received presence list:", data.users);
      setUsers(data.users);
    });

    newSocket.on("user_joined", (data: any) => {
      console.log("User joined:", data);
      toast.info(`${data.user_email} joined the workspace`);
      
      // Add user to presence list
      setUsers((prev) => {
        const exists = prev.some((u) => u.user_id === data.user_id);
        if (exists) return prev;
        return [
          ...prev,
          {
            user_id: data.user_id,
            user_email: data.user_email,
            user_name: data.user_name,
            color: data.color,
            status: "active",
          },
        ];
      });

      onUserJoined?.(data);
    });

    newSocket.on("user_left", (data: any) => {
      console.log("User left:", data);
      toast.info(`${data.user_email} left the workspace`);
      
      // Remove user from presence list
      setUsers((prev) => prev.filter((u) => u.user_id !== data.user_id));

      onUserLeft?.(data);
    });

    // Cursor and selection events
    newSocket.on("cursor_updated", (data: any) => {
      setUsers((prev) =>
        prev.map((u) =>
          u.user_id === data.user_id
            ? { ...u, cursor_position: data.cursor }
            : u
        )
      );
    });

    newSocket.on("selection_updated", (data: any) => {
      setUsers((prev) =>
        prev.map((u) =>
          u.user_id === data.user_id ? { ...u, selection: data.selection } : u
        )
      );
    });

    // State synchronization events
    newSocket.on("pipeline_updated", (data: any) => {
      console.log("Pipeline updated:", data);
      onStateUpdate?.(data);
    });

    newSocket.on("state_updated", (data: any) => {
      console.log("State updated:", data);
      onStateUpdate?.(data);
    });

    return () => {
      newSocket.disconnect();
      socketRef.current = null;
    };
  }, [workspaceId, token, userId, userEmail, userName, onStateUpdate, onUserJoined, onUserLeft]);

  // Send cursor position
  const sendCursorPosition = useCallback(
    (x: number, y: number, nodeId?: string) => {
      if (socket && connected) {
        socket.emit("cursor_move", {
          cursor: { x, y, node_id: nodeId },
        });
      }
    },
    [socket, connected]
  );

  // Send selection
  const sendSelection = useCallback(
    (selection: any) => {
      if (socket && connected) {
        socket.emit("selection_change", {
          selection,
        });
      }
    },
    [socket, connected]
  );

  // Send pipeline update
  const sendPipelineUpdate = useCallback(
    (changes: any) => {
      if (socket && connected) {
        socket.emit("pipeline_update", {
          changes,
        });
      }
    },
    [socket, connected]
  );

  // Send state update
  const sendStateUpdate = useCallback(
    (update: any) => {
      if (socket && connected) {
        socket.emit("state_update", {
          update,
        });
      }
    },
    [socket, connected]
  );

  // Request sync
  const requestSync = useCallback(
    async (version: number = 0) => {
      if (!socket || !connected) return null;

      setSyncing(true);
      try {
        return new Promise((resolve, reject) => {
          socket.emit("sync_request", { version }, (response: any) => {
            setSyncing(false);
            if (response.error) {
              reject(new Error(response.error));
            } else {
              resolve(response);
            }
          });
        });
      } catch (error) {
        setSyncing(false);
        throw error;
      }
    },
    [socket, connected]
  );

  return {
    socket,
    connected,
    users,
    syncing,
    sendCursorPosition,
    sendSelection,
    sendPipelineUpdate,
    sendStateUpdate,
    requestSync,
  };
}
