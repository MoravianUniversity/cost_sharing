"""Custom exceptions for the Cost Sharing application"""


class DuplicateEmailError(Exception):
    """Raised when attempting to create a user with an email that already exists"""


class UserNotFoundError(Exception):
    """Raised when a requested user cannot be found"""


class GroupNotFoundError(Exception):
    """Raised when a requested group cannot be found"""


class ForbiddenError(Exception):
    """Raised when a user does not have permission to perform an action"""


class ConflictError(Exception):
    """Raised when an operation conflicts with existing data (e.g., duplicate member)"""


class StorageException(Exception):
    """Raised when a database storage operation fails"""
