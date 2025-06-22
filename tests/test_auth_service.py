import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from jose import JWTError, jwt
from fastapi import HTTPException

from app.services.auth_service import (
    create_access_token,
    get_current_user,
    get_current_active_user,
    get_current_optional_user,
    verify_password
)
from app import crud, schemas
from app.database import User

# Test data
TEST_USER_DATA = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

def test_verify_password():
    """Test password verification with bcrypt."""
    from app import security
    
    # Generate a proper hash for our test password
    test_password = "testpassword123"
    hashed = security.pwd_context.hash(test_password)
    
    # Test correct password
    assert verify_password(test_password, hashed)
    
    # Test incorrect password
    assert not verify_password("wrongpassword", hashed)

def test_verify_password_manual_authentication(db_session):
    """Test manual authentication flow using the actual functions."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Test authentication using the same logic as login_for_access_token
    db_user = crud.get_user_by_username(db_session, username=TEST_USER_DATA["username"])
    assert db_user is not None
    
    # Test correct password
    assert verify_password(TEST_USER_DATA["password"], db_user.hashed_password)
    
    # Test wrong password
    assert not verify_password("wrongpassword", db_user.hashed_password)

def test_create_access_token():
    """Test JWT access token creation."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    
    token = create_access_token(data=data, expires_delta=expires_delta)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Verify the token can be decoded (we'll need to import the security module for the key)
    from app import security
    decoded = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert decoded["sub"] == "testuser"

def test_create_access_token_without_expires():
    """Test JWT access token creation without expiration delta."""
    data = {"sub": "testuser"}
    
    token = create_access_token(data=data)  # No expires_delta
    
    assert token is not None
    assert isinstance(token, str)
    
    # Token should still be valid
    from app import security
    decoded = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert decoded["sub"] == "testuser"

@pytest.mark.asyncio
async def get_current_user_success(db_session):
    """Test getting current user with valid token."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Create a valid token
    token = create_access_token(data={"sub": user.username})
    
    current_user = await get_current_user(token=token, db=db_session)
    
    assert current_user is not None
    assert current_user.username == TEST_USER_DATA["username"]

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    """Test getting current user with invalid token."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="invalid_token", db=db_session)
    
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(db_session):
    """Test getting current user with token for non-existent user."""
    # Create token for non-existent user
    token = create_access_token(data={"sub": "nonexistent"})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=db_session)
    
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_active_user_active(db_session):
    """Test getting current active user when user is active."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Create a valid token
    token = create_access_token(data={"sub": user.username})
    
    current_user = await get_current_user(token=token, db=db_session)
    active_user = await get_current_active_user(current_user=current_user)
    
    assert active_user is not None
    assert active_user.username == TEST_USER_DATA["username"]

@pytest.mark.asyncio
async def test_get_current_active_user_inactive(db_session):
    """Test getting current active user when user is inactive."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Set user as inactive
    user.is_active = False
    db_session.commit()
    
    # Create a valid token
    token = create_access_token(data={"sub": user.username})
    
    current_user = await get_current_user(token=token, db=db_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(current_user=current_user)
    
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_get_current_optional_user_with_token(db_session):
    """Test optional user authentication with valid token."""
    # Create a test user
    user_in = schemas.UserCreate(**TEST_USER_DATA)
    user = crud.create_user(db=db_session, user=user_in)
    
    # Create a valid token
    token = create_access_token(data={"sub": user.username})
    
    # Mock the request object
    mock_request = Mock()
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    
    current_user = await get_current_optional_user(request=mock_request, db=db_session)
    
    assert current_user is not None
    assert current_user.username == TEST_USER_DATA["username"]

@pytest.mark.asyncio
async def test_get_current_optional_user_without_token(db_session):
    """Test optional user authentication without token."""
    mock_request = Mock()
    mock_request.headers = {}
    
    current_user = await get_current_optional_user(request=mock_request, db=db_session)
    
    assert current_user is None

@pytest.mark.asyncio
async def test_get_current_optional_user_invalid_token(db_session):
    """Test optional user authentication with invalid token."""
    mock_request = Mock()
    mock_request.headers = {"Authorization": "Bearer invalid_token"}
    
    current_user = await get_current_optional_user(request=mock_request, db=db_session)
    
    assert current_user is None

@pytest.mark.asyncio
async def test_get_current_optional_user_malformed_header(db_session):
    """Test optional user authentication with malformed Authorization header."""
    mock_request = Mock()
    mock_request.headers = {"Authorization": "InvalidFormat"}
    
    current_user = await get_current_optional_user(request=mock_request, db=db_session)
    
    assert current_user is None

def test_token_expiration():
    """Test that tokens expire correctly."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(seconds=1)  # 1 second expiration
    
    token = create_access_token(data=data, expires_delta=expires_delta)
    
    # Wait for token to expire
    import time
    time.sleep(1.5)  # Wait longer than the expiration
    
    # Token should be expired
    from app import security
    with pytest.raises(JWTError):
        jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM]) 