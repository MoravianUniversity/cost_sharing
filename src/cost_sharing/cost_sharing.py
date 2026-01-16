"""Application layer for Cost Sharing system."""

from cost_sharing.exceptions import (
    UserNotFoundError,
    GroupNotFoundError,
    ForbiddenError,
    ConflictError,
    ValidationError,
    ExpenseNotFoundError
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

    def get_or_create_user(self, user):
        """
        Get existing user or create new user.

        Args:
            user: UserRequest with email and name

        Returns:
            User object (existing or newly created)
        """
        existing_user = self._storage.get_user_by_email(user.email)
        if existing_user is not None:
            return existing_user
        return self._storage.create_user(user)

    def get_user_groups(self, user_id):
        """
        Get all groups that a user belongs to.

        Args:
            user_id: User ID

        Returns:
            List of Group objects for groups the user belongs to
        """
        return self._storage.get_user_groups(user_id)

    def create_group(self, group):
        """
        Create a new group with the specified user as creator and member.

        Args:
            group: GroupRequest with name, description, and created_by_user_id

        Returns:
            Group object for the newly created group

        Raises:
            UserNotFoundError: If user with the given ID is not found
        """
        # Business logic: verify user exists - will raise UserNotFoundError if user does not exist
        self.get_user_by_id(group.created_by_user_id)
        return self._storage.create_group(group)

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

    def add_group_member(self, group_id, caller_user_id, user):
        """
        Add a member to a group by email. Creates user account if user doesn't exist.

        Args:
            group_id: Group ID to add member to
            caller_user_id: User ID of the authenticated caller (must be a member)
            user: UserRequest with email and name of the user to add

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
        new_user = self.get_or_create_user(user)

        # Check if user is already a member
        user_ids = [member.id for member in group.members]
        if new_user.id in user_ids:
            raise ConflictError("User is already a member of this group")

        # Add member to group
        self._storage.add_group_member(group_id, new_user.id)

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

    def create_expense(self, expense):
        """
        Create a new expense in a group.

        Args:
            expense: ExpenseRequest with group_id, description, amount,
                date, paid_by_user_id, and participant_user_ids

        Returns:
            Expense object with per_person_amount calculated

        Raises:
            GroupNotFoundError: If group doesn't exist
            ForbiddenError: If user is not a member of the group
            ValidationError: If validation fails (user not in splitBetween, 
                invalid participants, etc.)
        """
        # Verify authorization (raises GroupNotFoundError or ForbiddenError if invalid)
        group = self.get_group_by_id(expense.group_id, expense.paid_by_user_id)

        # Validate split_between is not empty
        participant_ids = expense.participant_user_ids
        if not participant_ids or len(participant_ids) == 0:
            raise ValidationError("splitBetween must contain at least one user ID")

        # Validate user is included in split_between
        if expense.paid_by_user_id not in participant_ids:
            raise ValidationError("splitBetween must include the authenticated user's ID")

        # Validate all users in split_between are group members
        member_ids = [member.id for member in group.members]
        invalid_users = [uid for uid in participant_ids if uid not in member_ids]
        if invalid_users:
            raise ValidationError("All users in splitBetween must be members of the group")

        # Create expense in storage layer
        created_expense = self._storage.create_expense(expense)

        # Calculate per_person_amount
        num_participants = len(created_expense.split_between)
        created_expense.per_person_amount = round(created_expense.amount / num_participants, 2)

        return created_expense

    def get_expense_by_id(self, expense_id, group_id, user_id):
        """
        Get expense by ID, ensuring the user is a member of the group.

        Args:
            expense_id: Expense ID
            group_id: Group ID
            user_id: User ID of the requesting user (must be a member)

        Returns:
            Expense object with per_person_amount calculated

        Raises:
            ExpenseNotFoundError: If expense doesn't exist
            GroupNotFoundError: If group doesn't exist
            ForbiddenError: If user is not a member of the group
        """
        # Verify authorization (raises GroupNotFoundError or ForbiddenError if invalid)
        self.get_group_by_id(group_id, user_id)

        # Get expense from storage
        expense = self._storage.get_expense_by_id(expense_id)

        if expense is None:
            raise ExpenseNotFoundError(f"Expense with ID {expense_id} not found")

        # Verify expense belongs to the group
        if expense.group_id != group_id:
            raise ExpenseNotFoundError(f"Expense with ID {expense_id} not found")

        # Calculate per_person_amount
        num_participants = len(expense.split_between)
        expense.per_person_amount = round(expense.amount / num_participants, 2)

        return expense
