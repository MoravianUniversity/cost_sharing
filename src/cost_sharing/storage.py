"""In-memory storage implementation for testing and mocking"""

from cost_sharing.models import User
from cost_sharing.exceptions import DuplicateEmailError, DuplicateOAuthProviderIdError


class InMemoryCostStorage:
    """
    In-memory storage implementation for development and testing.

    Uses a dictionary keyed by user ID to store users.
    Auto-increments user IDs starting at 1.
    """

    def __init__(self):
        """Initialize empty storage"""
        self._users = {}
        self._next_id = 1
        self._email_index = {}
        self._oauth_provider_id_index = {}

    def find_user_by_oauth_provider_id(self, oauth_provider_id):
        """
        Find user by OAuth provider ID.

        Args:
            oauth_provider_id: OAuth provider's unique user ID (Google's 'sub')

        Returns:
            User if found, None otherwise
        """
        return self._oauth_provider_id_index.get(oauth_provider_id)

    def create_user(self, email, name, oauth_provider_id):
        """
        Create a new user.

        Args:
            email: User's email address
            name: User's name
            oauth_provider_id: OAuth provider's unique user ID (Google's 'sub')

        Returns:
            Newly created User object

        Raises:
            DuplicateEmailError: If email already exists
            DuplicateOAuthProviderIdError: If oauth_provider_id already exists
        """
        # Check for duplicate email
        if email in self._email_index:
            raise DuplicateEmailError()

        # Check for duplicate oauth_provider_id
        if oauth_provider_id in self._oauth_provider_id_index:
            raise DuplicateOAuthProviderIdError()

        # Create user with auto-incremented ID
        user = User(
            id=self._next_id,
            email=email,
            name=name,
            oauth_provider_id=oauth_provider_id
        )

        # Store in all indices
        self._users[user.id] = user
        self._email_index[email] = user
        self._oauth_provider_id_index[oauth_provider_id] = user

        # Increment next ID
        self._next_id += 1

        return user

    def get_user_by_id(self, user_id):
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        return self._users.get(user_id)
