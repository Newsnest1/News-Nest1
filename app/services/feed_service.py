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

    # Deduplicate articles from adapters first, based on URL
    unique_articles_dict = {art["url"]: art for art in articles}
    articles = list(unique_articles_dict.values())

    # Sort by published_at descending
    articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    new_articles_to_add = []
    new_articles_to_return = []
    
    for art in articles:
        # Check if article already exists in the DB
        exists = db.query(Article).filter(Article.url == art["url"]).first()
        if not exists:
            # Categorize only if the category is not already provided by the adapter
            if "category" not in art or not art["category"]:
                art["category"] = categorize_article(art)
            
            new_article = Article(
                url=art["url"],
                title=art["title"],
                source=art["source"],
                content=art.get("content"),
                published_at=datetime.fromisoformat(art["published_at"].replace("Z", "+00:00")) if art.get("published_at") else None,
                category=art["category"],
            )
            new_articles_to_add.append(new_article)
            new_articles_to_return.append(art)

    if new_articles_to_add:
        db.add_all(new_articles_to_add)
        db.commit()

    return new_articles_to_return[:limit]

def get_all_articles(db: Session):
    """Return all articles from the database."""
    return db.query(Article).all()
