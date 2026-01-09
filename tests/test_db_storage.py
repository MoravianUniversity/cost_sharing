"""
Tests for DatabaseCostStorage class.

This test file uses fixtures from tests/conftest.py:
- empty_db_storage: For tests that need an empty database
- db_storage_with_sample_data: For tests that use the sample data

The sample data is defined in src/cost_sharing/sql/sample-data.sql and documented
in docs/sample-dataset.md. Helper functions from tests/helpers.py are used for
assertions (e.g., assert_user_matches, assert_groups_are).
"""

import sqlite3
from unittest.mock import MagicMock
import pytest
from helpers import assert_user_matches, assert_groups_are
from cost_sharing.db_storage import DatabaseCostStorage
from cost_sharing.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    StorageException
)


def test_is_user_returns_true_for_existing_user(empty_db_storage):
    """Test is_user returns True when user exists"""
    empty_db_storage.create_user("test@example.com", "Test User")
    assert empty_db_storage.is_user("test@example.com") is True


def test_is_user_returns_false_for_nonexistent_user(empty_db_storage):
    """Test is_user returns False when user does not exist"""
    assert empty_db_storage.is_user("nonexistent@example.com") is False


def test_get_user_by_email_returns_user_when_exists(empty_db_storage):
    """Test get_user_by_email retrieves user and all fields are correct"""
    created_user = empty_db_storage.create_user("test@example.com", "Test User")
    retrieved_user = empty_db_storage.get_user_by_email("test@example.com")
    assert_user_matches(retrieved_user, created_user.id, "test@example.com", "Test User")


def test_get_user_by_email_raises_user_not_found_error_when_not_exists(empty_db_storage):
    """Test get_user_by_email raises UserNotFoundError when user does not exist"""
    with pytest.raises(UserNotFoundError):
        empty_db_storage.get_user_by_email("nonexistent@example.com")


def test_create_user_returns_user_with_id_one_for_first_user(empty_db_storage):
    """Test create_user returns user with ID 1 for first user and all fields are correct"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    assert_user_matches(user, 1, "test@example.com", "Test User")


def test_create_user_auto_increments_after_sample_data(db_storage_with_sample_data):
    """Test create_user auto-increments ID after sample data and all fields are correct"""
    user = db_storage_with_sample_data.create_user("newuser@example.com", "New User")
    assert_user_matches(user, 12, "newuser@example.com", "New User")


def test_create_user_raises_duplicate_email_error_for_existing_email(empty_db_storage):
    """Test create_user raises DuplicateEmailError for duplicate email"""
    empty_db_storage.create_user("test@example.com", "Test User")
    with pytest.raises(DuplicateEmailError):
        empty_db_storage.create_user("test@example.com", "Another User")


def test_create_user_auto_increments_ids_for_multiple_users(empty_db_storage):
    """Test create_user auto-increments IDs for multiple users"""
    user1 = empty_db_storage.create_user("user1@example.com", "User One")
    user2 = empty_db_storage.create_user("user2@example.com", "User Two")
    user3 = empty_db_storage.create_user("user3@example.com", "User Three")

    assert user1.id == 1
    assert user2.id == 2
    assert user3.id == 3


def test_get_user_by_id_returns_user_when_exists(empty_db_storage):
    """Test get_user_by_id retrieves user and all fields are correct"""
    created_user = empty_db_storage.create_user("test@example.com", "Test User")
    retrieved_user = empty_db_storage.get_user_by_id(created_user.id)
    assert_user_matches(retrieved_user, created_user.id, "test@example.com", "Test User")


def test_get_user_by_id_raises_user_not_found_error_when_not_exists(empty_db_storage):
    """Test get_user_by_id raises UserNotFoundError for invalid ID"""
    with pytest.raises(UserNotFoundError):
        empty_db_storage.get_user_by_id(999)

    with pytest.raises(UserNotFoundError):
        empty_db_storage.get_user_by_id(0)

    with pytest.raises(UserNotFoundError):
        empty_db_storage.get_user_by_id(-1)


def test_create_and_retrieve_user_by_email(empty_db_storage):
    """Test creating user and retrieving by email"""
    created_user = empty_db_storage.create_user("test@example.com", "Test User")
    retrieved_user = empty_db_storage.get_user_by_email("test@example.com")
    assert_user_matches(retrieved_user, created_user.id, "test@example.com", "Test User")


def test_create_and_retrieve_user_by_id(empty_db_storage):
    """Test creating user and retrieving by ID"""
    created_user = empty_db_storage.create_user("test@example.com", "Test User")
    retrieved_user = empty_db_storage.get_user_by_id(created_user.id)
    assert_user_matches(retrieved_user, created_user.id, "test@example.com", "Test User")


def test_create_user_then_check_is_user(empty_db_storage):
    """Test creating user and verifying with is_user"""
    empty_db_storage.create_user("test@example.com", "Test User")
    assert empty_db_storage.is_user("test@example.com") is True
    assert empty_db_storage.is_user("nonexistent@example.com") is False


def test_multiple_users_can_be_created_and_retrieved(empty_db_storage):
    """Test multiple users can be created and all operations work"""
    user1 = empty_db_storage.create_user("user1@example.com", "User One")
    user2 = empty_db_storage.create_user("user2@example.com", "User Two")
    user3 = empty_db_storage.create_user("user3@example.com", "User Three")

    assert empty_db_storage.is_user("user1@example.com") is True
    assert empty_db_storage.is_user("user2@example.com") is True
    assert empty_db_storage.is_user("user3@example.com") is True

    retrieved1 = empty_db_storage.get_user_by_email("user1@example.com")
    retrieved2 = empty_db_storage.get_user_by_id(user2.id)
    retrieved3 = empty_db_storage.get_user_by_email("user3@example.com")

    assert retrieved1.id == user1.id
    assert retrieved2.id == user2.id
    assert retrieved3.id == user3.id


@pytest.fixture(name='error_storage')
def create_error_storage():
    """
    Create a DatabaseCostStorage instance that raises errors.
    """
    mock_conn = MagicMock()
    storage = DatabaseCostStorage(mock_conn)
    mock_conn.execute = MagicMock(side_effect=sqlite3.Error("Mock database error"))
    return storage


def test_is_user_raises_storage_exception_on_database_error(error_storage):
    """Test is_user raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.is_user("test@example.com")


def test_get_user_by_email_raises_storage_exception_on_database_error(error_storage):
    """Test get_user_by_email raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.get_user_by_email("test@example.com")


def test_create_user_raises_storage_exception_on_database_error(error_storage):
    """Test create_user raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.create_user("test@example.com", "Test User")


def test_get_user_by_id_raises_storage_exception_on_database_error(error_storage):
    """Test get_user_by_id raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.get_user_by_id(1)


# ============================================================================
# get_user_groups Tests
# ============================================================================

def test_get_user_groups_returns_empty_list_when_user_in_no_groups(db_storage_with_sample_data):
    """Test get_user_groups returns empty list when user belongs to no groups"""
    groups = db_storage_with_sample_data.get_user_groups(7)
    assert groups == []


def test_get_user_groups_returns_single_group(db_storage_with_sample_data):
    """Test get_user_groups returns single group when user belongs to one group"""
    groups = db_storage_with_sample_data.get_user_groups(3)
    assert_groups_are(groups, ["roommates"])


def test_get_user_groups_returns_multiple_groups(db_storage_with_sample_data):
    """Test get_user_groups returns multiple groups when user belongs to multiple groups"""
    groups = db_storage_with_sample_data.get_user_groups(1)
    assert_groups_are(groups, ["weekend_trip", "roommates"])


def test_get_user_groups_raises_storage_exception_on_database_error(error_storage):
    """Test get_user_groups raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.get_user_groups(1)


# ============================================================================
# create_group Tests
# ============================================================================

def test_create_group_returns_group_with_id_one_for_first_group(empty_db_storage):
    """Test create_group returns group with ID 1 for first group"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    group = empty_db_storage.create_group(user.id, "Test Group", "Test description")
    assert group.id == 1
    assert group.name == "Test Group"
    assert group.description == "Test description"
    assert group.member_count == 1


def test_create_group_auto_increments_after_sample_data(db_storage_with_sample_data):
    """Test create_group auto-increments ID after sample data"""
    user = db_storage_with_sample_data.get_user_by_id(1)
    group = db_storage_with_sample_data.create_group(user.id, "New Group", "New description")
    assert group.id == 7  # Sample data has 6 groups
    assert group.name == "New Group"
    assert group.description == "New description"
    assert group.member_count == 1


def test_create_group_without_description(empty_db_storage):
    """Test create_group works without description"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    group = empty_db_storage.create_group(user.id, "Test Group")
    assert group.id == 1
    assert group.name == "Test Group"
    assert group.description == ""
    assert group.member_count == 1


def test_create_group_adds_creator_as_member(empty_db_storage):
    """Test create_group adds the creator as a member"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    group = empty_db_storage.create_group(user.id, "Test Group")

    # Verify user is in the group
    user_groups = empty_db_storage.get_user_groups(user.id)
    assert len(user_groups) == 1
    assert user_groups[0].id == group.id
    assert user_groups[0].name == "Test Group"


def test_create_group_raises_user_not_found_error_for_invalid_user(empty_db_storage):
    """Test create_group raises UserNotFoundError when user doesn't exist"""
    with pytest.raises(UserNotFoundError):
        empty_db_storage.create_group(999, "Test Group")


def test_create_group_raises_storage_exception_on_database_error(error_storage):
    """Test create_group raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.create_group(1, "Test Group")
