from fastapi import APIRouter, Query
from typing import Optional
from app.services.feed_service import get_latest_articles

router = APIRouter(tags=["feed"])

@router.get("/feed")
async def feed(
    limit: int = Query(20, le=100),
    category: Optional[str] = Query(None, description="Optional category filter (e.g. Technology, Sports, etc.)")
):
    """Return the most recent aggregated articles, optionally filtered by category."""
    articles = await get_latest_articles(limit=limit)

    # If a category filter is provided, filter the results
    if category:
        articles = [article for article in articles if article.get("category") == category]

    return {"items": articles}
