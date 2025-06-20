import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.adapters.newsapi_adapter import fetch_newsapi_articles
from app.adapters.rss_adapter import fetch_rss_articles
from app.services.categorization import categorize_article
from app.database import Article


async def get_latest_articles(db: Session, limit: int = 20):
    """Fetch and merge articles from all adapters, deduplicate & sort."""
    newsapi_task = fetch_newsapi_articles(limit=limit)
    rss_task = fetch_rss_articles(limit=limit)

    results = await asyncio.gather(newsapi_task, rss_task, return_exceptions=True)
    articles = [
        item for sub in results if not isinstance(sub, Exception) for item in sub
    ]

    # Sort by published_at descending
    articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    new_articles = []
    for art in articles:
        # Check if article already exists in the DB
        exists = db.query(Article).filter(Article.url == art["url"]).first()
        if not exists:
            art["category"] = categorize_article(art)
            new_article = Article(
                url=art["url"],
                title=art["title"],
                source=art["source"],
                content=art.get("content"),
                published_at=datetime.fromisoformat(art["published_at"].replace("Z", "+00:00")) if art.get("published_at") else None,
                category=art["category"],
            )
            db.add(new_article)
            new_articles.append(art)
    
    db.commit()

    # The database now ensures uniqueness, so we just return the new articles
    return new_articles[:limit]

def get_all_articles(db: Session):
    """Return all articles from the database."""
    return db.query(Article).all()
