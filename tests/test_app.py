import pytest
from oauth_handler_mock import OAuthHandlerMock
from cost_sharing_mock import CostSharingMock
from cost_sharing.app import create_app
from cost_sharing.oauth_handler import OAuthCodeError, OAuthVerificationError


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
    """Test that index route returns Hello, World!"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Hello, World!"


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
