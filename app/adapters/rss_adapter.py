import asyncio
import datetime

import feedparser
import httpx

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]


async def _fetch_rss(url: str) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


async def fetch_rss_articles(limit: int = 20):
    tasks = [_fetch_rss(url) for url in RSS_FEEDS]
    texts = await asyncio.gather(*tasks, return_exceptions=True)

    articles = []
    for text in texts:
        if isinstance(text, Exception):
            continue
        feed = feedparser.parse(text)
        for entry in feed.entries[:limit]:
            published = None
            if getattr(entry, "published_parsed", None):
                published = datetime.datetime(*entry.published_parsed[:6]).isoformat()
            articles.append(
                {
                    "title": entry.title,
                    "url": entry.link,
                    "source": feed.feed.get("title", "RSS"),
                    "published_at": published,
                    "summary": getattr(entry, "summary", ""),
                }
            )
    return articles
