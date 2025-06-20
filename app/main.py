from dotenv import load_dotenv
from fastapi import FastAPI
from app.routes.feed import router as feed_router
from app.routes.search import router as search_router
from app.services.index_populator import populate_meilisearch_index
from app.database import create_db_and_tables, SessionLocal
from app.services.feed_service import get_latest_articles

load_dotenv()

app = FastAPI(title="News Aggregator API")

app.include_router(feed_router, prefix="/v1")
app.include_router(search_router, prefix="/v1")

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    # Create a new DB session
    db = SessionLocal()
    try:
        # Fetch initial articles and populate DB
        await get_latest_articles(db=db, limit=50)
    finally:
        db.close()
    
    # Populate MeiliSearch index with articles from the DB
    await populate_meilisearch_index()
