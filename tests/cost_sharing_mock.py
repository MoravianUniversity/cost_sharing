"""Mock implementation of CostSharing for testing"""

from cost_sharing.models import User, Group


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

        # Configuration for get_user_by_id
        self._get_user_by_id_result = None

        # Configuration for get_user_groups
        self._get_user_groups_result = []

        # Configuration for create_group
        self._create_group_result = None

    def get_or_create_user_returns(self, user_id, email, name):
        """
        Configure get_or_create_user to return successfully.

        Args:
            user_id: User ID to return
            email: Email to return
            name: Name to return
        """
        self._get_or_create_result = User(id=user_id, email=email, name=name)

    def get_user_by_id_returns(self, user_id, email, name):
        """
        Configure get_user_by_id to return successfully.

        Args:
            user_id: User ID to return
            email: Email to return
            name: Name to return
        """
        self._get_user_by_id_result = User(id=user_id, email=email, name=name)

    def get_user_groups_returns(self, groups):
        """
        Configure get_user_groups to return a list of groups.

        Args:
            groups: List of Group objects
        """
        self._get_user_groups_result = groups

    def create_group_returns(self, group):
        """
        Configure create_group to return successfully.

        Args:
            group: Group object to return
        """
        self._create_group_result = group

    def get_or_create_user(self, email, name):  # pylint: disable=W0613
        """
        Get existing user or create new user (mock implementation).

        Args:
            email: User's email (ignored, uses configured behavior)
            name: User's name (ignored, uses configured behavior)

        Returns:
            User object from configured result
        """
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
        """
        if self._get_user_by_id_result is None:
            # Default behavior if not configured
            return User(id=1, email="default@example.com", name="Default User")

        return self._get_user_by_id_result

    def get_user_groups(self, user_id):  # pylint: disable=W0613
        """
        Get all groups that a user belongs to (mock implementation).

        Args:
            user_id: User ID (ignored, uses configured behavior)

        Returns:
            List of Group objects from configured result
        """
        return self._get_user_groups_result

    def create_group(self, user_id, name, description=None):  # pylint: disable=W0613
        """
        Create a new group (mock implementation).

        Args:
            user_id: User ID (ignored, uses configured behavior)
            name: Group name (ignored, uses configured behavior)
            description: Group description (ignored, uses configured behavior)

        Returns:
            Group object from configured result
        """
        if self._create_group_result is None:
            # Default behavior if not configured
            default_user = User(id=1, email="default@example.com", name="Default User")
            return Group(
                id=1, name="Default Group", description="",
                created_by=default_user, members=[default_user]
            )

        return self._create_group_result
