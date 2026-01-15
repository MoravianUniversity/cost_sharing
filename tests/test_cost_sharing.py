"""
Tests for CostSharing application layer.

This test file uses fixtures from tests/conftest.py:
- app_empty_db: For tests that need an empty database
- app_with_sample_data: For tests that use the sample data

The sample data is defined in src/cost_sharing/sql/sample-data.sql and documented
in docs/sample-dataset.md. Helper functions from tests/helpers.py are used for
assertions (e.g., assert_user_is, assert_groups_are).
"""

import pytest
from helpers import (
    assert_user_is, assert_user_matches, assert_groups_are,
    assert_group_matches, assert_group_is, assert_group_has_members
)
from cost_sharing.exceptions import (
    UserNotFoundError, GroupNotFoundError, ForbiddenError, ConflictError
)


def test_get_user_by_id_succeeds(app_with_sample_data):
    """Test get_user_by_id - succeeds when user exists"""
    user = app_with_sample_data.get_user_by_id(1)
    assert_user_is(user, "alice")


def test_get_user_by_id_raises_exception(app_with_sample_data):
    """Test get_user_by_id - raises exception when user doesn't exist"""
    with pytest.raises(UserNotFoundError):
        app_with_sample_data.get_user_by_id(999)


def test_get_or_create_user_returns_existing(app_with_sample_data):
    """Test get_or_create_user - returns existing user when email exists"""
    user = app_with_sample_data.get_or_create_user(
        email="alice@school.edu",
        name="Updated Name"
    )
    # Should return existing user, not create new one - original name preserved
    assert_user_is(user, "alice")


def test_get_or_create_user_returns_new(app_empty_db):
    """Test get_or_create_user - creates and returns new user when email doesn't exist"""
    user = app_empty_db.get_or_create_user(
        email="newuser@example.com",
        name="New User"
    )
    assert_user_matches(user, 1, "newuser@example.com", "New User")


# ============================================================================
# get_user_groups Tests
# ============================================================================


def test_get_user_groups_returns_empty_list_when_user_in_no_groups(app_with_sample_data):
    """Test get_user_groups returns empty list when user belongs to no groups"""
    groups = app_with_sample_data.get_user_groups(7)
    assert groups == []


def test_get_user_groups_returns_groups_for_user(app_with_sample_data):
    """Test get_user_groups returns groups for user with sample data"""
    groups = app_with_sample_data.get_user_groups(1)
    assert_groups_are(groups, ["weekend_trip", "roommates"])


def test_get_user_groups_returns_only_user_groups(app_with_sample_data):
    """Test get_user_groups returns only groups the user belongs to"""
    groups = app_with_sample_data.get_user_groups(3)
    assert_groups_are(groups, ["roommates"])


def test_get_user_groups_returns_correct_members(app_with_sample_data):
    """Test get_user_groups returns correct members for each group"""
    groups = app_with_sample_data.get_user_groups(1)
    assert_groups_are(groups, ["weekend_trip", "roommates"])


# ============================================================================
# create_group Tests
# ============================================================================

def test_create_group_returns_group_with_correct_fields(app_empty_db):
    """Test create_group returns group with correct fields"""
    user = app_empty_db.get_or_create_user("test@example.com", "Test User")
    group = app_empty_db.create_group(user.id, "Test Group", "Test description")
    assert_group_matches(group, 1, "Test Group", "Test description", user, expected_member_count=1)
    assert_user_matches(group.members[0], user.id, "test@example.com", "Test User")


def test_create_group_without_description(app_empty_db):
    """Test create_group works without description"""
    user = app_empty_db.get_or_create_user("test@example.com", "Test User")
    group = app_empty_db.create_group(user.id, "Test Group")
    assert_group_matches(group, 1, "Test Group", "", user, expected_member_count=1)
    assert_user_matches(group.members[0], user.id, "test@example.com", "Test User")


def test_create_group_adds_creator_as_member(app_empty_db):
    """Test create_group adds the creator as a member"""
    user = app_empty_db.get_or_create_user("test@example.com", "Test User")
    group = app_empty_db.create_group(user.id, "Test Group")

    # Verify user is in the group
    user_groups = app_empty_db.get_user_groups(user.id)
    assert len(user_groups) == 1
    assert_group_matches(user_groups[0], group.id, "Test Group", "", user, expected_member_count=1)
    assert_user_matches(user_groups[0].members[0], user.id, "test@example.com", "Test User")


def test_create_group_raises_user_not_found_error_for_invalid_user(app_empty_db):
    """Test create_group raises UserNotFoundError when user doesn't exist"""
    with pytest.raises(UserNotFoundError):
        app_empty_db.create_group(999, "Test Group")


def test_get_group_by_id_returns_group_for_member(app_with_sample_data):
    """Test get_group_by_id returns group when user is a member"""
    app = app_with_sample_data

    # User 1 (Alice) is a member of group 2 (Roommates Spring 2025)
    group = app.get_group_by_id(2, 1)

    assert_group_is(group, "roommates")


def test_get_group_by_id_raises_forbidden_error_for_non_member(app_with_sample_data):
    """Test get_group_by_id raises ForbiddenError when user is not a member"""
    app = app_with_sample_data

    # User 2 (Bob) is not a member of group 2 (Roommates Spring 2025)
    with pytest.raises(ForbiddenError) as exc_info:
        app.get_group_by_id(2, 2)
    assert "You do not have access to this group" in str(exc_info.value)


def test_get_group_by_id_raises_group_not_found_error_for_invalid_group(app_empty_db):
    """Test get_group_by_id raises GroupNotFoundError when group doesn't exist"""
    app = app_empty_db
    user = app.get_or_create_user("test@example.com", "Test User")

    with pytest.raises(GroupNotFoundError) as exc_info:
        app.get_group_by_id(999, user.id)
    assert "Group with ID 999 not found" in str(exc_info.value)


def test_get_group_by_id_handles_empty_description(app_with_sample_data):
    """Test get_group_by_id handles group with empty description correctly"""
    app = app_with_sample_data

    # User 9 (Iris) is a member of group 5 (Quick Split) which has null description
    group = app.get_group_by_id(5, 9)

    assert_group_is(group, "quick_split")


# ============================================================================
# add_group_member Tests
# ============================================================================

def test_add_group_member_creator_adds_existing_user(app_with_sample_data):
    """Test add_group_member - creator adds existing user to group"""
    app = app_with_sample_data

    # Group 1: creator is user 1 (Alice), members [1, 2] (Alice, Bob)
    # User 3 (Charlie) exists but is not in group 1
    # User 1 (Alice) is the creator, so she can add members
    group = app.add_group_member(1, 1, "charlie@school.edu", "Charlie")

    # Verify group now has members [1, 2, 3]
    assert_group_has_members(group, [1, 2, 3])


def test_add_group_member_creator_adds_new_user(app_with_sample_data):
    """Test add_group_member - creator creates new user and adds to group"""
    app = app_with_sample_data

    # Group 1: creator is user 1 (Alice), members [1, 2] (Alice, Bob)
    # User 1 (Alice) is the creator, so she can add members
    # Add a new user that doesn't exist
    group = app.add_group_member(1, 1, "newuser@example.com", "New User")

    # Verify group now has the new member
    member_ids = [member.id for member in group.members]
    assert 1 in member_ids  # Alice
    assert 2 in member_ids  # Bob
    # New user should have ID 12 (after 11 sample users)
    assert 12 in member_ids
    assert len(group.members) == 3

    # Verify the new user was created
    new_user = app.get_user_by_id(12)
    assert_user_matches(new_user, 12, "newuser@example.com", "New User")


def test_add_group_member_non_creator_member_adds_existing_user(app_with_sample_data):
    """Test add_group_member - non-creator member adds existing user to group"""
    app = app_with_sample_data

    # Group 2: creator is user 3 (Charlie), members [3, 1, 4] (Charlie, Alice, David)
    # User 1 (Alice) is a member but not the creator
    # User 2 (Bob) exists but is not in group 2
    # User 1 (Alice) can add members even though she's not the creator
    group = app.add_group_member(2, 1, "bob@school.edu", "Bob")

    # Verify group now has members [3, 1, 4, 2]
    assert_group_has_members(group, [3, 1, 4, 2])


def test_add_group_member_raises_group_not_found_error(app_with_sample_data):
    """Test add_group_member raises GroupNotFoundError when group doesn't exist"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError) as exc_info:
        app.add_group_member(999, 1, "charlie@school.edu", "Charlie")
    assert "Group with ID 999 not found" in str(exc_info.value)


def test_add_group_member_raises_forbidden_error_for_non_member_caller(app_with_sample_data):
    """Test add_group_member raises ForbiddenError when caller is not a member"""
    app = app_with_sample_data

    # User 2 (Bob) is not a member of group 2 (Roommates Spring 2025)
    with pytest.raises(ForbiddenError) as exc_info:
        app.add_group_member(2, 2, "charlie@school.edu", "Charlie")
    assert "You do not have access to this group" in str(exc_info.value)


def test_add_group_member_raises_conflict_error_for_duplicate_member(app_with_sample_data):
    """Test add_group_member raises ConflictError when user is already a member"""
    app = app_with_sample_data

    # Group 2 has members [3, 1, 4] (Charlie, Alice, David) from sample data
    # User 1 (Alice) is a member, so she can add members
    # Try to add Alice (user 1) again
    with pytest.raises(ConflictError) as exc_info:
        app.add_group_member(2, 1, "alice@school.edu", "Alice")
    assert "User is already a member of this group" in str(exc_info.value)
