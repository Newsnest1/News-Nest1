from dotenv import load_dotenv
from fastapi import FastAPI
from app.routes.feed import router as feed_router
from app.routes.search import router as search_router
from app.services.index_populator import populate_meilisearch_index

load_dotenv()

app = FastAPI(title="News Aggregator API")

app.include_router(feed_router, prefix="/v1")
app.include_router(search_router, prefix="/v1")

@app.on_event("startup")
async def startup_event():
    # Populate MeiliSearch index with articles from both sources
    await populate_meilisearch_index()
