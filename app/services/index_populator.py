import asyncio
import os
import logging
import hashlib
from app.services.feed_service import get_all_articles
from app.database import SessionLocal
import meilisearch

logger = logging.getLogger(__name__)
client = meilisearch.Client("http://search:7700", os.getenv("MEILI_MASTER_KEY", "a_master_key"))

def sanitize_id(url):
    """Convert URL to a valid MeiliSearch document ID by using a hash."""
    return hashlib.md5(url.encode()).hexdigest()

async def populate_meilisearch_index():
    logger.info("Starting MeiliSearch index population...")
    db = SessionLocal()
    try:
        # Fetch articles from the database
        logger.info("Fetching articles from database...")
        all_articles = get_all_articles(db)
        logger.info(f"Found {len(all_articles)} articles in database")

        # Convert ORM objects to dicts
        articles_dict = [
            {
                "id": sanitize_id(article.url),  # Use sanitized URL hash as ID
                "url": article.url,              # Keep original URL as a field
                "title": article.title,
                "source": article.source,
                "content": article.content,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "category": article.category,
            }
            for article in all_articles
        ]

        logger.info(f"Converted {len(articles_dict)} articles to dict format")

        if articles_dict:
            logger.info("Adding documents to MeiliSearch index...")
            try:
                index = client.index("articles")
                # Clear existing documents first
                index.delete_all_documents()
                # Add new documents
                result = index.add_documents(articles_dict, primary_key="id")
                logger.info(f"Successfully added documents to index. Result: {result}")
            except Exception as e:
                logger.error(f"Error adding documents to MeiliSearch: {e}")
                raise
        else:
            logger.warning("No articles found to index")
    except Exception as e:
        logger.error(f"Error in populate_meilisearch_index: {e}")
        raise
    finally:
        db.close()
