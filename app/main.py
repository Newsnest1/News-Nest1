from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from app.routes import feed, search

app = FastAPI(title="News Aggregator API")

app.include_router(feed, prefix="/v1")
app.include_router(search, prefix="/v1")
