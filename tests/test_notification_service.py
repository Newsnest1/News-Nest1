import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.notification_service import (
    send_personalized_notifications,
    send_broadcast_notification
)
from app import crud, schemas
from app.database import User, Article

# Test data
TEST_USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

@pytest.mark.asyncio
async def test_send_personalized_notifications_with_matching_articles(db_session):
    """Test sending personalized notifications when articles match user preferences."""
    # Create a test user with notification preferences
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Set user notification preferences
    user.notifications_enabled = True
    user.notify_topics = True
    user.notify_outlets = True
    db_session.commit()
    
    # Create test articles
    new_articles = [
        {
            "title": "Tech Article",
            "url": "http://test.com/tech",
            "source": "Tech Source",
            "category": "Technology",
            "published_at": "2023-01-01T12:00:00Z"
        },
        {
            "title": "Business Article", 
            "url": "http://test.com/business",
            "source": "Business Source",
            "category": "Business",
            "published_at": "2023-01-01T13:00:00Z"
        }
    ]
    
    # Mock the WebSocket manager
    with patch('app.services.notification_service.manager') as mock_manager:
        mock_manager.send_personalized_notification = AsyncMock()
        
        await send_personalized_notifications(new_articles, db_session)
        
        # Verify notification was sent
        mock_manager.send_personalized_notification.assert_called_once()
        call_args = mock_manager.send_personalized_notification.call_args
        assert call_args[0][0] == user.id  # user_id
        notification_data = call_args[0][1]  # notification data
        assert notification_data["type"] == "personalized_articles"
        assert len(notification_data["articles"]) == 2

@pytest.mark.asyncio
async def test_send_personalized_notifications_no_matching_articles(db_session):
    """Test sending personalized notifications when no articles match user preferences."""
    # Create a test user with notification preferences
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Set user notification preferences
    user.notifications_enabled = True
    user.notify_topics = True
    user.notify_outlets = True
    db_session.commit()
    
    # Create test articles that don't match user follows
    new_articles = [
        {
            "title": "Unrelated Article",
            "url": "http://test.com/unrelated",
            "source": "Unrelated Source",
            "category": "Unrelated",
            "published_at": "2023-01-01T12:00:00Z"
        }
    ]
    
    # Patch follows to non-empty lists that do not match the article
    with patch('app.services.notification_service.crud.get_followed_topics', return_value=["Technology"]):
        with patch('app.services.notification_service.crud.get_followed_outlets', return_value=["Tech Source"]):
            # Mock the WebSocket manager
            with patch('app.services.notification_service.manager') as mock_manager:
                mock_manager.send_personalized_notification = AsyncMock()
                
                await send_personalized_notifications(new_articles, db_session)
                
                # Verify no notification was sent (no matching articles)
                mock_manager.send_personalized_notification.assert_not_called()

@pytest.mark.asyncio
async def test_send_personalized_notifications_user_notifications_disabled(db_session):
    """Test that notifications are not sent when user has notifications disabled."""
    # Create a test user with notifications disabled
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Set user notification preferences to disabled
    user.notifications_enabled = False
    db_session.commit()
    
    # Create test articles
    new_articles = [
        {
            "title": "Tech Article",
            "url": "http://test.com/tech",
            "source": "Tech Source",
            "category": "Technology",
            "published_at": "2023-01-01T12:00:00Z"
        }
    ]
    
    # Mock the WebSocket manager
    with patch('app.services.notification_service.manager') as mock_manager:
        mock_manager.send_personalized_notification = AsyncMock()
        
        await send_personalized_notifications(new_articles, db_session)
        
        # Verify no notification was sent
        mock_manager.send_personalized_notification.assert_not_called()

@pytest.mark.asyncio
async def test_send_personalized_notifications_empty_articles(db_session):
    """Test sending personalized notifications with empty article list."""
    # Mock the WebSocket manager
    with patch('app.services.notification_service.manager') as mock_manager:
        mock_manager.send_personalized_notification = AsyncMock()
        
        await send_personalized_notifications([], db_session)
        
        # Verify no notification was sent
        mock_manager.send_personalized_notification.assert_not_called()

@pytest.mark.asyncio
async def test_send_personalized_notifications_with_topic_follows(db_session):
    """Test sending personalized notifications based on topic follows."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Set user notification preferences
    user.notifications_enabled = True
    user.notify_topics = True
    user.notify_outlets = False
    db_session.commit()
    
    # Mock the CRUD function to return followed topics
    with patch('app.services.notification_service.crud.get_followed_topics', return_value=["Technology"]):
        with patch('app.services.notification_service.crud.get_followed_outlets', return_value=[]):
            
            # Create test articles
            new_articles = [
                {
                    "title": "Tech Article",
                    "url": "http://test.com/tech",
                    "source": "Tech Source",
                    "category": "Technology",
                    "published_at": "2023-01-01T12:00:00Z"
                }
            ]
            
            # Mock the WebSocket manager
            with patch('app.services.notification_service.manager') as mock_manager:
                mock_manager.send_personalized_notification = AsyncMock()
                
                await send_personalized_notifications(new_articles, db_session)
                
                # Verify notification was sent
                mock_manager.send_personalized_notification.assert_called_once()

@pytest.mark.asyncio
async def test_send_broadcast_notification(db_session):
    """Test sending broadcast notification to all connected clients."""
    # Mock the WebSocket manager
    with patch('app.services.notification_service.manager') as mock_manager:
        mock_manager.broadcast = AsyncMock()
        
        await send_broadcast_notification("New articles available!", 5)
        
        # Verify broadcast was sent
        mock_manager.broadcast.assert_called_once()
        call_args = mock_manager.broadcast.call_args
        broadcast_data = call_args[0][0]  # The notification data
        
        # The broadcast data should be a string representation of the notification
        assert "new_articles" in broadcast_data
        assert "5" in broadcast_data
        assert "New articles available!" in broadcast_data

@pytest.mark.asyncio
async def test_send_personalized_notifications_error_handling(db_session):
    """Test error handling in personalized notifications."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Set user notification preferences
    user.notifications_enabled = True
    user.notify_topics = True
    user.notify_outlets = True
    db_session.commit()
    
    # Create test articles
    new_articles = [
        {
            "title": "Tech Article",
            "url": "http://test.com/tech",
            "source": "Tech Source",
            "category": "Technology",
            "published_at": "2023-01-01T12:00:00Z"
        }
    ]
    
    # Mock the WebSocket manager to raise an exception
    with patch('app.services.notification_service.manager') as mock_manager:
        mock_manager.send_personalized_notification = AsyncMock(side_effect=Exception("WebSocket error"))
        
        # Should not raise an exception, should handle it gracefully
        await send_personalized_notifications(new_articles, db_session)
        
        # Verify the function completed without crashing
        assert True  # If we get here, no exception was raised 