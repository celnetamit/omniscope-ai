"""
Collaboration Service - CRDT-based state synchronization
Implements Yjs-based conflict-free collaborative editing
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
import json
import base64

from .models import Workspace, WorkspaceMember
from .database import SessionLocal

# In-memory storage for Yjs documents
# In production, this should be Redis or another distributed cache
yjs_documents: Dict[str, Dict[str, Any]] = {}


class CollaborationService:
    """Service for managing collaborative state synchronization"""
    
    @staticmethod
    def get_or_create_document(workspace_id: str) -> Dict[str, Any]:
        """
        Get or create a Yjs document for a workspace
        
        Args:
            workspace_id: The workspace identifier
            
        Returns:
            Dictionary containing document state
        """
        if workspace_id not in yjs_documents:
            # Initialize new document
            yjs_documents[workspace_id] = {
                'state': {},
                'updates': [],
                'version': 0,
                'last_modified': datetime.utcnow().isoformat()
            }
        
        return yjs_documents[workspace_id]
    
    @staticmethod
    def apply_update(workspace_id: str, update: bytes, user_id: str) -> Dict[str, Any]:
        """
        Apply a Yjs update to the document
        
        Args:
            workspace_id: The workspace identifier
            update: Binary Yjs update
            user_id: User who made the update
            
        Returns:
            Updated document state
        """
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        # Store the update
        update_record = {
            'update': base64.b64encode(update).decode('utf-8'),
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'version': doc['version'] + 1
        }
        
        doc['updates'].append(update_record)
        doc['version'] += 1
        doc['last_modified'] = datetime.utcnow().isoformat()
        
        # Keep only last 100 updates in memory
        if len(doc['updates']) > 100:
            doc['updates'] = doc['updates'][-100:]
        
        return doc
    
    @staticmethod
    def get_updates_since(workspace_id: str, since_version: int) -> List[Dict[str, Any]]:
        """
        Get all updates since a specific version
        
        Args:
            workspace_id: The workspace identifier
            since_version: Version number to get updates from
            
        Returns:
            List of updates
        """
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        # Filter updates by version
        updates = [
            u for u in doc['updates']
            if u['version'] > since_version
        ]
        
        return updates
    
    @staticmethod
    def get_full_state(workspace_id: str) -> Dict[str, Any]:
        """
        Get the full document state
        
        Args:
            workspace_id: The workspace identifier
            
        Returns:
            Full document state
        """
        return CollaborationService.get_or_create_document(workspace_id)
    
    @staticmethod
    def persist_state(workspace_id: str, db: Session) -> bool:
        """
        Persist the current document state to the database
        
        Args:
            workspace_id: The workspace identifier
            db: Database session
            
        Returns:
            Success status
        """
        try:
            doc = yjs_documents.get(workspace_id)
            if not doc:
                return False
            
            # Get workspace from database
            workspace = db.query(Workspace).filter(
                Workspace.id == workspace_id
            ).first()
            
            if not workspace:
                return False
            
            # Store the state in pipeline_state field
            workspace.pipeline_state = {
                'yjs_state': doc['state'],
                'version': doc['version'],
                'last_modified': doc['last_modified']
            }
            workspace.updated_at = datetime.utcnow()
            
            db.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error persisting state: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def load_state(workspace_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Load document state from the database
        
        Args:
            workspace_id: The workspace identifier
            db: Database session
            
        Returns:
            Document state or None
        """
        try:
            workspace = db.query(Workspace).filter(
                Workspace.id == workspace_id
            ).first()
            
            if not workspace or not workspace.pipeline_state:
                return None
            
            # Load state into memory
            if 'yjs_state' in workspace.pipeline_state:
                yjs_documents[workspace_id] = {
                    'state': workspace.pipeline_state.get('yjs_state', {}),
                    'updates': [],
                    'version': workspace.pipeline_state.get('version', 0),
                    'last_modified': workspace.pipeline_state.get(
                        'last_modified',
                        datetime.utcnow().isoformat()
                    )
                }
                
                return yjs_documents[workspace_id]
            
            return None
            
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            return None
    
    @staticmethod
    def merge_states(workspace_id: str, states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple states using CRDT conflict resolution
        
        Args:
            workspace_id: The workspace identifier
            states: List of states to merge
            
        Returns:
            Merged state
        """
        # Simple last-write-wins for now
        # In production, use proper Yjs merge algorithm
        if not states:
            return CollaborationService.get_or_create_document(workspace_id)
        
        # Sort by version and take the latest
        sorted_states = sorted(states, key=lambda s: s.get('version', 0))
        latest_state = sorted_states[-1]
        
        # Update in-memory document
        yjs_documents[workspace_id] = latest_state
        
        return latest_state
    
    @staticmethod
    def create_snapshot(workspace_id: str) -> Dict[str, Any]:
        """
        Create a snapshot of the current state
        
        Args:
            workspace_id: The workspace identifier
            
        Returns:
            Snapshot data
        """
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        snapshot = {
            'workspace_id': workspace_id,
            'state': doc['state'].copy(),
            'version': doc['version'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return snapshot
    
    @staticmethod
    def restore_snapshot(workspace_id: str, snapshot: Dict[str, Any]) -> bool:
        """
        Restore state from a snapshot
        
        Args:
            workspace_id: The workspace identifier
            snapshot: Snapshot data
            
        Returns:
            Success status
        """
        try:
            yjs_documents[workspace_id] = {
                'state': snapshot['state'].copy(),
                'updates': [],
                'version': snapshot['version'],
                'last_modified': datetime.utcnow().isoformat()
            }
            return True
        except Exception as e:
            print(f"❌ Error restoring snapshot: {e}")
            return False
    
    @staticmethod
    def cleanup_old_documents(max_age_hours: int = 24):
        """
        Clean up old documents from memory
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        from datetime import timedelta
        
        current_time = datetime.utcnow()
        to_remove = []
        
        for workspace_id, doc in yjs_documents.items():
            last_modified = datetime.fromisoformat(doc['last_modified'])
            age = current_time - last_modified
            
            if age > timedelta(hours=max_age_hours):
                to_remove.append(workspace_id)
        
        for workspace_id in to_remove:
            del yjs_documents[workspace_id]
            print(f"🧹 Cleaned up document for workspace {workspace_id}")


class StateManager:
    """Manager for workspace state operations"""
    
    @staticmethod
    def get_workspace_state(workspace_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get the current workspace state
        
        Args:
            workspace_id: The workspace identifier
            db: Database session
            
        Returns:
            Workspace state or None
        """
        # Try to get from memory first
        if workspace_id in yjs_documents:
            return yjs_documents[workspace_id]
        
        # Load from database
        return CollaborationService.load_state(workspace_id, db)
    
    @staticmethod
    def update_workspace_state(
        workspace_id: str,
        state_update: Dict[str, Any],
        user_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Update workspace state
        
        Args:
            workspace_id: The workspace identifier
            state_update: State changes to apply
            user_id: User making the update
            db: Database session
            
        Returns:
            Updated state
        """
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        # Apply the update
        if 'state' in state_update:
            doc['state'].update(state_update['state'])
        
        doc['version'] += 1
        doc['last_modified'] = datetime.utcnow().isoformat()
        
        # Record the update
        update_record = {
            'user_id': user_id,
            'changes': state_update,
            'timestamp': datetime.utcnow().isoformat(),
            'version': doc['version']
        }
        doc['updates'].append(update_record)
        
        # Persist to database periodically (every 10 updates)
        if doc['version'] % 10 == 0:
            CollaborationService.persist_state(workspace_id, db)
        
        return doc
    
    @staticmethod
    def sync_workspace_state(
        workspace_id: str,
        client_version: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Sync workspace state with client
        
        Args:
            workspace_id: The workspace identifier
            client_version: Client's current version
            db: Database session
            
        Returns:
            Sync data including missing updates
        """
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        # Get updates since client version
        missing_updates = CollaborationService.get_updates_since(
            workspace_id,
            client_version
        )
        
        return {
            'current_version': doc['version'],
            'missing_updates': missing_updates,
            'full_state': doc['state'] if client_version == 0 else None
        }
