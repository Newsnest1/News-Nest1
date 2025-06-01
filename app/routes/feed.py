from fastapi import APIRouter, Query
from typing import List
from app.services.feed_service import get_latest_articles

router = APIRouter(tags=["feed"])

@router.get("/feed")
async def feed(limit: int = Query(20, le=100)):
    """Return the most recent aggregated articles."""
    articles = await get_latest_articles(limit=limit)
    return {"items": articles}
