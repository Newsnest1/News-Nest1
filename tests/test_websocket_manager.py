import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import WebSocket, WebSocketDisconnect

from app.services.websocket_manager import EnhancedWebSocketManager, manager

@pytest.fixture(autouse=True)
def clear_connections():
    manager.active_connections.clear()

@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    mock_ws = Mock(spec=WebSocket)
    mock_ws.send_text = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.accept = AsyncMock()
    return mock_ws

@pytest.mark.asyncio
async def test_connect_user(mock_websocket):
    """Test connecting a user to WebSocket."""
    user_id = 1
    
    # Test connection
    await manager.connect(mock_websocket, user_id)
    
    # Verify WebSocket was accepted
    mock_websocket.accept.assert_called_once()
    
    # Verify user is in active connections
    assert mock_websocket in manager.active_connections
    assert manager.active_connections[mock_websocket] == user_id

@pytest.mark.asyncio
async def test_disconnect_user(mock_websocket):
    """Test disconnecting a user from WebSocket."""
    user_id = 1
    
    # First connect the user
    await manager.connect(mock_websocket, user_id)
    assert mock_websocket in manager.active_connections
    
    # Then disconnect
    manager.disconnect(mock_websocket)
    
    # Verify user is removed from active connections
    assert mock_websocket not in manager.active_connections

@pytest.mark.asyncio
async def test_disconnect_nonexistent_user():
    """Test disconnecting a user that doesn't exist."""
    mock_ws = Mock(spec=WebSocket)
    
    # Should not raise an exception
    manager.disconnect(mock_ws)
    
    # Verify user is not in active connections
    assert mock_ws not in manager.active_connections

@pytest.mark.asyncio
async def test_send_personalized_notification(mock_websocket):
    """Test sending personalized notification to a specific user."""
    user_id = 1
    notification_data = {
        "type": "personalized_articles",
        "articles": [{"title": "Test Article"}],
        "count": 1,
        "message": "You have new articles!"
    }
    
    # Connect user
    await manager.connect(mock_websocket, user_id)
    
    # Send notification
    await manager.send_personalized_notification(user_id, notification_data)
    
    # Verify notification was sent
    mock_websocket.send_text.assert_called_once()

@pytest.mark.asyncio
async def test_send_personalized_notification_user_not_connected():
    """Test sending notification to user who is not connected."""
    user_id = 999
    notification_data = {"type": "test", "message": "test"}
    
    # Should not raise an exception
    await manager.send_personalized_notification(user_id, notification_data)

@pytest.mark.asyncio
async def test_broadcast_to_all_users(mock_websocket):
    """Test broadcasting message to all connected users."""
    user_id = 1
    message = "Broadcast message"
    
    # Connect user
    await manager.connect(mock_websocket, user_id)
    
    # Broadcast message
    await manager.broadcast(message)
    
    # Verify message was sent
    mock_websocket.send_text.assert_called_once_with(message)

@pytest.mark.asyncio
async def test_broadcast_to_no_users():
    """Test broadcasting when no users are connected."""
    message = "Broadcast message"
    
    # Should not raise an exception
    await manager.broadcast(message)

@pytest.mark.asyncio
async def test_send_notification_to_users(mock_websocket):
    """Test sending notification to multiple specific users."""
    user_id = 1
    notification_data = {
        "id": 1,
        "title": "Test Notification",
        "message": "Test message",
        "is_read": False,
        "created_at": "2023-01-01T12:00:00"
    }
    
    # Connect user
    await manager.connect(mock_websocket, user_id)
    
    # Send notification
    await manager.send_notification_to_users([user_id], notification_data)
    
    # Verify notification was sent
    mock_websocket.send_text.assert_called_once()

@pytest.mark.asyncio
async def test_send_notification_to_users_not_connected():
    """Test sending notification to users who are not connected."""
    user_ids = [999, 998]
    notification_data = {"title": "Test", "message": "test"}
    
    # Should not raise an exception
    await manager.send_notification_to_users(user_ids, notification_data)

@pytest.mark.asyncio
async def test_get_connected_users(mock_websocket):
    """Test getting list of connected users."""
    user_id = 1
    
    # Initially no users
    assert manager.get_connected_users() == []
    
    # Connect user
    await manager.connect(mock_websocket, user_id)
    
    # Should return the user
    assert manager.get_connected_users() == [user_id]
    
    # Disconnect
    manager.disconnect(mock_websocket)
    
    # Should be empty again
    assert manager.get_connected_users() == []

@pytest.mark.asyncio
async def test_websocket_connection_error_handling():
    """Test handling of WebSocket connection errors."""
    user_id = 1
    
    # Create a mock WebSocket that raises an exception on accept
    mock_ws = Mock(spec=WebSocket)
    mock_ws.accept = AsyncMock(side_effect=Exception("Connection failed"))
    mock_ws.send_text = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.close = AsyncMock()
    
    # Should handle the exception gracefully
    with pytest.raises(Exception, match="Connection failed"):
        await manager.connect(mock_ws, user_id)
    
    # Verify user is not in active connections
    assert mock_ws not in manager.active_connections

@pytest.mark.asyncio
async def test_websocket_send_error_handling(mock_websocket):
    """Test handling of WebSocket send errors."""
    user_id = 1
    message = "Test message"
    
    # Make send_text raise an exception
    mock_websocket.send_text = AsyncMock(side_effect=Exception("Send failed"))
    
    # Connect user
    await manager.connect(mock_websocket, user_id)
    
    # Should handle the exception gracefully
    await manager.broadcast(message)
    
    # Verify the connection was cleaned up
    assert mock_websocket not in manager.active_connections

@pytest.mark.asyncio
async def test_multiple_users_connection():
    """Test multiple users connecting and disconnecting."""
    user1_id = 1
    user2_id = 2
    
    # Create separate mock WebSockets for each user
    mock_ws1 = Mock(spec=WebSocket)
    mock_ws1.send_text = AsyncMock()
    mock_ws1.send_json = AsyncMock()
    mock_ws1.close = AsyncMock()
    mock_ws1.accept = AsyncMock()
    
    mock_ws2 = Mock(spec=WebSocket)
    mock_ws2.send_text = AsyncMock()
    mock_ws2.send_json = AsyncMock()
    mock_ws2.close = AsyncMock()
    mock_ws2.accept = AsyncMock()
    
    # Connect both users
    await manager.connect(mock_ws1, user1_id)
    await manager.connect(mock_ws2, user2_id)
    
    # Verify both are connected
    assert mock_ws1 in manager.active_connections
    assert mock_ws2 in manager.active_connections
    assert manager.active_connections[mock_ws1] == user1_id
    assert manager.active_connections[mock_ws2] == user2_id
    
    # Disconnect one user
    manager.disconnect(mock_ws1)
    
    # Verify only one remains
    assert mock_ws1 not in manager.active_connections
    assert mock_ws2 in manager.active_connections 