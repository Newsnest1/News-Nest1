from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import time
from app.routes.feed import router as feed_router
from app.routes.search import router as search_router
from app.routes.ws import router as ws_router
from app.routes.users import router as users_router
from app.services.index_populator import populate_meilisearch_index
from app.database import create_db_and_tables, SessionLocal
from app.services.feed_service import fetch_and_store_latest_articles
from app.services.websocket_manager import manager
from app.services.notification_service import send_personalized_notifications, send_broadcast_notification

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Aggregator API")

# Set up CORS middleware
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "*"  # Allow all origins for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request {request.method} {request.url.path} processed in {process_time:.4f} seconds")
    return response

app.include_router(feed_router, prefix="/v1")
app.include_router(search_router, prefix="/v1")
app.include_router(users_router, prefix="/v1")
app.include_router(ws_router)

async def periodic_feed_update():
    """Periodically fetches new articles and sends personalized notifications."""
    while True:
        await asyncio.sleep(300)  # Sleep for 5 minutes
        logger.info("Running periodic feed update...")
        db = SessionLocal()
        try:
            new_articles = await fetch_and_store_latest_articles(db=db, limit=100)
            if new_articles:
                logger.info(f"Found {len(new_articles)} new articles. Sending personalized notifications...")
                
                # Convert articles to dict format for notifications
                article_dicts = []
                for article in new_articles:
                    article_dict = {
                        "url": article.url,
                        "title": article.title,
                        "source": article.source,
                        "category": article.category,
                        "published_at": article.published_at.isoformat() if article.published_at else None
                    }
                    article_dicts.append(article_dict)
                
                # Send personalized notifications to users
                await send_personalized_notifications(article_dicts, db)
                
                # Also send broadcast notification for backward compatibility
                await send_broadcast_notification(f"Found {len(new_articles)} new articles", len(new_articles))
                
                # Update MeiliSearch index
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
            await fetch_and_store_latest_articles(db=db, limit=50)
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
