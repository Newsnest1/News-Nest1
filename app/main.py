from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from app.services.categorization import recategorize_existing_articles
import app.crud as crud
from app.schemas import ArticleResponse

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Aggregator API")

# Mount static files
app.mount("/static", StaticFiles(directory=".", html=True), name="static")
app.mount("/styles", StaticFiles(directory="styles"), name="styles")
app.mount("/js", StaticFiles(directory="js"), name="js")

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
app.include_router(ws_router, prefix="/v1")

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/index.html")
async def read_index_html():
    return FileResponse("index.html")

@app.get("/favicon.ico")
async def get_favicon():
    return {"message": "No favicon"}

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

@app.post("/api/admin/recategorize")
async def recategorize_articles():
    """Recategorize all existing articles with improved categorization logic."""
    try:
        updated_count = await recategorize_existing_articles()
        return {"message": f"Successfully recategorized {updated_count} articles", "updated_count": updated_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recategorize articles: {str(e)}")

@app.get("/api/articles")
async def get_articles(page: int = 1, limit: int = 20, category: str = None):
    """Get articles with pagination and optional category filtering."""
    db = SessionLocal()
    try:
        skip = (page - 1) * limit
        if category:
            articles = crud.get_articles_by_category(db, category, skip, limit)
        else:
            articles = crud.get_articles(db, skip, limit)
        return {"articles": [ArticleResponse.from_orm(a).dict() for a in articles]}
    finally:
        db.close()

@app.get("/v1/articles")
async def get_articles_v1(page: int = 1, limit: int = 20, category: str = None):
    """Get articles with pagination and optional category filtering (v1 endpoint)."""
    db = SessionLocal()
    try:
        skip = (page - 1) * limit
        if category:
            articles = crud.get_articles_by_category(db, category, skip, limit)
        else:
            articles = crud.get_articles(db, skip, limit)
        return {"articles": [ArticleResponse.from_orm(a).dict() for a in articles]}
    finally:
        db.close()
