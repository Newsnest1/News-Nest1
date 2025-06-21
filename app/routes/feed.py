from typing import Optional
from collections import defaultdict
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.services.feed_service import get_latest_articles, get_all_articles
from app.database import get_db

router = APIRouter(tags=["feed"])


@router.get("/feed")
async def feed(
    db: Session = Depends(get_db),
    limit: int = Query(20, le=100),
    category: Optional[str] = Query(
        None, description="Optional category filter (e.g. Technology, Sports, etc.)")
):
    """Return articles grouped by category, or filtered by one category."""
    articles = get_all_articles(db=db)

    if category:
        # Only return articles from one category if specified
        articles = [a for a in articles if a.category == category]
        return {"items": articles[:limit]}

    # Group articles by category
    grouped = defaultdict(list)
    for article in articles:
        if len(grouped[article.category]) < limit:
            grouped[article.category].append(article)

    # Return a limited number of articles per category
    return grouped
