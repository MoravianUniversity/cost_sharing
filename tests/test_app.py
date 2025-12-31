import pytest
from oauth_handler_mock import OAuthHandlerMock
from cost_sharing_mock import CostSharingMock
from cost_sharing.app import create_app
from cost_sharing.oauth_handler import (
    OAuthCodeError, OAuthVerificationError,
    TokenExpiredError, TokenInvalidError
)
from cost_sharing.exceptions import UserNotFoundError


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
    assert 'Cost Sharing Demo' in html
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


def test_auth_me_user_not_found(configured_client, oauth_handler, application):
    """Test /auth/me when user doesn't exist."""
    # Configure mocks
    oauth_handler.validate_token_returns(999)  # Valid token but user doesn't exist
    application.get_user_by_id_raises(UserNotFoundError("User not found"))

    response = configured_client.get(
        '/auth/me',
        headers={'Authorization': 'Bearer valid-token'}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "Resource not found"
    assert data['message'] == "User not found"


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
