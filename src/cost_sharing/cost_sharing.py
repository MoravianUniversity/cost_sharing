"""Application layer for Cost Sharing system."""


class CostSharing:
    """Application layer for Cost Sharing system."""

    def __init__(self, storage):
        """
        Initialize the application layer with a storage implementation.

        Args:
            storage: CostStorage implementation (e.g., DatabaseCostStorage)
        """
        self._storage = storage

    def get_user_by_id(self, user_id):
        """
        Get user by their ID.

        Args:
            user_id: User ID

        Returns:
            User object

        Raises:
            UserNotFoundError: If user doesn't exist
        """
        return self._storage.get_user_by_id(user_id)

    def get_or_create_user(self, email, name):
        """
        Get existing user or create new user.

        Args:
            email: User's email
            name: User's name

        Returns:
            User object (existing or newly created)
        """
        if self._storage.is_user(email):
            return self._storage.get_user_by_email(email)
        return self._storage.create_user(email, name)

    def get_user_groups(self, user_id):
        """
        Get all groups that a user belongs to.

        Args:
            user_id: User ID

        Returns:
            List of Group objects for groups the user belongs to
        """
        return self._storage.get_user_groups(user_id)

    def create_group(self, user_id, name, description=None):
        """
        Create a new group with the specified user as creator and member.

        Args:
            user_id: User ID of the group creator
            name: Group name (must be at least 1 character)
            description: Optional group description (max 500 characters)

        Returns:
            Group object for the newly created group

        Raises:
            UserNotFoundError: If user with the given ID is not found
        """
        return self._storage.create_group(user_id, name, description)
