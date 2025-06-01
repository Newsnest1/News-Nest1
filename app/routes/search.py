from fastapi import APIRouter, Query
from app.services.search_service import search_articles

router = APIRouter(tags=["search"])

@router.get("/search")
async def search(q: str = Query(..., min_length=2), limit: int = Query(20, le=100)):
    """Full‑text search endpoint (currently stub)."""
    return {"items": await search_articles(q, limit)}
