# pylint: disable=C0302

import pytest
from oauth_handler_mock import OAuthHandlerMock
from helpers import (
    assert_groups_json_response, assert_json_response,
    assert_error_response, assert_auth_me_response,
    assert_auth_callback_response, assert_validation_error_response,
    assert_group_json_is
)
from cost_sharing.app import create_app
from cost_sharing.oauth_handler import (
    OAuthCodeError, OAuthVerificationError,
    TokenExpiredError, TokenInvalidError
)


@pytest.fixture(name='oauth_handler')
def create_oauth_handler():
    """Create OAuth handler mock for test configuration."""
    return OAuthHandlerMock()


@pytest.fixture(name='api_client')
def create_api_client(oauth_handler, app_with_sample_data):
    """Create Flask test client with real CostSharing and sample data."""
    app = create_app(oauth_handler, app_with_sample_data)
    return app.test_client()


@pytest.fixture(name='api_client_empty_db')
def create_api_client_empty_db(oauth_handler, app_empty_db):
    """Create Flask test client with real CostSharing and empty database."""
    app = create_app(oauth_handler, app_empty_db)
    return app.test_client()


def test_index(api_client):
    """Test that index route returns the demo page HTML."""
    response = api_client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Cost Sharing' in html
    assert 'style.css' in html
    assert 'script.js' in html


def test_auth_callback_success_new_user(api_client_empty_db, oauth_handler):
    """Test successful OAuth callback - creates new user."""
    # Configure OAuth mock
    oauth_handler.exchange_code_returns("newuser@example.com", "New User")

    # Make request
    response = api_client_empty_db.get('/auth/callback?code=test123')

    # Verify response - user should be created with ID 1
    assert_auth_callback_response(response, "dummy-jwt-token-for-user-1",
                                  1, "newuser@example.com", "New User")


def test_auth_callback_success_existing_user(api_client, oauth_handler):
    """Test successful OAuth callback - returns existing user (Alice from sample data)."""
    # Configure OAuth mock to return Alice's email
    oauth_handler.exchange_code_returns("alice@school.edu", "Alice")

    # Make request
    response = api_client.get('/auth/callback?code=test123')

    # Verify response - should return existing user ID 1 (Alice)
    assert_auth_callback_response(response, "dummy-jwt-token-for-user-1",
                                  1, "alice@school.edu", "Alice")


def test_auth_callback_missing_code(api_client):
    """Test OAuth callback with missing code parameter."""
    response = api_client.get('/auth/callback')

    assert_validation_error_response(response, "code parameter is required")


def test_auth_callback_invalid_code(api_client, oauth_handler):
    """Test OAuth callback with invalid authorization code."""
    # Configure OAuth mock
    oauth_handler.exchange_code_raises(OAuthCodeError("Invalid code"))

    # Make request
    response = api_client.get('/auth/callback?code=invalid')

    # Verify response
    assert_validation_error_response(response, "Invalid or expired authorization code")


def test_auth_callback_verification_error(api_client, oauth_handler):
    """Test OAuth callback with verification error."""
    # Configure OAuth mock
    oauth_handler.exchange_code_raises(OAuthVerificationError("Verification failed"))

    # Make request
    response = api_client.get('/auth/callback?code=test123')

    # Verify response
    assert_error_response(response, 401, "Unauthorized", "OAuth verification failed")


def test_auth_me_success(api_client, oauth_handler):
    """Test successful /auth/me request - uses sample data (Alice, user ID 1)."""
    # Configure OAuth mock to return user ID 1 (Alice from sample data)
    oauth_handler.validate_token_returns(1)

    # Make request with Authorization header
    response = api_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer valid-token-123'}
    )

    # Verify response - Alice from sample data
    assert_auth_me_response(response, 1, "alice@school.edu", "Alice")


def test_auth_me_missing_header(api_client):
    """Test /auth/me with missing Authorization header."""
    response = api_client.get('/auth/me')

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_auth_me_invalid_header_format(api_client):
    """Test /auth/me with invalid Authorization header format."""
    # Missing "Bearer " prefix
    response = api_client.get(
        '/auth/me',
        headers={'Authorization': 'invalid-token-123'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_auth_me_expired_token(api_client, oauth_handler):
    """Test /auth/me with expired token."""
    # Configure OAuth mock to raise TokenExpiredError
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = api_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_auth_me_invalid_token(api_client, oauth_handler):
    """Test /auth/me with invalid token."""
    # Configure OAuth mock to raise TokenInvalidError
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = api_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_auth_login_success(api_client):
    """Test /auth/login returns authorization URL."""
    # OAuthHandlerMock.get_authorization_url() returns dummy values
    response = api_client.get('/auth/login')

    assert response.status_code == 200
    data = response.get_json()
    assert 'url' in data
    assert 'state' in data
    assert data['url'] == "https://accounts.google.com/o/oauth2/auth?dummy=true"
    assert data['state'] == "dummy-state-123"


# ============================================================================
# GET /groups Tests
# ============================================================================

def test_get_groups_missing_header(api_client):
    """Test GET /groups with missing Authorization header."""
    response = api_client.get('/groups')

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_invalid_header_format(api_client):
    """Test GET /groups with invalid Authorization header format."""
    # Missing "Bearer " prefix
    response = api_client.get(
        '/groups',
        headers={'Authorization': 'invalid-token-123'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_expired_token(api_client, oauth_handler):
    """Test GET /groups with expired token."""
    # Configure OAuth mock to raise TokenExpiredError
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_invalid_token(api_client, oauth_handler):
    """Test GET /groups with invalid token."""
    # Configure OAuth mock to raise TokenInvalidError
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_empty_list(api_client, oauth_handler):
    """Test GET /groups when user belongs to no groups - User 7 (George) has no groups."""
    # Configure OAuth mock to return user ID 7 (George from sample data - no groups)
    oauth_handler.validate_token_returns(7)

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert data['groups'] == []


def test_get_groups_single_group(api_client, oauth_handler):
    """Test GET /groups when user belongs to one group - User 3 (Charlie) has group 2."""
    # Configure OAuth mock to return user ID 3 (Charlie from sample data - member of group 2)
    oauth_handler.validate_token_returns(3)

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 1
    assert_group_json_is(data['groups'][0], "roommates")


def test_get_groups_multiple_groups(api_client, oauth_handler):
    """Test GET /groups when user belongs to multiple groups - User 1 (Alice) has groups 1 and 2."""
    # Configure OAuth mock to return user ID 1 (Alice from sample data - member of groups 1 and 2)
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 2
    # Alice is in groups 1 (weekend_trip) and 2 (roommates)
    assert_group_json_is(data['groups'][0], "weekend_trip")
    assert_group_json_is(data['groups'][1], "roommates")


def test_get_groups_response_structure(api_client, oauth_handler):
    """Test GET /groups response has correct structure - 
       uses group 4 (study_group) with 5 members."""
    # Configure OAuth mock to return user ID 2 (Bob from sample data - member of groups 1 and 4)
    oauth_handler.validate_token_returns(2)

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 2  # Bob is in groups 1 and 4
    # Find group 4 (study_group) in the response
    study_group = next(g for g in data['groups'] if g['id'] == 4)
    assert_group_json_is(study_group, "study_group")
    # Verify structure by checking it has all required fields
    assert 'id' in study_group
    assert 'name' in study_group
    assert 'description' in study_group
    assert 'createdBy' in study_group
    assert 'members' in study_group
    assert len(study_group['members']) == 5


def test_get_groups_null_description(api_client, oauth_handler):
    """Test GET /groups handles null/empty description correctly - 
       Group 5 (quick_split) has null description."""
    # Configure OAuth mock to return user ID 9 (Iris from sample data - member of groups 4 and 5)
    oauth_handler.validate_token_returns(9)

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 2  # Iris is in groups 4 and 5
    # Find group 5 (quick_split) in the response
    quick_split_group = next(g for g in data['groups'] if g['id'] == 5)
    assert_group_json_is(quick_split_group, "quick_split")
    assert quick_split_group['description'] == ""


def test_get_groups_members_accuracy(api_client, oauth_handler):
    """Test GET /groups members array reflects actual members - 
       Alice has groups with different member counts."""
    # Configure OAuth mock to return user ID 1 (Alice from sample data)
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 2
    # Group 1 (weekend_trip) has 2 members
    assert len(data['groups'][0]['members']) == 2
    # Group 2 (roommates) has 3 members
    assert len(data['groups'][1]['members']) == 3


# ============================================================================
# POST /groups Tests
# ============================================================================

def test_create_group_success(api_client_empty_db, oauth_handler):
    """Test successful group creation."""
    # Configure OAuth mock to return user ID 1 (will create user if needed)
    oauth_handler.exchange_code_returns("test@example.com", "Test User")

    # First, create a user via OAuth callback
    api_client_empty_db.get('/auth/callback?code=test123')

    # Now configure token validation
    oauth_handler.validate_token_returns(1)

    response = api_client_empty_db.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'name': 'Test Group',
            'description': 'Test description'
        }
    )

    data = assert_json_response(response, expected_status=201)
    assert data['name'] == 'Test Group'
    assert data['description'] == 'Test description'
    assert data['id'] == 1
    assert data['createdBy']['id'] == 1
    assert len(data['members']) == 1
    assert data['members'][0]['id'] == 1


def test_create_group_without_description(api_client_empty_db, oauth_handler):
    """Test group creation without description."""
    # Configure OAuth mock to return user ID 1 (will create user if needed)
    oauth_handler.exchange_code_returns("test@example.com", "Test User")

    # First, create a user via OAuth callback
    api_client_empty_db.get('/auth/callback?code=test123')

    # Now configure token validation
    oauth_handler.validate_token_returns(1)

    response = api_client_empty_db.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'name': 'Test Group'
        }
    )

    data = assert_json_response(response, expected_status=201)
    assert data['name'] == 'Test Group'
    assert data['description'] == ''
    assert data['id'] == 1


def test_create_group_missing_header(api_client):
    """Test POST /groups with missing Authorization header."""
    response = api_client.post(
        '/groups',
        json={'name': 'Test Group'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_create_group_missing_name(api_client, oauth_handler):
    """Test POST /groups with missing name."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={}
    )

    assert_validation_error_response(response, "name is required")


def test_create_group_empty_name(api_client, oauth_handler):
    """Test POST /groups with empty name."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': ''}
    )

    assert_validation_error_response(response, "name must be at least 1 character")


def test_create_group_name_too_long(api_client, oauth_handler):
    """Test POST /groups with name too long."""
    oauth_handler.validate_token_returns(1)

    long_name = 'a' * 101
    response = api_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': long_name}
    )

    assert_validation_error_response(response, "name must be at most 100 characters")


def test_create_group_description_too_long(api_client, oauth_handler):
    """Test POST /groups with description too long."""
    oauth_handler.validate_token_returns(1)

    long_description = 'a' * 501
    response = api_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'name': 'Test Group',
            'description': long_description
        }
    )

    assert_validation_error_response(response, "description must be at most 500 characters")


def test_create_group_non_string_description(api_client, oauth_handler):
    """Test POST /groups with non-string description."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'name': 'Test Group',
            'description': 123
        }
    )

    assert_validation_error_response(response, "description must be a string")


def test_create_group_invalid_json(api_client, oauth_handler):
    """Test POST /groups with invalid JSON."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        data='invalid json'
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert 'message' in data


def test_create_group_max_length_name(api_client_empty_db, oauth_handler):
    """Test POST /groups with maximum length name (100 chars)."""
    # Configure OAuth mock to return user ID 1 (will create user if needed)
    oauth_handler.exchange_code_returns("test@example.com", "Test User")
    api_client_empty_db.get('/auth/callback?code=test123')
    oauth_handler.validate_token_returns(1)

    max_name = 'a' * 100
    response = api_client_empty_db.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': max_name}
    )

    data = assert_json_response(response, expected_status=201)
    assert data['name'] == max_name
    assert len(data['name']) == 100


def test_create_group_max_length_description(api_client_empty_db, oauth_handler):
    """Test POST /groups with maximum length description (500 chars)."""
    # Configure OAuth mock to return user ID 1 (will create user if needed)
    oauth_handler.exchange_code_returns("test@example.com", "Test User")
    api_client_empty_db.get('/auth/callback?code=test123')
    oauth_handler.validate_token_returns(1)

    max_description = 'a' * 500
    response = api_client_empty_db.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'name': 'Test Group',
            'description': max_description
        }
    )

    data = assert_json_response(response, expected_status=201)
    assert data['description'] == max_description
    assert len(data['description']) == 500


# ============================================================================
# GET /groups/{groupId} Tests
# ============================================================================

def test_get_group_success(api_client, oauth_handler):
    """Test successful group retrieval - User 1 (Alice) accessing group 2 (roommates)."""
    # Configure OAuth mock to return user ID 1 (Alice from sample data - member of group 2)
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups/2',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert_group_json_is(data, "roommates")


def test_get_group_missing_header(api_client):
    """Test GET /groups/{groupId} without Authorization header."""
    response = api_client.get('/groups/1')

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_invalid_header_format(api_client):
    """Test GET /groups/{groupId} with invalid Authorization header format."""
    response = api_client.get(
        '/groups/1',
        headers={'Authorization': 'InvalidFormat token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_expired_token(api_client, oauth_handler):
    """Test GET /groups/{groupId} with expired token."""
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = api_client.get(
        '/groups/1',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_invalid_token(api_client, oauth_handler):
    """Test GET /groups/{groupId} with invalid token."""
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = api_client.get(
        '/groups/1',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_not_found(api_client, oauth_handler):
    """Test GET /groups/{groupId} when group doesn't exist."""
    # Configure OAuth mock to return user ID 1 (Alice from sample data)
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups/999',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert_error_response(response, 404, "Resource not found", "Group not found")


def test_get_group_forbidden(api_client, oauth_handler):
    """Test GET /groups/{groupId} when user is not a member - 
       User 2 (Bob) accessing group 2 (roommates)."""
    # Configure OAuth mock to return user ID 2 (Bob from sample data - NOT a member of group 2)
    oauth_handler.validate_token_returns(2)

    response = api_client.get(
        '/groups/2',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert_error_response(response, 403, "Forbidden", "Access denied")


def test_get_group_response_structure(api_client, oauth_handler):
    """Test GET /groups/{groupId} response has correct structure - 
       uses group 4 (study_group) with 5 members."""
    # Configure OAuth mock to return user ID 2 (Bob from sample data - member of group 4)
    oauth_handler.validate_token_returns(2)

    response = api_client.get(
        '/groups/4',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert_group_json_is(data, "study_group")
    # Verify structure
    assert 'id' in data
    assert 'name' in data
    assert 'description' in data
    assert 'createdBy' in data
    assert 'members' in data
    assert len(data['members']) == 5


def test_get_group_null_description(api_client, oauth_handler):
    """Test GET /groups/{groupId} handles null/empty description correctly - 
       Group 5 (quick_split) has null description."""
    # Configure OAuth mock to return user ID 9 (Iris from sample data - member of group 5)
    oauth_handler.validate_token_returns(9)

    response = api_client.get(
        '/groups/5',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert_group_json_is(data, "quick_split")
    assert data['description'] == ""


# ============================================================================
# POST /groups/{groupId}/members Tests
# ============================================================================

def test_add_group_member_success_existing_user(api_client, oauth_handler):
    """Test successful addition of existing user to group."""
    # User 1 (Alice) is a member of group 1 (weekend_trip)
    # User 3 (Charlie) exists but is not in group 1
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'charlie@school.edu',
            'name': 'Charlie'
        }
    )

    data = assert_json_response(response, expected_status=201)
    # Verify the added user is in the members list
    member_emails = [member['email'] for member in data['members']]
    assert 'charlie@school.edu' in member_emails
    # Verify it's a Group object
    assert 'id' in data
    assert 'name' in data
    assert 'members' in data


def test_add_group_member_success_new_user(api_client, oauth_handler):
    """Test successful addition of new user (creates user account)."""
    # User 1 (Alice) is a member of group 1 (weekend_trip)
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'newuser@example.com',
            'name': 'New User'
        }
    )

    data = assert_json_response(response, expected_status=201)
    # Verify the added user is in the members list
    member_emails = [member['email'] for member in data['members']]
    assert 'newuser@example.com' in member_emails


def test_add_group_member_missing_header(api_client):
    """Test POST /groups/{groupId}/members without Authorization header."""
    response = api_client.post(
        '/groups/1/members',
        json={'email': 'test@example.com', 'name': 'Test User'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_add_group_member_invalid_token(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members with invalid token."""
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer invalid-token',
            'Content-Type': 'application/json'
        },
        json={'email': 'test@example.com', 'name': 'Test User'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_add_group_member_missing_email(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members with missing email."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': 'Test User'}
    )

    assert_validation_error_response(response, "email is required")


def test_add_group_member_missing_name(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members with missing name."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'email': 'test@example.com'}
    )

    assert_validation_error_response(response, "name is required")


def test_add_group_member_invalid_email_format(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members with invalid email format."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'not-an-email',
            'name': 'Test User'
        }
    )

    assert_validation_error_response(response, "email must be a valid email address")


def test_add_group_member_invalid_json(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members with invalid JSON."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/1/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        data='invalid json'
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert 'message' in data


def test_add_group_member_group_not_found(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members when group doesn't exist."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/999/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'test@example.com',
            'name': 'Test User'
        }
    )

    assert_error_response(response, 404, "Resource not found", "Group not found")


def test_add_group_member_forbidden(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members when user is not a member."""
    # User 2 (Bob) is NOT a member of group 2 (roommates)
    oauth_handler.validate_token_returns(2)

    response = api_client.post(
        '/groups/2/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'test@example.com',
            'name': 'Test User'
        }
    )

    assert_error_response(response, 403, "Forbidden", "Access denied")


def test_add_group_member_conflict(api_client, oauth_handler):
    """Test POST /groups/{groupId}/members when user is already a member."""
    # User 1 (Alice) is a member of group 2 (roommates)
    # User 1 (Alice) is already in group 2
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/members',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'alice@school.edu',
            'name': 'Alice'
        }
    )

    assert_error_response(response, 409, "Conflict", "User is already a member of this group")


# ============================================================================
# GET /groups/{groupId}/expenses Tests
# ============================================================================

def test_get_group_expenses_success(api_client, oauth_handler): # pylint: disable=R0915
    """Test successful expense retrieval - User 1 (Alice) accessing group 2 (roommates)."""
    # Configure OAuth mock to return user ID 1 (Alice from sample data - member of group 2)
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert 'expenses' in data
    assert isinstance(data['expenses'], list)
    assert len(data['expenses']) == 4

    # Verify first expense structure
    expense = data['expenses'][0]
    assert 'id' in expense
    assert 'groupId' in expense
    assert 'description' in expense
    assert 'amount' in expense
    assert 'date' in expense
    assert 'paidBy' in expense
    assert 'splitBetween' in expense
    assert 'perPersonAmount' in expense

    # Verify paidBy is a User object
    assert 'id' in expense['paidBy']
    assert 'email' in expense['paidBy']
    assert 'name' in expense['paidBy']

    # Verify splitBetween is an array of User objects
    assert isinstance(expense['splitBetween'], list)
    assert len(expense['splitBetween']) > 0
    assert 'id' in expense['splitBetween'][0]
    assert 'email' in expense['splitBetween'][0]
    assert 'name' in expense['splitBetween'][0]


def test_get_group_expenses_empty_list(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses when group has no expenses."""
    # Group 1 (weekend_trip) has no expenses, user 1 (Alice) is a member
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups/1/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert 'expenses' in data
    assert isinstance(data['expenses'], list)
    assert len(data['expenses']) == 0


def test_get_group_expenses_single_expense(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses when group has one expense."""
    # Group 3 has one expense (team_lunch), user 5 (Eve) is a member
    oauth_handler.validate_token_returns(5)

    response = api_client.get(
        '/groups/3/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert 'expenses' in data
    assert isinstance(data['expenses'], list)
    assert len(data['expenses']) == 1

    expense = data['expenses'][0]
    assert expense['description'] == "Team lunch"
    assert expense['amount'] == 45.67
    assert expense['perPersonAmount'] is not None


def test_get_group_expenses_missing_header(api_client):
    """Test GET /groups/{groupId}/expenses without Authorization header."""
    response = api_client.get('/groups/2/expenses')

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_expenses_invalid_header_format(api_client):
    """Test GET /groups/{groupId}/expenses with invalid Authorization header format."""
    response = api_client.get(
        '/groups/2/expenses',
        headers={'Authorization': 'InvalidFormat token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_expenses_expired_token(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses with expired token."""
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = api_client.get(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_expenses_invalid_token(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses with invalid token."""
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = api_client.get(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_group_expenses_group_not_found(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses when group doesn't exist."""
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups/999/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert_error_response(response, 404, "Resource not found", "Group not found")


def test_get_group_expenses_forbidden(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses when user is not a member."""
    # User 2 (Bob) is NOT a member of group 2 (roommates)
    oauth_handler.validate_token_returns(2)

    response = api_client.get(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert_error_response(response, 403, "Forbidden", "Access denied")


def test_get_group_expenses_response_structure(api_client, oauth_handler): # pylint: disable=R0915
    """Test GET /groups/{groupId}/expenses response has correct structure."""
    # User 1 (Alice) is a member of group 2 (roommates) with 4 expenses
    oauth_handler.validate_token_returns(1)

    response = api_client.get(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert 'expenses' in data
    assert isinstance(data['expenses'], list)
    assert len(data['expenses']) == 4

    # Verify all expenses have required fields
    for expense in data['expenses']:
        assert isinstance(expense['id'], int)
        assert isinstance(expense['groupId'], int)
        assert isinstance(expense['description'], str)
        assert isinstance(expense['amount'], (int, float))
        assert isinstance(expense['date'], str)
        assert isinstance(expense['paidBy'], dict)
        assert isinstance(expense['splitBetween'], list)
        assert isinstance(expense['perPersonAmount'], (int, float))
        assert expense['perPersonAmount'] is not None

        # Verify paidBy structure
        assert 'id' in expense['paidBy']
        assert 'email' in expense['paidBy']
        assert 'name' in expense['paidBy']

        # Verify splitBetween structure
        assert len(expense['splitBetween']) > 0
        for user in expense['splitBetween']:
            assert 'id' in user
            assert 'email' in user
            assert 'name' in user


def test_get_group_expenses_with_many_participants(api_client, oauth_handler):
    """Test GET /groups/{groupId}/expenses with expenses that have many participants."""
    # User 8 (Helen) is a member of group 4 (study_group) with expenses
    oauth_handler.validate_token_returns(8)

    response = api_client.get(
        '/groups/4/expenses',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_json_response(response, expected_status=200)
    assert 'expenses' in data
    assert len(data['expenses']) == 4

    # Find textbooks expense (split between 5 people)
    textbooks_expense = [e for e in data['expenses'] if e['description'] == 'Textbooks'][0]
    assert len(textbooks_expense['splitBetween']) == 5
    assert textbooks_expense['perPersonAmount'] is not None


# ============================================================================
# POST /groups/{groupId}/expenses Tests
# ============================================================================

def test_create_expense_success(api_client, oauth_handler):
    """Test successful expense creation - User 1 (Alice) creating expense in group 2."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'New expense',
            'amount': 50.00,
            'date': '2025-02-01',
            'splitBetween': [1, 3]
        }
    )

    data = assert_json_response(response, expected_status=201)
    assert data['description'] == 'New expense'
    assert data['amount'] == 50.00
    assert data['date'] == '2025-02-01'
    assert data['paidBy']['id'] == 1
    assert len(data['splitBetween']) == 2
    assert data['perPersonAmount'] == 25.00


def test_create_expense_missing_header(api_client):
    """Test POST /groups/{groupId}/expenses without Authorization header."""
    response = api_client.post(
        '/groups/2/expenses',
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_create_expense_invalid_token(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with invalid token."""
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer invalid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_create_expense_missing_description(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with missing description."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'description is required')


def test_create_expense_empty_description(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with empty description."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': '',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'description must be at least 1 character')


def test_create_expense_description_too_long(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with description too long."""
    oauth_handler.validate_token_returns(1)

    long_description = 'a' * 201
    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': long_description,
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'description must be at most 200 characters')


def test_create_expense_missing_amount(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with missing amount."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'amount is required')


def test_create_expense_invalid_amount_too_small(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with amount too small."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 0.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'amount must be at least 0.01')


def test_create_expense_invalid_amount_not_number(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with amount that is not a number."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 'not a number',
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'amount must be a number')


def test_create_expense_missing_date(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with missing date."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'date is required')


def test_create_expense_invalid_date_format(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with invalid date format."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '01/15/2025',
            'splitBetween': [1]
        }
    )

    assert_validation_error_response(response, 'date must be in ISO 8601 format (YYYY-MM-DD)')


def test_create_expense_missing_split_between(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with missing splitBetween."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15'
        }
    )

    assert_validation_error_response(response, 'splitBetween is required')


def test_create_expense_empty_split_between(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with empty splitBetween array."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': []
        }
    )

    assert_validation_error_response(response, 'splitBetween must contain at least one user ID')


def test_create_expense_split_between_not_array(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses when splitBetween is not an array."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': 'not an array'
        }
    )

    assert_validation_error_response(response, 'splitBetween must be an array')


def test_create_expense_split_between_invalid_user_id_type(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses when splitBetween contains non-integer."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1, 'not an integer', 3]
        }
    )

    assert_validation_error_response(response,
        'splitBetween must contain only user IDs (integers)')


def test_create_expense_user_not_in_split_between(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses when user is not in splitBetween."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [3]  # Only Charlie, not Alice (user 1)
        }
    )

    assert_validation_error_response(response,
        'splitBetween must include the authenticated user\'s ID')


def test_create_expense_user_not_in_group(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses when participant is not a group member."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1, 2]  # Bob (user 2) is not a member of group 2
        }
    )

    assert_validation_error_response(response,
        'All users in splitBetween must be members of the group')


def test_create_expense_group_not_found(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses when group doesn't exist."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/999/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [1]
        }
    )

    assert_error_response(response, 404, "Resource not found", "Group not found")


def test_create_expense_forbidden(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses when user is not a member."""
    # User 2 (Bob) is NOT a member of group 2 (roommates)
    oauth_handler.validate_token_returns(2)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 50.00,
            'date': '2025-01-15',
            'splitBetween': [2]
        }
    )

    assert_error_response(response, 403, "Forbidden", "Access denied")


def test_create_expense_response_structure(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses response has correct structure."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={'Authorization': 'Bearer valid-token'},
        json={
            'description': 'Test expense',
            'amount': 75.50,
            'date': '2025-02-05',
            'splitBetween': [1, 3, 4]
        }
    )

    data = assert_json_response(response, expected_status=201)
    assert 'id' in data
    assert 'groupId' in data
    assert 'description' in data
    assert 'amount' in data
    assert 'date' in data
    assert 'paidBy' in data
    assert 'splitBetween' in data
    assert 'perPersonAmount' in data

    assert data['description'] == 'Test expense'
    assert data['amount'] == 75.50
    assert data['date'] == '2025-02-05'
    assert data['paidBy']['id'] == 1
    assert len(data['splitBetween']) == 3
    assert data['perPersonAmount'] == 25.17  # 75.50 / 3 rounded


def test_create_expense_invalid_json(api_client, oauth_handler):
    """Test POST /groups/{groupId}/expenses with invalid JSON."""
    oauth_handler.validate_token_returns(1)

    response = api_client.post(
        '/groups/2/expenses',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        data='invalid json'
    )

    assert_validation_error_response(response, 'Invalid JSON')
