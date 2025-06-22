import meilisearch
import os
from typing import List, Optional

client = meilisearch.Client(
    "http://search:7700",
    os.getenv("MEILI_MASTER_KEY", "your_secure_meili_master_key")
)

INDEX_NAME = "articles"

async def search_articles(
    q: str, 
    limit: int = 20, 
    attributes_to_search_on: Optional[List[str]] = None
) -> List[dict]:
    index = client.index(INDEX_NAME)
    
    search_params = {
        "limit": limit
    }
    if attributes_to_search_on:
        search_params["attributesToSearchOn"] = attributes_to_search_on
        
    search_result = index.search(q, search_params)
    return search_result.get("hits", [])
