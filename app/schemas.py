from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the account", example="john_doe")
    email: str = Field(..., description="Valid email address", example="john@example.com")

class UserCreate(UserBase):
    password: str = Field(..., description="Password for the account (min 6 characters)", example="securepass123")

class User(UserBase):
    id: int = Field(..., description="Unique user ID")
    is_active: bool = Field(..., description="Whether the user account is active")
    notifications_enabled: bool = Field(..., description="Whether notifications are enabled")
    notify_topics: bool = Field(..., description="Whether to receive notifications for followed topics")
    notify_outlets: bool = Field(..., description="Whether to receive notifications for followed outlets")

    class Config:
        orm_mode = True

class NotificationPreferences(BaseModel):
    notifications_enabled: bool = Field(..., description="Enable/disable all notifications")
    notify_topics: bool = Field(..., description="Receive notifications for followed topics")
    notify_outlets: bool = Field(..., description="Receive notifications for followed outlets")

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token for authentication")
    token_type: str = Field(..., description="Type of token (usually 'bearer')")

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username from token payload") 