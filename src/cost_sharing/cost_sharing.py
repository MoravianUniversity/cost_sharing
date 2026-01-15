"""Application layer for Cost Sharing system."""

from cost_sharing.exceptions import (
    UserNotFoundError,
    GroupNotFoundError,
    ForbiddenError
)


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
        user = self._storage.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return user

    def get_or_create_user(self, email, name):
        """
        Get existing user or create new user.

        Args:
            email: User's email
            name: User's name

        Returns:
            User object (existing or newly created)
        """
        user = self._storage.get_user_by_email(email)
        if user is not None:
            return user
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

    def create_group(self, user_id, name, description=''):
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
        # Business logic: verify user exists - will raise UserNotFoundError if user does not exist
        self.get_user_by_id(user_id)
        return self._storage.create_group(name, description, user_id)

    def get_group_by_id(self, group_id, user_id):
        """
        Get group by ID, ensuring the user is a member.

        Args:
            group_id: Group ID
            user_id: User ID of the requesting user

        Returns:
            Group object with creator and members populated

        Raises:
            GroupNotFoundError: If group doesn't exist
            ForbiddenError: If user is not a member of the group
        """
        group = self._storage.get_group_by_id(group_id)

        if group is None:
            raise GroupNotFoundError(f"Group with ID {group_id} not found")

        user_ids = [member.id for member in group.members]
        if user_id not in user_ids:
            raise ForbiddenError("You do not have access to this group")

        return group
