"""Tests for InMemoryCostStorage"""

import pytest
from cost_sharing.storage import InMemoryCostStorage
from cost_sharing.models import User
from cost_sharing.exceptions import (
    DuplicateEmailError,
    UserNotFoundError
)


@pytest.fixture(name='storage')
def create_storage():
    """Fixture for InMemoryCostStorage"""
    return InMemoryCostStorage()


def test_create_user(storage):
    """Test creating a new user"""
    user = storage.create_user(
        email="test@example.com",
        name="Test User"
    )

    assert isinstance(user, User)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_create_user_auto_increment_id(storage):
    """Test that user IDs auto-increment"""
    user1 = storage.create_user("memuser1@example.com", "User One")
    user2 = storage.create_user("memuser2@example.com", "User Two")
    user3 = storage.create_user("memuser3@example.com", "User Three")

    assert user1.id == 1
    assert user2.id == 2
    assert user3.id == 3


def test_create_user_duplicate_email(storage):
    """Test that creating user with duplicate email raises DuplicateEmailError"""
    storage.create_user("test@example.com", "Test User")

    with pytest.raises(DuplicateEmailError):
        storage.create_user("test@example.com", "Another User")


def test_is_user(storage):
    """Test is_user returns True for existing users"""
    storage.create_user("memuser@example.com", "Test User")

    assert storage.is_user("memuser@example.com") is True
    assert storage.is_user("nonexistent@example.com") is False


def test_get_user_by_email(storage):
    """Test get_user_by_email retrieves existing user by email"""
    created_user = storage.create_user("memuser@example.com", "Test User")

    retrieved_user = storage.get_user_by_email("memuser@example.com")

    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name


def test_get_user_by_email_nonexistent(storage):
    """Test get_user_by_email raises UserNotFoundError for non-existent user"""
    with pytest.raises(UserNotFoundError):
        storage.get_user_by_email("nonexistent@example.com")


def test_get_user_by_id_existing(storage):
    """Test getting user by ID when user exists"""
    created_user = storage.create_user("memuser@example.com", "Test User")

    retrieved_user = storage.get_user_by_id(created_user.id)

    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name


def test_get_user_by_id_nonexistent(storage):
    """Test getting user by ID when user doesn't exist raises UserNotFoundError"""
    with pytest.raises(UserNotFoundError):
        storage.get_user_by_id(999)


def test_multiple_users_stored_separately(storage):
    """Test that multiple users are stored and can be retrieved independently"""
    user1 = storage.create_user("user1@example.com", "User One")
    user2 = storage.create_user("user2@example.com", "User Two")
    user3 = storage.create_user("user3@example.com", "User Three")

    # Retrieve by ID
    assert storage.get_user_by_id(user1.id).email == "user1@example.com"
    assert storage.get_user_by_id(user2.id).email == "user2@example.com"
    assert storage.get_user_by_id(user3.id).email == "user3@example.com"

    # Retrieve by email
    assert storage.get_user_by_email("user1@example.com").id == user1.id
    assert storage.get_user_by_email("user2@example.com").id == user2.id
    assert storage.get_user_by_email("user3@example.com").id == user3.id
