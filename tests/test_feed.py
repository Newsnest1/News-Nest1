import pytest
import asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db, Article
from app import crud
from app.services.feed_service import get_latest_articles

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
async def test_get_latest_articles_populates_db(mocker, db_session):
    """
    Test that the get_latest_articles service function correctly fetches
    articles from adapters and saves them to the database.
    """
    # 1. Mock the external API calls
    mock_newsapi_articles = [
        {"title": "NewsAPI Article", "url": "http://test.com/newsapi", "source": "NewsAPI", "published_at": "2023-01-01T12:00:00Z", "content": "Content"}
    ]
    mock_rss_articles = [
        {"title": "RSS Article", "url": "http://test.com/rss", "source": "RSS Feed", "published_at": "2023-01-01T13:00:00Z", "content": "Content"}
    ]

    mocker.patch('app.services.feed_service.fetch_newsapi_articles', return_value=mock_newsapi_articles)
    mocker.patch('app.services.feed_service.fetch_rss_articles', return_value=mock_rss_articles)
    
    # 2. Mock the categorization service where it is imported and used
    mocker.patch('app.services.feed_service.categorize_article', return_value="Technology")

    # 3. Call the service function directly
    new_articles = await get_latest_articles(db=db_session, limit=10)

    # 4. Assert the results
    assert len(new_articles) == 2
    
    # Verify articles were actually written to the test DB
    articles_in_db = db_session.query(Article).all()
    assert len(articles_in_db) == 2
    assert articles_in_db[0].title == "RSS Article" # Sorted by date
    assert articles_in_db[1].title == "NewsAPI Article"
    assert articles_in_db[0].category == "Technology"
