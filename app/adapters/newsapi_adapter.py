import asyncio
import datetime
import os
import httpx

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/top-headlines"
NEWSAPI_CATEGORIES = ["technology", "business", "sports", "science", "health", "entertainment", "general"]

# Major news sources to fetch from
NEWSAPI_SOURCES = [
    "the-guardian-uk",      # The Guardian
    "reuters",              # Reuters
    "deutsche-welle",       # Deutsche Welle (DW)
    "bbc-news",             # BBC News
    "cnn",                  # CNN
    "the-new-york-times",   # The New York Times
    "the-washington-post",  # The Washington Post
    "al-jazeera-english",   # Al Jazeera English
    "npr",                  # NPR
    "politico",             # Politico
    "techcrunch",           # TechCrunch
    "ars-technica",         # Ars Technica
    "wired",                # Wired
    "the-verge",            # The Verge
    "engadget",             # Engadget
    "venturebeat",          # VentureBeat
    "bloomberg",            # Bloomberg
    "financial-times",      # Financial Times
    "the-economist",        # The Economist
    "nature",               # Nature
    "science",              # Science Magazine
]

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
                    "category": category.capitalize(),  # Use NewsAPI's built-in category
                    "source_type": "newsapi",  # Mark as NewsAPI source for tracking
                    "image_url": item.get("urlToImage")  # Extract image from NewsAPI
                }
            )
        return articles
    except httpx.HTTPStatusError as e:
        print(f"Error fetching NewsAPI category {category}: {e}")
        return []

async def fetch_source(session, source, api_key, limit):
    """Fetches articles from a specific source."""
    params = {
        "sources": source,
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
                    "category": "General",  # Default category for source-based articles
                    "source_type": "newsapi",  # Mark as NewsAPI source for tracking
                    "image_url": item.get("urlToImage")  # Extract image from NewsAPI
                }
            )
        return articles
    except httpx.HTTPStatusError as e:
        print(f"Error fetching NewsAPI source {source}: {e}")
        return []

async def fetch_newsapi_articles(limit: int = 20):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return []

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch from categories
        category_tasks = [fetch_category(client, category, api_key, limit) for category in NEWSAPI_CATEGORIES]
        
        # Fetch from specific sources
        source_tasks = [fetch_source(client, source, api_key, limit) for source in NEWSAPI_SOURCES]
        
        # Combine all tasks
        all_tasks = category_tasks + source_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
    # Flatten the list of lists into a single list of articles
    all_articles = []
    for result in results:
        if isinstance(result, list):  # Skip exceptions
            all_articles.extend(result)
    
    # Deduplicate articles based on URL, keeping the first one seen
    unique_articles = []
    seen_urls = set()
    for article in all_articles:
        if article["url"] not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(article["url"])
            
    return unique_articles
