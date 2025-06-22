from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the account", example="john_doe", min_length=3, max_length=30)
    email: EmailStr = Field(..., description="Valid email address", example="john@example.com")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

class UserCreate(UserBase):
    password: str = Field(..., description="Password for the account (min 8 characters)", example="securepass123", min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class User(UserBase):
    id: int = Field(..., description="Unique user ID")
    is_active: bool = Field(..., description="Whether the user account is active")
    notifications_enabled: bool = Field(..., description="Whether notifications are enabled")
    notify_topics: bool = Field(..., description="Whether to receive notifications for followed topics")
    notify_outlets: bool = Field(..., description="Whether to receive notifications for followed outlets")

    class Config:
        from_attributes = True

class NotificationPreferences(BaseModel):
    notifications_enabled: bool = Field(..., description="Enable/disable all notifications")
    notify_topics: bool = Field(..., description="Receive notifications for followed topics")
    notify_outlets: bool = Field(..., description="Receive notifications for followed outlets")

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token for authentication")
    token_type: str = Field(..., description="Type of token (usually 'bearer')")

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username from token payload")

class ArticleBase(BaseModel):
    url: str
    title: str
    source: str
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    is_saved: bool = False

    class Config:
        from_attributes = True

class ArticleResponse(Article):
    pass 