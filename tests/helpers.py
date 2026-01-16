"""
Test helper functions and sample data constants for assertions.

This module provides:
1. SAMPLE_USERS, SAMPLE_GROUPS, SAMPLE_EXPENSES constants matching the sample data
2. SAMPLE_EXPENSE_PARTICIPANTS and SAMPLE_GROUP_MEMBERS for relationships
3. Helper assertion functions for users, groups, expenses, and relationships
4. JSON response assertion helpers for API tests
5. Test data factory functions for creating test objects

The sample data is defined in src/cost_sharing/sql/sample-data.sql and fully
documented in docs/sample-dataset.md. These constants serve as the single source
of truth for expected values in tests, avoiding duplication.

Usage in tests:
    from helpers import (
        assert_user_is, assert_groups_are, assert_expenses_are,
        assert_expense_participants, assert_group_members,
        assert_user_json, assert_groups_json_response,
        assert_error_response
    )
    assert_user_is(user, "alice")
    assert_groups_are(groups, ["weekend_trip", "roommates"])
    assert_expenses_are(expenses, ["grocery_shopping", "utilities_bill"])
    assert_expense_participants(expense, [1, 2])
    assert_group_members(2, [3, 1, 4])
    data = assert_groups_json_response(response, expected_status=200)
"""

from cost_sharing.models import UserRequest, ExpenseRequest

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


# disable because it is test code, and lots of arguments is ok
def assert_group_matches(group, group_id, name, description, creator_user, expected_member_count=1): # pylint: disable=R0913 R0917
    """
    Assert group matches expected values for newly created groups.

    Args:
        group: Group object to check
        group_id: Expected group ID
        name: Expected group name
        description: Expected group description
        creator_user: User object for expected creator
        expected_member_count: Expected number of members (default: 1)
    """
    assert group.id == group_id, \
        f"Expected group ID {group_id}, got {group.id}"
    assert group.name == name, \
        f"Expected group name '{name}', got '{group.name}'"
    assert group.description == description, \
        f"Expected description '{description}', got '{group.description}'"
    assert_user_matches(group.created_by, creator_user.id,
                        creator_user.email, creator_user.name)
    assert len(group.members) == expected_member_count, \
        f"Expected {expected_member_count} members, got {len(group.members)}"


def assert_group_is(group, group_key):  # pylint: disable=R0914
    """
    Assert group matches expected group from sample data.
    
    Args:
        group: Group object to check
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

    # Check member count matches expected
    expected_member_count = expected["member_count"]
    assert len(group.members) == expected_member_count, \
        f"Expected member_count {expected_member_count}, got {len(group.members)}"

    # Check that creator is correct
    # Creator IDs: 1->1, 2->3, 3->5, 4->8, 5->9, 6->10
    creator_ids = {1: 1, 2: 3, 3: 5, 4: 8, 5: 9, 6: 10}
    expected_creator_id = creator_ids[group.id]
    assert group.created_by.id == expected_creator_id, \
        f"Expected creator ID {expected_creator_id}, got {group.created_by.id}"

    # Check that all expected members are present
    expected_member_ids = sorted(SAMPLE_GROUP_MEMBERS[group.id])
    actual_member_ids = sorted([member.id for member in group.members])
    assert actual_member_ids == expected_member_ids, \
        f"Expected member IDs {expected_member_ids}, got {actual_member_ids}"


def assert_groups_are(groups, group_keys):
    """
    Assert list of groups matches expected groups from sample data.
    
    Args:
        groups: List of Group objects to check
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
    assert expense.group_id == expected["group_id"], \
        f"Expected group_id {expected['group_id']}, got {expense.group_id}"
    assert expense.description == expected["description"], \
        f"Expected description '{expected['description']}', got '{expense.description}'"
    assert expense.amount == expected["amount"], \
        f"Expected amount {expected['amount']}, got {expense.amount}"
    assert expense.date == expected["expense_date"], \
        f"Expected date {expected['expense_date']}, got {expense.date}"

    # Check paid_by user
    assert expense.paid_by.id == expected["paid_by_user_id"], \
        f"Expected paid_by user ID {expected['paid_by_user_id']}, got {expense.paid_by.id}"

    # Check split_between participants
    expected_participants = SAMPLE_EXPENSE_PARTICIPANTS[expected["id"]]
    actual_participant_ids = sorted([user.id for user in expense.split_between])
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
    Assert expense split_between matches expected user IDs.
    
    Args:
        expense: Expense object to check
        expected_user_ids: List of expected user IDs in split_between
    """
    actual_user_ids = sorted([user.id for user in expense.split_between])
    expected_sorted = sorted(expected_user_ids)
    assert actual_user_ids == expected_sorted, \
        f"Expected splitBetween user IDs {expected_sorted}, got {actual_user_ids}"


def assert_expense_matches_retrieved(created_expense, expenses_list):
    """
    Assert that an expense returned from create_expense matches the expense
    retrieved from get_group_expenses by ID.
    
    This verifies that the expense was correctly persisted to the database
    and can be retrieved.
    
    Args:
        created_expense: Expense object returned from create_expense
        expenses_list: List of Expense objects from get_group_expenses
    """
    # Find the expense in the list by ID
    matching_expense = None
    for expense in expenses_list:
        if expense.id == created_expense.id:
            matching_expense = expense
            break

    assert matching_expense is not None, \
        f"Expense with ID {created_expense.id} not found in retrieved expenses"

    # Verify all fields match
    assert matching_expense.id == created_expense.id, \
        f"Expense ID mismatch: {created_expense.id} vs {matching_expense.id}"
    assert matching_expense.group_id == created_expense.group_id, \
        f"Group ID mismatch: {created_expense.group_id} vs {matching_expense.group_id}"
    assert matching_expense.description == created_expense.description, \
        f"Description mismatch: '{created_expense.description}' vs '{matching_expense.description}'"
    assert matching_expense.amount == created_expense.amount, \
        f"Amount mismatch: {created_expense.amount} vs {matching_expense.amount}"
    assert matching_expense.date == created_expense.date, \
        f"Date mismatch: '{created_expense.date}' vs '{matching_expense.date}'"

    # Verify paid_by user
    assert matching_expense.paid_by.id == created_expense.paid_by.id, \
        (f"Paid by user ID mismatch: {created_expense.paid_by.id} vs "
         f"{matching_expense.paid_by.id}")
    assert matching_expense.paid_by.email == created_expense.paid_by.email, \
        (f"Paid by email mismatch: '{created_expense.paid_by.email}' vs "
         f"'{matching_expense.paid_by.email}'")
    assert matching_expense.paid_by.name == created_expense.paid_by.name, \
        (f"Paid by name mismatch: '{created_expense.paid_by.name}' vs "
         f"'{matching_expense.paid_by.name}'")

    # Verify split_between participants
    created_participant_ids = sorted([user.id for user in created_expense.split_between])
    retrieved_participant_ids = sorted([user.id for user in matching_expense.split_between])
    assert retrieved_participant_ids == created_participant_ids, \
        (f"Split between mismatch: {created_participant_ids} vs "
         f"{retrieved_participant_ids}")

    # Verify per_person_amount (should both be None in storage layer)
    assert matching_expense.per_person_amount == created_expense.per_person_amount, \
        (f"Per person amount mismatch: {created_expense.per_person_amount} vs "
         f"{matching_expense.per_person_amount}")


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


def assert_group_has_members(group, expected_member_ids):
    """
    Assert group has the expected members.
    
    Args:
        group: Group object to check
        expected_member_ids: List of expected member user IDs
    """
    actual_member_ids = sorted([member.id for member in group.members])
    expected_sorted = sorted(expected_member_ids)
    assert actual_member_ids == expected_sorted, \
        f"Expected group {group.id} members {expected_sorted}, got {actual_member_ids}"


# ============================================================================
# JSON Response Assertion Helpers
# ============================================================================

def assert_user_json(user_json, user_id, email, name):
    """
    Assert JSON user object matches expected values.

    Args:
        user_json: JSON user object from API response
        user_id: Expected user ID
        email: Expected email
        name: Expected name
    """
    assert user_json['id'] == user_id, \
        f"Expected user ID {user_id}, got {user_json.get('id')}"
    assert user_json['email'] == email, \
        f"Expected email {email}, got {user_json.get('email')}"
    assert user_json['name'] == name, \
        f"Expected name {name}, got {user_json.get('name')}"



def assert_groups_json_response(response, expected_status=200):
    """
    Assert GET /groups response structure and status.

    Args:
        response: Flask response object
        expected_status: Expected HTTP status code (default: 200)

    Returns:
        Parsed JSON data from response
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    data = response.get_json()
    assert isinstance(data, dict), f"Response should be dict, got {type(data)}"
    assert 'groups' in data, "Response missing 'groups' field"
    assert isinstance(data['groups'], list), \
        f"groups should be a list, got {type(data['groups'])}"
    return data


def assert_group_json_is(group_json, group_key):  # pylint: disable=R0914
    """
    Assert JSON group object matches expected group from sample data.
    
    Args:
        group_json: JSON group object from API response
        group_key: Key from SAMPLE_GROUPS (e.g., "weekend_trip", "roommates")
    """
    expected = SAMPLE_GROUPS[group_key]
    assert group_json['id'] == expected["id"], \
        f"Expected group ID {expected['id']}, got {group_json.get('id')}"
    assert group_json['name'] == expected["name"], \
        f"Expected group name '{expected['name']}', got {group_json.get('name')}"
    expected_desc = expected["description"] or ""
    assert group_json['description'] == expected_desc, \
        f"Expected group description '{expected_desc}', got {group_json.get('description')}"

    # Check member count matches expected
    expected_member_count = expected["member_count"]
    assert len(group_json['members']) == expected_member_count, \
        f"Expected member_count {expected_member_count}, got {len(group_json['members'])}"

    # Check that creator is correct
    # Creator IDs: 1->1, 2->3, 3->5, 4->8, 5->9, 6->10
    creator_ids = {1: 1, 2: 3, 3: 5, 4: 8, 5: 9, 6: 10}
    expected_creator_id = creator_ids[group_json['id']]
    assert group_json['createdBy']['id'] == expected_creator_id, \
        f"Expected creator ID {expected_creator_id}, got {group_json['createdBy'].get('id')}"

    # Check that all expected members are present
    expected_member_ids = sorted(SAMPLE_GROUP_MEMBERS[group_json['id']])
    actual_member_ids = sorted([member['id'] for member in group_json['members']])
    assert actual_member_ids == expected_member_ids, \
        f"Expected member IDs {expected_member_ids}, got {actual_member_ids}"


def assert_json_response(response, expected_status=200):
    """
    Assert JSON response status and return parsed data.

    Args:
        response: Flask response object
        expected_status: Expected HTTP status code (default: 200)

    Returns:
        Parsed JSON data from response
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    data = response.get_json()
    assert isinstance(data, dict), f"Response should be dict, got {type(data)}"
    return data


def assert_error_response(response, expected_status, expected_error, expected_message=None):
    """
    Assert error response structure.

    Args:
        response: Flask response object
        expected_status: Expected HTTP status code
        expected_error: Expected error type string
        expected_message: Optional expected error message
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    data = response.get_json()
    assert isinstance(data, dict), f"Response should be dict, got {type(data)}"
    assert data['error'] == expected_error, \
        f"Expected error '{expected_error}', got '{data.get('error')}'"
    if expected_message:
        assert data['message'] == expected_message, \
            f"Expected message '{expected_message}', got '{data.get('message')}'"


def assert_auth_me_response(response, user_id, email, name):
    """
    Assert /auth/me response matches expected user.

    Args:
        response: Flask response object
        user_id: Expected user ID
        email: Expected email
        name: Expected name
    """
    assert response.status_code == 200, \
        f"Expected status 200, got {response.status_code}"
    data = response.get_json()
    assert_user_json(data, user_id, email, name)


def assert_auth_callback_response(response, expected_token, user_id, email, name):
    """
    Assert /auth/callback response structure.

    Args:
        response: Flask response object
        expected_token: Expected JWT token string
        user_id: Expected user ID
        email: Expected email
        name: Expected name
    """
    assert response.status_code == 200, \
        f"Expected status 200, got {response.status_code}"
    data = response.get_json()
    assert isinstance(data, dict), f"Response should be dict, got {type(data)}"
    assert 'token' in data, "Response missing 'token' field"
    assert data['token'] == expected_token, \
        f"Expected token '{expected_token}', got '{data.get('token')}'"
    assert 'user' in data, "Response missing 'user' field"
    assert_user_json(data['user'], user_id, email, name)


def assert_validation_error_response(response, expected_message):
    """
    Assert validation error response structure.

    Args:
        response: Flask response object
        expected_message: Expected error message
    """
    assert_error_response(response, 400, "Validation failed", expected_message)


# ============================================================================
# Test Request Objects (Constants)
# ============================================================================
# These constants correspond to the sample data defined above (SAMPLE_USERS,
# SAMPLE_GROUPS, SAMPLE_EXPENSES, SAMPLE_EXPENSE_PARTICIPANTS, etc.)
# Refer to those constants to understand the relationships and test scenarios
# covered by these request objects.
# ============================================================================

# UserRequest objects matching sample data users
# Keys match SAMPLE_USERS dictionary for consistency
SAMPLE_USER_REQUESTS = {
    "alice": UserRequest(email="alice@school.edu", name="Alice"),
    "bob": UserRequest(email="bob@school.edu", name="Bob"),
    "charlie": UserRequest(email="charlie@school.edu", name="Charlie"),
    "david": UserRequest(email="david@school.edu", name="David"),
    "eve": UserRequest(email="eve@school.edu", name="Eve"),
    "frank": UserRequest(email="frank@school.edu", name="Frank"),
    "george": UserRequest(email="george@school.edu", name="George"),
    "helen": UserRequest(email="helen@school.edu", name="Helen"),
    "iris": UserRequest(email="iris@school.edu", name="Iris"),
    "jack": UserRequest(email="jack@school.edu", name="Jack"),
    "kate": UserRequest(email="kate@school.edu", name="Kate"),
}

# Test UserRequest objects for creating new test users
# These are used when tests need to create users that don't exist in sample data
TEST_USER_REQUESTS = {
    "test_user": UserRequest(email="test@example.com", name="Test User"),
    "new_user": UserRequest(email="newuser@example.com", name="New User"),
    "user1": UserRequest(email="user1@example.com", name="User One"),
    "user2": UserRequest(email="user2@example.com", name="User Two"),
    "user3": UserRequest(email="user3@example.com", name="User Three"),
    "another_user": UserRequest(
        email="test@example.com", name="Another User"
    ),
}

# GroupRequest constants
# Note: GroupRequest requires created_by_user_id which varies dynamically by test context.
# Therefore, GroupRequest objects must be created inline in tests when the creator_id
# is known. This is acceptable as group creation scenarios vary significantly.
# Standard patterns used in tests:
# - Test Group with description:
#     GroupRequest(name="Test Group", description="Test description", created_by_user_id=<user_id>)
# - Test Group without description:
#     GroupRequest(name="Test Group", description=None, created_by_user_id=<user_id>)
# - New Group:
#     GroupRequest(name="New Group", description="New description", created_by_user_id=<user_id>)

# ExpenseRequest objects matching sample data expenses
# Keys match SAMPLE_EXPENSES dictionary for consistency
# Participants match SAMPLE_EXPENSE_PARTICIPANTS
SAMPLE_EXPENSE_REQUESTS = {
    "grocery_shopping": ExpenseRequest(
        group_id=2,
        description="Grocery shopping",
        amount=86.40,
        date="2025-01-10",
        paid_by_user_id=3,
        participant_user_ids=[3, 1]
    ),
    "utilities_bill": ExpenseRequest(
        group_id=2,
        description="Utilities bill",
        amount=120.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[3, 1]
    ),
    "restaurant_dinner": ExpenseRequest(
        group_id=2,
        description="Restaurant dinner",
        amount=67.89,
        date="2025-01-20",
        paid_by_user_id=4,
        participant_user_ids=[1, 4]
    ),
    "internet_bill": ExpenseRequest(
        group_id=2,
        description="Internet bill",
        amount=100.00,
        date="2025-01-25",
        paid_by_user_id=1,
        participant_user_ids=[3, 1, 4]
    ),
    "team_lunch": ExpenseRequest(
        group_id=3,
        description="Team lunch",
        amount=45.67,
        date="2025-02-01",
        paid_by_user_id=5,
        participant_user_ids=[5, 6]
    ),
}

# Test ExpenseRequest objects for creating new test expenses
# These are used when tests need to create expenses that don't exist in sample data
# Keys describe the purpose of each test expense
TEST_EXPENSE_REQUESTS = {
    # Standard test expenses
    "test_expense_group2": ExpenseRequest(
        group_id=2,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[1]
    ),
    "test_expense_group1": ExpenseRequest(
        group_id=1,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[1]
    ),
    "hotel_room": ExpenseRequest(
        group_id=1,
        description="Hotel room",
        amount=125.50,
        date="2025-02-15",
        paid_by_user_id=1,
        participant_user_ids=[1]
    ),
    "split_expense_group1": ExpenseRequest(
        group_id=1,
        description="Split expense",
        amount=86.40,
        date="2025-03-05",
        paid_by_user_id=1,
        participant_user_ids=[1, 2]
    ),
    "gas_for_trip": ExpenseRequest(
        group_id=1,
        description="Gas for trip",
        amount=50.00,
        date="2025-03-01",
        paid_by_user_id=1,
        participant_user_ids=[1, 2]
    ),
    "new_expense_group2": ExpenseRequest(
        group_id=2,
        description="New expense",
        amount=25.50,
        date="2025-02-01",
        paid_by_user_id=3,
        participant_user_ids=[3, 1]
    ),
    "new_expense_group2_100": ExpenseRequest(
        group_id=2,
        description="New expense",
        amount=100.00,
        date="2025-02-01",
        paid_by_user_id=3,
        participant_user_ids=[3, 1, 4]
    ),
    "study_materials": ExpenseRequest(
        group_id=4,
        description="Study materials",
        amount=75.00,
        date="2025-03-10",
        paid_by_user_id=8,
        participant_user_ids=[8, 9, 10, 11]
    ),
    "office_supplies": ExpenseRequest(
        group_id=3,
        description="Office supplies",
        amount=30.25,
        date="2025-03-05",
        paid_by_user_id=5,
        participant_user_ids=[5]
    ),
    # Updated expenses for update testing
    "updated_utilities_bill": ExpenseRequest(
        group_id=2,
        description="Updated utilities bill",
        amount=125.00,
        date="2025-01-16",
        paid_by_user_id=1,
        participant_user_ids=[3, 1]
    ),
    "updated_grocery_shopping": ExpenseRequest(
        group_id=2,
        description="Updated grocery shopping",
        amount=95.50,
        date="2025-01-12",
        paid_by_user_id=3,
        participant_user_ids=[3, 1, 4]
    ),
    "updated_internet_bill": ExpenseRequest(
        group_id=2,
        description="Internet bill",
        amount=100.00,
        date="2025-01-25",
        paid_by_user_id=1,
        participant_user_ids=[1, 4]
    ),
    "updated_description": ExpenseRequest(
        group_id=2,
        description="Updated description",
        amount=90.00,
        date="2025-01-11",
        paid_by_user_id=1,
        participant_user_ids=[3, 1]
    ),
    "updated_utilities_bill_diff_payer": ExpenseRequest(
        group_id=2,
        description="Updated utilities bill",
        amount=125.00,
        date="2025-01-16",
        paid_by_user_id=3,  # Should be ignored in update
        participant_user_ids=[3, 1]
    ),
    "internet_bill_2_participants": ExpenseRequest(
        group_id=2,
        description="Internet bill",
        amount=100.00,
        date="2025-01-25",
        paid_by_user_id=1,
        participant_user_ids=[3, 1]  # Remove David from [3, 1, 4]
    ),
    # Error/validation test expenses
    "bad_expense_group999": ExpenseRequest(
        group_id=999,
        description="Bad expense",
        amount=10.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[1]
    ),
    "test_expense_user2_payer": ExpenseRequest(
        group_id=2,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=2,  # User 2 not a member of group 2
        participant_user_ids=[2]
    ),
    "test_expense_empty_participants": ExpenseRequest(
        group_id=2,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[]  # Empty participants for validation
    ),
    "test_expense_only_charlie": ExpenseRequest(
        group_id=2,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[3]  # Only Charlie, not Alice
    ),
    "test_expense_with_bob": ExpenseRequest(
        group_id=2,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[1, 2]  # Bob not a member of group 2
    ),
    "test_expense_invalid_payer": ExpenseRequest(
        group_id=1,
        description="Test expense",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=999,  # Invalid user ID
        participant_user_ids=[999]
    ),
    "test_failure": ExpenseRequest(
        group_id=1,
        description="Test failure",
        amount=50.00,
        date="2025-01-15",
        paid_by_user_id=1,
        participant_user_ids=[1]
    ),
}
