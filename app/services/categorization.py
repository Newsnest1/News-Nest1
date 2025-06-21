def categorize_article(article):
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    content_to_check = title + " " + summary

    # More comprehensive keywords
    categories = {
        "Technology": ["ai", "tech", "gadget", "software", "hardware", "apple", "google", "microsoft", "startup", "data", "code", "computer", "robotics", "innovation"],
        "Sports": ["football", "nba", "fifa", "olympics", "nfl", "mlb", "nhl", "soccer", "tennis", "golf", "cricket", "f1", "champions league", "world cup", "athlete"],
        "Business": ["bitcoin", "stock", "crypto", "business", "economy", "market", "finance", "trade", "wall street", "shares", "investment", "earnings", "nasdaq"],
        "Politics": ["biden", "election", "law", "government", "senate", "congress", "parliament", "white house", "democrat", "republican", "vote", "political"],
        "Health": ["health", "medical", "fda", "cdc", "hospital", "disease", "virus", "pandemic", "vaccine", "medicine", "doctor", "healthcare"],
        "Science": ["science", "nasa", "space", "research", "discovery", "planet", "climate", "environment", "study", "physics", "biology", "chemistry"],
        "Entertainment": ["movie", "film", "music", "hollywood", "celebrity", "tv", "netflix", "disney", "grammy", "oscar", "actor", "actress", "song"]
    }

    for category, keywords in categories.items():
        if any(keyword in content_to_check for keyword in keywords):
            return category

    return "General"
