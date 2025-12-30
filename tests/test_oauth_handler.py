import datetime
import jwt
import pytest
from cost_sharing.oauth_handler import OAuthHandler, TokenExpiredError, TokenInvalidError


@pytest.fixture(name='handler')
def create_handler():
    """Fixture for OAuthHandler"""
    return OAuthHandler(
        base_url="http://localhost:8000",
        google_client_id="test-client-id",
        google_client_secret="test-secret",
        jwt_secret="test-jwt-secret"
    )


def test_create_jwt_token(handler):
    """Test JWT token creation"""
    user_id = 123
    token = handler.create_jwt_token(user_id)

    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0


def test_validate_jwt_token(handler):
    """Test JWT token validation"""
    user_id = 456
    token = handler.create_jwt_token(user_id)

    # Should be able to validate and extract user_id
    extracted_user_id = handler.validate_jwt_token(token)
    assert extracted_user_id == user_id


def test_validate_jwt_token_expired(handler):
    """Test that expired tokens are rejected"""
    # Manually create a token with expired timestamp
    # JWT expects timestamps as seconds since epoch
    expired_time = datetime.datetime(2020, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    issued_time = datetime.datetime(2019, 12, 25, 12, 0, 0, tzinfo=datetime.timezone.utc)

    expired_payload = {
        'user_id': 789,
        'exp': int(expired_time.timestamp()),
        'iat': int(issued_time.timestamp())
    }
    expired_token = jwt.encode(
        expired_payload,
        handler.jwt_secret,
        algorithm='HS256'
    )

    # Should raise TokenExpiredError for expired token
    with pytest.raises(TokenExpiredError):
        handler.validate_jwt_token(expired_token)


def test_validate_jwt_token_invalid_secret():
    """Test that tokens with wrong secret are rejected"""
    handler1 = OAuthHandler(
        base_url="http://localhost:8000",
        google_client_id="test-client-id",
        google_client_secret="test-secret",
        jwt_secret="secret-1"
    )

    handler2 = OAuthHandler(
        base_url="http://localhost:8000",
        google_client_id="test-client-id",
        google_client_secret="test-secret",
        jwt_secret="secret-2"  # Different secret
    )

    user_id = 999
    token = handler1.create_jwt_token(user_id)

    # Should raise TokenInvalidError for invalid token
    with pytest.raises(TokenInvalidError):
        handler2.validate_jwt_token(token)


def test_validate_jwt_token_malformed(handler):
    """Test that malformed tokens are rejected"""
    # Invalid token string
    with pytest.raises(TokenInvalidError):
        handler.validate_jwt_token("not-a-valid-token")


def test_create_jwt_token_with_custom_expiration(handler):
    """Test JWT token creation with custom expiration"""
    user_id = 111
    token = handler.create_jwt_token(user_id, expiration_days=1)

    # Should be able to validate
    extracted_user_id = handler.validate_jwt_token(token)
    assert extracted_user_id == user_id


def test_get_authorization_url(handler):
    """Test authorization URL generation"""
    auth_url, state = handler.get_authorization_url()

    # Should return URL and state
    assert isinstance(auth_url, str)
    assert len(auth_url) > 0
    assert isinstance(state, str)
    assert len(state) > 0
    # URL should point to Google
    assert "accounts.google.com" in auth_url


def test_redirect_uri_computed_from_base_url():
    """Test that redirect_uri is computed correctly from base_url"""
    test_handler = OAuthHandler(
        base_url="https://example.com",
        google_client_id="test-client-id",
        google_client_secret="test-secret",
        jwt_secret="test-jwt-secret"
    )

    assert test_handler.redirect_uri == "https://example.com/auth/callback"
