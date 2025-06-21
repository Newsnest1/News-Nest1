from dotenv import load_dotenv
from fastapi import FastAPI
import logging
import asyncio
from app.routes.feed import router as feed_router
from app.routes.search import router as search_router
from app.routes.ws import router as ws_router
from app.services.index_populator import populate_meilisearch_index
from app.database import create_db_and_tables, SessionLocal
from app.services.feed_service import get_latest_articles
from app.services.websocket_manager import manager

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Aggregator API")

app.include_router(feed_router, prefix="/v1")
app.include_router(search_router, prefix="/v1")
app.include_router(ws_router)

async def periodic_feed_update():
    """Periodically fetches new articles and notifies clients."""
    while True:
        await asyncio.sleep(300)  # Sleep for 5 minutes
        logger.info("Running periodic feed update...")
        db = SessionLocal()
        try:
            new_articles = await get_latest_articles(db=db, limit=100)
            if new_articles:
                logger.info(f"Found {len(new_articles)} new articles. Broadcasting...")
                await manager.broadcast(f'{{"type": "new_articles", "count": {len(new_articles)}}}')
                # Also update MeiliSearch index
                await populate_meilisearch_index()
        finally:
            db.close()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application startup...")
    
    try:
        logger.info("Creating database tables...")
        create_db_and_tables()
        
        # Create a new DB session
        db = SessionLocal()
        try:
            # Fetch initial articles and populate DB
            logger.info("Fetching initial articles...")
            await get_latest_articles(db=db, limit=50)
        finally:
            db.close()
        
        # Try to populate MeiliSearch index with retry logic
        logger.info("Attempting to populate MeiliSearch index...")
        for attempt in range(3):
            try:
                await populate_meilisearch_index()
                logger.info("MeiliSearch index populated successfully!")
                break
            except Exception as e:
                logger.warning(f"MeiliSearch index population attempt {attempt + 1} failed: {e}")
                if attempt < 2:  # Don't sleep on the last attempt
                    logger.info("Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.error("Failed to populate MeiliSearch index after 3 attempts. Search functionality may not work.")
        
        # Start the background task
        asyncio.create_task(periodic_feed_update())
        
        logger.info("Startup completed!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
