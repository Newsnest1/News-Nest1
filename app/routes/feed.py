from typing import Optional
from collections import defaultdict
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.feed_service import get_all_articles, get_latest_articles
from app.services.search_service import search_articles
from app.database import get_db
from app.services.auth_service import get_current_active_user, oauth2_scheme, get_current_user, get_current_optional_user
from app import crud, schemas
from app.services.notification_service import send_personalized_notifications, send_broadcast_notification
from app.services.index_populator import populate_meilisearch_index
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["feed"])


@router.get("/feed")
async def feed(
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    category: Optional[str] = Query(
        None, description="Optional category filter (e.g. Technology, Sports, etc.)"),
    current_user: Optional[schemas.User] = Depends(get_current_optional_user)
):
    """Return articles grouped by category, or filtered by one category."""
    if category:
        # Use MeiliSearch for typo-tolerant, case-insensitive category filtering
        search_results = await search_articles(
            q=category, 
            limit=limit, 
            attributes_to_search_on=['category']
        )
        
        # Add saved status if user is authenticated
        if current_user:
            for article in search_results:
                article['is_saved'] = crud.is_saved(db, current_user.id, article['url'])
        else:
            for article in search_results:
                article['is_saved'] = False
                
        return {"items": search_results}

    # If no category, get all articles and group them
    articles = get_all_articles(db=db)
    grouped = defaultdict(list)
    for article in articles:
        # Don't apply the limit here, group all and then slice if needed.
        # This part could be further optimized if needed.
        grouped[article.category].append(article)

    # Limit the number of articles per category for the final output
    for cat in grouped:
        grouped[cat] = grouped[cat][:limit]
        
    return grouped


@router.get("/feed/personalized")
async def personalized_feed(
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100)
):
    """Return articles filtered by user's followed topics and outlets."""
    # Get user's followed topics and outlets
    followed_topics = crud.get_followed_topics(db, current_user.id)
    followed_outlets = crud.get_followed_outlets(db, current_user.id)
    
    if not followed_topics and not followed_outlets:
        return {"items": [], "message": "No topics or outlets followed. Follow some to get personalized content!"}
    
    # Get all articles
    all_articles = get_all_articles(db=db)
    
    # Filter articles based on follows
    filtered_articles = []
    for article in all_articles:
        # Check if article matches followed topics or outlets
        topic_match = not followed_topics or article.category in followed_topics
        outlet_match = not followed_outlets or article.source in followed_outlets
        
        if topic_match or outlet_match:
            # Convert to dict and add saved status
            article_dict = {
                "url": article.url,
                "title": article.title,
                "source": article.source,
                "content": article.content,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "category": article.category,
                "is_saved": crud.is_saved(db, current_user.id, article.url)
            }
            filtered_articles.append(article_dict)
    
    # Sort by published_at (newest first) and limit
    filtered_articles.sort(key=lambda x: x["published_at"] or "", reverse=True)
    filtered_articles = filtered_articles[:limit]
    
    return {
        "items": filtered_articles,
        "followed_topics": followed_topics,
        "followed_outlets": followed_outlets
    }


@router.post("/feed/test-notifications")
async def test_notifications(
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manually trigger the notification system for testing."""
    try:
        logger.info("Manually triggering notification test...")
        
        # Get existing articles for testing
        articles = get_all_articles(db=db)
        
        if not articles:
            return {"message": "No articles found to test notifications"}
        
        # Take first 5 articles for testing
        test_articles = articles[:5]
        
        # Convert articles to dict format for notifications
        article_dicts = []
        for article in test_articles:
            article_dict = {
                "url": article.url,
                "title": article.title,
                "source": article.source,
                "category": article.category,
                "published_at": article.published_at.isoformat() if article.published_at else None
            }
            article_dicts.append(article_dict)
        
        # Send personalized notifications
        await send_personalized_notifications(article_dicts, db)
        
        # Also send broadcast notification
        await send_broadcast_notification(f"Test: Found {len(test_articles)} articles", len(test_articles))
        
        return {
            "message": f"Test notifications sent for {len(test_articles)} articles",
            "articles_count": len(test_articles),
            "articles": [{"title": a.title, "source": a.source, "category": a.category} for a in test_articles]
        }
        
    except Exception as e:
        logger.error(f"Error testing notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing notifications: {str(e)}")
