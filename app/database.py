import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
    published_at = Column(DateTime, nullable=True)
    category = Column(String, nullable=True)
    comment = Column(String, nullable=True)

    def __repr__(self):
        return f"<Article(title='{self.title}', category='{self.category}')>"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class UserSavedArticle(Base):
    __tablename__ = 'user_saved_articles'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    article_url = Column(String, ForeignKey('articles.url'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserTopic(Base):
    __tablename__ = 'user_topics'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserOutlet(Base):
    __tablename__ = 'user_outlets'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    outlet = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 