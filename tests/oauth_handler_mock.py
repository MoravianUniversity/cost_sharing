"""Mock implementation of OAuthHandler for testing"""

class OAuthHandlerMock:
    """
    Mock implementation of OAuthHandler for testing.

    This mock allows you to configure behavior for testing different scenarios.
    Use the configuration methods to set up the desired behavior before passing
    the mock to create_app().
    """

    def __init__(self):
        """Initialize the mock."""
        # Configuration for exchange_code_for_user_info
        self._exchange_code_result = None
        self._exchange_code_exception = None

        # Configuration for validate_jwt_token
        self._validate_token_result = None
        self._validate_token_exception = None

    def exchange_code_returns(self, email, name):
        """
        Configure exchange_code_for_user_info to return successfully.

        Args:
            email: Email to return
            name: Name to return
        """
        self._exchange_code_result = {"email": email, "name": name}
        self._exchange_code_exception = None

    def exchange_code_raises(self, exception):
        """
        Configure exchange_code_for_user_info to raise an exception.

        Args:
            exception: Exception instance to raise (OAuthCodeError or OAuthVerificationError)
        """
        self._exchange_code_result = None
        self._exchange_code_exception = exception

    def validate_token_returns(self, user_id):
        """
        Configure validate_jwt_token to return successfully.

        Args:
            user_id: User ID to return
        """
        self._validate_token_result = user_id
        self._validate_token_exception = None

    def validate_token_raises(self, exception):
        """
        Configure validate_jwt_token to raise an exception.

        Args:
            exception: Exception instance to raise (TokenExpiredError or TokenInvalidError)
        """
        self._validate_token_result = None
        self._validate_token_exception = exception

    def get_authorization_url(self):
        """
        Get Google OAuth authorization URL (mock implementation).

        Returns:
            Tuple of (authorization_url, state) with dummy values
        """
        return ("https://accounts.google.com/o/oauth2/auth?dummy=true", "dummy-state-123")

    def exchange_code_for_user_info(self, oauth_code):  # pylint: disable=W0613
        """
        Exchange OAuth authorization code for user information (mock implementation).

        Args:
            oauth_code: Authorization code (ignored, uses configured behavior)

        Returns:
            Dict with keys: email, name

        Raises:
            OAuthCodeError: If configured to raise OAuthCodeError
            OAuthVerificationError: If configured to raise OAuthVerificationError
        """
        if self._exchange_code_exception is not None:
            raise self._exchange_code_exception

        if self._exchange_code_result is None:
            # Default behavior if not configured
            return {"email": "default@example.com", "name": "Default User"}

        return self._exchange_code_result

    def create_jwt_token(self, user_id, expiration_days=7):  # pylint: disable=W0613
        """
        Create a JWT token for authenticated user (mock implementation).

        Args:
            user_id: User ID to encode in token
            expiration_days: Number of days until token expires (ignored in mock)

        Returns:
            Dummy JWT token string
        """
        return f"dummy-jwt-token-for-user-{user_id}"

    def validate_jwt_token(self, token):  # pylint: disable=W0613
        """
        Validate JWT token and extract user ID (mock implementation).

        Args:
            token: JWT token string (ignored, uses configured behavior)

        Returns:
            user_id from configured result

        Raises:
            TokenExpiredError: If configured to raise TokenExpiredError
            TokenInvalidError: If configured to raise TokenInvalidError
        """
        if self._validate_token_exception is not None:
            raise self._validate_token_exception

        if self._validate_token_result is None:
            # Default behavior if not configured
            return 1

        return self._validate_token_result
