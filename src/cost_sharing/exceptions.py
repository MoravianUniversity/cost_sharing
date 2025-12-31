"""Custom exceptions for the Cost Sharing application"""


class DuplicateEmailError(Exception):
    """Raised when attempting to create a user with an email that already exists"""


class UserNotFoundError(Exception):
    """Raised when a requested user cannot be found"""
