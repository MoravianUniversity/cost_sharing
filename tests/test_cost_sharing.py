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
    assert_group_matches, assert_group_is, assert_group_has_members,
    assert_expenses_are, assert_expense_participants,
    SAMPLE_USER_REQUESTS,
    TEST_USER_REQUESTS, TEST_EXPENSE_REQUESTS
)
from cost_sharing.models import UserRequest, GroupRequest
from cost_sharing.exceptions import (
    UserNotFoundError, GroupNotFoundError, ForbiddenError, ConflictError,
    ValidationError, ExpenseNotFoundError
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
    # Note: Name is intentionally different to test that existing user name is preserved
    user_request = UserRequest(email="alice@school.edu", name="Updated Name")
    user = app_with_sample_data.get_or_create_user(user_request)
    # Should return existing user, not create new one - original name preserved
    assert_user_is(user, "alice")


def test_get_or_create_user_returns_new(app_empty_db):
    """Test get_or_create_user - creates and returns new user when email doesn't exist"""
    user = app_empty_db.get_or_create_user(TEST_USER_REQUESTS["new_user"])
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
    user = app_empty_db.get_or_create_user(TEST_USER_REQUESTS["test_user"])
    group_request = GroupRequest(
        name="Test Group",
        description="Test description",
        created_by_user_id=user.id
    )
    group = app_empty_db.create_group(group_request)
    assert_group_matches(group, 1, "Test Group", "Test description", user, expected_member_count=1)
    assert_user_matches(group.members[0], user.id, "test@example.com", "Test User")


def test_create_group_without_description(app_empty_db):
    """Test create_group works without description"""
    user = app_empty_db.get_or_create_user(TEST_USER_REQUESTS["test_user"])
    group_request = GroupRequest(
        name="Test Group",
        description="",
        created_by_user_id=user.id
    )
    group = app_empty_db.create_group(group_request)
    assert_group_matches(group, 1, "Test Group", "", user, expected_member_count=1)
    assert_user_matches(group.members[0], user.id, "test@example.com", "Test User")


def test_create_group_adds_creator_as_member(app_empty_db):
    """Test create_group adds the creator as a member"""
    user = app_empty_db.get_or_create_user(TEST_USER_REQUESTS["test_user"])
    group_request = GroupRequest(
        name="Test Group",
        description="",
        created_by_user_id=user.id
    )
    group = app_empty_db.create_group(group_request)

    # Verify user is in the group
    user_groups = app_empty_db.get_user_groups(user.id)
    assert len(user_groups) == 1
    assert_group_matches(user_groups[0], group.id, "Test Group", "", user, expected_member_count=1)
    assert_user_matches(user_groups[0].members[0], user.id, "test@example.com", "Test User")


def test_create_group_raises_user_not_found_error_for_invalid_user(app_empty_db):
    """Test create_group raises UserNotFoundError when user doesn't exist"""
    with pytest.raises(UserNotFoundError):
        group_request = GroupRequest(
            name="Test Group",
            description="",
            created_by_user_id=999
        )
        app_empty_db.create_group(group_request)


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
    user = app.get_or_create_user(TEST_USER_REQUESTS["test_user"])

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
    group = app.add_group_member(1, 1, SAMPLE_USER_REQUESTS["charlie"])

    # Verify group now has members [1, 2, 3]
    assert_group_has_members(group, [1, 2, 3])


def test_add_group_member_creator_adds_new_user(app_with_sample_data):
    """Test add_group_member - creator creates new user and adds to group"""
    app = app_with_sample_data

    # Group 1: creator is user 1 (Alice), members [1, 2] (Alice, Bob)
    # User 1 (Alice) is the creator, so she can add members
    # Add a new user that doesn't exist
    group = app.add_group_member(1, 1, TEST_USER_REQUESTS["new_user"])

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
    group = app.add_group_member(2, 1, SAMPLE_USER_REQUESTS["bob"])

    # Verify group now has members [3, 1, 4, 2]
    assert_group_has_members(group, [3, 1, 4, 2])


def test_add_group_member_raises_group_not_found_error(app_with_sample_data):
    """Test add_group_member raises GroupNotFoundError when group doesn't exist"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError) as exc_info:
        app.add_group_member(999, 1, SAMPLE_USER_REQUESTS["charlie"])
    assert "Group with ID 999 not found" in str(exc_info.value)


def test_add_group_member_raises_forbidden_error_for_non_member_caller(app_with_sample_data):
    """Test add_group_member raises ForbiddenError when caller is not a member"""
    app = app_with_sample_data

    # User 2 (Bob) is not a member of group 2 (Roommates Spring 2025)
    with pytest.raises(ForbiddenError) as exc_info:
        app.add_group_member(2, 2, SAMPLE_USER_REQUESTS["charlie"])
    assert "You do not have access to this group" in str(exc_info.value)


def test_add_group_member_raises_conflict_error_for_duplicate_member(app_with_sample_data):
    """Test add_group_member raises ConflictError when user is already a member"""
    app = app_with_sample_data

    # Group 2 has members [3, 1, 4] (Charlie, Alice, David) from sample data
    # User 1 (Alice) is a member, so she can add members
    # Try to add Alice (user 1) again
    with pytest.raises(ConflictError) as exc_info:
        app.add_group_member(2, 1, SAMPLE_USER_REQUESTS["alice"])
    assert "User is already a member of this group" in str(exc_info.value)


# ============================================================================
# remove_group_member Tests
# ============================================================================

def test_member_can_remove_themself(app_with_sample_data):
    """Test member can remove themselves from group with no expenses"""
    app = app_with_sample_data

    # Group 1: creator is user 1 (Alice), members [1, 2] (Alice, Bob),
    # no expenses. User 2 (Bob) removes themselves.
    app.remove_group_member(1, 2, 2)

    # Verify Bob is no longer a member
    group = app.get_group_by_id(1, 1)
    assert_group_has_members(group, [1])


def test_group_creator_can_remove_other_member(app_with_sample_data):
    """Test group creator can remove another member from group with no
    expenses"""
    app = app_with_sample_data

    # Group 1: creator is user 1 (Alice), members [1, 2] (Alice, Bob),
    # no expenses. User 1 (Alice, creator) removes user 2 (Bob).
    app.remove_group_member(1, 2, 1)

    # Verify Bob is no longer a member
    group = app.get_group_by_id(1, 1)
    assert_group_has_members(group, [1])


def test_group_creator_cannot_remove_themself(app_with_sample_data):
    """Test group creator cannot remove themselves"""
    app = app_with_sample_data

    # Group 1: creator is user 1 (Alice), members [1, 2] (Alice, Bob).
    # User 1 (Alice, creator) tries to remove themselves.
    with pytest.raises(ConflictError) as exc_info:
        app.remove_group_member(1, 1, 1)
    assert "Creator cannot remove themself" in str(exc_info.value)


def test_non_creator_member_cannot_remove_others(app_with_sample_data):
    """Test non-creator member cannot remove another member"""
    app = app_with_sample_data

    # Group 2: creator is user 3 (Charlie), members [3, 1, 4] (Charlie,
    # Alice, David). User 1 (Alice, not creator) tries to remove user 4
    # (David).
    with pytest.raises(ConflictError) as exc_info:
        app.remove_group_member(2, 4, 1)
    assert "Only group creator can remove others" in str(exc_info.value)


def test_member_cannot_be_removed_when_involved_in_expenses_as_payer(
        app_with_sample_data):
    """Test member cannot be removed when involved in expenses as payer"""
    app = app_with_sample_data

    # Group 2: creator is user 3 (Charlie), members [3, 1, 4]. User 1
    # (Alice, not creator) is involved in expenses as participant. User 1
    # tries to remove themselves (but involved in expenses).
    with pytest.raises(ConflictError) as exc_info:
        app.remove_group_member(2, 1, 1)
    assert "Cannot remove member who is involved in expenses" in str(
        exc_info.value)


def test_member_cannot_be_removed_when_involved_in_expenses_as_participant(
        app_with_sample_data):
    """Test member cannot be removed when involved in expenses as
    participant"""
    app = app_with_sample_data

    # Group 2: has expenses where user 1 (Alice) is a participant. User 3
    # (Charlie, creator) tries to remove user 1 (Alice, involved as
    # participant).
    with pytest.raises(ConflictError) as exc_info:
        app.remove_group_member(2, 1, 3)
    assert "Cannot remove member who is involved in expenses" in str(
        exc_info.value)


def test_cannot_remove_member_from_nonexistent_group(app_with_sample_data):
    """Test cannot remove member from nonexistent group"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError) as exc_info:
        app.remove_group_member(999, 1, 1)
    assert "Group with ID 999 not found" in str(exc_info.value)


def test_cannot_remove_nonexistent_member_from_group(app_with_sample_data):
    """Test cannot remove nonexistent member from group"""
    app = app_with_sample_data

    # Group 1: members [1, 2] (Alice, Bob). Try to remove user 3 (Charlie)
    # who is not a member.
    with pytest.raises(GroupNotFoundError) as exc_info:
        app.remove_group_member(1, 3, 1)
    assert "User with ID 3 not found in this group" in str(exc_info.value)


def test_non_member_cannot_remove_member_from_group(app_with_sample_data):
    """Test non-member cannot remove member from group"""
    app = app_with_sample_data

    # Group 1: members [1, 2] (Alice, Bob). User 3 (Charlie) is not a
    # member, tries to remove user 2 (Bob).
    with pytest.raises(ForbiddenError) as exc_info:
        app.remove_group_member(1, 2, 3)
    assert "You do not have access to this group" in str(exc_info.value)


# ============================================================================
# get_group_expenses Tests
# ============================================================================

def test_get_group_expenses_returns_empty_list_when_no_expenses(app_with_sample_data):
    """Test get_group_expenses returns empty list when group has no expenses"""
    app = app_with_sample_data
    # Group 1 (weekend_trip) has no expenses, user 1 (Alice) is a member
    expenses = app.get_group_expenses(1, 1)
    assert expenses == []


def test_get_group_expenses_returns_single_expense(app_with_sample_data):
    """Test get_group_expenses returns single expense when group has one expense"""
    app = app_with_sample_data
    # Group 3 has one expense (team_lunch), user 5 (Eve) is a member
    expenses = app.get_group_expenses(3, 5)
    assert_expenses_are(expenses, ["team_lunch"])
    # Team lunch: $45.67 split between 2 people = $22.84 (rounded)
    assert expenses[0].per_person_amount == 22.84


def test_get_group_expenses_returns_multiple_expenses(app_with_sample_data):
    """Test get_group_expenses returns multiple expenses when group has multiple expenses"""
    app = app_with_sample_data
    # Group 2 has 4 expenses, user 1 (Alice) is a member
    expenses = app.get_group_expenses(2, 1)
    assert_expenses_are(expenses, ["grocery_shopping", "utilities_bill",
                                   "restaurant_dinner", "internet_bill"])


def test_get_group_expenses_calculates_per_person_amount(app_with_sample_data):
    """Test get_group_expenses calculates per_person_amount correctly"""
    app = app_with_sample_data
    expenses = app.get_group_expenses(2, 1)

    # First expense: Grocery shopping $86.40 split between 2 people = $43.20
    assert expenses[0].per_person_amount == 43.20

    # Second expense: Utilities bill $120.00 split between 2 people = $60.00
    assert expenses[1].per_person_amount == 60.00

    # Third expense: Restaurant dinner $67.89 split between 2 people = $33.95 (rounded)
    assert expenses[2].per_person_amount == 33.95

    # Fourth expense: Internet bill $100.00 split between 3 people = $33.33 (rounded)
    assert expenses[3].per_person_amount == 33.33


def test_get_group_expenses_handles_rounding_correctly(app_with_sample_data):
    """Test get_group_expenses handles rounding correctly (e.g., $100 / 3 = $33.33)"""
    app = app_with_sample_data
    expenses = app.get_group_expenses(2, 1)

    # Internet bill: $100.00 / 3 = $33.333... rounded to $33.33
    internet_bill = [e for e in expenses if e.id == 4][0]
    assert internet_bill.per_person_amount == 33.33
    assert len(internet_bill.split_between) == 3


def test_get_group_expenses_raises_group_not_found_error(app_with_sample_data):
    """Test get_group_expenses raises GroupNotFoundError when group doesn't exist"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError) as exc_info:
        app.get_group_expenses(999, 1)
    assert "Group with ID 999 not found" in str(exc_info.value)


def test_get_group_expenses_raises_forbidden_error_for_non_member(app_with_sample_data):
    """Test get_group_expenses raises ForbiddenError when user is not a member"""
    app = app_with_sample_data

    # User 2 (Bob) is not a member of group 2 (Roommates Spring 2025)
    with pytest.raises(ForbiddenError) as exc_info:
        app.get_group_expenses(2, 2)
    assert "You do not have access to this group" in str(exc_info.value)


def test_get_group_expenses_with_many_participants(app_with_sample_data):
    """Test get_group_expenses correctly calculates per_person_amount with many participants"""
    app = app_with_sample_data
    # Group 4 has expenses, user 8 (Helen) is a member
    expenses = app.get_group_expenses(4, 8)

    # Textbooks expense: $250.00 split between 5 people = $50.00
    textbooks_expense = [e for e in expenses if e.id == 6][0]
    assert textbooks_expense.per_person_amount == 50.00
    assert_expense_participants(textbooks_expense, [8, 9, 10, 11, 2])


def test_get_group_expenses_all_expenses_have_per_person_amount(app_with_sample_data):
    """Test get_group_expenses ensures all expenses have per_person_amount calculated"""
    app = app_with_sample_data
    expenses = app.get_group_expenses(2, 1)

    # All expenses should have per_person_amount calculated (not None)
    for expense in expenses:
        assert expense.per_person_amount is not None
        assert isinstance(expense.per_person_amount, float)
        assert expense.per_person_amount > 0


# ============================================================================
# create_expense Tests
# ============================================================================

def test_create_expense_success(app_with_sample_data):
    """Test create_expense successfully creates expense with single participant"""
    app = app_with_sample_data
    # Group 1 (weekend_trip) has no expenses, members are [1, 2] (Alice, Bob)
    # User 1 (Alice) creates an expense for herself

    expense_request = TEST_EXPENSE_REQUESTS["hotel_room"]
    expense = app.create_expense(expense_request)

    assert expense.group_id == 1
    assert expense.description == "Hotel room"
    assert expense.amount == 125.50
    assert expense.date == "2025-02-15"
    assert_user_is(expense.paid_by, "alice")
    assert len(expense.split_between) == 1
    assert expense.split_between[0].id == 1
    assert expense.per_person_amount == 125.50


def test_create_expense_with_multiple_participants(app_with_sample_data):
    """Test create_expense successfully creates expense with multiple participants"""
    app = app_with_sample_data
    # Group 2 (roommates) has members [3, 1, 4] (Charlie, Alice, David)
    # User 3 (Charlie) creates an expense split between all three

    expense_request = TEST_EXPENSE_REQUESTS["new_expense_group2_100"]
    expense = app.create_expense(expense_request)

    assert expense.amount == 100.00
    assert len(expense.split_between) == 3
    assert expense.per_person_amount == 33.33  # 100.00 / 3 rounded to 2 decimals


def test_create_expense_calculates_per_person_amount(app_with_sample_data):
    """Test create_expense calculates per_person_amount correctly"""
    app = app_with_sample_data
    # Group 1 (weekend_trip) has members [1, 2] (Alice, Bob)
    # User 1 (Alice) creates an expense split between both

    expense_request = TEST_EXPENSE_REQUESTS["split_expense_group1"]
    expense = app.create_expense(expense_request)

    assert expense.per_person_amount == 43.20  # 86.40 / 2


def test_create_expense_raises_group_not_found_error(app_with_sample_data):
    """Test create_expense raises GroupNotFoundError when group doesn't exist"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError) as exc_info:
        expense_request = TEST_EXPENSE_REQUESTS["bad_expense_group999"]
        app.create_expense(expense_request)
    assert "Group with ID 999 not found" in str(exc_info.value)


def test_create_expense_raises_forbidden_error_for_non_member(app_with_sample_data):
    """Test create_expense raises ForbiddenError when user is not a member"""
    app = app_with_sample_data

    # User 2 (Bob) is not a member of group 2 (roommates)
    with pytest.raises(ForbiddenError) as exc_info:
        expense_request = TEST_EXPENSE_REQUESTS["test_expense_user2_payer"]
        app.create_expense(expense_request)
    assert "You do not have access to this group" in str(exc_info.value)


def test_create_expense_raises_validation_error_for_empty_split_between(app_with_sample_data):
    """Test create_expense raises ValidationError when split_between is empty"""
    app = app_with_sample_data

    with pytest.raises(ValidationError) as exc_info:
        expense_request = TEST_EXPENSE_REQUESTS["test_expense_empty_participants"]
        app.create_expense(expense_request)
    assert "splitBetween must contain at least one user ID" in str(exc_info.value)


def test_create_expense_raises_validation_error_user_not_in_split_between(app_with_sample_data):
    """Test create_expense raises ValidationError when user is not in split_between"""
    app = app_with_sample_data

    # User 1 (Alice) is a member of group 2, but try to create expense without including her
    with pytest.raises(ValidationError) as exc_info:
        expense_request = TEST_EXPENSE_REQUESTS["test_expense_only_charlie"]
        app.create_expense(expense_request)
    assert "splitBetween must include the authenticated user's ID " in str(exc_info.value)


def test_create_expense_raises_validation_error_invalid_participant(app_with_sample_data):
    """Test create_expense raises ValidationError when participant is not a group member"""
    app = app_with_sample_data

    # User 1 (Alice) is a member of group 2, but user 2 (Bob) is not
    with pytest.raises(ValidationError) as exc_info:
        expense_request = TEST_EXPENSE_REQUESTS["test_expense_with_bob"]
        app.create_expense(expense_request)
    assert "All users in splitBetween must be members of the group" in str(exc_info.value)


# ============================================================================
# get_expense_by_id Tests
# ============================================================================

def test_get_expense_by_id_succeeds(app_with_sample_data):
    """Test get_expense_by_id returns expense for member"""
    app = app_with_sample_data
    # User 1 (Alice) is a member of group 2, expense 1 exists
    expense = app.get_expense_by_id(1, 2, 1)
    assert expense.id == 1
    assert expense.description == "Grocery shopping"
    assert expense.amount == 86.40
    assert expense.per_person_amount is not None
    assert expense.per_person_amount == 43.20


def test_get_expense_by_id_calculates_per_person_amount(app_with_sample_data):
    """Test get_expense_by_id calculates per_person_amount correctly"""
    app = app_with_sample_data
    # Expense 4 (internet_bill) is $100.00 split 3 ways = $33.33
    expense = app.get_expense_by_id(4, 2, 1)
    assert expense.per_person_amount == 33.33


def test_get_expense_by_id_raises_expense_not_found_error(app_with_sample_data):
    """Test get_expense_by_id raises ExpenseNotFoundError for invalid expense"""
    app = app_with_sample_data
    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 999 not found"):
        app.get_expense_by_id(999, 2, 1)


def test_get_expense_by_id_raises_group_not_found_error(app_with_sample_data):
    """Test get_expense_by_id raises GroupNotFoundError for invalid group"""
    app = app_with_sample_data
    with pytest.raises(GroupNotFoundError,
                      match="Group with ID 999 not found"):
        app.get_expense_by_id(1, 999, 1)


def test_get_expense_by_id_raises_forbidden_error_for_non_member(
        app_with_sample_data):
    """Test get_expense_by_id raises ForbiddenError for non-member"""
    app = app_with_sample_data
    # User 2 (Bob) is NOT a member of group 2
    with pytest.raises(ForbiddenError, match="You do not have access"):
        app.get_expense_by_id(1, 2, 2)


def test_get_expense_by_id_raises_error_when_expense_not_in_group(
        app_with_sample_data):
    """Test get_expense_by_id raises ExpenseNotFoundError when expense
    belongs to different group"""
    app = app_with_sample_data
    # Expense 1 belongs to group 2, but we're querying group 1
    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 1 not found"):
        app.get_expense_by_id(1, 1, 1)


# ============================================================================
# update_expense Tests
# ============================================================================

def test_update_expense_succeeds(app_with_sample_data):
    """Test update_expense successfully updates expense when user is payer"""
    app = app_with_sample_data
    # User 1 (Alice) paid for expense 2 (utilities_bill)
    expense_request = TEST_EXPENSE_REQUESTS["updated_utilities_bill"]

    updated_expense = app.update_expense(2, 2, 1, expense_request)

    assert updated_expense.id == 2
    assert updated_expense.description == "Updated utilities bill"
    assert updated_expense.amount == 125.00
    assert updated_expense.date == "2025-01-16"
    assert updated_expense.per_person_amount is not None
    assert updated_expense.per_person_amount == 62.50


def test_update_expense_calculates_per_person_amount(app_with_sample_data):
    """Test update_expense calculates per_person_amount correctly"""
    app = app_with_sample_data
    # User 1 (Alice) paid for expense 4 (internet_bill), update to 2 participants
    expense_request = TEST_EXPENSE_REQUESTS["updated_internet_bill"]

    updated_expense = app.update_expense(4, 2, 1, expense_request)

    assert updated_expense.per_person_amount == 50.00


def test_update_expense_raises_forbidden_error_when_not_payer(
        app_with_sample_data):
    """Test update_expense raises ForbiddenError when user is not the payer"""
    app = app_with_sample_data
    # User 1 (Alice) tries to update expense 1 (grocery_shopping)
    # which was paid by user 3 (Charlie)
    expense_request = TEST_EXPENSE_REQUESTS["updated_description"]

    with pytest.raises(ForbiddenError,
                      match="Only the person who paid for this expense"):
        app.update_expense(1, 2, 1, expense_request)


def test_update_expense_raises_group_not_found_error(app_with_sample_data):
    """Test update_expense raises GroupNotFoundError for invalid group"""
    app = app_with_sample_data
    expense_request = TEST_EXPENSE_REQUESTS["bad_expense_group999"]

    with pytest.raises(GroupNotFoundError,
                      match="Group with ID 999 not found"):
        app.update_expense(1, 999, 1, expense_request)


def test_update_expense_raises_forbidden_error_for_non_member(
        app_with_sample_data):
    """Test update_expense raises ForbiddenError for non-member"""
    app = app_with_sample_data
    # User 2 (Bob) is NOT a member of group 2
    expense_request = TEST_EXPENSE_REQUESTS["test_expense_user2_payer"]

    with pytest.raises(ForbiddenError, match="You do not have access"):
        app.update_expense(1, 2, 2, expense_request)


def test_update_expense_raises_expense_not_found_error(app_with_sample_data):
    """Test update_expense raises ExpenseNotFoundError for invalid expense"""
    app = app_with_sample_data
    expense_request = TEST_EXPENSE_REQUESTS["test_expense_group2"]

    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 999 not found"):
        app.update_expense(999, 2, 1, expense_request)


def test_update_expense_raises_error_when_expense_not_in_group(
        app_with_sample_data):
    """Test update_expense raises ExpenseNotFoundError when expense
    belongs to different group"""
    app = app_with_sample_data
    # Expense 1 (grocery_shopping) belongs to group 2, but we're updating with group_id=1
    # User 1 (Alice) is a member of both group 1 and group 2
    expense_request = TEST_EXPENSE_REQUESTS["test_expense_group2"]

    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 1 not found"):
        app.update_expense(1, 1, 1, expense_request)


def test_update_expense_raises_validation_error_for_empty_split_between(
        app_with_sample_data):
    """Test update_expense raises ValidationError when split_between is empty"""
    app = app_with_sample_data
    expense_request = TEST_EXPENSE_REQUESTS["test_expense_empty_participants"]

    with pytest.raises(ValidationError) as exc_info:
        app.update_expense(2, 2, 1, expense_request)
    assert "splitBetween must contain at least one user ID" in str(exc_info.value)


def test_update_expense_raises_validation_error_user_not_in_split_between(
        app_with_sample_data):
    """Test update_expense raises ValidationError when user not in split_between"""
    app = app_with_sample_data
    # User 1 (Alice) tries to update expense but doesn't include herself
    expense_request = TEST_EXPENSE_REQUESTS["test_expense_only_charlie"]

    with pytest.raises(ValidationError) as exc_info:
        app.update_expense(2, 2, 1, expense_request)
    assert "splitBetween must include the authenticated user's ID" in str(exc_info.value)


def test_update_expense_raises_validation_error_invalid_participant(
        app_with_sample_data):
    """Test update_expense raises ValidationError when participant is not a group member"""
    app = app_with_sample_data
    # User 1 (Alice) is a member of group 2, but user 2 (Bob) is not
    expense_request = TEST_EXPENSE_REQUESTS["test_expense_with_bob"]

    with pytest.raises(ValidationError) as exc_info:
        app.update_expense(2, 2, 1, expense_request)
    assert "All users in splitBetween must be members of the group" in str(exc_info.value)


# ============================================================================
# delete_expense Tests
# ============================================================================

def test_delete_expense_succeeds(app_with_sample_data):
    """Test delete_expense successfully deletes expense when user is payer"""
    app = app_with_sample_data
    # User 1 (Alice) paid for expense 2 (utilities_bill)

    app.delete_expense(2, 2, 1)

    # Verify expense was deleted by trying to retrieve it
    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 2 not found"):
        app.get_expense_by_id(2, 2, 1)


def test_delete_expense_removes_expense_from_group_expenses(app_with_sample_data):
    """Test delete_expense removes expense from group expenses list"""
    app = app_with_sample_data
    # User 3 (Charlie) paid for expense 1 (grocery_shopping)

    app.delete_expense(1, 2, 3)

    # Verify expense is no longer in group expenses
    expenses = app.get_group_expenses(2, 1)
    expense_ids = [e.id for e in expenses]
    assert 1 not in expense_ids


def test_delete_expense_raises_forbidden_error_when_not_payer(
        app_with_sample_data):
    """Test delete_expense raises ForbiddenError when user is not the payer"""
    app = app_with_sample_data
    # User 1 (Alice) tries to delete expense 1 (grocery_shopping)
    # which was paid by user 3 (Charlie)

    with pytest.raises(ForbiddenError,
                      match="Only the person who paid for this expense"):
        app.delete_expense(1, 2, 1)


def test_delete_expense_raises_group_not_found_error(app_with_sample_data):
    """Test delete_expense raises GroupNotFoundError for invalid group"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError,
                      match="Group with ID 999 not found"):
        app.delete_expense(1, 999, 3)


def test_delete_expense_raises_forbidden_error_for_non_member(
        app_with_sample_data):
    """Test delete_expense raises ForbiddenError for non-member"""
    app = app_with_sample_data
    # User 2 (Bob) is NOT a member of group 2

    with pytest.raises(ForbiddenError, match="You do not have access"):
        app.delete_expense(1, 2, 2)


def test_delete_expense_raises_expense_not_found_error(app_with_sample_data):
    """Test delete_expense raises ExpenseNotFoundError for invalid expense"""
    app = app_with_sample_data

    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 999 not found"):
        app.delete_expense(999, 2, 1)


def test_delete_expense_raises_error_when_expense_not_in_group(
        app_with_sample_data):
    """Test delete_expense raises ExpenseNotFoundError when expense
    belongs to different group"""
    app = app_with_sample_data
    # Expense 1 (grocery_shopping) belongs to group 2, but we're deleting with group_id=1
    # User 1 (Alice) is a member of both group 1 and group 2

    with pytest.raises(ExpenseNotFoundError,
                      match="Expense with ID 1 not found"):
        app.delete_expense(1, 1, 1)


# ============================================================================
# delete_group Tests
# ============================================================================

def test_delete_group_succeeds(app_with_sample_data):
    """Test delete_group successfully deletes group when no expenses exist"""
    app = app_with_sample_data
    # Group 1 (weekend_trip) has no expenses and user 1 (Alice) is a member

    app.delete_group(1, 1)

    # Verify group was deleted by trying to retrieve it
    with pytest.raises(GroupNotFoundError,
                      match="Group with ID 1 not found"):
        app.get_group_by_id(1, 1)


def test_delete_group_raises_conflict_error_when_expenses_exist(app_with_sample_data):
    """Test delete_group raises ConflictError when group has expenses"""
    app = app_with_sample_data
    # Group 2 (roommates) has expenses

    with pytest.raises(ConflictError,
                      match="Cannot delete group with existing expenses"):
        app.delete_group(2, 1)


def test_delete_group_raises_group_not_found_error(app_with_sample_data):
    """Test delete_group raises GroupNotFoundError for invalid group"""
    app = app_with_sample_data

    with pytest.raises(GroupNotFoundError,
                      match="Group with ID 999 not found"):
        app.delete_group(999, 1)


def test_delete_group_raises_forbidden_error_for_non_member(app_with_sample_data):
    """Test delete_group raises ForbiddenError for non-member"""
    app = app_with_sample_data
    # User 3 (Charlie) is NOT a member of group 1

    with pytest.raises(ForbiddenError, match="You do not have access"):
        app.delete_group(1, 3)
