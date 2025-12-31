"""Application layer for Cost Sharing system."""


class CostSharing:
    """Application layer for Cost Sharing system."""

    def __init__(self, storage):
        """
        Initialize the application layer with a storage implementation.

        Args:
            storage: CostStorage implementation (e.g., InMemoryCostStorage, DBCostStorage)
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
