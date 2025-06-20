import pytest
import asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db, Article

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def override_get_db(test_db):
    def get_test_db():
        yield test_db
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_feed_endpoint_populates_db(mocker, test_db):
    # Mock the external API calls to avoid actual network requests
    mock_newsapi_articles = [
        {"title": "Test Article 1", "url": "http://test.com/1", "source": "Test Source", "published_at": "2023-01-01T12:00:00Z", "content": "Test content 1"}
    ]
    mock_rss_articles = [
        {"title": "Test Article 2", "url": "http://test.com/2", "source": "Test Source", "published_at": "2023-01-01T13:00:00Z", "content": "Test content 2"}
    ]

    mocker.patch('app.services.feed_service.fetch_newsapi_articles', new_callable=AsyncMock, return_value=mock_newsapi_articles)
    mocker.patch('app.services.feed_service.fetch_rss_articles', new_callable=AsyncMock, return_value=mock_rss_articles)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/v1/feed")

    assert response.status_code == 200
    
    articles_in_db = test_db.query(Article).order_by(Article.published_at.desc()).all()
    assert len(articles_in_db) == 2
    assert articles_in_db[0].title == "Test Article 2"
    assert articles_in_db[1].title == "Test Article 1"
