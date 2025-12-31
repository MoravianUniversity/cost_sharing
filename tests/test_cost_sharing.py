"""Tests for CostSharing application layer"""

import pytest
from cost_sharing.cost_sharing import CostSharing
from cost_sharing.storage import InMemoryCostStorage
from cost_sharing.exceptions import UserNotFoundError


@pytest.fixture(name='app')
def create_app_with_user():
    """Fixture for CostSharing with a single existing user"""
    storage = InMemoryCostStorage()
    storage.create_user(email="test@example.com", name="Test User")
    return CostSharing(storage)


def test_get_user_by_id_succeeds(app):
    """Test get_user_by_id - succeeds when user exists"""
    user = app.get_user_by_id(1)

    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_get_user_by_id_raises_exception(app):
    """Test get_user_by_id - raises exception when user doesn't exist"""
    with pytest.raises(UserNotFoundError):
        app.get_user_by_id(999)


def test_get_or_create_user_returns_existing(app):
    """Test get_or_create_user - returns existing user when email exists"""
    user = app.get_or_create_user(
        email="test@example.com",
        name="Updated Name"
    )

    # Should return existing user, not create new one
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test User"  # Original name, not updated


def test_get_or_create_user_returns_new(app):
    """Test get_or_create_user - creates and returns new user when email doesn't exist"""
    user = app.get_or_create_user(
        email="newuser@example.com",
        name="New User"
    )

    assert user.email == "newuser@example.com"
    assert user.name == "New User"
    assert user.id == 2  # Second user created
