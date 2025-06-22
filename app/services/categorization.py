def categorize_article(title: str, content: str = "") -> str:
    """
    Categorizes an article based on keywords in its title and content.
    Matches whole words only to avoid false positives.
    """
    text_to_analyze = (title + " " + content).lower()
    words = text_to_analyze.split()

    # Keywords for each category (whole words only)
    categories = {
        "Technology": [
            "tech", "technology", "apple", "google", "microsoft", "software", "ai", "artificial", "intelligence",
            "crypto", "cryptocurrency", "bitcoin", "computer", "digital", "internet", "web", "app", "mobile",
            "smartphone", "laptop", "startup", "innovation", "algorithm", "data", "cyber", "hack", "code",
            "programming", "developer", "silicon", "valley", "facebook", "twitter", "amazon", "tesla", "spacex",
            "robot", "automation", "blockchain", "nft", "metaverse", "vr", "ar", "virtual", "reality"
        ],
        "Sports": [
            "sports", "nba", "nfl", "soccer", "football", "basketball", "olympics", "game", "match", "tournament",
            "championship", "league", "team", "player", "coach", "score", "win", "lose", "victory", "defeat",
            "baseball", "tennis", "golf", "hockey", "rugby", "cricket", "volleyball", "swimming", "athletics",
            "marathon", "race", "competition", "medal", "gold", "silver", "bronze", "olympic", "world cup"
        ],
        "Business": [
            "business", "finance", "financial", "money", "stock", "market", "economy", "economic", "trade",
            "investment", "investor", "bank", "banking", "bankruptcy", "profit", "revenue", "earnings",
            "quarterly", "annual", "report", "merger", "acquisition", "ipo", "startup", "venture", "capital",
            "funding", "fund", "dollar", "euro", "currency", "inflation", "recession", "growth", "decline",
            "ceo", "executive", "board", "shareholder", "dividend", "bond", "loan", "credit", "debt"
        ],
        "Health": [
            "health", "hospital", "patient", "treatment", "therapy", "disease", "illness", "virus", "bacteria", 
            "infection", "vaccine", "vaccination", "drug", "pharmaceutical", "clinical", "trial", "diagnosis", 
            "symptom", "cure", "prevention", "wellness", "fitness", "nutrition", "diet", "exercise", "mental", 
            "psychology", "surgery", "emergency", "ambulance", "pharmacy", "prescription", "antibiotic", "doctor",
            "nurse", "medical", "medicine", "healthcare", "insurance", "medicare", "medicaid", "obamacare"
        ],
        "Science": [
            "science", "scientific", "research", "study", "discovery", "experiment", "laboratory", "lab",
            "nasa", "space", "astronomy", "physics", "chemistry", "biology", "genetics", "dna", "evolution", 
            "climate", "environment", "ecosystem", "species", "animal", "plant", "microscope", "telescope", 
            "satellite", "planet", "galaxy", "universe", "molecule", "atom", "particle", "quantum", "theoretical", 
            "hypothesis", "theory", "evidence", "data"
        ],
        "Entertainment": [
            "entertainment", "movie", "film", "cinema", "actor", "actress", "director", "producer",
            "hollywood", "netflix", "streaming", "television", "tv", "show", "series", "episode",
            "music", "song", "album", "artist", "singer", "band", "concert", "tour", "performance",
            "theater", "play", "broadway", "award", "oscar", "grammy", "celebrity", "star", "fame",
            "gossip", "red carpet", "premiere", "release", "box office", "rating", "review", "critic"
        ],
        "Politics": [
            "politics", "political", "government", "election", "president", "congress", "senate", "vote",
            "voting", "campaign", "candidate", "democrat", "republican", "parliament", "minister", "prime",
            "minister", "parliament", "legislation", "bill", "law", "policy", "diplomatic", "diplomacy",
            "foreign", "affairs", "embassy", "ambassador", "treaty", "agreement", "sanction", "protest",
            "demonstration", "rally", "activist", "lobby", "lobbyist", "corruption", "scandal", "impeachment"
        ],
        "Weather": [
            "weather", "storm", "rain", "sun", "snow", "temperature", "climate", "forecast", "hurricane",
            "tornado", "flood", "drought", "heat", "cold", "warm", "cool", "wind", "windy", "cloudy",
            "sunny", "rainy", "snowy", "fog", "foggy", "thunder", "lightning", "blizzard", "typhoon",
            "cyclone", "tsunami", "earthquake", "volcano", "eruption", "global", "warming", "greenhouse",
            "emission", "carbon", "pollution", "environment", "environmental"
        ]
    }

    for category, keywords in categories.items():
        if any(keyword in words for keyword in keywords):
            return category

    return "General"
