from app.database import get_db
from app.crud import update_article_category

async def recategorize_existing_articles():
    """
    Recategorizes all existing articles in the database using the improved categorization system.
    This should be run after updating the categorization logic.
    """
    db = get_db()
    
    # Get all articles that need recategorization
    articles = db.execute(
        "SELECT id, title, content FROM articles WHERE category = 'General' OR category IS NULL"
    ).fetchall()
    
    updated_count = 0
    for article in articles:
        new_category = categorize_article(article.title, article.content or "")
        
        # Only update if the category changed
        if new_category != "General":
            update_article_category(db, article.id, new_category)
            updated_count += 1
    
    print(f"Recategorized {updated_count} articles")
    return updated_count

def categorize_article(title: str, content: str = "") -> str:
    """
    Categorizes an article based on keywords in its title and content.
    Uses improved matching to avoid false positives and better political detection.
    """
    text_to_analyze = (title + " " + content).lower()
    
    # Create a more comprehensive and accurate categorization system
    categories = {
        "Politics": [
            # Government and elections
            "president", "congress", "senate", "house", "representative", "senator", "governor", "mayor",
            "election", "campaign", "vote", "voting", "ballot", "primary", "caucus", "democrat", "republican",
            "liberal", "conservative", "progressive", "moderate", "independent", "party", "political",
            
            # Government actions
            "legislation", "bill", "law", "act", "policy", "executive order", "veto", "sign", "approve",
            "pass", "reject", "amendment", "constitution", "supreme court", "judge", "justice", "nomination",
            "confirmation", "impeachment", "investigation", "hearing", "committee", "subpoena", "testimony",
            
            # International relations
            "diplomatic", "diplomacy", "foreign policy", "embassy", "ambassador", "treaty", "agreement",
            "sanction", "tariff", "trade war", "nato", "united nations", "un", "alliance", "partnership",
            "summit", "meeting", "negotiation", "peace", "war", "conflict", "crisis", "tension",
            
            # Political events
            "protest", "demonstration", "rally", "march", "activist", "lobby", "lobbyist", "corruption",
            "scandal", "ethics", "ethics committee", "oversight", "whistleblower", "leak", "classified",
            "national security", "defense", "military", "veteran", "veterans affairs", "homeland security",
            
            # Political figures and institutions
            "white house", "capitol", "pentagon", "state department", "treasury", "justice department",
            "fbi", "cia", "nsa", "intelligence", "secretary", "minister", "prime minister", "chancellor",
            "parliament", "legislature", "assembly", "council", "commission", "agency", "department",
            
            # Political issues
            "immigration", "border", "refugee", "asylum", "citizenship", "voter", "voting rights",
            "gerrymandering", "redistricting", "electoral", "electoral college", "popular vote",
            "campaign finance", "super pac", "dark money", "lobbying", "special interest", "pork barrel",
            "earmark", "appropriation", "budget", "deficit", "debt ceiling", "government shutdown",
            "federal", "state", "local", "municipal", "county", "district", "ward", "precinct"
        ],
        
        "Technology": [
            # Tech companies and products
            "apple", "google", "microsoft", "amazon", "facebook", "meta", "twitter", "x", "tesla", "spacex",
            "netflix", "spotify", "uber", "lyft", "airbnb", "zoom", "slack", "discord", "tiktok", "instagram",
            "youtube", "linkedin", "snapchat", "whatsapp", "telegram", "signal", "github", "stack overflow",
            
            # Tech concepts
            "artificial intelligence", "ai", "machine learning", "ml", "deep learning", "neural network",
            "algorithm", "data", "big data", "analytics", "cloud", "cloud computing", "saas", "paas", "iaas",
            "blockchain", "cryptocurrency", "bitcoin", "ethereum", "nft", "web3", "metaverse", "vr", "ar",
            "virtual reality", "augmented reality", "mixed reality", "quantum computing", "5g", "6g",
            
            # Software and development
            "software", "app", "application", "programming", "coding", "developer", "programmer", "coder",
            "code", "bug", "debug", "deploy", "release", "version", "update", "patch", "security", "hack",
            "cybersecurity", "malware", "virus", "phishing", "encryption", "password", "authentication",
            
            # Hardware and devices
            "smartphone", "iphone", "android", "laptop", "computer", "pc", "mac", "tablet", "ipad",
            "smartwatch", "wearable", "headphone", "earbud", "speaker", "camera", "drone", "robot",
            "automation", "iot", "internet of things", "smart home", "smart city", "autonomous", "self-driving"
        ],
        
        "Business": [
            # Financial terms
            "stock", "market", "trading", "investor", "investment", "portfolio", "fund", "mutual fund",
            "etf", "bond", "dividend", "earnings", "revenue", "profit", "loss", "quarterly", "annual",
            "report", "filing", "sec", "securities", "exchange", "nyse", "nasdaq", "dow", "s&p",
            
            # Business operations
            "company", "corporation", "inc", "llc", "startup", "venture", "capital", "funding", "ipo",
            "merger", "acquisition", "buyout", "takeover", "bankruptcy", "restructuring", "layoff",
            "hiring", "recruitment", "hr", "human resources", "ceo", "executive", "board", "director",
            
            # Economic terms
            "economy", "economic", "gdp", "inflation", "deflation", "recession", "depression", "growth",
            "decline", "unemployment", "employment", "job", "career", "salary", "wage", "minimum wage",
            "union", "strike", "labor", "workforce", "productivity", "efficiency", "innovation",
            
            # Banking and finance
            "bank", "banking", "credit", "debit", "loan", "mortgage", "interest", "rate", "federal reserve",
            "fed", "central bank", "monetary", "fiscal", "tax", "taxation", "irs", "audit", "accounting",
            "bookkeeping", "balance sheet", "income statement", "cash flow", "budget", "forecast"
        ],
        
        "Sports": [
            # Major sports
            "nba", "nfl", "mlb", "nhl", "soccer", "football", "basketball", "baseball", "hockey",
            "tennis", "golf", "boxing", "mma", "ufc", "wrestling", "olympics", "olympic", "paralympic",
            "world cup", "championship", "tournament", "playoff", "final", "semifinal", "quarterfinal",
            
            # Sports terms
            "game", "match", "competition", "race", "athlete", "player", "coach", "team", "league",
            "conference", "division", "season", "draft", "trade", "free agent", "contract", "salary cap",
            "score", "win", "lose", "victory", "defeat", "tie", "overtime", "penalty", "foul", "referee",
            
            # Sports events
            "super bowl", "world series", "stanley cup", "nba finals", "march madness", "final four",
            "bowl game", "all-star", "pro bowl", "olympic games", "paralympic games", "world championship",
            "national championship", "conference championship", "division championship"
        ],
        
        "Health": [
            # Medical terms
            "hospital", "clinic", "doctor", "physician", "nurse", "patient", "treatment", "therapy",
            "diagnosis", "symptom", "disease", "illness", "infection", "virus", "bacteria", "pathogen",
            "vaccine", "vaccination", "immunization", "antibiotic", "medication", "drug", "prescription",
            "pharmacy", "pharmacist", "clinical trial", "research", "study", "medical", "medicine",
            
            # Health conditions
            "cancer", "diabetes", "heart", "cardiac", "stroke", "alzheimer", "dementia", "autism",
            "depression", "anxiety", "mental health", "psychology", "psychiatry", "therapy", "counseling",
            "addiction", "substance abuse", "recovery", "rehabilitation", "physical therapy", "occupational therapy",
            
            # Healthcare system
            "healthcare", "health insurance", "medicare", "medicaid", "obamacare", "aca", "affordable care act",
            "premium", "deductible", "copay", "coverage", "provider", "network", "hmo", "ppo", "deductible",
            "emergency", "urgent care", "primary care", "specialist", "surgeon", "surgery", "operation"
        ],
        
        "Science": [
            # Scientific fields
            "physics", "chemistry", "biology", "genetics", "dna", "rna", "protein", "molecule", "atom",
            "particle", "quantum", "theoretical", "experimental", "laboratory", "lab", "research", "study",
            "experiment", "hypothesis", "theory", "evidence", "data", "analysis", "statistics", "peer review",
            
            # Space and astronomy
            "nasa", "space", "astronomy", "astronaut", "satellite", "rocket", "launch", "orbit", "planet",
            "star", "galaxy", "universe", "cosmos", "solar system", "mars", "moon", "earth", "sun",
            "telescope", "observatory", "mission", "rover", "probe", "spacecraft", "space station",
            
            # Environmental science
            "climate", "climate change", "global warming", "environment", "environmental", "ecosystem",
            "species", "biodiversity", "conservation", "pollution", "emission", "carbon", "greenhouse",
            "renewable", "solar", "wind", "nuclear", "fossil fuel", "oil", "gas", "coal", "sustainability"
        ],
        
        "Entertainment": [
            # Movies and TV
            "movie", "film", "cinema", "theater", "hollywood", "netflix", "hulu", "disney", "amazon prime",
            "streaming", "television", "tv", "show", "series", "episode", "season", "premiere", "finale",
            "actor", "actress", "director", "producer", "screenwriter", "script", "screenplay", "casting",
            
            # Music
            "music", "song", "album", "artist", "singer", "band", "concert", "tour", "performance",
            "grammy", "billboard", "chart", "hit", "single", "release", "debut", "collaboration", "duet",
            "playlist", "streaming", "spotify", "apple music", "pandora", "radio", "dj", "producer",
            
            # Awards and events
            "oscar", "academy award", "golden globe", "emmy", "tony", "grammy", "mtv", "billboard music award",
            "red carpet", "premiere", "award show", "ceremony", "gala", "festival", "cannes", "sundance",
            "celebrity", "star", "fame", "gossip", "tabloid", "paparazzi", "fan", "fandom", "convention"
        ],
        
        "Weather": [
            # Weather conditions
            "weather", "forecast", "temperature", "humidity", "pressure", "wind", "rain", "snow", "sleet",
            "hail", "storm", "thunderstorm", "lightning", "thunder", "cloud", "sunny", "cloudy", "rainy",
            "snowy", "foggy", "misty", "drizzle", "shower", "downpour", "blizzard", "whiteout",
            
            # Severe weather
            "hurricane", "typhoon", "cyclone", "tornado", "twister", "flood", "flash flood", "drought",
            "heat wave", "cold snap", "freeze", "frost", "ice", "sleet", "hail", "wildfire", "bushfire",
            "tsunami", "earthquake", "volcano", "eruption", "landslide", "avalanche", "mudslide",
            
            # Climate and environment
            "climate", "climate change", "global warming", "greenhouse effect", "carbon dioxide", "co2",
            "emission", "pollution", "air quality", "uv index", "pollen", "allergy", "seasonal", "spring",
            "summer", "fall", "autumn", "winter", "season", "seasonal", "equinox", "solstice"
        ]
    }


    category_scores = {}
    
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
        
            if f" {keyword} " in f" {text_to_analyze} ":
                score += 2 
            elif keyword in text_to_analyze:
                score += 1  
        category_scores[category] = score
    
  
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        if category_scores[best_category] > 0:
            return best_category
    
    return "General"
