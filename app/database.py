from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./news.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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