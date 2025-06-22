def categorize_article(title: str, content: str = "") -> str:
    """
    Categorizes an article based on keywords in its title and content.
    Matches whole words only to avoid false positives.
    """
    text_to_analyze = (title + " " + content).lower()
    words = text_to_analyze.split()

    # Keywords for each category (whole words only)
    categories = {
        "Technology": ["tech", "apple", "google", "microsoft", "software", "ai", "crypto", "computer", "digital"],
        "Sports": ["sports", "nba", "nfl", "soccer", "olympics", "game", "football", "basketball"],
        "Business": ["business", "finance", "money", "stock", "market", "economy", "trade", "investment"],
        "Politics": ["politics", "government", "election", "president", "congress", "senate", "vote"],
        "Weather": ["weather", "storm", "rain", "sun", "snow", "temperature", "climate", "forecast"]
    }

    for category, keywords in categories.items():
        if any(keyword in words for keyword in keywords):
            return category

    return "General"
