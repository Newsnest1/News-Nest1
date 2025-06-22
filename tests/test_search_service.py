import pytest
from unittest.mock import patch, Mock
from app.services import search_service

@pytest.fixture
def mock_client():
    return Mock()

@pytest.mark.asyncio
async def test_search_articles_success():
    mock_results = {
        "hits": [
            {"id": "1", "title": "Test Article", "content": "Test content"},
            {"id": "2", "title": "Another Article", "content": "More content"}
        ]
    }
    with patch("app.services.search_service.client") as mock_client:
        mock_index = Mock()
        mock_client.index.return_value = mock_index
        mock_index.search.return_value = mock_results
        results = await search_service.search_articles("test query")
        assert isinstance(results, list)
        assert len(results) == 2
        assert results[0]["title"] == "Test Article"

@pytest.mark.asyncio
async def test_search_articles_no_results():
    mock_results = {"hits": []}
    with patch("app.services.search_service.client") as mock_client:
        mock_index = Mock()
        mock_client.index.return_value = mock_index
        mock_index.search.return_value = mock_results
        results = await search_service.search_articles("no match")
        assert isinstance(results, list)
        assert len(results) == 0

@pytest.mark.asyncio
async def test_search_articles_error():
    with patch("app.services.search_service.client") as mock_client:
        mock_index = Mock()
        mock_client.index.return_value = mock_index
        mock_index.search.side_effect = Exception("search error")
        with pytest.raises(Exception, match="search error"):
            await search_service.search_articles("error query") 