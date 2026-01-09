import pytest
from oauth_handler_mock import OAuthHandlerMock
from cost_sharing_mock import CostSharingMock
from helpers import (
    assert_groups_json_response, assert_json_response,
    assert_group_json_full, assert_error_response,
    assert_auth_me_response, assert_auth_callback_response,
    assert_validation_error_response, create_test_user, create_test_group
)
from cost_sharing.app import create_app
from cost_sharing.oauth_handler import (
    OAuthCodeError, OAuthVerificationError,
    TokenExpiredError, TokenInvalidError
)


@pytest.fixture(name='client')
def create_client():
    """Create Flask test client with mocked dependencies."""
    # Create mocks for dependencies
    oauth_handler = OAuthHandlerMock()
    application = CostSharingMock()

    app = create_app(oauth_handler, application)
    return app.test_client()


@pytest.fixture(name='oauth_handler')
def create_oauth_handler():
    """Create OAuth handler mock for test configuration."""
    return OAuthHandlerMock()


@pytest.fixture(name='application')
def create_application():
    """Create application mock for test configuration."""
    return CostSharingMock()


@pytest.fixture(name='configured_client')
def create_configured_client(oauth_handler, application):
    """Create Flask test client with configured mocks."""
    app = create_app(oauth_handler, application)
    return app.test_client()


def test_index(client):
    """Test that index route returns the demo page HTML."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Cost Sharing' in html
    assert 'style.css' in html
    assert 'script.js' in html


def test_auth_callback_success(configured_client, oauth_handler, application):
    """Test successful OAuth callback."""
    # Configure mocks
    oauth_handler.exchange_code_returns("test@example.com", "Test User")
    application.get_or_create_user_returns(1, "test@example.com", "Test User")

    # Make request
    response = configured_client.get('/auth/callback?code=test123')

    # Verify response
    assert_auth_callback_response(response, "dummy-jwt-token-for-user-1",
                                  1, "test@example.com", "Test User")


def test_auth_callback_missing_code(configured_client):
    """Test OAuth callback with missing code parameter."""
    response = configured_client.get('/auth/callback')

    assert_validation_error_response(response, "code parameter is required")


def test_auth_callback_invalid_code(configured_client, oauth_handler):
    """Test OAuth callback with invalid authorization code."""
    # Configure mocks
    oauth_handler.exchange_code_raises(OAuthCodeError("Invalid code"))

    # Make request
    response = configured_client.get('/auth/callback?code=invalid')

    # Verify response
    assert_validation_error_response(response, "Invalid or expired authorization code")


def test_auth_callback_verification_error(configured_client, oauth_handler):
    """Test OAuth callback with verification error."""
    # Configure mocks
    oauth_handler.exchange_code_raises(OAuthVerificationError("Verification failed"))

    # Make request
    response = configured_client.get('/auth/callback?code=test123')

    # Verify response
    assert_error_response(response, 401, "Unauthorized", "OAuth verification failed")


def test_auth_me_success(configured_client, oauth_handler, application):
    """Test successful /auth/me request."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_by_id_returns(1, "test@example.com", "Test User")

    # Make request with Authorization header
    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer valid-token-123'}
    )

    # Verify response
    assert_auth_me_response(response, 1, "test@example.com", "Test User")


def test_auth_me_missing_header(configured_client):
    """Test /auth/me with missing Authorization header."""
    response = configured_client.get('/auth/me')

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_auth_me_invalid_header_format(configured_client):
    """Test /auth/me with invalid Authorization header format."""
    # Missing "Bearer " prefix
    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'invalid-token-123'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_auth_me_expired_token(configured_client, oauth_handler):
    """Test /auth/me with expired token."""
    # Configure mock to raise TokenExpiredError
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_auth_me_invalid_token(configured_client, oauth_handler):
    """Test /auth/me with invalid token."""
    # Configure mock to raise TokenInvalidError
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_auth_login_success(configured_client):
    """Test /auth/login returns authorization URL."""
    # OAuthHandlerMock.get_authorization_url() returns dummy values
    response = configured_client.get('/auth/login')

    assert response.status_code == 200
    data = response.get_json()
    assert 'url' in data
    assert 'state' in data
    assert data['url'] == "https://accounts.google.com/o/oauth2/auth?dummy=true"
    assert data['state'] == "dummy-state-123"


# ============================================================================
# GET /groups Tests
# ============================================================================

def test_get_groups_missing_header(configured_client):
    """Test GET /groups with missing Authorization header."""
    response = configured_client.get('/groups')

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_invalid_header_format(configured_client):
    """Test GET /groups with invalid Authorization header format."""
    # Missing "Bearer " prefix
    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'invalid-token-123'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_expired_token(configured_client, oauth_handler):
    """Test GET /groups with expired token."""
    # Configure mock to raise TokenExpiredError
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_invalid_token(configured_client, oauth_handler):
    """Test GET /groups with invalid token."""
    # Configure mock to raise TokenInvalidError
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_get_groups_empty_list(configured_client, oauth_handler, application):
    """Test GET /groups when user belongs to no groups."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert data['groups'] == []


# disable because it is test code, and breaking into functions would be overkill
def test_get_groups_single_group(configured_client, oauth_handler, application): # pylint: disable=R0914
    """Test GET /groups when user belongs to one group."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator = create_test_user(3, "charlie@school.edu", "Charlie")
    member1 = create_test_user(1, "alice@school.edu", "Alice")
    member2 = create_test_user(4, "david@school.edu", "David")
    group = create_test_group(
        group_id=1,
        name="Roommates Spring 2025",
        description="Shared expenses for apartment 4B",
        creator=creator,
        members=[creator, member1, member2]
    )
    application.get_user_groups_returns([group])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 1
    assert_group_json_full(data['groups'][0], group)


# disable because it is test code, and breaking into functions would be overkill
def test_get_groups_multiple_groups(configured_client, oauth_handler, application): # pylint: disable=R0914
    """Test GET /groups when user belongs to multiple groups."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator1 = create_test_user(1, "alice@school.edu", "Alice")
    member1 = create_test_user(2, "bob@school.edu", "Bob")
    group1 = create_test_group(
        group_id=1,
        name="Weekend Trip Planning",
        description="Planning expenses for upcoming weekend getaway",
        creator=creator1,
        members=[creator1, member1]
    )
    creator2 = create_test_user(3, "charlie@school.edu", "Charlie")
    member2a = create_test_user(1, "alice@school.edu", "Alice")
    member2b = create_test_user(4, "david@school.edu", "David")
    group2 = create_test_group(
        group_id=2,
        name="Roommates Spring 2025",
        description="Shared expenses for apartment 4B",
        creator=creator2,
        members=[creator2, member2a, member2b]
    )
    application.get_user_groups_returns([group1, group2])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 2
    assert_group_json_full(data['groups'][0], group1)
    assert_group_json_full(data['groups'][1], group2)


def test_get_groups_response_structure(configured_client, oauth_handler, application):
    """Test GET /groups response has correct structure."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator = create_test_user(1, "creator@example.com", "Creator")
    members = [
        create_test_user(i, f"user{i}@example.com", f"User {i}")
        for i in range(1, 6)
    ]
    group = create_test_group(
        group_id=1,
        name="Test Group",
        description="Test description",
        creator=creator,
        members=members
    )
    application.get_user_groups_returns([group])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert len(data['groups']) == 1
    assert_group_json_full(data['groups'][0], group)


def test_get_groups_null_description(configured_client, oauth_handler, application):
    """Test GET /groups handles null/empty description correctly."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator = create_test_user(1, "creator@example.com", "Creator")
    member = create_test_user(2, "member@example.com", "Member")
    group = create_test_group(
        group_id=1,
        name="Test Group",
        description="",
        creator=creator,
        members=[creator, member]
    )
    application.get_user_groups_returns([group])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert_group_json_full(data['groups'][0], group)


# disable because it is test code, and breaking into functions would be overkill
def test_get_groups_members_accuracy(configured_client, oauth_handler, application): # pylint: disable=R0914
    """Test GET /groups members array reflects actual members."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator1 = create_test_user(1, "creator1@example.com", "Creator 1")
    member1 = create_test_user(2, "member1@example.com", "Member 1")
    group1 = create_test_group(
        group_id=1,
        name="Small Group",
        description="Description",
        creator=creator1,
        members=[creator1, member1]
    )
    creator2 = create_test_user(3, "creator2@example.com", "Creator 2")
    members2 = [
        create_test_user(i, f"member{i}@example.com", f"Member {i}")
        for i in range(4, 14)
    ]
    group2 = create_test_group(
        group_id=2,
        name="Large Group",
        description="Description",
        creator=creator2,
        members=[creator2] + members2
    )
    application.get_user_groups_returns([group1, group2])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    data = assert_groups_json_response(response)
    assert_group_json_full(data['groups'][0], group1)
    assert_group_json_full(data['groups'][1], group2)


# ============================================================================
# POST /groups Tests
# ============================================================================

def test_create_group_success(configured_client, oauth_handler, application):
    """Test successful group creation."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator = create_test_user(1, "test@example.com", "Test User")
    group = create_test_group(
        group_id=1,
        name="Test Group",
        description="Test description",
        creator=creator
    )
    application.create_group_returns(group)

    response = configured_client.post(
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
    assert_group_json_full(data, group)


def test_create_group_without_description(configured_client, oauth_handler, application):
    """Test group creation without description."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    creator = create_test_user(1, "test@example.com", "Test User")
    group = create_test_group(
        group_id=1,
        name="Test Group",
        description="",
        creator=creator
    )
    application.create_group_returns(group)

    response = configured_client.post(
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
    assert_group_json_full(data, group)


def test_create_group_missing_header(configured_client):
    """Test POST /groups with missing Authorization header."""
    response = configured_client.post(
        '/groups',
        json={'name': 'Test Group'}
    )

    assert_error_response(response, 401, "Unauthorized", "Authentication required")


def test_create_group_missing_name(configured_client, oauth_handler):
    """Test POST /groups with missing name."""
    oauth_handler.validate_token_returns(1)

    response = configured_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={}
    )

    assert_validation_error_response(response, "name is required")


def test_create_group_empty_name(configured_client, oauth_handler):
    """Test POST /groups with empty name."""
    oauth_handler.validate_token_returns(1)

    response = configured_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': ''}
    )

    assert_validation_error_response(response, "name must be at least 1 character")


def test_create_group_name_too_long(configured_client, oauth_handler):
    """Test POST /groups with name too long."""
    oauth_handler.validate_token_returns(1)

    long_name = 'a' * 101
    response = configured_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': long_name}
    )

    assert_validation_error_response(response, "name must be at most 100 characters")


def test_create_group_description_too_long(configured_client, oauth_handler):
    """Test POST /groups with description too long."""
    oauth_handler.validate_token_returns(1)

    long_description = 'a' * 501
    response = configured_client.post(
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


def test_create_group_non_string_description(configured_client, oauth_handler):
    """Test POST /groups with non-string description."""
    oauth_handler.validate_token_returns(1)

    response = configured_client.post(
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


def test_create_group_invalid_json(configured_client, oauth_handler):
    """Test POST /groups with invalid JSON."""
    oauth_handler.validate_token_returns(1)

    response = configured_client.post(
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


def test_create_group_max_length_name(configured_client, oauth_handler, application):
    """Test POST /groups with maximum length name (100 chars)."""
    oauth_handler.validate_token_returns(1)
    max_name = 'a' * 100
    creator = create_test_user(1, "test@example.com", "Test User")
    group = create_test_group(
        group_id=1,
        name=max_name,
        description="",
        creator=creator
    )
    application.create_group_returns(group)

    response = configured_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': max_name}
    )

    data = assert_json_response(response, expected_status=201)
    assert_group_json_full(data, group)


def test_create_group_max_length_description(configured_client, oauth_handler, application):
    """Test POST /groups with maximum length description (500 chars)."""
    oauth_handler.validate_token_returns(1)
    max_description = 'a' * 500
    creator = create_test_user(1, "test@example.com", "Test User")
    group = create_test_group(
        group_id=1,
        name="Test Group",
        description=max_description,
        creator=creator
    )
    application.create_group_returns(group)

    response = configured_client.post(
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
    assert_group_json_full(data, group)
