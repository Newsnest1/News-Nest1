from typing import Optional
from collections import defaultdict
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.services.feed_service import get_latest_articles
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
    articles = await get_latest_articles(db=db, limit=limit)

    if category:
        # Only return articles from one category if specified
        articles = [a for a in articles if a.get("category") == category]
        return {"items": articles}

    # Group articles by category
    grouped = defaultdict(list)
    for article in articles:
        grouped[article.get("category", "Other")].append(article)

    return grouped
