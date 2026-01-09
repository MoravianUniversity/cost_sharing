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
from helpers import assert_user_is, assert_user_matches, assert_groups_are
from cost_sharing.exceptions import UserNotFoundError


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


def test_get_user_groups_returns_correct_member_counts(app_with_sample_data):
    """Test get_user_groups returns correct member counts for each group"""
    groups = app_with_sample_data.get_user_groups(1)
    assert_groups_are(groups, ["weekend_trip", "roommates"])
