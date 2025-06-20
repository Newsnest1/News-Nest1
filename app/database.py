import os
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database credentials from environment variables
DB_USER = os.environ.get("POSTGRES_USER", "news")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "news")
DB_HOST = os.environ.get("POSTGRES_HOST", "db")  # 'db' is the service name in docker-compose
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_NAME = os.environ.get("POSTGRES_DB", "news")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    url = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    source = Column(String)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime)
    category = Column(String, nullable=True)


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 