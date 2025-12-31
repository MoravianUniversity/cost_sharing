"""In-memory storage implementation for testing and mocking"""

from cost_sharing.models import User
from cost_sharing.exceptions import (
    DuplicateEmailError,
    UserNotFoundError
)


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

    def is_user(self, email):
        """
        Check if a user exists with the given email.

        Args:
            email: User's email address

        Returns:
            bool: True if user exists, False otherwise
        """
        return email in self._email_index

    def get_user_by_email(self, email):
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User if found

        Raises:
            UserNotFoundError: If user with the given email is not found
        """
        user = self._email_index.get(email)
        if user is None:
            raise UserNotFoundError(f"User with email '{email}' not found")
        return user

    def create_user(self, email, name):
        """
        Create a new user.

        Args:
            email: User's email address
            name: User's name

        Returns:
            Newly created User object

        Raises:
            DuplicateEmailError: If email already exists
        """
        # Check for duplicate email
        if email in self._email_index:
            raise DuplicateEmailError()

        # Create user with auto-incremented ID
        user = User(
            id=self._next_id,
            email=email,
            name=name
        )

        # Store in all indices
        self._users[user.id] = user
        self._email_index[email] = user

        # Increment next ID
        self._next_id += 1

        return user

    def get_user_by_id(self, user_id):
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found

        Raises:
            UserNotFoundError: If user with the given ID is not found
        """
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user
