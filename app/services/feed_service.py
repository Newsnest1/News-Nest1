import asyncio

from app.adapters.newsapi_adapter import fetch_newsapi_articles
from app.adapters.rss_adapter import fetch_rss_articles
from app.services.categorization import categorize_article


async def get_latest_articles(limit: int = 20):
    """Fetch and merge articles from all adapters, deduplicate & sort."""
    newsapi_task = fetch_newsapi_articles(limit=limit)
    rss_task = fetch_rss_articles(limit=limit)

    results = await asyncio.gather(newsapi_task, rss_task, return_exceptions=True)
    articles = [
        item for sub in results if not isinstance(sub, Exception) for item in sub
    ]

    # Sort by published_at descending
    articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    # Deduplicate by title + source
    seen = set()
    unique = []
    for art in articles:
        key = art["title"] + art["source"]
        if key not in seen:
            seen.add(key)
            art["category"] = categorize_article(art)
            unique.append(art)
    return unique[:limit]
