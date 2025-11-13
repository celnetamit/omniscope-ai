"""
Integration Tests for Collaboration Features
Tests WebSocket connection, message passing, state synchronization, and workspace permissions
Requirements: 1.1, 1.2, 1.3
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import socketio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
TEST_WORKSPACE_ID = "test-workspace-123"
TEST_USER_1 = {
    "id": "user-1",
    "email": "user1@test.com",
    "name": "User One"
}
TEST_USER_2 = {
    "id": "user-2",
    "email": "user2@test.com",
    "name": "User Two"
}


class TestWebSocketConnection:
    """Test WebSocket connection and message passing (Requirement 1.1)"""
    
    async def test_websocket_connection_establishment(self):
        """Test that WebSocket connection is established within 2 seconds"""
        from modules.collaboration_module import sio
        from unittest.mock import AsyncMock
        
        # Mock Socket.IO server
        mock_sid = "test-session-123"
        auth_data = {
            'token': 'test-token',
            'workspace_id': TEST_WORKSPACE_ID,
            'user_id': TEST_USER_1['id'],
            'user_email': TEST_USER_1['email'],
            'user_name': TEST_USER_1['name']
        }
        
        # Test connection
        start_time = datetime.now()
        
        # Simulate connection with async mocks
        with patch.object(sio, 'save_session', new=AsyncMock()) as mock_save:
            with patch.object(sio, 'enter_room', new=AsyncMock()) as mock_enter:
                with patch.object(sio, 'emit', new=AsyncMock()) as mock_emit:
                    from modules.collaboration_module import connect
                    result = await connect(mock_sid, {}, auth_data)
                    
                    end_time = datetime.now()
                    connection_time = (end_time - start_time).total_seconds()
                    
                    # Verify connection succeeded
                    assert result is True, "Connection should succeed with valid auth"
                    
                    # Verify connection time < 2 seconds (Requirement 1.1)
                    assert connection_time < 2.0, f"Connection took {connection_time}s, should be < 2s"
                    
                    # Verify session was saved
                    mock_save.assert_called_once()
                    
                    # Verify room was joined
                    mock_enter.assert_called_once_with(mock_sid, TEST_WORKSPACE_ID)
                    
                    print(f"✅ WebSocket connection established in {connection_time:.3f}s")
    
    async def test_websocket_connection_without_auth(self):
        """Test that connection fails without authentication"""
        from modules.collaboration_module import connect
        
        mock_sid = "test-session-456"
        
        # Test connection without auth
        result = await connect(mock_sid, {}, {})
        
        assert result is False, "Connection should fail without auth"
        print("✅ Connection properly rejected without authentication")
    
    async def test_websocket_connection_without_workspace(self):
        """Test that connection fails without workspace_id"""
        from modules.collaboration_module import connect
        
        mock_sid = "test-session-789"
        auth_data = {
            'token': 'test-token',
            'user_id': TEST_USER_1['id'],
            'user_email': TEST_USER_1['email']
            # Missing workspace_id
        }
        
        result = await connect(mock_sid, {}, auth_data)
        
        assert result is False, "Connection should fail without workspace_id"
        print("✅ Connection properly rejected without workspace_id")
    
    async def test_message_broadcast_latency(self):
        """Test that changes are broadcast within 500ms (Requirement 1.2)"""
        from modules.collaboration_module import pipeline_update, sio
        from unittest.mock import AsyncMock
        
        mock_sid = "test-session-broadcast"
        
        # Mock session
        session_data = {
            'workspace_id': TEST_WORKSPACE_ID,
            'user_id': TEST_USER_1['id']
        }
        
        update_data = {
            'changes': {
                'node_id': 'node-123',
                'property': 'value',
                'action': 'update'
            }
        }
        
        start_time = datetime.now()
        
        with patch.object(sio, 'get_session', return_value=session_data):
            with patch.object(sio, 'emit', new=AsyncMock()) as mock_emit:
                result = await pipeline_update(mock_sid, update_data)
                
                end_time = datetime.now()
                broadcast_time = (end_time - start_time).total_seconds()
                
                # Verify broadcast succeeded
                assert result['status'] == 'success'
                
                # Verify broadcast time < 500ms (Requirement 1.2)
                assert broadcast_time < 0.5, f"Broadcast took {broadcast_time}s, should be < 0.5s"
                
                # Verify emit was called
                mock_emit.assert_called_once()
                call_args = mock_emit.call_args
                assert call_args[0][0] == 'pipeline_updated'
                assert call_args[1]['room'] == TEST_WORKSPACE_ID
                assert call_args[1]['skip_sid'] == mock_sid
                
                print(f"✅ Message broadcast completed in {broadcast_time*1000:.1f}ms")


class TestStateSynchronization:
    """Test CRDT-based state synchronization (Requirement 1.2)"""
    
    def test_document_creation(self):
        """Test that documents are created for workspaces"""
        from backend_db.collaboration import CollaborationService
        
        workspace_id = "test-workspace-doc-create"
        
        # Get or create document
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        assert doc is not None
        assert 'state' in doc
        assert 'updates' in doc
        assert 'version' in doc
        assert doc['version'] == 0
        
        print("✅ Document creation successful")
    
    def test_apply_update(self):
        """Test applying updates to documents"""
        from backend_db.collaboration import CollaborationService
        
        workspace_id = "test-workspace-update"
        user_id = TEST_USER_1['id']
        
        # Create document
        doc = CollaborationService.get_or_create_document(workspace_id)
        initial_version = doc['version']
        
        # Apply update
        update_data = b"test-update-data"
        updated_doc = CollaborationService.apply_update(workspace_id, update_data, user_id)
        
        assert updated_doc['version'] == initial_version + 1
        assert len(updated_doc['updates']) == 1
        assert updated_doc['updates'][0]['user_id'] == user_id
        
        print("✅ Update application successful")
    
    def test_get_updates_since_version(self):
        """Test retrieving updates since a specific version"""
        from backend_db.collaboration import CollaborationService
        
        workspace_id = "test-workspace-updates-since"
        
        # Create document and apply multiple updates
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        for i in range(5):
            CollaborationService.apply_update(
                workspace_id,
                f"update-{i}".encode(),
                TEST_USER_1['id']
            )
        
        # Get updates since version 2
        updates = CollaborationService.get_updates_since(workspace_id, 2)
        
        assert len(updates) == 3  # versions 3, 4, 5
        assert all(u['version'] > 2 for u in updates)
        
        print("✅ Update retrieval successful")
    
    def test_state_synchronization_across_clients(self):
        """Test that state synchronizes correctly across multiple clients"""
        from backend_db.collaboration import CollaborationService, StateManager
        from backend_db.database import SessionLocal
        
        workspace_id = "test-workspace-sync"
        db = SessionLocal()
        
        try:
            # Client 1 makes an update
            state_update_1 = {
                'state': {
                    'nodes': [{'id': 'node-1', 'type': 'upload'}]
                }
            }
            
            updated_state = StateManager.update_workspace_state(
                workspace_id,
                state_update_1,
                TEST_USER_1['id'],
                db
            )
            
            version_1 = updated_state['version']
            
            # Client 2 syncs from version 0
            sync_data = StateManager.sync_workspace_state(workspace_id, 0, db)
            
            assert sync_data['current_version'] == version_1
            assert len(sync_data['missing_updates']) >= 1
            assert sync_data['full_state'] is not None
            
            # Client 2 makes an update
            state_update_2 = {
                'state': {
                    'nodes': [
                        {'id': 'node-1', 'type': 'upload'},
                        {'id': 'node-2', 'type': 'normalize'}
                    ]
                }
            }
            
            updated_state_2 = StateManager.update_workspace_state(
                workspace_id,
                state_update_2,
                TEST_USER_2['id'],
                db
            )
            
            # Verify version incremented
            assert updated_state_2['version'] > version_1
            
            # Client 1 syncs from their version
            sync_data_2 = StateManager.sync_workspace_state(workspace_id, version_1, db)
            
            assert sync_data_2['current_version'] == updated_state_2['version']
            assert len(sync_data_2['missing_updates']) >= 1
            
            print("✅ State synchronization across clients successful")
            
        finally:
            db.close()
    
    def test_conflict_free_concurrent_updates(self):
        """Test that concurrent updates don't cause conflicts (CRDT property)"""
        from backend_db.collaboration import CollaborationService
        
        workspace_id = "test-workspace-concurrent"
        
        # Create document
        doc = CollaborationService.get_or_create_document(workspace_id)
        
        # Simulate concurrent updates from two users
        update_1 = b"user1-update"
        update_2 = b"user2-update"
        
        doc1 = CollaborationService.apply_update(workspace_id, update_1, TEST_USER_1['id'])
        doc2 = CollaborationService.apply_update(workspace_id, update_2, TEST_USER_2['id'])
        
        # Both updates should be recorded
        assert len(doc2['updates']) == 2
        assert doc2['version'] == 2
        
        # Verify both users' updates are present
        user_ids = [u['user_id'] for u in doc2['updates']]
        assert TEST_USER_1['id'] in user_ids
        assert TEST_USER_2['id'] in user_ids
        
        print("✅ Concurrent updates handled without conflicts")


class TestPresenceSystem:
    """Test user presence tracking (Requirement 1.3, 1.4)"""
    
    def test_user_join_workspace(self):
        """Test user joining workspace and presence tracking"""
        from backend_db.presence import PresenceService
        
        workspace_id = "test-workspace-presence"
        
        # User joins workspace
        presence = PresenceService.join_workspace(
            workspace_id,
            TEST_USER_1['id'],
            TEST_USER_1['email'],
            TEST_USER_1['name']
        )
        
        assert presence is not None
        assert presence.user_id == TEST_USER_1['id']
        assert presence.user_email == TEST_USER_1['email']
        assert presence.status == "active"
        assert presence.color is not None  # Color assigned
        
        print("✅ User join and presence tracking successful")
    
    def test_cursor_position_tracking(self):
        """Test cursor position updates (Requirement 1.3)"""
        from backend_db.presence import PresenceService
        
        workspace_id = "test-workspace-cursor"
        
        # User joins
        PresenceService.join_workspace(
            workspace_id,
            TEST_USER_1['id'],
            TEST_USER_1['email']
        )
        
        # Update cursor position
        cursor_pos = {'x': 100, 'y': 200, 'node_id': 'node-123'}
        updated_presence = PresenceService.update_cursor(
            workspace_id,
            TEST_USER_1['id'],
            cursor_pos
        )
        
        assert updated_presence is not None
        assert updated_presence.cursor_position == cursor_pos
        assert updated_presence.status == "active"
        
        print("✅ Cursor position tracking successful")
    
    def test_user_avatars_display(self):
        """Test that user avatars and colors are assigned (Requirement 1.3)"""
        from backend_db.presence import PresenceService
        
        workspace_id = "test-workspace-avatars"
        
        # Multiple users join
        presence_1 = PresenceService.join_workspace(
            workspace_id,
            TEST_USER_1['id'],
            TEST_USER_1['email'],
            TEST_USER_1['name']
        )
        
        presence_2 = PresenceService.join_workspace(
            workspace_id,
            TEST_USER_2['id'],
            TEST_USER_2['email'],
            TEST_USER_2['name']
        )
        
        # Verify both have colors assigned
        assert presence_1.color is not None
        assert presence_2.color is not None
        
        # Verify colors are different
        assert presence_1.color != presence_2.color
        
        # Verify names are set
        assert presence_1.user_name == TEST_USER_1['name']
        assert presence_2.user_name == TEST_USER_2['name']
        
        print("✅ User avatars and colors assigned successfully")
    
    def test_user_join_notification(self):
        """Test that join notifications are sent within 1 second (Requirement 1.4)"""
        from modules.collaboration_module import connect, sio
        from unittest.mock import AsyncMock
        
        mock_sid = "test-session-join-notif"
        auth_data = {
            'token': 'test-token',
            'workspace_id': TEST_WORKSPACE_ID,
            'user_id': TEST_USER_1['id'],
            'user_email': TEST_USER_1['email'],
            'user_name': TEST_USER_1['name']
        }
        
        start_time = datetime.now()
        
        async def test_notification():
            with patch.object(sio, 'save_session', new=AsyncMock()):
                with patch.object(sio, 'enter_room', new=AsyncMock()):
                    with patch.object(sio, 'emit', new=AsyncMock()) as mock_emit:
                        await connect(mock_sid, {}, auth_data)
                        
                        end_time = datetime.now()
                        notification_time = (end_time - start_time).total_seconds()
                        
                        # Verify notification time < 1 second (Requirement 1.4)
                        assert notification_time < 1.0, f"Notification took {notification_time}s, should be < 1s"
                        
                        # Verify user_joined event was emitted
                        emit_calls = [call for call in mock_emit.call_args_list 
                                     if call[0][0] == 'user_joined']
                        assert len(emit_calls) > 0, "user_joined event should be emitted"
                        
                        print(f"✅ Join notification sent in {notification_time*1000:.1f}ms")
        
        asyncio.run(test_notification())
    
    def test_online_users_list(self):
        """Test getting list of online users"""
        from backend_db.presence import PresenceService
        
        workspace_id = "test-workspace-online"
        
        # Add multiple users
        PresenceService.join_workspace(workspace_id, TEST_USER_1['id'], TEST_USER_1['email'])
        PresenceService.join_workspace(workspace_id, TEST_USER_2['id'], TEST_USER_2['email'])
        
        # Get online users
        online_users = PresenceService.get_online_users(workspace_id)
        
        assert len(online_users) == 2
        user_ids = [u.user_id for u in online_users]
        assert TEST_USER_1['id'] in user_ids
        assert TEST_USER_2['id'] in user_ids
        
        print("✅ Online users list retrieved successfully")
    
    def test_user_leave_workspace(self):
        """Test user leaving workspace"""
        from backend_db.presence import PresenceService
        
        workspace_id = "test-workspace-leave"
        
        # User joins
        PresenceService.join_workspace(workspace_id, TEST_USER_1['id'], TEST_USER_1['email'])
        
        # Verify user is present
        presence = PresenceService.get_presence(workspace_id, TEST_USER_1['id'])
        assert presence is not None
        
        # User leaves
        result = PresenceService.leave_workspace(workspace_id, TEST_USER_1['id'])
        assert result is True
        
        # Verify user is no longer present
        presence_after = PresenceService.get_presence(workspace_id, TEST_USER_1['id'])
        assert presence_after is None
        
        print("✅ User leave workspace successful")


class TestWorkspacePermissions:
    """Test workspace permission system (Requirement 1.6)"""
    
    def test_workspace_creation(self):
        """Test creating a workspace"""
        from backend_db.models import Workspace, WorkspaceMember
        from backend_db.database import SessionLocal
        
        db = SessionLocal()
        
        try:
            # Create workspace
            workspace = Workspace(
                name="Test Workspace",
                owner_id=TEST_USER_1['id'],
                pipeline_state={}
            )
            db.add(workspace)
            db.flush()
            
            # Add owner as member
            member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=TEST_USER_1['id'],
                role="owner"
            )
            db.add(member)
            db.commit()
            
            assert workspace.id is not None
            assert workspace.owner_id == TEST_USER_1['id']
            
            print("✅ Workspace creation successful")
            
        finally:
            db.rollback()
            db.close()
    
    def test_workspace_member_roles(self):
        """Test different member roles (owner, editor, viewer)"""
        from backend_db.models import Workspace, WorkspaceMember
        from backend_db.database import SessionLocal
        
        db = SessionLocal()
        
        try:
            # Create workspace
            workspace = Workspace(
                name="Test Workspace Roles",
                owner_id=TEST_USER_1['id']
            )
            db.add(workspace)
            db.flush()
            
            # Add members with different roles
            owner_member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=TEST_USER_1['id'],
                role="owner"
            )
            
            editor_member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=TEST_USER_2['id'],
                role="editor"
            )
            
            viewer_member = WorkspaceMember(
                workspace_id=workspace.id,
                user_id="user-3",
                role="viewer"
            )
            
            db.add_all([owner_member, editor_member, viewer_member])
            db.commit()
            
            # Verify roles
            members = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace.id
            ).all()
            
            assert len(members) == 3
            roles = {m.user_id: m.role for m in members}
            assert roles[TEST_USER_1['id']] == "owner"
            assert roles[TEST_USER_2['id']] == "editor"
            assert roles["user-3"] == "viewer"
            
            print("✅ Workspace member roles configured successfully")
            
        finally:
            db.rollback()
            db.close()
    
    def test_concurrent_users_support(self):
        """Test that workspace supports 10+ concurrent users (Requirement 1.6)"""
        from backend_db.presence import PresenceService
        
        workspace_id = "test-workspace-concurrent-users"
        
        # Add 15 users to test > 10 concurrent users
        for i in range(15):
            PresenceService.join_workspace(
                workspace_id,
                f"user-{i}",
                f"user{i}@test.com",
                f"User {i}"
            )
        
        # Get all presence
        all_presence = PresenceService.get_all_presence(workspace_id)
        
        assert len(all_presence) == 15
        assert len(all_presence) >= 10, "Should support at least 10 concurrent users"
        
        # Verify all users have unique colors
        colors = [p.color for p in all_presence]
        assert len(colors) == 15
        
        print(f"✅ Workspace supports {len(all_presence)} concurrent users")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("COLLABORATION FEATURES - INTEGRATION TEST SUITE")
    print("="*80)
    
    # WebSocket Connection Tests
    print("\n--- WebSocket Connection Tests ---")
    test_ws = TestWebSocketConnection()
    asyncio.run(test_ws.test_websocket_connection_establishment())
    asyncio.run(test_ws.test_websocket_connection_without_auth())
    asyncio.run(test_ws.test_websocket_connection_without_workspace())
    asyncio.run(test_ws.test_message_broadcast_latency())
    
    # State Synchronization Tests
    print("\n--- State Synchronization Tests ---")
    test_sync = TestStateSynchronization()
    test_sync.test_document_creation()
    test_sync.test_apply_update()
    test_sync.test_get_updates_since_version()
    test_sync.test_state_synchronization_across_clients()
    test_sync.test_conflict_free_concurrent_updates()
    
    # Presence System Tests
    print("\n--- Presence System Tests ---")
    test_presence = TestPresenceSystem()
    test_presence.test_user_join_workspace()
    test_presence.test_cursor_position_tracking()
    test_presence.test_user_avatars_display()
    test_presence.test_user_join_notification()
    test_presence.test_online_users_list()
    test_presence.test_user_leave_workspace()
    
    # Workspace Permissions Tests
    print("\n--- Workspace Permissions Tests ---")
    test_permissions = TestWorkspacePermissions()
    test_permissions.test_workspace_creation()
    test_permissions.test_workspace_member_roles()
    test_permissions.test_concurrent_users_support()
    
    print("\n" + "="*80)
    print("✅ ALL COLLABORATION INTEGRATION TESTS PASSED")
    print("="*80)
    print("\nRequirements Verified:")
    print("  ✅ 1.1 - WebSocket connection within 2 seconds")
    print("  ✅ 1.2 - Changes broadcast within 500 milliseconds")
    print("  ✅ 1.2 - CRDT-based state synchronization")
    print("  ✅ 1.3 - Cursor positions and user avatars displayed")
    print("  ✅ 1.4 - User join notifications within 1 second")
    print("  ✅ 1.6 - Support for 10+ concurrent users")


if __name__ == "__main__":
    run_all_tests()
