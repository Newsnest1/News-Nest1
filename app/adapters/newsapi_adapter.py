import os, datetime
import httpx

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/top-headlines"

async def fetch_newsapi_articles(limit: int = 20):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return []

    params = {
        "country": "us",
        "pageSize": limit,
        "apiKey": api_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(NEWSAPI_ENDPOINT, params=params)
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
            }
        )
    return articles
