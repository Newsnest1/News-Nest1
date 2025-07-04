from app.services.categorization import categorize_article

def test_categorize_technology():
    assert categorize_article("Apple launches new AI chip", "") == "Technology"
    assert categorize_article("Google unveils new software", "") == "Technology"
    assert categorize_article("Crypto market update", "") == "Technology"

def test_categorize_sports():
    assert categorize_article("NBA finals results", "") == "Sports"
    assert categorize_article("Olympics soccer game", "") == "Sports"

def test_categorize_business():
    assert categorize_article("Stock market hits record", "") == "Business"
    assert categorize_article("Finance news: economy grows", "") == "Business"

def test_categorize_politics():
    assert categorize_article("Government election results", "") == "Politics"
    assert categorize_article("President addresses congress", "") == "Politics"

def test_categorize_weather():
    assert categorize_article("Storm warning issued", "") == "Weather"
    assert categorize_article("Snow and rain expected", "") == "Weather"

def test_categorize_science():
    assert categorize_article("NASA discovers new planet", "") == "Science"
    assert categorize_article("Research study shows breakthrough", "") == "Science"

def test_categorize_health():
    assert categorize_article("New medical treatment approved", "") == "Health"
    assert categorize_article("Hospital reports patient recovery", "") == "Health"

def test_categorize_entertainment():
    assert categorize_article("New movie breaks box office records", "") == "Entertainment"
    assert categorize_article("Actor wins award for performance", "") == "Entertainment"

def test_categorize_general():
    assert categorize_article("Random headline with no keywords", "") == "General"
    assert categorize_article("A day in the life", "") == "General" 