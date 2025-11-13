"use client";

import { useEffect, useState } from "react";
import { UserPresenceData } from "./user-presence";

interface CursorDisplayProps {
  users: UserPresenceData[];
  containerRef?: React.RefObject<HTMLElement>;
}

export function CursorDisplay({ users, containerRef }: CursorDisplayProps) {
  const [cursors, setCursors] = useState<Map<string, UserPresenceData>>(
    new Map()
  );

  useEffect(() => {
    const newCursors = new Map<string, UserPresenceData>();
    users.forEach((user) => {
      if (user.cursor_position) {
        newCursors.set(user.user_id, user);
      }
    });
    setCursors(newCursors);
  }, [users]);

  return (
    <>
      {Array.from(cursors.values()).map((user) => {
        if (!user.cursor_position) return null;

        const { x, y } = user.cursor_position;

        return (
          <div
            key={user.user_id}
            className="pointer-events-none fixed z-50 transition-all duration-100"
            style={{
              left: `${x}px`,
              top: `${y}px`,
              transform: "translate(-50%, -50%)",
            }}
          >
            {/* Cursor pointer */}
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{ filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.3))" }}
            >
              <path
                d="M5.65376 12.3673L11.6538 18.3673L13.6538 10.3673L19.6538 8.36729L5.65376 12.3673Z"
                fill={user.color || "#888"}
                stroke="white"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            {/* User label */}
            <div
              className="absolute left-6 top-0 px-2 py-1 rounded text-xs text-white whitespace-nowrap"
              style={{
                backgroundColor: user.color || "#888",
                boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
              }}
            >
              {user.user_name || user.user_email.split("@")[0]}
            </div>
          </div>
        );
      })}
    </>
  );
}
