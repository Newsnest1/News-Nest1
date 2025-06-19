import meilisearch
from typing import List

from fastapi.concurrency import run_in_threadpool

# Initialize the MeiliSearch client
client = meilisearch.Client("http://127.0.0.1:7701", "masterKey")
INDEX_NAME = "articles"


async def search_articles(q: str, limit: int = 20) -> List[dict]:
    """Performs full-text search on articles using MeiliSearch."""
    index = client.index(INDEX_NAME)

    # Run blocking search in a threadpool to avoid blocking the event loop
    search_result = await run_in_threadpool(index.search, q, {"limit": limit})

    return search_result.get("hits", [])
