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

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token for authentication")
    token_type: str = Field(..., description="Type of token (usually 'bearer')")

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="Username from token payload") 