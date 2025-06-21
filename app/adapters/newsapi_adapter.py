import asyncio
import datetime
import os
import httpx

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/top-headlines"
NEWSAPI_CATEGORIES = ["technology", "business", "sports", "science", "health", "entertainment"]

async def fetch_category(session, category, api_key, limit):
    """Fetches articles for a single category."""
    params = {
        "country": "us",
        "category": category,
        "pageSize": limit,
        "apiKey": api_key,
    }
    try:
        r = await session.get(NEWSAPI_ENDPOINT, params=params)
        r.raise_for_status()
        data = r.json()
        articles = []
        for item in data.get("articles", []):
            articles.append(
                {
                    "title": item["title"],
                    "url": item["url"],
                    "source": item["source"]["name"],
                    "published_at": item.get("publishedAt", datetime.datetime.utcnow().isoformat()),
                    "summary": item.get("description") or "",
                    "category": category.capitalize()  # Add the category here
                }
            )
        return articles
    except httpx.HTTPStatusError as e:
        print(f"Error fetching NewsAPI category {category}: {e}")
        return []

async def fetch_newsapi_articles(limit: int = 20):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return []

    async with httpx.AsyncClient(timeout=20) as client:
        tasks = [fetch_category(client, category, api_key, limit) for category in NEWSAPI_CATEGORIES]
        results = await asyncio.gather(*tasks)
        
    # Flatten the list of lists into a single list of articles
    all_articles = [article for sublist in results for article in sublist]
    
    # Deduplicate articles based on URL, keeping the first one seen
    unique_articles = []
    seen_urls = set()
    for article in all_articles:
        if article["url"] not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article["url"])
            
    return unique_articles
