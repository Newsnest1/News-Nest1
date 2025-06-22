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

    # Check which articles already exist in the database
    article_urls = [art["url"] for art in articles]
    existing_urls = {
        res[0] for res in db.query(Article.url).filter(Article.url.in_(article_urls))
    }

    new_articles_to_add = []
    new_articles_to_return = []
    
    for article_data in articles:
        if article_data["url"] not in existing_urls:
            # First, categorize the article
            category = categorize_article(article_data["title"], article_data.get("summary", ""))
            
            new_article = Article(
                url=article_data["url"],
                title=article_data["title"],
                source=article_data["source"],
                content=article_data.get("summary", ""),
                published_at=datetime.fromisoformat(article_data["published_at"].replace("Z", "+00:00")),
                category=category, # Use the determined category
            )
            new_articles_to_add.append(new_article)
            new_articles_to_return.append(article_data)

    if new_articles_to_add:
        db.add_all(new_articles_to_add)
        db.commit()

    return new_articles_to_return[:limit]

def get_all_articles(db: Session):
    """Return all articles from the database."""
    return db.query(Article).all()
