from typing import Optional, List
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


@router.get("/feed", response_model=List[schemas.Article])
async def get_feed(
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    category: Optional[str] = Query(None, description="Optional category filter.")
):
    """
    Get the latest articles from the feed.
    If a category is provided, it filters by that category.
    """
    if category:
        articles = crud.get_articles_by_category(db=db, category=category, limit=limit)
    else:
        articles = crud.get_articles(db=db, limit=limit)
    
    return articles


@router.get("/feed/categories")
async def get_categories(db: Session = Depends(get_db)):
    """
    Get all available categories from the database.
    """
    categories = crud.get_categories(db=db)
    return {"categories": categories}


@router.get("/feed/personalized", response_model=List[schemas.Article])
async def get_personalized_feed(
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100)
):
    """
    Get personalized feed based on user's followed topics and outlets.
    Note: This is a simplified version that returns all articles.
    For full personalization, user authentication would be required.
    """
    # For now, return all articles as a simplified personalized feed
    articles = crud.get_articles(db=db, limit=limit)
    return articles


@router.get("/feed/test")
async def get_test_feed():
    """
    Get a test feed for development purposes.
    """
    from app.database import Article
    
    test_articles = [
        Article(
            url="https://example.com/1",
            title="Test Article 1",
            source="Test Source",
            content="This is a test article about technology.",
            category="Technology",
            published_at=None
        ),
        Article(
            url="https://example.com/2", 
            title="Test Article 2",
            source="Test Source",
            content="This is a test article about business.",
            category="Business",
            published_at=None
        )
    ]
    
    return {
        "articles": [{"title": a.title, "source": a.source, "category": a.category} for a in test_articles]
    }


@router.post("/feed/populate-search-index")
async def populate_search_index(
    db: Session = Depends(get_db)
):
    """Manually populate the MeiliSearch index with articles from the database."""
    try:
        logger.info("Manually triggering search index population...")
        await populate_meilisearch_index()
        return {"message": "Search index populated successfully"}
    except Exception as e:
        logger.error(f"Error populating search index: {e}")
        raise HTTPException(status_code=500, detail=f"Error populating search index: {str(e)}")


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
