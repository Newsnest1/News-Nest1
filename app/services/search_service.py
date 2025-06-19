import meilisearch
from typing import List

client = meilisearch.Client(
    "http://127.0.0.1:7701",
    "ryiQdZzczfwDopVd1T_gY-Tftk-bBcpGxjq6KO3qDbU"  # ← new key!
)

INDEX_NAME = "articles"

async def search_articles(q: str, limit: int = 20) -> List[dict]:
    index = client.index(INDEX_NAME)
    search_result = index.search(q, {"limit": limit})
    return search_result.get("hits", [])
