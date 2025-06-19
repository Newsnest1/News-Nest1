import meilisearch
from typing import List

client = meilisearch.Client(
    "http://search:7700",
    "79218197551724857046"  # ← new key!
)

INDEX_NAME = "articles"

async def search_articles(q: str, limit: int = 20) -> List[dict]:
    index = client.index(INDEX_NAME)
    search_result = index.search(q, {"limit": limit})
    return search_result.get("hits", [])
