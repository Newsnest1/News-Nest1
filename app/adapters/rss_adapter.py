import asyncio
import datetime

import feedparser
import httpx

RSS_FEEDS = [
    # Major News Sources
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theguardian.com/technology/rss",
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/business/rss",
    "https://feeds.reuters.com/reuters/technologyNews",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://rss.dw.com/xml/rss-de-all",
    "https://rss.dw.com/xml/rss-en-all",
    
    # Technology Focused
    "https://feeds.feedburner.com/TechCrunch",
    "https://arstechnica.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://www.engadget.com/rss.xml",
    "https://venturebeat.com/feed/",
    
    # Business & Finance
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.bloomberg.com/technology/news.rss",
    "https://www.ft.com/rss/home",
    "https://www.economist.com/finance-and-economics/rss.xml",
    
    # Science & Research
    "https://www.nature.com/nature.rss",
    "https://www.science.org/rss/news_current.xml",
    
    # Additional Major Sources
    "https://rss.cnn.com/rss/edition.rss",
    "https://feeds.npr.org/1001/rss.xml",
    "https://www.politico.com/rss/politicopicks.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    
    # Regional & Specialized
    "https://www.euronews.com/rss?format=rss&level=theme&name=news",
    "https://www.france24.com/en/rss",
    "https://www.dw.com/rss/xml-rss-en-all",
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
            
            # Extract image from various RSS fields
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('url')
                        break
            elif hasattr(entry, 'links') and entry.links:
                for link in entry.links:
                    if link.get('type', '').startswith('image/'):
                        image_url = link.get('href')
                        break
            
            # Extract summary/description/content
            summary = getattr(entry, "summary", None)
            if not summary:
                summary = getattr(entry, "description", None)
            if not summary and hasattr(entry, "content") and entry.content:
                # content is usually a list of dicts with 'value'
                summary = entry.content[0].get('value') if isinstance(entry.content, list) and 'value' in entry.content[0] else None
            if not summary and hasattr(entry, "content_encoded"):
                summary = getattr(entry, "content_encoded", None)
            if not summary:
                summary = ""
            
            articles.append(
                {
                    "title": entry.title,
                    "url": entry.link,
                    "source": feed.feed.get("title", "RSS"),
                    "published_at": published,
                    "summary": summary,
                    "source_type": "rss",  # Mark as RSS source for tracking
                    "image_url": image_url  # Extract image from RSS
                }
            )
    return articles
