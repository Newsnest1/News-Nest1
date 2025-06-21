from typing import Optional
from collections import defaultdict
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.services.feed_service import get_all_articles
from app.services.search_service import search_articles
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
    if category:
        # Use MeiliSearch for typo-tolerant, case-insensitive category filtering
        search_results = await search_articles(
            q=category, 
            limit=limit, 
            attributes_to_search_on=['category']
        )
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
