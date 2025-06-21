import asyncio
import os
from app.services.feed_service import get_all_articles
from app.database import SessionLocal
import meilisearch

client = meilisearch.Client("http://search:7700", "79218197551724857046")

async def populate_meilisearch_index():
    db = SessionLocal()
    try:
        # Fetch articles from the database
        all_articles = get_all_articles(db)

        # Convert ORM objects to dicts
        articles_dict = [
            {
                "id": article.url,  # Use URL as the unique ID
                "title": article.title,
                "source": article.source,
                "content": article.content,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "category": article.category,
            }
            for article in all_articles
        ]

        if articles_dict:
            client.index("articles").add_documents(articles_dict, primary_key="id")
    finally:
        db.close()
