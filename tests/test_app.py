import pytest
from oauth_handler_mock import OAuthHandlerMock
from cost_sharing_mock import CostSharingMock
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
    assert response.status_code == 200
    data = response.get_json()
    assert data['token'] == "dummy-jwt-token-for-user-1"
    assert data['user']['id'] == 1
    assert data['user']['email'] == "test@example.com"
    assert data['user']['name'] == "Test User"


def test_auth_callback_missing_code(configured_client):
    """Test OAuth callback with missing code parameter."""
    response = configured_client.get('/auth/callback')

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "code parameter is required"


def test_auth_callback_invalid_code(configured_client, oauth_handler):
    """Test OAuth callback with invalid authorization code."""
    # Configure mocks
    oauth_handler.exchange_code_raises(OAuthCodeError("Invalid code"))

    # Make request
    response = configured_client.get('/auth/callback?code=invalid')

    # Verify response
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "Invalid or expired authorization code"


def test_auth_callback_verification_error(configured_client, oauth_handler):
    """Test OAuth callback with verification error."""
    # Configure mocks
    oauth_handler.exchange_code_raises(OAuthVerificationError("Verification failed"))

    # Make request
    response = configured_client.get('/auth/callback?code=test123')

    # Verify response
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "OAuth verification failed"


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
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 1
    assert data['email'] == "test@example.com"
    assert data['name'] == "Test User"


def test_auth_me_missing_header(configured_client):
    """Test /auth/me with missing Authorization header."""
    response = configured_client.get('/auth/me')

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_auth_me_invalid_header_format(configured_client):
    """Test /auth/me with invalid Authorization header format."""
    # Missing "Bearer " prefix
    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'invalid-token-123'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_auth_me_expired_token(configured_client, oauth_handler):
    """Test /auth/me with expired token."""
    # Configure mock to raise TokenExpiredError
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


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

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_get_groups_invalid_header_format(configured_client):
    """Test GET /groups with invalid Authorization header format."""
    # Missing "Bearer " prefix
    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'invalid-token-123'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_get_groups_expired_token(configured_client, oauth_handler):
    """Test GET /groups with expired token."""
    # Configure mock to raise TokenExpiredError
    oauth_handler.validate_token_raises(TokenExpiredError("Token expired"))

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer expired-token'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_get_groups_invalid_token(configured_client, oauth_handler):
    """Test GET /groups with invalid token."""
    # Configure mock to raise TokenInvalidError
    oauth_handler.validate_token_raises(TokenInvalidError("Invalid token"))

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


def test_get_groups_empty_list(configured_client, oauth_handler, application):
    """Test GET /groups when user belongs to no groups."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'groups' in data
    assert data['groups'] == []


def test_get_groups_single_group(configured_client, oauth_handler, application):
    """Test GET /groups when user belongs to one group."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([
        (1, "Roommates Spring 2025", "Shared expenses for apartment 4B", 3)
    ])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'groups' in data
    assert len(data['groups']) == 1
    group = data['groups'][0]
    assert group['id'] == 1
    assert group['name'] == "Roommates Spring 2025"
    assert group['description'] == "Shared expenses for apartment 4B"
    assert group['memberCount'] == 3


def test_get_groups_multiple_groups(configured_client, oauth_handler, application):
    """Test GET /groups when user belongs to multiple groups."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([
        (1, "Weekend Trip Planning", "Planning expenses for upcoming weekend getaway", 2),
        (2, "Roommates Spring 2025", "Shared expenses for apartment 4B", 3)
    ])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'groups' in data
    assert len(data['groups']) == 2
    assert data['groups'][0]['id'] == 1
    assert data['groups'][0]['name'] == "Weekend Trip Planning"
    assert data['groups'][1]['id'] == 2
    assert data['groups'][1]['name'] == "Roommates Spring 2025"


def test_get_groups_response_structure(configured_client, oauth_handler, application):
    """Test GET /groups response has correct structure."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([
        (1, "Test Group", "Test description", 5)
    ])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert 'groups' in data
    assert isinstance(data['groups'], list)
    assert len(data['groups']) == 1
    group = data['groups'][0]
    assert 'id' in group
    assert 'name' in group
    assert 'description' in group
    assert 'memberCount' in group
    assert isinstance(group['id'], int)
    assert isinstance(group['name'], str)
    assert isinstance(group['description'], str)
    assert isinstance(group['memberCount'], int)


def test_get_groups_null_description(configured_client, oauth_handler, application):
    """Test GET /groups handles null/empty description correctly."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([
        (1, "Test Group", "", 2)
    ])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200
    data = response.get_json()
    group = data['groups'][0]
    assert group['description'] == ""


def test_get_groups_member_count_accuracy(configured_client, oauth_handler, application):
    """Test GET /groups memberCount reflects actual number of members."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.get_user_groups_returns([
        (1, "Small Group", "Description", 2),
        (2, "Large Group", "Description", 10)
    ])

    response = configured_client.get(
        '/groups',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['groups'][0]['memberCount'] == 2
    assert data['groups'][1]['memberCount'] == 10


# ============================================================================
# POST /groups Tests
# ============================================================================

def test_create_group_success(configured_client, oauth_handler, application):
    """Test successful group creation."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.create_group_returns(1, "Test Group", "Test description", 1)
    application.get_user_by_id_returns(1, "test@example.com", "Test User")

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

    assert response.status_code == 201
    data = response.get_json()
    assert data['id'] == 1
    assert data['name'] == "Test Group"
    assert data['description'] == "Test description"
    assert data['memberCount'] == 1
    assert data['createdBy']['id'] == 1
    assert data['createdBy']['email'] == "test@example.com"
    assert data['createdBy']['name'] == "Test User"


def test_create_group_without_description(configured_client, oauth_handler, application):
    """Test group creation without description."""
    # Configure mocks
    oauth_handler.validate_token_returns(1)
    application.create_group_returns(1, "Test Group", "", 1)
    application.get_user_by_id_returns(1, "test@example.com", "Test User")

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

    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Test Group"
    assert data['description'] == ""


def test_create_group_missing_header(configured_client):
    """Test POST /groups with missing Authorization header."""
    response = configured_client.post(
        '/groups',
        json={'name': 'Test Group'}
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized"
    assert data['message'] == "Authentication required"


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

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "name is required"


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

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "name must be at least 1 character"


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

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "name must be at most 100 characters"


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

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "description must be at most 500 characters"


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

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Validation failed"
    assert data['message'] == "description must be a string"


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
    application.create_group_returns(1, max_name, "", 1)
    application.get_user_by_id_returns(1, "test@example.com", "Test User")

    response = configured_client.post(
        '/groups',
        headers={
            'Authorization': 'Bearer valid-token',
            'Content-Type': 'application/json'
        },
        json={'name': max_name}
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == max_name


def test_create_group_max_length_description(configured_client, oauth_handler, application):
    """Test POST /groups with maximum length description (500 chars)."""
    oauth_handler.validate_token_returns(1)
    max_description = 'a' * 500
    application.create_group_returns(1, "Test Group", max_description, 1)
    application.get_user_by_id_returns(1, "test@example.com", "Test User")

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

    assert response.status_code == 201
    data = response.get_json()
    assert data['description'] == max_description
