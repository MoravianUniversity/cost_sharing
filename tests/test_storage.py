"""Tests for InMemoryCostStorage"""

import pytest
from storage import InMemoryCostStorage
from cost_sharing.models import User
from cost_sharing.exceptions import DuplicateEmailError, DuplicateOAuthProviderIdError


@pytest.fixture(name='storage')
def create_storage():
    """Fixture for InMemoryCostStorage"""
    return InMemoryCostStorage()


def test_create_user(storage):
    """Test creating a new user"""
    user = storage.create_user(
        email="test@example.com",
        name="Test User",
        oauth_provider_id="oauth-123"
    )

    assert isinstance(user, User)
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.oauth_provider_id == "oauth-123"


def test_create_user_auto_increment_id(storage):
    """Test that user IDs auto-increment"""
    user1 = storage.create_user("user1@example.com", "User One", "oauth-1")
    user2 = storage.create_user("user2@example.com", "User Two", "oauth-2")
    user3 = storage.create_user("user3@example.com", "User Three", "oauth-3")

    assert user1.id == 1
    assert user2.id == 2
    assert user3.id == 3


def test_create_user_duplicate_email(storage):
    """Test that creating user with duplicate email raises DuplicateEmailError"""
    storage.create_user("test@example.com", "Test User", "oauth-123")

    with pytest.raises(DuplicateEmailError):
        storage.create_user("test@example.com", "Another User", "oauth-456")


def test_create_user_duplicate_oauth_provider_id(storage):
    """Test duplicate oauth_provider_id raises DuplicateOAuthProviderIdError"""
    storage.create_user("user1@example.com", "User One", "oauth-123")

    with pytest.raises(DuplicateOAuthProviderIdError):
        storage.create_user("user2@example.com", "User Two", "oauth-123")


def test_get_user_by_id_existing(storage):
    """Test getting user by ID when user exists"""
    created_user = storage.create_user("test@example.com", "Test User", "oauth-123")

    retrieved_user = storage.get_user_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name
    assert retrieved_user.oauth_provider_id == created_user.oauth_provider_id


def test_get_user_by_id_nonexistent(storage):
    """Test getting user by ID when user doesn't exist"""
    retrieved_user = storage.get_user_by_id(999)

    assert retrieved_user is None


def test_find_user_by_oauth_provider_id_existing(storage):
    """Test finding user by OAuth provider ID when user exists"""
    created_user = storage.create_user("test@example.com", "Test User", "oauth-123")

    found_user = storage.find_user_by_oauth_provider_id("oauth-123")

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == created_user.email
    assert found_user.name == created_user.name
    assert found_user.oauth_provider_id == created_user.oauth_provider_id


def test_find_user_by_oauth_provider_id_nonexistent(storage):
    """Test finding user by OAuth provider ID when user doesn't exist"""
    found_user = storage.find_user_by_oauth_provider_id("nonexistent-oauth-id")

    assert found_user is None


def test_multiple_users_stored_separately(storage):
    """Test that multiple users are stored and can be retrieved independently"""
    user1 = storage.create_user("user1@example.com", "User One", "oauth-1")
    user2 = storage.create_user("user2@example.com", "User Two", "oauth-2")
    user3 = storage.create_user("user3@example.com", "User Three", "oauth-3")

    # Retrieve by ID
    assert storage.get_user_by_id(user1.id).email == "user1@example.com"
    assert storage.get_user_by_id(user2.id).email == "user2@example.com"
    assert storage.get_user_by_id(user3.id).email == "user3@example.com"

    # Retrieve by oauth_provider_id
    assert storage.find_user_by_oauth_provider_id("oauth-1").id == user1.id
    assert storage.find_user_by_oauth_provider_id("oauth-2").id == user2.id
    assert storage.find_user_by_oauth_provider_id("oauth-3").id == user3.id
