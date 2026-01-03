"""Database storage implementation using sqlite3"""

import sqlite3

from cost_sharing.models import User
from cost_sharing.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    StorageException
)


class DatabaseCostStorage:
    """
    Database storage implementation using sqlite3.

    Uses SQLite database (in-memory or file-based) for persistence.
    """

    def __init__(self, connection):
        """
        Initialize database storage with a database connection.

        Args:
            connection: A sqlite3.Connection object (e.g., sqlite3.connect(':memory:')
                       or sqlite3.connect('costsharing.db'))
        """
        self._conn = connection

        # Use Row factory for dict-like access to rows
        self._conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        self._conn.execute('PRAGMA foreign_keys = ON')

    def is_user(self, email):
        """
        Check if a user exists with the given email.

        Args:
            email: User's email address

        Returns:
            bool: True if user exists, False otherwise

        Raises:
            StorageException: If a database error occurs
        """
        try:
            cursor = self._conn.execute(
                'SELECT 1 FROM users WHERE email = ?',
                (email,)
            )
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            raise StorageException(f"Database error checking user existence: {e}") from e

    def get_user_by_email(self, email):
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            User if found

        Raises:
            UserNotFoundError: If user with the given email is not found
            StorageException: If a database error occurs
        """
        try:
            cursor = self._conn.execute(
                'SELECT id, email, name FROM users WHERE email = ?',
                (email,)
            )
            row = cursor.fetchone()
            if row is None:
                raise UserNotFoundError(f"User with email '{email}' not found")
            return User(id=row['id'], email=row['email'], name=row['name'])
        except sqlite3.Error as e:
            raise StorageException(f"Database error retrieving user by email: {e}") from e

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
            StorageException: If a database error occurs
        """
        try:
            cursor = self._conn.execute(
                'INSERT INTO users (email, name) VALUES (?, ?)',
                (email, name)
            )
            self._conn.commit()
            user_id = cursor.lastrowid
            return User(id=user_id, email=email, name=name)
        except sqlite3.IntegrityError as e:
            self._conn.rollback()
            # IntegrityError on users table insert is always a duplicate email
            raise DuplicateEmailError() from e
        except sqlite3.Error as e:
            self._conn.rollback()
            raise StorageException(f"Database error creating user: {e}") from e

    def get_user_by_id(self, user_id):
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User if found

        Raises:
            UserNotFoundError: If user with the given ID is not found
            StorageException: If a database error occurs
        """
        try:
            cursor = self._conn.execute(
                'SELECT id, email, name FROM users WHERE id = ?',
                (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            return User(id=row['id'], email=row['email'], name=row['name'])
        except sqlite3.Error as e:
            raise StorageException(f"Database error retrieving user by ID: {e}") from e
