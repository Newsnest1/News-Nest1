import asyncio
from app.adapters.rss_adapter import fetch_rss_articles
from app.adapters.newsapi_adapter import fetch_newsapi_articles
import meilisearch

client = meilisearch.Client("http://search:7700", "79218197551724857046")

async def populate_meilisearch_index():
    # Fetch articles from both sources
    rss_articles = await fetch_rss_articles(limit=50)
    newsapi_articles = await fetch_newsapi_articles(limit=50)
    all_articles = rss_articles + newsapi_articles

    # Assign unique IDs to each article (required by MeiliSearch)
    for i, article in enumerate(all_articles):
        article["id"] = i + 1

    if all_articles:
        client.index("articles").add_documents(all_articles)
