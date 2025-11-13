"""
Presence Service - User tracking and online status
Tracks user cursors, selections, and online status in real-time
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json


@dataclass
class UserPresence:
    """Data class for user presence information"""
    user_id: str
    user_email: str
    user_name: Optional[str] = None
    cursor_position: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    color: Optional[str] = None  # Assigned color for cursor display
    last_activity: Optional[str] = None
    status: str = "active"  # active, idle, away
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class PresenceService:
    """Service for managing user presence in workspaces"""
    
    # In-memory storage for presence data
    # workspace_id -> {user_id -> UserPresence}
    _presence_data: Dict[str, Dict[str, UserPresence]] = {}
    
    # Color palette for user cursors
    _colors = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
        "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52B788"
    ]
    _color_index: Dict[str, int] = {}
    
    @classmethod
    def join_workspace(
        cls,
        workspace_id: str,
        user_id: str,
        user_email: str,
        user_name: Optional[str] = None
    ) -> UserPresence:
        """
        User joins a workspace
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            user_email: User email
            user_name: User display name
            
        Returns:
            UserPresence object
        """
        if workspace_id not in cls._presence_data:
            cls._presence_data[workspace_id] = {}
            cls._color_index[workspace_id] = 0
        
        # Assign a color
        color_idx = cls._color_index[workspace_id] % len(cls._colors)
        color = cls._colors[color_idx]
        cls._color_index[workspace_id] += 1
        
        # Create presence
        presence = UserPresence(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name or user_email.split('@')[0],
            color=color,
            last_activity=datetime.utcnow().isoformat(),
            status="active"
        )
        
        cls._presence_data[workspace_id][user_id] = presence
        
        return presence
    
    @classmethod
    def leave_workspace(cls, workspace_id: str, user_id: str) -> bool:
        """
        User leaves a workspace
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            
        Returns:
            Success status
        """
        if workspace_id in cls._presence_data:
            if user_id in cls._presence_data[workspace_id]:
                del cls._presence_data[workspace_id][user_id]
                
                # Clean up empty workspaces
                if not cls._presence_data[workspace_id]:
                    del cls._presence_data[workspace_id]
                    if workspace_id in cls._color_index:
                        del cls._color_index[workspace_id]
                
                return True
        
        return False
    
    @classmethod
    def update_cursor(
        cls,
        workspace_id: str,
        user_id: str,
        cursor_position: Dict[str, Any]
    ) -> Optional[UserPresence]:
        """
        Update user cursor position
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            cursor_position: Cursor position data
            
        Returns:
            Updated UserPresence or None
        """
        if workspace_id in cls._presence_data:
            if user_id in cls._presence_data[workspace_id]:
                presence = cls._presence_data[workspace_id][user_id]
                presence.cursor_position = cursor_position
                presence.last_activity = datetime.utcnow().isoformat()
                presence.status = "active"
                return presence
        
        return None
    
    @classmethod
    def update_selection(
        cls,
        workspace_id: str,
        user_id: str,
        selection: Dict[str, Any]
    ) -> Optional[UserPresence]:
        """
        Update user selection
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            selection: Selection data
            
        Returns:
            Updated UserPresence or None
        """
        if workspace_id in cls._presence_data:
            if user_id in cls._presence_data[workspace_id]:
                presence = cls._presence_data[workspace_id][user_id]
                presence.selection = selection
                presence.last_activity = datetime.utcnow().isoformat()
                presence.status = "active"
                return presence
        
        return None
    
    @classmethod
    def update_status(
        cls,
        workspace_id: str,
        user_id: str,
        status: str
    ) -> Optional[UserPresence]:
        """
        Update user status
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            status: New status (active, idle, away)
            
        Returns:
            Updated UserPresence or None
        """
        if workspace_id in cls._presence_data:
            if user_id in cls._presence_data[workspace_id]:
                presence = cls._presence_data[workspace_id][user_id]
                presence.status = status
                presence.last_activity = datetime.utcnow().isoformat()
                return presence
        
        return None
    
    @classmethod
    def get_presence(
        cls,
        workspace_id: str,
        user_id: str
    ) -> Optional[UserPresence]:
        """
        Get user presence
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            
        Returns:
            UserPresence or None
        """
        if workspace_id in cls._presence_data:
            return cls._presence_data[workspace_id].get(user_id)
        
        return None
    
    @classmethod
    def get_all_presence(cls, workspace_id: str) -> List[UserPresence]:
        """
        Get all user presence in a workspace
        
        Args:
            workspace_id: The workspace identifier
            
        Returns:
            List of UserPresence objects
        """
        if workspace_id in cls._presence_data:
            return list(cls._presence_data[workspace_id].values())
        
        return []
    
    @classmethod
    def get_online_users(cls, workspace_id: str) -> List[UserPresence]:
        """
        Get all online users in a workspace
        
        Args:
            workspace_id: The workspace identifier
            
        Returns:
            List of online UserPresence objects
        """
        all_presence = cls.get_all_presence(workspace_id)
        return [p for p in all_presence if p.status in ["active", "idle"]]
    
    @classmethod
    def update_idle_status(cls, idle_threshold_minutes: int = 5):
        """
        Update idle status for users who haven't been active
        
        Args:
            idle_threshold_minutes: Minutes of inactivity before marking as idle
        """
        current_time = datetime.utcnow()
        threshold = timedelta(minutes=idle_threshold_minutes)
        
        for workspace_id in cls._presence_data:
            for user_id, presence in cls._presence_data[workspace_id].items():
                if presence.last_activity:
                    last_activity = datetime.fromisoformat(presence.last_activity)
                    if current_time - last_activity > threshold:
                        if presence.status == "active":
                            presence.status = "idle"
    
    @classmethod
    def cleanup_inactive_users(cls, timeout_minutes: int = 30):
        """
        Remove users who have been inactive for too long
        
        Args:
            timeout_minutes: Minutes of inactivity before removal
        """
        current_time = datetime.utcnow()
        threshold = timedelta(minutes=timeout_minutes)
        
        workspaces_to_clean = []
        
        for workspace_id in cls._presence_data:
            users_to_remove = []
            
            for user_id, presence in cls._presence_data[workspace_id].items():
                if presence.last_activity:
                    last_activity = datetime.fromisoformat(presence.last_activity)
                    if current_time - last_activity > threshold:
                        users_to_remove.append(user_id)
            
            for user_id in users_to_remove:
                del cls._presence_data[workspace_id][user_id]
            
            if not cls._presence_data[workspace_id]:
                workspaces_to_clean.append(workspace_id)
        
        for workspace_id in workspaces_to_clean:
            del cls._presence_data[workspace_id]
            if workspace_id in cls._color_index:
                del cls._color_index[workspace_id]
    
    @classmethod
    def get_workspace_stats(cls, workspace_id: str) -> Dict[str, Any]:
        """
        Get statistics about workspace presence
        
        Args:
            workspace_id: The workspace identifier
            
        Returns:
            Statistics dictionary
        """
        all_presence = cls.get_all_presence(workspace_id)
        
        active_count = sum(1 for p in all_presence if p.status == "active")
        idle_count = sum(1 for p in all_presence if p.status == "idle")
        away_count = sum(1 for p in all_presence if p.status == "away")
        
        return {
            'total_users': len(all_presence),
            'active_users': active_count,
            'idle_users': idle_count,
            'away_users': away_count,
            'users': [p.to_dict() for p in all_presence]
        }
    
    @classmethod
    def broadcast_presence_update(
        cls,
        workspace_id: str,
        user_id: str,
        update_type: str
    ) -> Dict[str, Any]:
        """
        Prepare presence update for broadcasting
        
        Args:
            workspace_id: The workspace identifier
            user_id: User identifier
            update_type: Type of update (join, leave, cursor, selection, status)
            
        Returns:
            Broadcast data
        """
        presence = cls.get_presence(workspace_id, user_id)
        
        if not presence:
            return {
                'type': 'leave',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return {
            'type': update_type,
            'user_id': user_id,
            'presence': presence.to_dict(),
            'timestamp': datetime.utcnow().isoformat()
        }
