"""Tests for DatabaseCostStorage class"""

import sqlite3
import importlib.resources
from unittest.mock import MagicMock
import pytest
from cost_sharing.db_storage import DatabaseCostStorage
from cost_sharing.exceptions import (
    DuplicateEmailError,
    UserNotFoundError,
    StorageException
)


def execute_sql_file(connection, sql_path):
    """
    Execute SQL statements from a file.
    
    Args:
        connection: sqlite3.Connection to execute SQL against
        sql_path: Path to SQL file to execute (string or pathlib.Path)
    """
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    connection.executescript(sql_content)


@pytest.fixture(name='db_connection')
def create_db_connection():
    """
    Create an in-memory SQLite database connection with schema loaded.
    """
    # Create in-memory database connection
    conn = sqlite3.connect(':memory:')

    # Load schema - get path to SQL file using importlib.resources
    schema_path = importlib.resources.files('cost_sharing') / 'sql' / 'schema-sqlite.sql'
    execute_sql_file(conn, schema_path)

    yield conn

    # Cleanup
    conn.close()


@pytest.fixture(name='db_connection_with_data')
def create_db_connection_with_data(db_connection):
    """
    Create an in-memory SQLite database connection with schema and sample data loaded.
    """
    # Load sample data - get path to SQL file using importlib.resources
    sample_data_path = importlib.resources.files('cost_sharing') / 'sql' / 'sample-data.sql'
    execute_sql_file(db_connection, sample_data_path)

    return db_connection


@pytest.fixture(name='db_storage')
def create_db_storage(db_connection):
    """
    Create a DatabaseCostStorage instance with an empty database (schema only, no data).
    """
    return DatabaseCostStorage(db_connection)


@pytest.fixture(name='db_storage_with_sample_data')
def create_db_storage_with_sample_data(db_connection_with_data):
    """
    Create a DatabaseCostStorage instance with sample data loaded.
    """
    return DatabaseCostStorage(db_connection_with_data)


def test_is_user_returns_true_for_existing_user(db_storage):
    """Test is_user returns True when user exists"""
    storage = db_storage
    storage.create_user("test@example.com", "Test User")

    assert storage.is_user("test@example.com") is True


def test_is_user_returns_false_for_nonexistent_user(db_storage):
    """Test is_user returns False when user does not exist"""
    storage = db_storage

    assert storage.is_user("nonexistent@example.com") is False


def test_get_user_by_email_returns_user_when_exists(db_storage):
    """Test get_user_by_email retrieves user and all fields are correct"""
    storage = db_storage
    created_user = storage.create_user("test@example.com", "Test User")

    retrieved_user = storage.get_user_by_email("test@example.com")

    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.name == "Test User"


def test_get_user_by_email_raises_user_not_found_error_when_not_exists(db_storage):
    """Test get_user_by_email raises UserNotFoundError when user does not exist"""
    storage = db_storage

    with pytest.raises(UserNotFoundError):
        storage.get_user_by_email("nonexistent@example.com")


def test_create_user_returns_user_with_id_one_for_first_user(db_storage):
    """Test create_user returns user with ID 1 for first user and all fields are correct"""
    storage = db_storage

    user = storage.create_user("test@example.com", "Test User")

    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_create_user_auto_increments_after_sample_data(db_storage_with_sample_data):
    """Test create_user auto-increments ID after sample data and all fields are correct"""
    storage = db_storage_with_sample_data

    user = storage.create_user("newuser@example.com", "New User")

    assert user.id == 7
    assert user.email == "newuser@example.com"
    assert user.name == "New User"


def test_create_user_raises_duplicate_email_error_for_existing_email(db_storage):
    """Test create_user raises DuplicateEmailError for duplicate email"""
    storage = db_storage
    storage.create_user("test@example.com", "Test User")

    with pytest.raises(DuplicateEmailError):
        storage.create_user("test@example.com", "Another User")


def test_create_user_auto_increments_ids_for_multiple_users(db_storage):
    """Test create_user auto-increments IDs for multiple users"""
    storage = db_storage

    user1 = storage.create_user("user1@example.com", "User One")
    user2 = storage.create_user("user2@example.com", "User Two")
    user3 = storage.create_user("user3@example.com", "User Three")

    assert user1.id == 1
    assert user2.id == 2
    assert user3.id == 3


def test_get_user_by_id_returns_user_when_exists(db_storage):
    """Test get_user_by_id retrieves user and all fields are correct"""
    storage = db_storage
    created_user = storage.create_user("test@example.com", "Test User")

    retrieved_user = storage.get_user_by_id(created_user.id)

    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.name == "Test User"


def test_get_user_by_id_raises_user_not_found_error_when_not_exists(db_storage):
    """Test get_user_by_id raises UserNotFoundError for invalid ID"""
    storage = db_storage

    with pytest.raises(UserNotFoundError):
        storage.get_user_by_id(999)

    with pytest.raises(UserNotFoundError):
        storage.get_user_by_id(0)

    with pytest.raises(UserNotFoundError):
        storage.get_user_by_id(-1)


def test_create_and_retrieve_user_by_email(db_storage):
    """Test creating user and retrieving by email"""
    storage = db_storage

    created_user = storage.create_user("test@example.com", "Test User")
    retrieved_user = storage.get_user_by_email("test@example.com")

    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name


def test_create_and_retrieve_user_by_id(db_storage):
    """Test creating user and retrieving by ID"""
    storage = db_storage

    created_user = storage.create_user("test@example.com", "Test User")
    retrieved_user = storage.get_user_by_id(created_user.id)

    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email
    assert retrieved_user.name == created_user.name


def test_create_user_then_check_is_user(db_storage):
    """Test creating user and verifying with is_user"""
    storage = db_storage

    storage.create_user("test@example.com", "Test User")

    assert storage.is_user("test@example.com") is True
    assert storage.is_user("nonexistent@example.com") is False


def test_multiple_users_can_be_created_and_retrieved(db_storage):
    """Test multiple users can be created and all operations work"""
    storage = db_storage

    user1 = storage.create_user("user1@example.com", "User One")
    user2 = storage.create_user("user2@example.com", "User Two")
    user3 = storage.create_user("user3@example.com", "User Three")

    assert storage.is_user("user1@example.com") is True
    assert storage.is_user("user2@example.com") is True
    assert storage.is_user("user3@example.com") is True

    retrieved1 = storage.get_user_by_email("user1@example.com")
    retrieved2 = storage.get_user_by_id(user2.id)
    retrieved3 = storage.get_user_by_email("user3@example.com")

    assert retrieved1.id == user1.id
    assert retrieved2.id == user2.id
    assert retrieved3.id == user3.id


@pytest.fixture(name='error_storage')
def create_error_storage():
    """
    Create a DatabaseCostStorage instance with a connection that raises errors.

    Creates storage with a real connection to allow __init__ to complete normally,
    then replaces the connection with a MagicMock that raises sqlite3.Error.
    This allows testing the StorageException handling paths.
    """
    conn = sqlite3.connect(':memory:')
    storage = DatabaseCostStorage(conn)
    conn.close()
    # Replace connection with mock that raises errors
    mock_conn = MagicMock()
    mock_conn.execute = MagicMock(side_effect=sqlite3.Error("Mock database error"))
    storage._conn = mock_conn # pylint: disable=protected-access
    return storage


def test_is_user_raises_storage_exception_on_database_error(error_storage):
    """Test is_user raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.is_user("test@example.com")


def test_get_user_by_email_raises_storage_exception_on_database_error(error_storage):
    """Test get_user_by_email raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.get_user_by_email("test@example.com")


def test_create_user_raises_storage_exception_on_database_error(error_storage):
    """Test create_user raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.create_user("test@example.com", "Test User")


def test_get_user_by_id_raises_storage_exception_on_database_error(error_storage):
    """Test get_user_by_id raises StorageException when database error occurs"""
    storage = error_storage

    with pytest.raises(StorageException):
        storage.get_user_by_id(1)
