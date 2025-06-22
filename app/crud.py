from sqlalchemy.orm import Session
from . import database, schemas, security

def get_user_by_username(db: Session, username: str):
    return db.query(database.User).filter(database.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(database.User).filter(database.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = database.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_saved_article(db: Session, user_id: int, article_url: str):
    # Check if already saved
    existing = db.query(database.UserSavedArticle).filter(
        database.UserSavedArticle.user_id == user_id,
        database.UserSavedArticle.article_url == article_url
    ).first()
    if existing:
        return existing  # Already saved
    
    user_saved_article = database.UserSavedArticle(user_id=user_id, article_url=article_url)
    db.add(user_saved_article)
    db.commit()
    db.refresh(user_saved_article)
    return user_saved_article

def remove_saved_article(db: Session, user_id: int, article_url: str):
    user_saved_article = db.query(database.UserSavedArticle).filter(
        database.UserSavedArticle.user_id == user_id,
        database.UserSavedArticle.article_url == article_url
    ).first()
    if user_saved_article:
        db.delete(user_saved_article)
        db.commit()
        return True
    return False

def is_saved(db: Session, user_id: int, article_url: str):
    return db.query(database.UserSavedArticle).filter(
        database.UserSavedArticle.user_id == user_id,
        database.UserSavedArticle.article_url == article_url
    ).first() is not None

def get_user_saved_articles(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(database.Article).join(database.UserSavedArticle).filter(
        database.UserSavedArticle.user_id == user_id
    ).offset(skip).limit(limit).all()

def follow_topic(db: Session, user_id: int, topic: str):
    existing = db.query(database.UserTopic).filter(
        database.UserTopic.user_id == user_id,
        database.UserTopic.topic == topic
    ).first()
    if existing:
        return existing
    user_topic = database.UserTopic(user_id=user_id, topic=topic)
    db.add(user_topic)
    db.commit()
    db.refresh(user_topic)
    return user_topic

def unfollow_topic(db: Session, user_id: int, topic: str):
    user_topic = db.query(database.UserTopic).filter(
        database.UserTopic.user_id == user_id,
        database.UserTopic.topic == topic
    ).first()
    if user_topic:
        db.delete(user_topic)
        db.commit()
        return True
    return False

def get_followed_topics(db: Session, user_id: int):
    return [ut.topic for ut in db.query(database.UserTopic).filter(database.UserTopic.user_id == user_id).all()]

def follow_outlet(db: Session, user_id: int, outlet: str):
    existing = db.query(database.UserOutlet).filter(
        database.UserOutlet.user_id == user_id,
        database.UserOutlet.outlet == outlet
    ).first()
    if existing:
        return existing
    user_outlet = database.UserOutlet(user_id=user_id, outlet=outlet)
    db.add(user_outlet)
    db.commit()
    db.refresh(user_outlet)
    return user_outlet

def unfollow_outlet(db: Session, user_id: int, outlet: str):
    user_outlet = db.query(database.UserOutlet).filter(
        database.UserOutlet.user_id == user_id,
        database.UserOutlet.outlet == outlet
    ).first()
    if user_outlet:
        db.delete(user_outlet)
        db.commit()
        return True
    return False

def get_followed_outlets(db: Session, user_id: int):
    return [uo.outlet for uo in db.query(database.UserOutlet).filter(database.UserOutlet.user_id == user_id).all()]

def update_notification_preferences(db: Session, user_id: int, notifications_enabled: bool, notify_topics: bool, notify_outlets: bool):
    user = db.query(database.User).filter(database.User.id == user_id).first()
    if user:
        user.notifications_enabled = notifications_enabled
        user.notify_topics = notify_topics
        user.notify_outlets = notify_outlets
        db.commit()
        db.refresh(user)
        return user
    return None

def delete_user(db: Session, user_id: int):
    # Delete saved articles
    db.query(database.UserSavedArticle).filter(database.UserSavedArticle.user_id == user_id).delete()
    # Delete followed topics
    db.query(database.UserTopic).filter(database.UserTopic.user_id == user_id).delete()
    # Delete followed outlets
    db.query(database.UserOutlet).filter(database.UserOutlet.user_id == user_id).delete()
    # Delete the user
    db.query(database.User).filter(database.User.id == user_id).delete()
    db.commit()
    return True

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Article).offset(skip).limit(limit).all()

def get_articles_by_category(db: Session, category: str, skip: int = 0, limit: int = 100):
    return db.query(database.Article).filter(database.Article.category == category).offset(skip).limit(limit).all()

def get_all_articles(db: Session):
    return db.query(database.Article).all()

def get_categories(db: Session):
    """Get all unique categories from the database."""
    categories = db.query(database.Article.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]  # Filter out None values 