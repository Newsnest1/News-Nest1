from sqlalchemy.orm import Session
from app import crud, schemas

def test_create_user(db_session: Session):
    """
    Test creating a new user.
    """
    user_in = schemas.UserCreate(username="testuser", email="test@example.com", password="password")
    user = crud.create_user(db=db_session, user=user_in)
    
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert hasattr(user, "hashed_password")

def test_get_user_by_username(db_session: Session):
    """
    Test retrieving a user by their username.
    """
    # First, create a user to retrieve
    user_in = schemas.UserCreate(username="testuser2", email="test2@example.com", password="password")
    crud.create_user(db=db_session, user=user_in)
    
    user = crud.get_user_by_username(db=db_session, username="testuser2")
    
    assert user is not None
    assert user.username == "testuser2"

def test_get_user_by_username_not_found(db_session: Session):
    """

    Test retrieving a non-existent user returns None.
    """
    user = crud.get_user_by_username(db=db_session, username="nonexistentuser")
    assert user is None

def test_duplicate_user_creation(db_session: Session):
    """
    Test that creating a user with a duplicate username is handled,
    although the unique constraint is at the DB level.
    This test primarily ensures our function doesn't crash.
    """
    import pytest
    from sqlalchemy.exc import IntegrityError

    user_in1 = schemas.UserCreate(username="duplicateuser", email="dup1@example.com", password="password")
    crud.create_user(db=db_session, user=user_in1)

    user_in2 = schemas.UserCreate(username="duplicateuser", email="dup2@example.com", password="password")
    
    # The database constraint should raise an IntegrityError
    with pytest.raises(IntegrityError):
        crud.create_user(db=db_session, user=user_in2)
        # We need to rollback the session after an integrity error
        db_session.rollback() 