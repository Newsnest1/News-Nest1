from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .. import crud, database
from .websocket_manager import manager
import logging

logger = logging.getLogger(__name__)

async def send_personalized_notifications(new_articles: List[Dict[str, Any]], db: Session):
    """
    Send personalized notifications to users based on their follows and preferences.
    
    Args:
        new_articles: List of new articles with their details
        db: Database session
    """
    if not new_articles:
        return
    
    # Get all users with their notification preferences
    users = db.query(database.User).filter(
        database.User.notifications_enabled == True
    ).all()
    
    for user in users:
        try:
            # Check if user should receive notifications
            if not user.notifications_enabled:
                continue
            
            # Get user's follows
            followed_topics = crud.get_followed_topics(db, user.id)
            followed_outlets = crud.get_followed_outlets(db, user.id)
            
            # Filter articles relevant to this user
            relevant_articles = []
            
            for article in new_articles:
                # Check if article matches user's follows
                topic_match = (not user.notify_topics or not followed_topics or 
                             article.get('category') in followed_topics)
                outlet_match = (not user.notify_outlets or not followed_outlets or 
                              article.get('source') in followed_outlets)
                
                if topic_match or outlet_match:
                    relevant_articles.append(article)
            
            # Send notification if there are relevant articles
            if relevant_articles:
                notification = {
                    "type": "personalized_articles",
                    "user_id": user.id,
                    "articles": relevant_articles[:5],  # Limit to 5 articles
                    "count": len(relevant_articles),
                    "message": f"You have {len(relevant_articles)} new articles from your followed topics/outlets!"
                }
                
                await manager.send_personalized_notification(user.id, notification)
                logger.info(f"Sent personalized notification to user {user.id} for {len(relevant_articles)} articles")
        
        except Exception as e:
            logger.error(f"Error sending notification to user {user.id}: {e}")

async def send_broadcast_notification(message: str, article_count: int):
    """
    Send broadcast notification to all connected clients (existing functionality).
    
    Args:
        message: Notification message
        article_count: Number of new articles
    """
    notification = {
        "type": "new_articles",
        "count": article_count,
        "message": message
    }
    
    await manager.broadcast(str(notification))
    logger.info(f"Sent broadcast notification: {message}") 