"""
Test helper functions and sample data constants for assertions.

This module provides:
1. SAMPLE_USERS, SAMPLE_GROUPS, SAMPLE_EXPENSES constants matching the sample data
2. SAMPLE_EXPENSE_PARTICIPANTS and SAMPLE_GROUP_MEMBERS for relationships
3. Helper assertion functions for users, groups, expenses, and relationships

The sample data is defined in src/cost_sharing/sql/sample-data.sql and fully
documented in docs/sample-dataset.md. These constants serve as the single source
of truth for expected values in tests, avoiding duplication.

Usage in tests:
    from helpers import (
        assert_user_is, assert_groups_are, assert_expenses_are,
        assert_expense_participants, assert_group_members
    )
    assert_user_is(user, "alice")
    assert_groups_are(groups, ["weekend_trip", "roommates"])
    assert_expenses_are(expenses, ["grocery_shopping", "utilities_bill"])
    assert_expense_participants(expense, [1, 2])
    assert_group_members(2, [3, 1, 4])
"""

# Sample data constants matching sample-data.sql
# These serve as the single source of truth for expected values in tests

SAMPLE_USERS = {
    "alice": {"id": 1, "email": "alice@school.edu", "name": "Alice"},
    "bob": {"id": 2, "email": "bob@school.edu", "name": "Bob"},
    "charlie": {"id": 3, "email": "charlie@school.edu", "name": "Charlie"},
    "david": {"id": 4, "email": "david@school.edu", "name": "David"},
    "eve": {"id": 5, "email": "eve@school.edu", "name": "Eve"},
    "frank": {"id": 6, "email": "frank@school.edu", "name": "Frank"},
    "george": {"id": 7, "email": "george@school.edu", "name": "George"},
    "helen": {"id": 8, "email": "helen@school.edu", "name": "Helen"},
    "iris": {"id": 9, "email": "iris@school.edu", "name": "Iris"},
    "jack": {"id": 10, "email": "jack@school.edu", "name": "Jack"},
    "kate": {"id": 11, "email": "kate@school.edu", "name": "Kate"},
}

SAMPLE_GROUPS = {
    "weekend_trip": {
        "id": 1,
        "name": "Weekend Trip Planning",
        "description": "Planning expenses for upcoming weekend getaway",
        "member_count": 2
    },
    "roommates": {
        "id": 2,
        "name": "Roommates Spring 2025",
        "description": "Shared expenses for apartment 4B",
        "member_count": 3
    },
    "project_team": {
        "id": 3,
        "name": "Project Team Expenses",
        "description": "Team project collaboration costs",
        "member_count": 2
    },
    "study_group": {
        "id": 4,
        "name": "Study Group Fall 2025",
        "description": "Shared costs for study materials and snacks for our weekly study sessions",
        "member_count": 5
    },
    "quick_split": {
        "id": 5,
        "name": "Quick Split",
        "description": None,
        "member_count": 2
    },
    "max_length": {
        "id": 6,
        "name": (
            "This is a group name that is exactly one hundred characters long to test "
            "maximum length validation  "
        ),
        "description": (
            "This is a group description that is exactly five hundred characters long "
            "to test the maximum length validation rule for group descriptions. "
            "It contains multiple sentences and demonstrates how the system handles "
            "descriptions at the upper limit of the allowed length. "
            "The description field can store up to 500 characters, and this example uses "
            "every single one of those characters to ensure proper validation and display "
            "handling. This is useful for testing edge cases in the user interface and "
            "API val"
        ),
        "member_count": 2
    },
}

SAMPLE_EXPENSES = {
    "grocery_shopping": {
        "id": 1,
        "group_id": 2,
        "description": "Grocery shopping",
        "amount": 86.40,
        "expense_date": "2025-01-10",
        "paid_by_user_id": 3,
    },
    "utilities_bill": {
        "id": 2,
        "group_id": 2,
        "description": "Utilities bill",
        "amount": 120.00,
        "expense_date": "2025-01-15",
        "paid_by_user_id": 1,
    },
    "restaurant_dinner": {
        "id": 3,
        "group_id": 2,
        "description": "Restaurant dinner",
        "amount": 67.89,
        "expense_date": "2025-01-20",
        "paid_by_user_id": 4,
    },
    "internet_bill": {
        "id": 4,
        "group_id": 2,
        "description": "Internet bill",
        "amount": 100.00,
        "expense_date": "2025-01-25",
        "paid_by_user_id": 1,
    },
    "team_lunch": {
        "id": 5,
        "group_id": 3,
        "description": "Team lunch",
        "amount": 45.67,
        "expense_date": "2025-02-01",
        "paid_by_user_id": 5,
    },
    "textbooks": {
        "id": 6,
        "group_id": 4,
        "description": "Textbooks",
        "amount": 250.00,
        "expense_date": "2025-02-05",
        "paid_by_user_id": 8,
    },
    "coffee_snacks": {
        "id": 7,
        "group_id": 4,
        "description": "Coffee and snacks",
        "amount": 35.50,
        "expense_date": "2025-02-10",
        "paid_by_user_id": 9,
    },
    "printing_costs": {
        "id": 8,
        "group_id": 4,
        "description": "Printing costs",
        "amount": 12.75,
        "expense_date": "2025-02-12",
        "paid_by_user_id": 10,
    },
    "group_dinner": {
        "id": 9,
        "group_id": 4,
        "description": "Group dinner",
        "amount": 125.33,
        "expense_date": "2025-02-15",
        "paid_by_user_id": 11,
    },
    "quick_expense": {
        "id": 10,
        "group_id": 5,
        "description": "Quick expense",
        "amount": 25.00,
        "expense_date": "2025-02-20",
        "paid_by_user_id": 9,
    },
    "max_length_expense": {
        "id": 11,
        "group_id": 6,
        "description": (
            "This is an expense description that is exactly two hundred "
            "characters long to test the maximum length validation rule for "
            "expense descriptions in the system. It demonstrates proper handling "
            "of edge ca"
        ),
        "amount": 50.00,
        "expense_date": "2025-02-25",
        "paid_by_user_id": 10,
    },
}

# Expense participants: maps expense_id to list of user_ids who split the expense
SAMPLE_EXPENSE_PARTICIPANTS = {
    1: [3, 1],  # Grocery shopping: Charlie, Alice
    2: [3, 1],  # Utilities bill: Charlie, Alice
    3: [1, 4],  # Restaurant dinner: Alice, David
    4: [3, 1, 4],  # Internet bill: Charlie, Alice, David
    5: [5, 6],  # Team lunch: Eve, Frank
    6: [8, 9, 10, 11, 2],  # Textbooks: Helen, Iris, Jack, Kate, Bob
    7: [9, 10, 11],  # Coffee and snacks: Iris, Jack, Kate
    8: [10, 11],  # Printing costs: Jack, Kate
    9: [8, 9, 10, 11, 2],  # Group dinner: Helen, Iris, Jack, Kate, Bob
    10: [9, 8],  # Quick expense: Iris, Helen
    11: [10, 11],  # Max length expense: Jack, Kate
}

# Group members: maps group_id to list of user_ids who are members
SAMPLE_GROUP_MEMBERS = {
    1: [1, 2],  # Weekend Trip Planning: Alice, Bob
    2: [3, 1, 4],  # Roommates Spring 2025: Charlie, Alice, David
    3: [5, 6],  # Project Team Expenses: Eve, Frank
    4: [8, 9, 10, 11, 2],  # Study Group Fall 2025: Helen, Iris, Jack, Kate, Bob
    5: [9, 8],  # Quick Split: Iris, Helen
    6: [10, 11],  # Max length group: Jack, Kate
}


def assert_user_is(user, user_key):
    """
    Assert user matches expected user from sample data.
    
    Args:
        user: User object to check
        user_key: Key from SAMPLE_USERS (e.g., "alice", "bob")
    """
    expected = SAMPLE_USERS[user_key]
    assert user.id == expected["id"], \
        f"Expected user ID {expected['id']}, got {user.id}"
    assert user.email == expected["email"], \
        f"Expected email {expected['email']}, got {user.email}"
    assert user.name == expected["name"], \
        f"Expected name {expected['name']}, got {user.name}"


def assert_user_matches(user, user_id, email, name):
    """
    Assert user matches specific values (for non-sample-data tests).
    
    Args:
        user: User object to check
        user_id: Expected user ID
        email: Expected email
        name: Expected name
    """
    assert user.id == user_id, f"Expected user ID {user_id}, got {user.id}"
    assert user.email == email, f"Expected email {email}, got {user.email}"
    assert user.name == name, f"Expected name {name}, got {user.name}"


def assert_group_is(group, group_key):
    """
    Assert group matches expected group from sample data.
    
    Args:
        group: GroupInfo object to check
        group_key: Key from SAMPLE_GROUPS (e.g., "weekend_trip", "roommates")
    """
    expected = SAMPLE_GROUPS[group_key]
    assert group.id == expected["id"], \
        f"Expected group ID {expected['id']}, got {group.id}"
    assert group.name == expected["name"], \
        f"Expected group name '{expected['name']}', got '{group.name}'"
    expected_desc = expected["description"] or ""
    assert group.description == expected_desc, \
        f"Expected group description '{expected_desc}', got '{group.description}'"
    assert group.member_count == expected["member_count"], \
        f"Expected member_count {expected['member_count']}, got {group.member_count}"


def assert_groups_are(groups, group_keys):
    """
    Assert list of groups matches expected groups from sample data.
    
    Args:
        groups: List of GroupInfo objects to check
        group_keys: List of keys from SAMPLE_GROUPS (e.g., ["weekend_trip", "roommates"])
    """
    assert len(groups) == len(group_keys), \
        f"Expected {len(group_keys)} groups, got {len(groups)}"
    for group, key in zip(groups, group_keys):
        assert_group_is(group, key)


def assert_expense_is(expense, expense_key):
    """
    Assert expense matches expected expense from sample data.
    
    Args:
        expense: Expense object to check
        expense_key: Key from SAMPLE_EXPENSES (e.g., "grocery_shopping", "utilities_bill")
    """
    expected = SAMPLE_EXPENSES[expense_key]
    assert expense.id == expected["id"], \
        f"Expected expense ID {expected['id']}, got {expense.id}"
    assert expense.groupId == expected["group_id"], \
        f"Expected group_id {expected['group_id']}, got {expense.groupId}"
    assert expense.description == expected["description"], \
        f"Expected description '{expected['description']}', got '{expense.description}'"
    assert expense.amount == expected["amount"], \
        f"Expected amount {expected['amount']}, got {expense.amount}"
    assert expense.date == expected["expense_date"], \
        f"Expected date {expected['expense_date']}, got {expense.date}"

    # Check paidBy user
    assert expense.paidBy.id == expected["paid_by_user_id"], \
        f"Expected paidBy user ID {expected['paid_by_user_id']}, got {expense.paidBy.id}"

    # Check splitBetween participants
    expected_participants = SAMPLE_EXPENSE_PARTICIPANTS[expected["id"]]
    actual_participant_ids = sorted([user.id for user in expense.splitBetween])
    expected_participant_ids = sorted(expected_participants)
    assert actual_participant_ids == expected_participant_ids, \
        f"Expected splitBetween user IDs {expected_participant_ids}, got {actual_participant_ids}"


def assert_expenses_are(expenses, expense_keys):
    """
    Assert list of expenses matches expected expenses from sample data.
    
    Args:
        expenses: List of Expense objects to check
        expense_keys: List of keys from SAMPLE_EXPENSES 
            (e.g., ["grocery_shopping", "utilities_bill"])
    """
    assert len(expenses) == len(expense_keys), \
        f"Expected {len(expense_keys)} expenses, got {len(expenses)}"
    for expense, key in zip(expenses, expense_keys):
        assert_expense_is(expense, key)


def assert_expense_participants(expense, expected_user_ids):
    """
    Assert expense splitBetween matches expected user IDs.
    
    Args:
        expense: Expense object to check
        expected_user_ids: List of expected user IDs in splitBetween
    """
    actual_user_ids = sorted([user.id for user in expense.splitBetween])
    expected_sorted = sorted(expected_user_ids)
    assert actual_user_ids == expected_sorted, \
        f"Expected splitBetween user IDs {expected_sorted}, got {actual_user_ids}"


def assert_group_members(group_id, actual_member_ids):
    """
    Assert group members match expected members from sample data.
    
    Args:
        group_id: Group ID to check
        actual_member_ids: List of actual member user IDs
    """
    expected_member_ids = sorted(SAMPLE_GROUP_MEMBERS[group_id])
    actual_sorted = sorted(actual_member_ids)
    assert actual_sorted == expected_member_ids, \
        f"Expected group {group_id} members {expected_member_ids}, got {actual_sorted}"
