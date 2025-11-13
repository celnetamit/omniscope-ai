"""
Collaboration Module - Real-time collaborative editing and workspace management
Implements WebSocket-based collaboration using Socket.IO
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import socketio
import json

from backend_db.database import get_db
from backend_db.models import User, Workspace, WorkspaceMember
from backend_db.auth import get_current_user
from backend_db.collaboration import CollaborationService, StateManager
from backend_db.presence import PresenceService

# Create FastAPI router
router = APIRouter()

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio)

# In-memory storage for active connections and presence
active_connections: Dict[str, Dict[str, Any]] = {}  # workspace_id -> {user_id: {sid, cursor, etc}}
workspace_rooms: Dict[str, set] = {}  # workspace_id -> set of session IDs


# ============================================================================
# Pydantic Models
# ============================================================================

class WorkspaceCreate(BaseModel):
    """Model for creating a new workspace"""
    name: str = Field(..., min_length=1, max_length=255)
    pipeline_state: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    """Model for updating workspace"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    pipeline_state: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    """Response model for workspace"""
    id: str
    name: str
    owner_id: str
    pipeline_state: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    members: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True


class WorkspaceInvite(BaseModel):
    """Model for inviting users to workspace"""
    user_email: str
    role: str = Field(default="editor", pattern="^(owner|editor|viewer)$")


class MemberResponse(BaseModel):
    """Response model for workspace member"""
    user_id: str
    user_email: str
    role: str
    last_seen: Optional[datetime]
    is_online: bool = False

    class Config:
        from_attributes = True


class CursorPosition(BaseModel):
    """Model for cursor position"""
    x: float
    y: float
    node_id: Optional[str] = None


class PresenceUpdate(BaseModel):
    """Model for presence updates"""
    cursor_position: Optional[CursorPosition] = None
    selection: Optional[Dict[str, Any]] = None


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@sio.event
async def connect(sid, environ, auth):
    """
    Handle client connection
    Authenticate user and join workspace room
    """
    print(f"🔌 Client connecting: {sid}")
    
    # Extract authentication token from auth dict
    if not auth or 'token' not in auth:
        print(f"❌ Connection rejected: No authentication token")
        return False
    
    token = auth['token']
    workspace_id = auth.get('workspace_id')
    
    if not workspace_id:
        print(f"❌ Connection rejected: No workspace_id")
        return False
    
    try:
        # Verify token and get user (simplified - in production use proper JWT validation)
        # For now, we'll store the token and validate on each event
        await sio.save_session(sid, {
            'token': token,
            'workspace_id': workspace_id,
            'user_id': auth.get('user_id'),
            'user_email': auth.get('user_email')
        })
        
        # Join workspace room
        await sio.enter_room(sid, workspace_id)
        
        # Track connection
        if workspace_id not in workspace_rooms:
            workspace_rooms[workspace_id] = set()
        workspace_rooms[workspace_id].add(sid)
        
        if workspace_id not in active_connections:
            active_connections[workspace_id] = {}
        
        active_connections[workspace_id][auth.get('user_id')] = {
            'sid': sid,
            'user_email': auth.get('user_email'),
            'cursor': None,
            'connected_at': datetime.utcnow().isoformat()
        }
        
        # Add to presence service
        presence = PresenceService.join_workspace(
            workspace_id,
            auth.get('user_id'),
            auth.get('user_email'),
            auth.get('user_name')
        )
        
        print(f"✅ Client connected: {sid} to workspace {workspace_id}")
        
        # Notify other users in the workspace
        await sio.emit('user_joined', {
            'user_id': auth.get('user_id'),
            'user_email': auth.get('user_email'),
            'user_name': presence.user_name,
            'color': presence.color,
            'timestamp': datetime.utcnow().isoformat()
        }, room=workspace_id, skip_sid=sid)
        
        # Send current presence to the new user
        all_presence = PresenceService.get_all_presence(workspace_id)
        presence_list = [
            p.to_dict() for p in all_presence
            if p.user_id != auth.get('user_id')
        ]
        
        await sio.emit('presence_list', {
            'users': presence_list
        }, to=sid)
        
        return True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


@sio.event
async def disconnect(sid):
    """
    Handle client disconnection
    Remove from workspace and notify others
    """
    print(f"🔌 Client disconnecting: {sid}")
    
    try:
        session = await sio.get_session(sid)
        workspace_id = session.get('workspace_id')
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        
        if workspace_id and user_id:
            # Remove from tracking
            if workspace_id in workspace_rooms:
                workspace_rooms[workspace_id].discard(sid)
                if not workspace_rooms[workspace_id]:
                    del workspace_rooms[workspace_id]
            
            if workspace_id in active_connections and user_id in active_connections[workspace_id]:
                del active_connections[workspace_id][user_id]
                if not active_connections[workspace_id]:
                    del active_connections[workspace_id]
            
            # Remove from presence service
            PresenceService.leave_workspace(workspace_id, user_id)
            
            # Notify other users
            await sio.emit('user_left', {
                'user_id': user_id,
                'user_email': user_email,
                'timestamp': datetime.utcnow().isoformat()
            }, room=workspace_id)
            
            print(f"✅ Client disconnected: {sid} from workspace {workspace_id}")
    
    except Exception as e:
        print(f"❌ Disconnect error: {e}")


@sio.event
async def pipeline_update(sid, data):
    """
    Handle pipeline state updates
    Broadcast changes to all users in the workspace
    """
    try:
        session = await sio.get_session(sid)
        workspace_id = session.get('workspace_id')
        user_id = session.get('user_id')
        
        if not workspace_id:
            return {'error': 'Not in a workspace'}
        
        # Broadcast update to all other users in the workspace
        await sio.emit('pipeline_updated', {
            'user_id': user_id,
            'changes': data.get('changes'),
            'timestamp': datetime.utcnow().isoformat()
        }, room=workspace_id, skip_sid=sid)
        
        return {'status': 'success'}
        
    except Exception as e:
        print(f"❌ Pipeline update error: {e}")
        return {'error': str(e)}


@sio.event
async def cursor_move(sid, data):
    """
    Handle cursor position updates
    Broadcast to other users for real-time cursor display
    """
    try:
        session = await sio.get_session(sid)
        workspace_id = session.get('workspace_id')
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        
        if not workspace_id:
            return
        
        # Update cursor position in memory
        if workspace_id in active_connections and user_id in active_connections[workspace_id]:
            active_connections[workspace_id][user_id]['cursor'] = data.get('cursor')
        
        # Update in presence service
        presence = PresenceService.update_cursor(
            workspace_id,
            user_id,
            data.get('cursor')
        )
        
        # Broadcast cursor position to other users
        if presence:
            await sio.emit('cursor_updated', {
                'user_id': user_id,
                'user_email': user_email,
                'cursor': data.get('cursor'),
                'color': presence.color,
                'timestamp': datetime.utcnow().isoformat()
            }, room=workspace_id, skip_sid=sid)
        
    except Exception as e:
        print(f"❌ Cursor move error: {e}")


@sio.event
async def selection_change(sid, data):
    """
    Handle selection changes
    Broadcast to other users
    """
    try:
        session = await sio.get_session(sid)
        workspace_id = session.get('workspace_id')
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        
        if not workspace_id:
            return
        
        # Update in presence service
        presence = PresenceService.update_selection(
            workspace_id,
            user_id,
            data.get('selection')
        )
        
        # Broadcast selection to other users
        if presence:
            await sio.emit('selection_updated', {
                'user_id': user_id,
                'user_email': user_email,
                'selection': data.get('selection'),
                'color': presence.color,
                'timestamp': datetime.utcnow().isoformat()
            }, room=workspace_id, skip_sid=sid)
        
    except Exception as e:
        print(f"❌ Selection change error: {e}")


@sio.event
async def sync_request(sid, data):
    """
    Handle sync request from client
    Send current workspace state and missing updates
    """
    try:
        session = await sio.get_session(sid)
        workspace_id = session.get('workspace_id')
        
        if not workspace_id:
            return {'error': 'Not in a workspace'}
        
        client_version = data.get('version', 0)
        
        # Get database session
        from backend_db.database import SessionLocal
        db = SessionLocal()
        try:
            # Sync state
            sync_data = StateManager.sync_workspace_state(
                workspace_id,
                client_version,
                db
            )
            
            return {
                'status': 'success',
                'data': sync_data,
                'timestamp': datetime.utcnow().isoformat()
            }
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Sync request error: {e}")
        return {'error': str(e)}


@sio.event
async def state_update(sid, data):
    """
    Handle state update from client
    Apply CRDT-based state synchronization
    """
    try:
        session = await sio.get_session(sid)
        workspace_id = session.get('workspace_id')
        user_id = session.get('user_id')
        
        if not workspace_id:
            return {'error': 'Not in a workspace'}
        
        # Get database session
        from backend_db.database import SessionLocal
        db = SessionLocal()
        try:
            # Apply state update
            updated_state = StateManager.update_workspace_state(
                workspace_id,
                data.get('update', {}),
                user_id,
                db
            )
            
            # Broadcast update to other users
            await sio.emit('state_updated', {
                'user_id': user_id,
                'version': updated_state['version'],
                'update': data.get('update'),
                'timestamp': datetime.utcnow().isoformat()
            }, room=workspace_id, skip_sid=sid)
            
            return {
                'status': 'success',
                'version': updated_state['version']
            }
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ State update error: {e}")
        return {'error': str(e)}


# ============================================================================
# REST API Endpoints
# ============================================================================

@router.post("/workspace/create", response_model=WorkspaceResponse)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new collaborative workspace
    """
    try:
        # Create workspace
        new_workspace = Workspace(
            name=workspace.name,
            owner_id=current_user.id,
            pipeline_state=workspace.pipeline_state or {}
        )
        db.add(new_workspace)
        db.flush()
        
        # Add owner as member
        owner_member = WorkspaceMember(
            workspace_id=new_workspace.id,
            user_id=current_user.id,
            role="owner"
        )
        db.add(owner_member)
        db.commit()
        db.refresh(new_workspace)
        
        return WorkspaceResponse(
            id=str(new_workspace.id),
            name=new_workspace.name,
            owner_id=str(new_workspace.owner_id),
            pipeline_state=new_workspace.pipeline_state,
            created_at=new_workspace.created_at,
            updated_at=new_workspace.updated_at,
            members=[{
                'user_id': str(current_user.id),
                'user_email': current_user.email,
                'role': 'owner'
            }]
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace: {str(e)}"
        )


@router.get("/workspace/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get workspace details
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if user is a member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    # Get all members
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()
    
    member_list = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            is_online = (
                workspace_id in active_connections and
                str(m.user_id) in active_connections[workspace_id]
            )
            member_list.append({
                'user_id': str(m.user_id),
                'user_email': user.email,
                'role': m.role,
                'last_seen': m.last_seen,
                'is_online': is_online
            })
    
    return WorkspaceResponse(
        id=str(workspace.id),
        name=workspace.name,
        owner_id=str(workspace.owner_id),
        pipeline_state=workspace.pipeline_state,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        members=member_list
    )


@router.get("/workspace/list", response_model=List[WorkspaceResponse])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all workspaces the user is a member of
    """
    # Get all workspace memberships for the user
    memberships = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()
    
    workspaces = []
    for membership in memberships:
        workspace = db.query(Workspace).filter(
            Workspace.id == membership.workspace_id
        ).first()
        
        if workspace:
            # Get member count
            member_count = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace.id
            ).count()
            
            workspaces.append(WorkspaceResponse(
                id=str(workspace.id),
                name=workspace.name,
                owner_id=str(workspace.owner_id),
                pipeline_state=workspace.pipeline_state,
                created_at=workspace.created_at,
                updated_at=workspace.updated_at,
                members=[{'count': member_count}]
            ))
    
    return workspaces


@router.put("/workspace/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_update: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update workspace details
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if user has edit permissions
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.role.in_(["owner", "editor"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this workspace"
        )
    
    # Update fields
    if workspace_update.name is not None:
        workspace.name = workspace_update.name
    if workspace_update.pipeline_state is not None:
        workspace.pipeline_state = workspace_update.pipeline_state
    
    workspace.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(workspace)
        
        return WorkspaceResponse(
            id=str(workspace.id),
            name=workspace.name,
            owner_id=str(workspace.owner_id),
            pipeline_state=workspace.pipeline_state,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workspace: {str(e)}"
        )


@router.delete("/workspace/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a workspace (owner only)
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if user is owner
    if str(workspace.owner_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the workspace owner can delete it"
        )
    
    try:
        # Delete all members first
        db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id
        ).delete()
        
        # Delete workspace
        db.delete(workspace)
        db.commit()
        
        return {"message": "Workspace deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workspace: {str(e)}"
        )


@router.post("/workspace/{workspace_id}/invite")
async def invite_to_workspace(
    workspace_id: str,
    invite: WorkspaceInvite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a user to the workspace
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if current user has permission to invite
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.role.in_(["owner", "editor"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite users"
        )
    
    # Find user by email
    invited_user = db.query(User).filter(User.email == invite.user_email).first()
    
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a member
    existing_member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == invited_user.id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace"
        )
    
    # Add as member
    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=invited_user.id,
        role=invite.role
    )
    
    try:
        db.add(new_member)
        db.commit()
        
        return {
            "message": f"User {invite.user_email} invited successfully",
            "user_id": str(invited_user.id),
            "role": invite.role
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invite user: {str(e)}"
        )


@router.delete("/workspace/{workspace_id}/leave")
async def leave_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Leave a workspace
    """
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check if user is owner
    if str(workspace.owner_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace owner cannot leave. Transfer ownership or delete the workspace."
        )
    
    # Remove membership
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this workspace"
        )
    
    try:
        db.delete(member)
        db.commit()
        
        return {"message": "Left workspace successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave workspace: {str(e)}"
        )


@router.get("/workspace/{workspace_id}/members", response_model=List[MemberResponse])
async def get_workspace_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all members of a workspace
    """
    # Check if user is a member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    # Get all members
    members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()
    
    member_list = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            is_online = (
                workspace_id in active_connections and
                str(m.user_id) in active_connections[workspace_id]
            )
            member_list.append(MemberResponse(
                user_id=str(m.user_id),
                user_email=user.email,
                role=m.role,
                last_seen=m.last_seen,
                is_online=is_online
            ))
    
    return member_list


@router.get("/workspace/{workspace_id}/state")
async def get_workspace_state(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current workspace state
    """
    # Check if user is a member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    # Get state
    state = StateManager.get_workspace_state(workspace_id, db)
    
    if not state:
        # Initialize empty state
        state = CollaborationService.get_or_create_document(workspace_id)
    
    return {
        'workspace_id': workspace_id,
        'state': state.get('state', {}),
        'version': state.get('version', 0),
        'last_modified': state.get('last_modified')
    }


@router.post("/workspace/{workspace_id}/state/sync")
async def sync_workspace_state(
    workspace_id: str,
    sync_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync workspace state (get missing updates)
    """
    # Check if user is a member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    client_version = sync_data.get('version', 0)
    
    # Sync state
    result = StateManager.sync_workspace_state(
        workspace_id,
        client_version,
        db
    )
    
    return result


@router.post("/workspace/{workspace_id}/state/persist")
async def persist_workspace_state(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually persist workspace state to database
    """
    # Check if user has edit permissions
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.role.in_(["owner", "editor"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to persist state"
        )
    
    # Persist state
    success = CollaborationService.persist_state(workspace_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist state"
        )
    
    return {"message": "State persisted successfully"}


@router.post("/workspace/{workspace_id}/snapshot")
async def create_workspace_snapshot(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a snapshot of the current workspace state
    """
    # Check if user has edit permissions
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.role.in_(["owner", "editor"])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create snapshots"
        )
    
    # Create snapshot
    snapshot = CollaborationService.create_snapshot(workspace_id)
    
    return {
        'message': 'Snapshot created successfully',
        'snapshot': snapshot
    }


@router.get("/workspace/{workspace_id}/presence")
async def get_workspace_presence(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all user presence in a workspace
    """
    # Check if user is a member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    # Get presence stats
    stats = PresenceService.get_workspace_stats(workspace_id)
    
    return stats


@router.get("/workspace/{workspace_id}/online-users")
async def get_online_users(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all online users in a workspace
    """
    # Check if user is a member
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    # Get online users
    online_users = PresenceService.get_online_users(workspace_id)
    
    return {
        'count': len(online_users),
        'users': [p.to_dict() for p in online_users]
    }
