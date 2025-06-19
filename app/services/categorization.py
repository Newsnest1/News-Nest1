def categorize_article(article):
    title = article.get("title", "").lower()

    if any(word in title for word in ["football", "nba", "fifa"]):
        return "Sports"
    elif any(word in title for word in ["bitcoin", "stock", "crypto"]):
        return "Finance"
    elif any(word in title for word in ["ai", "tech", "gadget"]):
        return "Technology"
    elif any(word in title for word in ["biden", "election", "law"]):
        return "Politics"
    else:
        return "Other"
