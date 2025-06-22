import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from datetime import datetime

from app.adapters.newsapi_adapter import fetch_category, fetch_newsapi_articles
from app.adapters.rss_adapter import fetch_rss_articles

@pytest.mark.asyncio
async def test_fetch_category_success():
    """Test successful category fetching from NewsAPI."""
    mock_session = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "articles": [
            {
                "title": "Test Article",
                "url": "http://test.com/article",
                "source": {"name": "Test Source"},
                "publishedAt": "2023-01-01T12:00:00Z",
                "description": "Test description"
            }
        ]
    }
    mock_session.get.return_value = mock_response
    
    articles = await fetch_category(mock_session, "technology", "test-api-key", 10)
    
    assert len(articles) == 1
    assert articles[0]["title"] == "Test Article"
    assert articles[0]["category"] == "Technology"

@pytest.mark.asyncio
async def test_fetch_category_http_error():
    """Test handling of HTTP errors in category fetching."""
    mock_session = AsyncMock()
    mock_session.get.side_effect = httpx.HTTPStatusError("404", request=Mock(), response=Mock())
    
    articles = await fetch_category(mock_session, "technology", "test-api-key", 10)
    
    assert articles == []

@pytest.mark.asyncio
async def test_fetch_category_empty_response():
    """Test handling of empty response from NewsAPI."""
    mock_session = AsyncMock()
    mock_response = Mock()
    mock_response.json.return_value = {"articles": []}
    mock_session.get.return_value = mock_response
    
    articles = await fetch_category(mock_session, "technology", "test-api-key", 10)
    
    assert articles == []

@pytest.mark.asyncio
async def test_fetch_newsapi_articles_success():
    """Test successful fetching of articles from all NewsAPI categories."""
    mock_articles = [
        {"title": "Tech Article", "url": "http://test.com/tech", "source": "Tech Source", "published_at": "2023-01-01T12:00:00Z", "summary": "Tech content", "category": "Technology"},
        {"title": "Business Article", "url": "http://test.com/business", "source": "Business Source", "published_at": "2023-01-01T13:00:00Z", "summary": "Business content", "category": "Business"}
    ]
    
    with patch('app.adapters.newsapi_adapter.fetch_category', new_callable=AsyncMock, return_value=mock_articles):
        with patch('os.getenv', return_value="test-api-key"):
            articles = await fetch_newsapi_articles(limit=10)
    
    assert len(articles) == 2

@pytest.mark.asyncio
async def test_fetch_newsapi_articles_no_api_key():
    """Test handling when no API key is provided."""
    with patch('os.getenv', return_value=None):
        articles = await fetch_newsapi_articles(limit=10)
    
    assert articles == []

@pytest.mark.asyncio
async def test_fetch_newsapi_articles_deduplication():
    """Test that duplicate articles are removed based on URL."""
    mock_articles = [
        {"title": "Same Article", "url": "http://test.com/same", "source": "Source 1", "published_at": "2023-01-01T12:00:00Z", "summary": "Content", "category": "Technology"},
        {"title": "Same Article", "url": "http://test.com/same", "source": "Source 2", "published_at": "2023-01-01T13:00:00Z", "summary": "Content", "category": "Business"}
    ]
    
    with patch('app.adapters.newsapi_adapter.fetch_category', new_callable=AsyncMock, return_value=mock_articles):
        with patch('os.getenv', return_value="test-api-key"):
            articles = await fetch_newsapi_articles(limit=10)
    
    assert len(articles) == 1  # Duplicate URL should be removed

@pytest.mark.asyncio
async def test_fetch_rss_articles_success():
    """Test successful RSS article fetching."""
    mock_feed = Mock()
    mock_feed.entries = [
        Mock(
            title="RSS Article",
            link="http://test.com/rss",
            source=Mock(title="RSS Source"),
            published_parsed=(2023, 1, 1, 12, 0, 0, 0, 0, 0),
            summary="RSS content"
        )
    ]
    mock_feed.feed = {"title": "RSS Source"}
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.text = "mock RSS content"
        mock_get.return_value = mock_response
        
        with patch('feedparser.parse', return_value=mock_feed):
            articles = await fetch_rss_articles(limit=10)
    
    assert len(articles) == 2  # One from each RSS feed
    assert articles[0]["title"] == "RSS Article"
    assert articles[0]["source"] == "RSS Source"

@pytest.mark.asyncio
async def test_fetch_rss_articles_empty_feed():
    """Test handling of empty RSS feed."""
    mock_feed = Mock()
    mock_feed.entries = []
    mock_feed.feed = {"title": "RSS Source"}
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.text = "mock RSS content"
        mock_get.return_value = mock_response
        
        with patch('feedparser.parse', return_value=mock_feed):
            articles = await fetch_rss_articles(limit=10)
    
    assert articles == []

@pytest.mark.asyncio
async def test_fetch_rss_articles_missing_fields():
    """Test handling of RSS entries with missing fields."""
    mock_feed = Mock()
    mock_entry = Mock()
    mock_entry.title = "Article"
    mock_entry.link = "http://test.com/article"
    mock_entry.source = None  # Missing source
    mock_entry.published_parsed = None  # Missing date
    mock_entry.summary = None  # Missing summary
    mock_feed.entries = [mock_entry]
    mock_feed.feed = {"title": "RSS Source"}
    
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.text = "mock RSS content"
        mock_get.return_value = mock_response
        
        with patch('feedparser.parse', return_value=mock_feed):
            articles = await fetch_rss_articles(limit=10)
    
    assert len(articles) == 2  # One from each RSS feed
    assert articles[0]["source"] == "RSS Source"
    assert articles[0]["published_at"] is None  # Should be None when missing

@pytest.mark.asyncio
async def test_fetch_rss_articles_parse_error():
    """Test handling of RSS parsing errors."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.text = "mock RSS content"
        mock_get.return_value = mock_response
        
        with patch('feedparser.parse', side_effect=Exception("Parse error")):
            with pytest.raises(Exception, match="Parse error"):
                await fetch_rss_articles(limit=10) 