import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.adapters.newsapi_adapter import fetch_newsapi_articles
from app.adapters.rss_adapter import fetch_rss_articles
from app.services.categorization import categorize_article
from app.database import Article
from app import crud


async def fetch_and_store_latest_articles(db: Session, limit: int = 20):
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
    articles.sort(key=lambda x: x.get("published_at") or "", reverse=True)

    # Check which articles already exist in the database
    article_urls = [art["url"] for art in articles]
    existing_urls = {
        res[0] for res in db.query(Article.url).filter(Article.url.in_(article_urls))
    }

    new_articles_to_add = []
    
    for article_data in articles:
        if article_data["url"] not in existing_urls:
            # Use NewsAPI's built-in category for NewsAPI articles, custom categorization for RSS
            if article_data.get("source_type") == "newsapi" and article_data.get("category"):
                # Use NewsAPI's built-in category
                category = article_data["category"]
            else:
                # Apply custom categorization for RSS articles or articles without category
                category = categorize_article(article_data["title"], article_data.get("summary", ""))
            
            # Handle None published_at values
            published_at = None
            if article_data.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(article_data["published_at"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    published_at = None
            
            new_article = Article(
                url=article_data["url"],
                title=article_data["title"],
                source=article_data["source"],
                content=article_data.get("summary", ""),
                published_at=published_at,
                category=category, # Use the determined category
                image_url=article_data.get("image_url"),  # Store the image URL
            )
            new_articles_to_add.append(new_article)

    if new_articles_to_add:
        db.add_all(new_articles_to_add)
        db.commit()

    # After storing, fetch the latest to return them as ORM objects
    return get_latest_articles(db, limit)


def get_all_articles(db: Session):
    """A wrapper function to get all articles from the database."""
    return crud.get_all_articles(db=db)


def get_latest_articles(db: Session, limit: int = 20):
    """
    Get the latest articles from the database, sorted by published_at.
    """
    return db.query(Article).order_by(Article.published_at.desc()).limit(limit).all()
