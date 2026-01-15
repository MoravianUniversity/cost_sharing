"""
Shared pytest fixtures and utilities for all tests.

This module provides fixtures for creating test databases with or without sample data.
All fixtures use in-memory SQLite databases for fast, isolated tests.

Fixtures:
- empty_db_storage: DatabaseCostStorage with empty database (schema only)
- db_storage_with_sample_data: DatabaseCostStorage with sample data loaded
- app_empty_db: CostSharing application layer with empty database
- app_with_sample_data: CostSharing application layer with sample data loaded

The sample data is defined in src/cost_sharing/sql/sample-data.sql and documented in
docs/sample-dataset.md. Test helpers in tests/helpers.py provide assertion functions
that reference this sample data.
"""

import sqlite3
import importlib.resources
import pytest
from cost_sharing.db_storage import DatabaseCostStorage
from cost_sharing.cost_sharing import CostSharing


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


# ============================================================================
# Database Connection Fixtures (Chained)
# ============================================================================

@pytest.fixture(name='db_connection')
def create_db_connection():
    """
    Base fixture: Create an in-memory SQLite database connection with schema loaded.
    The connection is properly closed when the fixture tears down.
    """
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')

    # Load schema
    schema_path = importlib.resources.files('cost_sharing') / 'sql' / 'schema-sqlite.sql'
    execute_sql_file(conn, schema_path)

    yield conn

    # Close connection during fixture teardown
    conn.close()


@pytest.fixture(name='db_connection_with_data')
def create_db_connection_with_data(db_connection):
    """
    Load sample data into the database connection.
    Depends on db_connection fixture (which already has schema loaded).
    """
    sample_data_path = importlib.resources.files('cost_sharing') / 'sql' / 'sample-data.sql'
    execute_sql_file(db_connection, sample_data_path)
    yield db_connection


# ============================================================================
# Database Storage Fixtures
# ============================================================================

@pytest.fixture(name='empty_db_storage')
def create_empty_db_storage(db_connection):
    """
    Create a DatabaseCostStorage instance with an empty database (schema only, no data).
    """
    yield DatabaseCostStorage(db_connection)


@pytest.fixture(name='db_storage_with_sample_data')
def create_db_storage_with_sample_data(db_connection_with_data):
    """
    Create a DatabaseCostStorage instance with sample data loaded.
    """
    yield DatabaseCostStorage(db_connection_with_data)


# ============================================================================
# Application Layer Fixtures
# ============================================================================

@pytest.fixture(name='app_empty_db')
def create_app_empty_db(db_connection):
    """Fixture for CostSharing with empty database (schema only, no data)"""
    storage = DatabaseCostStorage(db_connection)
    yield CostSharing(storage)


@pytest.fixture(name='app_with_sample_data')
def create_app_with_sample_data(db_connection_with_data):
    """Fixture for CostSharing with database storage and sample data"""
    storage = DatabaseCostStorage(db_connection_with_data)
    yield CostSharing(storage)
