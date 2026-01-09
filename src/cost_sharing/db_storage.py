"""Database storage implementation using sqlite3"""

import sqlite3

from cost_sharing.models import User, Group
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
            connection: A sqlite3.Connection object
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
            List of Group objects for groups the user belongs to

        Raises:
            StorageException: If a database error occurs
        """
        try:
            group_rows = self._get_groups_with_creator_info(user_id)
            groups = []
            for row in group_rows:
                members = self._get_group_members(row['id'])
                creator = self._build_creator_from_row(row)
                groups.append(Group(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or '',
                    created_by=creator,
                    members=members
                ))
            return groups
        except sqlite3.Error as e:
            raise StorageException(f"Database error retrieving user groups: {e}") from e

    def _get_groups_with_creator_info(self, user_id):
        """
        Private helper to get all groups (with creator info) a user belongs to.
        """
        cursor = self._conn.execute(
            '''
            SELECT g.id, g.name, g.description, g.created_by_user_id,
                   creator.id as creator_id, creator.email as creator_email,
                   creator.name as creator_name
            FROM groups g
            INNER JOIN users creator ON g.created_by_user_id = creator.id
            WHERE g.id IN (
                SELECT group_id FROM group_members WHERE user_id = ?
            )
            ORDER BY g.id
            ''',
            (user_id,)
        )
        return cursor.fetchall()

    def _get_group_members(self, group_id):
        """
        Private helper to get all users who are members of the given group.
        """
        members_cursor = self._conn.execute(
            '''
            SELECT u.id, u.email, u.name
            FROM group_members gm
            INNER JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = ?
            ORDER BY u.id
            ''',
            (group_id,)
        )
        member_rows = members_cursor.fetchall()
        return [
            User(id=member_row['id'], email=member_row['email'], name=member_row['name'])
            for member_row in member_rows
        ]

    def _build_creator_from_row(self, row):
        """
        Private helper to build a User object for the creator from a group row.
        """
        return User(
            id=row['creator_id'],
            email=row['creator_email'],
            name=row['creator_name']
        )

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
            StorageException: If a database error occurs
        """
        try:
            creator = self._get_user_by_id(user_id)
            group_id = self._insert_group(name, description, user_id)
            self._add_group_member(group_id, user_id)
            self._conn.commit()

            return Group(
                id=group_id,
                name=name,
                description=description or '',
                created_by=creator,
                members=[creator]
            )
        except sqlite3.Error as e:
            self._conn.rollback()
            raise StorageException(f"Database error creating group: {e}") from e

    def _get_user_by_id(self, user_id):
        """
        Private helper to fetch User object by ID.
        Raises UserNotFoundError if user does not exist.
        """
        user_cursor = self._conn.execute(
            'SELECT id, email, name FROM users WHERE id = ?',
            (user_id,)
        )
        user_row = user_cursor.fetchone()
        if user_row is None:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return User(id=user_row['id'], email=user_row['email'], name=user_row['name'])

    def _insert_group(self, name, description, user_id):
        """
        Private helper to insert a new group and return its id.
        """
        cursor = self._conn.execute(
            'INSERT INTO groups (name, description, created_by_user_id) VALUES (?, ?, ?)',
            (name, description, user_id)
        )
        return cursor.lastrowid

    def _add_group_member(self, group_id, user_id):
        """
        Private helper to add a user as a member to a group.
        """
        self._conn.execute(
            'INSERT INTO group_members (group_id, user_id) VALUES (?, ?)',
            (group_id, user_id)
        )
