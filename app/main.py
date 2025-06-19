from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.routes.feed import router as feed_router
from app.routes.search import router as search_router

app = FastAPI(title="News Aggregator API")

app.include_router(feed_router, prefix="/v1")
app.include_router(search_router, prefix="/v1")
