import pytest
from unittest.mock import patch, Mock
from app.services import index_populator

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def mock_articles():
    return [
        Mock(url="http://a.com", title="Test Article 1", content="Content 1", category="Tech", source="S1", published_at=None),
        Mock(url="http://b.com", title="Test Article 2", content="Content 2", category="Business", source="S2", published_at=None),
    ]

def test_populate_meilisearch_index_success(mock_db, mock_articles):
    with patch("app.services.index_populator.get_all_articles", return_value=mock_articles):
        with patch("app.services.index_populator.client") as mock_client:
            mock_index = Mock()
            mock_client.index.return_value = mock_index
            mock_index.delete_all_documents.return_value = None
            mock_index.add_documents.return_value = {"updateId": 1}
            # Should not raise
            import asyncio
            asyncio.run(index_populator.populate_meilisearch_index())
            mock_client.index.assert_called_once_with("articles")
            mock_index.delete_all_documents.assert_called_once()
            mock_index.add_documents.assert_called_once()

def test_populate_meilisearch_index_no_articles(mock_db):
    with patch("app.services.index_populator.get_all_articles", return_value=[]):
        with patch("app.services.index_populator.client") as mock_client:
            mock_index = Mock()
            mock_client.index.return_value = mock_index
            # Should not raise
            import asyncio
            asyncio.run(index_populator.populate_meilisearch_index())
            # Should not call delete_all_documents or add_documents
            mock_index.delete_all_documents.assert_not_called()
            mock_index.add_documents.assert_not_called()

def test_populate_meilisearch_index_add_documents_error(mock_db, mock_articles):
    with patch("app.services.index_populator.get_all_articles", return_value=mock_articles):
        with patch("app.services.index_populator.client") as mock_client:
            mock_index = Mock()
            mock_client.index.return_value = mock_index
            mock_index.delete_all_documents.return_value = None
            mock_index.add_documents.side_effect = Exception("add error")
            import asyncio
            with pytest.raises(Exception, match="add error"):
                asyncio.run(index_populator.populate_meilisearch_index())

def test_populate_meilisearch_index_index_error(mock_db, mock_articles):
    with patch("app.services.index_populator.get_all_articles", return_value=mock_articles):
        with patch("app.services.index_populator.client") as mock_client:
            mock_client.index.side_effect = Exception("index error")
            import asyncio
            with pytest.raises(Exception, match="index error"):
                asyncio.run(index_populator.populate_meilisearch_index())

def test_sanitize_id():
    url = "http://example.com/article"
    result = index_populator.sanitize_id(url)
    assert isinstance(result, str)
    assert len(result) == 32  # md5 hex 