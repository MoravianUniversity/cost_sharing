"""Database storage implementation using sqlite3"""

import sqlite3

from cost_sharing.models import User, GroupInfo
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

    def get_user_groups(self, user_id):
        """
        Get all groups that a user belongs to.

        Args:
            user_id: User ID

        Returns:
            List of GroupInfo objects for groups the user belongs to

        Raises:
            StorageException: If a database error occurs
        """
        try:
            cursor = self._conn.execute(
                '''
                SELECT g.id, g.name, g.description,
                       COUNT(gm.user_id) as member_count
                FROM groups g
                INNER JOIN group_members gm ON g.id = gm.group_id
                WHERE g.id IN (
                    SELECT group_id FROM group_members WHERE user_id = ?
                )
                GROUP BY g.id, g.name, g.description
                ORDER BY g.id
                ''',
                (user_id,)
            )
            rows = cursor.fetchall()
            groups = []
            for row in rows:
                groups.append(GroupInfo(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or '',
                    member_count=row['member_count']
                ))
            return groups
        except sqlite3.Error as e:
            raise StorageException(f"Database error retrieving user groups: {e}") from e

    def create_group(self, user_id, name, description=None):
        """
        Create a new group with the specified user as creator and member.

        Args:
            user_id: User ID of the group creator
            name: Group name (must be at least 1 character)
            description: Optional group description (max 500 characters)

        Returns:
            GroupInfo object for the newly created group

        Raises:
            UserNotFoundError: If user with the given ID is not found
            StorageException: If a database error occurs
        """
        try:
            # Verify user exists
            user_cursor = self._conn.execute(
                'SELECT id FROM users WHERE id = ?',
                (user_id,)
            )
            if user_cursor.fetchone() is None:
                raise UserNotFoundError(f"User with ID {user_id} not found")

            # Insert group
            cursor = self._conn.execute(
                'INSERT INTO groups (name, description, created_by_user_id) VALUES (?, ?, ?)',
                (name, description, user_id)
            )
            group_id = cursor.lastrowid

            # Add creator as member
            self._conn.execute(
                'INSERT INTO group_members (group_id, user_id) VALUES (?, ?)',
                (group_id, user_id)
            )

            self._conn.commit()

            # Return GroupInfo with member_count = 1 (just the creator)
            return GroupInfo(
                id=group_id,
                name=name,
                description=description or '',
                member_count=1
            )
        except sqlite3.Error as e:
            self._conn.rollback()
            raise StorageException(f"Database error creating group: {e}") from e
