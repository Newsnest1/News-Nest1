import pytest
import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set an environment variable to signal that we are in test mode
os.environ['TESTING'] = 'True'

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for testing to ensure no file-based issues
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Apply the override for the 'get_db' dependency in our app
def override_get_db():
    """
    A dependency override that provides a test database session.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for our test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session(event_loop):
    """
    Fixture to provide a clean database session for each test function.
    Creates tables, yields a session, and then cleans up.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables to ensure a clean state for the next test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    A fixture that provides a test client for our FastAPI app.
    Depends on db_session to ensure the database is ready.
    """
    with TestClient(app) as c:
        yield c 