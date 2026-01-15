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
from helpers import assert_user_matches, assert_groups_are, \
    assert_user_is, assert_group_matches, assert_group_is, assert_group_has_members, \
    assert_expenses_are, assert_expense_participants
from cost_sharing.db_storage import DatabaseCostStorage
from cost_sharing.exceptions import StorageException


def test_get_user_by_email_returns_user_when_exists(empty_db_storage):
    """Test get_user_by_email retrieves user and all fields are correct"""
    created_user = empty_db_storage.create_user("test@example.com", "Test User")
    retrieved_user = empty_db_storage.get_user_by_email("test@example.com")
    assert_user_matches(retrieved_user, created_user.id, "test@example.com", "Test User")


def test_get_user_by_email_returns_none_when_not_exists(empty_db_storage):
    """Test get_user_by_email returns None when user does not exist"""
    user = empty_db_storage.get_user_by_email("nonexistent@example.com")
    assert user is None


def test_create_user_returns_user_with_id_one_for_first_user(empty_db_storage):
    """Test create_user returns user with ID 1 for first user and all fields are correct"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    assert_user_matches(user, 1, "test@example.com", "Test User")


def test_create_user_auto_increments_after_sample_data(db_storage_with_sample_data):
    """Test create_user auto-increments ID after sample data and all fields are correct"""
    user = db_storage_with_sample_data.create_user("newuser@example.com", "New User")
    assert_user_matches(user, 12, "newuser@example.com", "New User")


def test_create_user_raises_storage_exception_for_duplicate_email(empty_db_storage):
    """Test create_user raises StorageException for duplicate email (IntegrityError wrapped)"""
    empty_db_storage.create_user("test@example.com", "Test User")
    with pytest.raises(StorageException) as exc_info:
        empty_db_storage.create_user("test@example.com", "Another User")
    assert "Database error creating user" in str(exc_info.value)


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


def test_get_user_by_id_returns_none_when_not_exists(empty_db_storage):
    """Test get_user_by_id returns None for invalid ID"""
    user = empty_db_storage.get_user_by_id(999)
    assert user is None

    user = empty_db_storage.get_user_by_id(0)
    assert user is None

    user = empty_db_storage.get_user_by_id(-1)
    assert user is None


def test_multiple_users_can_be_created_and_retrieved(empty_db_storage):
    """Test multiple users can be created and all operations work"""
    user1 = empty_db_storage.create_user("user1@example.com", "User One")
    user2 = empty_db_storage.create_user("user2@example.com", "User Two")
    user3 = empty_db_storage.create_user("user3@example.com", "User Three")

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
    group = empty_db_storage.create_group("Test Group", "Test description", user.id)
    assert_group_matches(group, 1, "Test Group", "Test description", user, expected_member_count=1)
    assert_user_matches(group.members[0], user.id, "test@example.com", "Test User")


def test_create_group_auto_increments_after_sample_data(db_storage_with_sample_data):
    """Test create_group auto-increments ID after sample data"""
    user = db_storage_with_sample_data.get_user_by_id(1)
    group = db_storage_with_sample_data.create_group("New Group", "New description", user.id)
    assert_group_matches(group, 7, "New Group", "New description", user, expected_member_count=1)
    assert_user_is(group.members[0], "alice")


def test_create_group_without_description(empty_db_storage):
    """Test create_group works without description"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    group = empty_db_storage.create_group("Test Group", None, user.id)
    assert_group_matches(group, 1, "Test Group", "", user, expected_member_count=1)
    assert_user_matches(group.members[0], user.id, "test@example.com", "Test User")


def test_create_group_adds_creator_as_member(empty_db_storage):
    """Test create_group adds the creator as a member"""
    user = empty_db_storage.create_user("test@example.com", "Test User")
    group = empty_db_storage.create_group("Test Group", None, user.id)

    # Verify user is in the group
    user_groups = empty_db_storage.get_user_groups(user.id)
    assert len(user_groups) == 1
    assert_group_matches(user_groups[0], group.id, "Test Group", "", user, expected_member_count=1)
    assert_user_matches(user_groups[0].members[0], user.id, "test@example.com", "Test User")


def test_create_group_raises_storage_exception_when_creator_not_found(empty_db_storage):
    """Test create_group raises StorageException when creator user doesn't exist (line 206)"""
    storage = empty_db_storage

    # get_user_by_id will return None for non-existent user
    with pytest.raises(StorageException) as exc_info:
        storage.create_group("Test Group", None, 999)
    assert "User with ID 999 not found" in str(exc_info.value)


def test_create_group_raises_storage_exception_on_database_error(error_storage):
    """Test create_group raises StorageException when database error occurs during insert"""
    storage = error_storage

    # This test exists to cover the except block in create_group, but we have to get past
    # the get_user_by_id check.  This is a hack.  We need get_user_by_id to return a "User"
    # so that we get past that check. I made it return a dict because I don't want to import
    # the User model just for this test.
    storage.get_user_by_id = MagicMock(return_value={"id":1,
    "email":"test@example.com", "name":"Test User"})

    with pytest.raises(StorageException) as exc_info:
        storage.create_group("Test Group", None, 1)
    assert "Database error creating group" in str(exc_info.value)


def test_get_group_by_id_returns_group_with_creator_and_members(db_storage_with_sample_data):
    """Test get_group_by_id returns group with creator and members populated"""
    storage = db_storage_with_sample_data

    # Get group 2 (Roommates Spring 2025)
    group = storage.get_group_by_id(2)

    # Verify group matches expected sample data
    assert_group_is(group, "roommates")


def test_get_group_by_id_returns_none_when_not_exists(empty_db_storage):
    """Test get_group_by_id returns None when group doesn't exist"""
    group = empty_db_storage.get_group_by_id(999)
    assert group is None


def test_get_group_by_id_handles_empty_description(db_storage_with_sample_data):
    """Test get_group_by_id handles group with empty description correctly"""
    storage = db_storage_with_sample_data

    # Group 5 has null description in sample data
    group = storage.get_group_by_id(5)

    assert_group_is(group, "quick_split")


def test_get_group_by_id_raises_storage_exception_on_database_error(error_storage):
    """Test get_group_by_id raises StorageException when database error occurs (lines 282-283)"""
    storage = error_storage

    with pytest.raises(StorageException) as exc_info:
        storage.get_group_by_id(1)
    assert "Database error retrieving group by ID" in str(exc_info.value)


# ============================================================================
# add_group_member Tests
# ============================================================================

def test_add_group_member_adds_member_to_existing_group_and_user(db_storage_with_sample_data):
    """Test add_group_member successfully adds an existing user to an existing group"""
    storage = db_storage_with_sample_data

    # Group 1 has members [1, 2] (Alice, Bob) from sample data
    # Add user 3 (Charlie) to group 1
    result = storage.add_group_member(1, 3)
    assert result is True

    # Verify group now has members [1, 2, 3]
    group = storage.get_group_by_id(1)
    assert_group_has_members(group, [1, 2, 3])


def test_add_group_member_fails_for_nonexistent_group(db_storage_with_sample_data):
    """Test add_group_member raises StorageException when group doesn't exist"""
    storage = db_storage_with_sample_data

    # Try to add existing user (user 1) to non-existent group
    with pytest.raises(StorageException) as exc_info:
        storage.add_group_member(999, 1)
    assert "Database error adding member" in str(exc_info.value)


def test_add_group_member_fails_for_nonexistent_user(db_storage_with_sample_data):
    """Test add_group_member raises StorageException when user doesn't exist"""
    storage = db_storage_with_sample_data

    # Try to add non-existent user to existing group (group 1)
    with pytest.raises(StorageException) as exc_info:
        storage.add_group_member(1, 999)
    assert "Database error adding member" in str(exc_info.value)


def test_add_group_member_fails_for_duplicate_member(db_storage_with_sample_data):
    """Test add_group_member raises StorageException when user is already a member"""
    storage = db_storage_with_sample_data

    # Group 2 has members [3, 1, 4] (Charlie, Alice, David) from sample data
    # Try to add Alice (user 1) again
    with pytest.raises(StorageException) as exc_info:
        storage.add_group_member(2, 1)
    assert "Database error adding member" in str(exc_info.value)


def test_add_group_member_fails_on_database_error(error_storage):
    """Test add_group_member raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException) as exc_info:
        storage.add_group_member(1, 1)
    assert "Database error adding member" in str(exc_info.value)


# ============================================================================
# get_group_expenses Tests
# ============================================================================

def test_get_group_expenses_returns_empty_list_when_no_expenses(db_storage_with_sample_data):
    """Test get_group_expenses returns empty list when group has no expenses"""
    storage = db_storage_with_sample_data
    # Group 1 (weekend_trip) has no expenses in sample data
    expenses = storage.get_group_expenses(1)
    assert expenses == []


def test_get_group_expenses_returns_empty_list_for_nonexistent_group(empty_db_storage):
    """Test get_group_expenses returns empty list when group doesn't exist"""
    expenses = empty_db_storage.get_group_expenses(999)
    assert expenses == []


def test_get_group_expenses_returns_single_expense(db_storage_with_sample_data):
    """Test get_group_expenses returns single expense when group has one expense"""
    storage = db_storage_with_sample_data
    # Group 3 has one expense (team_lunch)
    expenses = storage.get_group_expenses(3)
    assert_expenses_are(expenses, ["team_lunch"])


def test_get_group_expenses_returns_multiple_expenses(db_storage_with_sample_data):
    """Test get_group_expenses returns multiple expenses when group has multiple expenses"""
    storage = db_storage_with_sample_data
    # Group 2 has 4 expenses
    expenses = storage.get_group_expenses(2)
    assert_expenses_are(
        expenses,
        ["grocery_shopping", "utilities_bill", "restaurant_dinner", "internet_bill"]
    )


def test_get_group_expenses_includes_paid_by_user(db_storage_with_sample_data):
    """Test get_group_expenses includes correct paid_by user for each expense"""
    storage = db_storage_with_sample_data
    expenses = storage.get_group_expenses(2)

    # First expense (grocery_shopping) was paid by Charlie (user 3)
    assert expenses[0].paid_by.id == 3
    assert_user_is(expenses[0].paid_by, "charlie")

    # Second expense (utilities_bill) was paid by Alice (user 1)
    assert expenses[1].paid_by.id == 1
    assert_user_is(expenses[1].paid_by, "alice")


def test_get_group_expenses_includes_split_between_participants(db_storage_with_sample_data):
    """Test get_group_expenses includes correct split_between participants for each expense"""
    storage = db_storage_with_sample_data
    expenses = storage.get_group_expenses(2)

    # First expense (grocery_shopping) split between Charlie and Alice
    assert_expense_participants(expenses[0], [3, 1])

    # Fourth expense (internet_bill) split between Charlie, Alice, and David
    assert_expense_participants(expenses[3], [3, 1, 4])


def test_get_group_expenses_has_per_person_amount_as_none(db_storage_with_sample_data):
    """Test get_group_expenses returns expenses with per_person_amount as None"""
    storage = db_storage_with_sample_data
    expenses = storage.get_group_expenses(2)

    # All expenses should have per_person_amount as None from storage layer
    for expense in expenses:
        assert expense.per_person_amount is None


def test_get_group_expenses_orders_by_date_then_id(db_storage_with_sample_data):
    """Test get_group_expenses returns expenses ordered by date, then by ID"""
    storage = db_storage_with_sample_data
    expenses = storage.get_group_expenses(2)

    # Group 2 expenses should be ordered by date:
    # 2025-01-10 (grocery_shopping, id=1)
    # 2025-01-15 (utilities_bill, id=2)
    # 2025-01-20 (restaurant_dinner, id=3)
    # 2025-01-25 (internet_bill, id=4)
    assert expenses[0].id == 1
    assert expenses[1].id == 2
    assert expenses[2].id == 3
    assert expenses[3].id == 4


def test_get_group_expenses_with_large_group(db_storage_with_sample_data):
    """Test get_group_expenses works with group that has many expenses"""
    storage = db_storage_with_sample_data
    # Group 4 has 4 expenses
    expenses = storage.get_group_expenses(4)
    assert_expenses_are(expenses, ["textbooks", "coffee_snacks", "printing_costs", "group_dinner"])


def test_get_group_expenses_with_many_participants(db_storage_with_sample_data):
    """Test get_group_expenses correctly handles expenses with many participants"""
    storage = db_storage_with_sample_data
    expenses = storage.get_group_expenses(4)

    # Textbooks expense split between all 5 members
    textbooks_expense = [e for e in expenses if e.id == 6][0]
    assert_expense_participants(textbooks_expense, [8, 9, 10, 11, 2])


def test_get_group_expenses_raises_storage_exception_on_database_error(error_storage):
    """Test get_group_expenses raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException) as exc_info:
        storage.get_group_expenses(1)
    assert "Database error retrieving group expenses" in str(exc_info.value)
