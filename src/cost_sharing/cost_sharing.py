"""Application layer for Cost Sharing system."""

from cost_sharing.exceptions import (
    UserNotFoundError,
    GroupNotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError
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

    def add_group_member(self, group_id, caller_user_id, email, name):
        """
        Add a member to a group by email. Creates user account if user doesn't exist.

        Args:
            group_id: Group ID to add member to
            caller_user_id: User ID of the authenticated caller (must be a member)
            email: Email address of the user to add
            name: Name of the user to add

        Returns:
            Group object with updated members list

        Raises:
            GroupNotFoundError: If group doesn't exist
            ForbiddenError: If caller is not a member of the group
            ConflictError: If user is already a member of the group
        """
        # Verify caller is a member (raises GroupNotFoundError or ForbiddenError if invalid)
        group = self.get_group_by_id(group_id, caller_user_id)

        # Get or create the user
        user = self.get_or_create_user(email, name)

        # Check if user is already a member
        user_ids = [member.id for member in group.members]
        if user.id in user_ids:
            raise ConflictError("User is already a member of this group")

        # Add member to group
        self._storage.add_group_member(group_id, user.id)

        # Return updated group
        return self._storage.get_group_by_id(group_id)

    def get_group_expenses(self, group_id, user_id):
        """
        Get all expenses for a group, ensuring the user is a member.

        Args:
            group_id: Group ID
            user_id: User ID of the requesting user (must be a member)

        Returns:
            List of Expense objects with per_person_amount calculated

        Raises:
            GroupNotFoundError: If group doesn't exist
            ForbiddenError: If user is not a member of the group
        """
        # Verify authorization (raises GroupNotFoundError or ForbiddenError if invalid)
        self.get_group_by_id(group_id, user_id)

        # Get expenses from storage
        expenses = self._storage.get_group_expenses(group_id)

        # Calculate per_person_amount for each expense
        for expense in expenses:
            num_participants = len(expense.split_between)
            expense.per_person_amount = round(expense.amount / num_participants, 2)

        return expenses

    def create_expense(self, group_id, user_id, description, amount, date, split_between):
        """
        Create a new expense in a group.

        Args:
            group_id: Group ID
            user_id: User ID of the authenticated user (payer)
            description: Expense description (1-200 characters)
            amount: Expense amount (>= 0.01)
            date: Expense date (YYYY-MM-DD format)
            split_between: List of user IDs to split the expense among

        Returns:
            Expense object with per_person_amount calculated

        Raises:
            GroupNotFoundError: If group doesn't exist
            ForbiddenError: If user is not a member of the group
            ValidationError: If validation fails (user not in splitBetween, 
                invalid participants, etc.)
        """
        # Verify authorization (raises GroupNotFoundError or ForbiddenError if invalid)
        group = self.get_group_by_id(group_id, user_id)

        # Validate split_between is not empty
        if not split_between or len(split_between) == 0:
            raise ValidationError("splitBetween must contain at least one user ID")

        # Validate user is included in split_between
        if user_id not in split_between:
            raise ValidationError("splitBetween must include the authenticated user's ID")

        # Validate all users in split_between are group members
        member_ids = [member.id for member in group.members]
        invalid_users = [uid for uid in split_between if uid not in member_ids]
        if invalid_users:
            raise ValidationError("All users in splitBetween must be members of the group")

        # Create expense in storage layer
        expense = self._storage.create_expense(
            group_id=group_id,
            description=description,
            amount=amount,
            expense_date=date,
            paid_by_user_id=user_id,
            participant_user_ids=split_between
        )

        # Calculate per_person_amount
        num_participants = len(expense.split_between)
        expense.per_person_amount = round(expense.amount / num_participants, 2)

        return expense
