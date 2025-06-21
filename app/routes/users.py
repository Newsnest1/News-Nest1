from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import crud, schemas, database
from ..services import auth_service
from datetime import timedelta

router = APIRouter(tags=["users"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/users/register", response_model=schemas.User, tags=["users"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token, tags=["authentication"])
async def login_for_access_token(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User, tags=["users"])
async def read_users_me(current_user: schemas.User = Depends(auth_service.get_current_active_user)):
    return current_user

@router.post("/users/me/saved", tags=["saved-articles"])
async def add_saved_article(
    article_url: str = Query(..., description="URL of the article to save"),
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    result = crud.add_saved_article(db=db, user_id=current_user.id, article_url=article_url)
    return {"message": "Article saved", "article_url": article_url}

@router.delete("/users/me/saved", tags=["saved-articles"])
async def remove_saved_article(
    article_url: str = Query(..., description="URL of the article to unsave"),
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    result = crud.remove_saved_article(db=db, user_id=current_user.id, article_url=article_url)
    if result:
        return {"message": "Article removed from saved", "article_url": article_url}
    else:
        raise HTTPException(status_code=404, detail="Article not in saved list")

@router.get("/users/me/saved", tags=["saved-articles"])
async def get_saved_articles(
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db),
    skip: int = 0,
    limit: int = 100
):
    saved_articles = crud.get_user_saved_articles(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return saved_articles

# Topic follow endpoints
@router.post("/users/me/follow/topic", tags=["follows"])
async def follow_topic(
    topic: str = Query(..., description="Topic to follow"),
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    crud.follow_topic(db, current_user.id, topic)
    return {"message": f"Now following topic: {topic}"}

@router.delete("/users/me/follow/topic", tags=["follows"])
async def unfollow_topic(
    topic: str = Query(..., description="Topic to unfollow"),
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    result = crud.unfollow_topic(db, current_user.id, topic)
    if result:
        return {"message": f"Unfollowed topic: {topic}"}
    else:
        raise HTTPException(status_code=404, detail="Topic not followed")

@router.get("/users/me/followed/topics", tags=["follows"])
async def get_followed_topics(
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    topics = crud.get_followed_topics(db, current_user.id)
    return {"topics": topics}

# Outlet follow endpoints
@router.post("/users/me/follow/outlet", tags=["follows"])
async def follow_outlet(
    outlet: str = Query(..., description="Outlet to follow"),
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    crud.follow_outlet(db, current_user.id, outlet)
    return {"message": f"Now following outlet: {outlet}"}

@router.delete("/users/me/follow/outlet", tags=["follows"])
async def unfollow_outlet(
    outlet: str = Query(..., description="Outlet to unfollow"),
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    result = crud.unfollow_outlet(db, current_user.id, outlet)
    if result:
        return {"message": f"Unfollowed outlet: {outlet}"}
    else:
        raise HTTPException(status_code=404, detail="Outlet not followed")

@router.get("/users/me/followed/outlets", tags=["follows"])
async def get_followed_outlets(
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    outlets = crud.get_followed_outlets(db, current_user.id)
    return {"outlets": outlets}

# Notification preferences
@router.put("/users/me/notifications", response_model=schemas.User)
async def update_notification_preferences(
    preferences: schemas.NotificationPreferences,
    current_user: schemas.User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(database.get_db)
):
    updated_user = crud.update_notification_preferences(
        db=db,
        user_id=current_user.id,
        notifications_enabled=preferences.notifications_enabled,
        notify_topics=preferences.notify_topics,
        notify_outlets=preferences.notify_outlets
    )
    if updated_user:
        return updated_user
    else:
        raise HTTPException(status_code=404, detail="User not found") 