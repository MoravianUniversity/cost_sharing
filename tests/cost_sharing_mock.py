"""Mock implementation of CostSharing for testing"""

from cost_sharing.models import User


class CostSharingMock:
    """
    Mock implementation of CostSharing for testing.

    This mock allows you to configure behavior for testing different scenarios.
    Use the configuration methods to set up the desired behavior before passing
    the mock to create_app().
    """

    def __init__(self):
        """Initialize the mock."""
        # Configuration for get_or_create_user
        self._get_or_create_result = None
        self._get_or_create_exception = None

        # Configuration for get_user_by_id
        self._get_user_by_id_result = None
        self._get_user_by_id_exception = None

    def get_or_create_user_returns(self, user_id, email, name):
        """
        Configure get_or_create_user to return successfully.

        Args:
            user_id: User ID to return
            email: Email to return
            name: Name to return
        """
        self._get_or_create_result = User(id=user_id, email=email, name=name)
        self._get_or_create_exception = None

    def get_or_create_user_raises(self, exception):
        """
        Configure get_or_create_user to raise an exception.

        Args:
            exception: Exception instance to raise
        """
        self._get_or_create_result = None
        self._get_or_create_exception = exception

    def get_user_by_id_returns(self, user_id, email, name):
        """
        Configure get_user_by_id to return successfully.

        Args:
            user_id: User ID to return
            email: Email to return
            name: Name to return
        """
        self._get_user_by_id_result = User(id=user_id, email=email, name=name)
        self._get_user_by_id_exception = None

    def get_user_by_id_raises(self, exception):
        """
        Configure get_user_by_id to raise an exception.

        Args:
            exception: Exception instance to raise (UserNotFoundError)
        """
        self._get_user_by_id_result = None
        self._get_user_by_id_exception = exception

    def get_or_create_user(self, email, name):  # pylint: disable=W0613
        """
        Get existing user or create new user (mock implementation).

        Args:
            email: User's email (ignored, uses configured behavior)
            name: User's name (ignored, uses configured behavior)

        Returns:
            User object from configured result

        Raises:
            Exception: If configured to raise an exception
        """
        if self._get_or_create_exception is not None:
            raise self._get_or_create_exception

        if self._get_or_create_result is None:
            # Default behavior if not configured
            return User(id=1, email="default@example.com", name="Default User")

        return self._get_or_create_result

    def get_user_by_id(self, user_id):  # pylint: disable=W0613
        """
        Get user by their ID (mock implementation).

        Args:
            user_id: User ID (ignored, uses configured behavior)

        Returns:
            User object from configured result

        Raises:
            UserNotFoundError: If configured to raise UserNotFoundError
        """
        if self._get_user_by_id_exception is not None:
            raise self._get_user_by_id_exception

        if self._get_user_by_id_result is None:
            # Default behavior if not configured
            return User(id=1, email="default@example.com", name="Default User")

        return self._get_user_by_id_result
