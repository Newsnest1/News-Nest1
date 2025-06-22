import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Default to the development database URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/newsdb")

# Allow overriding for tests
if os.getenv("TESTING"):
    SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# For SQLite, we need to add a special connect_args
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

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
    notifications_enabled = Column(Boolean, default=True)
    notify_topics = Column(Boolean, default=True)
    notify_outlets = Column(Boolean, default=True)


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