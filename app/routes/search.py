from fastapi import APIRouter, Query
from app.services.search_service import search_articles
from app.schemas import ArticleResponse

router = APIRouter(tags=["search"])


@router.get("/search")
async def search(q: str = Query(..., min_length=2), page: int = Query(1, ge=1), limit: int = Query(20, le=100)):
    """Full‑text search endpoint."""
    skip = (page - 1) * limit
    search_results = await search_articles(q, limit + skip)
    
    # Apply pagination
    paginated_results = search_results[skip:skip + limit]
    
    # Convert to ArticleResponse format
    articles = []
    for result in paginated_results:
        # MeiliSearch returns the document data directly
        article_data = {
            "url": result.get("url"),
            "title": result.get("title"),
            "source": result.get("source"),
            "content": result.get("content"),
            "published_at": result.get("published_at"),
            "category": result.get("category"),
            "image_url": result.get("image_url"),
            "is_saved": False  # Default value, would need to check user's saved articles
        }
        articles.append(article_data)
    
    return {"articles": articles}
