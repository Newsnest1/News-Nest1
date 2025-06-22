from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .. import crud, schemas, security
from ..database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")

def verify_password(plain_password, hashed_password):
    return security.pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security.SECRET_KEY, algorithm=security.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[schemas.User]:
    """
    A dependency that returns the current user if a valid token is provided,
    or None if the token is missing or invalid. Does not raise an error.
    """
    token = request.headers.get("Authorization")
    if token:
        # Expected format: "Bearer <token>"
        parts = token.split()
        if len(parts) == 2 and parts[0] == "Bearer":
            token = parts[1]
            try:
                # This reuses the logic from get_current_user but without the auto_error
                payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
                username: str = payload.get("sub")
                if username is None:
                    return None
                user = crud.get_user_by_username(db, username=username)
                return user
            except JWTError:
                # Token is invalid
                return None
    # No token provided
    return None 